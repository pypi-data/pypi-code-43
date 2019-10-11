import os
import platform


def goto_origin(origin_path):
    """Moves current directory back to where it was when the command
    was called."""
    os.chdir(origin_path)


def goto_music():
    """Moves current directory to the user's music folder."""
    if platform.system() == 'Windows':
        download_path = 'Music\\Instrumentals'
    else:
        download_path = 'Music/Instrumentals'
    os.chdir(os.path.join(os.path.expanduser('~'), download_path))


def goto_program():
    """Moves current directory to the instrumental_dl folder."""
    os.chdir(
        os.path.dirname(
            os.path.dirname(
                os.path.realpath(__file__))))
