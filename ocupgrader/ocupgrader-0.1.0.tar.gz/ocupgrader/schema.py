from jsonschema import validate
from jsonschema.exceptions import ValidationError
import logging
import yaml

log = logging.getLogger(__name__)
log.level = logging.INFO

SCHEMA = yaml.safe_load("""
type: object
properties:
  tasks:
    type: object
    additionalProperties:
      type: object
      properties:
        commands:
          type: array
          items:
            type: object
            properties:
              args:
                type: array
                items:
                  type: string
                  example: pods
              description:
                type: string
            required:
              - args
        description:
          type: string
        parameters:
          type: array
          items:
            type: string
            example: version
      required:
        - commands
        - description
required:
  - tasks
""")


def validate_schema(project_spec):
    try:
        validate(project_spec, SCHEMA)
        return True
    except ValidationError as e:
        log.error(e)
    return False
