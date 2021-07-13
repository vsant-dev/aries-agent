from .messages.request import RequestMessage
from aiohttp import web
from aiohttp_apispec import docs

from aries_cloudagent.admin.request_context import AdminRequestContext
from aries_cloudagent.storage.error import StorageNotFoundError
from aries_cloudagent.connections.models.conn_record import ConnRecord

@docs(tags=["data"], summary="Get Data")
async def get_data_handler(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    connection_id = request.match_info["conn_id"]
    outbound_handler = request["outbound_message_router"]

    try: 
        async with context.session() as session :
            connection = await ConnRecord.retrieve_by_id(session, connection_id)


    except StorageNotFoundError as err:
        raise web.HTTPNotFound(reason=err.roll_up) from err

    if not connection.is_ready:
        raise web.HTTPBadRequest(reason=f"Connection {connection_id} is not ready")

    request_message = RequestMessage()
    await outbound_handler(request_message, connection_id=connection_id)

    return web.json_response({})

async def register(app: web.Application):
    app.add_routes([web.get("/connections/{conn_id}/data_exchange/1.0/request", get_data_handler)])