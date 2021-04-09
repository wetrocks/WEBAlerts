import datetime
import logging

import azure.functions as func
import azure.durable_functions as df

async def main(mytimer: func.TimerRequest, starter: str) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    orchestration_name =  "WEBScrapeOrchestrator"
    client = df.DurableOrchestrationClient(starter)
    instance_id = await client.start_new(orchestration_name, None, None)

    logging.info(f"Started orchestration with ID = '{instance_id}' at '{utc_timestamp}'")
