from typing import List, Dict
import click
import os
import yaml
from termcolor_util import red, cyan, green, yellow
import sys


DEFAULT_KUBE_CONFIG = os.path.join(
        os.environ.get("HOME", "/"),
        ".kube",
        "config")


def read_yaml_file(file_name, validate) -> Dict:
    """
    Reads an yaml file
    """
    print(cyan("Reading"),
          cyan(file_name, bold=True))

    with open(file_name, 'r', encoding='utf-8') as f:
        content = f.read()

        if not validate:
            return yaml.safe_load(content)

        if "REDACTED" in content or "DATA+OMITTED" in content:
            print(red("REDACTED", bold=True),
                  red("or"),
                  red("DATA+OMITTED", bold=True),
                  red("found in"),
                  red(file_name, bold=True))
            print(red("Ensure the context was dumped with"),
                  red("--raw", bold=True))
            print(red("i.e."),
                  red("kubectl config view --raw", bold=True))
            sys.exit(3)

        return yaml.safe_load(content)


def merge_kube_context(
        merged_yaml: Dict,
        new_content: Dict) -> None:
    """
    Merges the data from the other context
    """
    for cluster in new_content["clusters"]:
        print(green("Merging cluster"),
              green(cluster["name"], bold=True))
        merged_yaml["clusters"].append(cluster)

    for user in new_content["users"]:
        print(green("Merging user"),
              green(user["name"], bold=True))
        merged_yaml["users"].append(user)

    for context in new_content["contexts"]:
        print(green("Merging context"),
              green(context["name"], bold=True))
        merged_yaml["contexts"].append(context)


def write_yaml_file(file_name, content) -> None:
    """
    Writes the file
    """
    print(yellow("Writing"),
          yellow(file_name, bold=True))

    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(yaml.safe_dump(content))


@click.command()
@click.argument("contexts_to_merge", nargs=-1)
@click.option("--validate/--no-validate",
              default=True,
              help="Validates if the config was saved with --raw.")
@click.option("--output-context",
              default=DEFAULT_KUBE_CONFIG,
              help=f"Specify the .kube/config filename. Defaults to "
                   f"{DEFAULT_KUBE_CONFIG}.")
def main(output_context: str,
         contexts_to_merge: List[str],
         validate: bool) -> None:
    if not contexts_to_merge:
        print(red("Paths to the contexts to be merged was not provided."
                  " Pass it as an argument."))
        sys.exit(1)

    merged_yaml = read_yaml_file(output_context, validate)

    for f in contexts_to_merge:
        new_context = read_yaml_file(f, validate)
        merge_kube_context(
                merged_yaml,
                new_context)

    write_yaml_file(output_context, merged_yaml)


if __name__ == '__main__':
    main()
