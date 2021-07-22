
from aries_cloudagent.core.profile import ProfileSession
from datetime import datetime
from aiohttp_apispec.decorators.request import request_schema

from aries_cloudagent.connections.models.conn_record import ConnRecord
from aries_cloudagent.admin.request_context import AdminRequestContext
from aries_cloudagent.storage.error import StorageError
from aries_cloudagent.messaging.models.base import BaseModelError

from plugins.data_webhooks_protocol.data_webhooks_protocol.messages.data_message import DataMessageSchema

from aiohttp import web 
from aiohttp_apispec import (
    docs,
    request_schema,
)

from .models.iot_device_data import IOTDeviceDataSchema

def connection_sort_key(conn):
    """Get the sorting key for a particular connection."""

    conn_rec_state = ConnRecord.State.get(conn["state"])
    if conn_rec_state is ConnRecord.State.ABANDONED:
        pfx = "2"
    elif conn_rec_state is ConnRecord.State.INVITATION:
        pfx = "1"
    else:
        pfx = "0"

    return pfx + conn["created_at"]
    
async def get_connections(session: ProfileSession):

    try:
        records = await ConnRecord.query(
            session
        )
        results = [record.serialize() for record in records]
        results.sort(key=connection_sort_key)

    except (StorageError, BaseModelError) as err:
        raise web.HTTPBadRequest(reason=err.roll_up) from err

    return results

@docs(tags=["data_webhook"])
@request_schema(IOTDeviceDataSchema())
async def data_webhook_handler(request: web.BaseRequest):
    
    context: AdminRequestContext = request["context"]
    session = await context.session()

    connections_records_dict = await get_connections(session)

    connection_records = list(map(lambda x: ConnRecord(connection_id=x.get('connection_id')), connections_records_dict))
    
    for connection_record in connection_records:
        metadata = await connection_record.metadata_get(session, 'data_webhook')
        print(metadata)

    return web.json_response({'timestamp': datetime.now().timestamp(), 'status': 'received'})

async def register(app: web.Application):
    app.add_routes([web.post("/webhooks/iot-devices/data", data_webhook_handler)])