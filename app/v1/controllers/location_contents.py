from time import time

from infra.mongodb import MongoDbManager
from infra.pubsub import PubsubManager
from pharmagob.mongodb_repositories.location_contents import LocationContentRepository
from pharmagob.v1.models.location_content import LocationContentModel
from pharmagob.v1.models.messages.pubsub_msgs import LocationContentStatesPubsubMessage
from pharmagob.v1.services.location_contents import LocationContentService
from utils.logger import Logger

from app.v1.schemas.location_contents import ShipmentStatusMessage

from ._base import BaseController


class LocationContentsController(BaseController):
    pubsub_manager: PubsubManager
    db_manager: MongoDbManager

    def __init__(
        self,
        *,
        logger: Logger,
        db: MongoDbManager,
        pubsub: PubsubManager,
        verbose: bool = True
    ) -> None:
        self.db_manager = db
        self.pubsub_manager = pubsub
        self.location_content_service = LocationContentService(
            LocationContentRepository(db, LocationContentModel.get_entity_name())
        )
        super().__init__(logger=logger, verbose=verbose)

    def save_location_contents(
        self, data: ShipmentStatusMessage
    ) -> LocationContentModel:
        model = LocationContentModel(
            umu_id=data.payload.umu,
            quantity=data.payload.box_quantity,
            shipment_detail={
                "id": data.payload.order_id,
                "umu_id": data.payload.umu,
                "lot": data.payload.load,
                "brand": data.payload.route,
            },
            user=data.payload.user,
            item=data.payload.skus[0],
        )
        self.location_content_service.create(model)
        return model

    def publish_location_contents(self, location: LocationContentModel):
        message = LocationContentStatesPubsubMessage(
            payload=location,
            status=location.status,
            published_at=round(time() * 1000),
            author=location.user,
        )
        attributes: dict = {"version": message.version, "status": location.status}
        self.pubsub_manager.publish(
            LocationContentStatesPubsubMessage.topic(),
            message=message.dict(),
            attributes=attributes,
        )
