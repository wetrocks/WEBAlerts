from structlog import get_logger
import os
import pathlib
import requests
import time
from urllib.parse import urlparse
import datetime
from dataclasses import asdict
import json
from pydantic import BaseSettings

from common.domain import Alert, AlertRepository
from common.storage import CosmosAlertRepository
from dapr.clients import DaprClient
from .scrape import pageprocessor

class Settings(BaseSettings):
    url: str
    db_endpoint: str
    db_name: str

SLEEP_SECONDS = 60 * 60 * 6

logger = get_logger()
settings = Settings(_env_file='.env')

MSG_BINDING_NAME = "alertqueue"


def main():
    alertRepo = CosmosAlertRepository(settings.db_endpoint, settings.db_name)

    maint_urls = scrape_maint_links(settings.url)
    logger.info('Found maintenance links', count=len(maint_urls))

    for maint_page in fetch_alert_details(maint_urls, alertRepo):
        if maint_page:
            logger.debug('Saving alert details', **asdict(maint_page))
            alertRepo.save(maint_page)
            logger.info('Saved alert', id=maint_page.id)

            publish_alert(maint_page)


def scrape_maint_links(mainUrl: str) -> list:
    logger.debug('Scraping for maintenance page links', url=mainUrl)

    page_response = requests.get(mainUrl)
    page_response.raise_for_status()

    interruption_links = pageprocessor.extract_maintenance_links(page_response.content)

    return interruption_links


def fetch_alert_details(maint_urls: list, repo: AlertRepository) -> Alert:
    alert_type = 'interruption'

    for maint_page in maint_urls:
        # get id from end of url path
        id = pathlib.PurePosixPath(urlparse(maint_page).path).parts[-1]

        logger.debug('Checking repository for alert', id=id)
        savedAlert = repo.get(id)
        if savedAlert is None:
            logger.info('New alert detected', id=id)

            logger.debug('Scraping maintenance page', url=maint_page)
            page_response = requests.get(maint_page)
            page_response.raise_for_status()
            maint_info = pageprocessor.extract_interruption_info(page_response.text)

            if maint_info:
                alert = Alert(id, alert_type, datetime.datetime.utcnow(),
                              maint_info["title"], maint_info["content"])
                yield alert
            else:
                logger.debug('Processing page failed, skipping', url=maint_page)
                yield None
        else:
            logger.info('Alert already processed',  id=id)
            yield None


def publish_alert(alert: Alert):

    with DaprClient() as client:
        msg = {
            "id": alert.id,
            "notificationType": alert.notificationType
        }
        logger.debug("Publishing alert to binding", binding=MSG_BINDING_NAME, data=msg)
        client.invoke_binding(MSG_BINDING_NAME, "create", json.dumps(msg))


if __name__ == "__main__":
    while True:
        main()
        logger.info("Waiting to run again", seconds=SLEEP_SECONDS)
        time.sleep(SLEEP_SECONDS)
