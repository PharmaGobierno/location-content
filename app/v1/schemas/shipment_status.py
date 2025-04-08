"""
* :description: Schema for shipment-status pubsub msg requests.
"""

from pydantic import BaseModel, ConfigDict, Field, PositiveInt


class Author(BaseModel):
    id: str
    umu_id: str
    display_name: str


class Shipment(BaseModel):
    id: str = Field(alias="_id")
    umu_id: str
    foreign_id: str
    order_id: str
    status: str


class ShipmentStatusDataPayload(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    payload: Shipment
    status: str
    origin_timestamp: PositiveInt
    origin: str = "TODO"  # TODO
    author: Author
    version: str
