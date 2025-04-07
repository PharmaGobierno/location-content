from typing import Optional

from infra.pubsub import PubsubConnectionConf, PubsubManager


class Pubsub:
    manager: Optional[PubsubManager] = None


pubsub = Pubsub()


async def get_manager():
    return pubsub.manager


async def open_connection():
    conn_conf = PubsubConnectionConf()
    pubsub.manager = PubsubManager(connection_conf=conn_conf)
