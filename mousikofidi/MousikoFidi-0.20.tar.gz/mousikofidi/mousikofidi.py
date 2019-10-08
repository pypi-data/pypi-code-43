# MousikóFídi
# Copyright (C) 2019  Hristos N. Triantafillou
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import ast
import datetime
import math
import os
import urllib
import yaml

from flask import (
    Flask,
    abort,
    flash,
    render_template,
    redirect,
    request,
    send_from_directory,
    session,
    url_for,
)
from mutagen.flac import FLAC, FLACNoHeaderError
from mutagen.mp3 import MP3, HeaderNotFoundError as MP3HeaderNotFoundError
from mutagen.mp4 import MP4, MP4StreamInfoError
from mutagen.oggvorbis import OggVorbis, OggVorbisHeaderError
from typing import Union as T


app = Flask(__name__)
debug = os.getenv("FLASK_ENV") == "development"

MAX_COOKIE_SIZE = 4093

LOGOS = {
    "*": "fidi.png",
    "month:10": "fidi-oct.png",
    "month:12": "fidi-dec.png",
    "04-20": "fidi-420.png",
    "08-09": "fidi-birth.png",
}

THEMES = {
    "dark": "/css/water/dark.standalone",
    "light": "/css/water/light.standalone",
    "nes": "/css/nes/nes",
    "terminal": "/css/terminal",
    "terminal-green": "/css/terminal-green",
    "terminal-solarized": "/css/terminal-solarized",
}

try:
    local_config_file = os.path.join(
        os.path.abspath(os.path.dirname(os.getenv("FLASK_APP"))), "fidi.yml"
    )
except (AttributeError, TypeError):
    local_config_file = None
user_config_file = os.path.join(os.getenv("HOME"), ".config", "fidi", "config.yml")

dbg = app.logger.debug
err = app.logger.error
wrn = app.logger.warning

if debug:
    # The local dev server wants the double backslash
    dir_detail_route = "/browse//<path:path>"
    playlistctl_route = "/playlist/<cmd>//<path:path>"
    serve_file_route = "/serve//<path:path>"
else:
    # uwsgi does not!
    dir_detail_route = "/browse/<path:path>"
    playlistctl_route = "/playlist/<cmd>/<path:path>"
    serve_file_route = "/serve/<path:path>"


def quote(string: str) -> str:
    return urllib.parse.quote(string, safe="")


def file_metadata(file_path: str) -> dict:
    ft = None
    if file_path.lower().endswith(".flac"):
        try:
            data_string = FLAC(file_path).pprint()
            ft = "flac"
        except FLACNoHeaderError:
            wrn("This file is not a valid flac file: " + file_path)
            return {}
    elif file_path.lower().endswith(".mp3"):
        try:
            data_string = MP3(file_path).pprint()
            ft = "mp3"
        except MP3HeaderNotFoundError:
            wrn("This file is not a valid mp3 file: " + file_path)
            return {}

    elif file_path.lower().endswith(".ogg"):
        try:
            data_string = OggVorbis(file_path).tags.pprint()
            ft = "ogg"
        except OggVorbisHeaderError:
            wrn("This file is not a valid ogg vorbis file: " + file_path)
            return {}

    elif file_path.lower().endswith(".mp4"):
        try:
            data_string = MP4(file_path).pprint().strip("\xa9").rstrip("\xa9")
            ft = "mp4"
        except MP4StreamInfoError:
            wrn("This file is not a valid mp4 file: " + file_path)
            return {}

    else:
        data_string = ""

    data_dict = {}
    data_list = data_string.split("\n")

    _data = data_list[0]

    if ft:
        # Calculate and inject the track length
        if ft == "mp3":
            raw_length = _data.split(",")[-1].split()[0]
            del data_list[0]

        elif ft in ("flac", "mp4"):
            raw_length = _data.split(",")[1].split()[0]
            del data_list[0]

        elif ft == "ogg":
            raw_length = "0"

        length = str(datetime.timedelta(seconds=math.ceil(float(raw_length)))).split(
            "."
        )[0]

        if length.split(":")[0] == "0":
            length = ":".join(length.split(":")[1:])

        if length.split(":")[0].startswith("00"):
            length = length[1:]

        if length.split(":")[0] != "0" and length.split(":")[0].startswith("0"):
            length = length[1:]

        data_list.append("length=" + length)

    for item in data_list:
        data_dict.update({item.split("=")[0]: item.split("=")[-1]})

    return data_dict


