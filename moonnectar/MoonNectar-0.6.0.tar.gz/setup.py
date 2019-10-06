import pathlib
import setuptools
import distutils
import os
import subprocess
import re

import setup_qt

entry_points = [
    "Registry                                                            = mnectar.registry:Registry",
    "Registry.Backend                                                    = mnectar.registry:Backend",
    "Registry.Backend.BackendMock                                        = mnectar.backend.mock:BackendMock",
    "Registry.Backend.BackendVLC                                         = mnectar.backend.vlc:BackendVLC",
    "Registry.Control                                                    = mnectar.registry:Control",
    "Registry.Control.AlbumSkip                                          = mnectar.plugins.album_skip:AlbumSkip",
    "Registry.Control.MacMMKeyPlugin                                     = mnectar.backend.macos_key:MacMMKeyPlugin",
    "Registry.Control.MacOSNoSleep                                       = mnectar.plugins.macos.macos_nosleep:MacOSNoSleep",
    "Registry.Control.OrderAgents                                        = mnectar.backend.order:OrderAgents",
    "Registry.Control.OrderAgents.Linear                                 = mnectar.backend.order:Linear",
    "Registry.Control.OrderAgents.Random                                 = mnectar.backend.order:Random",
    "Registry.Control.OrderAgents.RandomAlbum                            = mnectar.backend.order:RandomAlbum",
    "Registry.Control.OrderAgents.RandomArtist                           = mnectar.backend.order:RandomArtist",
    "Registry.Control.OrderManager                                       = mnectar.backend.order:OrderManager",
    "Registry.Library                                                    = mnectar.library.registry:Library",
    "Registry.Library.Columns                                            = mnectar.library.registry:Columns",
    "Registry.Library.Columns.BaseColumns                                = mnectar.library.registry:BaseColumns",
    "Registry.Library.Columns.HashtagColumn                              = mnectar.plugins.hashtag.column:HashtagColumn",
    "Registry.Library.Extensions                                         = mnectar.library.registry:Extensions",
    "Registry.Library.Extensions.LibraryWatchdog                         = mnectar.plugins.library.LibraryWatchdog:LibraryWatchdog",
    "Registry.Library.SearchEngine                                       = mnectar.library.registry:SearchEngine",
    "Registry.Library.SearchEngine.LarkSearchEngine                      = mnectar.library.LarkSearchEngine:LarkSearchEngine",
    "Registry.Library.SearchEngine.LogicEngineGrammar                    = mnectar.plugins.logic:LogicEngineGrammar",
    "Registry.Library.SearchEngine.LogicEngineGrammar.AutoColumnGrammar  = mnectar.plugins.logic:AutoColumnGrammar",
    "Registry.Library.SearchEngine.LogicEngineGrammar.BaseGrammar        = mnectar.plugins.logic:BaseGrammar",
    "Registry.Library.SearchEngine.LogicEngineGrammar.ColumnGrammar      = mnectar.plugins.logic:ColumnGrammar",
    "Registry.Library.SearchEngine.LogicEngineGrammar.HashtagLogicSearch = mnectar.plugins.hashtag.hashtag:HashtagLogicSearch",
    "Registry.Library.SearchEngine.LogicEngineGrammar.LogicGrammar       = mnectar.plugins.logic:LogicGrammar",
    "Registry.Library.SearchEngine.LogicEngineGrammar.TimeSearch         = mnectar.plugins.logic:TimeSearch",
    "Registry.Library.SearchEngine.LogicSearchEngine                     = mnectar.plugins.logic:LogicSearchEngine",
    "Registry.Playlist                                                   = mnectar.registry:Playlist",
    "Registry.Playlist.Changed                                           = mnectar.library.view:Changed",
    "Registry.Playlist.Editable                                          = mnectar.library.view:Editable",
    "Registry.Playlist.Filtered                                          = mnectar.library.view:Filtered",
    "Registry.Playlist.Grouped                                           = mnectar.library.view:Grouped",
    "Registry.Playlist.RandomGroup                                       = mnectar.library.view:RandomGroup",
    "Registry.Playlist.Randomized                                        = mnectar.library.view:Randomized",
    "Registry.Playlist.Selected                                          = mnectar.library.view:Selected",
    "Registry.Playlist.Shifted                                           = mnectar.library.view:Shifted",
    "Registry.Playlist.Sorted                                            = mnectar.library.view:Sorted",
    "Registry.Playlist.View                                              = mnectar.library.view:View",
    "Registry.Plugin                                                     = mnectar.registry:Plugin",
    "Registry.Storage                                                    = mnectar.registry:Storage",
    "Registry.UI                                                         = mnectar.ui.manager:UI",
    "Registry.UI.GuiPyQt                                                 = mnectar.ui.pyqt5.uipyqt5:GuiPyQt",
    "Registry.UI.PyQt                                                    = mnectar.ui.pyqt5.__init__:PyQt",
    "Registry.UI.PyQt.Browsers                                           = mnectar.ui.pyqt5.__init__:Browsers",
    "Registry.UI.PyQt.Browsers.DefaultBrowser                            = mnectar.ui.pyqt5.browser:DefaultBrowser",
    "Registry.UI.PyQt.Docked                                             = mnectar.ui.pyqt5.__init__:Docked",
    "Registry.UI.PyQt.Docked.HashtagManager                              = mnectar.plugins.hashtag.manager:HashtagManager",
    "Registry.UI.PyQt.Docked.PyConsole                                   = mnectar.plugins.ui.pyqt5.console:PyConsole",
    "Registry.UI.PyQt.Docked.Queue                                       = mnectar.plugins.ui.pyqt5.queue:Queue",
    "Registry.UI.PyQt.Menu                                               = mnectar.ui.pyqt5.__init__:Menu",
    "Registry.UI.PyQt.Menu.OrderMenu                                     = mnectar.plugins.ui.pyqt5.order:OrderMenu",
    "Registry.UI.UiPlugin                                                = mnectar.ui.manager:UiPlugin",
]

