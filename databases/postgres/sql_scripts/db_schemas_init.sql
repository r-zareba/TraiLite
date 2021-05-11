DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'asset') THEN
		CREATE TYPE asset AS ENUM (
		    'EURUSD',
		    'GBPUSD',
		    'DAX'
		);
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'ohlc_interval') THEN
		CREATE TYPE ohlc_interval AS ENUM (
		    'M1',
		    'M3',
		    'M5',
		    'M10',
		    'M15',
		    'M30',
		    'H1',
		    'H2',
		    'H4'
		);
    END IF;
END$$;

-- Alternative type creation
-- DO $$ BEGIN
--     CREATE TYPE my_type AS (/* fields go here */);
-- EXCEPTION
--     WHEN duplicate_object THEN null;
-- END $$;

CREATE TABLE IF NOT EXISTS prices (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT (CURRENT_TIMESTAMP - (1 * interval '1 minute')),
    asset asset NOT NULL,
    open REAL NOT NULL,
    high REAL NOT NULL,
    low REAL NOT NULL,
    close REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS stochastic_oscillators (
    id SERIAL PRIMARY KEY,
    time_interval ohlc_interval NOT NULL,
    k_period INTEGER NOT NULL,
    smooth INTEGER NOT NULL,
    d_period INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS stochastic_strategies (
    id SERIAL PRIMARY KEY,
    asset asset NOT NULL,
    enter_oscillator_id INTEGER NOT NULL,
    exit_oscillator_id INTEGER NOT NULL,
    enter_lower_threshold INTEGER DEFAULT 20,
    enter_upper_threshold INTEGER DEFAULT 80,
    exit_lower_threshold INTEGER DEFAULT 20,
    exit_upper_threshold INTEGER DEFAULT 80,
    start_hour INTEGER NOT NULL,
    end_hour INTEGER NOT NULL,

    CONSTRAINT fk_enter_stochastic_oscillator
        FOREIGN KEY(enter_oscillator_id)
            REFERENCES stochastic_oscillators(id)
            ON DELETE CASCADE,

    CONSTRAINT fk_exit_stochastic_oscillator
        FOREIGN KEY(exit_oscillator_id)
            REFERENCES stochastic_oscillators(id)
            ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS stochastic_values (
    id SERIAL PRIMARY KEY,
    stochastic_oscillator_id INTEGER NOT NULL,
    asset asset NOT NULL,
    timestamp timestamp DEFAULT (CURRENT_TIMESTAMP - (1 * interval '1 minute')),
    k_value REAL NOT NULL,
    d_value REAL NOT NULL,

    CONSTRAINT fk_stochastic_oscillator
        FOREIGN KEY(stochastic_oscillator_id)
            REFERENCES stochastic_oscillators(id)
            ON DELETE CASCADE
);


--
-- CREATE TABLE "stochastic_transactions" (
--   "id" SERIAL PRIMARY KEY,
--   "strategy_id" integer,
--   "currency" currency,
--   "timestamp" timestamp DEFAULT (current_timestamp),
--   "action" integer,
--   "comment" varchar(20)
-- );
--