def browse_dir(context: dict, unescaped_path: str) -> dict:
    dbg("Reading Dir: " + unescaped_path)

    try:
        dir_items = sorted(os.listdir(unescaped_path))
    except PermissionError:
        dbg("Got a PermissionError on '{}'!".format(unescaped_path))
        dir_items = list()
        flash(
            """<p class="bold center red">The directory '{}' could not be read due to a permissions error!</p>""".format(
                unescaped_path
            )
        )

    dir_list = []
    file_list = []
    _item_list = []

    for i in dir_items:
        item_path = os.path.join(unescaped_path, i)
        metadata = get_metadata_dict(item_path)

        if is_audio_file(item_path):
            dbg("Audio found: " + i)
            file_list.append(item_path)
            _item_list.append(file_dict(item_path, metadata, "audio"))
            context["add_all_button"] = True
            context["audio_player"] = True

        elif is_video_file(item_path):
            dbg("Video found: " + i)
            file_list.append(item_path)
            _item_list.append(file_dict(item_path, metadata, "video"))
            context["add_all_button"] = True
            context["video_player"] = True

        elif os.path.isdir(item_path):
            dbg("Dir found: " + i)
            dir_list.append(dir_dict(item_path))

    item_list = make_unique_slugs(_item_list)

    music_dirs = []
    for d in context["music_dirs"]:
        music_dirs.append(d["raw"])

    context["file_list"] = file_list
    context["page_name"] = unescaped_path
    context["page_path"] = breadcrumb_links_from_path(unescaped_path, music_dirs)
    context["playlist_add"] = True
    context["playlist_rm"] = False
    context["item_type"] = "dir"
    context["dir_list"] = dir_list
    context["item_list"] = item_list
    return context


def browse_file(context: dict, unescaped_path: str) -> dict:
    dbg("Reading File: " + unescaped_path)

    file_name = unescaped_path.split("/")[-1]
    metadata = get_metadata_dict(unescaped_path)

    if is_audio_file(unescaped_path):
        context["item_type"] = "audio"

    elif is_video_file(unescaped_path):
        context["item_type"] = "video"

    music_dirs = []
    for d in context["music_dirs"]:
        music_dirs.append(d["raw"])

    for tag in (
        "album",
        "artist",
        "comment",
        "date",
        "encoded_by",
        "genre",
        "length",
        "lyrics",
        "title",
        "track",
        "tracktotal",
    ):
        try:
            context[tag] = metadata[tag]
        except KeyError:
            # A given track may have any or none of the above tags.
            pass

    context["page_name"] = metadata["title"] or file_name
    context["escaped_path"] = quote(unescaped_path)
    context["unescaped_path"] = unescaped_path
    context["file_name"] = file_name
    context["page_path"] = breadcrumb_links_from_path(unescaped_path, music_dirs)

    return context


def config_to_string(config_file: str) -> str:
    try:
        with open(config_file, "r") as f:
            lines = f.readlines()
        return "".join(lines)
    except FileNotFoundError:
        pass


def request_context(config_data: dict) -> dict:
    favicon = select_logo(config_data, "favicon_path")
    logo = select_logo(config_data, "logo_path")
    m = config_data["config"]["music_dirs"]
    music_dirs = paths_list(m)
    playlists = list_playlists(config_data["config"]["playlist"]["dir"])

    try:
        icons = session["icons"]
    except KeyError:
        icons = config_data["config"]["icons"]

    try:
        session_theme = session["theme"]
    except KeyError:
        session_theme = None

    try:
        user_playlist = session["user_playlist"]
    except KeyError:
        user_playlist = []

    try:
        username = session["username"]
    except KeyError:
        username = None

    return {
        "debug": debug,
        "favicon_path": favicon,
        "icons": icons,
        "logo_path": logo,
        "music_dirs": music_dirs,
        "playlist_dir": config_data["config"]["playlist"]["dir"],
        "playlist_save": config_data["config"]["playlist"]["save"],
        "playlists": playlists,
        "preload_audio": config_data["config"]["preload_audio"],
        "preload_video": config_data["config"]["preload_video"],
        "search": config_data["config"]["search"],
        "secret_key": config_data["config"]["secret_key"],
        "site_name": config_data["config"]["site_name"],
        "user_playlist": user_playlist,
        "theme": session_theme or get_theme_from_config(config_data),
        "username": username,
    }


