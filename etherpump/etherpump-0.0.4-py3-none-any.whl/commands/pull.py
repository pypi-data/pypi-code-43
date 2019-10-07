"""Check for pads that have changed since last sync (according to .meta.json)"""

import json
import os
import re
import sys
from argparse import ArgumentParser
from datetime import datetime
from fnmatch import fnmatch
from time import sleep
from urllib.parse import quote, urlencode
from urllib.request import HTTPError
from xml.etree import ElementTree as ET

import html5lib

from etherpump.commands.common import *  # noqa
from etherpump.commands.html5tidy import html5tidy


"""
pull(meta):
    Update meta data files for those that have changed.
    Check for changed pads by looking at revisions & comparing to existing
todo...
use/prefer public interfaces ? (export functions)
"""


def try_deleting(files):
    for f in files:
        try:
            os.remove(f)
        except OSError:
            pass


def main(args):
    p = ArgumentParser(
        "Check for pads that have changed since last sync (according to .meta.json)"
    )

    p.add_argument("padid", nargs="*", default=[])
    p.add_argument(
        "--glob", default=False, help="download pads matching a glob pattern"
    )

    p.add_argument(
        "--padinfo",
        default=".etherpump/settings.json",
        help="settings, default: .etherpump/settings.json",
    )
    p.add_argument(
        "--zerorevs",
        default=False,
        action="store_true",
        help="include pads with zero revisions, default: False (i.e. pads with no revisions are skipped)",
    )
    p.add_argument(
        "--pub",
        default="p",
        help="folder to store files for public pads, default: p",
    )
    p.add_argument(
        "--group",
        default="g",
        help="folder to store files for group pads, default: g",
    )
    p.add_argument(
        "--skip",
        default=None,
        type=int,
        help="skip this many items, default: None",
    )
    p.add_argument(
        "--meta",
        default=False,
        action="store_true",
        help="download meta to PADID.meta.json, default: False",
    )
    p.add_argument(
        "--text",
        default=False,
        action="store_true",
        help="download text to PADID.txt, default: False",
    )
    p.add_argument(
        "--html",
        default=False,
        action="store_true",
        help="download html to PADID.html, default: False",
    )
    p.add_argument(
        "--dhtml",
        default=False,
        action="store_true",
        help="download dhtml to PADID.diff.html, default: False",
    )
    p.add_argument(
        "--all",
        default=False,
        action="store_true",
        help="download all files (meta, text, html, dhtml), default: False",
    )
    p.add_argument(
        "--folder",
        default=False,
        action="store_true",
        help="dump files in a folder named PADID (meta, text, html, dhtml), default: False",
    )
    p.add_argument(
        "--output",
        default=False,
        action="store_true",
        help="output changed padids on stdout",
    )
    p.add_argument(
        "--force",
        default=False,
        action="store_true",
        help="reload, even if revisions count matches previous",
    )
    p.add_argument(
        "--no-raw-ext",
        default=False,
        action="store_true",
        help="save plain text as padname with no (additional) extension",
    )
    p.add_argument(
        "--fix-names",
        default=False,
        action="store_true",
        help="normalize padid's (no spaces, special control chars) for use in file names",
    )

    p.add_argument(
        "--filter-ext", default=None, help="filter pads by extension"
    )

    p.add_argument(
        "--css",
        default="/styles.css",
        help="add css url to output pages, default: /styles.css",
    )
    p.add_argument(
        "--script",
        default="/versions.js",
        help="add script url to output pages, default: /versions.js",
    )

    p.add_argument(
        "--nopublish",
        default="__NOPUBLISH__",
        help="no publish magic word, default: __NOPUBLISH__",
    )
    p.add_argument(
        "--publish",
        default="__PUBLISH__",
        help="the publish magic word, default: __PUBLISH__",
    )
    p.add_argument(
        "--publish-opt-in",
        default=False,
        action="store_true",
        help="ensure `--publish` is honoured instead of `--nopublish`",
    )

    args = p.parse_args(args)

    raw_ext = ".raw.txt"
    if args.no_raw_ext:
        raw_ext = ""

    info = loadpadinfo(args.padinfo)
    data = {}
    data['apikey'] = info['apikey']

    if args.padid:
        padids = args.padid
    elif args.glob:
        padids = getjson(
            info['localapiurl'] + 'listAllPads?' + urlencode(data)
        )['data']['padIDs']
        padids = [x for x in padids if fnmatch(x, args.glob)]
    else:
        padids = getjson(
            info['localapiurl'] + 'listAllPads?' + urlencode(data)
        )['data']['padIDs']
    padids.sort()
    numpads = len(padids)
    # maxmsglen = 0
    count = 0
    for i, padid in enumerate(padids):
        if args.skip != None and i < args.skip:
            continue
        progressbar(i, numpads, padid)

        data['padID'] = padid
        p = padpath(padid, args.pub, args.group, args.fix_names)
        if args.folder:
            p = os.path.join(p, padid)

        metapath = p + ".meta.json"
        revisions = None
        tries = 1
        skip = False
        padurlbase = re.sub(r"api/1.2.9/$", "p/", info["apiurl"])
        meta = {}

        while True:
            try:
                if os.path.exists(metapath):
                    with open(metapath) as f:
                        meta.update(json.load(f))
                    revisions = getjson(
                        info['localapiurl']
                        + 'getRevisionsCount?'
                        + urlencode(data)
                    )['data']['revisions']
                    if meta['revisions'] == revisions and not args.force:
                        skip = True
                        break

                meta['padid'] = padid
                versions = meta["versions"] = []
                versions.append(
                    {
                        "url": padurlbase + quote(padid),
                        "type": "pad",
                        "code": 200,
                    }
                )

                if revisions == None:
                    meta['revisions'] = getjson(
                        info['localapiurl']
                        + 'getRevisionsCount?'
                        + urlencode(data)
                    )['data']['revisions']
                else:
                    meta['revisions'] = revisions

                if (meta['revisions'] == 0) and (not args.zerorevs):
                    # print("Skipping zero revs", file=sys.stderr)
                    skip = True
                    break

                # todo: load more metadata!
                meta['group'], meta['pad'] = splitpadname(padid)
                meta['pathbase'] = p
                meta['lastedited_raw'] = int(
                    getjson(
                        info['localapiurl'] + 'getLastEdited?' + urlencode(data)
                    )['data']['lastEdited']
                )
                meta['lastedited_iso'] = datetime.fromtimestamp(
                    int(meta['lastedited_raw']) / 1000
                ).isoformat()
                meta['author_ids'] = getjson(
                    info['localapiurl'] + 'listAuthorsOfPad?' + urlencode(data)
                )['data']['authorIDs']
                break
            except HTTPError as e:
                tries += 1
                if tries > 3:
                    print(
                        "Too many failures ({0}), skipping".format(padid),
                        file=sys.stderr,
                    )
                    skip = True
                    break
                else:
                    sleep(3)
            except TypeError as e:
                print(
                    "Type Error loading pad {0} (phantom pad?), skipping".format(
                        padid
                    ),
                    file=sys.stderr,
                )
                skip = True
                break

        if skip:
            continue

        count += 1

        if args.output:
            print(padid)

        if args.all or (args.meta or args.text or args.html or args.dhtml):
            try:
                os.makedirs(os.path.split(metapath)[0])
            except OSError:
                pass

        if args.all or args.text:
            text = getjson(info['localapiurl'] + 'getText?' + urlencode(data))
            ver = {"type": "text"}
            versions.append(ver)
            ver["code"] = text["_code"]
            if text["_code"] == 200:
                text = text['data']['text']

                ##########################################
                ## ENFORCE __NOPUBLISH__ MAGIC WORD
                ##########################################
                if args.nopublish and args.nopublish in text:
                    # NEED TO PURGE ANY EXISTING DOCS
                    try_deleting(
                        (
                            p + raw_ext,
                            p + ".raw.html",
                            p + ".diff.html",
                            p + ".meta.json",
                        )
                    )
                    continue

                ##########################################
                ## ENFORCE __PUBLISH__ MAGIC WORD
                ##########################################
                if args.publish_opt_in and args.publish not in text:
                    try_deleting(
                        (
                            p + raw_ext,
                            p + ".raw.html",
                            p + ".diff.html",
                            p + ".meta.json",
                        )
                    )
                    continue

                ver["path"] = p + raw_ext
                ver["url"] = quote(ver["path"])
                with open(ver["path"], "w") as f:
                    f.write(text)
                # once the content is settled, compute a hash
                # and link it in the metadata!

        links = []
        if args.css:
            links.append({"href": args.css, "rel": "stylesheet"})
        # todo, make this process reflect which files actually were made
        versionbaseurl = quote(padid)
        links.append(
            {
                "href": versions[0]["url"],
                "rel": "alternate",
                "type": "text/html",
                "title": "Etherpad",
            }
        )
        if args.all or args.text:
            links.append(
                {
                    "href": versionbaseurl + raw_ext,
                    "rel": "alternate",
                    "type": "text/plain",
                    "title": "Plain text",
                }
            )
        if args.all or args.html:
            links.append(
                {
                    "href": versionbaseurl + ".raw.html",
                    "rel": "alternate",
                    "type": "text/html",
                    "title": "HTML",
                }
            )
        if args.all or args.dhtml:
            links.append(
                {
                    "href": versionbaseurl + ".diff.html",
                    "rel": "alternate",
                    "type": "text/html",
                    "title": "HTML with author colors",
                }
            )
        if args.all or args.meta:
            links.append(
                {
                    "href": versionbaseurl + ".meta.json",
                    "rel": "alternate",
                    "type": "application/json",
                    "title": "Meta data",
                }
            )

        # links.append({"href":"/", "rel":"search", "type":"text/html", "title":"Index"})

        if args.all or args.dhtml:
            data['startRev'] = "0"
            html = getjson(
                info['localapiurl'] + 'createDiffHTML?' + urlencode(data)
            )
            ver = {"type": "diffhtml"}
            versions.append(ver)
            ver["code"] = html["_code"]
            if html["_code"] == 200:
                try:
                    html = html['data']['html']
                    ver["path"] = p + ".diff.html"
                    ver["url"] = quote(ver["path"])
                    # doc = html5lib.parse(html, treebuilder="etree", override_encoding="utf-8", namespaceHTMLElements=False)
                    doc = html5lib.parse(
                        html, treebuilder="etree", namespaceHTMLElements=False
                    )
                    html5tidy(
                        doc,
                        indent=True,
                        title=padid,
                        scripts=args.script,
                        links=links,
                    )
                    with open(ver["path"], "w") as f:
                        print(
                            ET.tostring(doc, method="html", encoding="unicode"),
                            file=f,
                        )
                except TypeError:
                    # Malformed / incomplete response, record the message (such as "internal error") in the metadata and write NO file!
                    ver["message"] = html["message"]
                    # with open(ver["path"], "w") as f:
                    #     print ("""<pre>{0}</pre>""".format(json.dumps(html, indent=2)), file=f)

        # Process text, html, dhtml, all options
        if args.all or args.html:
            html = getjson(info['localapiurl'] + 'getHTML?' + urlencode(data))
            ver = {"type": "html"}
            versions.append(ver)
            ver["code"] = html["_code"]
            if html["_code"] == 200:
                html = html['data']['html']
                ver["path"] = p + ".raw.html"
                ver["url"] = quote(ver["path"])
                doc = html5lib.parse(
                    html, treebuilder="etree", namespaceHTMLElements=False
                )
                html5tidy(
                    doc,
                    indent=True,
                    title=padid,
                    scripts=args.script,
                    links=links,
                )
                with open(ver["path"], "w") as f:
                    print(
                        ET.tostring(doc, method="html", encoding="unicode"),
                        file=f,
                    )

        # output meta
        if args.all or args.meta:
            ver = {"type": "meta"}
            versions.append(ver)
            ver["path"] = metapath
            ver["url"] = quote(metapath)
            with open(metapath, "w") as f:
                json.dump(meta, f, indent=2)

    print("\n{0} pad(s) loaded".format(count), file=sys.stderr)
