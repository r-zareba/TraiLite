FROM python:3.6.9
COPY requirements.txt /
RUN pip install -r /requirements.txt

RUN mkdir -p /usr/src/app
COPY . /usr/src/app
WORKDIR /usr/src/app

CMD ["python", "main.py"]