def init(
    fidi_config=None,
    use_config=(
        os.getenv("FIDI_CONFIG_PATH")
        or os.getenv("FIDI_CONFIG")
        or os.getenv("FIDI_CFG_PATH")
        or os.getenv("FIDI_CFG")
        or None
    ),
) -> dict:
    if use_config:
        fidi_config = use_config

    if fidi_config and os.path.isfile(fidi_config):
        dbg("Reading User-Supplied Config: " + fidi_config)

    # uwsgi blows up if we don't first test local_config_file here..
    elif local_config_file and os.path.isfile(local_config_file):
        dbg("Reading Module-Local Config: " + local_config_file)
        fidi_config = local_config_file

    elif os.path.isfile(user_config_file):
        dbg("Reading User Config: " + user_config_file)
        fidi_config = user_config_file

    if fidi_config:
        c = yaml.load(config_to_string(fidi_config), Loader=yaml.BaseLoader)
    else:
        err("")
        err("No valid configuration file was provided!")
        err("Please see this URL for how to get setup with a config file:")
        err("")
        err("https://man.sr.ht/~hristoast/mousikofidi/setup.md#configuring-mousikfdi")
        err("")
        err("MousikóFídi will not work without a valid config file!")
        err("")
        return abort(500)

    # TODO: A more DRY way to handle checking for configs
    try:
        if c["config"]["holidays"].lower() == "true":
            c["config"]["holidays"] = True
        else:
            c["config"]["holidays"] = False
    except KeyError:
        wrn(
            "No 'holidays' value was found in the configuration file!  Defaulting to on..."
        )
        c["config"]["holidays"] = True

    try:
        if c["config"]["icons"].lower() == "true":
            c["config"]["icons"] = True
        else:
            c["config"]["icons"] = False
    except KeyError:
        wrn(
            "No 'icons' value was found in the configuration file!  Defaulting to off..."
        )
        c["config"]["icons"] = False

    # TODO: Re-enable this when db support is added
    # try:
    #     if c["config"]["search"].lower() == "true":
    #         c["config"]["search"] = True
    #     else:
    #         c["config"]["search"] = False
    # except KeyError:
    #     wrn(
    #         "No 'search' value was found in the configuration file!  Defaulting to off..."
    #     )
    #     c["config"]["search"] = False
    c["config"]["search"] = False

    try:
        app.secret_key = c["config"]["secret_key"]
        # Sort of obscure the key
        c["config"]["secret_key"] = True
    except KeyError:
        err(
            "No 'secret_key' was found in the configuration file!  Related functionality will be disabled..."
        )
        c["config"]["secret_key"] = None

    try:
        if c["config"]["playlist"]["save"].lower() == "true":
            c["config"]["playlist"]["save"] = True
        else:
            c["config"]["playlist"]["save"] = False
    except KeyError:
        wrn(
            "No 'playlist.save' value was found in the configuration file!  Defaulting to off..."
        )
        c["config"]["playlist"]["save"] = False

    try:
        if c["config"]["preload_audio"].lower() == "true":
            c["config"]["preload_audio"] = True
        else:
            c["config"]["preload_audio"] = False
    except KeyError:
        wrn(
            "No 'preload_audio' value was found in the configuration file!  Defaulting to off..."
        )
        c["config"]["preload_audio"] = False

    try:
        if c["config"]["preload_video"].lower() == "true":
            c["config"]["preload_video"] = True
        else:
            c["config"]["preload_video"] = False
    except KeyError:
        wrn(
            "No 'preload_video' value was found in the configuration file!  Defaulting to off..."
        )
        c["config"]["preload_video"] = False

    return c


def get_metadata_dict(file_path: str) -> dict:
    d = {
        "artist": None,
        "album": None,
        "date": None,
        "genre": None,
        "length": None,
        "title": None,
        "track": None,
        "tracktotal": None,
    }
    metadata = file_metadata(file_path)

    if is_audio_file(file_path):
        d.update(
            {
                "album": get_metadata_value(
                    [
                        "ALBUM",
                        "album",
                        # for mp3
                        "TALB",
                    ],
                    metadata,
                )
            }
        )
        d.update(
            {
                "artist": get_metadata_value(
                    [
                        # TODO: make this ordering configurable
                        "ARTIST",
                        "ARTIST_CREDIT",
                        "ARTISTSORT",
                        "artist",
                        "ALBUMARTIST",
                        "ALBUMARTIST_CREDIT",
                        "ALBUMARTISTSORT",
                        # for mp3
                        "TPE1",
                    ],
                    metadata,
                )
            }
        )
        d.update(
            {
                "date": get_metadata_value(
                    [
                        "DATE",
                        "ORIGINALDATE",
                        "YEAR",
                        "date",
                        # for mp3
                        "TDRC",
                    ],
                    metadata,
                )
            }
        )
        d.update(
            {
                "genre": get_metadata_value(
                    [
                        "GENRE",
                        "genre",
                        # for mp3
                        "TCON",
                    ],
                    metadata,
                )
            }
        )
        d.update(
            {
                "title": get_metadata_value(
                    [
                        "TITLE",
                        "title",
                        # for mp3
                        "TIT2",
                    ],
                    metadata,
                )
            }
        )
        d.update({"track": get_metadata_value(["TRACK", "TRACKNUMBER"], metadata)})
        tracktotal = get_metadata_value(
            ["TRACKTOTAL", "TRACKC", "TOTALTRACKS", "TRCK"], metadata
        )

        if tracktotal and "/" in tracktotal:
            # MP3s commonly have the track number and total stored as one value...
            trackdata = tracktotal.split("/")
            d.update({"track": trackdata[0].strip()})
            d.update({"tracktotal": trackdata[1].strip()})

        else:
            d.update({"tracktotal": tracktotal})

        d.update({"comment": get_metadata_value(["COMMENT", "COMM"], metadata)})

        d.update({"encoded_by": get_metadata_value(["ENCODED-BY", "TENC"], metadata)})

        d.update({"lyrics": get_metadata_value(["LYRICS", "USLT"], metadata)})

    elif is_video_file(file_path):
        if file_path.endswith(".mp4"):
            for k, v in metadata.items():

                if "ART" in k:
                    d.update({"artist": v})

                elif "alb" in k:
                    d.update({"album": v})

                elif "cmt" in k:
                    d.update({"comment": v})

                elif "day" in k:
                    d.update({"date": v})

                elif "enc" in k:
                    d.update({"encoded_by": v})

                elif "gen" in k:
                    d.update({"genre": v})

                elif "lyr" in k:
                    d.update({"lyrics": v})

                elif "nam" in k:
                    d.update({"title": v})

                elif "trkn" in k:
                    track_list = v.strip("(").strip(")").split(",")

                    if track_list[0] != "0":
                        d.update({"track": track_list[0].strip(" ")})

                    if track_list[1] != "0":
                        d.update({"tracktotal": track_list[1].strip(" ")})

    d.update({"length": get_metadata_value(["length"], metadata)})
    return d


