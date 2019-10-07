# Python imports
from __future__ import division


# 3rd party imports

# Our imports
import vespa.analysis.src.dialog_dataset_browser as dialog_dataset_browser


def select_ecc_dataset(datasets):
    dialog = dialog_dataset_browser.DialogDatasetBrowser(datasets)
    dialog.ShowModal()
    dataset = dialog.dataset
    dialog.Destroy()
    return dataset
