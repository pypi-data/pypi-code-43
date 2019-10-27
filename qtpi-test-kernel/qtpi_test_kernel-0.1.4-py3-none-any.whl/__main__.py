from ipykernel.kernelapp import IPKernelApp
from . import QtpiTestKernel

IPKernelApp.launch_instance(kernel_class=QtpiTestKernel)
