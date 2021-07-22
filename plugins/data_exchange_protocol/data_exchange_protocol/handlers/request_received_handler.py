from aries_cloudagent.wallet.base import BaseWallet
import os
from aries_cloudagent.messaging.decorators.attach_decorator import AttachDecorator, AttachDecoratorData
from aries_cloudagent.messaging.base_handler import (
    BaseHandler,
    BaseResponder,
    RequestContext
)

from ..messages.data_sent import DataSentMessage

class RequestReceivedHandler(BaseHandler):
    def __init__(self):
        pass

    async def handle(self, context: RequestContext, responder: BaseResponder):
        
        connection_record = context.connection_record
        connection_id = connection_record.connection_id

        session = await context.session()
        wallet = session.inject(BaseWallet)

        my_info = await wallet.get_public_did()

        data = "SGVsbG8gV29ybGQ="
        attach = AttachDecorator(data=AttachDecoratorData(base64_=data))
        
        await attach.data.sign(my_info.verkey, wallet)

        message = DataSentMessage(attached_data=attach)

        outbound_message = await responder.create_outbound(message, connection_id=connection_id)
        await responder.send_outbound(outbound_message)
        
        await context.profile.notify("acapy::data_exchange::request_received", {})