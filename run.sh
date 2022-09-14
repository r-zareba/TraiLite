#!/bin/bash


python manage.py makemigrations
python manage.py migrate

if [[ $1 = test ]]
then
  python -m unittest tests/test_prices.py
else
  python main.py
fi
