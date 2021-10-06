COPY prices(id, timestamp, asset, open, high, low, close)
FROM '/Users/kq794tb/Desktop/TRAI_Lite/prices.csv'
DELIMITER ','
CSV HEADER;


INSERT INTO stochastic_oscillators (time_interval, k_period, smooth, d_period)
VALUES
       ('M1', 14, 2, 2),
       ('M1', 12, 2, 2),
       ('M5', 7, 3, 3),
       ('M10', 9, 2, 3),
       ('M15', 9, 2, 3);


INSERT INTO stochastic_strategies (asset, enter_oscillator_id, exit_oscillator_id, start_hour, end_hour)
VALUES
       ('EURUSD', 1, 3, 8, 16);


