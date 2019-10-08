# -*- coding: utf-8 -*-
# !/usr/bin/env python3
"""
@author: Stephan Rein

 GLOPEL
 Program for analysis and global analysis  of Peldor/DEER data

FOR MANUAL INSTALLATION FROM SOURCE PLEASE READ THE README FILE!

The program is distributed under a GPLv3 license
For further details see LICENSE.txt

Copyright (c) 2018, Stephan Rein
All rights reserved.
"""


# Load all libraries
try:
    import GloPel
except ImportError:
    pass
import time as time
import datetime
import numpy as np
import sys
import os
import matplotlib
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMessageBox,
                             QFileDialog, QLabel, QAction, QDialog,
                             QGridLayout, QSplashScreen)
from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap, QIcon
try:
    from GloPel.GloPelMainGui import Ui_GloPel2017
    from GloPel.Variable_Initialization import (initialize_var1,
                                                initialize_var2,
                                                read_input_var)
    from GloPel.Calculations import (make_FT, bg_correction,
                                     bg_subtraction, normalize,
                                     AutomaticPc, normalize_Mod,
                                     make_distance_dist,
                                     bg_correction_fit_dim)
    from GloPel.figure_handler import (figure_handler_init,
                                       figure_handler,
                                       figure_handler_fit,
                                       figure_handler_globalfit,
                                       figure_handler_reg,
                                       figure_handler_dual_disp)
    from GloPel.Calculations_Fitting import (trust_region_reflective,
                                             objective_min,
                                             final_PELDOR_Calculation,
                                             lsq_deviation,
                                             F_test_model_comp)
    from GloPel.Residue_SubGUI import ResidueSubGUIhandling
    from GloPel.Validation_SubGUI import ValidationSubGUIhandling
    from GloPel.Regularization import regularization, form_fac_fit
    from GloPel.Warning_BG_dim_FIT import Ui_Warning_BGDIMFIT as ChildBGWarn
except ImportError:
    from GloPelMainGui import Ui_GloPel2017
    from Variable_Initialization import (initialize_var1, initialize_var2,
                                         read_input_var)
    from Calculations import (make_FT, bg_correction,  bg_subtraction,
                              normalize, AutomaticPc, normalize_Mod,
                              make_distance_dist, bg_correction_fit_dim)
    from figure_handler import (figure_handler_init, figure_handler,
                                figure_handler_fit, figure_handler_globalfit,
                                figure_handler_reg, figure_handler_dual_disp)
    from Calculations_Fitting import (trust_region_reflective, objective_min,
                                      final_PELDOR_Calculation, lsq_deviation,
                                      F_test_model_comp)
    from Residue_SubGUI import ResidueSubGUIhandling
    from Validation_SubGUI import ValidationSubGUIhandling
    from Regularization import regularization, form_fac_fit
    from Warning_BG_dim_FIT import Ui_Warning_BGDIMFIT as ChildBGWarn
from scipy.ndimage import gaussian_filter
from scipy import interpolate
# Define backend string for matplotlib
matplotlib.use("Qt5Agg", force=True)


# Subclass for printing in GUI instead of the console
class EmittingStream(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))

    def flush(self):
        pass


# Relative path (redirected in binary to _MEIPASS)
def resource_path(relative_path):
    try:
        try:
            return os.path.join(sys._MEIPASS, relative_path)
        except Exception:
            return os.path.join(GloPel.__path__[0], relative_path)
    except:
        return relative_path

