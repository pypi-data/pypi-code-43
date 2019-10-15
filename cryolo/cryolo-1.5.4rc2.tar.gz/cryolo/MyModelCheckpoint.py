#
# COPYRIGHT
#
# All contributions by Thorsten Wagner:
# Copyright (c) 2017 - 2019, Thorsten Wagner.
# All rights reserved.
#
# ---------------------------------------------------------------------------
#         Do not reproduce or redistribute, in whole or in part.
#      Use of this code is permitted only under licence from Max Planck Society.
#            Contact us at thorsten.wagner@mpi-dortmund.mpg.de
# ---------------------------------------------------------------------------
#

from keras.callbacks import ModelCheckpoint
import h5py


class MyModelCheckpoint(ModelCheckpoint):
    def __init__(
        self,
        filepath,
        monitor="val_loss",
        verbose=0,
        save_best_only=False,
        save_weights_only=False,
        mode="auto",
        period=1,
    ):
        pass

    def on_epoch_end(self, epoch, logs=None):
        current = logs.get(self.monitor)
        model_improved = self.monitor_op(current, self.best)
        super(ModelCheckpoint, self).on_epoch_end(epoch, logs)
        if model_improved:

            with h5py.File(self.filepath, mode="r+") as f:
                f["anchors"] = self.anchors
