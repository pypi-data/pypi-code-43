import configparser
import logging
import os
from datetime import datetime
from os.path import getmtime
from tkinter import *
from tkinter import filedialog
from xml.dom.expatbuilder import TEXT_NODE
from xml.dom.minidom import parseString

from django.core.management import BaseCommand
from django.db import transaction
from tqdm import tqdm

from isc_common import getAttr, setAttr
from isc_common.management.commands.refresh_mat_views import refresh_mat_view
from kaf_pas.ckk.models.files_askon import Files_askon
from kaf_pas.ckk.models.material_askon import Material_askon

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Загрузка материалов и АСКОНа"
    config = configparser.ConfigParser()
    config['DEFAULT'] = {}

    config.sections()
    config.read('config.ini')

    root = Tk()

    def is_text_node(self, node):
        if len(node.childNodes) > 1:
            return None, None
        elif len(node.childNodes) == 1:
            child = node.childNodes[0]
            if child.nodeType == TEXT_NODE:
                tag_name = node.tagName
                value = child.data
                return tag_name, value
            else:
                return None, None
        else:
            raise Exception(f"Unknown case.")

    def rec_node(self, node, parent=None):
        text_nodes = dict()
        elements = []
        for child in node.childNodes:
            tag_name, value = self.is_text_node(child)
            if tag_name and value:
                setAttr(text_nodes, tag_name, value)
            elif not tag_name and not value:
                elements.append(child)

        if bool(text_nodes):
            if parent:
                setAttr(text_nodes, 'parent_id', parent.id)
            parent, created = Material_askon.objects.update_or_create(**text_nodes)
            if created:
                logger.debug(f'created: {parent}')
            else:
                logger.debug(f'updated: {parent}')
        else:
            parent = None

        for element in elements:
            self.rec_node(element, parent)

    def handle(self, *args, **options):

        logger.info(self.help)

        try:
            initialdir = self.config['DEFAULT']['askondir']
            if not os.path.exists(initialdir):
                initialdir = None
        except KeyError:
            initialdir = None

        self.root.filename = filedialog.askopenfilename(title="Выберите файл документов", initialdir=initialdir)
        if len(self.root.filename) == 0:
            return

        dir, _ = os.path.split(self.root.filename)
        self.config['DEFAULT']['askondir'] = dir

        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)

        logger.debug(f'filename : {self.root.filename}')
        self.root.withdraw()

        date_modification = datetime.fromtimestamp(getmtime(self.root.filename))
        with transaction.atomic():

            file, created = Files_askon.objects.get_or_create(real_name=self.root.filename, file_modification_time=date_modification, props=Files_askon.props.imp)

            if created:
                file = open(self.root.filename, 'r')
                data = file.read()
                file.close()
                dom = parseString(data)

                rows = dom.getElementsByTagName('rows')
                qty = len(rows[0].childNodes)
                self.pbar = tqdm(total=qty)
                for child in rows[0].childNodes:
                    self.rec_node(child)

                    if self.pbar:
                        self.pbar.update(1)

                if self.pbar:
                    self.pbar.close()

                refresh_mat_view('ckk_material_askon_mview')

            else:
                logger.warning(f'Файл: {self.root.filename}, уже импортирован !')

        logger.info("Загрузка выполнена.")
