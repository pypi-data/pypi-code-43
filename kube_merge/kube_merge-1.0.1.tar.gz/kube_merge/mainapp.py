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
        new_content: Dict,
        *,
        merge_users: bool,
        merge_clusters: bool) -> None:
    """
    Merges the data from the other context
    """
    if merge_clusters:
        for cluster in new_content["clusters"]:
            print(green("Merging cluster"),
                  green(cluster["name"], bold=True))
            merged_yaml["clusters"].append(cluster)

    if merge_users:
        for user in new_content["users"]:
            print(green("Merging user"),
                  green(user["name"], bold=True))
            merged_yaml["users"].append(user)


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
@click.option("--validate/--no-validate", default=True)
@click.option("--output-context", default=DEFAULT_KUBE_CONFIG)
@click.option("--only-users", is_flag=True)
@click.option("--only-clusters", is_flag=True)
def main(output_context: str,
         contexts_to_merge: List[str],
         validate: bool,
         only_users: bool,
         only_clusters: bool) -> None:
    if not contexts_to_merge:
        print(red("Paths to the contexts to be merged was not provided."
                  " Pass it as an argument."))
        sys.exit(1)

    if only_users and only_clusters:
        print(red("Both only users, and only clusters ware passed"))
        sys.exit(2)

    merge_users = not only_users and not only_clusters or only_users
    merge_clusters = not only_users and not only_clusters or only_clusters

    merged_yaml = read_yaml_file(output_context, validate)

    for f in contexts_to_merge:
        new_context = read_yaml_file(f, validate)
        merge_kube_context(
                merged_yaml,
                new_context,
                merge_users=merge_users,
                merge_clusters=merge_clusters)

    write_yaml_file(output_context, merged_yaml)


if __name__ == '__main__':
    main()
