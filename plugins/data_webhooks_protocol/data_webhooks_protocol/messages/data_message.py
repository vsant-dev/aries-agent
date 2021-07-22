
from marshmallow import EXCLUDE, fields
from aries_cloudagent.messaging.agent_message import AgentMessage, AgentMessageSchema
from aries_cloudagent.messaging.decorators.attach_decorator import (
    AttachDecorator,
    AttachDecoratorSchema
)

from ..message_types import PROTOCOL_PACKAGE, DATA

HANDLER_CLASS = (
    f"{PROTOCOL_PACKAGE}.handlers.data_received_handler.DataReceivedHandler"
)

class DataMessage(AgentMessage):
    class Meta:
        handler_class = HANDLER_CLASS
        message_type = DATA
        schema_class = "DataMessageSchema"

    def __init__(
        self,
        data_attach = AttachDecorator,
        **kwargs,
    ):
        """Initialize Handshake Reuse message object."""
        super().__init__(**kwargs)
        self.data_attach = data_attach


class DataMessageSchema(AgentMessageSchema):
    class Meta:
        model_class = DataMessage
        unknown = EXCLUDE

    data_attach = fields.Nested(
        AttachDecoratorSchema,
        data_key="data~attach",
        description="Batch of data from agent", 
        required=True
    )