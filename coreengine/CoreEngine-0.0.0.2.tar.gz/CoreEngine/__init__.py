import os

# todo license

__author__ = "CoreTaxxe"
__version__ = "0.0.0.dev1"

animationSyntax = "{\n'IDLE':{\n   'FRAMES':[bilda.png,bildb.png], \n   'TICKS':1\n   },\n'RUNNING':{\n   'FRAMES':[bilda.png,bildb.png], \n   'TICKS':2\n   }\n}"

# imports
from CoreEngine import *
from CoreEngine.maphandler import Buffered2DMapHandler  # import MapHandler
from CoreEngine.dataadapter import DataAdapter, TiledMap  # import DataAdapter
from CoreEngine.physics2D import PhysicsBody2D
from CoreEngine.scenecontroller import SceneController
from CoreEngine.scenes import Scene
from CoreEngine.utility import *
from CoreEngine.spritesheetcreator import SpriteSheetCreator
from CoreEngine.entity import Entity, SimpleEntity, ComplexEntity
from CoreEngine.staticobject import StaticObject, SimpleStaticObject, ComplexStaticObject
from CoreEngine.musicplayer import MusicPlayer
from CoreEngine.fontobjects import Label, Button, TextInputBox
from CoreEngine.loadingscreen import LoadingScreen
from CoreEngine.particles import Particle
# template

if "COREENGINE_HIDE_SUPPORT_PROMPT" not in os.environ:
    print("CoreEngine %s" % __version__)
    print("Thanks for using CoreEngine!")
    print("This prompt can get disabled - read docs for further information")

del pygame, os
