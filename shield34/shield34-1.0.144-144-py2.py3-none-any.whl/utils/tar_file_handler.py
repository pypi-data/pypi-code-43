import os
import tarfile
class TarFileHandler():

    @staticmethod
    def make_tarfile(output_filename, file_name, files):
        with tarfile.open(os.path.join(output_filename, file_name), "w:gz") as tar:
            for file_path in files:
                tar.add(file_path, arcname=os.path.basename(file_path))
