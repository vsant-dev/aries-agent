from aries_cloudagent.messaging.base_handler import (
    BaseHandler,
    BaseResponder,
    RequestContext
)

class DataReceivedHandler(BaseHandler):
    async def handle(self, context: RequestContext, responder: BaseResponder):

        payload = {
            "connection_id": context.connection_record.connection_id,
            "data_attach": context.message.data_attach,
            "state": "data_received"
        }

        print(payload)
        
        await context.profile.notify("acapy::data_exchange::data_received", payload)