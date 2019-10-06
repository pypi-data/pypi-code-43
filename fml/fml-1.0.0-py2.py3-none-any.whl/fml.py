import sys

import cowsay
import html
import json
import os
import requests
import random


class Fml:
    data_file_path = os.getenv("HOME") + "/.fml_data"

    @staticmethod
    def data_file_exists():
        return os.path.exists(Fml.data_file_path)

    @staticmethod
    def set_name(first_name, last_name):

        if first_name is None or last_name is None:
            return "First name or last name is invalid"

        if not first_name.isalpha() or not last_name.isalpha():
            print("First name and last name can just contain alphabets")
            return

        data = {"first_name": first_name, "last_name": last_name}

        with open(Fml.data_file_path, "w") as data_file_handle:
            data_file_handle.write(json.dumps(data))
        return

    @staticmethod
    def get_joke():
        if not Fml.data_file_exists():
            first_name = "Chuck"
            last_name = "Norris"
        else:
            data = json.load(open(Fml.data_file_path))
            first_name = data["first_name"]
            last_name = data["last_name"]

        url = f"http://api.icndb.com/jokes/random?firstName={first_name}&lastName={last_name}"
        icndb_response = requests.get(url)

        if not 200 <= icndb_response.status_code <= 299:
            return "Oops! Something is wrong. I wasn't able to tell you a joke :/"

        return icndb_response.json().get("value").get("joke")

    def joke_with_character(self):
        characters = {
            "beavis": cowsay.beavis,
            "cheese": cowsay.cheese,
            "daemon": cowsay.daemon,
            "cow": cowsay.cow,
            "dragon": cowsay.dragon,
            "ghostbusters": cowsay.ghostbusters,
            "kitty": cowsay.kitty,
            "meow": cowsay.meow,
            "milk": cowsay.milk,
            "stegosaurus": cowsay.stegosaurus,
            "stimpy": cowsay.stimpy,
            "turkey": cowsay.turkey,
            "turtle": cowsay.turtle,
            "tux": cowsay.tux,
        }
        joke = html.unescape(Fml.get_joke())
        characters[random.choice(cowsay.char_names)](joke)


def main():
    if len(sys.argv) == 1:
        Fml().joke_with_character()
        return

    argument = sys.argv[1]

    if len(sys.argv) == 2:
        if argument == "--help":
            print(
                "To see a joke on your terminal. Type fml\nTo set a custom name instead of Chuck Norris"
                " use, fml --name <first-name> <last-name>\nExample: fml --name Jhon Doe will use Jhon Doe as the"
                " character instead of Chuck Norris\nFacing an issue? or want to drop a feedback? write to me at "
                "slash-arun@outlook.com or create an issue on github at https://github.com/slash-arun/fml/issues"
            )
            return

    if len(sys.argv) == 4:
        if argument == "--name":
            first_name = sys.argv[2]
            last_name = sys.argv[3]
            Fml().set_name(first_name, last_name)
            return

    print(
        "Oops! the command could not be understood. Please type fml --help to see the usage."
    )
