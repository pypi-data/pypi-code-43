import requests
import json
from datetime import datetime

DC_PRODUCTION_URL = "https://dc.directchannel.it/mentor/api"
DC_TEST_URL = "http://test.directchannel.it/mentor/api"


class RequestWrapper(object):

    def _send_request(self, url, payload, headers, method="POST", debug=False):
        try:
            response = requests.request(method, url=url, data=json.dumps(payload, ensure_ascii=False).encode('utf-8'), headers=headers)
            if debug:
                message = "\n"
                message += "%s\n" % datetime.now().strftime("%Y-%m-%d %H:%M:%s")
                message += "Method: %s - %s\n" % (method, url)
                message += "Request: %s\n" % json.dumps(payload)
                message += "Response: %s\n" % response.text
                with open(debug, 'a+') as f:
                    f.write(message)
            return response
        except requests.exceptions.RequestException as e:
            return {
                "result": "KO",
                "message": "SERVER ERROR {0}".format(str(e)),
                "data": "",
            }

    def _handle_data(self, data):
        if hasattr(data, 'text'):
            return json.loads(data.text)
        else:
            return data


class DirectChannel(RequestWrapper):
    url = None
    env = None
    application = None
    token = None
    user = None

    def __init__(self, env, application, token, user, test=False, debug=False):
        self.url = DC_PRODUCTION_URL if not test else DC_TEST_URL
        self.env = env
        self.application = application
        self.token = token
        self.user = user
        self.debug = debug

    def wsc_table(self, param):
        payload = {
            "env": self.env,
            "application": self.application,
            "operation": "get",
            "token": self.token,
            "user": self.user,
            "param": param,
            "data": None
        }
        headers = {'content-type': 'application/json; charset=utf-8'}
        url = "{0}/{1}".format(self.url, 'wsc_table.ashx')
        return self._handle_data(self._send_request(url=url, method="GET", payload=payload, headers=headers, debug=self.debug))

    def wsc_donor_exists(self, **kwargs):
        kwargs['check'] = True
        res = self.wsc_save_donor(**kwargs)
        return res

    def wsc_save_donor(self, codice=None, codiceorigine=None, codiceweb=None, tipo=None, sottotipo=None, nome=None,
                       cognome=None, ragionesociale=None, genere=None, datanascita=None, luogonascita=None, dataraccolta=None,
                       codicefiscale=None, partitaiva=None, email1=None, email2=None, telefono1=None, telefono2=None,
                       cellulare1=None, cellulare2=None, presso=None, dug=None, duf=None, civico=None, altrocivico=None,
                       frazione=None, localita=None, provincia=None, cap=None, codicenazione=None, codicecampagna=None,
                       codiceprofessione=None, lotto=None, check=False):
        payload = {
            "env": self.env,
            "application": self.application,
            "operation": "save",
            "token": self.token,
            "user": self.user,
            "param": "check" if check else "",
            "data": {
                "codice": codice,
                "codiceOrigine": codiceorigine,
                "codiceWeb": codiceweb,
                "tipo": tipo,
                "sottotipo": sottotipo,
                "nome": nome,
                "cognome": cognome,
                "ragioneSociale": ragionesociale,
                "genere": genere,
                "dataNascita": datanascita,
                "luogoNascita": luogonascita,
                "codiceFiscale": codicefiscale,
                "partitaIVA": partitaiva,
                "email1": email1,
                "email2": email2,
                "telefono1": telefono1,
                "telefono2": telefono2,
                "cellulare1": cellulare1,
                "cellulare2": cellulare2,
                "presso": presso,
                "lotto": lotto,
                "dug": dug,
                "duf": duf,
                "civico": civico,
                "altroCivico": altrocivico,
                "frazione": frazione,
                "localita": localita,
                "provincia": provincia,
                "cap": cap,
                "codiceNazione": codicenazione,
                "codiceCampagna": codicecampagna,
                "dataRaccolta": dataraccolta,
                "codiceProfessione": codiceprofessione,
            }
        }
        headers = {'content-type': 'application/json'}
        url = "{0}/{1}".format(self.url, 'wsc_save_donor.ashx')
        return self._handle_data(self._send_request(url=url, payload=payload, headers=headers, debug=self.debug))

    def wsc_get_regulars(self, codice=None):

        payload = {
            "env": self.env,
            "application": self.application,
            "operation": "save",
            "token": self.token,
            "user": self.user,
            "param": codice,
            "data": None
        }

        headers = {'content-type': 'application/json'}
        url = "{0}/{1}".format(self.url, 'wsc_get_regulars.ashx')
        return self._handle_data(self._send_request(url=url, payload=payload, headers=headers, debug=self.debug))

    def wsc_save_profile(self, codicedonatore=None, codiceprofilazione=None, descrizioneranking=None, 
                         codicecampagna=None, dataentrata=None, datauscita=None):
        payload = {
            "env": self.env,
            "application": self.application,
            "operation": "save",
            "token": self.token,
            "user": self.user,
            "param": "",
            "data": {
                "codiceDonatore": codicedonatore,
                "codiceProfilazione": codiceprofilazione,
                "descrizioneRanking": descrizioneranking,
                "codiceCampagna": codicecampagna,
                "dataEntrata": dataentrata, 
                "dataUscita": datauscita
            }
        }
        headers = {'content-type': 'application/json'}
        url = "{0}/{1}".format(self.url, 'wsc_save_profile.ashx')
        return self._handle_data(self._send_request(url=url, payload=payload, headers=headers, debug=self.debug))

    def wsc_save_product(self, iddonazione=None, codiceprodotto=None, quantita=None, prezzounitario=None):
        payload = {
            "env": self.env,
            "application": self.application,
            "operation": "save",
            "token": self.token,
            "user": self.user,
            "param": "",
            "data": {
                "idDonazione": iddonazione,
                "codiceProdotto": codiceprodotto,
                "quantita": quantita,
                "prezzoUnitario": prezzounitario
            }
        }
        headers = {'content-type': 'application/json'}
        url = "{0}/{1}".format(self.url, 'wsc_save_product.ashx')
        return self._handle_data(self._send_request(url=url, payload=payload, headers=headers, debug=self.debug))

    def wsc_save_regular(self, id=None, generasostegno=None, codicedonatore=None, codicecampagna=None, codicecentro=None,
                         codicebambino=None, codiceprogetto=None, codicecanale=None, codicetema=None, importo=None, frequenza=None,
                         metodo=None, iban=None, urn=None, lotto=None, locazione=None, cittalocazione=None,
                         preferenzagenere=None, preferenzaetaminima=None, preferenzaetamassima=None, note=None, datadelega=None,
                         token=None, mesetoken=None, providerincasso=None, nometitolare=None, datarichiesta=None, dataprossimarichiesta=None,
                         codicefiscaletitolare=None, indirizzotitolare=None, localitatitolare=None, cartaprepagata=None,
                         provinciatitolare=None, annotoken=None, cap=None, codicedialogatoreinterno=None, codicedialogatoreesterno=None, nomedialogatoreesterno=None,
                         flagallineamento=None, datapromessa=None):
        payload = {
            "env": self.env,
            "application": self.application,
            "operation": "save",
            "token": self.token,
            "user": self.user,
            "param": "",
            "data": {
                "ID": id,
                "generaSostegno": generasostegno,
                "codiceDonatore": codicedonatore,
                "codiceCampagna": codicecampagna,
                "codiceCentro": codicecentro,
                "codiceBambino": codicebambino,
                "codiceTema": codicetema,
                "codiceProgetto": codiceprogetto,
                "codiceCanale": codicecanale,
                "importo": importo,
                "frequenza": frequenza,
                "metodo": metodo,
                "dataRichiesta": datarichiesta,
                "dataDelega": datadelega,
                "dataPromessa": datapromessa,
                "dataProssimaRichiesta": dataprossimarichiesta,
                "IBAN": iban,
                "Token": token,
                "meseToken": mesetoken,
                "annoToken": annotoken,
                "providerincasso": providerincasso,
                "nomeTitolare": nometitolare,
                "codiceFiscaleTitolare": codicefiscaletitolare,
                "IndirizzoTitolare": indirizzotitolare,
                "localitaTitolare": localitatitolare,
                "provinciaTitolare": provinciatitolare,
                "cartaPrepagata": cartaprepagata,
                "codiceDialogatoreEsterno": codicedialogatoreesterno,
                "codiceDialogatoreInterno": codicedialogatoreinterno,
                "nomeDialogatoreEsterno": nomedialogatoreesterno,
                "cap": cap,
                "urn": urn,
                "lotto": lotto,
                "locazione": locazione,
                "cittaLocazione": cittalocazione,
                "preferenzaGenere": preferenzagenere,
                "preferenzaEtaMinima": preferenzaetaminima,
                "preferenzaEtaMassima": preferenzaetamassima,
                "flagAllineamento": flagallineamento,
                "note": note
            }
        }

        headers = {'content-type': 'application/json'}
        url = "{0}/{1}".format(self.url, 'wsc_save_regular.ashx')
        return self._handle_data(self._send_request(url=url, payload=payload, headers=headers, debug=self.debug))

    def wsc_save_attachment(self, codiceDonatore, filename, file, content_type):
        params = {
            "env": self.env,
            "application": self.application,
            "token": self.token,
            "user": self.user,
            "codiceDonatore": codiceDonatore,
        }

        headers = {'content-type': 'application/json'}
        url = "{0}/{1}".format(self.url, 'wsc_save_attachment.ashx')
        files = {'file': (filename, file, content_type)}

        try:
            response = requests.post(url=url, files=files, params=params)
            return response
        except requests.exceptions.RequestException as e:
            return {
                "result": "KO",
                "message": "SERVER ERROR {0}".format(str(e)),
                "data": "",
            }

    def wsc_save_donation(self, codicedonatore=None, codicecampagna=None, codicecentro=None, codicecanale=None, codicebambino=None,
                          codiceprogetto=None, codiceconto=None, importo=None, metodo=None, note=None, dataoperazione=None, datavaluta=None,
                          idregolare=None, idweb=None, codicetransazione=None, tipo=None, evento=None):
        
        payload = {
            "env": self.env,
            "application": self.application,
            "operation": "save",
            "token": self.token,
            "user": self.user,
            "param": "",
            "data": {
                "codiceDonatore": codicedonatore,
                "codiceCampagna": codicecampagna,
                "codiceCentro": codicecentro,
                "codiceCanale": codicecanale,
                "codiceBambino": codicebambino,
                "codiceProgetto": codiceprogetto,
                "codiceConto": codiceconto,
                "importo": ("%s" % importo).replace('.',','),
                "metodo": metodo,
                "note": note,
                "dataOperazione": dataoperazione,
                "dataValuta": datavaluta,
                "idRegolare": idregolare,
                "idWeb": idweb,
                "codiceTransazione": codicetransazione,
                "tipo": tipo,
                "evento": evento,
            }
        }
        
        headers = {'content-type': 'application/json'}
        url = "{0}/{1}".format(self.url, 'wsc_save_donation.ashx')
        return self._handle_data(self._send_request(url=url, payload=payload, headers=headers, debug=self.debug))

    def wsc_save_activity(self, codicedonatore=None, codicecampagna=None, codicebambino=None, codiceprogetto=None,
                          codicecanale=None, idregolare=None, tipo=None, sottotipo=None,
                          oggetto=None, note=None, utenteassegnatario=None, gruppoutentiassegnatario=None,
                          stato=None, dataattivita=None, datachiusura=None):
        payload = {
            "env": self.env,
            "application": self.application,
            "operation": "save",
            "token": self.token,
            "user": self.user,
            "param": "",
            "data": {
                "codiceDonatore": codicedonatore,
                "codiceCampagna": codicecampagna,
                "codiceBambino": codicebambino,
                "codiceProgetto": codiceprogetto,
                "codiceCanale": codicecanale,
                "idRegolare": idregolare,
                "tipo": tipo,
                "sottotipo": sottotipo,
                "oggetto": oggetto,
                "note": note,
                "utenteAssegnatario": utenteassegnatario,
                "gruppoUtentiAssegnatario": gruppoutentiassegnatario,
                "stato": stato,
                "dataAttivita": dataattivita,
                "dataChiusura": datachiusura,
            }
        }
        headers = {'content-type': 'application/json'}
        url = "{0}/{1}".format(self.url, 'wsc_save_activity.ashx')
        return self._handle_data(self._send_request(url=url, payload=payload, headers=headers, debug=self.debug))

    def wsc_save_privacy(self, codicedonatore, codiceprivacy, attiva, dataentrata, datauscita, note):
        payload = {
            "env": self.env,
            "application": self.application,
            "operation": "save",
            "token": self.token,
            "user": self.user,
            "param": "",
            "data": {
                "codiceDonatore": codicedonatore,
                "codicePrivacy": codiceprivacy ,
                "attiva": attiva,
                "dataEntrata": dataentrata,
                "dataUscita": datauscita,
                "note": note
            }
        }
        headers = {'content-type': 'application/json'}
        url = "{0}/{1}".format(self.url, 'wsc_save_privacy.ashx')
        return self._handle_data(self._send_request(url=url, payload=payload, headers=headers, debug=self.debug))
    
    def wsc_set_spec(self, codicedonatore, codicecampo, valore):
        payload = {
            "env": self.env,
            "application": self.application,
            "operation": "save",
            "token": self.token,
            "user": self.user,
            "param": "",
            "data": {
                "codiceAnagrafica": codicedonatore,
                "codiceCampo": codicecampo,
                "valore": valore
            }
        }
        headers = {'content-type': 'application/json'}
        url = "{0}/{1}".format(self.url, 'wsc_set_spec.ashx')
        return self._handle_data(self._send_request(url=url, payload=payload, headers=headers, debug=self.debug))


    def wsc_call_regular(self, idRegolare, codiceEsito):
        payload = {
            "env": self.env,
            "application": self.application,
            "operation": "save",
            "token": self.token,
            "user": self.user,
            "param": "",
            "data": {
                "idRegolare": idRegolare,
                "codiceEsito": codiceEsito 
            }
        }

        headers = {'content-type': 'application/json'}
        url = "{0}/{1}".format(self.url, 'wsc_call_regular.ashx')
        return self._handle_data(self._send_request(url=url, payload=payload, headers=headers, debug=self.debug))

    def wsc_get_children(self, codicebambino):
        payload = {
            "env": self.env,
            "application": self.application,
            "operation": "get",
            "token": self.token,
            "user": self.user,
            "param": codicebambino,
            "data": None
        }
        headers = {'content-type': 'application/json'}
        url = "{0}/{1}".format(self.url, 'wsc_get_children.ashx')
        return self._handle_data(self._send_request(url=url, method="GET", payload=payload, headers=headers, debug=self.debug))
