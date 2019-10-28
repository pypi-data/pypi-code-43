import subprocess
import sys


def validate_subprocess(get_file_names_command_result: subprocess.CompletedProcess) -> bool:
    """Validate that a subprocess completed successfully or print output and exit"""
    if get_file_names_command_result.returncode != 0:
        print(f"Error while running a command!!!\n"
              f"| Command was: {' '.join(get_file_names_command_result.args)}\n"
              f"| Error was: {get_file_names_command_result.stderr}\n"
              f"| return code is: {get_file_names_command_result.returncode}")

        sys.exit(get_file_names_command_result.returncode)

    return True
