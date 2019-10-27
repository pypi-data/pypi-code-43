from dataclasses import dataclass
from typing import List, Set, Optional, Tuple
import datetime
import bs4
import requests
from itertools import zip_longest
from mashumaro import DataClassJSONMixin


__all__ = ["Substitution", "SubstitutionTable", "substitutiontables_from_urls"]


@dataclass(frozen=True)  # frozen == unveränderbar, nötig um es als Set zu speichern
class Substitution(DataClassJSONMixin):
    """Eine Substitution repräsentiert eine Vertretung."""

    classes: Tuple[str]
    period: str
    subject_new: str
    subject_old: str
    teacher_new: str
    teacher_old: str
    room: str
    type: str
    text: str

    def pretty(self) -> str:
        """formatiert die Vertretung als menschlich lesbarer Text"""
        text = ""

        if self.type == "Ausfall":
            text += "{period}. Stunde: {subject_old} "
            if self.teacher_old != "":
                text += "bei {teacher_old} "
            text += "entfällt"
            if self.text != "":
                text += "{text}"
        elif self.type == "Raum-Vtr.":
            if self.teacher_new == self.teacher_old:
                text += "{period}. Stunde: {subject_new} bei {teacher_old} verlegt zu Raum {room}"
            else:
                text += "{period}. Stunde: {subject_new} bei {teacher_old} verlegt zu Raum {room} bei {teacher_new}"
        elif self.type == "Vertretung":
            text += "{period}. Stunde "
            if self.subject_new != "" and self.subject_old != "":
                if self.teacher_new == "+":
                    text += "{subject_old} in Raum {room} entfällt"
                else:
                    text += "{subject_old} Vertretung bei {teacher_new} statt {teacher_old} in Raum {room}"
            elif self.subject_new != "" and self.subject_old == "":
                text += "Klausur: {text}"
            else:
                if self.teacher_new == "+":
                    text += "{subject_old} entfällt"
                else:
                    text += "{subject_old} Vertretung bei {teacher_new}"
        elif self.type == "Verlegung":
            text += "{period}. Stunde: {subject_new} bei {teacher_new} anstelle von {subject_old} bei {teacher_old}; {subject_old} verlegt auf {text}"
        elif self.type == "Freistunde":
            text += "{period}. Stunde: {subject_old} bei {teacher_old} fällt aus"
        elif self.type == "Tausch":
            if (
                self.teacher_new == self.teacher_old
                and self.subject_new == self.subject_old
            ):
                text += "{period}. Stunde {subject_new} bei {teacher_old}: {text}"
            else:
                text += "{period}. Stunde {subject_old} bei {teacher_old} getauscht mit {subject_new} bei {teacher_new}: {text}"
        elif self.type == "Sondereinsatz":
            text += "{period}. Stunde: Sondereinsatz in Raum {room}"
        elif self.type == "Betreuung":
            text += "{period}. Stunde: Betreuung durch {teacher_new} in Raum {room}"
        elif self.type == "Pausenaufsicht":
            if self.teacher_new == "???" and self.teacher_old != "":
                text += "Pausenaufsicht von {teacher_old} auf {room} in der {period}"
            else:
                text += "Pausenaufsicht von {teacher_new} auf {room} in der {period}"
        else:
            text += "TODO: {type}. pls contact fijitech"

        return text.format(
            period=self.period,
            subject_new=self.subject_new,
            subject_old=self.subject_old,
            teacher_new=self.teacher_new,
            teacher_old=self.teacher_old,
            room=self.room,
            type=self.type,
            text=self.text,
        )


@dataclass
class SubstitutionTable(DataClassJSONMixin):
    """Ein SubstitutionTable ist eine Liste an Vertretungen sowie zusätzliche Daten wie
    abwesenden Klassen und betroffenen Lehrern/Klassen (je nach typ des Plans)"""

    affected: Set[str]
    absent: Set[str]
    substitutions: List[Substitution]
    date: datetime.date


