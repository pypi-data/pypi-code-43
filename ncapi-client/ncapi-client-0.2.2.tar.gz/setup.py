from setuptools import setup, find_namespace_packages, wheel
from setuptools.command.build_py import build_py as SetuptoolsBuild
from wheel.bdist_wheel import bdist_wheel as SetupToolsBdistWheel
import os
import shutil


def notify(path):
    if os.path.isdir(path):
        for p in os.listdir(path):
            notify(os.path.join(path, p))
    elif (
        len(os.path.splitext(path)) > 1 and os.path.splitext(path)[1].strip(".") == "py"
    ):
        with open("notice.txt", "r", encoding="utf-8") as f:
            with open(path, "r", encoding="utf-8") as script:
                notice_content = f.read()
                script_content = script.read()
        with open(path, "w", encoding="utf-8") as script:
            script.writelines(notice_content)
            script.writelines(script_content)
    else:
        pass


def save_dotpy_files(root_dir, tmp_dir, copy=False):
    dotpys = []
    for curr_root, _, filenames in os.walk(root_dir):
        curr_dotpys = [
            fname for fname in filenames if os.path.splitext(fname)[1] == ".py"
        ]
        if not curr_dotpys:
            continue

        dst_dir = os.path.join(tmp_dir, curr_root)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)

        for fname in curr_dotpys:
            src = os.path.join(curr_root, fname)
            dst = os.path.join(dst_dir, fname)
            if copy:
                shutil.copy(src, dst)
            else:
                shutil.move(src, dst)
            dotpys.append(dst)

    return dotpys


def restore_dotpy_files(fnames, root_dir, tmp_dir):
    for src in fnames:
        dst = src.lstrip(tmp_dir).lstrip(os.sep)
        assert dst.startswith(root_dir)
        shutil.move(src, dst)


class NCSBuild(SetuptoolsBuild):
    def run(self):
        root_dir = "ncapi_client"
        tmp_dir = ".build"
        dotpys = save_dotpy_files(root_dir, tmp_dir, copy=True)
        notify(root_dir)
        super().run()
        restore_dotpy_files(dotpys, root_dir, tmp_dir)


with open("VERSION") as f:
    version = f.readline()
setup(
    name="ncapi-client",
    description="Python client for NCAPI",
    version=version,
    install_requires=[
        "requests",
        "websockets",
        "click>=7.0",
        "halo",
        "tabulate",
        "tqdm",
        "nest_asyncio",
        "numpy",
        "pyyaml",
        "matplotlib",
        "ipywidgets",
	"parso>=0.5.1"
    ],
    entry_points={
        "console_scripts": [
            "ncs = ncapi_client.ncs:safe_cli",
            "ncs-dev = ncapi_client.ncs:cli",
        ]
    },
    packages=["ncapi_client"],
    python_requires=">=3.6",
    cmdclass={"build_py": NCSBuild},
)
