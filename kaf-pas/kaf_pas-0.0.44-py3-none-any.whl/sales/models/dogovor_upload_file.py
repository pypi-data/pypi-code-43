import json
import logging
from tempfile import TemporaryFile

import dateutil
from django.core.files import File
from websocket import create_connection

from crypto.models.upload_file import DSResponse_UploadFile
from isc_common.dropzone import Dz
from isc_common.http.DSResponse import JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from kaf_pas.ckk.models.status import Status
from kaf_pas.common.UploadItem import UploadItem
from kaf_pas.sales.models.customer import Customer
from kaf_pas.sales.models.dogovors import Dogovors

logger = logging.getLogger(__name__)


@JsonResponseWithException()
class DSResponse__Dogovor_UploadFile(DSResponse_UploadFile):

    def __init__(self, request):
        # raise Exception ('Its me !!!!!')
        self.id = request.GET.get('id')
        if request.GET.get('from_grid') == 'true':
            self.from_grid = True
        else:
            self.from_grid = False

        self.dictionary = dict(
            id=request.GET.get('id'),
            code=request.GET.get('code'),
            type=request.GET.get('type'),
            description=request.GET.get('description'),
            date=request.GET.get('date'),
            date_sign=request.GET.get('date_sign'),
            status_id=request.GET.get('status_id'),
            customer_id=request.GET.get('customer_id'),
        )

        self.dz_dictionary = Dz(request.POST)

        self.host = request.GET.get('host')
        self.port = request.GET.get('port')
        if not self.port:
            self.port = 80
        self.channel = request.GET.get('ws_channel')
        self.file = request.FILES.get('upload_attatch')

        self.handle_uploaded_file()

    @property
    def first_chunk(self):
        res = int(self.dz_dictionary.dzchunkindex) == 0
        return res

    @property
    def last_chunk(self):
        res = int(self.dz_dictionary.dztotalchunkcount) == int(self.dz_dictionary.dzchunkindex) + 1
        return res

    def handle_uploaded_file(self):
        try:
            self.dictionary.update(dict(
                real_file_name=self.file.name,
                stored_file_name=self.dz_dictionary.dzuuid,
                file_size=int(self.dz_dictionary.dztotalfilesize),
                file_mime_type=self.file.content_type)
            )

            item = UploadItem(dictionary=self.dictionary)
            old_path = None

            def load_str(pers):
                return f'Загружено: {pers} %'

            with TemporaryFile() as src:
                src.seek(int(self.dz_dictionary.dzchunkbyteoffset))
                src.write(self.file.read())

                pers = round((int(self.dz_dictionary.dzchunkindex) * 100) / int(self.dz_dictionary.dztotalchunkcount), 2)
                if self.last_chunk:
                    pers = 100

                logger.debug(f'{load_str(pers)}, шаг : {int(self.dz_dictionary.dzchunkindex) + 1} из {self.dz_dictionary.dztotalchunkcount}')

                if self.last_chunk:
                    logger.debug(f'Загружен файл: {item.real_file_name}.')
                    logger.debug(f'Запись временного файла.')
                    with open(item.full_path, 'w+b') as destination:
                        src.seek(0)
                        destination.write(src.read())
                    logger.debug(f'Запись временного файла выполнена.')

                    logger.debug(f'Запись: {item.full_path}.')
                    with open(item.full_path, 'rb') as src:
                        fileObj = File(src)

                        try:
                            old_path = Dogovors.objects.get(id=item.id).attfile.name
                        except Dogovors.DoesNotExist:
                            pass

                        res, created = Dogovors.objects.update_or_create(
                            id=item.id,
                            defaults=dict(
                                code=item.code,
                                type=item.type,
                                description=item.description,
                                date=dateutil.parser.parse(item.date) if item.date else None,
                                date_sign=dateutil.parser.parse(item.date_sign) if item.date_sign else None,
                                status=Status.objects.get(id=item.status_id) if item.status_id else None,
                                customer=Customer.objects.get(id=item.customer_id) if item.customer_id else None,
                                attfile=fileObj,
                                file_store=self.get_path(fileObj.name),
                                format=item.file_format,
                                mime_type=item.file_mime_type,
                                size=item.file_size,
                                real_name=item.real_file_name,
                            )
                        )

                        ws = create_connection(f"ws://{self.host}:{self.port}/ws/{self.channel}/")
                        ws.send(json.dumps(dict(id=res.id, type="uploaded")))
                        ws.close()

                        logger.debug(f'Запись: {item.real_file_name} ({fileObj.name}) завершена.')

                    if old_path:
                        self.remove(old_path)
                        logger.debug(f'Удаление: {old_path} завершено.')

                    self.remove(item.full_path)
                    logger.debug(f'Удаление: {item.full_path} завершено.')

            self.response = dict(status=RPCResponseConstant.statusSuccess)

        except Exception as e:
            raise e
