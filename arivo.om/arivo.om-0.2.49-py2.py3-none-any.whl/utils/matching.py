# coding=utf-8
from __future__ import unicode_literals

import codecs
import glob
import logging
import os
import sys

import editdistance
import yaml

try:
    from yaml import CFullLoader as Loader
except ImportError:
    try:
        from yaml import FullLoader as Loader
    except ImportError:
        from yaml import Loader  # fallback for old pyyaml versions

SEPARATOR_CHARS = " -_.:"
LEGACY_YAML_STRING = """
allowed: "0123456789ABCDEFGHIJKLMNPRSTUVWXYZ"
kept_separators: NONE
replacements:
  - from: "O"
    to: "0"
  - from: "Q"
    to: "0"
  - from: "Ä"
    to: "A"
  - from: "Ö"
    to: "0"
  - from: "Ü"
    to: "U"
exactitude: 0.0
"""

if sys.version_info < (3, 0):
    def ucode(txt):
        return unicode(txt)
else:
    def ucode(txt):
        return str(txt)


class PlateYaml(object):
    def __init__(self, filename):
        self.scheme = ""
        self.version = -1
        self.exactitude = 0.0
        self.filename = filename
        with codecs.open(filename, 'r', encoding="utf8") as f:
            try:
                self.settings = yaml.load(f, Loader=Loader)
                self.valid_chars = self.settings["allowed"]
                self.exactitude = self.settings["exactitude"]
                self.kept_separators = self.settings.get("kept_separators", "NONE").upper()
                self.replacements = []
                for r in self.settings.get("replacements", []):
                    if r.get("from", "") != "" and "to" in r:
                        self.replacements.append((ucode(r.get("from")), ucode(r.get("to"))))
            except:
                logging.error("Error loading Plate Yaml %s, will be ignored", filename)
                return

        try:
            self.scheme, tmp = os.path.basename(filename).replace(".", "-").split("-")[:2]
            self.version = int(tmp)
        except Exception as e:
            logging.exception(e)
            logging.error("Invalid Plate Yaml filename %s, will be ignored", filename)
            return

    def convert(self, plate):
        plate = plate.upper()
        for r in self.replacements:
            plate = plate.replace(r[0], r[1])
        tmp = plate
        for c in tmp:
            if c not in self.valid_chars:
                plate = plate.replace(c, "")

        if self.kept_separators != "ALL":
            plate_stripped = plate
            for c in list(SEPARATOR_CHARS):
                plate_stripped = plate_stripped.replace(c, "")
            if self.kept_separators == "FIRST":
                for i, c in enumerate(list(plate)):
                    if c in SEPARATOR_CHARS:
                        plate = plate[:i + 1] + plate_stripped[i:]
                        break
            elif self.kept_separators == "LAST":
                for i, c in enumerate(reversed(list(plate))):
                    if c in SEPARATOR_CHARS:
                        plate = plate_stripped[:-i] + plate[-1 - i:]
                        break
            else:
                plate = plate_stripped

        return plate


