import datetime
import logging

import azure.functions as func
from lxml import html
from lxml import etree
import requests
import json



def main(url: str) -> dict:
   # url = "https://www.webbonaire.com/en/announcement-electricity-interruption-thursday-february-18th-2021/"
 
    page_repsonse = requests.get(url)
    page_repsonse.raise_for_status()

    page_tree = html.fromstring(page_repsonse.content)
    main_element = page_tree.xpath('body//main[1]')
    if len(main_element) != 1:
        logging.warning("No main element found")
        return

    main_element = main_element[0]
    title = "".join(main_element.xpath('h1[1]/text()'))

    interruption = {
        "url": url,
        "title": title,
        "content": str(etree.tostring(main_element))
    }

    return interruption


