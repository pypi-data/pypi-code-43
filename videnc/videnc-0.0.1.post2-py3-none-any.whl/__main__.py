import argparse
import os

from python_find.tree_search import TreeSearch

from .video import Video

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='videnc',
        description='A python script for video processing and information.')

    # TODO use nargs='*' to take multiple paths
    parser.add_argument('path',
        help='path to video or directory containing video files')
    parser.add_argument('-o', '--output-path', default='~/videnc',
        help='directory to place output file(s)')
    parser.add_argument('-c', '--compress', type=bool, default=True,
        help='enable video compression to output directory')
    parser.add_argument('-d', '--delete-source', type=bool, default=False,
        help='delete source files after successful encode')
    parser.add_argument('-q', '--quality', type=int, default=25,
        choices=range(52),
        help='quality of output video, see FFmpeg x265 CRF for more')
    parser.add_argument('-p', '--preset', default='medium',
        choices=['ultrafast', 'superfast', 'veryfast', 'faster', 'fast',
            'medium', 'slow', 'slower', 'veryslow'],
        help='used to achieve certain encoding speed to compression ratio.')
    parser.add_argument('-a', '--audio-streams', default=None,
        help='comma separated list of audio streams to select for output')

    args = parser.parse_args()

    try:
        input_path = os.path.expanduser(args.path)
        output_path = os.path.expanduser(args.output_path)
        selected_audio_streams = args.audio_streams

        if selected_audio_streams:
            selected_audio_streams = selected_audio_streams.split(',')

        if not os.path.isdir(output_path):
            os.mkdir(output_path)

        if os.path.isdir(input_path):
            search = TreeSearch(root=input_path, name='*.mkv')
            for video in search.generate_found_files():
                path_basename = os.path.basename(video)
                video_output_path = os.path.join(output_path, path_basename)
                v = Video(path=video, output_path=video_output_path,
                    audio_streams=selected_audio_streams,
                    compress=args.compress, preset=args.preset,
                    quality=args.quality)

                if args.delete_source:
                    os.remove(video)

        else:
            path_basename = os.path.basename(input_path)
            video_output_path = os.path.join(output_path, path_basename)
            v = Video(path=input_path, output_path=video_output_path,
                    audio_streams=selected_audio_streams,
                    compress=args.compress, preset=args.preset,
                    quality=args.quality)

            if args.delete_source:
                os.remove(input_path)

    except KeyboardInterrupt:
        if os.path.exists(output_path):
            os.remove(output_path)

