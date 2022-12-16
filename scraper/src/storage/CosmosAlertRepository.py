from azure.cosmos import CosmosClient
from domain import Alert
from datetime import datetime
from structlog import get_logger


class CosmosAlertRepository:

    conn_str: str = ''
    db_name: str = ''
    container = 'notifications'
    container_client = None
    logger = None

    def __init__(self, connStr: str, dbName: str):
        self.logger = get_logger()

        self.conn_Str = connStr
        self.db_name = dbName

        self.container_client = self.__get_container_client(self.conn_Str, self.db_name, self.container)

    def get(self, id: str) -> Alert:
        self.logger.debug('Query db for notification', db_name=self.db_name, id=id)

        # check if exists in db
        dbItems = self.container_client.query_items(
            query='SELECT * FROM notifications p WHERE p.id = @docId',
            parameters=[dict(name="@docId", value=id)],
            partition_key='interruption',
            max_item_count=1
        )

        dbAlert = next(dbItems, None)
        if not dbAlert:
            return None

        return Alert(
                dbAlert["id"],
                dbAlert["notificationType"],
                datetime.fromisoformat(dbAlert["created"]),
                dbAlert["title"],
                dbAlert["content"]
            )

    def save(self, alert: Alert) -> dict:

        newItem = {
            "id": alert.id,
            "notificationType": alert.notificationType,
            "created": alert.created.isoformat(),
            "title": alert.title,
            "content": alert.content
        }

        return self.container_client.create_item(newItem)

    def __get_container_client(self, conn_str: str, db_name: str, db_container: str):
        client = CosmosClient.from_connection_string(conn_str) \
                            .get_database_client(db_name) \
                            .get_container_client(db_container)

        return client
