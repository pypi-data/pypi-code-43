import requests
import base64
import gzip
import json
import datetime
from dataclasses import dataclass
from typing import Tuple, List
from mashumaro import DataClassJSONMixin

__all__ = ["LoginException", "News", "Tile", "get_DSB_info"]


class LoginException(Exception):
    """Fehler für falsche Logindaten"""

    pass


@dataclass
class News(DataClassJSONMixin):
    """Ein DSB-News Objekt, bspw. 'Heute ab der sechsten Stunde für alle frei'"""

    title: str
    text: str
    date: datetime.datetime


@dataclass
class Tile(DataClassJSONMixin):
    """Ein DSB-Aushang"""

    title: str
    urls: List[str]
    date: datetime.datetime


def get_DSB_info(
    username: str, password: str, mock=False
) -> Tuple[List[str], List[News], List[Tile]]:
    """gibt einen Tuple aus der Liste der Vertretungsplan-URLs,
    der News und der Aushänge zurück.
    """
    # ein JSON-Objekt der Anfrage wird erstellt
    creds = '{{"UserId": "{}", "UserPw": "{}", BundleId:""}}'.format(username, password)
    encodedCreds = base64.b64encode(gzip.compress(creds.encode())).decode()
    request = '{"req":{"Data":"' + encodedCreds + '","DataType":1}}'
    # die Anfrage wird ausgeführt
    r = requests.post(
        "https://www.dsbmobile.de/JsonHandlerWeb.ashx/GetData",
        data=request,
        headers={"Content-Type": "application/json", "Referer": "x"},
    )

    print(r.status_code)
    print(r.content)

    if r.status_code == 200:
        # die Antwort wird verarbeitet und dekodiert.
        d = json.loads(r.content.decode())["d"]
        response = json.loads(gzip.decompress(base64.b64decode(d)).decode())
    else:
        # sollte nicht passieren, dsb gibt eine unerwartete antwort
        raise Exception("dsb response invalid")

    # Demo-Daten, zum testen von news etc
    if mock:
        response = json.loads(
            '{"Resultcode":0,"ResultStatusInfo":"","StartIndex":-1,"ResultMenuItems":[{"Index":0,"IconLink":"","Title":"Inhalte","Childs":[{"Index":2,"IconLink":"https://app.dsbcontrol.de/static/androidicons/News.png","Title":"News","Root":{"Id":"","Date":"","Title":"","Detail":"","Tags":"","ConType":0,"Prio":0,"Index":0,"Childs":[{"Id":"d1f3cf50-215f-4801-bb01-f1c735eba4bc","Date":"03.07.2018 11:29","Title":"Unterrichtsende","Detail":"Der Unterricht endet am Mittwoch für alle nach der 4. Std. und am Donnerstag nach der 6. Std. ","Tags":"","ConType":5,"Prio":0,"Index":0,"Childs":[],"Preview":""},{"Id":"d1f3cf50-215f-4801-bb01-f1c735eba4bc","Date":"03.07.2018 11:29","Title":"Unterrichtsende","Detail":"Der Unterricht endet am Mittwoch für alle nach der 4. Std. und am Donnerstag nach der 6. Std. ","Tags":"","ConType":5,"Prio":0,"Index":0,"Childs":[],"Preview":""}],"Preview":""},"Childs":[],"MethodName":"news","NewCount":0,"SaveLastState":true},{"Index":1,"IconLink":"https://app.dsbcontrol.de/static/androidicons/Tiles.png","Title":"Aushänge","Root":{"Id":"","Date":"","Title":"","Detail":"","Tags":"","ConType":0,"Prio":0,"Index":0,"Childs":[{"Id":"72b5bcba-3008-4fed-8f57-f54d81b29922","Date":"03.07.2018 14:44","Title":"Theater-AG.jpg","Detail":"","Tags":"","ConType":2,"Prio":0,"Index":0,"Childs":[{"Id":"72b5bcba-3008-4fed-8f57-f54d81b29922","Date":"03.07.2018 14:44","Title":"Theater-AG.jpg","Detail":"https://app.dsbcontrol.de/data/5a0479a5-911d-4d6d-ace0-6b211b968e3a/72b5bcba-3008-4fed-8f57-f54d81b29922/72b5bcba-3008-4fed-8f57-f54d81b29922_000.jpg","Tags":"","ConType":4,"Prio":0,"Index":0,"Childs":[],"Preview":"5a0479a5-911d-4d6d-ace0-6b211b968e3a/72b5bcba-3008-4fed-8f57-f54d81b29922/72b5bcba-3008-4fed-8f57-f54d81b29922_000.jpg"}],"Preview":""},{"Id":"662f63f0-f278-415d-971e-a7963a01515f","Date":"03.07.2018 00:02","Title":"Schülerinfo - Rückgabe der Schulbücher Juli 2018.p","Detail":"","Tags":"","ConType":2,"Prio":0,"Index":0,"Childs":[{"Id":"662f63f0-f278-415d-971e-a7963a01515f","Date":"03.07.2018 00:02","Title":"Schülerinfo - Rückgabe der Schulbücher Juli 2018.p","Detail":"https://app.dsbcontrol.de/data/5a0479a5-911d-4d6d-ace0-6b211b968e3a/662f63f0-f278-415d-971e-a7963a01515f/662f63f0-f278-415d-971e-a7963a01515f_000.jpg","Tags":"","ConType":4,"Prio":0,"Index":0,"Childs":[],"Preview":"5a0479a5-911d-4d6d-ace0-6b211b968e3a/662f63f0-f278-415d-971e-a7963a01515f/662f63f0-f278-415d-971e-a7963a01515f_000.jpg"},{"Id":"662f63f0-f278-415d-971e-a7963a01515f","Date":"03.07.2018 00:02","Title":"Schülerinfo - Rückgabe der Schulbücher Juli 2018.p","Detail":"https://app.dsbcontrol.de/data/5a0479a5-911d-4d6d-ace0-6b211b968e3a/662f63f0-f278-415d-971e-a7963a01515f/662f63f0-f278-415d-971e-a7963a01515f_000.jpg","Tags":"","ConType":4,"Prio":0,"Index":0,"Childs":[],"Preview":"5a0479a5-911d-4d6d-ace0-6b211b968e3a/662f63f0-f278-415d-971e-a7963a01515f/662f63f0-f278-415d-971e-a7963a01515f_000.jpg"}],"Preview":""},{"Id":"52087653-d763-4e10-baa0-b56ae219e8cc","Date":"02.07.2018 23:23","Title":"Information fu¨r Schu¨ler","Detail":"","Tags":"","ConType":2,"Prio":0,"Index":0,"Childs":[{"Id":"52087653-d763-4e10-baa0-b56ae219e8cc","Date":"02.07.2018 23:23","Title":"Information fu¨r Schu¨ler.pdf","Detail":"https://app.dsbcontrol.de/data/5a0479a5-911d-4d6d-ace0-6b211b968e3a/52087653-d763-4e10-baa0-b56ae219e8cc/52087653-d763-4e10-baa0-b56ae219e8cc_000.jpg","Tags":"","ConType":4,"Prio":0,"Index":0,"Childs":[],"Preview":"5a0479a5-911d-4d6d-ace0-6b211b968e3a/52087653-d763-4e10-baa0-b56ae219e8cc/52087653-d763-4e10-baa0-b56ae219e8cc_000.jpg"},{"Id":"52087653-d763-4e10-baa0-b56ae219e8cc","Date":"02.07.2018 23:23","Title":"Information fu¨r Schu¨ler.pdf","Detail":"https://app.dsbcontrol.de/data/5a0479a5-911d-4d6d-ace0-6b211b968e3a/52087653-d763-4e10-baa0-b56ae219e8cc/52087653-d763-4e10-baa0-b56ae219e8cc_000.jpg","Tags":"","ConType":4,"Prio":0,"Index":0,"Childs":[],"Preview":"5a0479a5-911d-4d6d-ace0-6b211b968e3a/52087653-d763-4e10-baa0-b56ae219e8cc/52087653-d763-4e10-baa0-b56ae219e8cc_000.jpg"}],"Preview":""},{"Id":"479753f5-76fe-4400-8bd4-f21bc9c43217","Date":"03.07.2018 14:44","Title":"Nachschreibklausuren  Termine","Detail":"","Tags":"","ConType":2,"Prio":0,"Index":0,"Childs":[{"Id":"479753f5-76fe-4400-8bd4-f21bc9c43217","Date":"03.07.2018 14:44","Title":"Nachschreibklausuren  Termine.pdf","Detail":"https://app.dsbcontrol.de/data/5a0479a5-911d-4d6d-ace0-6b211b968e3a/479753f5-76fe-4400-8bd4-f21bc9c43217/479753f5-76fe-4400-8bd4-f21bc9c43217_000.jpg","Tags":"","ConType":4,"Prio":0,"Index":0,"Childs":[],"Preview":"5a0479a5-911d-4d6d-ace0-6b211b968e3a/479753f5-76fe-4400-8bd4-f21bc9c43217/479753f5-76fe-4400-8bd4-f21bc9c43217_000.jpg"}],"Preview":""},{"Id":"3e8ea49e-575c-4bd7-9210-a598bde5e9e0","Date":"03.07.2018 14:44","Title":"Theater-AG.jpg","Detail":"","Tags":"","ConType":2,"Prio":0,"Index":0,"Childs":[{"Id":"3e8ea49e-575c-4bd7-9210-a598bde5e9e0","Date":"03.07.2018 14:44","Title":"Theater-AG.jpg","Detail":"https://app.dsbcontrol.de/data/5a0479a5-911d-4d6d-ace0-6b211b968e3a/3e8ea49e-575c-4bd7-9210-a598bde5e9e0/3e8ea49e-575c-4bd7-9210-a598bde5e9e0_000.jpg","Tags":"","ConType":4,"Prio":0,"Index":0,"Childs":[],"Preview":"5a0479a5-911d-4d6d-ace0-6b211b968e3a/3e8ea49e-575c-4bd7-9210-a598bde5e9e0/3e8ea49e-575c-4bd7-9210-a598bde5e9e0_000.jpg"}],"Preview":""}],"Preview":""},"Childs":[],"MethodName":"tiles","NewCount":0,"SaveLastState":true},{"Index":0,"IconLink":"https://app.dsbcontrol.de/static/androidicons/Timetable.png","Title":"Pläne","Root":{"Id":"","Date":"","Title":"","Detail":"","Tags":"","ConType":0,"Prio":0,"Index":0,"Childs":[{"Id":"7db185f8-b376-4a6f-b5db-15797b643bac","Date":"03.07.2018 14:46","Title":"VP morgen","Detail":"","Tags":"","ConType":2,"Prio":0,"Index":0,"Childs":[{"Id":"7db185f8-b376-4a6f-b5db-15797b643bac","Date":"03.07.2018 14:46","Title":"VP_SuS_morgen_JWS","Detail":"https://app.dsbcontrol.de/data/5a0479a5-911d-4d6d-ace0-6b211b968e3a/7db185f8-b376-4a6f-b5db-15797b643bac/7db185f8-b376-4a6f-b5db-15797b643bac.html","Tags":"","ConType":6,"Prio":0,"Index":0,"Childs":[],"Preview":"5a0479a5-911d-4d6d-ace0-6b211b968e3a/7db185f8-b376-4a6f-b5db-15797b643bac/preview.png"}],"Preview":""},{"Id":"1f8bd203-d42c-4f35-8cb0-9daed164e0fe","Date":"03.07.2018 14:46","Title":"VP heute","Detail":"","Tags":"","ConType":2,"Prio":0,"Index":0,"Childs":[{"Id":"1f8bd203-d42c-4f35-8cb0-9daed164e0fe","Date":"03.07.2018 14:46","Title":"VP_SuS_heute_JWS","Detail":"https://app.dsbcontrol.de/data/5a0479a5-911d-4d6d-ace0-6b211b968e3a/1f8bd203-d42c-4f35-8cb0-9daed164e0fe/1f8bd203-d42c-4f35-8cb0-9daed164e0fe.html","Tags":"","ConType":6,"Prio":0,"Index":0,"Childs":[],"Preview":"5a0479a5-911d-4d6d-ace0-6b211b968e3a/1f8bd203-d42c-4f35-8cb0-9daed164e0fe/preview.png"}],"Preview":""},{"Id":"4828917c-0c35-47e2-8170-60a0efe76e58","Date":"03.07.2018 14:46","Title":"VP morgen","Detail":"","Tags":"","ConType":2,"Prio":0,"Index":0,"Childs":[{"Id":"4828917c-0c35-47e2-8170-60a0efe76e58","Date":"03.07.2018 14:46","Title":"VP_SuS_morgen_HG","Detail":"https://app.dsbcontrol.de/data/5a0479a5-911d-4d6d-ace0-6b211b968e3a/4828917c-0c35-47e2-8170-60a0efe76e58/4828917c-0c35-47e2-8170-60a0efe76e58.html","Tags":"","ConType":6,"Prio":0,"Index":0,"Childs":[],"Preview":"5a0479a5-911d-4d6d-ace0-6b211b968e3a/4828917c-0c35-47e2-8170-60a0efe76e58/preview.png"}],"Preview":""},{"Id":"a59fb879-6c50-46c2-a683-331f5b8d01be","Date":"03.07.2018 14:46","Title":"VP heute","Detail":"","Tags":"","ConType":2,"Prio":0,"Index":0,"Childs":[{"Id":"a59fb879-6c50-46c2-a683-331f5b8d01be","Date":"03.07.2018 14:46","Title":"VP_SuS_heute_HG","Detail":"https://app.dsbcontrol.de/data/5a0479a5-911d-4d6d-ace0-6b211b968e3a/a59fb879-6c50-46c2-a683-331f5b8d01be/a59fb879-6c50-46c2-a683-331f5b8d01be.html","Tags":"","ConType":6,"Prio":0,"Index":0,"Childs":[],"Preview":"5a0479a5-911d-4d6d-ace0-6b211b968e3a/a59fb879-6c50-46c2-a683-331f5b8d01be/preview.png"}],"Preview":""}],"Preview":""},"Childs":[],"MethodName":"timetable","NewCount":0,"SaveLastState":true}],"MethodName":"","NewCount":0,"SaveLastState":true},{"Index":1,"IconLink":"","Title":"Sonstiges","Childs":[{"Index":0,"IconLink":"https://app.dsbcontrol.de/static/androidicons/Feedback.png","Title":"Feedback","Childs":[],"MethodName":"feedback","NewCount":0,"SaveLastState":false},{"Index":1,"IconLink":"https://app.dsbcontrol.de/static/androidicons/About.png","Title":"Info","Childs":[],"MethodName":"about","NewCount":0,"SaveLastState":false},{"Index":2,"IconLink":"https://app.dsbcontrol.de/static/androidicons/Logout.png","Title":"Logout","Childs":[],"MethodName":"logout","NewCount":0,"SaveLastState":false}],"MethodName":"","NewCount":0,"SaveLastState":true}],"ChannelType":0,"MandantId":"0c29638e-fd9f-422d-9074-04fbe1914b23"}'
        )

    # falls die login-daten falsch waren
    if response["Resultcode"] != 0:
        raise LoginException("invalid login: '{}':'{}'".format(username, password))

    # sammele alle relevante daten in drei arrays:
    timetableurls = []
    news = []
    tiles = []  # type: List[Tile]

    nids = []  # type: List[str]
    for method in response["ResultMenuItems"][0]["Childs"]:
        for item in method["Root"]["Childs"]:
            if method["MethodName"] == "timetable":
                timetableurls.append(item["Childs"][0]["Detail"])
            elif method["MethodName"] == "news":
                # ignoriere doppelte news (nach id)
                if not (item["Id"] in nids):
                    nn = News(
                        item["Title"], item["Detail"], _parse_datetime(item["Date"])
                    )
                    nids.append(item["Id"])
                    news.append(nn)
            elif method["MethodName"] == "tiles":
                urls = map(
                    lambda child: child["Detail"], item["Childs"]
                )  # mappe JSON-Objekte zu ihrem "Detail"-Feld
                tile = Tile(item["Title"], list(urls), _parse_datetime(item["Date"]))
                # ignoriere doppelte tiles (nach titel)
                if tile.title not in map(lambda t: t.title, tiles):
                    tiles.append(tile)

    return (timetableurls, news, tiles)


def _parse_datetime(datestr: str) -> datetime.datetime:
    return datetime.datetime.strptime(datestr, "%d.%m.%Y %H:%M")
