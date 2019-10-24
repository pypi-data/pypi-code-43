from bwplot import lsbox, cbox


def pack_plotting_kwargs(ccbox, lls):
    kwargs = {}
    if lls is not None:
        kwargs["ls"] = lsbox(lls)
    if ccbox is not None:
        kwargs["c"] = cbox(ccbox)
    return kwargs
