CREATE OR REPLACE FUNCTION get_price_ma(price_column TEXT, asset_type asset, window_len INTEGER)
RETURNS TABLE (
                time_stamp TIMESTAMP,
                ma DOUBLE PRECISION
              )
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY EXECUTE FORMAT (
        'SELECT timestamp,
        AVG(%s)
        OVER(ORDER BY timestamp DESC ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS moving_average
        FROM prices
        WHERE asset = ''%s'';', price_column, window_len, asset_type);

end $$;


CREATE OR REPLACE FUNCTION ohlc_interval_to_n_minutes(ohlc_interval ohlc_interval)
RETURNS INTEGER
LANGUAGE plpgsql IMMUTABLE PARALLEL SAFE
AS $$
DECLARE
    ohlc_interval_text CONSTANT TEXT := ohlc_interval::TEXT;
BEGIN
    IF POSITION('M' IN ohlc_interval_text) > 0 THEN
        RETURN REPLACE(ohlc_interval_text, 'M', '')::INTEGER;
    ELSIF POSITION('H' IN ohlc_interval_text) > 0 THEN
        RETURN (REPLACE(ohlc_interval_text, 'H', '')::INTEGER) * 60;
    END IF;
end $$;


CREATE OR REPLACE FUNCTION ohlc_to_postgres_interval(ohlc_interval ohlc_interval)
RETURNS INTERVAL
LANGUAGE plpgsql IMMUTABLE PARALLEL SAFE
AS $$
DECLARE
    ohlc_interval_text CONSTANT TEXT := ohlc_interval::TEXT;
    numeric_value TEXT;
BEGIN
    IF POSITION('M' IN ohlc_interval_text) > 0 THEN
        numeric_value := REPLACE(ohlc_interval_text, 'M', '');
        RETURN CONCAT(numeric_value, ' min')::INTERVAL;
    ELSIF POSITION('H' IN ohlc_interval_text) > 0 THEN
        numeric_value := REPLACE(ohlc_interval_text, 'H', '');
        RETURN CONCAT(numeric_value, ' hour')::INTERVAL;
    END IF;
end $$;


CREATE OR REPLACE FUNCTION round_minutes_in_timestamp(timestamp_field TIMESTAMP WITHOUT TIME ZONE, n_minutes INTEGER)
RETURNS TIMESTAMP WITHOUT TIME ZONE
LANGUAGE SQL IMMUTABLE AS $$
SELECT
     date_trunc('hour', timestamp_field)
     +  cast((n_minutes::varchar ||' min') as interval)
     * round((date_part('minute', timestamp_field)::float + date_part('second', timestamp_field) / 60.)::float / n_minutes::float)
$$;


CREATE OR REPLACE FUNCTION get_n_last_prices(n integer, in_asset asset)
RETURNS TABLE (LIKE prices)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
        SELECT * FROM prices
        WHERE asset = in_asset
        ORDER BY timestamp DESC
        LIMIT n;
END $$;


CREATE OR REPLACE FUNCTION get_resampled_prices(in_asset asset, in_ohlc_interval ohlc_interval, n_necessary_ohlc integer)
RETURNS TABLE (
    resampled_timestamp timestamp,
    asset asset,
    open real,
    high real,
    low real,
    close real
              )
LANGUAGE plpgsql
AS $$
DECLARE
    in_interval constant interval := ohlc_to_postgres_interval(in_ohlc_interval);
    n_minutes constant integer := ohlc_interval_to_n_minutes(in_ohlc_interval);
    first_timestamp timestamp;
    last_timestamp timestamp;
BEGIN

    CREATE TEMP TABLE IF NOT EXISTS last_prices ON COMMIT DROP AS
        SELECT * FROM get_n_last_prices(n_necessary_ohlc, in_asset);

    SELECT timestamp
    FROM last_prices
    ORDER BY timestamp ASC
    LIMIT 1
    INTO first_timestamp;
    first_timestamp := round_minutes_in_timestamp(first_timestamp, n_minutes);

    SELECT timestamp
    FROM last_prices
    ORDER BY timestamp DESC
    LIMIT 1
    INTO last_timestamp;

    RETURN QUERY
        with intervals as (
          select start, start + in_interval as end
          from generate_series(first_timestamp, last_timestamp, in_interval) as start
        )
        select distinct
            intervals.start as timestamp,
            p.asset,
            first_value(p.open) over w as open,
            max(p.high) over w as high,
            min(p.low) over w as low,
            last_value(p.close) over w as close
        from intervals
          join prices as p on
            p.asset = in_asset and
            p.timestamp >= intervals.start and
            p.timestamp < intervals.end
        window w as (partition by intervals.start order by p.timestamp asc rows between unbounded preceding and unbounded following)
        order by intervals.start;

END $$;


CREATE OR REPLACE FUNCTION get_stochastic(in_ohlc_interval ohlc_interval, in_asset asset, k_period INTEGER, smooth INTEGER, d_period INTEGER)
RETURNS TABLE (
                datetime TIMESTAMP,
                k_value REAL,
                d_value REAL
              )
LANGUAGE plpgsql
AS $$
DECLARE
    extra_ohlc_buffer CONSTANT INTEGER := 20;
	n_necessary_ohlc INTEGER;
    window_lowest DOUBLE PRECISION;
    window_highest DOUBLE PRECISION;
    available_prices_count INTEGER;
    n_minutes CONSTANT INTEGER := ohlc_interval_to_n_minutes(in_ohlc_interval);
BEGIN

    SELECT ((GREATEST(k_period, d_period) + smooth) * n_minutes) + extra_ohlc_buffer
    INTO n_necessary_ohlc;

    SELECT COUNT(*) FROM prices
    WHERE asset = in_asset
    INTO available_prices_count;

    IF NOT available_prices_count >= n_necessary_ohlc THEN
        RETURN;
    end if;

    CREATE TEMP TABLE IF NOT EXISTS temp_stochastic ON COMMIT DROP AS
        SELECT resampled_timestamp,
               high,
               low,
               close,
               NULL::REAL AS min_values,
               NULL::REAL AS max_values,
               NULL::REAL AS k_values,
               NULL::REAL AS k_value,
               NULL::REAL AS d_value
        FROM (SELECT * FROM get_resampled_prices(in_asset, in_ohlc_interval, n_necessary_ohlc)) AS last_prices
        ORDER BY resampled_timestamp;

    WITH min_values_window AS (
        SELECT resampled_timestamp, MIN(low)
            OVER(ORDER BY resampled_timestamp ROWS BETWEEN k_period - 1 PRECEDING AND CURRENT ROW) AS min_values
        FROM temp_stochastic)

    UPDATE temp_stochastic
    SET min_values = min_values_window.min_values
    FROM min_values_window
    WHERE temp_stochastic.resampled_timestamp = min_values_window.resampled_timestamp;

    WITH max_values_window AS (
        SELECT resampled_timestamp, MAX(high)
            OVER(ORDER BY resampled_timestamp ROWS BETWEEN k_period - 1 PRECEDING AND CURRENT ROW) AS max_values
        FROM temp_stochastic)

    UPDATE temp_stochastic
    SET max_values = max_values_window.max_values
    FROM max_values_window
    WHERE temp_stochastic.resampled_timestamp = max_values_window.resampled_timestamp;

    UPDATE temp_stochastic
    SET k_values = new_values.new_value
    FROM (
        SELECT resampled_timestamp, ((close - min_values) / (max_values - min_values)) * 100 AS new_value
        FROM temp_stochastic) AS new_values
    WHERE temp_stochastic.resampled_timestamp = new_values.resampled_timestamp;

    UPDATE temp_stochastic
    SET k_value = new_values.calculated_k
    FROM (
        SELECT resampled_timestamp, AVG(temp_stochastic.k_values)
            OVER(ORDER BY resampled_timestamp ROWS BETWEEN smooth - 1 PRECEDING AND CURRENT ROW) AS calculated_k
        FROM temp_stochastic) AS new_values
    WHERE temp_stochastic.resampled_timestamp = new_values.resampled_timestamp;

    UPDATE temp_stochastic
    SET d_value = new_values.calculated_d
    FROM (
        SELECT resampled_timestamp, AVG(temp_stochastic.k_value)
            OVER(ORDER BY resampled_timestamp ROWS BETWEEN d_period - 1 PRECEDING AND CURRENT ROW) AS calculated_d
        FROM temp_stochastic) AS new_values
    WHERE temp_stochastic.resampled_timestamp = new_values.resampled_timestamp;

    RETURN QUERY
        SELECT temp_stochastic.resampled_timestamp, temp_stochastic.k_value, temp_stochastic.d_value FROM temp_stochastic;

END $$;


-- TRIGGER FUNCTION
CREATE OR REPLACE FUNCTION insert_stochastic_values()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    last_k_value REAL;
    last_d_value REAL;
    stochastic_record RECORD;

BEGIN
    FOR stochastic_record IN (SELECT * FROM stochastic_oscillators) LOOP
        SELECT k_value, d_value FROM get_stochastic(ohlc_interval := stochastic_record.interval, asset_type := NEW.asset,
            k_period := stochastic_record.k_period, smooth := stochastic_record.smooth, d_period := stochastic_record.d_period)
        ORDER BY datetime DESC
        LIMIT 1
        INTO last_k_value, last_d_value;

        INSERT INTO stochastic_values (stochastic_oscillator_id, asset, k_value, d_value)
        VALUES (stochastic_record.id, NEW.asset, last_k_value, last_d_value);
    end loop;
    RETURN NEW;

END $$;

-- REGISTER TRIGGER
CREATE TRIGGER stochastic_test_prices_trigger
AFTER INSERT ON prices_test
    FOR EACH ROW
        EXECUTE FUNCTION insert_stochastic_values();