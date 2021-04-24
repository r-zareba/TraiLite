COPY prices(id, timestamp, asset, open, high, low, close)
FROM '/Users/kq794tb/Desktop/TRAI_Lite/prices.csv'
DELIMITER ','
CSV HEADER;


INSERT INTO stochastic_oscillators (interval, k_period, smooth, d_period)
VALUES
       ('M1', 14, 2, 2),
       ('M1', 12, 2, 2),
       ('M1', 7, 3, 3),
       ('M1', 9, 2, 3);