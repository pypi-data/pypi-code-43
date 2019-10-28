import attr


@attr.s(slots=True)
class SendEvent:
    payload = attr.ib(type=dict)
    event_name = attr.ib(type=str)


@attr.s(slots=True)
class SendResponse:
    success = attr.ib(type=bool)
