from typing import Optional

from infra.mongodb import MongoDbConnectionConf, MongoDbManager


class DataBase:
    manager: Optional[MongoDbManager] = None


db = DataBase()


async def get_manager():
    return db.manager


async def open_connection():
    conn_conf = MongoDbConnectionConf(connection_string={"authSource": "admin"})
    db.manager = MongoDbManager(connection_conf=conn_conf)


async def close_connection():
    if db.manager is not None:
        db.manager.close()
