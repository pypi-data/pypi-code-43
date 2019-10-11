from distutils.core import setup

setup(
    name='testkernel',
    version='1.4',
    packages=['kernels', 'kernels/att_kernel', 'kernels/intel_kernel', 'kernels/riscv_kernel', 'assembler', 'assembler/Intel', 'assembler/RISCV'],
)
