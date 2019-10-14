import subprocess
import platform

from PyInquirer import prompt

from blyaml.answers_to_yaml import answers_to_yaml
from blyaml.questions import meta_questions, standard_questions


def main() -> None:
    print(welcome_message())
    with open("test_file.txt", "w+") as file:
        print(file.read())
        text = input("New Text:")
        file.write(text)

    meta_answers = prompt(meta_questions)

    if meta_answers["ignore"] == "false":
        standard_answers = prompt(standard_questions)
    else:
        standard_answers = {}

    answers = {}
    answers.update(meta_answers)
    answers.update(standard_answers)

    yaml = answers_to_yaml(answers)
    output_filename = "output.yaml"
    with open(output_filename, "w") as file:
        file.write(yaml)

    print(f"Your yaml file has been written to: {output_filename}")

    if platform.system() == "Darwin":
        p = subprocess.Popen(
            "pbcopy", env={"LANG": "en_US.UTF-8"}, stdin=subprocess.PIPE
        )
        p.communicate(yaml.encode())
        print(f"Your yaml file has been copied to clipboard.")

    print("Check validation at: https://sesame.brainlabsdigital.com/yaml-validation")


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


if __name__ == "__main__":
    main()
