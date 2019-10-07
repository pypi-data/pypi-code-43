import json
import logging
import os

from build_utils import utils

logger = logging.getLogger(__name__)

def write_output_to_cfn_parameters(execution_context, path):
    output_file_path = os.path.join(execution_context.dir_path, path)
    with open(output_file_path, mode='w') as parameter_file:
        for output_key, output_value in execution_context.output.items():
            if output_key == 'images':
                # Write images
                for image_id, image_uri in output_value.items():
                    parameter_file.write("{0}Image={1}".format(image_id, image_uri))
                    parameter_file.write("\n")

            else:
                logger.warn("Output values with key '%s' currently not supported", output_key)
