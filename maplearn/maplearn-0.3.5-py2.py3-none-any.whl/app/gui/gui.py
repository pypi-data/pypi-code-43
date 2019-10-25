# -*- coding: utf-8 -*-
"""
Created on Sat Oct 29 18:12:02 2016

@author: ppichelin
"""
import sys
import os
import logging

from pkg_resources import resource_filename
from PyQt5.QtWidgets import QMainWindow, QFileDialog
from PyQt5 import QtCore

from maplearn.app.config import Config
from maplearn.app.gui.maplearn_ui import Ui_MainWindow
from maplearn.app.main import Main
from maplearn.app.reporting import ReportWriter
from maplearn.ml.algos_reduction import ALGOS as ALGOS_REDUCTION
from maplearn.ml.algos_classification import ALGOS as ALGOS_CLASSIFICATION
from maplearn.ml.algos_clustering import ALGOS as ALGOS_CLUSTERING
from maplearn.ml.algos_regression import ALGOS as ALGOS_REGRESSION


from maplearn import logger

class Gui(QMainWindow, Ui_MainWindow):
    """
    Mapping Learning's main GUI (actually the only one for now)
    """
    def __init__(self, parent=None):
        super(QMainWindow, self).__init__(parent)
        self.setupUi(parent)
        
        # initialize        
        self.cbo_pre_reduce.addItems(ALGOS_REDUCTION.keys())
        # add every classifiers (classification algorithms)
        self.lst_pro_algorithm.addItems(ALGOS_CLASSIFICATION.keys())
        self.set_doc(-1)
        # Set signals
        self.btn_io_data.clicked.connect(self.select_data)
        self.btn_io_samples.clicked.connect(self.select_samples)
        self.btn_io_output.clicked.connect(self.select_output)
        self.btn_run.clicked.connect(self.run)
        self.btn_cancel.clicked.connect(self._quit)
        self.action_open.triggered.connect(self._open)
        self.action_save.triggered.connect(self.save)
        self.action_saveas.triggered.connect(self.saveas)
        self.action_quit.triggered.connect(self._quit)
        self.cbo_pre_reduce.currentTextChanged['QString'].connect(self.__hide_ncomp)
        self.cbo_process.currentTextChanged['QString'].connect(self.__chge_process_type)
        self.tbx_main.currentChanged.connect(self.set_doc)
        
        # configuration (stored in an object)
        self.__cfg_file = None
        self.__cfg = Config(self.__cfg_file)
        self.__display_msg('Mapping Learning is ready')

    def set_doc(self, idx=None):
        """
        Display documentation about Gui in a web page
        """
        if idx is None:
            idx = self.tbx_main.currentIndex()
        
        if idx == 0:
            __file = 'fr_io.html'
        elif idx == 1:
            __file = 'fr_preprocess.html'
        elif idx == 2:
            __file = 'fr_process.html'
        else:
            __file = 'fr_index.html'
        __url = resource_filename('maplearn',
                                   os.path.join('app', 'doc', __file))
        self.web_doc.setUrl(QtCore.QUrl.fromLocalFile(__url))
        logger.debug('Documentation page = %s', __url)            

    def set_values(self):
        """
        Set values from config object into Gui
        """
        #IO
        self.le_io_samples.setText(self.__cfg.io['samples'])
        self.le_io_data.setText(self.__cfg.io['data'])
        self.le_io_output.setText(self.__cfg.io['output'])
        self.le_io_label_id.setText(self.__cfg.io['label_id'])
        self.le_io_label.setText(self.__cfg.io['label'])
        try:
            __tmp = ';'.join(self.__cfg.io['features'])
        except TypeError:
            __tmp =''
        self.le_io_features.setText(__tmp)
        #Preprocess
        self.chk_pre_scale.setChecked(self.__cfg.preprocess['scale'])
        self.chk_pre_balance.setChecked(self.__cfg.preprocess['balance'])
        self.chk_pre_separability.setChecked(self.__cfg.preprocess['separability'])
        self.cbo_pre_reduce.setCurrentText(self.__cfg.preprocess['reduce'])
        if self.__cfg.preprocess['ncomp'] is not None:
            self.sb_pre_ncomp.setValue(self.__cfg.preprocess['ncomp'])
        else:
            self.sb_pre_ncomp.clear()
        
        #Process
        self.cbo_process.setCurrentText(self.__cfg.process['type'].capitalize())
        self.chk_pro_predict.setChecked(self.__cfg.process['predict'])
        self.chk_pro_optimize.setChecked(self.__cfg.process['optimize'])
        for i in range(self.lst_pro_algorithm.count()):
            __item = self.lst_pro_algorithm.item(i)
            if __item.text() in self.__cfg.process['algorithm']:
                self.lst_pro_algorithm.item(i).setSelected(True)
            else:
                self.lst_pro_algorithm.item(i).setSelected(False)
        self.sbo_pro_kfold.setValue(self.__cfg.process['kfold'])

    def get_values(self):
        """
        Get values from Gui and put them into config object
        """
        #IO
        self.__cfg.io['samples'] = self.le_io_samples.text()
        self.__cfg.io['data'] = self.le_io_data.text()
        self.__cfg.io['label'] = self.le_io_label.text()
        self.__cfg.io['label_id'] = self.le_io_label_id.text()
        self.__cfg.io['output'] = self.le_io_output.text()
        __tmp = self.le_io_features.text()
        __tmp = __tmp.split(";")
        self.__cfg.io['features'] = __tmp
        #Preprocess
        self.__cfg.preprocess['scale'] = self.chk_pre_scale.isChecked()
        self.__cfg.preprocess['balance'] = self.chk_pre_balance.isChecked()
        self.__cfg.preprocess['separability'] = self.chk_pre_separability.isChecked()
        self.__cfg.preprocess['reduce'] = self.cbo_pre_reduce.currentText()
        self.__cfg.preprocess['ncomp'] = self.sb_pre_ncomp.value()
        
        #Process
        self.__cfg.process['kfold'] = self.sbo_pro_kfold.value()
        self.__cfg.process['type'] = self.cbo_process.currentText().lower()
        self.__cfg.process['predict'] = self.chk_pro_predict.isChecked()
        self.__cfg.process['optimize'] = self.chk_pro_optimize.isChecked()
        self.__cfg.process['algorithm'] = [i.text() for i in self.lst_pro_algorithm.selectedItems()]
        
    def __chge_process_type(self):
        """
        When user change type of process to apply (ie classification,
        clustering or regression)
        """
        str_type = self.cbo_process.currentText()
        
        # change url of doc widget
        self.set_doc(-1)
        # update list of available algorithms (depending of process type)
        __ALL_ALGOS = eval("ALGOS_%s" % str_type.upper())
        __algos = []
        for item in [self.lst_pro_algorithm.item(i) for i in range(self.lst_pro_algorithm.count())]:
            __algo = item.text()
            if __algo not in __ALL_ALGOS.keys():
                self.lst_pro_algorithm.takeItem(self.lst_pro_algorithm.row(item))
                del item
            else:
                __algos.append(__algo)
        for i in __ALL_ALGOS.keys():
            if i not in __algos:
                self.lst_pro_algorithm.addItem(i)
    
    def select_samples(self):
        self.io_samples = QFileDialog.getOpenFileName()
        self.le_io_samples.setText(self.io_samples[0])

    def select_data(self):
        self.io_data = QFileDialog.getOpenFileName()
        self.le_io_data.setText(self.io_data[0])

    def select_output(self):
        self.io_output = QFileDialog.getExistingDirectory(self)
        self.le_io_output.setText(self.io_output)

    def _open(self):
        """
        Opens a configuration file defined in Gui
        """
        self.__cfg_file = QFileDialog.getOpenFileName(self, \
                filter="Configuration files (*.cfg);;all (*.*)")[0]
        if not self.__cfg_file:
            return None
        self.__cfg = None
        self.__cfg = Config(self.__cfg_file)
        self.__cfg.read()
        self.set_values()
        self.__display_msg('Configuration file loaded (%s)' % self.__cfg_file)

    def __display_msg(self, msg, level=logging.INFO):
        """
        Display a message in log and on the gui
        """
        logger.log(level, msg)
        self.statusbar.showMessage(msg)
    
    def __hide_ncomp(self):
        
        """
        Disable (or hide ?) sb_pre_ncomp when no reduction method is chosen 
        """
        __tmp = self.cbo_pre_reduce.currentText()
        b_display = True
        if __tmp is None or __tmp =='':
            b_display = False
        self.sb_pre_ncomp.setEnabled(b_display)
        #self.sb_pre_ncomp.hide()
        #self.sb_pre_ncomp.show()

    def save(self):
        """
        Saves configuration (stored in object) into the file given in 
        __cfg_file attribute
        """
        self.get_values()
        if self.__cfg_file is None:
            self.saveas()
        else:
            self.__cfg.write(self.__cfg_file)
            self.__display_msg('Configuration saved.')
    
    def saveas(self):
        """
        Saves configuration (stored in object) into a file (specified in Gui)
        """
        self.get_values()
        __output = QFileDialog.getSaveFileName(self, \
                            filter="Configuration files (*.cfg);;all (*.*)")[0]
        if __output:
            self.__cfg.write(__output)
            self.__display_msg('Configuration saved (%s)' % __output)

    def run(self):
        """
        Runs Mapping Learning using configuration given in __cfg attribute
        """
        # GUI
        self.btn_cancel.setEnabled(True)
        self.btn_run.setEnabled(False)
        self.__display_msg('maplearn is running. Please wait...')
        
        # running application
        report_file = os.path.join(self.__cfg.io['output'], 'index')
        report_writer = ReportWriter(report_file)
        sys.stdout = report_writer
    
        print(self.__cfg)
        appli = Main(self.__cfg.io['output'], codes=self.__cfg.codes,
                     **self.__cfg.process)
    
        # TODO: PATCH tout moche à retirer dés que possible
        if self.__cfg.process['type'] == 'clustering' and \
                self.__cfg.io['samples'] is None:
            self.__cfg.io['samples'] = self.__cfg.io['data']
    
        appli.load(source=self.__cfg.io['samples'], **self.__cfg.io)
        if self.__cfg.io['data'] is not None:
            appli.load_data(self.__cfg.io['data'],
                            features=self.__cfg.io['features'])
        appli.preprocess(**self.__cfg.preprocess)
        appli.process(optimize=self.__cfg.process['optimize'],
                      predict=self.__cfg.process['predict'])
    
        report_writer.close()
        # export configuration in output folder
        self.__cfg.write(os.path.join(self.__cfg.io['output'], 'configuration.cfg'))
        # GUI update
        self.__display_msg('Mapping Learning: end.')
        self.btn_run.setEnabled(True)
        self.btn_cancel.setEnabled(False)

    def _quit(self):
        """
        Quits main window and application
        """
        self.__display_msg('Closing gui...')
        self.close()
        sys.exit(0)        

