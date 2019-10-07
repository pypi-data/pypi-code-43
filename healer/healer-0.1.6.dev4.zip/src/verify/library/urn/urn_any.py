
import uuid
from urllib.parse import urlparse


# Returns a tuple (<uuid>, <prefix>)
def urn_uuid_decode(urn_str):
    parts = urn_str.split(":")

    # Already supported format
    if len(parts) < 4:
        return uuid.UUID(urn_str), None

    return uuid.UUID("%s:%s:%s" % (parts[0], parts[-2], parts[-1])), ":".join(parts[1:-2])


# same UUID in different flavors
x = "0269803d50c446b09f5060ef7fe3e22b"
y = "urn:uuid:0269803d-50c4-46b0-9f50-60ef7fe3e22b"
z = "urn:vendor:processor:uuid:0269803d-50c4-46b0-9f50-60ef7fe3e22b"

print(urn_uuid_decode(x))
print(urn_uuid_decode(y))
print(urn_uuid_decode(z))

print(uuid.UUID("urn:uuid:0269803d-50c4-46b0-9f50-60ef7fe3e22b"))

print(urlparse("urn:hello:some-id"))
print(urlparse("tcp://host:port"))
