import os
import sys
import subprocess as sp
from videogrep import videogrep
from moviepy.tools import subprocess_call
from moviepy.config import get_setting
import subprocess


def ffmpeg_extract_subclip(filename, t1, t2, targetname=None):
    """ makes a new video file playing video file ``filename`` between
        the times ``t1`` and ``t2``. """
    name, ext = os.path.splitext(filename)
    if not targetname:
        T1, T2 = [int(1000 * t) for t in [t1, t2]]
        targetname = name + "%sSUB%d_%d.%s"(name, T1, T2, ext)

    cmd = [get_setting("FFMPEG_BINARY"), "-y",
           "-i", filename,
           "-ss", "%0.2f" % t1,
           "-t", "%0.2f" % (t2 - t1),
           "-vcodec", "copy", "-acodec", "copy", targetname]

    subprocess_call(cmd)


def ffmpeg_extract_audio(inputfile, output, bitrate=3000, fps=44100):
    """ extract the sound from a video file and save it in ``output`` """
    cmd = [get_setting("FFMPEG_BINARY"), "-y", "-i", inputfile, "-ab", "%dk" % bitrate,
           "-ar", "%d" % fps, output]
    subprocess_call(cmd)

def ffmpeg_extract_audio2(inputfile, output):
    """ extract the sound from a video file and save it in ``output`` """
    print(inputfile, output)
    inputfile = inputfile.replace(" ", "\ ")
    output = output.replace(" ", "\ ")
    cmd = f"ffmpeg -i {inputfile} -ab 160k -ac 2 -ar 11025 -vn {output}"
    # subprocess_call(cmd)
    subprocess.call(cmd, shell=True)


if __name__ == "__main__":
    pass
    # print("Running")
    # ferris_file_path_in = "feris_test.flv"
    # ferris_file_path_out = "feris_test.wav"
    # ffmpeg_extract_audio2(ferris_file_path_in, ferris_file_path_out)

    # subprocess.call(command, shell=True)
    # ffmpeg_extract_audio(ferris_file_path_in, ferris_file_path_out)
