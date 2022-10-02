FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt

COPY ./src/ .

CMD [ "python3", "alert-scraper.py" ]

