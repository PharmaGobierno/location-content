"""
* :description: Schema for location-contents msg requests.
"""

from typing import List

from pydantic import BaseModel, PositiveInt


class LoteInfo(BaseModel):
    lot_number: str
    expiration_date: str
    quantity: PositiveInt


class Sku(BaseModel):
    sku: str
    brand: str
    quantity: PositiveInt
    avg_cost: float
    lote_info: List[LoteInfo]


class User(BaseModel):
    user_id: str


class ShipmentStatusPayload(BaseModel):
    order_number: str
    order_id: str
    umu: str
    load: str
    route: str
    box_quantity: PositiveInt
    application_date: str  # TODO: change for a validator of str to date
    user: User
    status: str  # TODO: change for a ENUM
    shipment_type: str  # TODO: change for a ENUM
    skus: List[Sku]

    class Config:
        use_enum_values = True


class ShipmentStatusMessage(BaseModel):
    payload: ShipmentStatusPayload
    origin: str
    lat: float = 0.0
    lng: float = 0.0
    published_at: PositiveInt
    version: str

    class Config:
        use_enum_values = True
