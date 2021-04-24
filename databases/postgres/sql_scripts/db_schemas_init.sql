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
		    'M3'
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
  interval ohlc_interval NOT NULL,
  k_period INTEGER NOT NULL,
  smooth INTEGER NOT NULL,
  d_period INTEGER NOT NULL
);


CREATE TABLE IF NOT EXISTS stochastic_values (
  id SERIAL PRIMARY KEY,
  stochastic_oscillator_id INTEGER NOT NULL,
  currency currency,
  timestamp timestamp DEFAULT CURRENT_TIMESTAMP,
  k_value REAL NOT NULL,
  d_value REAL NOT NULL,
  CONSTRAINT fk_stochastic_oscillator
      FOREIGN KEY(stochastic_oscillator_id)
	  REFERENCES stochastic_oscillators(id)
	  ON DELETE CASCADE
);
--
-- CREATE TABLE "stochastic_strategies" (
--   "id" SERIAL PRIMARY KEY,
--   "oscillator_id" integer,
--   "enter_interval" varchar(5) NOT NULL,
--   "exit_interval" varchar(5) NOT NULL,
--   "lower_threshold" integer DEFAULT 20,
--   "upper_threshold" integer DEFAULT 80
-- );
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
-- ALTER TABLE "stochastic_values" ADD FOREIGN KEY ("oscillator_id") REFERENCES "stochastic_oscillators" ("id");
--
-- ALTER TABLE "stochastic_strategies" ADD FOREIGN KEY ("oscillator_id") REFERENCES "stochastic_oscillators" ("id");
--
-- ALTER TABLE "stochastic_transactions" ADD FOREIGN KEY ("strategy_id") REFERENCES "stochastic_strategies" ("id");