def get_metadata_value(key_list: list, metadata: dict) -> T[str, None]:
    for key in key_list:
        try:
            return metadata[key].strip()
        except KeyError:
            pass
    return None


def get_theme_from_config(config: dict) -> str:
    theme = config["config"]["theme"].lower()
    if theme in THEMES.keys():
        return THEMES[theme]
    elif theme:
        return theme


def dir_dict(path: str) -> dict:
    return {
        "dir_name": path.split(os.path.sep)[-1],
        "escaped_path": quote(path),
        "unescaped_path": path,
    }


def file_dict(path: str, metadata: dict, ftype: str, title_limit=17) -> dict:
    file_name = path.split(os.path.sep)[-1]
    file_name_mobile = path.split(os.path.sep)[-1]
    title = metadata["title"]
    title_mobile = title

    if len(file_name.split()) == 1 and len(file_name) > title_limit:
        file_name_mobile = file_name[:title_limit] + "…"

    if title:
        if len(title.split()) == 1 and len(title) > title_limit:
            title_mobile = title[:title_limit] + "…"

    return {
        "album": metadata["album"],
        "artist": metadata["artist"],
        "genre": metadata["genre"],
        "length": metadata["length"],
        "title": title,
        "title_mobile": title_mobile,
        "track": metadata["track"],
        "type": ftype,
        "tracktotal": metadata["tracktotal"],
        "file_name": file_name,
        "file_name_mobile": file_name_mobile,
        "escaped_path": quote(path),
        "unescaped_path": path,
        "slug": title_slug(title or file_name),
    }


def breadcrumb_links_from_path(path: str, music_dirs: list) -> str:
    link_string = ""
    path_string = ""

    for d in music_dirs:
        if path.startswith(d):
            link_string += '<a href="/browse/{escaped}">{unescaped}</a>'.format(
                escaped=quote(d), unescaped=d
            )
            path_string += d
            new_path = path.replace(d, "").strip("/")
            dir_list = new_path.split("/")

            for dd in dir_list:
                if dd:
                    path_string = os.path.join(path_string, dd)
                    if os.path.isdir(path_string):
                        link_string += ' / <a href="/browse/{escaped}">{dir_name}</a>'.format(
                            escaped=quote(path_string), dir_name=dd
                        )
                    elif os.path.isfile(path_string):
                        link_string += " / {}".format(dd)
    return link_string


def get_playlists(pdir: str) -> list:
    plist_contents = []
    plists = []

    if os.path.isdir(pdir):
        for plist in os.listdir(pdir):
            ppath = os.path.join(pdir, plist)

            with open(ppath, "r") as f:
                plist_contents = f.readlines()

            plists.append(
                {
                    "name": plist.split(".m3u")[0],
                    "filename": plist,
                    "count": len(plist_contents),
                }
            )

        return sorted(plists, key=lambda n: n["name"])
    return list()


