import deprecation
import logging

from pyqalx.__version__ import __version__
from pyqalx.core.adapters.adapter import QalxValidateBlueprintAdapter, \
    QalxFileAdapter
from pyqalx.core.entities import Item
from pyqalx.core.entities.item import ItemAddManyEntity
from pyqalx.core.errors import QalxFileError, QalxError


logger = logging.getLogger(__name__)


class QalxItem(QalxValidateBlueprintAdapter,
               QalxFileAdapter):
    _entity_class = Item

    def _validate(self, data=None, input_file=None, file_name="",
                  meta=None, blueprint_name=None,
                  **kwargs):
        if not any([data, input_file]):
            raise QalxError('At least one of `data` or `input_file` is '
                            'required')
        if data is None:
            data = {}
        return super(QalxItem, self)._validate(data=data,
                                               input_file=input_file,
                                               file_name=file_name,
                                               meta=meta,
                                               blueprint_name=blueprint_name,
                                               **kwargs)

    def add(self, data=None, input_file=None, file_name="",
            meta=None, blueprint_name=None, **kwargs):
        """
        Adds an `Item` instance that can contain either
        data (as a dict), a file or both.

        :param data: Optional data to store against this Item
        :type data: dict
        :param input_file: Optional input file path or stream
        :type input_file: str or `filestream`
        :param file_name: input file name. Optional for file path. Required for file stream
        :type file_name: str
        :param meta: A dictionary of metadata to store
        :type meta: dict
        :param blueprint_name: An optional blueprint name to use to validate this item against an existing Blueprint
        :return: A newly created `Item` instance
        """

        return super(QalxItem, self).add(data=data,
                                         input_file=input_file,
                                         file_name=file_name,
                                         meta=meta,
                                         blueprint_name=blueprint_name,
                                         **kwargs)

    def save(self, entity, input_file=None, file_name="", blueprint_name=None,
             **kwargs):
        """
        Saves an updated existing `Item` instance.
        To remove a file from an `Item` update the entity so that
        `entity['file'] = {}`

        :param entity: The entity that we are saving
        :type entity: An instance of `Item`
        :param input_file: Optional input file path or stream
        :type input_file: str or `filestream`
        :param file_name: input file name. Optional for file path. Required
                          for file stream
        :type file_name: str
        :param meta: A dictionary of metadata to store
        :type meta: dict
        :param blueprint_name: An optional blueprint name to use if you want
                              to validate this item against an existing
                              Blueprint
        :type blueprint_name: str
        :return: An updated `Item` instance
        """
        return super(QalxItem, self).save(entity=entity,
                                          input_file=input_file,
                                          file_name=file_name,
                                          blueprint_name=blueprint_name,
                                          **kwargs)

    def add_many(self, items, **kwargs):
        """
        Adds multiple items at once.
        :param items: A list of item data that you want to create.  This can
        be a mixture of non file items and file items. The keys of each item in the list should be the same as if a
        single item were being created via the `add` method
        :type items: list
        :return:
        """
        if not isinstance(items, list):
            raise QalxError('`items` argument must be a list')
        headers = {
            'qalx-bulk': 'true'
        }
        validated_items = []

        for item in items:
            # Ensure all the items are valid.  They should be in the same
            # format as if a user is adding a single item.  This also handles
            # checking the blueprint for each item
            validated_items.append(self._validate(**item))

        resp = self.add(items=validated_items,
                        headers=headers,
                        _is_validated=True,
                        # Don't upload as we need to handle
                        # the file upload manually
                        upload=False,
                        **kwargs)

        # We have all the data to create the files, but the indexes have
        # been split up compared to the response.  Therefore, inject blank
        # values into the response where there are errors.  This means that
        # the structure will match the original `items` that the user specified
        # (as the API preserves order when bulk creating data)
        ERRORED_KEY = None
        [resp['items'].insert(int(x), ERRORED_KEY) for x in resp['errors'].keys()]

        for index, item in enumerate(items):
            # Iterate the original `items` provided by the user
            created_item = resp['items'][index]
            if item.get('input_file') and created_item is not None:
                # There was a file on the original item and it was also
                # successfully created by the API.  Upload the file as normal
                self._upload_file(entity=resp['items'][index],
                                  input_file=item['input_file'])
        # Finally, remove all the `None` values from the items as these were
        # errors that we are done with
        resp['items'] = list(filter(lambda x: x is not ERRORED_KEY, resp['items']))
        if resp['errors']:
            for index, error in resp['errors'].items():
                logger.warning(f'Error bulk creating at index `{index}`. '
                               f'Error: `{error}`. '
                               f'Original Data: `{items[int(index)]}`')
        return ItemAddManyEntity(self.entity_class, resp)

    @deprecation.deprecated(deprecated_in="0.6", removed_in="1.0",
                            current_version=__version__,
                            details="Use the `add` function instead")
    def add_file(self, input_file, data=None, meta=None,
                 file_name="", blueprint_name=None, **kwargs):
        """adds a file to qalx with optional data and metadata

        :param input_file: input file path or stream
        :type input_file: str or `filestream`
        :param data: optional data you want to store with this file
        :type data: dict
        :param meta: additional data about the item
        :param meta: dict
        :param file_name: input file name. Optional for file path. Required
                          for file stream
        :type file_name: str
        :param blueprint_name: An optional blueprint name to use if you want
                              to validate this item against an existing
                              Blueprint
        :type blueprint_name: str
        :return: pyqalx.core.Item
        """
        if data is None:
            data = {}

        if self.session.rest_api.is_filestream(input_file) and not file_name:
            raise QalxFileError('You must supply a file name when supplying'
                                ' a file stream')
        return self.add(input_file=input_file,
                        file_name=file_name,
                        data=data,
                        meta=meta,
                        blueprint_name=blueprint_name,
                        **kwargs)
