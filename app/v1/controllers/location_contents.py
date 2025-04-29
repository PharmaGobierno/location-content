from time import time
from typing import Iterator

from infra.mongodb import MongoDbManager
from infra.pubsub import PubsubManager
from pharmagob.mongodb_repositories.base import BaseMongoDbRepository
from pharmagob.mongodb_repositories.locations import LocationRepository
from pharmagob.mongodb_repositories.shipment_details import ShipmentDetailRepository
from pharmagob.v1.models.location_content import LocationContentModel
from pharmagob.v1.models.messages.pubsub_msgs import LocationContentStatesPubsubMessage
from pharmagob.v1.models.minified import min_models
from pharmagob.v1.models.shipment import ShipmentModel
from pharmagob.v1.services.location_contents import LocationContentService
from pharmagob.v1.services.locations import LocationModel, LocationService
from pharmagob.v1.services.shipment_details import (
    ShipmentDetailModel,
    ShipmentDetailService,
)
from presentation.errors import ErrorLocationEnum, NotFoundError
from utils.logger import Logger

from app.v1.schemas.shipment_status import ShipmentStatusDataPayload

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
        verbose: bool = True,
    ) -> None:
        self.db_manager = db
        self.pubsub_manager = pubsub
        self.location_content_srv = LocationContentService(
            BaseMongoDbRepository(db, LocationContentModel.get_entity_name())  # type: ignore
        )
        self.location_srv = LocationService(
            LocationRepository(db, LocationModel.get_entity_name())  # type: ignore
        )
        self.shipment_detail_srv = ShipmentDetailService(
            ShipmentDetailRepository(db, ShipmentDetailModel.get_entity_name())  # type: ignore
        )
        super().__init__(logger=logger, verbose=verbose)

    def get_location(self, data: ShipmentModel) -> LocationModel:
        _, locations = self.location_srv.get_by_umu_id(data.umu_id)
        first_location = next(iter(locations or []), None)
        if first_location is None:
            raise NotFoundError(
                details="Location not found",
                location=ErrorLocationEnum.BODY,
                parameter="umu_id",
            )
        return LocationModel(**first_location)

    def get_shipment_details(self, data: ShipmentModel) -> Iterator[dict]:
        _, shipment_details = self.shipment_detail_srv.get_by_shipment_id(data._id)
        return shipment_details

    def save_location_contents(
        self,
        location: LocationModel,
        pubsub_message: ShipmentStatusDataPayload,
        shipment_details: Iterator[dict],
    ) -> list[LocationContentModel]:
        res: list[LocationContentModel] = []
        for detail in shipment_details:
            detail_model = ShipmentDetailModel.from_dict(data=detail)
            model = LocationContentModel(
                umu_id=pubsub_message.payload.umu_id,
                order_number=detail_model.shipment.order_number,
                lot=detail_model.lot,
                quantity=detail_model.quantity,
                item=min_models.ItemlMin(
                    id=detail_model.item.id,
                    foreign_id=detail_model.item.foreign_id,
                    name=detail_model.item.name,
                ),
                location=min_models.LocationMin(
                    id=location._id,
                    umu_id=location.umu_id,
                    label_code=location.label_code,
                ),
                shipment_details=[
                    min_models.ShipmentDetailMin(
                        id=detail_model._id,
                        umu_id=pubsub_message.payload.umu_id,
                        item_id=detail_model.item.id,
                        quantity=detail_model.quantity,
                        shipment_id=detail_model.shipment.id,
                        shipment_order_number=detail_model.shipment.order_number,
                        shipment_load_id=detail_model.shipment.load_id,
                        lot=detail_model.lot,
                        brand=detail_model.brand,
                    )
                ],
                last_author=min_models.UserMin(
                    id=pubsub_message.author.id,
                    umu_id=pubsub_message.author.umu_id,
                    display_name=pubsub_message.author.display_name,
                ),
            )
            res.append(model)
            self.location_content_srv.set(
                entity_id=model._id, entity=model, write_only_if_insert=True
            )

        return res

    def publish_location_content_states(
        self, location_content: list[LocationContentModel]
    ) -> None:
        """Publish location content states to PubSub."""
        for content in location_content:
            message = LocationContentStatesPubsubMessage(
                payload=content,
                state="INTEGRATED",  # TODO: Enum
                origin_timestamp=round(time() * 1000),
                published_at=round(time() * 1000),
                author=min_models.UserMin(
                    id=content.last_author.id,
                    umu_id=content.last_author.umu_id,
                    display_name=content.last_author.display_name,
                ),
            )
            attributes: dict = {"version": message.version, "state": message.state}
            self.pubsub_manager.publish(
                LocationContentStatesPubsubMessage.topic(),
                message=message.dict(),
                attributes=attributes,
            )
