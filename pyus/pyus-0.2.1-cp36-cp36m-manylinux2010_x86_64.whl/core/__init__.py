import os

# TODO: uncomment and replace when pulse moved as a submodule
PULSE_BASE_PATH = os.path.abspath(os.path.join(__file__, '..'))
PULSE_LIB_PATH = os.path.join(PULSE_BASE_PATH, 'lib')
PULSE_INCLUDE_PATH = os.path.join(PULSE_BASE_PATH, 'include')
CUDA_HEADERS_PATH = ('/usr/local/cuda/include')
