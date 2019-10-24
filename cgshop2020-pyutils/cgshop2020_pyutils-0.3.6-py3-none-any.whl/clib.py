"""
This file contains stuff needed to use the C++-cores.
It is to some degree ugly hackery, so be warned.
"""

import ctypes
import os
import subprocess
import platform
import sys

__CPP_CORE_SUPPORTED = True


def is_cgal_cpp_core_supported():
    return __CPP_CORE_SUPPORTED


def disable_cgal_cpp_support():
    print("Disabling C++ CGAL features.")
    print("You cannot use the verification functionality or TrivialTriangulationSolver.")
    print("Some other functionality such as parsing is replaced by pure Python.")
    if sys.maxsize <= 2**32:
        print("You are using either a 32bit operating system or a 32bit Python",
              "environment. For full functionality, 64bit is needed.",
              "Note that for Windows, you have to install",
              "the x86-64 version of Python.")
    global __CPP_CORE_SUPPORTED
    __CPP_CORE_SUPPORTED = False


# root folders of binaries
__here = os.path.dirname(os.path.realpath(__file__))
__cpp_core_folder = os.path.join(__here, "cpp_core")
cmake_bin = os.path.join(__cpp_core_folder, "bin", "python_interface")
precompiled_bin = os.path.join(__cpp_core_folder, "binaries")


# system specific paths to lib
__paths = {
    "Linux": [
        os.path.join(cmake_bin, "libcgshop2020_verifier_module.so"),
        os.path.join(precompiled_bin, "linux-x86_64", "libcgshop2020_verifier_module.so")
    ],
    "Darwin": [
        os.path.join(cmake_bin, "libcgshop2020_verifier_module.so"),
        os.path.join(precompiled_bin, "osx", "libcgshop2020_verifier_module.so")
    ],
    "Windows": [
        os.path.join(cmake_bin, "cgshop2020_verifier_module.dll"),
        os.path.join(precompiled_bin, "win64" if sys.maxsize > 2**32 else "win32", "cgshop2020_verifier_module.dll")
    ]
}


# for windows, we have to jump through some additional hoops to
# be able to load our libraries (mainly, because there are several of them)
# and the kernel32.LoadLibrary search order, for DLL dependencies, does not
# include the directory of the depending DLL.
def __windows_set_dll_directory(os_name, add_path):
    if os_name == "Windows":
        kernel32 = ctypes.WinDLL.LoadLibrary("kernel32.dll")
        kernel32.SetDllDirectoryW.restype = ctypes.c_uint
        kernel32.SetDllDirectoryW.argtypes = [ctypes.c_char_p]
        if int(kernel32.SetDllDirectoryW(add_path.encode("utf-16-le"))) == 0:
            print("Warning: Failed to set Windows DLL directory!")


def try_to_load_clib(paths):
    os_name = platform.system()
    if os_name not in paths:
        print("Your platform", os_name, "does not seem to be supported, yet.")
        return None
    for path in paths[os_name]:
        try:
            if os.path.exists(path):
                __windows_set_dll_directory(os_name, os.path.dirname(path))
                lib = ctypes.cdll.LoadLibrary(path)
                return lib
        except OSError as ose:
            print("Tried to load library {}; the file exists but could not be loaded: {}".format(path, ose))
            pass
    return None


def compile_cpp_core():
    print("Compiling the C++ core.")
    print("You need to have CMake, a C++ compiler, CGAL and Boost installed.")
    source_folder = os.path.join(__here, "cpp_core")
    bin_folder = os.path.join(source_folder, "bin")
    
    # do not create a command line by concatenating strings (shell injection attacks, errors with spaces in paths)
    # this is why check_call takes multiple arguments
    cmake_cmd_1 = ["cmake", "-DCMAKE_BUILD_TYPE=RelWithDebInfo", "-S", str(source_folder), "-B", str(bin_folder)]
    cmake_cmd_2 = ["cmake", "--build", str(bin_folder), "--target", "cgshop2020_verifier_module",
                   "--config", "RelWithDebInfo"]
    cmake_cmd_3 = ["cmake", "--build", str(bin_folder), "--target", "cgshop2020_trivial_triangulation_solver_module",
                   "--config", "RelWithDebInfo"]
    try:
        ret_code = subprocess.check_call(*cmake_cmd_1, stderr=subprocess.STDOUT,
                                         shell=True)
        ret_code = subprocess.check_call(*cmake_cmd_2, stderr=subprocess.STDOUT,
                                         shell=True)
        ret_code = subprocess.check_call(*cmake_cmd_3, stderr=subprocess.STDOUT,
                                         shell=True)
        print("You have to reload the module for the new c++-core to be loaded.")
    except subprocess.CalledProcessError as cpe:
        print(cpe)


_CLIB = try_to_load_clib(__paths)
if _CLIB:
    print("Enabled C++ CGAL support. You should have full functionality.")
else:
    disable_cgal_cpp_support()
