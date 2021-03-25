DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'currency') THEN
		CREATE TYPE currency AS ENUM (
		  'EURUSD',
		  'GBPUSD',
		  'DAX'
		);
    END IF;
END$$;

-- Alternative
-- DO $$ BEGIN
--     CREATE TYPE my_type AS (/* fields go here */);
-- EXCEPTION
--     WHEN duplicate_object THEN null;
-- END $$;

CREATE TABLE IF NOT EXISTS prices (
  id SERIAL PRIMARY KEY,
  timestamp TIMESTAMP DEFAULT (CURRENT_TIMESTAMP - (1 * interval '1 minute')),
  currency currency NOT NULL,
  open REAL NOT NULL,
  high REAL NOT NULL,
  low REAL NOT NULL,
  close REAL NOT NULL
);

-- CREATE TABLE "stochastic_oscillators" (
--   "id" SERIAL PRIMARY KEY,
--   "interval" varchar(5) NOT NULL,
--   "k_period" integer NOT NULL,
--   "smooth" integer NOT NULL,
--   "d_period" integer NOT NULL
-- );
--
-- CREATE TABLE "stochastic_values" (
--   "id" SERIAL PRIMARY KEY,
--   "oscillator_id" integer,
--   "currency" currency,
--   "timestamp" timestamp,
--   "k_value" double,
--   "d_value" double
-- );
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
