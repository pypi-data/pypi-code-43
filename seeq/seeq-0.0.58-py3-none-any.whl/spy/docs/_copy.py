import os

from distutils import dir_util


def copy(folder=None, *, overwrite=False):
    if not folder:
        folder = os.path.join(os.getcwd(), 'Spy Documentation')

    if os.path.exists(folder):
        if not overwrite:
            raise RuntimeError('The "%s" folder already exists. If you would like to overwrite it, supply the '
                               'overwrite=True parameter. Make sure you don\'t have any of your own work in that '
                               'folder!' % folder)

        dir_util.remove_tree(folder)

    library_doc_folder = os.path.join(os.path.dirname(__file__), 'Documentation')

    dir_util.copy_tree(library_doc_folder, folder)

    print('Copied Spy library documentation to "%s"' % folder)
