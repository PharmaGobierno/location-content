from typing import Iterator, Tuple

from infra.mongodb import MongoDbManager
from pharmagob.mongodb_repositories.base import BaseMongoDbRepository
from pharmagob.v1.models.location import LocationModel
from pharmagob.v1.models.location_content import LocationContentModel
from pharmagob.v1.models.minified import min_models
from pharmagob.v1.services.location_contents import LocationContentService
from pharmagob.v1.services.shipment_details import (
    ShipmentDetailModel,
    ShipmentDetailService,
)
from pharmagob.v1.services.shipments import ShipmentModel, ShipmentService
from utils.logger import Logger

from app.v1.schemas.shipment_status import Shipment

from ._base import BaseController


class LocationContentsController(BaseController):
    db_manager: MongoDbManager

    def __init__(
        self, *, logger: Logger, db: MongoDbManager, verbose: bool = True
    ) -> None:
        self.db_manager = db
        self.location_content_srv = LocationContentService(
            BaseMongoDbRepository(db, LocationContentModel.get_entity_name())  # type: ignore
        )
        self.shipment_srv = ShipmentService(
            BaseMongoDbRepository(db, ShipmentModel.get_entity_name())  # type: ignore
        )
        self.shipment_detail_srv = ShipmentDetailService(
            BaseMongoDbRepository(db, ShipmentDetailModel.get_entity_name())  # type: ignore
        )
        super().__init__(logger=logger, verbose=verbose)

    def get_location(self, data: Shipment) -> LocationModel:
        return self.shipment_srv.get(data.id)

    def get_shipment_details(self, data: Shipment) -> Tuple[int, Iterator[dict]]:
        return self.shipment_detail_srv.get_by_shipment_id(data.id)

    def save_location_contents(
        self,
        location: LocationModel,
        shipment: ShipmentModel,
        shipment_details: Iterator[dict],
    ) -> list[LocationContentModel]:
        res: list[LocationContentModel] = []
        for detail in shipment_details:
            model = LocationContentModel(
                umu_id=shipment.umu_id,
                quantity=detail.get("quantity", ""),
                shipment_detail=min_models.ShipmentDetailMin(
                    id=shipment._id,
                    umu_id=shipment.umu_id,
                    lot=detail.get("lot", ""),
                    brand=detail.get("brand"),
                ),
                user=shipment.user,
                item=detail.get("item"),
                location=min_models.LocationMin(
                    id=detail.get("location_id"),
                    umu_id=shipment.umu_id,
                    name=detail.get("location_name"),
                ),
            )
            self.location_content_srv.create(model)
        return model
