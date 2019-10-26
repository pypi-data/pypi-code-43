"""Entry point of CLI"""

# Built-in
import argparse
import os
import pathlib
import random
import re


parser = argparse.ArgumentParser(
    prog='spokennumbers',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=(
        'Generate spoken numbers audio files.\n\n'
        'If no options are provided, a random 100-digit mp3 file '
        'will be created.\nA text file will also be created next to the '
        'mp3 file contaning the raw\nnumbers (used for recall).'),
    epilog=(
        'Example:\n'
        '    $ spokennumbers -n 150 --speed 1.2 -o monday_training.mp3'))
parser.add_argument('-n', '--numbers', default='100', help=(
    'The number of random digits to generate. Defaults to 100. '
    'If a text file is specified, all digits it contains will be used '
    'instead (parsed by regexp).'))
parser.add_argument('-p', '--init-silence', type=int, default=3, help=(
    'Add some seconds of silence in the beginning of the audio file. '
    'Defaults to 3 seconds.'))
parser.add_argument('-c', '--skip-countdown', action='store_true', help=(
    'By default, a countdown sequence will be spoken at start: "3 ... '
    '2 ... 1 ... a ... b ... c ... ...". This option skips the countdown.'))
parser.add_argument('-s', '--speed', type=float, default=1, help=(
    'The pace at which numbers will be spoken in seconds. Defaults to one '
    'digit per second.'))
parser.add_argument('-d', '--source', default='default', help=(
    'Audio files source. The string "default" will use the default '
    'audio files included in the Python package. For custom audio '
    'files, you can specify the path to a directory as source. The '
    'directory must contain the required audio wav files: 0.wav ... '
    '9.wav and a.wav, b.wav and c.wav.'))
parser.add_argument('-e', '--exclude', default='', help=(
    'This option is used to exclude specified digits from the output. '
    'For example, if `--exclude 789` is used, the digits 7, 8 and 9 '
    'will not be present in the output file.'))
parser.add_argument('-o', '--output-file', default='spoken.mp3', help=(
    'Name of output file. Defaults to `spoken.mp3`.'))
parser.add_argument('-i', '--skip-txt-file', action='store_true', help=(
    'Do not create the txt file containing the spoken numbers next to the '
    'audio file. The txt file is used for recall.'))

def main():
    args = parser.parse_args()

    # Figure out the list of numbers to be spoken
    if os.path.isfile(args.numbers):
        with open(args.numbers, 'r') as file:
            digits = re.findall(r'\d', file.read(), re.MULTILINE)
        digits = [int(d) for d in digits if d not in args.exclude]
    else:
        nr_digits = int(args.numbers)
        digits = list()
        candidates = list(set('0123456789') - set(args.exclude))
        for _ in range(nr_digits):
            digits.append(int(random.choice(candidates)))

    # Put the import after `parse_args` so import errors don't prevent the
    # CLI from being used.
    import spokennumbers
    spokennumbers.spoken(
        digits, args.speed, args.init_silence, not args.skip_countdown,
        args.source, args.output_file)

    # Create txt file with answer
    if not args.skip_txt_file:
        output_txt = pathlib.Path(args.output_file).with_suffix('.txt')
        with open(output_txt, 'w') as file:
            for i, d in enumerate(digits, start=1):
                file.write(str(d))
                if i % 10 == 0:
                    file.write('\n')

if __name__ == '__main__':
    main()
