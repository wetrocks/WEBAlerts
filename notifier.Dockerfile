FROM python:3.10-slim

WORKDIR /app

COPY ./notifier/requirements.txt requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt

COPY ./common ./common
COPY ./notifier/ ./notifier

CMD [ "uvicorn" , "notifier.main:app", "--port", "8000" ]
