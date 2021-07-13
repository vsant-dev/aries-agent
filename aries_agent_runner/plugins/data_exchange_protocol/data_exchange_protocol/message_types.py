from aries_cloudagent.protocols.didcomm_prefix import DIDCommPrefix

REQUEST = "data_exchange/1.0/request"
DATA_SENT = "data_exchange/1.0/data_sent"

PROTOCOL_PACKAGE = "data_exchange_protocol"

MESSAGE_TYPES = DIDCommPrefix.qualify_all(
    {
        REQUEST: f"{PROTOCOL_PACKAGE}.messages.request.RequestMessage",
        DATA_SENT: f"{PROTOCOL_PACKAGE}.messages.data_sent.DataSentMessage"
    }
)
