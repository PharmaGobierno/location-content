"""
* :description: Namespace API
"""

from fastapi import APIRouter, Depends, Request, Response, status
from presentation.schemas.pubsub_request import PubsubMessage

from app.libs import mongo_handler
from app.v1.controllers.location_contents import LocationContentsController
from app.v1.exceptions.handler import exception_handler
from app.v1.schemas.shipment_status import ShipmentStatusDataPayload

router = APIRouter()


# ? [POST] <— /async-msg/location-contents
@router.post("/location-contents")
@exception_handler(response_status=status.HTTP_200_OK)
async def post_async_msg(
    request: Request,
    response: Response,
    db_manager=Depends(mongo_handler.get_manager),
) -> dict:
    """Endpoint ..."""
    location_contents_ctrl = LocationContentsController(
        logger=request.state.logger, db=db_manager
    )
    pubsub_msg: PubsubMessage = PubsubMessage(**(await request.json())["message"])
    parsed_msg = location_contents_ctrl.schema_validation(
        ShipmentStatusDataPayload, data=pubsub_msg.decoded_data
    )
    location = location_contents_ctrl.get_location(parsed_msg.payload)
    _, shipment_detail = location_contents_ctrl.get_shipment_details(parsed_msg.payload)
    res_model = location_contents_ctrl.save_location_contents(
        location=location,
        shipment=parsed_msg.payload,
        shipment_details=shipment_detail,
    )
    return {"location_contents": res_model.dict()}
