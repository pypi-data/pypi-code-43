# -*- coding: utf-8 -*-
from nfe.gateways.saopaulo import SaopauloGateway


parameters = {
    "CPFCNPJRemetente": "20018183000180",
    "InscricaoPrestador": "57038597",
    "NumeroNFe": "306"
}

json, status = SaopauloGateway.cancelRps(
    privateKey=open("../static/rsaKey.pem").read(),
    certificate=open("../static/certificate.crt").read(),
    **parameters
)

print(json)
print(status)
