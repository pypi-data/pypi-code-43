# Copyright 2019 Genymobile
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Cli for subcommand recipes
"""

import click
from tabulate import tabulate

from .checks import credentials_required
from ..saas import get_client, authcache

from ..logger import LOGGER


RECIPES_TABLE_HEADERS = ["UUID", "NAME", "ANDROID", "SCREEN", "SOURCE"]
NAME_HEADER_INDEX = RECIPES_TABLE_HEADERS.index("NAME")
ANDROID_HEADER_INDEX = RECIPES_TABLE_HEADERS.index("ANDROID")
SOURCE_HEADER_INDEX = RECIPES_TABLE_HEADERS.index("SOURCE")


@click.group()
def recipes():
    """
    View your Genymotion Cloud SaaS recipes
    """


@click.command("list")
@click.option("--name", help="Filter results with substring")
@click.pass_context
@credentials_required
def list_recipes(ctx, name):
    """
    List all available recipes
    """
    del ctx
    saas = get_client(authcache.get_email(), authcache.get_password())
    raw_recipes = saas.list_recipes()
    recipe_list = raw_recipes["base"] + raw_recipes["user"] + raw_recipes["shared"]
    LOGGER.debug("%d Recipes available", len(recipe_list))

    if name:
        recipe_list = _filter_recipes_by_name(recipe_list, name)

    recipes_table = _format_recipe_list(recipe_list)
    recipes_table = _sort_recipes_table(recipes_table)
    click.echo(tabulate(recipes_table, headers=RECIPES_TABLE_HEADERS, numalign="left"))


def _filter_recipes_by_name(recipe_list, name):
    return [r for r in recipe_list if name.strip().casefold() in r["name"].casefold()]


def _sort_recipes_table(recipes_table):
    # Recipes are sorted by several criteria which are (by priority ASC):
    # NAME, ANDROID, SOURCE
    return sorted(recipes_table, key=lambda x: (x[SOURCE_HEADER_INDEX], x[ANDROID_HEADER_INDEX], x[NAME_HEADER_INDEX]))


def _format_recipe_list(raw_recipes):
    """
    Format the list of Recipes into a readable table
    """
    formated_recipes = [
        [r["uuid"], r["name"], _get_android_version(r), _get_screen_info(r), r["source"]] for r in raw_recipes
    ]
    return formated_recipes


def _get_recipe_item_data(recipe, field):
    """
    Retrieve the data of the recipe item of the given type for the given recipe
    """
    for i in recipe["items"]:
        if i["type"] == field:
            return i["data"]
    return None


def _get_android_version(recipe):
    """
    Retrieve the Android Version of the given recipe
    """
    data = _get_recipe_item_data(recipe, "ova")
    return data["android_version"] if data else "Unknown"


def _get_screen_info(recipe):
    """
    Retrieve the screen dimension of the given recipe
    """
    item = _get_recipe_item_data(recipe, "screen")
    if not item:
        return "Unknown"
    return "{} x {} dpi {}".format(item["width"], item["height"], item["density"])


recipes.add_command(list_recipes)