def handle_playlist_cmd(cmd: str, path: str, context: dict) -> dict:
    # This is only used in one view but was created in order to keep
    # all of this business out of the main view function.

    flashme = """<p class="bold center red">The playlist add operation could not be
completed because it would cause the playlist to exceed the max cookie size!</p>
<p class="bold center red">See <a href="https://man.sr.ht/~hristoast/mousikofidi/user_guide.md#adding-tracks-to-the-playlist">
this User's Guide entry</a> for more information.</p>"""

    p_size = len(bytes(str(context["user_playlist"]), "utf8"))
    dbg("p_size: " + str(p_size))

    if cmd == "add":
        new_size = p_size + len(bytes(str(path), "utf8"))
        if new_size < MAX_COOKIE_SIZE:
            dbg("Adding item to playlist: " + path)
            context["user_playlist"].append(path)

        else:
            dbg("Cookie overflow detected, preventing add operation...")
            context["flashed"] = True
            flash(flashme)

    elif cmd == "bulk":
        bulk = ast.literal_eval(request.form["bulk-list"])
        new_size = p_size + len(bytes(str(bulk), "utf8"))
        if new_size < MAX_COOKIE_SIZE:
            dbg("Bulk adding items to playlist:")
            for path in bulk:
                dbg("Adding: " + path)
                context["user_playlist"].append(path)
            flash(
                """<p class="bold center green">All files in this dir added to your playlist!</p>"""
            )

        else:
            dbg("Cookie overflow detected, preventing bulk operation...")
            flash(flashme)

    elif cmd == "clear":
        if path == "/all":
            if len(bytes(str(context["user_playlist"]), "utf8")) < MAX_COOKIE_SIZE:
                flash(
                    """<p class="bold center green">Your playlist was cleared!</p>
<form id="playlistctl" action="/playlist/clear/%2Fundo" class="center" method="post">
  <input class="center" id="undo-clear" name="undo-clear" title="Undo clearing the playlist." value="Undo?" type="submit" />
  <input id="to-load" name="to-load" type="hidden" value="{}">
</form>""".format(
                        quote(str(context["user_playlist"]))
                    )
                )
            else:
                flash(
                    """<p class="bold center green">Your playlist was cleared but it was too big for an undo!</p>"""
                )
            context["user_playlist"] = []

        elif path == "/undo":
            dbg("Undoing playlist clear!")
            context["user_playlist"] = ast.literal_eval(
                urllib.parse.unquote(request.form["to-load"])
            )
            flash('<p class="bold center green">The playlist clear was undone!</p>')

    elif cmd == "load":
        playlist_dir = context["playlist_dir"]
        to_load = request.form["to-load"]
        new_size = p_size + len(bytes(str(to_load), "utf8"))
        full_path = os.path.join(playlist_dir, to_load + ".m3u")

        if "delete" in request.form or "really-delete" in request.form:
            if "delete" in request.form:
                if os.path.isfile(full_path):
                    flash(
                        """<p><form action="/playlist/load/%2Fdelete-confirm" class="center" id="playlistctl" method="post">
  <input class="center red" id="really-delete" name="really-delete" title="Verify to delete the selected playlist file." value="Really delete '{0}'?" type="submit" />
  <input id="to-load" name="to-load" type="hidden" value="{0}">
</form></p>""".format(
                            to_load
                        )
                    )
                    return context

            elif "really-delete" in request.form:
                os.remove(full_path)
                flash(
                    '<p class="bold center green">The playlist "{}" was deleted!</p>'.format(
                        to_load
                    )
                )

                return context

        if new_size < MAX_COOKIE_SIZE:
            load_error = False
            loaded = []

            if os.path.isfile(full_path):
                dbg("Loading playlist: " + full_path)
                content = []

                with open(full_path, "r") as f:
                    content = f.readlines()

                if content:
                    for line in content:
                        _line = line.rstrip()

                        if os.path.isfile(_line) and is_valid_path(context, _line):
                            dbg("Loading track: " + _line)
                            context["user_playlist"].append(_line)
                            loaded.append(_line)

                        else:
                            load_error = '<p class="bold center red">The playlist "{}" was loaded with errors!</p>'
                            err("Could not load track path: " + _line)

                else:
                    load_error = '<p class="bold center red">The playlist "{}" is empty and cannot be loaded!</p>'.format(
                        to_load
                    )

            if not loaded:
                load_error = '<p class="bold center red">The playlist "{}" was unable to load due to errors!</p>'

            if load_error:
                flash(load_error.format(to_load))

            else:
                flash(
                    '<p class="bold center green">The playlist "{}" was loaded!</p>'.format(
                        to_load
                    )
                )
        else:
            dbg("Cookie overflow detected, preventing load operation...")
            flash(flashme)

    elif cmd == "rm":
        dbg("Removing item from playlist: " + path)
        flash(
            """<p class="bold center green">The track '{}' was removed from the playlist!</p>""".format(
                get_metadata_dict(path)["title"]
            )
        )
        context["user_playlist"].remove(path)

    elif cmd == "save":
        allowed_chars = (" ", "_", "+")
        bulk_list = request.form.get("bulk-list")
        if bulk_list:
            bulk_paths = ast.literal_eval(bulk_list)
        else:
            bulk_paths = ast.literal_eval(
                urllib.parse.unquote(request.form.get("to-save"))
            )
        playlist_content = []
        playlist_dir = context["playlist_dir"]
        raw_file_name = request.form["file-name"]
        cleaned_file_name = "".join(
            s for s in raw_file_name if s.isalnum() or s in allowed_chars
        )
        full_path_file_name = os.path.join(playlist_dir, cleaned_file_name) + ".m3u"

        if not cleaned_file_name:
            flash(
                '<p class="bold center red">Playlist names may only contain alphanumeric characters, spaces, underscores, or plus signs!</p>'
            )
            return context

        if os.path.isfile(full_path_file_name):
            if "save" in request.form:

                flash(
                    """<p><form action="/playlist/save/%2Fsave-confirm" class="center" id="playlistctl" method="post">
  <input class="center red" id="really-save" name="really-save" title="Verify overwrite selected playlist file." value="Overwrite Existing playlist '{0}'?" type="submit" />
  <input id="file-name" name="file-name" type="hidden" value="{0}">
  <input id="to-save" name="to-save" type="hidden" value='{1}'>
</form></p>""".format(
                        cleaned_file_name, quote(str(context["user_playlist"]))
                    )
                )
                return context

            elif "really-save" in request.form:
                pass

        for p in bulk_paths:
            playlist_content.append(p)
            playlist_content.append("\n")

        with open(full_path_file_name, "w") as f:
            for line in playlist_content:
                f.write(line)

        dbg("Playlist written: " + full_path_file_name)
        flash(
            '<p class="bold center green">The playlist "{}" was saved.</p>'.format(
                cleaned_file_name
            )
        )

    return context