# verarbeitet einen Vertretungsplan,
# benötigt die benötigten HTML-Elemente des Datums und der beiden Tabellen der Seite
def _parse_substitution_table(
    date_element: bs4.element.Tag,
    additional_info: Optional[bs4.element.Tag],
    substitution_table: Optional[bs4.element.Tag],
) -> SubstitutionTable:

    date = datetime.datetime.strptime(
        date_element.text.split(", ")[0], "%d.%m.%Y"
    ).date()

    affected = []  # type: List[str]
    absent = []  # type: List[str]
    if additional_info is not None:
        for tr in additional_info.findAll("tr"):
            if tr.find("td") is not None:
                if "Betroffene" in tr.find("td").text:
                    affected = tr.findAll("td")[1].text.split(", ")
                elif "Abwesende" in tr.find("td").text:
                    absent = tr.findAll("td")[1].text.split(", ")

    subs = []  # type: List[Substitution]
    if substitution_table is not None:
        # falls es ein Lehrer-Plan ist, muss eine andere Reihenfolge angewandt werden
        is_teacher_subs = (
            not substitution_table.find("tr", {"class": "TeacherHead"}) is None
        )

        for tr in substitution_table.findAll("tr"):
            # unnötige zeile, wird nur auf html-seite benutzt
            if "TeacherHead" in tr.attrs["class"]:
                continue
            subData = [x.text for x in tr.findAll("td")]

            # Vertreter	Stunde	Art	Klasse	Raum	Lehrer	Fach	Fach alt	Vertretungs-Text
            # 0         1       2       3       4       5       6       7               8

            if is_teacher_subs:
                sub = Substitution(
                    tuple(subData[3].split(", ")),
                    subData[1],
                    subData[6],
                    subData[7],
                    subData[0],
                    subData[5],
                    subData[4],
                    subData[2],
                    subData[8],
                )
            else:
                # todo fix
                sub = Substitution(
                    tuple(subData[0].split(", ")),
                    subData[1],
                    subData[2],
                    subData[3],
                    subData[4],
                    subData[5],
                    subData[6],
                    subData[8],
                    subData[9],
                )

            if sub not in subs:
                subs.append(sub)
        del subs[0]  # der erste Sub ist die Header-Zeile der Tabelle

    return SubstitutionTable(set(affected), set(absent), subs, date)


# eine url kann (im Falle eines Lehrer-Plans) mehrere Vertretungspläne beinhalten.
# in _parse_substitutions_url wird eine URL in eine Liste aus Vertretungsplänen generiert,
# indem alle einzelnen Komponenten gesucht werden und in _parse_substitution_table gegeben wird.
def _parse_substitutions_url(url) -> List[SubstitutionTable]:
    soup = bs4.BeautifulSoup(requests.get(url).content, "html.parser")

    dates = []
    infos = []
    for date in soup.findAll("h1"):
        if "NoSubstitutes" in date.attrs.get("class", []):
            infos.append("no")
        else:
            dates.append(date)
            infos.append("date")

    has_content_list = []
    last_was_date = False
    for info in infos:
        if info == "date":
            if last_was_date:
                has_content_list.append(True)
            last_was_date = True
        else:
            if info == "no":
                has_content_list.append(False)
            last_was_date = False
    if last_was_date:
        has_content_list.append(True)

    add_infos = soup.findAll("table", {"class": "additionInfoTable"})
    subs_tables = soup.findAll("table", attrs={"cellspacing": 1})

    assert len(has_content_list) == len(
        dates
    ), "amount of has_content is not equal to amount of dates"
    assert len(add_infos) == len(
        subs_tables
    ), "amount of add infos is not equal to amount of subs tables"

    tables = []
    amount_no_content = 0
    for (i, (date, has_content)) in enumerate(zip(dates, has_content_list)):
        if not has_content:
            amount_no_content += 1
            tables.append(_parse_substitution_table(date, None, None))
        else:
            tables.append(
                _parse_substitution_table(
                    date,
                    add_infos[i - amount_no_content],
                    subs_tables[i - amount_no_content],
                )
            )

    assert (
        len(subs_tables) == len(has_content_list) - amount_no_content
    ), "amount_no_content logic is wrong"

    return tables


def substitutiontables_from_urls(urls: List[str]) -> List[SubstitutionTable]:
    """liest eine Liste aus URLs aus, gibt diese als SubstitutionTables zurück."""

    # WICHTIG: Pläne desselben Datums werden zusammengemerget

    # die liste der Vertretungspläne, die am ende returt wird
    timetables = []  # type: List[SubstitutionTable]
    for url in urls:
        for new_timetable in _parse_substitutions_url(url):
            for old_timetable in timetables:
                # falls das datum bereits vorhanden ist, füge alten und neuen
                # Plan zusammen
                if new_timetable.date == old_timetable.date:
                    old_timetable.affected.update(new_timetable.affected)
                    old_timetable.absent.update(new_timetable.absent)
                    old_timetable.substitutions.extend(new_timetable.substitutions)
                    break
            else:
                # falls das datum noch nicht in der liste ist,
                # hänge Plan hinten an
                timetables.append(new_timetable)
    for timetable in timetables:
        timetable.substitutions = sorted(
            timetable.substitutions, key=lambda s: s.classes
        )
    return sorted(timetables, key=lambda t: t.date)
