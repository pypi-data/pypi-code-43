import os
import traceback

from .logging import elogger


def ipfs_available():
    if os.path.exists("/ipfs"):
        fn = "/ipfs/QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG/readme"
        try:
            d = open(fn).read()
        except:
            msg = f"Could not open an IPFS file: {traceback.format_exc()}"
            elogger.warning(msg)
            return False

        if "Hello" in d:
            return True
        else:
            elogger.warning(d)
            return False
    else:
        elogger.warning("/ipfs not found")
        return False
