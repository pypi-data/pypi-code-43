import json
from jsonschema import validate, ValidationError
from collections import namedtuple


class SchemaValidation:
    @classmethod
    def __init__(cls):
        cls.schema_validation = namedtuple(
            typename="SchemaValidation", field_names=["valid", "error"], defaults=[False, None], module="pawn_pay"
        )

        cls.customer_upload_schema = {
            "type": "object",
            "required": ["name", "email", "phone"],
            "properties": {
                "name": {"$id": "#/properties/name", "type": "string", "examples": ["Johnny Appleseed"]},
                "email": {
                    "$id": "#/properties/email",
                    "type": "string",
                    "examples": ["j.appleseed@example.com"],
                    "pattern": "^(.*\@.*\..{3,})$",
                },
                "phone": {
                    "$id": "#/properties/phone",
                    "type": "string",
                    "examples": ["9544941112"],
                    "pattern": "^(.*)$",
                },
            },
        }

        cls.ticket_upload_schema = {
            "type": "object",
            "required": ["number", "amount", "due_date"],
            "optional": [
                "description",
                "renewal_period",
                "renew_from_payment",
                "layaway",
                "layaway_total",
                "layaway_payment",
                "customer_email",
            ],
            "properties": {
                "number": {
                    "$id": "#/properties/number",
                    "type": "string",
                    "examples": ["ZZFV-986225"],
                    "pattern": "^(.*)$",
                },
                "amount": {"$id": "#/properties/amount", "type": "integer"},
                "due_date": {
                    "$id": "#/properties/due_date",
                    "type": "date-time",
                    "examples": ["2020/07/29 03:59:59 +00:00"],
                },
                "description": {"$id": "#/properties/description", "type": "string", "default": ""},
                "renewal_period": {"$id": "#/properties/renewal_period", "type": "integer", "default": 30},
                "renew_from_payment": {
                    "$id": "#/properties/renew_from_payment",
                    "type": "string",
                    "default": "from_due_date",
                    "examples": ["from_due_date", "from_payment_date", "month", "limbo"],
                    "pattern": "^(.*)$",
                },
                "layaway": {
                    "$id": "#/properties/layaway",
                    "type": "boolean",
                    "default": False,
                    "examples": [True, False],
                },
                "layaway_total": {"$id": "#/properties/layaway_total", "type": "integer"},
                "layaway_payment": {"$id": "#/properties/layaway_payment", "type": "integer"},
                "customer_email": {
                    "$id": "#/properties/customer_email",
                    "type": "string",
                    "examples": ["shawnarnold@martinez.com"],
                    "pattern": "^(.*\@.*\..{3,})$",
                },
            },
        }

        cls.payment_upload_schema = {
            "type": "object",
            "required": ["payments"],
            "properties": {
                "payments": {
                    "$id": "#/properties/payments",
                    "type": "array",
                    "items": {
                        "$id": "#/properties/payments/items",
                        "type": "string",
                        "examples": ["ZTA3EIGL1N"],
                        "pattern": "^(.*)$",
                    },
                }
            },
        }

        cls.customer_response_schema = {
            "type": "array",
            "items": {
                "$id": "#/items",
                "type": "object",
                "required": ["id", "name", "email", "phone", "created_at", "updated_at"],
                "properties": {
                    "id": {"$id": "#/items/properties/id", "type": "integer"},
                    "name": {
                        "$id": "#/items/properties/name",
                        "type": "string",
                        "examples": ["Donald Doyle"],
                        "pattern": "^(.*)$",
                    },
                    "email": {
                        "$id": "#/items/properties/email",
                        "type": "string",
                        "examples": ["sassykatdesign@hotmail.com"],
                        "pattern": "^(.*\@.*\..{3,})$",
                    },
                    "phone": {
                        "$id": "#/items/properties/phone",
                        "type": "string",
                        "examples": ["(704) 789-7445"],
                        "pattern": "^(.*)$",
                    },
                    "created_at": {
                        "$id": "#/items/properties/created_at",
                        "type": "date-time",
                        "examples": ["2019/09/25 14:15:47 -04:00"],
                    },
                    "updated_at": {
                        "$id": "#/items/properties/updated_at",
                        "type": "date-time",
                        "examples": ["2019/09/28 11:58:28 -04:00"],
                    },
                },
            },
        }

        cls.ticket_response_schema = {
            "type": "array",
            "items": {
                "$id": "#/items",
                "type": "object",
                "required": [
                    "id",
                    "number",
                    "amount",
                    "status",
                    "due_date",
                    "description",
                    "autobill",
                    "customer_id",
                    "created_at",
                    "updated_at",
                    "scheduled_date",
                    "last_autobill",
                    "renewal_period",
                    "renew_from_payment",
                    "send_reminders",
                    "reminder_count",
                    "layaway",
                    "layaway_total",
                    "layaway_payment",
                    "payable",
                    "payment_method",
                ],
                "properties": {
                    "id": {"$id": "#/items/properties/id", "type": "integer", "default": 0, "examples": [1]},
                    "number": {
                        "$id": "#/items/properties/number",
                        "type": "string",
                        "examples": ["OUQD-645805"],
                        "pattern": "^(.*)$",
                    },
                    "amount": {
                        "$id": "#/items/properties/amount",
                        "type": "integer",
                        "default": 0,
                        "examples": [5000],
                    },
                    "status": {
                        "$id": "#/items/properties/status",
                        "type": "string",
                        "default": "active",
                        "examples": ["active", "inactive"],
                        "pattern": "^(.*)$",
                    },
                    "due_date": {
                        "$id": "#/items/properties/due_date",
                        "type": "date-time",
                        "examples": ["2019/11/25 23:59:59 -05:00"],
                    },
                    "description": {
                        "$id": "#/items/properties/description",
                        "type": "string",
                        "default": "",
                        "examples": ["Here come the future boys [future boys] - in the future, boys."],
                    },
                    "autobill": {
                        "$id": "#/items/properties/autobill",
                        "type": "boolean",
                        "default": False,
                        "examples": [True, False],
                    },
                    "customer_id": {"$id": "#/items/properties/customer_id", "type": "integer"},
                    "created_at": {
                        "$id": "#/items/properties/created_at",
                        "type": "date-time",
                        "examples": ["2019/09/25 14:37:28 -04:00"],
                    },
                    "updated_at": {
                        "$id": "#/items/properties/updated_at",
                        "type": "date-time",
                        "examples": ["2019/09/27 20:58:21 -04:00"],
                    },
                    "scheduled_date": {
                        "$id": "#/items/properties/scheduled_date",
                        "type": "None",
                        "default": None,
                        "examples": [None],
                    },
                    "last_autobill": {
                        "$id": "#/items/properties/last_autobill",
                        "type": "None",
                        "default": None,
                        "examples": [None],
                    },
                    "renewal_period": {"$id": "#/items/properties/renewal_period", "type": "integer", "default": 30},
                    "renew_from_payment": {
                        "$id": "#/items/properties/renew_from_payment",
                        "type": "string",
                        "default": "",
                        "examples": ["from_due_date"],
                        "pattern": "^(.*)$",
                    },
                    "send_reminders": {
                        "$id": "#/items/properties/send_reminders",
                        "type": "boolean",
                        "default": False,
                        "examples": [True, False],
                    },
                    "reminder_count": {"$id": "#/items/properties/reminder_count", "type": "integer", "default": 0},
                    "layaway": {
                        "$id": "#/items/properties/layaway",
                        "type": "boolean",
                        "default": False,
                        "examples": [True, False],
                    },
                    "layaway_total": {"$id": "#/items/properties/layaway_total", "type": "integer"},
                    "layaway_payment": {"$id": "#/items/properties/layaway_payment", "type": "boolean"},
                    "payable": {
                        "$id": "#/items/properties/payable",
                        "type": "boolean",
                        "default": False,
                        "examples": [True, False],
                    },
                    "payment_method": {"$id": "#/items/properties/payment_method", "type": "integer"},
                },
            },
        }

        cls.payments_recorded_schema = {
            "type": "object",
            "required": ["recorded"],
            "properties": {"recorded": {"$id": "#/properties/recorded", "type": "integer"}},
        }

        cls.new_payments_schema = {
            "type": "object",
            "required": [
                "amount",
                "created_at",
                "customer",
                "number",
                "payment_method",
                "recorded",
                "status",
                "ticket_number",
            ],
            "properties": {
                "amount": {"$id": "#/properties/amount", "type": "integer", "default": 0, "examples": [0]},
                "created_at": {
                    "$id": "#/properties/created_at",
                    "type": "date-time",
                    "examples": ["2019/04/30 08:52:17 -04:00"],
                },
                "customer": {
                    "$id": "#/properties/customer",
                    "type": "string",
                    "examples": ["jillturner@bowen.info"],
                    "pattern": "^(.*\@.*\..{3,})$",
                },
                "number": {
                    "$id": "#/properties/number",
                    "type": "string",
                    "examples": ["467529224381"],
                    "pattern": "^(.*)$",
                },
                "payment_method": {
                    "$id": "#/properties/payment_method",
                    "type": "object",
                    "required": [
                        "address",
                        "created_at",
                        "exp",
                        "expired",
                        "id",
                        "last_four",
                        "name",
                        "sub_type",
                        "type",
                        "updated_at",
                    ],
                    "properties": {
                        "address": {
                            "$id": "#/properties/payment_method/properties/address",
                            "type": "object",
                            "required": ["city", "country", "state", "street", "zip"],
                            "properties": {
                                "city": {
                                    "$id": "#/properties/payment_method/properties/address/properties/city",
                                    "type": "string",
                                    "default": "",
                                    "examples": ["East Coreneton"],
                                    "pattern": "^(.*)$",
                                },
                                "country": {
                                    "$id": "#/properties/payment_method/properties/address/properties/country",
                                    "type": "string",
                                    "default": "USA",
                                    "examples": ["USA"],
                                    "pattern": "^(.*)$",
                                },
                                "state": {
                                    "$id": "#/properties/payment_method/properties/address/properties/state",
                                    "type": "string",
                                    "default": "",
                                    "examples": ["DE"],
                                    "pattern": "^(.*)$",
                                },
                                "street": {
                                    "$id": "#/properties/payment_method/properties/address/properties/street",
                                    "type": "string",
                                    "default": "",
                                    "examples": ["91600 Jordan Forges Suite 759"],
                                    "pattern": "^(.*)$",
                                },
                                "zip": {
                                    "$id": "#/properties/payment_method/properties/address/properties/zip",
                                    "type": "string",
                                    "default": "",
                                    "examples": ["64411-8174"],
                                    "pattern": "^(.*)$",
                                },
                            },
                        },
                        "created_at": {
                            "$id": "#/properties/payment_method/properties/created_at",
                            "type": "date-time",
                            "examples": ["2019/03/26 13:27:25 -04:00"],
                        },
                        "exp": {
                            "$id": "#/properties/payment_method/properties/exp",
                            "type": "string",
                            "examples": ["1219"],
                            "pattern": "^(.*)$",
                        },
                        "expired": {
                            "$id": "#/properties/payment_method/properties/expired",
                            "type": "boolean",
                            "default": False,
                            "examples": [True, False],
                        },
                        "id": {"$id": "#/properties/payment_method/properties/id", "type": "integer"},
                        "last_four": {
                            "$id": "#/properties/payment_method/properties/last_four",
                            "type": "string",
                            "examples": ["4242"],
                            "pattern": "^(.*)$",
                        },
                        "name": {
                            "$id": "#/properties/payment_method/properties/name",
                            "type": "string",
                            "examples": ["Roger Wang"],
                            "pattern": "^(.*)$",
                        },
                        "sub_type": {
                            "$id": "#/properties/payment_method/properties/sub_type",
                            "type": "string",
                            "examples": ["visa"],
                            "pattern": "^(.*)$",
                        },
                        "type": {
                            "$id": "#/properties/payment_method/properties/type",
                            "type": "string",
                            "examples": ["credit"],
                            "pattern": "^(.*)$",
                        },
                        "updated_at": {
                            "$id": "#/properties/payment_method/properties/updated_at",
                            "type": "date-time",
                            "examples": ["2019/09/28 12:21:05 -04:00"],
                        },
                    },
                },
                "recorded": {
                    "$id": "#/properties/recorded",
                    "type": "boolean",
                    "default": False,
                    "examples": [True, False],
                },
                "status": {
                    "$id": "#/properties/status",
                    "type": "string",
                    "default": "captured",
                    "examples": ["captured", "refunded", "voided"],
                    "pattern": "^(.*)$",
                },
                "ticket_number": {
                    "$id": "#/properties/ticket_number",
                    "type": "string",
                    "examples": ["BMVQ-322975"],
                    "pattern": "^(.*)$",
                },
            },
        }

    def customer_upload(self, obj: any([dict, list])):
        try:
            return self.schema_validation(
                True if isinstance(validate(instance=obj, schema=self.customer_upload_schema), type(None)) else False,
                None,
            )
        except ValidationError as e_info:
            return self.schema_validation(False, str(e_info))

    def ticket_upload(self, obj: any([dict, list])):
        try:
            return self.schema_validation(
                True if isinstance(validate(instance=obj, schema=self.ticket_upload_schema), type(None)) else False,
                None,
            )
        except ValidationError as e_info:
            return self.schema_validation(False, str(e_info))

    def customer_response(self, obj: any([dict, list])):
        try:
            return self.schema_validation(
                True
                if isinstance(validate(instance=obj, schema=self.customer_response_schema), type(None))
                else False,
                None,
            )
        except ValidationError as e_info:
            return self.schema_validation(False, str(e_info))

    def ticket_response(self, obj: any([dict, list])):
        try:
            return self.schema_validation(
                True if isinstance(validate(instance=obj, schema=self.ticket_response_schema), type(None)) else False,
                None,
            )
        except ValidationError as e_info:
            return self.schema_validation(False, str(e_info))

    def new_payments_response(self, obj: any([dict, list])):
        try:
            return self.schema_validation(
                True if isinstance(validate(instance=obj, schema=self.new_payments_schema), type(None)) else False,
                None,
            )
        except ValidationError as e_info:
            return self.schema_validation(False, str(e_info))


def validate_json(data: str):
    """Validates that something is or can be converted to valid JSON

    Args:
        data (str): The supposedly-JSON data to validate

    Returns:
        valid (bool): True if data is JSON else False
    """
    validated = namedtuple(typename="JsonValidation", field_names=["valid", "error"], defaults=[False, None])
    try:
        json.loads(data)
        return validated(valid=True)
    except TypeError as err:
        try:
            json.loads(json.dumps(data))
            return validated(valid=True)
        except Exception as err:
            return validated(error=err)
    except json.decoder.JSONDecodeError as err:
        return validated(error=str(err))


#  Copyright (c) 2019 | Advancing Technology Systems, LLC
#  See LICENSE for any grants of usage, distribution, or modification