# GUI Main class
class GloPelMainGuiDesign(QMainWindow, Ui_GloPel2017,
                          EmittingStream):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.icon2 = QIcon()
        self.icon2.addPixmap(QPixmap(resource_path("icon_logo.ico")))
        self.iconpath = resource_path("icon.png")
        self.pdfpath = resource_path("Manual_GloPel.pdf")
        self.setWindowIcon(self.icon2)
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        # GloPel Version number
        self.GlopelVersion = "GloPel2017 Version 1.0.1"
        # Initialize Variables for time trace 1/2
        initialize_var1(self)
        initialize_var2(self)
        # Active dataset and global settings
        self.activeset = 1
        self.globalbg_fun = None
        self.globalbg_fun_isOn = False
        self.globalmod_isOn = False
        self.globalanaisOn = False
        self.fitweight = 0
        self.regularziationisoN = True
        self.dual_display = False
        self.global_output_results = list()
        self.save_glob_fit = False
        self.global_L_curve_num = 5
        self.currentglobal_result = False
        self.setexists = np.zeros(2)
        self.setexists[0] = False
        self.setexists[1] = False
        self.supressingglob = False
        self.supressingstartglo = 1
        self.supressingendglo = 1
        self.global_adaptive = False
        self.global_large_kernel1 = False
        self.redline_global = 8
        self.reg1_global = None
        self.Subguiinit = False
        self.show_autocorr = False
        self.show_autocorr_av = False
        self.L_autocorr = False
        self.fitting_algorithm = 1
        self.reg_method = 1
        self.normalize_to_maximum = True
        self.Subguiinit_Valid = False
        self.current_result_is_reg = False
        # Add Menubar to Main Window
        self.bar = self.menuBar()
        self.bar.setNativeMenuBar(False)
        self.edit = self.bar.addMenu("File")
        self.load = self.edit.addAction("Load Data")
        self.load.triggered.connect(self.Loaddata)
        #self.load_old_session = self.edit.addAction("Load Old Session")
        self.savedata = self.edit.addAction("Save Session")
        self.savedata.triggered.connect(self.save_file_menu)
        self.exit_menubar = self.edit.addAction("Exit")
        self.exit_menubar.triggered.connect(self.close_GUI)
        self.helpbar = self.bar.addMenu("Help")
        self.manual = self.helpbar.addAction("Load Manual")
        self. manual.triggered.connect(self.OpenManual)
        self.tool = self.helpbar.addAction("Enable Tooltips")
        self.tool.triggered.connect(self.Enable_Tooltips)
        self.tool2 = self.helpbar.addAction("Disable Tooltips")
        self.tool2.triggered.connect(self.Disable_Tooltips)
        # Define matplotlib for window  containered in QWidget
        figure_handler_init(self, True, 1)
        figure_handler_init(self, True, 2)
        figure_handler_init(self, True, 3)
        # Close Button Gui
        self.Closebutton.clicked.connect(self.close_GUI)
        self.Loadbuttonset2.clicked.connect(lambda: self.open_file(2))
        self.Loadbuttonset1.clicked.connect(lambda: self.open_file(1))
        # Choose active data set
        self.Enableset1.toggled.connect(lambda: self.which_dataset(1))
        self.Enableset2.toggled.connect(lambda: self.which_dataset(2))
        # If imaginary should be showed
        self.show_imaginary.toggled.connect(lambda: self.show_imag(
                                            self.activeset))
        # User defined background start
        self.Bg_Start.valueChanged.connect(lambda:
                                           self.set_bg_start(self.activeset))
        self.Bg_dimension.valueChanged.connect(lambda:
                                               self.set_bg_dim(self.activeset))
        # User defined zero-time
        self.Zerotimebox.valueChanged.connect(lambda: self.set_zero_time(
                                              self.activeset))
        # User defined zero-time
        self.Nomalizebox.valueChanged.connect(lambda:
                                              self.set_norm(self.activeset))
        # Global background correction
        self.Checkbox_GlobalBg.stateChanged.connect(lambda: self.use_globalBG(
                                                    self.Checkbox_GlobalBg))
        # Modulation depth normalization
        self.Checkbox_Moddepth_norm.stateChanged.connect(lambda:
                                                         self.use_globalmod(
                                                         self.Checkbox_Moddepth_norm))
        # Cut the data in the long time range
        self.Cutoffbox.valueChanged.connect(lambda:
                                            self.set_cut(self.activeset))
        # Use excluded volume effect
        self.Excluded_volBox.stateChanged.connect(lambda:
                                                  self.enable_exclusiv_vol(
                                                  self.Excluded_volBox))
        self.Bg_excluded_vol.valueChanged.connect(lambda:
                                                  self.exclude_vol(
                                                  self.activeset))

        # self.Form_factor_based_fit.stateChanged.connect(lambda:
        #                                                self.form_fac())
        # Fit background dimension
        self.Fit_Background_dimension.stateChanged.connect(lambda:
                                                           self.fit_background_dim(self.activeset))
        # Show dual display
        self.dual_display_button.toggled.connect(lambda:
                                                 self.dual_disp(self.activeset))
        # Zoom in or out
        self.ZoomFTScrollBar.valueChanged.connect(lambda:
                                                  self.zoom(self.activeset))
        self.ZoomFTScrollBar_2.valueChanged.connect(lambda:
                                                    self.zoom(self.activeset))
        self.ZoomFTScrollBar_3.valueChanged.connect(lambda:
                                                    self.zoom(self.activeset))
        # Settings for fitting
        self.TR_Rbutton.toggled.connect(lambda:
                                        self.fit_button_TR(self.activeset))
        self.Simplexbutton.toggled.connect(lambda:
                                           self.fit_button_Simplex(self.activeset))
        self.CG_Button.toggled.connect(lambda:
                                       self.fit_button_CG(self.activeset))
        self.Powell.toggled.connect(lambda:
                                    self.fit_button_Powell(self.activeset))
        self.DiffEvolv_Button.toggled.connect(lambda:
                                              self.fit_button_DiffEvol(self.activeset))
        self.StochsticTRbutton.toggled.connect(lambda:
                                               self.fit_button_STR(self.activeset))
        self.StartbuttonAna.clicked.connect(lambda:
                                            self.fit_button_pressed(self.activeset))
        self.Multigaussian_Box.stateChanged.connect(lambda:
                                                    self.set_fit_model_mult(self.Multigaussian_Box))
        self.GlobalAnalysis.stateChanged.connect(lambda:
                                                 self.set_global_analysis(self.GlobalAnalysis))
        # Settings for regularization
        self.thikonovbutton.toggled.connect(lambda:
                                            self.button_Thikonov(self.activeset))
        self.L_Curve_numberBox.valueChanged.connect(lambda:
                                                    self.L_curve(self.activeset))
        self.DTSVDbutton.toggled.connect(lambda:
                                         self.button_DTSVD(self.activeset))
        self.Maximum_Entropy_But.toggled.connect(lambda:
                                                 self.button_MaxEntr(self.activeset))

        # Define suppression of regions (Disabled at the moment)
        # self.Define_suppression.clicked.connect(lambda: self.def_suppression(self.activeset))
        # self.use_suppression_box.stateChanged.connect(lambda:self.set_enable_suppresssion(self.activeset))

        self.use_adaptive_kernel.stateChanged.connect(lambda:
                                                      self.enable_adaptive_kernel(self.activeset))
        self.use_large_kernel.stateChanged.connect(lambda:
                                                   self.enable_large_kernel(self.activeset))
        # Enable separate residual plot
        self.Detach_resiuals.clicked.connect(lambda:
                                             self.detach_lsq(self.activeset))
        self.Enable_validation_button.clicked.connect(lambda:
                                                      self.validation(self.activeset))
        self.L_curve_button.clicked.connect(lambda:
                                            self.Change_L_Curve(self.activeset))
        self.Maximum_area_norm_button.clicked.connect(lambda:
                                                      self.Change_Max_area_norm(self.activeset))
        # Save Results
        self.Savebutton.clicked.connect(lambda:
                                        self.save_file(self.activeset))

        _translate = QtCore.QCoreApplication.translate
        self.Enable_validation_button.setToolTip(_translate("GloPel2017", ""))

        """********************************************************************
        DEFINITION OF ALL FUNCTIONS/METHODS
        ********************************************************************"""
    def normalOutputWritten(self, text):
        # Append text to the QTextEdit
        self.cursor = self.plainTextEdit.textCursor()
        self.cursor.insertText(text)
        self.plainTextEdit.setTextCursor(self.cursor)
        self.plainTextEdit.ensureCursorVisible()

    def Loaddata(self):
        if self.Enableset1.isChecked():
            self.activeset = 1
        else:
            self.activeset = 2
        self.open_file(self.activeset)
        return

    def save_file_menu(self):
        self.save_file(self.activeset)

    def Enable_Tooltips(self):
        _translate = QtCore.QCoreApplication.translate
        str_tmp = ("<html><head/><body><p>Validation of the Tikhonov" +
                   " solution by evaluating the impact of variation of" +
                   " preprocessing parameters</p></body></html>")
        self.Enable_validation_button.setToolTip(_translate("GloPel2017",
                                                            str_tmp))
        self.Enable_validation_button.setToolTipDuration(6000)
        str_tmp = ("<html><head/><body><p>L-Curve plot or autocorrelation-of" +
                   "-residues-plot. The corner of both plots are heuristic" +
                   " indicators for an optimal regularization parameter " +
                   "(L-Curve number)</p></body></html>")
        self.L_curve_button.setToolTip(_translate("GloPel2017",
                                                  str_tmp))
        self.L_curve_button.setToolTipDuration(6000)
        str_tmp = ("Autocorrelation function and distribution function of " +
                   "residues")
        self.Detach_resiuals.setToolTip(_translate("GloPel2017",
                                                   str_tmp))
        self.Detach_resiuals.setToolTipDuration(6000)
        str_tmp = "Stepsize of the PELDOR inversion pulse"
        self.Timescaleset1.setToolTip(_translate("GloPel2017",
                                                 str_tmp))
        self.Timescaleset1.setToolTipDuration(6000)
        str_tmp = "Stepsize of the PELDOR inversion pulse"
        self.Timescaleset2.setToolTip(_translate("GloPel2017",
                                                 str_tmp))
        self.Timescaleset2.setToolTipDuration(6000)
        str_tmp = "261 instead of 131 points in the distance domain"
        self.use_adaptive_kernel.setToolTip(_translate("GloPel2017",
                                                       str_tmp))
        self.use_adaptive_kernel.setToolTipDuration(6000)
        str_tmp = "521 instead of 131 points in the distance domain"
        self.use_large_kernel.setToolTip(_translate("GloPel2017",
                                                    str_tmp))
        self.use_large_kernel.setToolTipDuration(6000)
        str_tmp = "Global analysis of two time traces"
        self.GlobalAnalysis.setToolTip(_translate("GloPel2017",
                                                  str_tmp))
        self.GlobalAnalysis.setToolTipDuration(6000)
        str_tmp = ("<html><head/><body><p>Cut part on the right hand side of" +
                   " the background corrected time trace.</p></body></html>")
        self.Cutoffbox.setToolTip(_translate("GloPel2017",
                                             str_tmp))
        self.Cutoffbox.setToolTipDuration(6000)
        str_tmp = "Normalization of the time trace to maximum/area"
        self.Maximum_area_norm_button.setToolTip(_translate("GloPel2017",
                                                            str_tmp))
        self.Maximum_area_norm_button.setToolTipDuration(6000)
        return

    def Disable_Tooltips(self):
        _translate = QtCore.QCoreApplication.translate
        self.Enable_validation_button.setToolTip(_translate("GloPel2017", ""))
        self.L_curve_button.setToolTip(_translate("GloPel2017", ""))
        self.Detach_resiuals.setToolTip(_translate("GloPel2017", ""))
        self.Timescaleset1.setToolTip(_translate("GloPel2017", ""))
        self.Timescaleset2.setToolTip(_translate("GloPel2017", ""))
        self.use_adaptive_kernel.setToolTip(_translate("GloPel2017", ""))
        self.use_large_kernel.setToolTip(_translate("GloPel2017", ""))
        self.GlobalAnalysis.setToolTip(_translate("GloPel2017", ""))
        self.Cutoffbox.setToolTip(_translate("GloPel2017", ""))
        self.Maximum_area_norm_button.setToolTip(_translate("GloPel2017", ""))
        return

    def OpenManual(self):
        try:
            print("Manual loaded")
            if os.name == "nt":
                os.startfile(self.pdfpath)
            elif os.name == "posix":
                str_tmp = "/usr/bin/xdg-open "+self.pdfpath
                os.system(str_tmp)
        except:
            print("Manual could not be loaded")
        return

    def open_file(self, t):
        self.dialog = QFileDialog()
        str_tmp = "*.txt (*.txt *.TXT);;*dat (*.dat .*DAT);;*dta (*.DTA *.dta)"
        name, name_tmp = self.dialog.getOpenFileName(self, 'Open File', None,
                                                     str_tmp)
        if not name:
            return
        if (name.endswith('.txt') or name.endswith('.TXT') or
           name.endswith('.dat') or name.endswith('.DAT')):
            try:
                try:
                    Input = np.loadtxt(name)
                except ValueError:
                    Input = np.loadtxt(name, skiprows=2)
                    Input = np.delete(Input, 0, 1)
                self.Checkbox_GlobalBg.setCheckState(False)
                self.Checkbox_Moddepth_norm.setCheckState(False)
                self.dual_display_button.setChecked(False)
                self.currentglobal_result = False
                self.use_adaptive_kernel.setCheckState(False)
                self.GlobalAnalysis.setCheckState(False)
                # self.use_suppression_box.setCheckState(False)
                self.use_large_kernel.setCheckState(False)
                if t == 2:
                    initialize_var2(self)
                    (self.pc_spetrum2, self.pc_imag2,
                     self.time2) = read_input_var(self, Input, 2, True)
                elif t == 1:
                    initialize_var1(self)
                    (self.pc_spetrum1, self.pc_imag1,
                     self.time1) = read_input_var(self, Input, 1, True)
                print('Reading file was successful\n')
            except:
                print('Reading file was not successful\n')
                return
        if name.endswith('.DTA') or name.endswith('.dta'):
            try:
                f = open(name, 'rb')
                data_type = np.dtype('>f8')
                Input = np.fromfile(f, data_type)
                self.Checkbox_GlobalBg.setCheckState(False)
                self.Checkbox_Moddepth_norm.setCheckState(False)
                self.dual_display_button.setChecked(False)
                self.currentglobal_result = False
                self.use_adaptive_kernel.setCheckState(False)
                self.GlobalAnalysis.setCheckState(False)
                # self.use_suppression_box.setCheckState(False)
                self.use_large_kernel.setCheckState(False)
                if t == 2:
                    initialize_var2(self)
                    (self.pc_spetrum2, self.pc_imag2,
                     self.time2) = read_input_var(self, Input, 2, False, name)
                elif t == 1:
                    initialize_var1(self)
                    (self.pc_spetrum1, self.pc_imag1,
                     self.time1) = read_input_var(self, Input, 1, False, name)
                print('Reading file was successful\n')
            except:
                print('Reading file was not successful\n')
                return
        # Give information about the filename
        ind = name.rfind("/")
        if ind == -1:
            if t == 1:
                self.filename1 = name
            elif t == 2:
                self.filename2 = name
        else:
            if t == 1:
                self.filename1 = name[ind+1:]
            elif t == 2:
                self.filename2 = name[ind+1:]
        # Disable the imaginary part
        self.show_imaginary.setChecked(False)
        # GUESS MAXIMUM
        self.shift_zero_time(t)
        # Make all default settings (standard norm, APC, data information)
        if t == 2:
            self.setexists[1] = True
            timescale = self.time2[1]-self.time2[0]
            self.Timescaleset2.setText(str(timescale))
            self.zerotime2 = self.time2[np.argmax(self.pc_spetrum2)]
            (self.pc_spetrum22, self.pc_imag22, self.pc2_phase0order,
             self.pc2_phase1order) = AutomaticPc(self.pc_spetrum2,
                                                 self.pc_imag2, self.time2)
            (self.normalizedpc_spetrum2, self.normalizedpc_simag2,
             self.zerotime2) = normalize(self.pc_spetrum22, self.pc_imag22,
                                         self.time2, self.zerotime2, True,
                                         self.normfactor2)
            self.set_phase_correction(t)
        elif t == 1:
            self.setexists[0] = True
            timescale = self.time1[1]-self.time1[0]
            self.Timescaleset1.setText(str(timescale))
            self.zerotime1 = self.time1[np.argmax(self.pc_spetrum1)]
            (self.pc_spetrum11, self.pc_imag11, self.pc1_phase0order,
             self.pc1_phase1order) = AutomaticPc(self.pc_spetrum1,
                                                 self.pc_imag1, self.time1)
            (self.normalizedpc_spetrum1, self.normalizedpc_simag1,
             self.zerotime1) = normalize(self.pc_spetrum11, self.pc_imag11,
                                         self.time1, self.zerotime1, True,
                                         self.normfactor1)
            self.set_phase_correction(t)
        # Make default background correction
        if t == 1:
            self.bg_start1 = max(self.time1)*0.5
        elif t == 2:
            self.bg_start2 = max(self.time2)*0.5
        # Enable background function
        if t == 2:
            self.cutoff2 = max(self.time2)
            self.Enableset2.setChecked(True)
            self.Enableset1.setChecked(False)
            self.Zerotimebox.setValue(self.zerotime2)
            self.Bg_Start.setValue(self.bg_start2)
            self.Cutoffbox.setValue(self.cutoff2)
            self.set_bg_start(2)
            self.Multigaussian_Box.setChecked(False)
        elif t == 1:
            self.cutoff1 = max(self.time1)
            self.Enableset1.setChecked(True)
            self.Enableset2.setChecked(False)
            self.Zerotimebox.setValue(self.zerotime1)
            self.Cutoffbox.setValue(max(self.time1))
            self.Bg_Start.setValue(self.bg_start1)
            self.set_bg_start(1)
            self.Multigaussian_Box.setChecked(False)
        # Initialize the FFT
        self.initalize_TT(t)
        self.dialog.close()
        return

    def shift_zero_time(self, n):
        if n == 1:
            get_max = np.argmax(np.absolute(self.pc_spetrum1))
            timemax = self.time1[get_max]
            self.time1 = self.time1-timemax
        else:
            get_max = np.argmax(np.absolute(self.pc_spetrum2))
            timemax = self.time2[get_max]
            self.time2 = self.time2-timemax
        return


    # Initialize the Fouriertransformed and make label with filename
    def initalize_TT(self, n):
        if n == 2:
            try:
                self.Label_fsecond_paramset.setText(self.filename2)
            except:
                pass
        if n == 1:
            try:
                self.Label_first_paramset.setText(self.filename1)
            except:
                pass
        return

    # Define user normalization
    def set_cut(self, n):
        if not self.setexists[n-1]:
            self.Cutoffbox.setValue(0)
            return
        if n == 1:
            self.cutoff1 = self.Cutoffbox.value()
            self.set_zero_time(n)
            self.update_figset(n)
            self.lsq_fit1 = None
        elif n == 2:
            self.cutoff2 = self.Cutoffbox.value()
            self.set_zero_time(n)
            self.update_figset(n)
            self.lsq_fit2 = None
        return

    # Define user normalization
    def set_norm(self, n):
        if not self.setexists[n-1]:
            self.Nomalizebox.setValue(0)
            return
        if n == 1:
            self.normfactor1 = self.Nomalizebox.value()
            self.set_zero_time(n)
        elif n == 2:
            self.normfactor2 = self.Nomalizebox.value()
            self.set_zero_time(n)
        return

    # Switch between data-sets
    def which_dataset(self, w):
        if self.activeset == w:
            return
        elif not self.setexists[w-1]:
            return
        else:
            print("\nActive data-set = ", w)
            self.activeset = w
            if w == 1:
                self.currentglobal_result = False
                self.Thik_regul1_exist = False
                self.Zerotimebox.setValue(self.zerotime1)
                self.Bg_Start.setValue(self.bg_start1)
                self.Nomalizebox.setValue(self.normfactor1)
                self.supressing1 = False
                self.adaptive_kernel1 = False
                self.use_adaptive_kernel.setCheckState(False)
                # self.use_suppression_box.setCheckState(False)
                self.use_large_kernel.setCheckState(False)
                self.Bg_dimension.setValue(self.bg_dim1)
                self.L_Curve_numberBox.setValue(self.L_curve_number1)
                self.Cutoffbox.setValue(self.cutoff1)
            elif w == 2:
                self.currentglobal_result = False
                self.Thik_regul2_exist = False
                self.Zerotimebox.setValue(self.zerotime2)
                self.Bg_Start.setValue(self.bg_start2)
                self.Nomalizebox.setValue(self.normfactor2)
                self.supressing2 = False
                self.adaptive_kernel2 = False
                self.use_adaptive_kernel.setCheckState(False)
                # self.use_suppression_box.setCheckState(False)
                self.use_large_kernel.setCheckState(False)
                self.Bg_dimension.setValue(self.bg_dim2)
                self.L_Curve_numberBox.setValue(self.L_curve_number1)
                self.Cutoffbox.setValue(self.cutoff2)
            self.set_phase_correction(w)
            self.show_imaginary.setChecked(False)
        return

    # Set the new background start
    def set_bg_start(self, n):
        if not self.setexists[n-1]:
            self.Bg_Start.setValue(0)
            return
        # self.Checkbox_GlobalBg.setCheckState(False)
        # self.Checkbox_Moddepth_norm.setCheckState(False)
        if self.activeset == 1:
            self.bg_start1 = self.Bg_Start.value()
            if (self.bg_start1 < max(self.time1)-10 and self.bg_start1 >= 0):
                self.lsq_fit1 = None
                pass
            else:
                self.lsq_fit1 = None
                self.bg_start1 = max(self.time1)-10
                self.Bg_Start.setValue(self.bg_start1)
            if self.Fit_Background_dimension.isChecked():
                self.fit_background_dim(n)
            else:
                self.make_bg(n)
        elif n == 2 and self.activeset == 2:
            self.bg_start2 = self.Bg_Start.value()
            if (self.bg_start2 < max(self.time2)-10 and self.bg_start2 >= 0):
                self.lsq_fit2 = None
                pass
            else:
                self.lsq_fit2 = None
                self.bg_start2 = max(self.time2)-10
                self.Bg_Start.setValue(self.bg_start2)
            self.make_bg(n)
        if self.globalbg_fun_isOn:
            self.Checkbox_GlobalBg.setChecked(False)
            self.Checkbox_GlobalBg.setChecked(True)
            QApplication.processEvents()
        self.update_figset(n)
        return

    def fit_background_dim(self, n):
        if self.Fit_Background_dimension.isChecked():
            if not self.Warning_BG_dim_fit():
                self.Fit_Background_dimension.setChecked(False)
                self.make_bg(n)
                return
            if n == 1:
                result = bg_correction_fit_dim(self.normalizedpc_spetrum1,
                                               self.time1, self.bg_start1,
                                               self.bg_dim1, self.exclude_vol1,
                                               self.bg_param1[0],
                                               self.bg_param1[1])
                self.bg_param1 = (result[0], result[1])
                self.Bg_dimension.setValue(round(result[2], 2))
                self.make_bg(n)
            elif n == 2:
                result = bg_correction_fit_dim(self.normalizedpc_spetrum2,
                                               self.time2, self.bg_start2,
                                               self.bg_dim2, self.exclude_vol2,
                                               self.bg_param2[0],
                                               self.bg_param2[1])
                self.bg_param2 = (result[0], result[1])
                self.Bg_dimension.setValue(round(result[2], 2))
                self.make_bg(n)
            print("Fitted background dimension: "+str(round(result[2], 3)))
        return

    def Warning_BG_dim_fit(self):
        self.dialog10 = QDialog()
        self.dialog10.ui = ChildBGWarn()
        self.dialog10.ui.setupUi(self.dialog10)
        self.dialog10.ui.Continue_BGDIM_Button.clicked.connect(self.dialog10.accept)
        self.dialog10.ui.Cancel_BGDIM_Button_reject.clicked.connect(self.dialog10.reject)
        self.dialog10.show()
        if self.dialog10.exec_():
            boolean = True
            return boolean
        if self.dialog10.accept:
            boolean = False
            return boolean
        if self.dialog10.reject:
            boolean = True
            return boolean

    def form_fac(self):
        lsq_best = 1e10
        best_start = self.Bg_Start.value()
        if self.Form_factor_based_fit.isChecked():
            step = np.linspace(0.2, 0.8, 30)
            for i in range(0, 30):
                if self.activeset == 1:
                    bg_start = np.max(self.time1)*step[i]
                    self.bg_param1 = bg_correction(self.normalizedpc_spetrum1,
                                                   self.time1, bg_start,
                                                   self.bg_dim1,
                                                   self.exclude_vol1)
                    (self.bg_corrected1, self.bg_time1,
                     self.bg_fun1) = bg_subtraction(self.normalizedpc_spetrum1,
                                                    self.time1,
                                                    self.bg_param1,
                                                    self.zerotime1,
                                                    self.bg_dim1,
                                                    None, self.exclude_vol1)
                    lsq = form_fac_fit(self.bg_time1, self.bg_corrected1)
                elif self.activeset == 2:
                    bg_start = np.max(self.time2)*step[i]
                    self.bg_param2 = bg_correction(self.normalizedpc_spetrum2,
                                                   self.time2, bg_start,
                                                   self.bg_dim2,
                                                   self.exclude_vol2)
                    (self.bg_corrected2, self.bg_time2,
                     self.bg_fun2) = bg_subtraction(self.normalizedpc_spetrum2,
                                                    self.time2,
                                                    self.bg_param2,
                                                    self.zerotime2,
                                                    self.bg_dim2,
                                                    None, self.exclude_vol2)
                    lsq = form_fac_fit(self.bg_time2, self.bg_corrected2)
                if lsq < lsq_best:
                    lsq_best = lsq
                    best_start = bg_start
                else:
                    if i > 15:
                        break
        self.Bg_Start.setValue(best_start)
        return

    # Make new background correction
    def make_bg(self, n):
        if n == 1:
            self.overwrite_fit_res1 = False
            if self.globalbg_fun_isOn:
                self.bg_param1 = self.globalbg_fun
                self.bg_dim1 = self.bg_dim2
            else:
                self.bg_param1 = bg_correction(self.normalizedpc_spetrum1,
                                               self.time1, self.bg_start1,
                                               self.bg_dim1, self.exclude_vol1)
            (self.bg_corrected1, self.bg_time1,
             self.bg_fun1) = bg_subtraction(self.normalizedpc_spetrum1,
                                            self.time1, self.bg_param1,
                                            self.zerotime1, self.bg_dim1,
                                            None, self.exclude_vol1)
            self.Fourier1, self.FFreq1 = make_FT(self.bg_time1,
                                                 self.bg_corrected1)
        if n == 2:
            self.overwrite_fit_res2 = False
            if self.globalbg_fun_isOn:
                if len(self.bg_corrected2) > len(self.bg_corrected1):
                    self.bg_param2 = bg_correction(self.normalizedpc_spetrum2,
                                                   self.time2, self.bg_start2,
                                                   self.bg_dim2,
                                                   self.exclude_vol1)
                self.bg_param2 = self.globalbg_fun
                self.bg_dim2 = self.bg_dim1
            else:
                self.bg_param2 = bg_correction(self.normalizedpc_spetrum2,
                                               self.time2, self.bg_start2,
                                               self.bg_dim2, self.exclude_vol2)
            (self.bg_corrected2, self.bg_time2,
             self.bg_fun2) = bg_subtraction(self.normalizedpc_spetrum2,
                                            self.time2, self.bg_param2,
                                            self.zerotime2, self.bg_dim2, None,
                                            self.exclude_vol2)
            self.Fourier2, self.FFreq2 = make_FT(self.bg_time2,
                                                 self.bg_corrected2)
        self.GlobalAnalysis.setCheckState(False)
        str_tmp = "background-color: rgb(165, 181, 209)"
        self.ZoomFTScrollBar.setStyleSheet(str_tmp)
        self.ZoomFTScrollBar_2.setStyleSheet(str_tmp)
        self.ZoomFTScrollBar_3.setStyleSheet(str_tmp)
        QApplication.processEvents()
        return

    # Set user defined zero time
    def set_zero_time(self, n):
        if not self.setexists[n-1]:
            self.Zerotimebox.setValue(0)
            return
        if n == 2:
            self.zerotime2 = self.Zerotimebox.value()
            (self.normalizedpc_spetrum2, self.normalizedpc_simag2,
             self.zerotime2) = normalize(self.pc_spetrum22, self.pc_imag22,
                                         self.time2, self.zerotime2, True,
                                         self.normfactor2, False)
            self.Zerotimebox.setValue(self.zerotime2)
            if self.Checkbox_GlobalBg.isChecked() and self.globalmod_isOn:
                self.use_globalmod(self.Checkbox_Moddepth_norm)
            else:
                self.make_bg(n)
                self.update_figset(n)
        elif n == 1:
            self.zerotime1 = self.Zerotimebox.value()
            (self.normalizedpc_spetrum1, self.normalizedpc_simag1,
             self.zerotime1) = normalize(self.pc_spetrum11, self.pc_imag11,
                                         self.time1, self.zerotime1, True,
                                         self.normfactor1, False)
            self.Zerotimebox.setValue(self.zerotime1)
            if self.Checkbox_GlobalBg.isChecked() and self.globalmod_isOn:
                self.use_globalmod(self.Checkbox_Moddepth_norm)
            else:
                self.make_bg(n)
                self.update_figset(n)
        return

    # Switch on the global background correction
    def use_globalBG(self, global_bg_on):
        if not self.setexists[0] or not self.setexists[1]:
            self.Checkbox_GlobalBg.setCheckState(False)
            return
        self.show_imaginary.setChecked(False)
        if (global_bg_on.isChecked() and self.setexists[0] and
           self.setexists[1]):
            if max(self.time1) > max(self.time2):
                self.globalbg_fun = self.bg_param1
                self.exclude_vol2 = self.exclude_vol1
            else:
                self.globalbg_fun = self.bg_param2
                self.exclude_vol1 = self.exclude_vol2
            self.globalbg_fun_isOn = True
            print("\nGlobal background correction is switched on")
        elif global_bg_on.isChecked():
            self.globalbg_fun = None
            self.globalbg_fun_isOn = False
            self.Checkbox_GlobalBg.setCheckState(False)
        else:
            self.globalbg_fun = None
            self.globalbg_fun_isOn = False
            self.Checkbox_GlobalBg.setCheckState(False)
            print("\nGlobal background correction is switched off")
        self.make_bg(1)
        self.make_bg(2)
        if (self.dual_display_button.isChecked() and self.setexists[0] and
           self.setexists[1]):
            self.update_figset(1)
            self.update_figset(2)
        else:
            self.update_figset(self.activeset)
        return

    # Switch on the normalization of modulation depth
    def use_globalmod(self, global_mod_on):
        if not self.setexists[0] or not self.setexists[1]:
            self.Checkbox_Moddepth_norm.setCheckState(False)
            return
        self.show_imaginary.setChecked(False)
        if (global_mod_on.isChecked() and self.setexists[0] and
           self.setexists[1]):
            if max(self.time1) > max(self.time2):
                usedset = 1
            else:
                usedset = 2
            self.global_moddepth(True, usedset)
            self.globalmod_isOn = True
            print("\nNormalization of modulation depth is switched on")
        elif global_mod_on.isChecked():
            self.globalmod_isOn = False
            self.Checkbox_Moddepth_norm.setCheckState(False)
        else:
            self.Checkbox_Moddepth_norm.setCheckState(False)
            self.globalmod_isOn = False
            if (self.setexists[0] and self.setexists[1] and
               self.dual_display_button.isChecked()):
                self.set_zero_time(1)
                self.set_zero_time(2)
            else:
                self.set_zero_time(self.activeset)
            print("\nNormalization of modulation depth is switched off")
        self.make_bg(self.activeset)
        if (self.dual_display_button.isChecked() and self.setexists[0] and
           self.setexists[1]):
            self.update_figset(1)
            self.update_figset(2)
        else:
            self.update_figset(self.activeset)
        return

    # Define moddepth normalization
    def global_moddepth(self, boolean, usedset=1):
        if not boolean:
            self.set_zero_time(self.activeset)
        else:
            if usedset == 2:
                self.normalizedpc_spetrum1 = normalize_Mod(self.normalizedpc_spetrum1,
                                                           self.normalizedpc_spetrum2,
                                                           self.time1,
                                                           self.time2)
                self.normalizedpc_spetrum2 = self.normalizedpc_spetrum2
            elif usedset == 1:
                self.normalizedpc_spetrum2 = normalize_Mod(self.normalizedpc_spetrum2,
                                                           self.normalizedpc_spetrum1,
                                                           self.time2,
                                                           self.time1)
                self.normalizedpc_spetrum1 = self.normalizedpc_spetrum1
        self.make_bg(1)
        self.make_bg(2)
        if self.dual_display_button.isChecked():
            self.update_figset(1)
            self.update_figset(2)
        else:
            self.update_figset(self.activeset)
        return

    def enable_exclusiv_vol(self, n):
        if not self.setexists[self.activeset-1]:
            self.Excluded_volBox.setCheckState(False)
            return
        if self.Excluded_volBox.isChecked():
            print("\nUse approximation of exclude volume effect")
            if self.activeset == 1:
                self.exclude_vol1 = self.Bg_excluded_vol.value()
            elif self.activeset == 2:
                self.exclude_vol2 = self.Bg_excluded_vol.value()
        elif not self.Excluded_volBox.isChecked():
            print("\nUse approximation of exclude volume effect")
            if self.activeset == 1:
                self.exclude_vol1 = None
            elif self.activeset == 2:
                self.exclude_vol2 = None
        self.make_bg(self.activeset)
        self.update_figset(self.activeset)
        return

    # Useage of fractional dimension for excluded volume effects
    def exclude_vol(self, n):
        if n == 2:
            self.exclude_vol2 = self.Bg_excluded_vol.value()
        elif n == 1:
            self.exclude_vol1 = self.Bg_excluded_vol.value()
        if self.Excluded_volBox.isChecked():
            self.make_bg(self.activeset)
            self.update_figset(self.activeset)
        return

    # Show the values of automatic phase correction
    def set_phase_correction(self, n):
        if n == 1:
            self.AutomaticPc0order.setText(str(round(self.pc1_phase0order, 1)))
        elif n == 2:
            self.AutomaticPc0order.setText(str(round(self.pc2_phase0order, 1)))
        return

    # Show imaginary part of the time trace
    def show_imag(self, n):
        try:
            if not self.show_imaginary.isChecked():
                self.update_figset(n)
            elif self.show_imaginary.isChecked():
                self.dual_display_button.setChecked(False)
                if n == 1:
                    figure_handler(self, self.time1,
                                   self.normalizedpc_simag1, 3)
                elif n == 2:
                    figure_handler(self, self.time2,
                                   self.normalizedpc_simag2, 3)
            return
        except:
            self.show_imaginary.setChecked(False)
            return

    # User defined bg-dimension
    def set_bg_dim(self, n):
        if not self.setexists[n-1]:
            self.Bg_dimension.setValue(3)
            return
        if n == 1:
            self.bg_dim1 = self.Bg_dimension.value()
        if n == 2:
            self.bg_dim2 = self.Bg_dimension.value()
        self.make_bg(self.activeset)
        self.update_figset(self.activeset)
        return

    # Update figureset
    def update_figset(self, n):
        if not self.setexists[n-1]:
            return
        if self.dual_display_button.isChecked():
            self.dual_disp(n)
        else:
            if n == 1:
                figure_handler(self, self.time1, self.normalizedpc_spetrum1,
                               3, self.cutoff1, self.bg_time1, self.bg_fun1,
                               self.zerotime1)
                figure_handler(self, self.bg_time1, self.bg_corrected1, 1,
                               self.cutoff1)
                figure_handler(self, self.FFreq1, self.Fourier1, 2)
            elif n == 2:
                figure_handler(self, self.time2, self.normalizedpc_spetrum2, 3,
                               self.cutoff2, self.bg_time2, self.bg_fun2,
                               self.zerotime2)
                figure_handler(self, self.bg_time2, self.bg_corrected2, 1,
                               self.cutoff2)
                figure_handler(self, self.FFreq2, self.Fourier2, 2)
            return

    # Set global analysis
    def set_global_analysis(self, boolean):
        if (boolean.isChecked() and self.lsq_fit1 is not None and
           self.lsq_fit2 is not None):
            self.globalanaisOn = True
            self.fitweight = (np.sqrt(self.lsq_fit1/self.lsq_fit2) *
                              np.sqrt((len(self.bg_time2)/len(self.bg_time1))))
            str_tmp = "\nGlobal analysis is switched on\n\nWeighting factor = "
            print(str_tmp, round(self.fitweight, 4))
        elif boolean.isChecked():
            self.globalanaisOn = False
            str_tmp = ("\nBoth singel time traces need to be analyzed before" +
                       " global analysis can be carried out!\n")
            print(str_tmp)
            self.GlobalAnalysis.setCheckState(False)
        else:
            self.globalanaisOn = False
            self.GlobalAnalysis.setCheckState(False)
            print("\nGlobal analysis is switched off")
        return

    # Enable dual display
    def dual_disp(self, n):
        if (self.dual_display_button.isChecked() and self.setexists[0] and
           self.setexists[1]):
            figure_handler_dual_disp(self, self.time1,
                                     self.normalizedpc_spetrum1, self.time2,
                                     self.normalizedpc_spetrum2,
                                     3, self.cutoff1, self.cutoff2,
                                     self.bg_time1, self.bg_fun1,
                                     self.bg_time2, self.bg_fun2)
            figure_handler_dual_disp(self, self.bg_time1, self.bg_corrected1,
                                     self.bg_time2, self.bg_corrected2, 1,
                                     self.cutoff1, self.cutoff2)
            figure_handler_dual_disp(self, self.FFreq1, self.Fourier1,
                                     self.FFreq2, self.Fourier2, 2)
            self.show_imaginary.setChecked(False)
        else:
            self.dual_display_button.setChecked(False)
            if self.setexists[self.activeset-1]:
                self.update_figset(n)
                self.show_imaginary.setChecked(False)
        return

    # FITTING AND REGULARIZATION
    def fit_button_TR(self, n):
        self.fitting_algorithm = 1
        self.regularziationisoN = False
        self.Multigaussian_Box.setChecked(True)
        return

    def fit_button_Simplex(self, n):
        self.fitting_algorithm = 2
        self.regularziationisoN = False
        self.Multigaussian_Box.setChecked(True)
        return

    def fit_button_Powell(self, n):
        self.fitting_algorithm = 3
        self.regularziationisoN = False
        self.Multigaussian_Box.setChecked(True)
        return

    def fit_button_CG(self, n):
        self.fitting_algorithm = 4
        self.regularziationisoN = False
        self.Multigaussian_Box.setChecked(True)
        return

    def fit_button_STR(self, n):
        self.fitting_algorithm = 5
        self.regularziationisoN = False
        self.Multigaussian_Box.setChecked(True)
        return

    def fit_button_DiffEvol(self, n):
        self.fitting_algorithm = 6
        self.regularziationisoN = False
        self.Multigaussian_Box.setChecked(True)
        return

    def button_Thikonov(self, n):
        self.regularziationisoN = True
        self.reg_method = 1
        self.current_result_is_reg = False
        self.Multigaussian_Box.setChecked(False)
        try:
            self.dialog4.close()
        except:
            pass
        return

    def button_DTSVD(self, n):
        self.regularziationisoN = True
        self.reg_method = 2
        self.current_result_is_reg = False
        self.Multigaussian_Box.setChecked(False)
        try:
            self.dialog4.close()
        except:
            pass
        return

    def button_MaxEntr(self, n):
        self.regularziationisoN = True
        self.reg_method = 3
        self.current_result_is_reg = False
        self.Multigaussian_Box.setChecked(False)
        try:
            self.dialog4.close()
        except:
            pass
        return

    def set_fit_model_mult(self, boolean):
        if boolean.isChecked():
            self.multigaussian1 = True
            self.multigaussian2 = True
            self.multigaussian_glo = True
            if self.regularziationisoN:
                self.TR_Rbutton.setChecked(True)
                self.regularziationisoN = False
        else:
            self.multigaussian1 = False
            self.multigaussian2 = False
            self.multigaussian_glo = False
            self.regularziationisoN = True
            self.thikonovbutton.setChecked(True)
        return

    def set_fit_model_tri(self, boolean):
        pass

    def show_timer_label(self):
        self.dialog1 = QDialog()
        self.dialog1.setWindowTitle("Calculation in progress")
        str_tmp = ("This may take from a few seconds up to several minutes." +
                   "\n\n\t\tPlease be patient.\n")
        self.label1 = QLabel(str_tmp)
        self.label1.setStyleSheet("font-size: 15px")
        self.dialog1.layout = QGridLayout(self.dialog1)
        self.dialog1.layout.addWidget(self.label1, 0, 0, 1, 0)
        self.dialog1.setStyleSheet("background-color:rgb(165, 181, 209)")
        self.dialog1.show()
        start = time.time()
        while time.time() - start < 0.05:
            QApplication.processEvents()
        time.sleep(0.01)
        return

    def close_timer_label(self):
        self.dialog1.accept()
        return

    def fit_button_pressed(self, n):
        if not self.setexists[0] and not self.setexists[1]:
            print("\nNo files loaded yet\n")
            return
        # Disable the scroll bar
        str_tmp = "background-color:rgb(188, 198, 207)"
        self.ZoomFTScrollBar.setStyleSheet(str_tmp)
        self.ZoomFTScrollBar_2.setStyleSheet(str_tmp)
        self.ZoomFTScrollBar_3.setStyleSheet(str_tmp)
        # Disable imaginary illustration
        self.show_imaginary.setChecked(False)
        self.dual_display_button.setChecked(False)
        if not self.globalanaisOn:
            self.currentglobal_result = False
        elif self.globalanaisOn:
            self.global_L_curve_num = 5
            self.currentglobal_result = True
            if self.activeset == 1:
                self.supressingglob = self.supressing1
                self.supressingstartglo = self.supressingstart1
                self.supressingendglo = self.supressingend1
                self.global_adaptive = self.adaptive_kernel1
                self.global_large_kernel1 = self.large_kernel1
            elif self.activeset == 2:
                self.supressingglob = self.supressing2
                self.supressingstartglo = self.supressingstart2
                self.supressingendglo = self.supressingend2
                self.global_adaptive = self.adaptive_kernel2
                self.global_large_kernel1 = self.large_kernel2
        if n == 1:
            self.overwrite_fit_res1 = True
            self.redline1 = abs(np.cbrt(max(self.bg_time1)*1e-3*52.04)*0.9)
        elif n == 2:
            self.overwrite_fit_res2 = True
            self.redline2 = abs(np.cbrt(max(self.bg_time2)*1e-3*52.04)*0.9)
        if self.globalanaisOn:
            if self.redline2 > self.redline1:
                self.redline_global = self.redline2
            else:
                self.redline_global = self.redline1
        if self.regularziationisoN:
            self.L_curve_number1 = 5
            self.L_curve_number2 = 5
        try:
            self.plainTextEdit.clear()
            QApplication.processEvents()
        except:
            pass
        print("\nCalculation starts...")
        print("This may take from a few seconds up to several minutes.\n")
        sys.stdout.flush()
        self.show_timer_label()
        start = time.time()
        while time.time() - start < 0.04:
            QApplication.processEvents()
        start = time.time()
        # Define maximum of reasonable analysis.
        if not self.regularziationisoN:
            for i in range(0, 2):
                self.multigaussian1 = i
                self.multigaussian2 = i
                self.multigaussian_glo = i
                if not self.globalanaisOn:
                    if n == 1:
                        # Induce Cut if enabled
                        if self.cutoff1 < max(self.bg_time1):
                            self.bg_time1_cut = self.bg_time1[self.bg_time1 <= self.cutoff1]
                            self.bg_corrected1_cut = self.bg_corrected1[0:len(self.bg_time1_cut)]
                        else:
                            self.bg_time1_cut = self.bg_time1
                            self.bg_corrected1_cut = self.bg_corrected1
                        # Decide for fitting routine
                        if (self.fitting_algorithm == 1 or
                           self.fitting_algorithm == 5):
                            (self.dist_1, self.coef1,
                             self.sigma1) = trust_region_reflective(self.bg_time1_cut,
                                                                    self.bg_corrected1_cut,
                                                                    self.bg_param1[0],
                                                                    self.multigaussian1,
                                                                    self.fitting_algorithm,
                                                                    None, None,
                                                                    0, False,
                                                                    self.supressing1,
                                                                    self.supressingstart1,
                                                                    self.supressingend1)
                        else:
                            (self.dist_1, self.coef1,
                             self.sigma1) = objective_min(self.bg_time1_cut,
                                                          self.bg_corrected1_cut,
                                                          self.bg_param1[0],
                                                          self.fitting_algorithm,
                                                          self.multigaussian1,
                                                          None, None, 0, False,
                                                          self.supressing1,
                                                          self.supressingstart1,
                                                          self.supressingend1)
                        self.process_fit_results()
                        len_var = (len(self.bg_corrected1_cut)-len(np.append(
                                   np.append(self.dist_1, self.coef1), self.sigma1)))
                        if i == 0:
                            len_var_tmp = len_var
                            lsq_fit1_tmp = self.lsq_fit1
                            dist_1 = self.dist_1
                            coef1 = self.coef1
                            sigma1 = self.sigma1
                        else:
                            p_value = F_test_model_comp(lsq_fit1_tmp,
                                                        self.lsq_fit1,
                                                        len_var_tmp, len_var)
                            print("\nModel Evalutation. 4Gaussians/5Gaussians")
                            print("p-value: "+str(p_value))
                            if p_value > 0.04:
                                self.multigaussian1 = False
                                self.dist_1 = dist_1
                                self.coef1 = coef1
                                self.sigma1 = sigma1
                                print("4 Gaussian model preferred")
                            else:
                                self.multigaussian1 = True
                                print("5 Gaussian model preferred")
                    elif n == 2:
                        # Induce Cut if enabled
                        if self.cutoff2 < max(self.bg_time2):
                            self.bg_time2_cut = self.bg_time2[self.bg_time2 <= self.cutoff2]
                            self.bg_corrected2_cut = self.bg_corrected2[0:len(self.bg_time2_cut)]
                        else:
                            self.bg_time2_cut = self.bg_time2
                            self.bg_corrected2_cut = self.bg_corrected2
                        # Decisions for fitting routines
                        if (self.fitting_algorithm == 1 or
                           self.fitting_algorithm == 5):
                            (self.dist_2, self.coef2,
                             self.sigma2) = trust_region_reflective(self.bg_time2_cut,
                                                                    self.bg_corrected2_cut,
                                                                    self.bg_param2[0],
                                                                    self.multigaussian2,
                                                                    self.fitting_algorithm,
                                                                    None, None,
                                                                    0, False,
                                                                    self.supressing2,
                                                                    self.supressingstart2,
                                                                    self.supressingend2)
                        else:
                            (self.dist_2, self.coef2,
                             self.sigma2) = objective_min(self.bg_time2_cut,
                                                          self.bg_corrected2_cut,
                                                          self.bg_param2[0],
                                                          self.fitting_algorithm,
                                                          self.multigaussian2,
                                                          None, None, 0, False,
                                                          self.supressing2,
                                                          self.supressingstart2,
                                                          self.supressingend2)
                        self.process_fit_results()
                        len_var = (len(self.bg_corrected2_cut)-len(np.append(
                                   np.append(self.dist_2,self.coef2),self.sigma2)))
                        if i == 0:
                            len_var_tmp = len_var
                            lsq_fit2_tmp = self.lsq_fit2
                            dist_2 = self.dist_2
                            coef2 = self.coef2
                            sigma2 = self.sigma2
                        else:
                            p_value = F_test_model_comp(lsq_fit2_tmp,
                                                        self.lsq_fit2,
                                                        len_var_tmp, len_var)
                            print("\nModel Evalutation. 4Gaussians/5Gaussians")
                            print("p-value: "+str(p_value))
                            if p_value > 0.04:
                                self.multigaussian2 = False
                                self.dist_2 = dist_2
                                self.coef2 = coef2
                                self.sigma2 = sigma2
                                print("4 Gaussian model preferred")
                            else:
                                self.multigaussian2 = True
                                print("5 Gaussian model preferred")
                    self.process_fit_results()

                elif self.globalanaisOn:
                    # Induce Cut if enabled
                    if self.cutoff1 < max(self.bg_time1):
                        self.bg_time1_cut = self.bg_time1[self.bg_time1 <= self.cutoff1]
                        self.bg_corrected1_cut = self.bg_corrected1[0:len(self.bg_time1_cut)]
                    else:
                        self.bg_time1_cut = self.bg_time1
                        self.bg_corrected1_cut = self.bg_corrected1
                    # Induce Cut if enabled
                    if self.cutoff2 < max(self.bg_time2):
                        self.bg_time2_cut = self.bg_time2[self.bg_time2 <= self.cutoff2]
                        self.bg_corrected2_cut = self.bg_corrected2[0:len(self.bg_time2_cut)]
                    else:
                        self.bg_time2_cut = self.bg_time2
                        self.bg_corrected2_cut = self.bg_corrected2
                    if (self.fitting_algorithm == 1 or
                       self.fitting_algorithm == 5):
                        (self.Globaldist, self.Globalcoef,
                         self.Globalsigma) = trust_region_reflective(self.bg_time1_cut,
                                                                     self.bg_corrected1_cut,
                                                                     self.bg_param1[0],
                                                                     self.multigaussian_glo,
                                                                     self.fitting_algorithm,
                                                                     self.bg_time2_cut,
                                                                     self.bg_corrected2_cut,
                                                                     self.fitweight,
                                                                     self.globalanaisOn,
                                                                     self.supressingglob,
                                                                     self.supressingstartglo,
                                                                     self.supressingendglo)
                    else:
                        (self.Globaldist, self.Globalcoef,
                         self.Globalsigma) = objective_min(self.bg_time1_cut,
                                                           self.bg_corrected1_cut,
                                                           self.bg_param1[0],
                                                           self.fitting_algorithm,
                                                           self.multigaussian_glo,
                                                           self.bg_time2_cut,
                                                           self.bg_corrected2_cut,
                                                           self.fitweight,
                                                           self.globalanaisOn,
                                                           self.supressingglob,
                                                           self.supressingstartglo,
                                                           self.supressingendglo)
                    self.process_globalfit_results()
                    lsq_fit = (lsq_deviation(self.bg_time1_cut, self.GlobalFit1) +
                               lsq_deviation(self.bg_time2_cut,self.GlobalFit2))
                    len_var = (len(self.bg_corrected2_cut) -
                               len(np.append(np.append(self.Globaldist,
                                                       self.Globalcoef),
                                                       self.Globalsigma)))
                    if i == 0:
                        len_var_tmp = len_var
                        lsq_fit_tmp = lsq_fit
                        dist = self.Globaldist
                        coef = self.Globalcoef
                        sigma = self.Globalsigma
                    else:
                        p_value = F_test_model_comp(lsq_fit_tmp, lsq_fit,
                                                    len_var_tmp, len_var)
                        print("\nModel Evalutation. 4Gaussians/5Gaussians")
                        print("p-value: "+str(p_value))
                        if p_value > 0.04:
                            self.multigaussian_glo = False
                            self.Globaldist = dist
                            self.Globalcoef = coef
                            self.Globalsigma = sigma
                            print("4 Gaussian model preferred")
                        else:
                            self.multigaussian_glo = True
                            print("5 Gaussian model preferred")
                    self.process_globalfit_results()
                self.current_result_is_reg = False
                QApplication.setOverrideCursor(QtCore.Qt.ArrowCursor)
                QApplication.processEvents()
        elif self.regularziationisoN:
            #try:
                if not self.globalanaisOn:
                    if n == 1:
                        # Induce Cut if enabled
                        if self.cutoff1 < max(self.bg_time1):
                            self.bg_time1_cut = self.bg_time1[self.bg_time1 <= self.cutoff1]
                            self.bg_corrected1_cut = self.bg_corrected1[0:len(self.bg_time1_cut)]
                        else:
                            self.bg_time1_cut = self.bg_time1
                            self.bg_corrected1_cut = self.bg_corrected1
                        (self.r1_reg, self.Pr1_reg, self.reg1, self.Lcurvex1,
                         self.Lcurvey1, self.alpha_cross1,
                         self.alpha_aic1) = regularization(self.bg_time1_cut,
                                                           self.bg_corrected1_cut,
                                                           self.reg_method,
                                                           True,
                                                           self.L_curve_number1,
                                                           False, None, None,
                                                           None,
                                                           self.supressing1,
                                                           self.supressingstart1,
                                                           self.supressingend1,
                                                           self.adaptive_kernel1,
                                                           self.large_kernel1)
                        self.Thik_regul1_exist = True
                        self.run_autocorr(self.reg1, self.bg_corrected1_cut)
                        self.run_crossval(self.activeset)
                        self.L_curve_number1 = self.L_Curve_numberBox.value()
                    elif n == 2:
                        # Induce Cut if enabled
                        if self.cutoff2 < max(self.bg_time2):
                            self.bg_time2_cut = self.bg_time2[self.bg_time2 <= self.cutoff2]
                            self.bg_corrected2_cut = self.bg_corrected2[0:len(self.bg_time2_cut)]
                        else:
                            self.bg_time2_cut = self.bg_time2
                            self.bg_corrected2_cut = self.bg_corrected2
                        (self.r2_reg, self.Pr2_reg, self.reg2, self.Lcurvex2,
                         self.Lcurvey2, self.alpha_cross2,
                         self.alpha_aic2) = regularization(self.bg_time2_cut,
                                                           self.bg_corrected2_cut,
                                                           self.reg_method,
                                                           True,
                                                           self.L_curve_number2,
                                                           False, None, None,
                                                           None,
                                                           self.supressing2,
                                                           self.supressingstart2,
                                                           self.supressingend2,
                                                           self.adaptive_kernel2,
                                                           self.large_kernel2)
                        self.Thik_regul2_exist = True
                        self.run_autocorr(self.reg2, self.bg_corrected2_cut)
                        self.run_crossval(self.activeset)
                        self.L_curve_number2 = self.L_Curve_numberBox.value()
                    self.process_reg_results(n)
                elif self.globalanaisOn:
                    # Induce Cut if enabled
                    if self.cutoff1 < max(self.bg_time1):
                        self.bg_time1_cut = self.bg_time1[self.bg_time1 <= self.cutoff1]
                        self.bg_corrected1_cut = self.bg_corrected1[0:len(self.bg_time1_cut)]
                    else:
                        self.bg_time1_cut = self.bg_time1
                        self.bg_corrected1_cut = self.bg_corrected1
                    #Induce Cut if enabled
                    if self.cutoff2 < max(self.bg_time2):
                        self.bg_time2_cut = self.bg_time2[self.bg_time2 <= self.cutoff2]
                        self.bg_corrected2_cut = self.bg_corrected2[0:len(self.bg_time2_cut)]
                    else:
                        self.bg_time2_cut = self.bg_time2
                        self.bg_corrected2_cut = self.bg_corrected2
                    (self.r_reg_global, self.Pr_reg_global, self.reg1_global,
                     self.reg2_global, self.Lcurvex_global,
                     self.Lcurvey_global, self.alpha_cross_glo,
                     self.alpha_aic_glo) = regularization(self.bg_time1_cut,
                                                          self.bg_corrected1_cut,
                                                          self.reg_method,
                                                          True,
                                                          self.global_L_curve_num,
                                                          True,
                                                          self.bg_time2_cut,
                                                          self.bg_corrected2_cut,
                                                          self.fitweight,
                                                          self.supressingglob,
                                                          self.supressingstartglo,
                                                          self.supressingendglo,
                                                          self.global_adaptive,
                                                          self.global_large_kernel1)
                    self.run_crossval(self.activeset, True)
                    self.global_L_curve_num = self.L_Curve_numberBox.value()
                    self.process_globalreg_results()
                self.current_result_is_reg = True
                QApplication.processEvents()
                QApplication.setOverrideCursor(QtCore.Qt.ArrowCursor)
            #except:
            #    print('\nAN error occured. No regularization possible\n')
        QApplication.processEvents()
        self.close_timer_label()
        # sys.exit(self.dialog1.exec_())
        eltime = (time.time()-start)
        print("Elapsed time: "+str(round(eltime, 4))+" s")
        time.sleep(0.02)
        QApplication.processEvents()
        print("\n")
        return

    def run_crossval(self, n, globalana=False):
        try:
            if n == 1:
                alpha = self.alpha_cross1
                alpha2 = self.alpha_aic1
            else:
                alpha = self.alpha_cross2
                alpha2 = self.alpha_aic2
            if globalana:
                alpha = self.alpha_cross_glo
                alpha2 = self.alpha_aic_glo
            str_tmp = ("\nGerneralized cross validation recommends " +
                       "a L-curve value of ")
            print(str_tmp + str(np.argmin(alpha)+1))
            self.L_Curve_numberBox.setValue(np.argmin(alpha)+1)
            try:
                l_val = np.linspace(1, 20, 20)
                grad1 = np.gradient(alpha)
                spl = interpolate.splrep(l_val, grad1, k=3)
                kt = interpolate.sproot(spl, mest=1)
                str_tmp = ("Interpolated optimal L-curve value according " +
                           "to generalized cross validation: ")
                print(str_tmp + str(round(kt[0], 2)))
            except:
                str_tmp = ("Interpolated evaluation of the L-curve value " +
                           "according to generalized cross validation " +
                           "evaluation failed")
                print(str_tmp)
            try:
                grad2 = np.gradient(alpha2)
                spl = interpolate.splrep(l_val, grad2, k=3)
                kt2 = interpolate.sproot(spl, mest=1)
                str_tmp = ("Interpolated optimal  L-curve value according to" +
                           " the AIC criterion: ")
                print(str_tmp + str(round(kt2[0], 2))+"\n")
            except:
                str_tmp = ("Interpolated evaluation of the L-curve value " +
                           "according to the AIC criterion failed\n")
                print(str_tmp)
        except:
            print("Gerneralized cross validation failed!")
            self.L_Curve_numberBox.setValue(10)
        return

    def Change_L_Curve(self, n):
        if not self.current_result_is_reg:
            return
        if self.globalanaisOn:
            return
        if not self.L_autocorr:
            self.L_autocorr = True
        else:
            self.L_autocorr = False
        if self.lsq_fit1 is None and self.activeset == 1:
            return
        if self.lsq_fit2 is None and self.activeset == 2:
            return
        self.process_reg_results(n)
        return

    def run_autocorr(self, fit, data):
        try:
            reffit = fit[:, 0]-data
            averagevalue = len(reffit)//100
            if averagevalue < 2:
                averagevalue = 2
            if averagevalue > 4:
                averagevalue = 4
            rmax = np.argmax(reffit)
            reffit[rmax] = 0
            autocorrref = np.correlate(reffit, reffit, mode='same')
            rmax = np.argmax(autocorrref)
            autocorrref[rmax] = 0
            autocors = np.zeros((len(fit[:, 0]), (len(fit[0, :])+1),))
            autocorrref = gaussian_filter(autocorrref, sigma=4)
            autocorrref = autocorrref
            autocors[:, 0] = autocorrref
            significance_vec = np.zeros(len(fit[0, :])+1)
            for i in range(1, len(fit[0, :])+1):
                if i < len(fit[0, :]):
                    auto_init = fit[:, i]-data
                else:
                    auto_init = data
                autocorr = np.correlate(auto_init, auto_init, mode='same')
                rmax = np.argmax(autocorr)
                autocorr[rmax] = 0
                autocorr = gaussian_filter(autocorr, sigma=4)
                autocorr = autocorr-autocorrref
                autocorr = autocorr-np.mean(autocorr)
                autocorr = np.sqrt(autocorr**2)
                autocors[:, i] = autocorr
                significance_vec[i] = np.std(autocorr)
            significance_vec[0] = significance_vec[1]
            significance_vec_tmp = significance_vec
            significance_vec = significance_vec/max(significance_vec)
            l = np.linspace(1, len(significance_vec), len(significance_vec))
            significance_vec = significance_vec_tmp
            significance_vec = abs(significance_vec/max(significance_vec))+1e-9
            if self.activeset == 1:
                self.Lcurvex_autocorr1 = l[0:-1]
                self.Lcurvey_autocorr1 = significance_vec[0:-1]
            else:
                self.Lcurvex_autocorr2 = l[0:-1]
                self.Lcurvey_autocorr2 = significance_vec[0:-1]
        except:
            print("Algorithmic regularization parameter determination failed")
        return

    def Change_Max_area_norm(self, n):
        if not self.normalize_to_maximum:
            self.normalize_to_maximum = True
        else:
            self.normalize_to_maximum = False
        if self.lsq_fit1 is None and self.activeset == 1:
            return
        if self.lsq_fit2 is None and self.activeset == 2:
            return
        if self.regularziationisoN:
            self.process_reg_results(n)
        else:
            self.figure_update_fit(n)
        return

    # Change current state of the L-curve number
    def L_curve(self, n):
        if self.currentglobal_result:
            if len(self.reg1_global) <= 1:
                self.L_Curve_numberBox.setValue(8)
                return
            else:
                self.global_L_curve_num = self.L_Curve_numberBox.value()
                self.process_globalreg_results()
        else:
            if n == 1 and self.activeset == 1:
                if self.Thik_regul1_exist and self.overwrite_fit_res1:
                    self.L_curve_number1 = self.L_Curve_numberBox.value()
                    self.process_reg_results(n)
                else:
                    self.L_Curve_numberBox.setValue(5)
                    return
            elif n == 2 and self.activeset == 2:
                if self.Thik_regul2_exist and self.overwrite_fit_res2:
                    self.L_curve_number2 = self.L_Curve_numberBox.value()
                    self.process_reg_results(n)
                else:
                    self.L_Curve_numberBox.setValue(5)
                    return
        QApplication.setOverrideCursor(QtCore.Qt.ArrowCursor)
        QApplication.processEvents()
        return

    # Process fit results (fill the dictionary)
    def process_fit_results(self):
        self.save_glob_fit = False
        if self.activeset == 1:
            self.Pr_1, self.distance_1 = make_distance_dist(self.dist_1,
                                                            self.coef1,
                                                            self.sigma1,
                                                            self.multigaussian1)
            self.Fourier1, self.FFreq1 = make_FT(self.bg_time1,
                                                 self.bg_corrected1)
            self.Fit1 = final_PELDOR_Calculation(self.bg_time1_cut,
                                                 self.bg_param1[0],
                                                 self.dist_1,
                                                 self.coef1,
                                                 self.sigma1,
                                                 self.multigaussian1)
            self.FourierFit1, self.FFreq1 = make_FT(self.bg_time1_cut,
                                                    self.Fit1)
            self.lsq_fit1 = lsq_deviation(self.bg_corrected1_cut, self.Fit1)
            self.output_results1 = (1, self.dist_1, self.coef1, self.sigma1,
                                    self.bg_time1_cut, self.bg_corrected1_cut,
                                    self.bg_param1[0], self.fitting_algorithm,
                                    self.multigaussian1, self.zerotime1,
                                    self.bg_start1, self.normfactor1,
                                    self.lsq_fit1, self.filename1, self.bg_dim1,
                                    self.globalbg_fun_isOn, self.globalmod_isOn,
                                    self.bg_param1, self.Fit1,
                                    self.Pr_1, self.distance_1,
                                    self.L_curve_number1, self.reg_method,
                                    self.supressing1, self.supressingstart1,
                                    self.supressingend1, self.bg_time1)
            self.residual1 = self.Fit1-self.bg_corrected1_cut
        elif self.activeset == 2:
            self.Pr_2, self.distance_2 = make_distance_dist(self.dist_2,
                                                            self.coef2,
                                                            self.sigma2,
                                                            self.multigaussian2)
            self.Fourier2, self.FFreq2 = make_FT(self.bg_time2,
                                                 self.bg_corrected2)
            self.Fit2 = final_PELDOR_Calculation(self.bg_time2_cut,
                                                 self.bg_param2[0],
                                                 self.dist_2, self.coef2,
                                                 self.sigma2,
                                                 self.multigaussian2)
            self.FourierFit2, self.FFreq2 = make_FT(self.bg_time2, self.Fit2)
            self.lsq_fit2 = lsq_deviation(self.bg_corrected2_cut, self.Fit2)
            self.output_results2 = (1, self.dist_2, self.coef2, self.sigma2,
                                    self.bg_time2_cut, self.bg_corrected2_cut,
                                    self.bg_param2[0], self.fitting_algorithm,
                                    self.multigaussian2, self.zerotime2,
                                    self.bg_start2, self.normfactor2,
                                    self.lsq_fit2, self.filename2,
                                    self.bg_dim2, self.globalbg_fun_isOn,
                                    self.globalmod_isOn, self.bg_param2,
                                    self.Fit2, self.Pr_2,
                                    self.distance_2, self.L_curve_number2,
                                    self.reg_method, self.supressing2,
                                    self.supressingstart2, self.supressingend2,
                                    self.bg_time2)
            self.residual2 = self.Fit2-self.bg_corrected2_cut
        self.figure_update_fit(self.activeset)
        self.detach_lsq(self.activeset, False)
        return

    # Process global fitting results (fill the dictionary)
    def process_globalfit_results(self):
        self.GlobalPr, self.Globaldistance = make_distance_dist(self.Globaldist,
                                                                self.Globalcoef,
                                                                self.Globalsigma,
                                                                self.multigaussian_glo)
        self.GlobalFit1 = final_PELDOR_Calculation(self.bg_time1_cut,
                                                   self.bg_param1[0],
                                                   self.Globaldist,
                                                   self.Globalcoef,
                                                   self.Globalsigma,
                                                   self.multigaussian_glo)
        self.GlobalFit2 = final_PELDOR_Calculation(self.bg_time2_cut,
                                                   self.bg_param2[0],
                                                   self.Globaldist,
                                                   self.Globalcoef,
                                                   self.Globalsigma,
                                                   self.multigaussian_glo)
        self.GlobalFourier1, self.GlobalFFreq1 = make_FT(self.bg_time1,
                                                         self.GlobalFit1)
        self.GlobalFourier2, self.GlobalFFreq2 = make_FT(self.bg_time2,
                                                         self.GlobalFit2)
        self.global_output_results = (1, self.Globaldist, self.Globalcoef,
                                      self.Globalsigma, self.bg_time1_cut,
                                      self.bg_corrected1_cut,
                                      self.bg_time2_cut,
                                      self.bg_corrected2_cut,
                                      self.fitting_algorithm,
                                      self.multigaussian2, self.filename1,
                                      self.filename2, self.GlobalFit1,
                                      self.GlobalFit2, self.GlobalPr,
                                      self.Globaldistance,
                                      self.L_curve_number2, self.reg_method,
                                      self.fitweight, self.supressingglob,
                                      self.supressingstartglo,
                                      self.supressingendglo)
        self.figure_update_globalfit()
        self.residual_global1 = self.GlobalFit1-self.bg_corrected1_cut
        self.residual_global2 = self.GlobalFit2-self.bg_corrected2_cut
        self.save_glob_fit = True
        self.detach_lsq(self.activeset, False)
        return

    # Process regularization results (fill the dict)
    def process_reg_results(self, n, verbose=False):
        self.save_glob_fit = False
        if n == 1 and self.activeset == 1:
            figure_handler_reg(self, self.bg_time1_cut, self.bg_corrected1_cut,
                               3, self.redline1,
                               self.reg1[:, self.L_curve_number1-1])
            figure_handler_reg(self, self.r1_reg,
                               self.Pr1_reg[:, self.L_curve_number1-1], 1,
                               self.redline1)
            if self.L_autocorr:
                x = self.Lcurvex_autocorr1
                y = self.Lcurvey_autocorr1
            else:
                x = self.Lcurvex1
                y = self.Lcurvey1
            figure_handler_reg(self, x, y, 2, self.redline1,
                               self.L_curve_number1, self.Lcurvex_autocorr1,
                               self.Lcurvey_autocorr1)
            self.residual1 = (self.reg1[:, self.L_curve_number1-1] -
                              self.bg_corrected1_cut)
            self.lsq_fit1 = lsq_deviation(self.bg_corrected1_cut,
                                          self.reg1[:, self.L_curve_number1-1])
            if verbose:
                print("L-curve number = ", self.L_curve_number1,
                      "\nLeast-squares = ", self.lsq_fit1, "\n")
            self.output_results1 = (0, self.dist_1, self.coef1, self.sigma1,
                                    self.bg_time1_cut, self.bg_corrected1_cut,
                                    self.bg_param1[0], self.fitting_algorithm,
                                    self.multigaussian1, self.zerotime1,
                                    self.bg_start1, self.normfactor1,
                                    self.lsq_fit1, self.filename1,
                                    self.bg_dim1, self.globalbg_fun_isOn,
                                    self.globalmod_isOn, self.bg_param1,
                                    self.reg1[:, self.L_curve_number1-1],
                                    self.Pr1_reg[:, self.L_curve_number1-1],
                                    self.r1_reg, self.L_curve_number1,
                                    self.reg_method, self.supressing1,
                                    self.supressingstart1,
                                    self.supressingend1, self.bg_time1)
        elif n == 2 and self.activeset == 2:
            figure_handler_reg(self, self.bg_time2_cut, self.bg_corrected2_cut,
                               3, self.redline2,
                               self.reg2[:, self.L_curve_number2-1])
            figure_handler_reg(self, self.r2_reg,
                               self.Pr2_reg[:, self.L_curve_number2-1],
                               1, self.redline2)
            if self.L_autocorr:
                x = self.Lcurvex_autocorr2
                y = self.Lcurvey_autocorr2
            else:
                x = self.Lcurvex2
                y = self.Lcurvey2
            figure_handler_reg(self, x, y, 2, self.redline2,
                               self.L_curve_number2)
            self.residual2 = (self.reg2[:, self.L_curve_number2-1] -
                              self.bg_corrected2_cut)
            self.lsq_fit2 = lsq_deviation(self.bg_corrected2_cut,
                                          self.reg2[:, self.L_curve_number2-1])
            if verbose:
                print("L-curve number = ", self.L_curve_number2,
                      "\nLeast-squares = ", self.lsq_fit2, "\n")
            self.output_results2 = (0, self.dist_2, self.coef2, self.sigma2,
                                    self.bg_time2_cut, self.bg_corrected2_cut,
                                    self.bg_param2[0], self.fitting_algorithm,
                                    self.multigaussian2, self.zerotime2,
                                    self.bg_start2, self.normfactor2,
                                    self.lsq_fit2, self.filename2,
                                    self.bg_dim2, self.globalbg_fun_isOn,
                                    self.globalmod_isOn, self.bg_param2,
                                    self.reg2[:, self.L_curve_number2-1],
                                    self.Pr2_reg[:, self.L_curve_number2-1],
                                    self.r2_reg, self.L_curve_number2,
                                    self.reg_method, self.supressing2,
                                    self.supressingstart2, self.supressingend2,
                                    self.bg_time2)
        self.detach_lsq(n, False)
        return

    def process_globalreg_results(self, verbose=False):
        figure_handler_reg(self, self.bg_time1_cut, self.bg_corrected1_cut, 3,
                           self.redline_global,
                           self.reg1_global[:, self.global_L_curve_num-1],
                           True, self.bg_time2_cut, self.bg_corrected2_cut,
                           self.reg2_global[:, self.global_L_curve_num-1])
        figure_handler_reg(self, self.r_reg_global,
                           self.Pr_reg_global[:, self.global_L_curve_num-1], 1,
                           self.redline_global)
        figure_handler_reg(self, self.Lcurvex_global, self.Lcurvey_global, 2,
                           self.redline_global, self.global_L_curve_num)
        self.global_output_results = (0, self.Globaldist, self.Globalcoef,
                                      self.Globalsigma, self.bg_time1_cut,
                                      self.bg_corrected1_cut,
                                      self.bg_time2_cut,
                                      self.bg_corrected2_cut,
                                      self.fitting_algorithm,
                                      self.multigaussian2,
                                      self.filename1, self.filename2,
                                      self.reg1_global[:, self.global_L_curve_num-1],
                                      self.reg2_global[:, self.global_L_curve_num-1],
                                      self.Pr_reg_global[:, self.global_L_curve_num-1],
                                      self.r_reg_global,
                                      self.global_L_curve_num,
                                      self.reg_method, self.fitweight,
                                      self.supressingglob,
                                      self.supressingstartglo,
                                      self.supressingendglo)
        self.save_glob_fit = True
        self.residual_global1 = (self.reg1_global[:,
                                 self.global_L_curve_num-1] -
                                 self.bg_corrected1_cut)
        self.residual_global2 = (self.reg2_global[:,
                                 self.global_L_curve_num-1] -
                                 self.bg_corrected2_cut)
        if verbose:
            print("L-curve number = ", self.global_L_curve_num)
        self.detach_lsq(self.activeset, False)
        return

    def figure_update_globalfit(self):
        figure_handler_globalfit(self, self.bg_time1_cut,
                                 self.bg_corrected1_cut, 3,
                                 self.redline_global, self.bg_time2_cut,
                                 self.bg_corrected2_cut, self.GlobalFit1,
                                 self.GlobalFit2)
        figure_handler_globalfit(self, self.Globaldistance, self.GlobalPr,
                                 1, self.redline_global)
        figure_handler_globalfit(self, self.GlobalFFreq1,
                                 self.Fourier1, 2, self.redline_global,
                                 self.GlobalFFreq2, self.Fourier2,
                                 self.GlobalFourier1, self.GlobalFourier2)
        self.detach_lsq(self.activeset, False)
        return

    def figure_update_fit(self, n):
        if n == 1:
            figure_handler_fit(self, self.bg_time1_cut, self.bg_corrected1_cut,
                               3, self.redline1, self.Fit1)
            figure_handler_fit(self, self.distance_1, self.Pr_1, 1,
                               self.redline1)
            figure_handler_fit(self, self.FFreq1, self.Fourier1, 2,
                               self.redline1, self.FourierFit1)
        elif n == 2:
            figure_handler_fit(self, self.bg_time2_cut, self.bg_corrected2_cut,
                               3, self.redline2, self.Fit2)
            figure_handler_fit(self, self.distance_2, self.Pr_2, 1,
                               self.redline2)
            figure_handler_fit(self, self.FFreq2, self.Fourier2, 2,
                               self.redline2, self.FourierFit2)
        return

    def zoom(self, n):
        if self.lsq_fit1 is not None and self.activeset == 1:
            return
        if self.lsq_fit2 is not None and self.activeset == 2:
            return
        if self.show_imaginary.isChecked():
            return
        self.update_figset(self.activeset)
        return

    def enable_adaptive_kernel(self, n):
        if not self.setexists[n-1]:
            self.use_adaptive_kernel.setCheckState(False)
            return
        if (self.use_adaptive_kernel.isChecked() and self.setexists[n-1]):
            self.use_large_kernel.setCheckState(False)
            if n == 1:
                self.large_kernel1 = False
                self.adaptive_kernel1 = True
            elif n == 2:
                self.large_kernel1 = False
                self.adaptive_kernel2 = True
            print("\nMedium size kernel is switched on")
        else:
            if n == 1:
                self.adaptive_kernel1 = False
            elif n == 2:
                self.adaptive_kernel2 = False
            print("\nMedium size  is switched off")
        QApplication.processEvents()
        try:
            self.dialog4.close()
        except:
            pass
        self.current_result_is_reg = False
        return

    def enable_large_kernel(self, n):
        if not self.setexists[n-1]:
            self.use_large_kernel.setCheckState(False)
            return
        if (self.use_large_kernel.isChecked() and self.setexists[n-1]):
            if n == 1:
                self.large_kernel1 = True
            elif n == 2:
                self.large_kernel2 = True
            print("\nLarge kernel is switched on")
            self.use_adaptive_kernel.setCheckState(False)
        else:
            if n == 1:
                self.large_kernel1 = False
            elif n == 2:
                self.large_kernel2 = False
            print("\nLarge kernel is switched off")
            QApplication.processEvents()
        try:
            self.dialog4.close()
        except:
            pass
        self.current_result_is_reg = False
        QApplication.processEvents()
        return

    def validation(self, n, boolean=True):
        if not self.current_result_is_reg:
            return
        if self.lsq_fit1 is None and n == 1:
            return
        if self.lsq_fit2 is None and n == 2:
            return
        if not boolean:
            return
        else:
            if not self.Subguiinit_Valid:
                ValidationSubGUIhandling(self, True)
            else:
                ValidationSubGUIhandling(self, boolean)
        return

    def detach_lsq(self, n, boolean=True):
        if self.lsq_fit1 is None and n == 1:
            return
        if self.lsq_fit2 is None and n == 2:
            return
        if (not boolean and not hasattr(self, 'dialog3')):
            return
        else:
            if not self.Subguiinit:
                ResidueSubGUIhandling(self, True)
            else:
                ResidueSubGUIhandling(self, boolean)
        return

    # SAVE OUTPUT
    def save_file(self, n):
        if self.lsq_fit1 is None and self.activeset == 1:
            return
        if self.lsq_fit2 is None and self.activeset == 2:
            return
        saveFile = QAction("&Save File", self)
        saveFile.setShortcut("Ctrl+S")
        saveFile.setStatusTip('Save File')
        self.file_save(n)
        return

    def file_save(self, n):
        self.dialog = QFileDialog()
        self.dialog.setStyleSheet("background-color:rgb(0, 196, 255)")
        str_tmp = "*.txt (*.txt);;*dat (*.dat)"
        name, name_tmp = self.dialog.getSaveFileName(self, 'Save File', None,
                                                     str_tmp)
        if not name:
            return
        self.save_name = name
        self.save_name = str(self.save_name)
        if not (self.save_name.endswith('.txt') or
                self.save_name.endswith('.dat')):
            self.save_name += '.txt'
        filetyp = '.txt'
        if '.txt' in self.save_name:
            pos = self.save_name.index('.txt')
            filetyp = '.txt'
            self.save_name = self.save_name[0:pos]
        elif '.dat' in self.save_name:
            pos = self.save_name.index('.dat')
            filetyp = '.dat'
            self.save_name = self.save_name[0:pos]
        strings = ('_fit', '_distr', '_infosheet')
        for k in range(0, 2):
            add = ""
            if self.save_glob_fit:
                n = k+1
                add = "_single"+str(n)
            if n == 1:
                listing = self.output_results1
            elif n == 2:
                listing = self.output_results2
            tmparra = np.array((listing[4], listing[5], listing[18]))
            tmparra2 = np.array((listing[20], listing[19]))
            tmparra = np.transpose(tmparra)
            y = tmparra.reshape((len(listing[4]), 3))
            tmparra2 = np.transpose(tmparra2)
            y2 = tmparra2.reshape((len(listing[20]), 2))
            y2 = np.around(y2, 8)
            list_of_agorithms = (" ", "Trust-region-reflective",
                                 "Sequential Least SQuares Programming (SLSQP)",
                                 'Modification of Powell’s method',
                                 ("Quasi-Newton method of Broyden, Fletcher," +
                                  " Goldfarb, and Shanno (BFGS)"),
                                 "Stochastic Trust-region-reflective",
                                 ("Constrained Optimization BY Linear " +
                                  "Approximation (COBYLA)"))
            list_of_reg = (" ", "Second order Tikhonov regularization",
                           "First order Tikhonov regularization",
                           "Hybrid Tikhonov functional")
            with open(self.save_name+strings[0]+add+filetyp, 'w') as file:
                file.write("\n".join("   ".join(map("{:.8f}".format, x)) for
                           x in (y)))
            file.close()
            with open(self.save_name+strings[1]+add+filetyp, 'w') as file:
                file.write("\n".join("   ".join(map("{:.8f}".format, x)) for
                           x in (y2)))
            file.close()
            with open(self.save_name+strings[2]+add+filetyp, 'w') as file:
                file.write("Infosheet for " + listing[13] + "\n\n\n\n")
                file.write("Analyzed at: ")
                now = datetime.datetime.now()
                file.write(now.strftime("%Y-%m-%d %H:%M:%S"))
                file.write("\n\nAnalyzed with: " + self.GlopelVersion + "\n")
                file.write("\n\n\n\n\n*************Analysis results******" +
                           "***********\n\n")
                if listing[0] == 1:
                    file.write("Fitting algorithm: " +
                               list_of_agorithms[listing[7]] + "\n\n")
                    if listing[8]:
                        str_tmp = "5-Gaussian Model"
                    else:
                        str_tmp = "4-Gaussian Model"
                    file.write("Used simulation model: " + str_tmp + "\n\n")
                    file.write("Coefficient\t\t Distance / nm" +
                               "\t\t sigma / nm\n")
                    for i in range(0, len(listing[1])):
                        file.write(str(i+1)+": "+str(round(listing[2][i], 5)) +
                                   "\t          ")
                        file.write(str(round(listing[1][i], 5)) +
                                   "\t           ")
                        if listing[8]:
                            file.write(str(round(listing[3], 5))+"\n")
                        else:
                            file.write(str(round(listing[3][i], 5))+"\n")
                elif listing[0] == 0:
                    file.write("Regularization method: " +
                               list_of_reg[listing[22]]+"\n\n")
                    file.write("L-curve number: " + str(listing[21])+"\n")
                if listing[23]:
                    str_tmp = ("\n\nSuppression of distances was applied in" +
                               " the interval\nbetween ")
                    file.write(str_tmp + str(round(listing[24], 3)) +
                               " nm and "+str(round(listing[25], 3))+" nm\n")
                file.write("\nObtained least-square-deviation = " +
                           str(round(listing[12], 8))+"\n\n")
                file.write("\n***************Presettings*******************\n")
                file.write("\nUsed zerotime = "+str(round(listing[9], 5)) +
                           " nm\n")
                file.write("\nUsed background start = " +
                           str(round(listing[10], 5))+" nm\n")
                file.write("\nUsed background dimension = " +
                           str(listing[14])+"\n")
                file.write("\nObtained background decay:  k = " +
                           str(round(listing[17][1], 6))+"\n")
                file.write("\nObtained modulation depth:  lambda = " +
                           str(round(listing[6], 6))+"\n")
                file.write("\nManual normalization = " +
                           str(round(listing[11], 5))+"E-3\n")
                if listing[15]:
                    str_tmp = ("\nGlobal background function used," +
                               "\nreferred to ")
                    if n == 1:
                        file.write(str_tmp+self.filename2+"\n")
                    elif n == 2:
                        file.write(str_tmp+self.filename1+"\n")
                else:
                    file.write("\nNo global background function used\n")
                if listing[16]:
                    str_tmp = ("\nModulation depth normalization used," +
                               "\nreferred to ")
                    if n == 1:
                        file.write(str_tmp+self.filename2+"\n")
                    elif n == 2:
                        file.write(str_tmp+self.filename1+"\n")
                else:
                    file.write("\nNo modulation depth normalization used\n")
                if max(listing[-1]) > max(listing[4]):
                    file.write("\nTime trace was cut at: " +
                               str(max(listing[4])) +
                               ' nm (Raw data maximum time: ' +
                               str(max(listing[-1]))+' nm \n')
            file.close()
            if not self.save_glob_fit:
                break
            elif self.save_glob_fit and k == 1:
                listing = self.global_output_results
                # Preparing the arrays for output
                tmparra = np.array((listing[4], listing[5], listing[12]))
                tmparra2 = np.array((listing[6], listing[7], listing[13]))
                tmparra3 = np.array((listing[15], listing[14]))
                tmparra = np.transpose(tmparra)
                y = tmparra.reshape((len(listing[4]), 3))
                tmparra2 = np.transpose(tmparra2)
                y2 = tmparra2.reshape((len(listing[6]), 3))
                tmparra3 = np.transpose(tmparra3)
                y3 = tmparra3.reshape((len(listing[14]), 2))
                y3 = np.around(y3, 8)
                with open(self.save_name+strings[0]+"_global1" +
                          filetyp, 'w') as file:
                    file.write("\n".join("   ".join(map("{:.8f}".format, x)) for x in (y)))
                file.close()
                with open(self.save_name+strings[0]+"_global2" +
                          filetyp, 'w') as file:
                    file.write("\n".join("   ".join(map("{:.8f}".format, x)) for x in (y2)))
                file.close()
                with open(self.save_name+strings[1]+"_global" +
                          filetyp, 'w') as file:
                    file.write("\n".join("   ".join(map("{:.8f}".format, x)) for x in (y3)))
                file.close()
                with open(self.save_name+strings[2]+"_global" +
                          filetyp, 'w') as file:
                    file.write("Infosheet for Gloabal Analysis of " +
                               listing[11]+" \nand "+listing[11]+"\n\n\n\n")
                    file.write("Analyzed at : ")
                    now = datetime.datetime.now()
                    file.write(now.strftime("%Y-%m-%d %H:%M:%S"))
                    str_tmp = ("\n\n\n\n\n*************Analysis results****" +
                               "*************\n\n")
                    file.write(str_tmp)
                    # For all Fitting things
                    if listing[0] == 1:
                        file.write("Fitting algorithm: " +
                                   list_of_agorithms[listing[8]]+"\n\n")
                        if listing[9]:
                            str_tmp = "5-Gaussian Model"
                        else:
                            str_tmp = "4-Gaussian Model"
                        file.write("Used simulation model: " + str_tmp +
                                   "\n\n")
                        str_tmp = ("Coefficient\t\t Distance / nm\t\t" +
                                   " sigma / nm\n")
                        file.write(str_tmp)
                        for i in range(0, len(listing[1])):
                            file.write(str(i+1)+": " +
                                       str(round(listing[2][i], 5)) +
                                       "\t          ")
                            file.write(str(round(listing[1][i], 5)) +
                                       "\t           ")
                            if listing[8]:
                                file.write(str(round(listing[3], 5))+"\n")
                            else:
                                file.write(str(round(listing[3][i], 5))+"\n")
                    elif listing[0] == 0:
                        file.write("Regularization method: " +
                                   list_of_reg[listing[17]]+"\n\n")
                        file.write("L-curve number: "+str(listing[16])+"\n")
                    if listing[19]:
                        str_tmp = ("\n\nSuppression of distances was applied" +
                                   " in the interval\nbetween ")
                        file.write(str_tmp + str(round(listing[20], 3)) +
                                   " nm and "+str(round(listing[21], 3)) +
                                   " nm\n")
                    # Final least-squares
                    file.write("\nUsed weighting factor = " +
                               str(round(listing[18], 8))+"\n\n")
        return

    def close_GUI(self):
        print("Close event")
        reply = QMessageBox.question(self, 'Message', "Are you sure to quit?",
                                     QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.close()
        else:
            return


"""********************************************************************
       MAIN GUI (EVENT) LOOP
********************************************************************"""


def run():
    app_ss = QApplication(sys.argv)
    splash_screen = QSplashScreen(QPixmap(resource_path(
                                          "GloPel_splashicon.png")))
    splash_screen.show()
    app_ss.processEvents()
    start = time.time()
    while time.time() - start < 2:
        time.sleep(0.001)
        app_ss.processEvents()
    # Main GUI Application
    app = QApplication(sys.argv)
    mainfun = GloPelMainGuiDesign()
    app.processEvents()
    mainfun.show()
    splash_screen.finish(mainfun)
    sys.exit(app_ss.exec_())
    sys.exit(app.exec_())
    return


if __name__ == '__main__':
    app_ss = QApplication(sys.argv)
    splash_screen = QSplashScreen(QPixmap(resource_path(
                                          "GloPel_splashicon.png")))
    splash_screen.show()
    app_ss.processEvents()
    start = time.time()
    while time.time() - start < 2:
        time.sleep(0.001)
        app_ss.processEvents()
    # Main GUI Application
    app = QApplication(sys.argv)
    mainfun = GloPelMainGuiDesign()
    app.processEvents()
    mainfun.show()
    splash_screen.finish(mainfun)
    sys.exit(app_ss.exec_())
    sys.exit(app.exec_())

