from aries_cloudagent.messaging.base_handler import (
    BaseHandler,
    BaseResponder,
    RequestContext
)

class DataReceivedHandler(BaseHandler):
    async def handle(self, context: RequestContext, responder: BaseResponder):

        payload = {
            "connection_id": context.connection_record.connection_id,
            "attached_data": context.message.attached_data,
            "state": "data_sent"
        }
        
        await context.profile.notify("acapy::data_exchange::data_received", payload)