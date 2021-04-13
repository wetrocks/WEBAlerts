import datetime
import json
import logging
import os
import pathlib
from urllib.parse import urlparse

import azure.functions as func
import requests
from azure.cosmos import CosmosClient
from lxml import etree, html
import datetime
from shared_code import html_helper


def get_container_client():
    conn_str = os.environ["DBConnection"]

    client = CosmosClient.from_connection_string(conn_str) \
                         .get_database_client("webalert_dev") \
                         .get_container_client("notifications")

    return client

def scrape_content(interruption_url: str) -> str:
    page_repsonse = requests.get(interruption_url)
    page_repsonse.raise_for_status()
    html_helper.extract_interruption_info(page_repsonse.content)


PARTITION_KEY_VAL = "interruption"
container_client = get_container_client()
    
def main(url: str) -> dict:

    # get id from end of url
    docId = pathlib.PurePosixPath(urlparse(url).path).parts[-1]

    # check if exists in db
    dbItem = container_client.query_items(
        query='SELECT * FROM notifications p WHERE p.id = @docId',
        parameters=[dict(name="@docId", value=docId)],
        partition_key=PARTITION_KEY_VAL,
        max_item_count=1
    )

    returnVal = { "url": url }
    if any(dbItem):
        returnVal["created"] = False
    else:
        pageContent = scrape_content(url)

        newItem = {
            "id": docId,
            "notificationType": PARTITION_KEY_VAL,
            "created": datetime.datetime.utcnow().isoformat(),
            "content": pageContent
        }

        container_client.create_item(newItem)
        
        returnVal["created"] = True

    return returnVal
