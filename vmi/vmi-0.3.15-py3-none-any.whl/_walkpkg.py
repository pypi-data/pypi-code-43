import importlib
import inspect
import pkgutil
import PySide2
import OCC
import vtk
import CGAL


def walk_packages(p):
    err_starts, err_ends = ['_',
                            'vtk.gtk',
                            'vtk.qt.QVTKRenderWindowInteractor',
                            'vtk.qt4',
                            'vtk.tk'], ['Python']

    modules = set()
    modules_error = set()
    modules.add(p)

    for pkg in [_ for _ in pkgutil.walk_packages(p.__path__, p.__name__ + '.')]:
        err_flag = False

        if not err_flag:
            for err_start in err_starts:
                if pkg.name.startswith(err_start):
                    err_flag = True
                    break

        if not err_flag:
            for err_end in err_ends:
                if pkg.name.endswith(err_end):
                    err_flag = True
                    break

        if not err_flag:
            try:
                modules.add(importlib.import_module(pkg.name))
            except ImportError as err:
                modules_error.add(pkg.name)

    # print(len(modules))
    m_count = c_count = f_count = 0
    c_set = set()
    f_set = set()
    txt_file = open(p.__name__ + '.txt', 'w')

    for m in modules:
        m_count += 1
        m_str = m.__name__
        # txt_file.write(m_str + '\t->\t' + m.__class__.__name__ + '\n')

        for c_name, c in inspect.getmembers(m, inspect.isclass):
            if hasattr(m, c_name):
                c_count += 1
                c_str = m_str + '.' + c_name
                c_set.add(c_name)
                txt_file.write(c_str + '\t->\t' + c.__class__.__name__ + '\n')

                for f_name, f in inspect.getmembers(c):
                    f_count += 1
                    f_str = c_str + '.' + f_name
                    f_set.add(f_name)
                    # txt_file.write(f_str + '\t->\t' + f.__class__.__name__ + '\n')

    txt_file.close()
    print(p.__name__)
    print('module:', m_count)
    print('class:', c_count, len(c_set))
    print('member:', f_count, len(f_set))
    # print(modules_error)


if __name__ == '__main__':
    walk_packages(vtk)
    # walk_packages(PySide2)
    # walk_packages(OCC)
    # walk_packages(vtk)
    # walk_packages(itk)
