import pyhandle
import logging

from pyhandle.client.resthandleclient import RESTHandleClient
from pyhandle.handleexceptions import HandleNotFoundException
from pyhandle.handleexceptions import GenericHandleError

from . import util
from . import hsresponses


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(util.NullHandler())

class EUDATHandleClient(RESTHandleClient):
    """
    Main B2Handle Class
    """
    def __init__(self, handle_server_url=None, **args):

       RESTHandleClient.__init__(self, handle_server_url, **args)


    def exchange_additional_URL(self, handle, old, new):
        '''
        Exchange an URL in the 10320/LOC entry against another, keeping the same id
        and other attributes.

        :param handle: The handle to modify.
        :param old: The URL to replace.
        :param new: The URL to set as new URL.
        '''
        LOGGER.debug('exchange_additional_URL...')

        handlerecord_json = self.retrieve_handle_record_json(handle)
        if handlerecord_json is None:
            msg = 'Cannot exchange URLs in unexisting handle'
            raise HandleNotFoundException(
                handle=handle,
                msg=msg
            )
        list_of_entries = handlerecord_json['values']

        if not self.is_URL_contained_in_10320LOC(handle, old, handlerecord_json):
            LOGGER.debug('exchange_additional_URL: No URLs exchanged, as the url was not in the record.')
        else:
            self.__exchange_URL_in_13020loc(old, new, list_of_entries, handle)

            op = 'exchanging URLs'
            resp, put_payload = self.restclient.__send_handle_put_request(
                handle,
                list_of_entries,
                overwrite=True,
                op=op
            )
            # TODO FIXME (one day): Implement overwriting by index (less risky)
            if hsresponses.handle_success(resp):
                pass
            else:
                msg = 'Could not exchange URL ' + str(old) + ' against ' + str(new)
                raise GenericHandleError(
                    operation=op,
                    handle=handle,
                    reponse=resp,
                    msg=msg,
                    payload=put_payload
                )

    def is_URL_contained_in_10320LOC(self, handle, url, handlerecord_json=None):
        '''
        Checks if the URL is already present in the handle record's
        10320/LOC entry.

        :param handle: The handle.
        :param url: The URL.
        :raises: :exc:`~b2handle.handleexceptions.HandleNotFoundException`
        :raises: :exc:`~b2handle.handleexceptions.HandleSyntaxError`
        :return: True if the handle record's 10320/LOC entry contains the URL;
            False otherwise. If the entry is empty or does not exist, False
            is returned.
        '''
        LOGGER.debug('is_URL_contained_in_10320LOC...')

        handlerecord_json = self.restclient.__get_handle_record_if_necessary(handle, handlerecord_json)
        if handlerecord_json is None:
            raise HandleNotFoundException(handle=handle)
        list_of_entries = handlerecord_json['values']

        num_entries = 0
        num_URL = 0
        for entry in list_of_entries:
            if entry['type'] == '10320/LOC':
                num_entries += 1
                xmlroot = ET.fromstring(entry['data']['value'])
                list_of_locations = xmlroot.findall('location')
                for item in list_of_locations:
                    if item.get('href') == url:
                        num_URL += 1

        if num_entries == 0:
            return False
        else:
            if num_URL == 0:
                return False
            else:
                return True

    def add_additional_URL(self, handle, *urls, **attributes):
        '''
        Add a URL entry to the handle record's 10320/LOC entry. If 10320/LOC
        does not exist yet, it is created. If the 10320/LOC entry already
        contains the URL, it is not added a second time.

        :param handle: The handle to add the URL to.
        :param urls: The URL(s) to be added. Several URLs may be specified.
        :param attributes: Optional. Additional key-value pairs to set as
            attributes to the <location> elements, e.g. weight, http_role or
            custom attributes. Note: If the URL already exists but the
            attributes are different, they are updated!
        :raises: :exc:`~pyhandle.handleexceptions.HandleNotFoundException`
        :raises: :exc:`~pyhandle.handleexceptions.HandleSyntaxError`
        :raises: :exc:`~pyhandle.handleexceptions.HandleAuthenticationError`
        '''
        LOGGER.debug('add_additional_URL...')

        handlerecord_json = self.retrieve_handle_record_json(handle)
        if handlerecord_json is None:
            msg = 'Cannot add URLS to unexisting handle!'
            raise HandleNotFoundException(handle=handle, msg=msg)
        list_of_entries = handlerecord_json['values']

        is_new = False
        for url in urls:
            if not self.is_URL_contained_in_10320LOC(handle, url, handlerecord_json):
                is_new = True

        if not is_new:
            LOGGER.debug("add_additional_URL: No new URL to be added (so no URL is added at all).")
        else:

            for url in urls:
                self.__add_URL_to_10320LOC(url, list_of_entries, handle)

            op = 'adding URLs'
            resp, put_payload = self.__send_handle_put_request(handle, list_of_entries, overwrite=True, op=op)
            # TODO FIXME (one day) Overwrite by index.

            if hsresponses.handle_success(resp):
                pass
            else:
                msg = 'Could not add URLs ' + str(urls)
                raise GenericHandleError(
                    operation=op,
                    handle=handle,
                    reponse=resp,
                    msg=msg,
                    payload=put_payload
                )

    def remove_additional_URL(self, handle, *urls):
        '''
        Remove a URL from the handle record's 10320/LOC entry.

        :param handle: The handle to modify.
        :param urls: The URL(s) to be removed. Several URLs may be specified.
        :raises: :exc:`~pyhandle.handleexceptions.HandleNotFoundException`
        :raises: :exc:`~pyhandle.handleexceptions.HandleSyntaxError`
        :raises: :exc:`~pyhandle.handleexceptions.HandleAuthenticationError`
        '''

        LOGGER.debug('remove_additional_URL...')

        handlerecord_json = self.retrieve_handle_record_json(handle)
        if handlerecord_json is None:
            msg = 'Cannot remove URLs from unexisting handle'
            raise HandleNotFoundException(handle=handle, msg=msg)
        list_of_entries = handlerecord_json['values']

        for url in urls:
            self.__remove_URL_from_10320LOC(url, list_of_entries, handle)

        op = 'removing URLs'
        resp, put_payload = self.__send_handle_put_request(
            handle,
            list_of_entries,
            overwrite=True,
            op=op
        )
        # TODO FIXME (one day): Implement overwriting by index (less risky),
        # once HS have fixed the issue with the indices.
        if hsresponses.handle_success(resp):
            pass
        else:
            op = 'removing "' + str(urls) + '"'
            msg = 'Could not remove URLs ' + str(urls)
            raise GenericHandleError(
                operation=op,
                handle=handle,
                reponse=resp,
                msg=msg,
                payload=put_payload
            )

