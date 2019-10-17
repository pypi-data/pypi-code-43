# -*- coding: utf-8 -*-

import requests

privateKey = open("../static/rsaKey.pem").read()
certificate = open("../static/certificate.crt").read()


xml = """<?xml version="1.0" encoding="utf-8"?><soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope"><soap12:Body><EnvioRPSRequest xmlns="http://www.prefeitura.sp.gov.br/nfe"><VersaoSchema>1</VersaoSchema><MensagemXML><![CDATA[<p1:PedidoEnvioRPS xmlns:p1="http://www.prefeitura.sp.gov.br/nfe" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><Cabecalho Versao="1"><CPFCNPJRemetente><CNPJ>20018183000180</CNPJ></CPFCNPJRemetente></Cabecalho><RPS><Assinatura>fyx16FI2ToVt1VZe5Q7UiEmVqzau1ZFkcqr1nHR+jU7TYV1kGIHBxhebx7xmhirUkQsjwR1DIh9qvkltHf36lvRiXId/ON31clvWtVaDq5WB5rhj4pPQ22esMjBoZRBS6usw10ZyEjo2iQAxyfnvfq/GZHZiwRizvPU1xnTPskZQfD9tFy5xNeydySf5/M5BeePvN9bz/Axk8dusKJ07et6LjyuHqbUHoO0l6/myAzR6WHqawDWEDuc3uLgfxyFKdKCG2FK0Lj1N/uGoZ3mtXTC1ciwMHtX5pjyr5UqV46YQz1/RPv8AdTRpYHLTku3KW8B8sInL5GH0/3u7WDxNjQ==</Assinatura><ChaveRPS><InscricaoPrestador>57038597</InscricaoPrestador><SerieRPS>TESTE</SerieRPS><NumeroRPS>9417092019</NumeroRPS></ChaveRPS><TipoRPS>RPS</TipoRPS><DataEmissao>2019-07-09</DataEmissao><StatusRPS>N</StatusRPS><TributacaoRPS>T</TributacaoRPS><ValorServicos>0.01</ValorServicos><ValorDeducoes>0.00</ValorDeducoes><ValorPIS>0.00</ValorPIS><ValorCOFINS>0.00</ValorCOFINS><ValorINSS>0.00</ValorINSS><ValorIR>0.00</ValorIR><ValorCSLL>0.00</ValorCSLL><CodigoServico>05895</CodigoServico><AliquotaServicos>0.02</AliquotaServicos><ISSRetido>false</ISSRetido><CPFCNPJTomador><CNPJ>30134945000167</CNPJ></CPFCNPJTomador><RazaoSocialTomador>HUMMINGBIRD HEALTH PRODUCTS</RazaoSocialTomador><EnderecoTomador><Logradouro>Null</Logradouro><NumeroEndereco>123</NumeroEndereco><ComplementoEndereco>Teste</ComplementoEndereco><Bairro>Null</Bairro><Cidade>3550308</Cidade><UF>SP</UF><CEP>00000000</CEP></EnderecoTomador><EmailTomador>none@none</EmailTomador><Discriminacao>Teste de emissao automática de NFS-e de boletos prestados</Discriminacao></RPS><Signature xmlns="http://www.w3.org/2000/09/xmldsig#"><SignedInfo><CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"></CanonicalizationMethod><SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"></SignatureMethod><Reference URI=""><Transforms><Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"></Transform><Transform Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"></Transform></Transforms><DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"></DigestMethod><DigestValue>gm4QtjMAhDOPj4aTCxzsJ6g71mU=</DigestValue></Reference></SignedInfo><SignatureValue>FGMo66jgo2Q1exwx7dTOsBDTwZWXV8QGGHpFUsR94hNsh3lzVstPcCaBMVWclPtmPJ8reOoFwOd6nOqe2yxQCtj6tTjrojkWUGE8P3LR5+yi12338310QdDDg59hZyMWkyEbE3IjxaBrz9d8uPH+J5rimntnjmSiNLYT1gX0Ivys+mgdKh12/K76K4mIXKr6VgAsDPYDJXqINlPsYTvtp1/xAtVVQ8zEkpiiexRBzH5gSf0DaMmGKNSDVVDPsrqQLbq08pF2+9Cnc9zQpizIKtW2jKTfOpgUiUb6VKm0MBzJqz35QBCnLLUP58HOVUlYKtq6ea7FQnVwmSnuZWaOHg==</SignatureValue><KeyInfo><X509Data><X509Certificate>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</X509Certificate></X509Data></KeyInfo></Signature></p1:PedidoEnvioRPS>]]></MensagemXML></EnvioRPSRequest></soap12:Body></soap12:Envelope>"""


def sendRequest(privateKey, certificate, xml):
    certPath = "/tmp/cert.crt"
    keyPath = "/tmp/rsaKey.pem"

    headers = {
        "Content-Type": "application/soap+xml; charset=utf-8;",
        "Accept": "application/soap+xml; charset=utf-8;",
        "Cache-Control": "no-cache",
        "Host": "nfe.prefeitura.sp.gov.br",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }

    with open(certPath, "w") as tempCert:
        tempCert.write(certificate)
    tempCert.close()

    with open(keyPath, "w") as tempKey:
        tempKey.write(privateKey)
    tempKey.close()

    print(xml.encode())
    response = requests.post(
        url="https://nfe.prefeitura.sp.gov.br/ws/lotenfe.asmx",
        data=xml.encode(),
        headers=headers,
        cert=(certPath, keyPath),
        verify=True
    )

    status = response.status_code
    response.encoding = "utf-8"
    print(status)
    print(response.content)


print(sendRequest(privateKey, certificate, xml))
