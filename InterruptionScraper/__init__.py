import datetime
import logging

import azure.functions as func
from lxml import html
import requests



def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)

    page_repsonse = requests.get('https://www.webbonaire.com/en/')
    page_repsonse.raise_for_status()

    page_tree = html.fromstring(page_repsonse.content)
    interruption_links = page_tree.xpath('//*[p[contains(text(), "Planned interruption")]]/ul/li//a/@href')

    logging.debug('Found links: %s', interruption_links)



