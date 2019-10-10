import subprocess
import platform

from PyInquirer import prompt

from blyaml.answers_to_yaml import answers_to_yaml
from blyaml.questions import meta_questions, standard_questions


def main():
    print("Welcome")
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


if __name__ == "__main__":
    main()
