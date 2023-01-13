from common.domain import Alert, AlertRepository
from common.storage import CosmosAlertRepository
from fastapi import FastAPI
from pydantic import BaseModel, BaseSettings
from structlog import get_logger
from sendgrid import SendGridAPIClient
from python_http_client.exceptions import HTTPError
import json


class Settings(BaseSettings):
    db_endpoint: str
    db_name: str
    sendgrid_api_key: str
    sendgrid_sender_id: str
    sendgrid_suppgrp_id: str
    sendgrid_list_id: str


class AlertMessage(BaseModel):
    id: str
    notificationType: str


app = FastAPI()
logger = get_logger()
settings = Settings(_env_file='.env')


# Needed for dapr
@app.options("/alertqueue")
async def handleAlertMsgOptions():
    return {"canprocess": True}


@app.post("/alertqueue")
async def handleAlertMsg(alertMsg: AlertMessage):
    logger.info("Recieved alert message", id=alertMsg.id)

    try:
        repo: AlertRepository = CosmosAlertRepository(settings.db_endpoint, settings.db_name)
        alert: Alert = repo.get(alertMsg.id)
        if alert:
            logger.info("Sending email for alert", details=alert)
            sendAlertEmail(alert)
        else:
            logger.warn("Alert not found in database", id=alertMsg.id)
    except HTTPError as httpe:
        logger.error("SendGrid API error:", **(httpe.to_dict))
    except Exception as e:
        logger.error("Error processing message", exception=e)


def sendAlertEmail(alert: Alert):

    # build SG API call to create a new single send
    singlesend_data = {
        "name":  alert.id,
        "send_to": {
            "list_ids": [settings.sendgrid_list_id],
            "all": False
        },
        "email_config": {
            "subject": f"WEB Notification{': ' if alert.title != '' else ''}{alert.title}",
            "html_content": alert.content,
            "sender_id": int(settings.sendgrid_sender_id),
            "suppression_group_id": int(settings.sendgrid_suppgrp_id)
        }
    }

    sg = SendGridAPIClient(api_key=settings.sendgrid_api_key)
    # create new single send
    singlesend_response = sg.client.marketing.singlesends.post(request_body=singlesend_data)
    singlesend = json.loads(singlesend_response.body)
    logger.info("Created new single send", id=singlesend['id'])

    # schedule single send for now
    sched_response = sg.client.marketing.singlesends._(singlesend["id"]).schedule.put(request_body={"send_at": "now"})
    logger.info("Scheduled single send", response=sched_response.body)
