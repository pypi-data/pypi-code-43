# cbcreator.py - main routines to render a class band slide
#
# Copyright 2018 Zhang Maiyun
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

from sys import argv, exit, stdin, stdout, stderr
from argparse import ArgumentParser
from random import randint
from pathlib import Path
from io import IOBase
from PIL import Image, ImageDraw, ImageFont, ImageFile
import pkg_resources as pr

__all__ = ['BandSlide', 'autowrap', 'avgcolor',
           'compcolor', 'eprint', 'getrc', 'start']


def ispath(s):
    return isinstance(s, (bytes, str, Path))


def openimage(f):
    if ispath(f):
        return Image.open(f)
    elif isinstance(f, ImageFile.ImageFile):
        return f
    elif isinstance(f, IOBase):
        return Image.open(f.name)
    else:
        raise TypeError(f"Unknown type {f.__class__} for f")


def getrc(rcname):
    """Get a program resource placed in cbcreator/resources.

    rcnane: The filename
    returns the full path to the file.
    """
    resource = pr.resource_filename(__name__, "resources/" + rcname)
    return resource


def avgcolor(imageobj):
    """Get the average color of the PIL.Image object.

    imageobj: the image
    returns a RGB tuple.
    """
    r = 0
    g = 0
    b = 0
    totalcount = 0
    colors = 256
    arr = None
    while True:
        arr = imageobj.getcolors(colors)
        if arr is None:
            colors *= 2
        else:
            break
    for tup in arr:
        r += tup[0] * tup[1][0]
        g += tup[0] * tup[1][1]
        b += tup[0] * tup[1][2]
        totalcount += tup[0]
    r //= totalcount
    g //= totalcount
    b //= totalcount
    return (r, g, b)


def compcolor(color):
    """Compute the complementary color of the given color.

    color: the color to be computed
    returns a RGB tuple.
    """
    return (255 - color[0], 255 - color[1], 255 - color[2])


def autowrap(text, width, draw, font):
    """ Word-wrap text to a fixed width
    text: the text to be wrapped
    width: the width of every line
    draw: pillow ImageDraw object
    font: the pillow ImageFont object to be used
    returns the wrapped text.
    """
    if not text:
        return ""
    lines = text.split('\n')
    if ''.join(lines) != text:
        # Already contains LFs
        wrapped = ""
        for line in lines:
            wrapped += autowrap(line, width, draw, font)
            wrapped += '\n'
        return wrapped
    initsz = draw.textsize(text, font=font)[0]
    txtlen = len(text)
    if txtlen == 0:
        return ""
    # shouldn't split a character into two
    wraploc = initsz / width  # lines the text should be
    wraploc = round(txtlen / wraploc)  # lenth of every line
    # leave some spare space for the round-off
    wraploc -= 1
    resultstr = ""
    for idx in range(0, txtlen):
        # insert a LF whenever the wraploc-th char is met
        if idx % wraploc == 0 and idx != 0:
            resultstr += '\n'
        resultstr += text[idx]
    return resultstr


