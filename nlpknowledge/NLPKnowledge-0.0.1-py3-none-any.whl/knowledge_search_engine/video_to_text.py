import logging
import mimetypes
import os
import time

from audio_from_video import ffmpeg_extract_audio
from speach_recogn import extract_text

logger = logging.getLogger("__name__")

workdir = "/Users/maistrovas/Documents/My Life/Education"
videos_dir = "test_videos_dir"
supported_formats = ["video/x-flv", "video/mp4"]
video_format_prefixes_map = {"video/x-flv": ".flv", "video/mp4": ".mp4"}


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts))
        else:
            print("%r  %s sec" % (method.__name__, (te - ts)))
        return result

    return timed


def video_to_text(currdir=f"{workdir}/{videos_dir}"):
    for file in os.listdir(currdir):
        # Do not process dir in case there is .srt inside this dir. They also can be used in search
        path = os.path.join(currdir, file)
        if not os.path.isdir(path):
            print(mimetypes.guess_type(file))
            contenttype, *_ = mimetypes.guess_type(file)
            if contenttype in supported_formats:
                audio_filepath = path.replace(video_format_prefixes_map[contenttype], '.wav')
                text_filepath = path.replace(video_format_prefixes_map[contenttype], '.txt')
                file_was_not_generated_before = not os.path.isfile(text_filepath)
                if file_was_not_generated_before:
                    print(f"Generating new file,  {audio_filepath}")
                    ffmpeg_extract_audio(path, audio_filepath)
                    print("Audio ready")
                    extract_text(audio_filepath, text_filepath)
                    print("Text ready")
                    os.remove(audio_filepath)
                    print("Audio file cleaned")

        else:
            video_to_text(currdir=path)


def do_nlp(currdir=f"{workdir}/{videos_dir}"):
    pass

# video_to_text()
