# -*- coding: utf-8 -*-
from nfe.gateways.saopaulo import SaopauloGateway
# NFSe Provider
taxId = "87654321000198"
providerSubscription = "12345678"  # Provider city subscription

# NFSe Taker
companyName = "SOME COMPANY LTDA"
takerTaxId = "12345678000198"


nota = {
    "CPFCNPJRemetente": "20018183000180",
    "InscricaoPrestador":  "57038597",
    "SerieRPS": "TESTE",
    "NumeroRPS": "9617092019",
    "TipoRPS": "RPS",
    "DataEmissao": "2019-07-09",
    "StatusRPS": "N",
    "TributacaoRPS": "T",
    "ValorServicos": "10",
    "ValorDeducoes": "0",
    "ValorPIS": "0",
    "ValorIR": "0",
    "ValorCSLL": "0",
    "ValorCOFINS": "0",
    "ValorINSS": "0",
    "CodigoServico": "05895",
    "AliquotaServicos": "2",
    "ISSRetido": "false",
    "CPFCNPJTomador": "30134945000167",
    "RazaoSocialTomador": "HUMMINGBIRD HEALTH PRODUCTS",
    "Logradouro": "Núll",
    "NumeroEndereco": "1234567890",
    "ComplementoEndereco": "emissao",
    "Bairro": "Nú11111Nú11111Nú11111Nú11111Nú",
    "Cidade": "3550308",
    "UF": "SP",
    "CEP": "00000000",
    "EmailTomador": "none@nonenonenonenonenonenonenonenonenonenonenonenonenonenonenonenonenone22",
    "Discriminacao": "Teste de emissão automática de NFS-e de boletos prestados",
}


json, status = SaopauloGateway.sendRps(
    privateKey=open("../static/rsaKey.pem").read(),
    certificate=open("../static/certificate.crt").read(),
    **nota
)

print(json)
print(status)
