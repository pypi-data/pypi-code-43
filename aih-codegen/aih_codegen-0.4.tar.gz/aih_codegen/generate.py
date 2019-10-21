import os
import sys
import yaml
import argparse
from jinja2 import FileSystemLoader, Environment
from six import text_type as _text_type

class GraphqlGenerate:
    def __init__(self):
        parser = argparse.ArgumentParser(
            usage=''' aih <command> [<args>]
   The most commonly used aih commands are:
   generate_schema     Generate schema
   generate_resolver   Generate resolver
            '''
        )
        parser.add_argument('command', help='Subcommand to run')
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command')
            parser.print_help()
            exit(1)

        getattr(self, args.command)()

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
            default="schema.graphql"
        )

        args = parser.parse_args(sys.argv[2:])

        with open(args.config, "r") as c:
            doc = yaml.load(c.read(), Loader=yaml.FullLoader)

        base_dir = os.getcwd()
        template_dir = os.path.join(base_dir, "templates")
        templateLoader = FileSystemLoader(searchpath=template_dir)
        templateEnv = Environment(loader=templateLoader, trim_blocks=True, lstrip_blocks=True)
        
        schema_template = templateEnv.get_template("schema.graphql.jinja2")

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

        base_dir = os.getcwd()
        template_dir = os.path.join(base_dir, "templates")
        templateLoader = FileSystemLoader(searchpath=template_dir)
        templateEnv = Environment(loader=templateLoader, trim_blocks=True, lstrip_blocks=True)
        
        resolver_template = templateEnv.get_template("resolvers.js.jinja2")

        resolver_output = resolver_template.render({ "types": doc["types"] })

        with open(args.output, mode="w") as r:
            r.write(resolver_output)

