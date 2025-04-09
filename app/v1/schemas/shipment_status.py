"""
* :description: Schema for shipment-status pubsub msg requests.
"""

from pharmagob.v1.models.shipment import ShipmentModel
from pydantic import BaseModel, ConfigDict, PositiveInt


class Author(BaseModel):
    id: str
    umu_id: str
    display_name: str


class ShipmentStatusDataPayload(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    payload: ShipmentModel
    status: str
    origin_timestamp: PositiveInt
    origin: str = "TODO"  # TODO
    author: Author
    version: str
