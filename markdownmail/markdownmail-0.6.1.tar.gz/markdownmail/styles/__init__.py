"""Css styles provided by markdownmail

- 'simple style' was the default style in v.0.2
- 'default style' comes from MarkdownHere, a plugin for browser and Thunderbird, under MIT licence
   (https://raw.githubusercontent.com/adam-p/markdown-here/master/src/common/default.css)
"""

import os
import os.path


_DEFAULT_STYLE_PATH = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__), "default.css")
)

with open(_DEFAULT_STYLE_PATH) as f:
    DEFAULT_STYLE = f.read()


SIMPLE_STYLE = """
body {
    font-family: Helvetica, Arial, sans-serif;
    text-align: left;
    background-color: #ebebeb;
    padding-top: 15px;
    padding-bottom: 15px;
}

pre, code {
  font-family: Consolas, Inconsolata, Courier, monospace;
}

#content {
    background-color: #ffffff;
    max-width: 650px;
    margin-left: auto;
    margin-right: auto;
    padding-left: 10px;
}

@media only screen and (max-width:650px) {
#content {
    width: 100%;
}
"""
