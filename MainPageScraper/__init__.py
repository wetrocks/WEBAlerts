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
from shared_code import html_helper

def main(notUsed: str) -> str:
    page_response = requests.get('https://www.webbonaire.com/news/?lang=en')
    page_response.raise_for_status()

    interruption_links = html_helper.extract_maintenance_links(page_response.content)

    logging.debug('Found links: %s', interruption_links)

    return interruption_links
