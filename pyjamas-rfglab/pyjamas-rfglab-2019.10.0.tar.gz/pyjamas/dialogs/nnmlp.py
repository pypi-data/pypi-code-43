"""
    PyJAMAS is Just A More Awesome Siesta
    Copyright (C) 2018  Rodrigo Fernandez-Gonzalez (rodrigo.fernandez.gonzalez@utoronto.ca)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from PyQt5 import QtCore, QtWidgets

from pyjamas.dialogs.classifierdialogABC import ClassifierDialogABC
import pyjamas.rimage.rimclassifier.rimnn as rimnn


class NNMLPDialog(ClassifierDialogABC):
    n_hidden: int = rimnn.nnmlp.N_HIDDEN
    l2: float = rimnn.nnmlp.L2
    epochs: int = rimnn.nnmlp.EPOCHS
    eta: float = rimnn.nnmlp.ETA
    minibatch_size = rimnn.nnmlp.MINIBATCH_SIZE

    def __init__(self):
        super().__init__()

        self.histogram_of_gradients = False

    def setupUi(self, NNMLP, parameters: dict = None):
        if parameters is None or parameters is False:
            parameters = {
                'positive_training_folder': NNMLPDialog.positive_training_folder,
                'negative_training_folder': NNMLPDialog.negative_training_folder,
                'hard_negative_training_folder': NNMLPDialog.hard_negative_training_folder,
                'histogram_of_gradients': NNMLPDialog.histogram_of_gradients,
                'train_image_size': NNMLPDialog.train_image_size,
                'step_sz': NNMLPDialog.step_sz,
                'n_hidden': NNMLPDialog.n_hidden,
                'l2': NNMLPDialog.l2,
                'epochs': NNMLPDialog.epochs,
                'eta': NNMLPDialog.eta,
                'minibatch_size': NNMLPDialog.minibatch_size,
            }

        NNMLPDialog.positive_training_folder = parameters.get('positive_training_folder', NNMLPDialog.positive_training_folder)
        NNMLPDialog.negative_training_folder = parameters.get('negative_training_folder', NNMLPDialog.negative_training_folder)
        NNMLPDialog.hard_negative_training_folder = parameters.get('hard_negative_training_folder', NNMLPDialog.hard_negative_training_folder)
        NNMLPDialog.histogram_of_gradients = parameters.get('histogram_of_gradients', NNMLPDialog.histogram_of_gradients)
        NNMLPDialog.train_image_size = parameters.get('train_image_size', NNMLPDialog.train_image_size)
        NNMLPDialog.step_sz = parameters.get('step_sz', NNMLPDialog.step_sz)
        NNMLPDialog.n_hidden = parameters.get('n_hidden', NNMLPDialog.n_hidden)
        NNMLPDialog.l2 = parameters.get('l2', NNMLPDialog.l2)
        NNMLPDialog.epochs = parameters.get('epochs', NNMLPDialog.epochs)
        NNMLPDialog.eta = parameters.get('eta', NNMLPDialog.eta)
        NNMLPDialog.minibatch_size = parameters.get('minibatch_size', NNMLPDialog.minibatch_size)

        NNMLP.setObjectName("NNMLP")
        NNMLP.resize(614, 450)
        self.buttonBox = QtWidgets.QDialogButtonBox(NNMLP)
        self.buttonBox.setGeometry(QtCore.QRect(240, 410, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.groupBox_2 = QtWidgets.QGroupBox(NNMLP)
        self.groupBox_2.setGeometry(QtCore.QRect(30, 26, 551, 121))
        self.groupBox_2.setObjectName("groupBox_2")
        self.label = QtWidgets.QLabel(self.groupBox_2)
        self.label.setGeometry(QtCore.QRect(31, 26, 141, 24))
        self.label.setObjectName("label")
        self.positive_training_folder_edit = QtWidgets.QLineEdit(self.groupBox_2)
        self.positive_training_folder_edit.setGeometry(QtCore.QRect(220, 30, 261, 21))
        self.positive_training_folder_edit.setObjectName("positive_training_folder_edit")
        self.positive_training_folder_edit.setText(NNMLPDialog.positive_training_folder)
        self.btnSavePositive = QtWidgets.QToolButton(self.groupBox_2)
        self.btnSavePositive.setGeometry(QtCore.QRect(490, 30, 26, 22))
        self.btnSavePositive.setObjectName("btnSavePositive")
        self.btnSavePositive.clicked.connect(self._open_positive_folder_dialog)
        self.negative_training_folder_edit = QtWidgets.QLineEdit(self.groupBox_2)
        self.negative_training_folder_edit.setGeometry(QtCore.QRect(220, 60, 261, 21))
        self.negative_training_folder_edit.setObjectName("negative_training_folder_edit")
        self.negative_training_folder_edit.setText(NNMLPDialog.negative_training_folder)
        self.label_2 = QtWidgets.QLabel(self.groupBox_2)
        self.label_2.setGeometry(QtCore.QRect(31, 56, 141, 24))
        self.label_2.setObjectName("label_2")
        self.btnSaveNegative = QtWidgets.QToolButton(self.groupBox_2)
        self.btnSaveNegative.setGeometry(QtCore.QRect(490, 60, 26, 22))
        self.btnSaveNegative.setObjectName("btnSaveNegative")
        self.btnSaveNegative.clicked.connect(self._open_negative_folder_dialog)
        self.label_3 = QtWidgets.QLabel(self.groupBox_2)
        self.label_3.setGeometry(QtCore.QRect(31, 86, 181, 24))
        self.label_3.setObjectName("label_3")
        self.btnSaveHard = QtWidgets.QToolButton(self.groupBox_2)
        self.btnSaveHard.setGeometry(QtCore.QRect(490, 90, 26, 22))
        self.btnSaveHard.setObjectName("btnSaveHard")
        self.btnSaveHard.clicked.connect(self._open_hard_folder_dialog)
        self.hard_negative_training_folder_edit = QtWidgets.QLineEdit(self.groupBox_2)
        self.hard_negative_training_folder_edit.setGeometry(QtCore.QRect(220, 90, 261, 21))
        self.hard_negative_training_folder_edit.setObjectName("hard_negative_training_folder_edit")
        self.hard_negative_training_folder_edit.setText(NNMLPDialog.hard_negative_training_folder)
        self.groupBox_3 = QtWidgets.QGroupBox(NNMLP)
        self.groupBox_3.setGeometry(QtCore.QRect(30, 156, 251, 61))
        self.groupBox_3.setObjectName("groupBox_3")
        self.label_4 = QtWidgets.QLabel(self.groupBox_3)
        self.label_4.setGeometry(QtCore.QRect(31, 28, 141, 24))
        self.label_4.setObjectName("label_4")
        self.lnWidth = QtWidgets.QLineEdit(self.groupBox_3)
        self.lnWidth.setGeometry(QtCore.QRect(70, 30, 31, 21))
        self.lnWidth.setObjectName("lnWidth")
        self.lnWidth.setText(str(NNMLPDialog.train_image_size[1]))
        self.lnHeight = QtWidgets.QLineEdit(self.groupBox_3)
        self.lnHeight.setGeometry(QtCore.QRect(170, 30, 31, 21))
        self.lnHeight.setObjectName("lnHeight")
        self.lnHeight.setText(str(NNMLPDialog.train_image_size[0]))
        self.label_5 = QtWidgets.QLabel(self.groupBox_3)
        self.label_5.setGeometry(QtCore.QRect(120, 28, 141, 24))
        self.label_5.setObjectName("label_5")
        self.label_5.raise_()
        self.label_4.raise_()
        self.lnWidth.raise_()
        self.lnHeight.raise_()
        self.groupBox_4 = QtWidgets.QGroupBox(NNMLP)
        self.groupBox_4.setGeometry(QtCore.QRect(30, 226, 551, 61))
        self.groupBox_4.setObjectName("groupBox_4")
        self.checkBoxHOG = QtWidgets.QCheckBox(self.groupBox_4)
        self.checkBoxHOG.setGeometry(QtCore.QRect(30, 30, 161, 20))
        self.checkBoxHOG.setObjectName("checkBoxHOG")
        self.checkBoxHOG.setChecked(NNMLPDialog.histogram_of_gradients)
        self.groupBox_5 = QtWidgets.QGroupBox(NNMLP)
        self.groupBox_5.setGeometry(QtCore.QRect(30, 296, 551, 101))
        self.groupBox_5.setObjectName("groupBox_5")
        self.lnHidden = QtWidgets.QLineEdit(self.groupBox_5)
        self.lnHidden.setGeometry(QtCore.QRect(160, 30, 31, 21))
        self.lnHidden.setObjectName("lnHidden")
        self.lnHidden.setText(str(NNMLPDialog.n_hidden))
        self.label_8 = QtWidgets.QLabel(self.groupBox_5)
        self.label_8.setGeometry(QtCore.QRect(30, 28, 181, 24))
        self.label_8.setObjectName("label_8")
        self.lnRegul = QtWidgets.QLineEdit(self.groupBox_5)
        self.lnRegul.setGeometry(QtCore.QRect(314, 30, 55, 21))
        self.lnRegul.setObjectName("lnRegul")
        self.lnRegul.setText(str(NNMLPDialog.l2))
        self.label_9 = QtWidgets.QLabel(self.groupBox_5)
        self.label_9.setGeometry(QtCore.QRect(210, 30, 141, 24))
        self.label_9.setObjectName("label_9")
        self.lnEpochs = QtWidgets.QLineEdit(self.groupBox_5)
        self.lnEpochs.setGeometry(QtCore.QRect(470, 30, 41, 21))
        self.lnEpochs.setObjectName("lnEpochs")
        self.lnEpochs.setText(str(NNMLPDialog.epochs))
        self.label_10 = QtWidgets.QLabel(self.groupBox_5)
        self.label_10.setGeometry(QtCore.QRect(380, 30, 91, 24))
        self.label_10.setObjectName("label_10")
        self.lnEta = QtWidgets.QLineEdit(self.groupBox_5)
        self.lnEta.setGeometry(QtCore.QRect(216, 66, 46, 21))
        self.lnEta.setObjectName("lnEta")
        self.lnEta.setText(str(NNMLPDialog.eta))
        self.label_11 = QtWidgets.QLabel(self.groupBox_5)
        self.label_11.setGeometry(QtCore.QRect(130, 70, 141, 16))
        self.label_11.setObjectName("label_11")
        self.lnBatchSz = QtWidgets.QLineEdit(self.groupBox_5)
        self.lnBatchSz.setGeometry(QtCore.QRect(373, 66, 36, 21))
        self.lnBatchSz.setObjectName("lnBatchSz")
        self.lnBatchSz.setText(str(NNMLPDialog.minibatch_size))
        self.label_14 = QtWidgets.QLabel(self.groupBox_5)
        self.label_14.setGeometry(QtCore.QRect(300, 70, 81, 16))
        self.label_14.setObjectName("label_14")
        self.label_8.raise_()
        self.lnHidden.raise_()
        self.label_9.raise_()
        self.lnRegul.raise_()
        self.label_10.raise_()
        self.lnEpochs.raise_()
        self.label_11.raise_()
        self.lnEta.raise_()
        self.label_14.raise_()
        self.lnBatchSz.raise_()
        self.groupBox_6 = QtWidgets.QGroupBox(NNMLP)
        self.groupBox_6.setGeometry(QtCore.QRect(300, 155, 281, 61))
        self.groupBox_6.setObjectName("groupBox_6")
        self.label_12 = QtWidgets.QLabel(self.groupBox_6)
        self.label_12.setGeometry(QtCore.QRect(31, 28, 141, 24))
        self.label_12.setObjectName("label_12")
        self.lnRow = QtWidgets.QLineEdit(self.groupBox_6)
        self.lnRow.setGeometry(QtCore.QRect(70, 30, 31, 21))
        self.lnRow.setObjectName("lnRow")
        self.lnRow.setText(str(NNMLPDialog.step_sz[0]))
        self.lnColumn = QtWidgets.QLineEdit(self.groupBox_6)
        self.lnColumn.setGeometry(QtCore.QRect(180, 30, 31, 21))
        self.lnColumn.setObjectName("lnColumn")
        self.lnColumn.setText(str(NNMLPDialog.step_sz[1]))
        self.label_13 = QtWidgets.QLabel(self.groupBox_6)
        self.label_13.setGeometry(QtCore.QRect(120, 28, 141, 24))
        self.label_13.setObjectName("label_13")
        self.label_13.raise_()
        self.label_12.raise_()
        self.lnRow.raise_()
        self.lnColumn.raise_()

        self.retranslateUi(NNMLP)
        self.buttonBox.accepted.connect(NNMLP.accept)
        self.buttonBox.rejected.connect(NNMLP.reject)
        QtCore.QMetaObject.connectSlotsByName(NNMLP)

    def retranslateUi(self, NNMLP):
        _translate = QtCore.QCoreApplication.translate
        NNMLP.setWindowTitle(_translate("NNMLP", "Train multilayer perceptron"))
        self.groupBox_2.setTitle(_translate("NNMLP", "Project files"))
        self.label.setText(_translate("NNMLP", "positive training folder"))
        self.btnSavePositive.setText(_translate("NNMLP", "..."))
        self.label_2.setText(_translate("NNMLP", "negative training folder"))
        self.btnSaveNegative.setText(_translate("NNMLP", "..."))
        self.label_3.setText(_translate("NNMLP", "hard negative training folder"))
        self.btnSaveHard.setText(_translate("NNMLP", "..."))
        self.groupBox_3.setTitle(_translate("NNMLP", "Training image size"))
        self.label_4.setText(_translate("NNMLP", "width"))
        self.label_5.setText(_translate("NNMLP", "height"))
        self.groupBox_4.setTitle(_translate("NNMLP", "Image features"))
        self.checkBoxHOG.setText(_translate("NNMLP", "histogram of gradients"))
        self.groupBox_5.setTitle(_translate("NNMLP", "Multilayer perceptron parameters"))
        self.label_8.setText(_translate("NNMLP", "no. of hidden layers"))
        self.label_9.setText(_translate("NNMLP", "l2 regularization"))
        self.label_10.setText(_translate("NNMLP", "no. of epochs"))
        self.label_11.setText(_translate("NNMLP", "learning rate"))
        self.groupBox_6.setTitle(_translate("NNMLP", "Image step size"))
        self.label_12.setText(_translate("NNMLP", "rows"))
        self.label_13.setText(_translate("NNMLP", "columns"))
        self.label_14.setText(_translate("NNMLP", "batch size"))

    def parameters(self) -> dict:
        NNMLPDialog.positive_training_folder = self.positive_training_folder_edit.text()
        NNMLPDialog.negative_training_folder = self.negative_training_folder_edit.text()
        NNMLPDialog.hard_negative_training_folder = self.hard_negative_training_folder_edit.text()
        NNMLPDialog.histogram_of_gradients = self.checkBoxHOG.isChecked()
        NNMLPDialog.train_image_size = int(self.lnHeight.text()), int(self.lnWidth.text())

        theparameters = {'positive_training_folder': NNMLPDialog.positive_training_folder,
                         'negative_training_folder': NNMLPDialog.negative_training_folder,
                         'hard_negative_training_folder': NNMLPDialog.hard_negative_training_folder,
                         'histogram_of_gradients': NNMLPDialog.histogram_of_gradients,
                         'train_image_size': NNMLPDialog.train_image_size,
                         'step_sz': NNMLPDialog.step_sz,
                         'n_hidden': NNMLPDialog.n_hidden,
                         'l2': NNMLPDialog.l2,
                         'epochs': NNMLPDialog.epochs,
                         'eta': NNMLPDialog.eta,
                         'minibatch_size': NNMLPDialog.minibatch_size
                         }

        return theparameters