def is_audio_file(file_path: str) -> bool:
    return os.path.isfile(file_path) and (
        file_path.endswith(".flac")
        or file_path.endswith(".mp3")
        or file_path.endswith(".ogg")
    )


def is_video_file(file_path: str) -> bool:
    return os.path.isfile(file_path) and (
        file_path.endswith(".mp4") or file_path.endswith(".webm")
    )


def is_valid_path(request_context: dict, path: str) -> bool:
    _path = path.strip("/").rstrip("/")
    abs_path = os.path.abspath(os.path.sep + _path)
    for d in request_context["music_dirs"]:
        raw_path = d["raw"]
        if abs_path.startswith(raw_path):
            return True
    return False


def list_playlists(playlist_dir: str) -> list:
    playlists = []
    dbg("Checking playlist dir: " + playlist_dir)
    if os.path.isdir(playlist_dir):
        contents = os.listdir(playlist_dir)
        if contents:
            for i in contents:
                if i.endswith(".m3u"):
                    p = os.path.join(playlist_dir, i)
                    playlists.append(p)
    return sorted(playlists)


def make_unique_slugs(item_list: list) -> list:
    used_slugs = []
    count = 0
    slug_extra = 0
    for i in item_list:
        if "slug" in i.keys():
            if i["slug"] in used_slugs:
                newslug = i["slug"] + str(slug_extra)
                while newslug in used_slugs:
                    slug_extra += 1
                    newslug = i["slug"] + str(slug_extra)
                item_list[count]["slug"] = newslug
                used_slugs.append(newslug)
            else:
                used_slugs.append(i["slug"])
            count += 1
    return item_list


def paths_list(music_dirs: list) -> list:
    dl = []
    for md in music_dirs:
        enc = quote(md)
        dl.append({"raw": md.rstrip("/"), "encoded": enc})
    return dl


def search_files(q: str, only_audio: bool, only_video: bool) -> list:
    hits = []
    mdirs = app.fidiConfig["config"]["music_dirs"]
    audio_exts = ("flac", "mp3", "ogg")
    video_exts = ("mp4", "webm")
    _exts = audio_exts + video_exts
    for topdir in mdirs:
        for dirpath, dirnames, files in os.walk(topdir):
            for name in files:
                ext = name.lower().split(".")[-1]
                if ext in _exts:
                    _file = os.path.join(dirpath, name)
                    md = get_metadata_dict(_file)

                    if not only_video and ext in audio_exts:
                        for k, v in file_dict(_file, md, "audio").items():

                            if (
                                v
                                and "_mobile" not in k
                                and "_path" not in k
                                and "slug" not in k
                            ):
                                if _file not in hits and (
                                    q in v.lower() or q in _file.lower()
                                ):
                                    hits.append(_file)

                    elif not only_audio and ext in video_exts:
                        for k, v in file_dict(_file, md, "video").items():

                            if (
                                v
                                and "_mobile" not in k
                                and "_path" not in k
                                and "slug" not in k
                            ):
                                if _file not in hits and (
                                    q in v.lower() or q in _file.lower()
                                ):
                                    hits.append(_file)
    return hits


def select_logo(config: dict, item: str, fakenow=None) -> str:
    # Don't spoil a user's custom settings
    if config["config"]["favicon_path"] != "/fidi.png":
        return config["config"]["favicon_path"]

    # Same here
    if config["config"]["logo_path"] != "/fidi.png":
        return config["config"]["logo_path"]

    if config["config"]["holidays"]:
        logo = config["config"]["logo_path"]

        if fakenow:
            now = fakenow
        else:
            now = datetime.datetime.now()

        for logo_date in LOGOS.keys():
            if "-" in logo_date:
                sdate = logo_date.split("-")

                if len(sdate) == 2:
                    month, date = sdate
                    today_month, today_date = now.strftime("%m-%d").split("-")

                    if month == today_month and date == today_date:
                        dbg(
                            "Activating holiday {item} for '{date}'!".format(
                                item=item, date=logo_date
                            )
                        )
                        logo = "/" + LOGOS[logo_date]

            elif ":" in logo_date:
                date_type, date = logo_date.split(":")

                if date_type == "day":
                    if date == now.strftime("%d"):
                        dbg(
                            "Activating holiday {item} for '{date}'!".format(
                                item=item, date=logo_date
                            )
                        )
                        logo = "/" + LOGOS[logo_date]

                elif date_type == "month":
                    if date == now.strftime("%m"):
                        dbg(
                            "Activating holiday {item} for '{date}'!".format(
                                item=item, date=logo_date
                            )
                        )
                        logo = "/" + LOGOS[logo_date]

            elif logo_date == "*":
                logo = "/" + LOGOS[logo_date]

        if debug:
            logo = "/static" + logo

        return logo

    else:
        # No holidays!
        if debug:
            return "/static" + config["config"][item]
        return config["config"][item]