# Get the app version
# ... By switching to the package directory, the version file becomes a local import
# ... This avoids problems with missing dependencies
appvars = {}
with open("mnectar/vars.py") as fp:
    exec(fp.read(), appvars)


module_packages = setuptools.find_packages()

setuptools.setup(
    name                 = appvars['__appname__'],
    packages             = module_packages,
    version              = appvars['__version__'],
    license              = "MIT License",
    description          = "Moon Nectar Media Player",
    author               = "David Morris",
    author_email         = "othalan@othalan.net",
    url                  = "https://gitlab.com/othalan/moon-nectar",
    include_package_data = True,
    zip_safe             = False,
    python_requires      = '>=3.7',
    entry_points         = {
        "gui_scripts": [
            f"{appvars['__appname__']} = mnectar.appinit:run_app",
        ],
        "mnectar.plugins": entry_points,
    },
    cmdclass    = {"build": setup_qt.build, "build_qt": setup_qt.BuildPyQt},
    options     = {"build_qt": {"packages": module_packages}},
    classifiers = [
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Topic :: Multimedia :: Sound/Audio :: Players",
    ],
    install_requires = [
        "ConfigArgParse",
        "lark-parser",
        "mutagen",
        "pkginfo",
        "PluginRegistry>=0.3.0",
        "python-vlc",
        "setuptools",
        "tinydb>=3.14.0",
        "watchdog",
    ],
    extras_require = {
        "test": [
            "coveralls",
            "pytest",
            "pytest-clarity",
            "pytest-cov",
            "pytest-mock",
            "pytest-qt",
            "pytest-sugar",
        ],
        "gui": ["pyqt5>=5.13.1"],
        "console": ["pyqtconsole"],
        "mmkey": ["pyobjc; sys_platform == 'darwin'"],
    },
)
