#!/usr/bin/python
import setuptools
import pkg_resources
import os
from subprocess import call
import shutil
from setuptools.command.install import install


package_name = "melopero-autostart"


def setup_system_service():
    autostart_dir = "/home/melopero-autostart/"
    scripts_dir = os.path.join(autostart_dir, "scripts/")
    uninstall_dir = os.path.join(autostart_dir, "uninstall/")
    uninstall_scripts_dir = os.path.join(uninstall_dir, "uninstall-scripts/")
    
    bash_script_name = "StartScripts.sh"
    instructions_name = "instructions.txt"
    uninstall_script_name = "uninstall.sh"
    uninstall_instructions_name = "uninstall_instructions.txt"
    
    systemd_dir = "/etc/systemd/system/"
    service_unit_name = "melopero-autostart.service"
    
    
    #create autostart dirs
    if not os.path.exists(autostart_dir):
        os.mkdir(autostart_dir)
    
    if not os.path.exists(scripts_dir):
        os.mkdir(scripts_dir)
        
    if not os.path.exists(uninstall_dir):
        os.mkdir(uninstall_dir)
        
    if not os.path.exists(uninstall_scripts_dir):
        os.mkdir(uninstall_scripts_dir)
        
    #copy bash script in autostart dir and instructions
    copyfile_and_chmod(bash_script_name, autostart_dir, mode = 0o554)
    copyfile_and_chmod(instructions_name, autostart_dir, mode = 0o444)
    
    #copy uninstall script in uninstall dir and instructions
    copyfile_and_chmod(uninstall_script_name, uninstall_dir, mode = 0o554)
    copyfile_and_chmod(uninstall_instructions_name, uninstall_dir, mode = 0o444)

    #copy system service unit
    service_unit_path = os.path.abspath(pkg_resources.resource_filename(package_name, service_unit_name))
    shutil.copyfile(service_unit_path, os.path.join(systemd_dir, service_unit_name))
    os.chmod(os.path.join(systemd_dir, service_unit_name), 0o664)
    shutil.chown(os.path.join(systemd_dir, service_unit_name), "root", "root")
    
    #enable service
    # =============================================================================
    # sudo systemctl daemon-reload
    # sudo systemctl enable sample.service
    # =============================================================================
    status = call(["systemctl", "daemon-reload"])
    if status == 0: 
        status = call(["systemctl", "enable", service_unit_name])
    
    if status != 0:
        print("""WARNING! Service could not be activated. Please enable the service
              by typing the following commands:\n sudo systemctl enable {} \n 
              sudo systemctl daemon-reload""".format(service_unit_name))
        
        
def copyfile_and_chmod(name, dest, mode = None):
    file_path = os.path.abspath(pkg_resources.resource_filename(package_name, name))
    final_path = os.path.join(dest, os.path.basename(file_path))
    shutil.copyfile(file_path, final_path)
    
    if mode is not None:
        os.chmod(final_path, mode)


class InstallCommand(install):
    def initialize_options(self):
        install.initialize_options(self)

    def finalize_options(self):
        #print('The custom option for install is ', self.custom_option)
        install.finalize_options(self)

    def run(self):
        setup_system_service()
        install.run(self)  # OR: install.do_egg_install(self)
    

setuptools.setup(
    name="melopero_autostart",
    version="0.0.8",
    description="Melopero Autostart, easily run python scripts at startup",
    #url="https://github.com/melopero/Melopero_AMG8833/tree/master/module",
    author="Melopero",
    author_email="info@melopero.com",
    license="MIT",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    cmdclass={
        'install': InstallCommand,
    },
)
