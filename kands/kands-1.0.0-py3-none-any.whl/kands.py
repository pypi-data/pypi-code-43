import random
import sys
import os
import time

from termcolor import colored, cprint


class Builder:
    """A funny and fake builder, use to show a progress bar but always 
    getting the same result. Just something funny 😃
    """

    def __init__(self):
        self.default_terminal_size = 25
        self.progress_symbol = "\u2588"
        self.progress_background = "\u2591"
        self.cool_features = [
            "Creating rendering cloud",
            "Building genetic vectors",
            "Training neuronal networks",
            "Training REAL neuronal networks",
            "Connecting to skynet",
            "Petting some cats",
            "Destroying all humans... or not",
        ]

    def terminal_size(self):
        """Gets the terminal columns size."""
        try:
            _, columns = os.popen("stty size", "r").read().split()
            return min(int(columns) - 10, 100)
        except ValueError:
            return self.default_terminal_size

    def answer(self):
        sys.stdout.write(colored(f"¡Hola Katha y Salva!\n\n", "blue"))
        sys.stdout.write(
            "Tras un arduo proceso realizado por los más complejos algoritmos, "
            "este programa a generado el siguiente reto que tendréis que resolver:\n\n"
        )
        sys.stdout.write(colored("¡Tenéis que hacer galletas juntos!\n\n", "green"))
        sys.stdout.write(
            "Sandra y yo solemos usar una receta que tiene estos ingredientes:\n\n"
        )
        ingredients = [
            " - 250g de mantequilla",
            " - 250g de azúcar blanco",
            " - 450g de harina",
            " - 1 huevo grande",
            " - 1 cucharada de canela",
            " - 1 cucharada de jengibre",
        ]
        for ingredient in ingredients:
            sys.stdout.write(colored(f"{ingredient}\n", "yellow"))
        sys.stdout.write(
            colored(
                "\n¡No os olvideis de proporcionar pruebas fotográficas!\n\n", "green"
            )
        )
        sys.stdout.write("❤️ ¡Un beso y un abrazo muy grande! ❤️\n\n")

    def run(self):
        """Runs the builder."""
        terminal_size = self.terminal_size()
        for cool_feature in self.cool_features:
            sys.stdout.write(colored(f"[ {cool_feature}... ] ", "magenta"))
            sys.stdout.write(f"{self.progress_background * terminal_size}")
            sys.stdout.flush()
            sys.stdout.write("\b" * (terminal_size))
            for _ in range(terminal_size):
                time.sleep(random.randint(10, 90) / 100)
                sys.stdout.write(colored(self.progress_symbol, "green"))
                sys.stdout.flush()
            sys.stdout.write("\n")
        sys.stdout.write("\n")
        self.answer()
