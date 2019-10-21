from easilyb.commands import run_command_ex1
import logging
logger = logging.getLogger(__name__)


def identify(filepath):
    try:
        return_code, output = run_command_ex1(["identify", filepath])
        if return_code != 0:
            raise Exception("Non-Zero return code: %d" % return_code)
        output = output.decode(errors="replace")
        splits = output.split()
        return splits[1:4]
    except:
        logging.error("Error while running and parsing identify command for file: %s", filepath, exc_info=True)


def crop(input_filepath, output_filepath, position):
    try:
        return_code, output = run_command_ex1(["convert", input_filepath, "-crop", position, output_filepath])
        if return_code != 0:
            raise Exception("Non-Zero return code: %d" % return_code)
    except:
        logging.error("Error while running crop command for (input_filepath=%s, output_filepath=%s, position=%s)",
                      input_filepath, output_filepath, position, exc_info=True)