import logging
import sendgrid
import azure.functions as func
import os
import python_http_client
import python_http_client.exceptions
import json

db_name = "cosmos-notificationdb"
 
def main(documents: func.DocumentList) -> None:
    if documents:
        logging.info('Document id: %s', documents[0]['id'])
        db_document = documents[0]

        sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
        sender_id = os.environ.get('SENDGRID_SENDER_ID')
        suppression_group_id = os.environ.get('SENDGRID_SUPPGRP_ID')
        list_id = os.environ.get('SENDGRID_LIST_ID')

        subject_txt = db_document.get("title", "")

        #build SG API call to create a new single send
        singlesend_data = {
            "name":  db_document["id"],
            "send_to": {
                "list_ids": [list_id],
                "all": False
            },
            "email_config": {
                "subject": f"WEB Notification{': ' if subject_txt != '' else ''}{subject_txt}",
                "html_content": db_document["content"],
                "sender_id": int(sender_id),
                "suppression_group_id": int(suppression_group_id)
            }
        }

        try:
            #create new single send
            singlesend_response = sg.client.marketing.singlesends.post(request_body=singlesend_data)
            singlesend = json.loads(singlesend_response.body)
            logging.info(f"Created new single send: {singlesend['id']}")

            #schedule single send for now
            sched_response = sg.client.marketing.singlesends._(singlesend["id"]).schedule.put(request_body= {"send_at": "now"})
            logging.info(sched_response.body)
        except Exception as e:
            logging.error(e.body)