class PlateYamlSelector(object):
    def __init__(self, yaml_dir, revision_file="", default_country_order=None, legacy_in_default_country_order=False,
                 always_add_other_country_to_plate_for_matching=True):
        if default_country_order is None:
            default_country_order = []
        self.yaml_dir = yaml_dir
        self.default_country_order = default_country_order
        self.legacy_in_default_country_order = legacy_in_default_country_order
        self.always_add_other_country_to_plate_for_matching = always_add_other_country_to_plate_for_matching
        self.schemes = {}
        self.revision_file = revision_file
        self.revision = ""
        self.reload_yamls()

    def reload_yamls(self):
        if self.revision_file != "" and os.path.exists(self.revision_file):
            with open(self.revision_file) as f:
                new_revision = f.read()
        else:
            new_revision = "LOADED"

        if new_revision != self.revision:
            yaml_filenames = glob.glob(os.path.join(self.yaml_dir, "*.yml"))
            self.schemes.clear()
            for fn in yaml_filenames:
                plate_yaml = PlateYaml(fn)
                if plate_yaml.version >= 0:  # check, if loading was successful
                    if plate_yaml.scheme in self.schemes:
                        self.schemes[plate_yaml.scheme][plate_yaml.version] = plate_yaml
                    else:
                        self.schemes[plate_yaml.scheme] = {plate_yaml.version: plate_yaml}
            if self.schemes.get("LEGACY", {}).get(0, None) is None:
                with codecs.open("/tmp/LEGACY-0.yml", 'w', encoding="utf8") as f:
                    f.write(LEGACY_YAML_STRING)
                legacy_yaml = PlateYaml("/tmp/LEGACY-0.yml")
                if legacy_yaml.version < 0:
                    raise Exception("NO LEGACY YAML COULD BE LOADED / CREATED")
            else:
                legacy_yaml = self.schemes["LEGACY"][0]
                del self.schemes["LEGACY"]
            if "DEFAULT" not in self.schemes:
                self.schemes["DEFAULT"] = {}

            for key in self.schemes.keys():
                self.schemes[key][0] = legacy_yaml

            self.revision = new_revision

    def get_all_exactitudes_decreasing(self):
        exactitudes = set([])
        for s in self.schemes.keys():
            for v in self.schemes[s].keys():
                exactitudes.add(self.schemes[s][v].exactitude)
        return sorted(exactitudes, reverse=True)

    def get_best_yaml(self, scheme, version):
        if scheme not in self.schemes:
            scheme = "DEFAULT"

        versions = sorted(self.schemes.get(scheme, {}).keys(), reverse=True)
        for v in versions:
            if v <= version:
                return self.schemes[scheme][v]

        raise Exception("NO YAML FOUND! THIS SHOULD NOT HAPPEN!")

    def convert(self, plate, scheme, version, return_matched_yaml=False):
        if return_matched_yaml:
            best_yaml = self.get_best_yaml(scheme, version)
            return {"plate": best_yaml.convert(plate), "scheme": best_yaml.scheme, "version": best_yaml.version,
                    "exactitude": best_yaml.exactitude}
        else:
            return self.get_best_yaml(scheme, version).convert(plate)

    def create_db_record(self, plate, country, scheme, version, id=None, **kwargs):
        """
        This function generates a valid database record.
        :param plate: read plate
        :param country: read country
        :param scheme: scheme that should be used
        :param version: version that should be used
        :param id: id only used in testcases
        :param kwargs: additional arguments, e.g. skidata hostcom provides ticket id
        :return: valid database entry
        """
        converted = self.convert(plate, scheme, version, return_matched_yaml=True)
        payload = {
            "plate": plate,
            "country": country,
            "plate_scheme": scheme,
            "plate_scheme_version": version,
            "plate_conv": converted.get("plate", plate),
            "exactitude": converted.get("exactitude", 0.0),
            "used_scheme": converted.get("scheme", scheme),
            "used_version": converted.get("version", version),
            "id": id,
        }
        if kwargs:
            if any(x in payload.keys() for x in kwargs.keys()):
                raise Exception("additional arguments have key that is part of the matching db record!")
            payload.update(kwargs)
        return payload

    def create_plate_for_matching(self, plate, country="OTHER", plate_confidence=0.5, country_confidence=0.5,
                                  alternatives=None):
        """
        This functions generates the plate payload that is needed by the `match_plate` function.
        :param plate: read plate
        :param country: read country
        :param plate_confidence: confidence of the plate
        :param country_confidence: confidence of the read country
        :param alternatives: plate alternatives
        :return: valid plate for `match_plate`
        """
        if alternatives is None:
            alternatives = []
        country = [{"code": country, "confidence": country_confidence}]
        if self.always_add_other_country_to_plate_for_matching and country != "OTHER":
            country.append({"code": "OTHER", "confidence": 0.5})
        return {
            "plate": {"plate": plate, "confidence": plate_confidence},
            "country": country,
            "alternatives": alternatives
        }

    def create_plate_for_matching_from_medium_message(self, medium_payload):
        """
        If given medium message is of type 'lpr' then a valid plate for `match_plate` will be generated.
        :param medium_payload: medium message
        :return: valid plate for `match_plate`
        """
        if medium_payload.get("type", "").lower() == "lpr":
            country = medium_payload.get("country", {})
            return self.create_plate_for_matching(
                str(medium_payload.get("id", "")), country.get("code", "OTHER"),
                medium_payload.get("confidence", 0.5), country.get("confidence", 0.5),
                medium_payload.get("alternatives")
            )
        return {}

    def insert_into_db(self, db, record):
        """
        This function inserts a record correctly into the db.
        :param db: database to insert
        :param record: db record created with `create_db_record`
        """
        country = record["country"]
        if country not in db:
            db[country] = {}
        if record["used_version"] not in db[country]:
            db[country][record["used_version"]] = []
        db[country][record["used_version"]].append(record)

    def insert_into_db_and_create_record(self, db, plate, country, scheme, version, id=None, **kwargs):
        """
        This function adds a record correctly into db with create_db_record and then inserting the record
        :param db: database to insert
        :param plate: read plate
        :param country: read country
        :param scheme: scheme that should be used
        :param version: version that should be used
        :param id: id only used in testcases
        """
        record = self.create_db_record(plate, country, scheme, version, id, **kwargs)
        self.insert_into_db(db, record)

    def check_ed0(self, db_cv, plate, matches, num_alt, return_only_best=True):
        if db_cv and "used_scheme" in db_cv[0]:
            p_conv = self.convert(plate, db_cv[0]["used_scheme"], db_cv[0]["used_version"])
            for db_entry in db_cv:
                if p_conv == db_entry["plate_conv"]:
                    matches[num_alt].append(db_entry)
                    if return_only_best:
                        return db_entry, matches
        return None, matches

    def check_edx(self, db_cv, plate, max_ed, matches, return_only_best=True):
        if db_cv and "used_scheme" in db_cv[0]:
            p_conv = self.convert(plate, db_cv[0]["used_scheme"], db_cv[0]["used_version"])
            for db_entry in db_cv:
                ed = editdistance.eval(p_conv, db_entry["plate_conv"])
                if ed <= max_ed:
                    matches[ed].append(db_entry)
                if ed == 0 and return_only_best:
                    return db_entry, matches
        return None, matches

    def match_plate(self, plate, db, use_alternatives=True, max_ed=0, return_only_best=True):
        """
        Expected format of plate: {"plate": {"plate": <plate>, ...},
                                       "country": [{"country": <A/D/...>, "confidence": <0.0-1.0>}],
                                       "alternatives": [{"plate": <alt_plate1>, "confidence": <0.0-1.0>},...]}
        Expected format of db: {<Country1>: {<Version1>: [<plate1>, <plate2>,...]}}
            plates in converted form (converted using the best matching yaml, sorted into convert scheme and version,
                                                                                not db entry scheme and version)
        ED0 if use_alternatives (ed1 and alternatives does not make much sense)
        if return_only_best, matching will be stopped if ED0 match was found
        """
        self.reload_yamls()

        if use_alternatives:
            max_ed = 0
            plates = plate.get("alternatives", [])
            if not plates:
                logging.warning("use alternatives is active but no alternatives present! falling back to plate")
                plates = [plate.get("plate", {})]
            matches = [[]] * len(plates)
        else:
            # If use_alternatives is false then match current plate with edX like the controller did
            plates = [plate.get("plate", {})]
            matches = [[]] * (max_ed + 1)
        for num_alt, p in enumerate(plates):
            check_other = False
            # first check based on countries given in plate
            checked_countries = []
            for c in plate.get("country", []):
                country = c["code"]
                if country == "OTHER":
                    check_other = True
                    break
                if country not in db:
                    continue
                for version in sorted(db[country].keys(), reverse=True):
                    if max_ed == 0:
                        res, matches = self.check_ed0(db[country].get(version, []), p["plate"], matches, num_alt,
                                                      return_only_best)
                    else:
                        res, matches = self.check_edx(db[country].get(version, []), p["plate"], max_ed, matches,
                                                      return_only_best)
                    if res is not None:
                        return [[res]]
                checked_countries.append(country)

            # if other specified, check other countries
            if check_other:
                no_legacy_checked_countries = []
                # first check in order given in config, but ignoring legacy (if not legacy_in_default_country_order)
                for country in self.default_country_order:
                    if country in checked_countries or country not in db:
                        continue
                    versions = sorted(db[country].keys(), reverse=True)
                    if not self.legacy_in_default_country_order and 0 in versions:
                        versions.remove(0)
                    for version in versions:
                        if max_ed == 0:
                            res, matches = self.check_ed0(db[country].get(version, []), p["plate"], matches, num_alt,
                                                          return_only_best)
                        else:
                            res, matches = self.check_edx(db[country].get(version, []), p["plate"], max_ed, matches,
                                                          return_only_best)
                        if res is not None:
                            return [[res]]
                    if self.legacy_in_default_country_order:
                        checked_countries.append(country)
                    else:
                        no_legacy_checked_countries.append(country)

                # rest is checked in decreasing version order
                for exactitude in self.get_all_exactitudes_decreasing():
                    for country, db_country in db.items():
                        if country in checked_countries or exactitude != 0 and country in no_legacy_checked_countries:
                            continue
                        for version, db_cv in db_country.items():
                            if db_cv and db_cv[0]["exactitude"] == exactitude:
                                if max_ed == 0:
                                    res, matches = self.check_ed0(db[country].get(version, []), p["plate"], matches,
                                                                  num_alt, return_only_best)
                                else:
                                    res, matches = self.check_edx(db[country].get(version, []), p["plate"], max_ed,
                                                                  matches, return_only_best)
                                if res is not None:
                                    return [[res]]

            if return_only_best:
                for edm in matches:
                    if len(edm) > 0:
                        return [[edm[0]]]

        return matches
