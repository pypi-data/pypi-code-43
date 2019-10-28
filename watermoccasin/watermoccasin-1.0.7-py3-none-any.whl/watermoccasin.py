import npr, argparse, logging, urllib, os, tempfile, subprocess
from shutil import copyfile
from pydub import AudioSegment
from humanfriendly import format_timespan
from requests import get
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.aac import AAC

def main():
    root_name = '_wm_npr_one_'
    parser = argparse.ArgumentParser(description='NPR One gathering app for offline use.', epilog='more info/coffee tip at github/watermoccasin')
    parser.add_argument('media', default='D:\\',
                        help='path to store media')
    parser.add_argument('-w', '--workout',
                        nargs='?', default=60, type=int,
                        help='length of workout in minutes')
    parser.add_argument('-s', '--speedup',
                        nargs='?', const=2.0, type=float,
                        help='speed up playback by factor (Default is 200%)')
    parser.add_argument("-l", "--log", dest="logLevel", 
                        nargs='?', const='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help="Set the logging level")
    parser.add_argument('-v', '--verbose',
                        help="increase output verbosity", action="store_true")

    args = parser.parse_args()

    dir = args.media
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    elif args.logLevel:
        logging.basicConfig(filename=os.path.join(dir, 'water_moccasin.log'),level=args.logLevel)

    # check media path ok first
    if (not os.access(dir, os.W_OK)):
        logging.warning('Media {0} not available.'.format(dir))
        exit()

    workout_length = args.workout * 60
    logging.info('workout length (in seconds): {0}'.format(workout_length))

    # clean up old media
    files = os.listdir(dir)
    for file in files:
        if root_name in file and file.endswith(".mp3"):
            os.remove(os.path.join(dir,file))

    time_length = track_count = 0
    npr.login()
    player = npr.One()
    while time_length < workout_length:
        track_count += 1

        path = urllib.parse.urlparse(player.audio).path
        name = os.path.splitext(os.path.basename(path))[0] + '.mp3'
        ext = os.path.splitext(path)[1]
        
        response = get(player.audio)
        fn = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
        fn.close()
        fn = fn.name

        file = tempfile.NamedTemporaryFile(delete=False, suffix=ext, mode='w+b')
        fn_orig = file.name
        logging.debug(fn_orig)
        file.write(response.content)
        file.close()

        speedup_cmd = ''
        if args.speedup: 
            speedup_cmd = ' -filter:a "atempo={0}" '.format(args.speedup)

        conversion_command = 'ffmpeg -y -i {0} {1} -vn {2}'.format(fn_orig, speedup_cmd, fn)

        logging.info(conversion_command)
        with open(os.devnull, 'rb') as devnull:
            p = subprocess.Popen(conversion_command, stdin=devnull, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p_out, p_err = p.communicate()

        logging.debug(p_out, time_length)

        sound = AudioSegment.from_file(fn).export(os.path.join(dir, '{0:02}{1}{2}'.format(track_count, root_name, name)), format="mp3")
        player.skip()

        if ext=='.mp3':
            audio = MP3(fn)
        elif ext == '.mp4':
            audio = MP4(fn)
        elif ext == '.aac':
            audio = AAC(fn)
        else:
            logging.warning('{0} format not found!'.format(ext))

        del fn_orig, fn

        time_length += audio.info.length
    print('Completed: {0} files for {1}.'.format(track_count, format_timespan(time_length)))