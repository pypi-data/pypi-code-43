import sys
import typing
from . import translations
from . import handlers

alembic = None
'''constant value bpy.app.alembic(supported=True, version=(1, 6, 0), version_string= 1, 6, 0) '''

background = None
'''Boolean, True when blender is running without a user interface (started with -b) '''

binary_path = None
'''The location of blenders executable, useful for utilities that spawn new instances '''

build_branch = None
'''The branch this blender instance was built from '''

build_cflags = None
'''C compiler flags '''

build_commit_date = None
'''The date of commit this blender instance was built '''

build_commit_time = None
'''The time of commit this blender instance was built '''

build_commit_timestamp = None
'''The unix timestamp of commit this blender instance was built '''

build_cxxflags = None
'''C++ compiler flags '''

build_date = None
'''The date this blender instance was built '''

build_hash = None
'''The commit hash this blender instance was built with '''

build_linkflags = None
'''Binary linking flags '''

build_options = None
'''constant value bpy.app.build_options(bullet=True, codec_avi=True, codec_ffmpeg=True, codec_quicktime=False, codec_sndfile=False, compositor=True, cycles=True, cycles_osl=True, freestyle=True, gameengine=True, image_cineon=True, image_dds=True, image_frameserver=True, image_hdr=True, image_openexr=True, image_openjpeg=True, image_tiff=True, input_ndof=True, audaspace=True, international=True, openal=True, sdl=True, sdl_dynload=True, jack=True, libmv=True, mod_boolean=True, mod_fluid=True, mod_oceansim=True, …) '''

build_platform = None
'''The platform this blender instance was built for '''

build_system = None
'''Build system used '''

build_time = None
'''The time this blender instance was built '''

build_type = None
'''The type of build (Release, Debug) '''

ffmpeg = None
'''constant value bpy.app.ffmpeg(supported=True, avcodec_version=(56, 60, 100), avcodec_version_string=‘56, 60, 100, avdevice_version=(56, 4, 100), avdevice_version_string=‘56, 4, 100, avformat_version=(56, 40, 101), avformat_version_string=‘56, 40, 101, avutil_version=(54, 31, 100), avutil_version_string=‘54, 31, 100, swscale_version=(3, 1, 101), swscale_version_string= 3, 1, 101) '''

handlers = None
'''constant value bpy.app.handlers(frame_change_pre=[], frame_change_post=[], render_pre=[], render_post=[], render_write=[], render_stats=[], render_init=[], render_complete=[], render_cancel=[], load_pre=[], load_post=[], save_pre=[], save_post=[], scene_update_pre=[], scene_update_post=[], game_pre=[], game_post=[], version_update=[<function do_versions at 0x7f19320a9d08>], persistent=<class ‘persistent>) '''

ocio = None
'''constant value bpy.app.ocio(supported=True, version=(1, 0, 9), version_string= 1, 0, 9) '''

oiio = None
'''constant value bpy.app.oiio(supported=True, version=(1, 6, 9), version_string= 1, 6, 9) '''

openvdb = None
'''constant value bpy.app.openvdb(supported=True, version=(3, 1, 0), version_string= 3, 1, 0) '''

sdl = None
'''constant value bpy.app.sdl(supported=True, version=(2, 0, 8), version_string=‘2.0.8, available=True) '''

translations = None
'''Application and addons internationalization API '''

version = None
'''The Blender version as a tuple of 3 numbers. eg. (2, 50, 11) '''

version_char = None
'''The Blender version character (for minor releases) '''

version_cycle = None
'''The release status of this build alpha/beta/rc/release '''

version_string = None
'''The Blender version formatted as a string '''