def title_slug(title: str, slug_limit=20) -> str:
    return "".join(thing for thing in title if thing.isalnum()).lower()[:slug_limit]


app.fidiConfig = init()


# Begin routes
@app.errorhandler(404)
def not_found(e):
    c = request_context(app.fidiConfig)
    c["code"] = 404
    c["error_text"] = "The page you requested does not exist!"
    c["page_name"] = "404 Not Found"
    return (render_template("error.html", **c), c["code"])


@app.errorhandler(500)
def internal_server_error(e):
    c = request_context(app.fidiConfig)
    c["code"] = 500
    c[
        "error_text"
    ] = "A programming error has occured.  Check the application log for more information."
    c["page_name"] = "Internal Server Error"
    return (render_template("error.html", **c), c["code"])


@app.route("/")
def index():
    c = request_context(app.fidiConfig)
    c["page_name"] = "Welcome to {}!".format(c["site_name"])
    c["plists"] = get_playlists(c["playlist_dir"])
    return render_template("index.html", **c)


@app.route("/about")
def about():
    c = request_context(app.fidiConfig)
    c["page_name"] = "About MousikóFídi"
    return render_template("about.html", **c)


@app.route("/browse")
def browse():
    c = request_context(app.fidiConfig)

    c["dir_list"] = c["music_dirs"]
    c["page_name"] = "Media Dirs"
    c["plists"] = get_playlists(c["playlist_dir"])
    c["top_link"] = True
    return render_template("dirs.html", **c)


@app.route(dir_detail_route)
def dir_detail(path):
    _c = request_context(app.fidiConfig)
    unescaped = os.path.sep + urllib.parse.unquote(path)

    if not is_valid_path(_c, unescaped):
        return abort(404)

    if os.path.isfile(unescaped):
        c = browse_file(_c, unescaped)

    elif os.path.isdir(unescaped):
        c = browse_dir(_c, unescaped)
        c["top_link"] = True

    else:
        abort(404)

    c["link_button"] = True
    return render_template("dir_detail.html", **c)


@app.route("/playlist")
def playlist():
    c = request_context(app.fidiConfig)
    _item_list = []
    _video_list = []
    file_list = []
    item_list = None
    video_list = None
    playlist_items = c["user_playlist"]
    playlist_names = []

    for p in c["playlists"]:
        name = os.path.split(p)[-1].replace(".m3u", "")
        playlist_names.append(name)

    if playlist_items:
        for i in playlist_items:
            dbg("playlist item: " + i)
            metadata = get_metadata_dict(i)
            if is_audio_file(i):
                file_list.append(i)
                _item_list.append(file_dict(i, metadata, "audio"))
            elif is_video_file(i):
                _video_list.append(file_dict(i, metadata, "video"))
                file_list.append(i)

    if _item_list:
        item_list = make_unique_slugs(_item_list)

    if _video_list:
        video_list = make_unique_slugs(_video_list)

    c["file_list"] = file_list
    c["item_list"] = item_list
    c["video_list"] = video_list
    c["playlist_add"] = False
    c["playlist_names"] = playlist_names
    c["playlist_rm"] = True
    c["playlistctl"] = True
    c["page_name"] = "Playlist"
    c["top_link"] = True
    return render_template("playlist.html", **c)


@app.route("/playlists")
def playlists():
    c = request_context(app.fidiConfig)

    c["page_name"] = "Playlists"
    c["plists"] = get_playlists(c["playlist_dir"])
    c["top_link"] = True

    return render_template("playlists.html", **c)


@app.route("/playlist/<name>")
def playlist_detail(name):
    c = request_context(app.fidiConfig)
    file_list = []
    item_list = []
    video_list = []
    _item_list = []
    _video_list = []
    bunk_tracks = []

    plist_file = os.path.join(c["playlist_dir"], name + ".m3u")

    if os.path.isfile(plist_file):
        with open(plist_file) as f:
            playlist_items = f.readlines()

        for _i in playlist_items:
            i = _i.rstrip("\n")
            dbg("playlist item: " + i)
            if is_audio_file(i):
                metadata = get_metadata_dict(i)
                file_list.append(i)
                _item_list.append(file_dict(i, metadata, "audio"))
            elif is_video_file(i):
                metadata = get_metadata_dict(i)
                _video_list.append(file_dict(i, metadata, "video"))
                file_list.append(i)
            else:
                bunk_tracks.append(i)
    else:
        return abort(404)

    if bunk_tracks:
        err(
            "The following items in this playlist could not be loaded because they are not valid audio or video:"
        )
        for t in bunk_tracks:
            err(t)

    if _item_list:
        item_list = make_unique_slugs(_item_list)

    if _video_list:
        video_list = make_unique_slugs(_video_list)

    c["link_button"] = True
    c["file_list"] = file_list
    c["item_list"] = item_list
    c["video_list"] = video_list
    c["page_name"] = "Playlist: " + name
    c["playlist_add"] = True
    c["playlist_detail"] = True
    c["playlist_name"] = name
    c["top_link"] = True

    return render_template("playlist.html", **c)


