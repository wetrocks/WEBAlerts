from structlog import get_logger
import sys
import os
import pathlib
import requests
from urllib.parse import urlparse
from dataclasses import dataclass
import datetime


from scrape import pageprocessor

logger = get_logger()

@dataclass(frozen=True)
class Alert:
    id: str
    notificationType: str
    created: datetime.datetime
    title: str
    content: str


def main():
    # get from env var or cmdline
    mainUrl = sys.argv[1] if len(sys.argv) >=2 else os.getenv("URL")

    if mainUrl == None:
        print('No url specified on cmdline or URL env var')
        exit(1)

    maint_urls = scrape_maint_links(mainUrl)
    logger.info('Found maintenance links', count=len(maint_urls))

    for maint_page in fetch_alert_details(maint_urls):
        print(maint_page)


def scrape_maint_links(mainUrl: str) -> list:
    logger.debug('Scraping for maintenance page links', url=mainUrl)

    page_response = requests.get(mainUrl)
    page_response.raise_for_status()

    interruption_links = pageprocessor.extract_maintenance_links(
        page_response.content)

    return interruption_links


def fetch_alert_details(maint_urls: list) -> Alert:
    alert_type = 'interruption'

    for maint_page in maint_urls:
        logger.debug('Scraping maintenance page', url=maint_page)

        # get id from end of url path
        id = pathlib.PurePosixPath(urlparse(maint_page).path).parts[-1]
        
        page_response = requests.get(maint_page)
        page_response.raise_for_status()
        maint_info = pageprocessor.extract_interruption_info(page_response.text)

        alert = Alert(id, alert_type, datetime.datetime.utcnow(),
                      maint_info["title"], maint_info["content"])
        yield alert


if __name__ == "__main__":
    main()
