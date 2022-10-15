from structlog import get_logger
import os
import pathlib
import requests
from urllib.parse import urlparse
import datetime
from dataclasses import asdict

from domain import Alert, AlertRepository
from storage.CosmosAlertRepository import CosmosAlertRepository

from scrape import pageprocessor

logger = get_logger()


def main():
    # get main URL and DB conection info
    try:
        main_url = os.environ["URL"]
        db_endpoint = os.environ["DB_ENDPOINT"]
        db_name = os.environ["DB_NAME"]
    except KeyError as ke:
        logger.fatal('Missing required environment variable', var=ke.args[0])
        exit(1)

    alertRepo = CosmosAlertRepository(db_endpoint, db_name)

    maint_urls = scrape_maint_links(main_url)
    logger.info('Found maintenance links', count=len(maint_urls))

    for maint_page in fetch_alert_details(maint_urls, alertRepo):
        if maint_page:
            logger.debug('Saving alert details', **asdict(maint_page))
            alertRepo.save(maint_page)
            logger.info('Saved alert', id=maint_page.id)


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

            alert = Alert(id, alert_type, datetime.datetime.utcnow(),
                          maint_info["title"], maint_info["content"])
            yield alert
        else:
            logger.debug('Alert already processed',  id=id)
            yield None


if __name__ == "__main__":
    main()
