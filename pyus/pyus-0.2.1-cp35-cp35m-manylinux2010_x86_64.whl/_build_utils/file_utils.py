import os
import re
import errno
from distutils.dir_util import copy_tree, remove_tree
from glob import glob


def clean_cython(path='.', verbose=False):
    """Clean compiled Cython files (.cpp or .so in this case)"""
    cython_sources = find_cython_sources(path=path)
    # Note: using set removes potential duplicates
    cython_folers = set([os.path.dirname(p) for p in cython_sources])
    clean_files = []
    for p in cython_folers:
        clean_files += [os.path.join(p, f) for f in os.listdir(path=p)
                        if f.endswith(('.cpp', '.so'))]

    if clean_files:  # if not empty
        clean_files.sort()

        for f in clean_files:
            print(os.path.abspath(f))
        usr_in = input('Do you want to permanently remove these files '
                       '(y/[n])? ')
        usr_in = usr_in.lower() if usr_in else 'n'  # default: 'n'
        if not usr_in.lower() == 'n':
            # Remove files if accepted by user
            for f in clean_files:
                os.remove(f)
                if verbose:
                    print('removed {}'.format(os.path.abspath(f)))


def find_cython_sources(path):
    """Find Cython source files (.pyx)"""
    return _scan_dir(path=path, file_ext='.pyx')


def _scan_dir(path, file_ext):
    """Find files with extension file_ext under path"""
    file_list = []
    for root, dirs, files in os.walk(path):
        dirs.sort()
        for file in files:
            if file.endswith(file_ext):
                file_list.append(os.path.join(root, file))

    return file_list


def _scan_dir_glob(path, file_ext):
    """Find files with extension file_ext under path using glob"""
    file_list = glob(os.path.join(path, '**', '*' + file_ext), recursive=True)

    return file_list


def _list_sub_dir(dir):
    return [name for name in os.listdir(dir)
            if os.path.isdir(os.path.join(dir, name))]


def _list_files(dir):
    return [name for name in os.listdir(dir)
            if os.path.isfile(os.path.join(dir, name))]


def copy_includes(src, dst):
    """
        Copies src directory to dst/include.
        Replaces dst/include subdirectories and to be copied from src.
        """
    src_include = src
    dst_include = os.path.join(dst, 'include')

    # List include dirs to copy
    if os.path.isdir(src_include):
        list_src_inc = _list_sub_dir(src_include)
    else:
        raise ValueError('{} is not a directory'.format(src_include))

    # List include dirs already present
    if os.path.isdir(dst_include):
        list_dst_inc = _list_sub_dir(dst_include)
    else:
        os.makedirs(dst_include)
        list_dst_inc = []

    # Remove from dst/include dirs to be copied from src
    for dir in list_src_inc:
        if dir in list_dst_inc:
            remove_tree(os.path.join(dst_include, dir))

    # Copy includes and libs
    copy_tree(src_include, dst_include)


def copy_and_symlink_lib(src, dst):
    """
    Copies src directory to dst/lib.
    Replaces dts/lib files to be copied from src.
    Once the lib files are copied, creates a symlink stripped from version info
    for every copied lib file
    """
    src_lib = src
    # dst_lib = os.path.join(dst, 'lib')
    dst_lib = os.path.join(dst, 'lib')

    # List lib files to copy
    if os.path.isdir(src_lib):
        list_src_lib = _list_files(src_lib)
    else:
        raise ValueError('{} is not a directory'.format(src_lib))

    # List lib files already present
    if os.path.isdir(dst_lib):
        list_dst_lib = _list_files(dst_lib)
    else:
        list_dst_lib = []

    # Extract lib names from filenames
    # libs_dst = set([re.search('lib([^/]*?)\.so', file)[0] for file in list_dst_lib])
    libs_dst = []
    for file in list_dst_lib:
        libname = re.search('lib([^/]*?)\.so', file)
        if libname is not None:
            libs_dst.append(libname[0])
    libs_dst = set(libs_dst)

    # libs_src = set([re.search('lib([^/]*?)\.so', file)[0] for file in list_src_lib])
    libs_src = []
    for file in list_dst_lib:
        libname = re.search('lib([^/]*?)\.so', file)
        if libname is not None:
            libs_src.append(libname[0])
    libs_src = set(libs_dst)

    # Remove from dst/lib any file that matches the libnames to be copied from src
    for lib_name in libs_src:
        if lib_name in libs_dst:
            glob_files = glob(os.path.join(dst_lib, lib_name)+'*')
            [os.remove(file) for file in glob_files]

    # Copy includes and libs
    copy_tree(src_lib, dst_lib)

    # Create symlink for each copied lib
    # for lib_name in list_src_lib:
    #
    #     lib = os.path.abspath(os.path.join(dst_lib, lib_name))
    #     link_name = re.match('^(.*?)\.so', lib_name)[0]
    #     link_name = os.path.abspath(os.path.join(dst_lib, link_name))
    #
    #     try:
    #         os.symlink(lib, link_name)
    #     except OSError as err:
    #         if err.errno == errno.EEXIST:
    #             os.remove(link_name)
    #             os.symlink(lib, link_name)
    #         else:
    #             raise err
