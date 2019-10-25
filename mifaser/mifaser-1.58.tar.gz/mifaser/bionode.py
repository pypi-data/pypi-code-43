import os
import io
from pathlib import Path
from .command_line import bionode_run, bionode_run_file


# TODO: Change according to the data type of your Node.
# If your input type is a directory, set it to '.'
input_filename = "."
output_filename = "mifaser.out"

# TODO: Specify if your method runs with 'data' or 'filename' inputs.
method_input = 'filename'

# Imports the right method from main respectively:
run_method = bionode_run if method_input == 'data' else bionode_run_file

# # TODO: (Optional) If the method name differs from `bionode_run`, set it like this:
# run_method = your_function_name


def get_jobdirs(input_path):
    for _, dirs, _ in os.walk(input_path):
        dirs[:] = [d for d in dirs if not d[0] == '.']
        return dirs


def run_dir(in_dir, out_dir, id=None, input_filename="input.txt"):
    """
    Reads the file contents of the input directory to perform the run command.
    If your processing requires more inputs than just a single file, you will
    find all files in the input directory. Ignore input_filename in that case.
    """

    file_name = in_dir / input_filename

    if method_input == 'data':
        with io.open(file_name, 'r', encoding="utf-8") as f:
            return run_method(f.read(), out_dir, id)
    else:
        return run_method(file_name, out_dir, id)


def init():
    input_path = Path(os.environ.get("INPUT_PATH", '/input'))
    output_path = Path(os.environ.get("OUTPUT_PATH", '/output'))

    for data_id in get_jobdirs(input_path):
        in_dir = input_path / data_id
        out_dir = output_path / data_id
        output = run_dir(in_dir, out_dir, id=data_id, input_filename=input_filename)

        if not out_dir.exists():
            os.makedirs(out_dir)
        with io.open(out_dir / output_filename, 'w', encoding='utf-8') as f:
            f.write(output)


if __name__ == "__main__":
    init()
