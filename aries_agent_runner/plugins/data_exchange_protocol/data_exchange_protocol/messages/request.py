
from marshmallow import EXCLUDE
from aries_cloudagent.messaging.agent_message import AgentMessage, AgentMessageSchema

from ..message_types import PROTOCOL_PACKAGE, REQUEST

HANDLER_CLASS = (
    f"{PROTOCOL_PACKAGE}.handlers.request_received_handler.RequestReceivedHandler"
)

class RequestMessage(AgentMessage):
    class Meta:
        handler_class = HANDLER_CLASS
        message_type = REQUEST
        schema_class = "RequestMessageSchema"

    def __init__(
        self,
        **kwargs,
    ):
        """Initialize Handshake Reuse message object."""
        super().__init__(**kwargs)

class RequestMessageSchema(AgentMessageSchema):
    class Meta:
        model_class = RequestMessage
        unknown = EXCLUDE