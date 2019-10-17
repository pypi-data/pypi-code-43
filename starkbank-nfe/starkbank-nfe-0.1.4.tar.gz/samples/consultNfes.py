# -*- coding: utf-8 -*-
from nfe.gateways.saopaulo import SaopauloGateway


parameters = {
    "CPFCNPJRemetente": "20018183000180",
    "Inscricao": "57038597",
    "dtInicio": "2019-09-15",
    "dtFim": "2019-09-30",
}

json, status = SaopauloGateway.consultNfes(
    privateKey=open("../static/rsaKey.pem").read(),
    certificate=open("../static/certificate.crt").read(),
    **parameters
)

print(json)
print(status)
