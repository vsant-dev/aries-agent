from aries_cloudagent.protocols.didcomm_prefix import DIDCommPrefix

DATA = "data_webhooks/1.0/data"

PROTOCOL_PACKAGE = "data_webhooks_protocol"

MESSAGE_TYPES = DIDCommPrefix.qualify_all(
    {
        DATA: f"{PROTOCOL_PACKAGE}.messages.data.DataSentMessage"
    }
)
