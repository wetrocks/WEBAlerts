FROM python:3.10-slim

WORKDIR /app

COPY ./scraper/requirements.txt requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt

COPY ./common ./common
COPY ./scraper/ ./scraper

CMD [ "python3", "-m", "scraper.alert-scraper" ]