class BandSlide(object):
    """Class wrapper of a class band slide."""

    def __init__(self, bgfile):
        """Create a class band slide object.

        bgfile: image path of the background
        """
        self.im = openimage(bgfile).resize((2661, 3072))
        self.title = None
        self.text = None
        self.pics = []
        self.titlefont = None
        self.titlesize = 600
        self.titlecolor = compcolor(avgcolor(self.im))
        self.textfont = None
        self.textsize = 100
        self.textcolor = compcolor(avgcolor(self.im))

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        """Close all images."""
        try:
            self.im.close()
            self.im = None
            for pic in self.pics:
                pic.close()
        except Exception:
            pass

    def addtitle(self, title):
        """Add a title to the slide."""
        self.title = title

    def addtext(self, textfile):
        """Add text to the slide."""
        if ispath(textfile):
            self.text = open(textfile).read()
        elif textfile is not None:
            self.text = textfile.read()
        else:
            pass  # None, nothing added

    def addpic(self, pics):
        """Add picture to the slide.

        pics: str, bytes or os.PathLike object, file object or their tuple or list
        """
        for pic in pics:
            if pic:  # Not empty or None
                self.pics.append(openimage(pic))

    def set_title_attrib(self, **kwargs):
        """Set attributes of the title.

        kwargs: attributes
            possible keys:
                font: full path of the font file
                color: color specified in RGB tuple
                size: font size in pixels
            Note that you should always specify size before font.
        """
        for attrib in kwargs:
            if attrib == "font":
                self.titlefont = ImageFont.truetype(
                    kwargs[attrib],
                    self.titlesize,
                    encoding="unic")
            elif attrib == "color":
                self.titlecolor = kwargs[attrib]
            elif attrib == "size":
                self.titlesize = int(kwargs[attrib])
            else:
                raise ValueError(f"Unexpected key {attrib}")

    def set_text_attrib(self, **kwargs):
        """Set attributes of the text.

        kwargs: attributes
            possible keys:
                font: full path of the font file
                color: color specified in RGB tuple
                size: font size in pixels
            Note that you should always specify size before font.
        """
        for attrib in kwargs:
            if attrib == "font":
                self.textfont = ImageFont.truetype(
                    kwargs[attrib],
                    self.textsize,
                    encoding="unic")
            elif attrib == "color":
                self.textcolor = kwargs[attrib]
            elif attrib == "size":
                self.textsize = int(kwargs[attrib])
            else:
                raise ValueError(f"Unexpected key {attrib}")

    def save(self, output):
        if self.titlefont is None:
            fontfile = "fonts/{:03}.ttf".format(randint(1, 4))
            fontfile = getrc(fontfile)
            self.titlefont = ImageFont.truetype(
                fontfile, self.titlesize, encoding="unic")
        """ Save the slide to a file. """
        if self.textfont is None:
            fontfile = "fonts/{:03}.ttf".format(randint(1, 4))
            fontfile = getrc(fontfile)
            self.textfont = ImageFont.truetype(
                fontfile, self.textsize, encoding="unic")
        # Only create the ImageDraw object if we aren't just resizing
        if self.title or self.text or self.pics:
            draw = ImageDraw.Draw(self.im)
            if not self.title:
                self.title = ""
            # size tuple of the title
            sizet = draw.textsize(self.title, font=self.titlefont)
            onechar = draw.textsize("a", font=self.textfont)[0]
            # don't ask what the 3 is, it just works
            self.text = autowrap(self.text, 2661 - 3 *
                                 onechar, draw, self.textfont)
            sizex = draw.textsize(self.text, font=self.textfont)
            leftt = (2661 - sizet[0]) // 2
            # Set margin to the width of a character
            leftx = (2661 - sizex[0]) // 2
            top = (3072 - sizet[1] - sizex[1] - onechar) // 2
            draw.text((leftt, top), self.title,
                      font=self.titlefont, fill=self.titlecolor)
            draw.text((leftx, top + sizet[1] + onechar),
                      self.text, font=self.textfont, fill=self.textcolor)
            # # TODO: Render the slide to self.im
            # # Use https://pillow.readthedocs.io/en/stable/reference/
            # # Image.html?highlight=overlay#PIL.Image.Image.alpha_composite
        self.im.save(output)


def eprint(*args, **kwargs):
    print(*args, file=stderr, **kwargs)


def parsecmd():
    parser = ArgumentParser(description="Automatically generate class bands.")
    parser.add_argument(
        "background", help="The background image, `-' for stdin")
    parser.add_argument("output", help="The output filename, `-' for stdout")
    parser.add_argument('--title', '-t', help="The title string")
    parser.add_argument(
        '--text', '-x', help="The filename of the text to insert, left blank for a title slide")
    parser.add_argument('--overlay', '-a', action="append",
                        help="Pictures to lay on the slide", default=[])
    args = parser.parse_args()

    if Path(args.output).exists():
        _ = input("The output file already exists, overwrite? [y/N] ")
        if _.lower() != "y":
            exit(1)

    # Read from stdin/write to stdout
    if args.background == "-":
        args.background = stdin
    if args.output == "-":
        args.output = stdout
    with BandSlide(args.background) as slide:
        slide.addtitle(args.title)
        slide.addtext(args.text)
        slide.addpic(args.overlay)
        slide.save(args.output)


def interactive():
    overlay = []
    while True:
        bgfile = input("The file to be used as the background: ")
        if bgfile:
            break
        eprint("Don't left this field blank!")
    title = input("The title for the page: ")
    textfile = input("The text file to use: ")
    while True:
        outputfile = input("Where to output: ")
        if outputfile:
            if Path(outputfile).exists():
                _ = input("The output file already exists, overwrite? [y/N] ")
                if _.lower() == "y":
                    break
                else:
                    continue
            else:
                break
        eprint("Don't left this field blank!")
    while True:
        currentin = input("Pictures to lay on(left blank to stop): ")
        if currentin:
            overlay.append(currentin)
        else:
            break
    with BandSlide(bgfile) as slide:
        slide.addtitle(title)
        if textfile:
            slide.addtext(textfile)
        slide.addpic(overlay)
        slide.save(outputfile)


def start():
    try:
        _ = argv[1]
    except IndexError:
        # No command line provided
        exit(interactive())
    parsecmd()


if __name__ == "__main__":
    start()
