"""LICENSE
Copyright 2015 Hermann Krumrey <hermann@krumreyh.com>

This file is part of toktokkie.

toktokkie is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

toktokkie is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with toktokkie.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

import os
import sys
import argparse
from typing import List, Dict
from datetime import datetime
from subprocess import Popen, check_output
from toktokkie.scripts.Command import Command
from toktokkie.Directory import Directory
from toktokkie.metadata.components.enums import MediaType
from toktokkie.metadata.TvSeries import TvSeries


class SuperCutCommand(Command):
    """
    Class that encapsulates behaviour of the supercut command
    """

    @classmethod
    def name(cls) -> str:
        """
        :return: The command name
        """
        return "supercut"

    @classmethod
    def prepare_parser(cls, parser: argparse.ArgumentParser):
        """
        Prepares an argumentparser for this command
        :param parser: The parser to prepare
        :return: None
        """
        parser.add_argument("directory",
                            help="The directory for which to create a "
                                 "supercut")
        parser.add_argument("--create", action="store_true",
                            help="If this flag is set, "
                                 "will generate new supercut instructions")

    def execute(self):
        """
        Executes the commands
        :return: None
        """
        for command in ["ffmpeg", "mkvmerge", "mkvextract", "mkvpropedit"]:
            if not self.is_installed(command):
                print("{} is not installed. Can not continue.".format(command))
                sys.exit(1)

        directory = Directory(self.args.directory)
        supercut_dir = os.path.join(directory.path, ".supercut")
        supercut_file = os.path.join(supercut_dir, "supercut.txt")

        if directory.metadata.media_type() != MediaType.TV_SERIES:
            print("Only TV Series support supercut instructions")
        elif not self.args.create and not os.path.isfile(supercut_file):
            print("Couldn't find supercut instructions. Run with --create "
                  "to generate an instruction file")
        else:
            if self.args.create:

                if not os.path.isdir(supercut_dir):
                    os.makedirs(supercut_dir)

                if os.path.isfile(supercut_file):

                    while True:
                        resp = input("Instructions exist. "
                                     "Do you want to overwrite the "
                                     "instructions file? (y|n)").lower()
                        if resp in ["y", "n"]:
                            break

                    if resp == "y":
                        self.generate_instructions(directory)
                else:
                    self.generate_instructions(directory)
            else:
                self.create_supercut(directory)

    @staticmethod
    def generate_instructions(directory: Directory):
        """
        Generates a supercut instructions file based on the the existing
        season metadata and episode files
        :param directory: The directory for which to generate the instructions
        :return: None
        """
        metadata = directory.metadata  # type: TvSeries  # type: ignore
        supercut_dir = os.path.join(directory.path, ".supercut")
        supercut_file = os.path.join(supercut_dir, "supercut.txt")

        instructions = "# Supercut Instructions for {}".format(metadata.name)
        instructions += "\n# Example for entry:"
        instructions += "\n# Episode <path-to-episode>:"
        instructions += "\n#   00:15:35-00:17:45; First appearance of char X\n"

        seasons = list(filter(lambda x: x.season_number > 0, metadata.seasons))
        seasons.sort(key=lambda x: x.season_number)

        for season in seasons:
            for episode in sorted(os.listdir(season.path)):
                episode_path = os.path.join(season.name, episode)
                instructions += "\nEpisode {}:".format(episode_path)
                instructions += "\n#" + ("-" * 80)

        with open(supercut_file, "w") as f:
            f.write(instructions)

    def create_supercut(self, directory: Directory):
        """
        Creates the supercut file
        :param directory: The directory for which to create a supercut
        :return: None
        """
        metadata = directory.metadata  # type: TvSeries  # type: ignore

        supercut_dir = os.path.join(directory.path, ".supercut")
        supercut_file = os.path.join(supercut_dir, "supercut.txt")
        instructions = self.read_supercut_instructions(
            metadata, supercut_file
        )

        chapter_info = []
        for instruction in instructions:
            chapter_info.append(self.cut_part(supercut_dir, instruction))

        files = list(map(lambda x: x["file"], chapter_info))
        chapters = list(map(lambda x: x["title"], chapter_info))

        supercut_result = self.merge_parts(supercut_dir, files)
        self.adjust_chapter_names(supercut_result, chapters)

    @staticmethod
    def read_supercut_instructions(metadata: TvSeries, supercut_file: str) \
            -> List[Dict[str, str]]:
        """
        Reads the supercut instructions file and generates an easily
        processable configuration list
        :param metadata: The metadata used for additional information
        :param supercut_file: The supercut file to parse
        :return: A list of dicitonaries modelling the individual parts of the
                 supercut in order
        """
        with open(supercut_file, "r") as f:
            instructions = f.read()

        config = []
        episode_file = None
        part_count = 0

        for line in instructions.split("\n"):
            line = line.strip()

            if line.startswith("#") or line == "":
                pass
            elif line.lower().startswith("episode "):
                episode_file = line.split(" ", 1)[1].rsplit(":", 1)[0]
                episode_file = os.path.join(
                    metadata.directory_path, episode_file
                )
            elif episode_file is None:
                raise ValueError("Instructions Syntax Error")
            elif not episode_file.endswith(".mkv"):
                print("WARNING: ONLY MKV FILES ARE SUPPORTED")
            else:
                part_count += 1
                config.append({
                    "start": line.split("-")[0].strip(),
                    "end": line.split("-")[1].split(";")[0].strip(),
                    "title": line.split(";")[1].strip(),
                    "file": episode_file,
                    "part": str(part_count).zfill(4)
                })

        return config

    def cut_part(self, supercut_dir: str, instruction: Dict[str, str]) \
            -> Dict[str, str]:
        """
        Cuts a part of a video file based on a supercut instruction using
        ffmpeg
        :param supercut_dir: The supercut directory in which to
                             store the output
        :param instruction: The instruction to use
        :return: A dictionary detailing the path to the cut clip and its title
        """

        input_file = instruction["file"]
        output_file = os.path.join(
            supercut_dir,
            "{} - {}.mkv".format(instruction["part"], instruction["title"])
        )

        start_time = instruction["start"]
        end_time = instruction["end"]
        delta = self.calculate_clip_duration(start_time, end_time)

        if not os.path.isfile(output_file):
            Popen([
                "ffmpeg",
                "-ss", start_time,
                "-i", input_file,
                "-t", str(delta),
                output_file
            ]).wait()

        return {"file": output_file, "title": instruction["title"]}

    @staticmethod
    def merge_parts(supercut_dir: str, files: List[str]) -> str:
        """
        Merges a list of MKV files and stores them in supercut.mkv
        :param supercut_dir: The supercut directory
        :param files: The files to combine
        :return: The path to the combined file
        """
        dest = os.path.join(supercut_dir, "supercut.mkv")
        mkvmerge_com = [
            "mkvmerge",
            "-o", dest,
            "--generate-chapters", "when-appending",
            files.pop(0)
        ]
        mkvmerge_com += list(map(lambda x: "+" + x, files))
        Popen(mkvmerge_com).wait()
        return dest

    @staticmethod
    def adjust_chapter_names(supercut_result: str, chapters: List[str]):
        """
        Changes the chapter names of a file to a given list of chapter names
        :param supercut_result: The file of which the chapters should be
                                renamed
        :param chapters: The chapter names
        :return: None
        """
        chapters_info = check_output([
            "mkvextract", "chapters", supercut_result
        ]).decode("utf-8")

        adjusted = []

        for line in chapters_info.split("\n"):
            if line.strip().startswith("<ChapterString>"):
                adjusted.append("<ChapterString>{}</ChapterString>".format(
                    chapters.pop(0)
                ))
            else:
                adjusted.append(line)

        with open("chapters.xml", "w") as f:
            f.write("\n".join(adjusted))

        Popen([
            "mkvpropedit", supercut_result, "--chapters", "chapters.xml"
        ]).wait()

        os.remove("chapters.xml")

    @staticmethod
    def calculate_clip_duration(start: str, end: str) -> int:
        """
        Calculates the tme delta in seconds between two timestamps
        :param start: The starting timestamp
        :param end: The ending timestamp
        :return: The time delta in seconds
        """
        start_hour, start_minute, start_second = \
            list(map(lambda x: int(x), start.split(":")))
        end_hour, end_minute, end_second = \
            list(map(lambda x: int(x), end.split(":")))

        _start = datetime(1, 1, 1, start_hour, start_minute, start_second)
        _end = datetime(1, 1, 1, end_hour, end_minute, end_second)
        return (_end - _start).seconds

    @staticmethod
    def is_installed(command: str) -> bool:
        """
        Checks whether or not a command is installed/in the path
        :param command: THe command to check
        :return: True if installed, else False
        """
        for path in os.environ["PATH"].split(":"):
            if os.path.isfile(os.path.join(path, command)):
                return True
        return False
