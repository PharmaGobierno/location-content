"""
* :description: Namespace API
"""

from fastapi import APIRouter, Depends, Request, Response, status

from app.libs import mongo_handler, pubsub_handler
from app.v1.controllers.location_contents import LocationContentsController
from app.v1.exceptions.handler import exception_handler
from app.v1.schemas.location_contents import ShipmentStatusMessage

router = APIRouter()


# ? [POST] <— /async-msg/location-contents
@router.post("")
@exception_handler(response_status=status.HTTP_200_OK)
async def post_async_msg(
    request: Request,
    response: Response,
    db_manager=Depends(mongo_handler.get_manager),
    pubsub_manager=Depends(pubsub_handler.get_manager),
) -> dict:
    """Endpoint ..."""
    payload = await request.json()
    message = ShipmentStatusMessage(**payload)
    location_contents_ctrl = LocationContentsController(
        logger=request.state.logger, db=db_manager, pubsub=pubsub_manager
    )
    res_model = location_contents_ctrl.save_location_contents(message)
    location_contents_ctrl.publish_integration(res_model)
    return {"location_contents": res_model.dict()}
