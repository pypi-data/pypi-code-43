from argparse import ArgumentParser
import subprocess
import platform
from pathlib import Path

import requests
from PyInquirer import prompt

from blyaml.answers_to_yaml import answers_to_yaml
from blyaml.questions import meta_questions, standard_questions


def main() -> None:
    token = get_token()
    print(welcome_message())

    meta_answers = prompt(meta_questions())
    print("Checking Sesame API for valid values ...")
    if meta_answers["ignore"] == "false":
        standard_answers = prompt(standard_questions(token))
    else:
        standard_answers = {}

    answers = {**meta_answers, **standard_answers}
    yaml = answers_to_yaml(answers)

    output_filename = "output.yaml"
    with open(output_filename, "w") as file:
        file.write(yaml)
    print(f"\nYour yaml file has been written to: {output_filename}")

    if platform.system() == "Darwin":  # Darwin is macOS
        copy_to_clipboard(yaml)
        print(f"Your yaml file has been copied to clipboard.")

    try:
        if validate(yaml, token):
            print("\nYour yaml appears to be valid.")
        else:
            print("\nYour yaml appears to be invalid.")
    except requests.RequestException:
        print("\nYour yaml was not able to validated by the Sesame API.")
    print("Check validation at: https://sesame.brainlabsdigital.com/yaml-validation")


def get_token() -> str:
    parser = ArgumentParser()
    parser.add_argument(
        "--reset",
        dest="reset",
        default=False,
        action="store_true",
        help="Reset the token",
    )
    args = parser.parse_args()

    token_file = Path.home() / ".blyaml_token.txt"
    with open(token_file, "a+") as file:
        file.seek(0)
        token = file.read()
    if not token or args.reset:
        with open(token_file, "w") as file:
            token = input("Sesame token: ")
            print("\n")
            file.write(token)
    return token


def welcome_message() -> str:
    bold = "\033[1m"
    end = "\033[0m"
    return (
        f"{bold}Welcome to the Brainlabs YAML Generator.{end}\n"
        + "\n"
        + "You will be asked a series of questions to generate your yaml.\n"
        + "Arrow keys select, enter confirms. "
        + "Spacebar is used in multi select questions"
        + "\n"
    )


def copy_to_clipboard(text: str) -> None:
    p = subprocess.Popen("pbcopy", env={"LANG": "en_US.UTF-8"}, stdin=subprocess.PIPE)
    p.communicate(text.encode())


def validate(yaml: str, token: str) -> bool:
    sesame_validate_url = "https://sesame.brainlabsdigital.com/api/validate/"
    headers = {"Authorization": f"token {token}"}
    response = requests.post(
        sesame_validate_url, data={"yaml-string": yaml}, headers=headers
    )
    if response.status_code == 200:
        return response.json()["errors"] == []
    else:
        raise requests.RequestException


if __name__ == "__main__":
    main()
