from typing import Generator
from unittest.mock import Mock

from infra.mongodb import MongoDbConnectionConf, MongoDbManager
from infra.pubsub import PubsubConnectionConf, PubsubManager
from pytest import fixture
from starlette.testclient import TestClient

from main import app


@fixture
def mocked_repository(mocker) -> Mock:
    mocked_repo = Mock()
    mocked_conf = Mock()
    mocker.patch.object(MongoDbConnectionConf, "__new__", return_value=mocked_conf)
    mocker.patch.object(MongoDbManager, "__new__", return_value=mocked_repo)
    return mocked_repo


@fixture
def mocked_publisher(mocker) -> Mock:
    mocked_publisher = Mock()
    mocked_conf = Mock()
    mocker.patch.object(PubsubConnectionConf, "__new__", return_value=mocked_conf)
    mocker.patch.object(PubsubManager, "__new__", return_value=mocked_publisher)
    return mocked_publisher


@fixture
def client() -> Generator:
    with TestClient(app) as test_client:
        yield test_client