@app.route(playlistctl_route, methods=("POST",))
def playlistctl(cmd, path):
    c = request_context(app.fidiConfig)
    p = os.path.join(os.path.sep, path)

    if path == "load-with-redirect":
        u = "/playlist"
    else:
        u = request.referrer

    c = handle_playlist_cmd(cmd, p, c)

    if (
        "flashed" not in c.keys()
        and cmd == "add"
        and request.form["slug"] is not "track-detail-no-slug"
    ):
        u += "#{}".format(request.form["slug"] + "-target")

    session["user_playlist"] = c["user_playlist"]

    return redirect(u)


@app.route("/search")
def search():
    if not app.fidiConfig["config"]["search"]:
        return abort(404)

    c = request_context(app.fidiConfig)
    c["page_name"] = "File Search"

    audio_list = []
    _audio_list = []
    video_list = []
    _video_list = []
    hits = []

    q = request.args.get("q")
    only_audio = request.args.get("only-audio") == "on"
    only_video = request.args.get("only-video") == "on"

    if only_audio and only_video:
        flash(
            """<p class="bold center red">The "Only Audio" and "Only Video" options cannot be used together!</p>"""
        )

    elif q:
        hits = search_files(q, only_audio, only_video)

    if hits:
        for hit in hits:
            md = get_metadata_dict(hit)
            if is_audio_file(hit):
                _audio_list.append(file_dict(hit, md, "audio"))

            elif is_video_file(hit):
                _video_list.append(file_dict(hit, md, "video"))

        audio_list = make_unique_slugs(_audio_list)
        video_list = make_unique_slugs(_video_list)

    c["hits"] = hits
    c["item_list"] = audio_list
    c["video_list"] = video_list
    c["only_audio"] = only_audio
    c["only_video"] = only_video
    c["q"] = q
    # TODO: The add all button here
    # c["add_all_button"] = True
    c["link_button"] = True
    c["top_link"] = True

    return render_template("search.html", **c)


@app.route(serve_file_route)
def serve_file(path):
    _c = request_context(app.fidiConfig)
    if not is_valid_path(_c, path):
        return abort(404)
    _path = os.path.sep + urllib.parse.unquote(path).rstrip("/")
    dirname = os.path.sep.join((_path.split(os.path.sep)[:-1]))
    dbg("dirname: " + dirname)
    filename = _path.split(os.path.sep)[-1]
    dbg("filename: " + filename)
    if filename.endswith(".flac"):
        mimetype = "audio/flac"
    elif filename.endswith(".mp3"):
        mimetype = "audio/mpeg"
    elif filename.endswith(".mp4"):
        mimetype = "video/mp4"
    elif filename.endswith(".webm"):
        mimetype = "video/webm"
    else:
        return send_from_directory(dirname, filename)
    return send_from_directory(dirname, filename, mimetype=mimetype)


@app.route("/settings")
def settings():
    c = request_context(app.fidiConfig)

    themes = []
    for theme in THEMES.keys():
        if theme == "nes":
            themes.append({"name": theme, "proper": theme.upper()})
        else:
            themes.append({"name": theme, "proper": theme.capitalize()})

    c["themes"] = themes
    c["page_name"] = "Settings"
    return render_template("settings.html", **c)


@app.route("/settings/edit", methods=("POST",))
def settings_edit():
    _icons = request.form.get("icons")
    _theme = request.form.get("theme")

    if _theme:
        session["theme"] = THEMES[_theme]

    if _icons == "disabled":
        dbg("DISABLING")
        session["icons"] = False
        dbg(str(session["icons"]))
    elif _icons == "enabled":
        dbg("ENABLING")
        session["icons"] = True
        dbg(str(session["icons"]))

    return redirect(url_for(".settings"))


@app.route("/test-js")
def test_js():
    _audio_list = []
    _video_list = []
    audio_list = []
    video_list = []
    example_dir = os.path.abspath(os.path.join(os.getcwd(), "example"))
    single_file_e = None

    if os.path.isdir(example_dir):

        for a in (
            "fake.flac",
            "fake.mp3",
            "fake.ogg",
            "real.flac",
            "real.mp3",
            "real.ogg",
        ):
            path = os.path.join(example_dir, a)
            m = get_metadata_dict(path)
            d = file_dict(path, m, "audio")
            _audio_list.append(d)
            _audio_list.append(d)

        for v in ("fake.mp4", "fake.webm", "real.mp4", "real.webm"):
            path = os.path.join(example_dir, v)
            m = get_metadata_dict(path)
            d = file_dict(path, m, "video")
            _video_list.append(d)
            _video_list.append(d)

    if _audio_list:
        audio_list = make_unique_slugs(_audio_list)
        single_file_e = audio_list[0]["escaped_path"]

    if _video_list:
        video_list = make_unique_slugs(_video_list)

    c = request_context(app.fidiConfig)
    c.update(
        {
            "page_name": "Javascript Tests Page!",
            "item_list": audio_list,
            "video_list": video_list,
            "single_file_e": single_file_e,
        }
    )
    return render_template("test_js.html", **c)
