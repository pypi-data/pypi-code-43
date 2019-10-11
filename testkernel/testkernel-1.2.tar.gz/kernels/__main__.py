from ipykernel.kernelapp import IPKernelApp
from intel_kernel.install import install_kernel as install_intel_kernel
from intel_kernel.uninstall import uninstall_intel_kernel as uninstall_intel_kernel
from att_kernel.install import install_kernel as install_att_kernel
from att_kernel.uninstall import uninstall_intel_kernel as uninstall_att_kernel


#IPKernelApp.launch_instance(kernel_class=IntelKernel)


import sys

def main():
	count = 0
	is_install = False
	is_uninstall = False
	for arg in sys.argv[1:]:
		if count == 0 and arg == "install":
			is_install = True
		elif count == 0 and arg == "uninstall":
			is_uninstall = True
		else:
			if count > 0:
				if is_install:
					if arg == "intel":
						install_intel_kernel()
					elif arg == "att":
						install_att_kernel()
					elif arg == "all":
						install_intel_kernel()
						install_att_kernel()
				elif is_uninstall:
					if arg == "intel":
						uninstall_intel_kernel()
					elif arg == "att":
						uninstall_att_kernel()
					elif arg == "all":
						uninstall_intel_kernel()
						uninstall_att_kernel()
		count+=1
					
		

if __name__ == "__main__":
    main()