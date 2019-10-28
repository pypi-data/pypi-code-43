import os
import sys
import yaml
import argparse
from .template import template
from jinja2 import Template
from six import text_type as _text_type

class GraphqlGenerate:
    def __init__(self):
        parser = argparse.ArgumentParser(
            usage='''aih [command] [options]

generate graphql code

commands:
   codegen:schema|s [options]     Generate schema
   codegen:resolver|r [options]   Generate resolver
   codegen:app|a [options]        Generate schema and resolver
            '''
        )
        parser.add_argument('command', help='Subcommand to run')
        args = parser.parse_args(sys.argv[1:2])
        command_dict = {
            "a": "generate_app",
            "r": "generate_resolver",
            "s": "generate_schema",
            "codegen:schema": "generate_schema",
            "codegen:resolver": "generate_resolver",
            "codegen:app": "generate_app"
        }
        command = command_dict[args.command]
        if not hasattr(self, command):
            print('Unrecognized command')
            parser.print_help()
            exit(1)

        getattr(self, command)()

    def generate_schema(self):
        parser = argparse.ArgumentParser(
            description="Generate schema"
        )

        parser.add_argument(
            "--config", "-c",
            type=_text_type,
            help="Config file",
            default="config.yaml"
        )

        parser.add_argument(
            "--output", "-o",
            type=_text_type,
            help="Output file",
            default="schema.js"
        )

        args = parser.parse_args(sys.argv[2:])

        with open(args.config, "r") as c:
            doc = yaml.load(c.read(), Loader=yaml.FullLoader)
        
        schema_template = Template(template["schema"])

        schema_output = schema_template.render({ "types": doc["types"] })

        with open(args.output, mode="w") as s:
            s.write(schema_output)

    def generate_resolver(self):
        parser = argparse.ArgumentParser(
            description="Generate resolver"
        )

        parser.add_argument(
            "--config", "-c",
            type=_text_type,
            help="Config file",
            default="config.yaml"
        )

        parser.add_argument(
            "--output", "-o",
            type=_text_type,
            help="Output file",
            default="resolvers.js"
        )

        args = parser.parse_args(sys.argv[2:])

        with open(args.config, "r") as c:
            doc = yaml.load(c.read(), Loader=yaml.FullLoader)
        
        resolver_template = Template(template["resolver"])

        resolver_output = resolver_template.render({ "types": doc["types"] })

        with open(args.output, mode="w") as r:
            r.write(resolver_output)

    def generate_app(self):
        parser = argparse.ArgumentParser(
            description="Generate schema and resolver"
        )

        parser.add_argument(
            "--config", "-c",
            type=_text_type,
            help="Path to config file",
            default="config.yaml"
        )

        parser.add_argument(
            "--soutput", "-s",
            type=_text_type,
            help="Path to scheme output file",
            default="schema.js"
        )

        parser.add_argument(
            "--routput", "-r",
            type=_text_type,
            help="Path to resolver output file",
            default="resolvers.js"
        )

        args = parser.parse_args(sys.argv[2:])

        with open(args.config, "r") as c:
            doc = yaml.load(c.read(), Loader=yaml.FullLoader)

        schema_template = Template(template["schema"])
        resolver_template = Template(template["resolver"])

        schema_output = schema_template.render({ "types": doc["types"] })
        resolver_output = resolver_template.render({ "types": doc["types"] })

        with open(args.soutput, mode="w") as s:
            s.write(schema_output)
        with open(args.routput, mode="w") as r:
            r.write(resolver_output)

