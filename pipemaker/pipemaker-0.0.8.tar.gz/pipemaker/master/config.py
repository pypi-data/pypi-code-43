from ..utils.dotdict import dotdict
import yaml
import os

# creds (in .gitignore)
HERE = os.path.dirname(__file__)
creds = dotdict(yaml.safe_load(open(f"{HERE}/._creds.yaml")))

# settings
config = dotdict(
    # automatically start local workers
    localworkers = True,
    # define to match external server OR by set_ftp()
    ftp_address = None,
    # define to match external server OR to avoid clash
    ftp_port = 4100,

    # default path filled at runtime with pathvars
    # filesystem examples
    #     "osfs://c/"
    #     "ftp://username:password@10.23.33.2:4100/"
    #     "s3://mybucket/
    path ="{filesystem}{datapath}/{job}/{name}{extension}",
    pathvars = dotdict(filesystem="osfs://", datapath="pipedata", job="default", extension=".pkl"),

    # dict(name=path) to override default path above e.g. for files shared across jobs
    # here rather than in functions as name/path is used in multiple functions as output and input
    paths=dotdict(),

    # dict(name=value) parameter inputs not from files
    params = dotdict(),

    # s=sync, a=async, b=block
    mode = "s")
