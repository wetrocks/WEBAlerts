# This function is not intended to be invoked directly. Instead it will be
# triggered by an orchestrator function.
# Before running this sample, please:
# - create a Durable orchestration function
# - create a Durable HTTP starter function
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt

import logging
from lxml import html
import requests

def main(notUsed: str) -> str:
    page_repsonse = requests.get('https://www.webbonaire.com/news/?lang=en')
    page_repsonse.raise_for_status()

    page_tree = html.fromstring(page_repsonse.content)
    interruption_links = page_tree.xpath('//*[p[contains(text(), "Planned interruption")]]/ul/li//a/@href')

    logging.debug('Found links: %s', interruption_links)

    return interruption_links
