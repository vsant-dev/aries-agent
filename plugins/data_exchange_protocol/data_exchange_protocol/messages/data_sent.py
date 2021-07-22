
from marshmallow import EXCLUDE, fields
from aries_cloudagent.messaging.agent_message import AgentMessage, AgentMessageSchema
from aries_cloudagent.messaging.decorators.attach_decorator import (
    AttachDecorator,
    AttachDecoratorSchema
)

from ..message_types import PROTOCOL_PACKAGE, DATA_SENT

HANDLER_CLASS = (
    f"{PROTOCOL_PACKAGE}.handlers.data_received_handler.DataReceivedHandler"
)

class DataSentMessage(AgentMessage):
    class Meta:
        handler_class = HANDLER_CLASS
        message_type = DATA_SENT
        schema_class = "DataSentMessageSchema"

    def __init__(
        self,
        attached_data = AttachDecorator,
        **kwargs,
    ):
        """Initialize Handshake Reuse message object."""
        super().__init__(**kwargs)
        self.attached_data = attached_data


class DataSentMessageSchema(AgentMessageSchema):
    class Meta:
        model_class = DataSentMessage
        unknown = EXCLUDE

    attached_data = fields.Nested(
        AttachDecoratorSchema,
        data_key="data~attach",
        description="Batch of data from agent", 
        required=True
    )