# coding: utf-8

"""
    convertapi

    Convert API lets you effortlessly convert file formats and types.  # noqa: E501

    OpenAPI spec version: v1
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from cloudmersive_convert_api_client.models.docx_image import DocxImage  # noqa: F401,E501


class DocxInsertImageRequest(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'input_document_file_bytes': 'str',
        'input_document_file_url': 'str',
        'input_image_file_bytes': 'str',
        'input_image_file_url': 'str',
        'image_to_add': 'DocxImage',
        'insert_placement': 'str',
        'insert_path': 'str'
    }

    attribute_map = {
        'input_document_file_bytes': 'InputDocumentFileBytes',
        'input_document_file_url': 'InputDocumentFileUrl',
        'input_image_file_bytes': 'InputImageFileBytes',
        'input_image_file_url': 'InputImageFileUrl',
        'image_to_add': 'ImageToAdd',
        'insert_placement': 'InsertPlacement',
        'insert_path': 'InsertPath'
    }

    def __init__(self, input_document_file_bytes=None, input_document_file_url=None, input_image_file_bytes=None, input_image_file_url=None, image_to_add=None, insert_placement=None, insert_path=None):  # noqa: E501
        """DocxInsertImageRequest - a model defined in Swagger"""  # noqa: E501

        self._input_document_file_bytes = None
        self._input_document_file_url = None
        self._input_image_file_bytes = None
        self._input_image_file_url = None
        self._image_to_add = None
        self._insert_placement = None
        self._insert_path = None
        self.discriminator = None

        if input_document_file_bytes is not None:
            self.input_document_file_bytes = input_document_file_bytes
        if input_document_file_url is not None:
            self.input_document_file_url = input_document_file_url
        if input_image_file_bytes is not None:
            self.input_image_file_bytes = input_image_file_bytes
        if input_image_file_url is not None:
            self.input_image_file_url = input_image_file_url
        if image_to_add is not None:
            self.image_to_add = image_to_add
        if insert_placement is not None:
            self.insert_placement = insert_placement
        if insert_path is not None:
            self.insert_path = insert_path

    @property
    def input_document_file_bytes(self):
        """Gets the input_document_file_bytes of this DocxInsertImageRequest.  # noqa: E501

        Optional: Bytes of the input file to operate on  # noqa: E501

        :return: The input_document_file_bytes of this DocxInsertImageRequest.  # noqa: E501
        :rtype: str
        """
        return self._input_document_file_bytes

    @input_document_file_bytes.setter
    def input_document_file_bytes(self, input_document_file_bytes):
        """Sets the input_document_file_bytes of this DocxInsertImageRequest.

        Optional: Bytes of the input file to operate on  # noqa: E501

        :param input_document_file_bytes: The input_document_file_bytes of this DocxInsertImageRequest.  # noqa: E501
        :type: str
        """
        if input_document_file_bytes is not None and not re.search(r'^(?:[A-Za-z0-9+\/]{4})*(?:[A-Za-z0-9+\/]{2}==|[A-Za-z0-9+\/]{3}=)?$', input_document_file_bytes):  # noqa: E501
            raise ValueError(r"Invalid value for `input_document_file_bytes`, must be a follow pattern or equal to `/^(?:[A-Za-z0-9+\/]{4})*(?:[A-Za-z0-9+\/]{2}==|[A-Za-z0-9+\/]{3}=)?$/`")  # noqa: E501

        self._input_document_file_bytes = input_document_file_bytes

    @property
    def input_document_file_url(self):
        """Gets the input_document_file_url of this DocxInsertImageRequest.  # noqa: E501

        Optional: URL of a file to operate on as input.  This can be a public URL, or you can also use the begin-editing API to upload a document and pass in the secure URL result from that operation as the URL here (this URL is not public).  # noqa: E501

        :return: The input_document_file_url of this DocxInsertImageRequest.  # noqa: E501
        :rtype: str
        """
        return self._input_document_file_url

    @input_document_file_url.setter
    def input_document_file_url(self, input_document_file_url):
        """Sets the input_document_file_url of this DocxInsertImageRequest.

        Optional: URL of a file to operate on as input.  This can be a public URL, or you can also use the begin-editing API to upload a document and pass in the secure URL result from that operation as the URL here (this URL is not public).  # noqa: E501

        :param input_document_file_url: The input_document_file_url of this DocxInsertImageRequest.  # noqa: E501
        :type: str
        """

        self._input_document_file_url = input_document_file_url

    @property
    def input_image_file_bytes(self):
        """Gets the input_image_file_bytes of this DocxInsertImageRequest.  # noqa: E501

        Optional: Bytes of the input image file to operate on; if you supply this value do not supply InputImageFileUrl or ImageToAdd.  # noqa: E501

        :return: The input_image_file_bytes of this DocxInsertImageRequest.  # noqa: E501
        :rtype: str
        """
        return self._input_image_file_bytes

    @input_image_file_bytes.setter
    def input_image_file_bytes(self, input_image_file_bytes):
        """Sets the input_image_file_bytes of this DocxInsertImageRequest.

        Optional: Bytes of the input image file to operate on; if you supply this value do not supply InputImageFileUrl or ImageToAdd.  # noqa: E501

        :param input_image_file_bytes: The input_image_file_bytes of this DocxInsertImageRequest.  # noqa: E501
        :type: str
        """
        if input_image_file_bytes is not None and not re.search(r'^(?:[A-Za-z0-9+\/]{4})*(?:[A-Za-z0-9+\/]{2}==|[A-Za-z0-9+\/]{3}=)?$', input_image_file_bytes):  # noqa: E501
            raise ValueError(r"Invalid value for `input_image_file_bytes`, must be a follow pattern or equal to `/^(?:[A-Za-z0-9+\/]{4})*(?:[A-Za-z0-9+\/]{2}==|[A-Za-z0-9+\/]{3}=)?$/`")  # noqa: E501

        self._input_image_file_bytes = input_image_file_bytes

    @property
    def input_image_file_url(self):
        """Gets the input_image_file_url of this DocxInsertImageRequest.  # noqa: E501

        Optional: URL of an image file to operate on as input; if you supply this value do not supply InputImageFileBytes or ImageToAdd.  This can be a public URL, or you can also use the begin-editing API to upload a document and pass in the secure URL result from that operation as the URL here (this URL is not public).  # noqa: E501

        :return: The input_image_file_url of this DocxInsertImageRequest.  # noqa: E501
        :rtype: str
        """
        return self._input_image_file_url

    @input_image_file_url.setter
    def input_image_file_url(self, input_image_file_url):
        """Sets the input_image_file_url of this DocxInsertImageRequest.

        Optional: URL of an image file to operate on as input; if you supply this value do not supply InputImageFileBytes or ImageToAdd.  This can be a public URL, or you can also use the begin-editing API to upload a document and pass in the secure URL result from that operation as the URL here (this URL is not public).  # noqa: E501

        :param input_image_file_url: The input_image_file_url of this DocxInsertImageRequest.  # noqa: E501
        :type: str
        """

        self._input_image_file_url = input_image_file_url

    @property
    def image_to_add(self):
        """Gets the image_to_add of this DocxInsertImageRequest.  # noqa: E501

        Optional: Image to add; if you supply in this object, do not supply InputImageFileBytes or InputImageFileUrl.  # noqa: E501

        :return: The image_to_add of this DocxInsertImageRequest.  # noqa: E501
        :rtype: DocxImage
        """
        return self._image_to_add

    @image_to_add.setter
    def image_to_add(self, image_to_add):
        """Sets the image_to_add of this DocxInsertImageRequest.

        Optional: Image to add; if you supply in this object, do not supply InputImageFileBytes or InputImageFileUrl.  # noqa: E501

        :param image_to_add: The image_to_add of this DocxInsertImageRequest.  # noqa: E501
        :type: DocxImage
        """

        self._image_to_add = image_to_add

    @property
    def insert_placement(self):
        """Gets the insert_placement of this DocxInsertImageRequest.  # noqa: E501

        Optional; default is DocumentEnd.  Placement Type of the insert; possible values are: DocumentStart (very beginning of the document), DocumentEnd (very end of the document), BeforeExistingObject (right before an existing object - fill in the InsertPath field using the Path value from an existing object), AfterExistingObject (right after an existing object - fill in the InsertPath field using the Path value from an existing object)  # noqa: E501

        :return: The insert_placement of this DocxInsertImageRequest.  # noqa: E501
        :rtype: str
        """
        return self._insert_placement

    @insert_placement.setter
    def insert_placement(self, insert_placement):
        """Sets the insert_placement of this DocxInsertImageRequest.

        Optional; default is DocumentEnd.  Placement Type of the insert; possible values are: DocumentStart (very beginning of the document), DocumentEnd (very end of the document), BeforeExistingObject (right before an existing object - fill in the InsertPath field using the Path value from an existing object), AfterExistingObject (right after an existing object - fill in the InsertPath field using the Path value from an existing object)  # noqa: E501

        :param insert_placement: The insert_placement of this DocxInsertImageRequest.  # noqa: E501
        :type: str
        """

        self._insert_placement = insert_placement

    @property
    def insert_path(self):
        """Gets the insert_path of this DocxInsertImageRequest.  # noqa: E501

        Optional; location within the document to insert the object; fill in the InsertPath field using the Path value from an existing object.  Used with InsertPlacement of BeforeExistingObject or AfterExistingObject  # noqa: E501

        :return: The insert_path of this DocxInsertImageRequest.  # noqa: E501
        :rtype: str
        """
        return self._insert_path

    @insert_path.setter
    def insert_path(self, insert_path):
        """Sets the insert_path of this DocxInsertImageRequest.

        Optional; location within the document to insert the object; fill in the InsertPath field using the Path value from an existing object.  Used with InsertPlacement of BeforeExistingObject or AfterExistingObject  # noqa: E501

        :param insert_path: The insert_path of this DocxInsertImageRequest.  # noqa: E501
        :type: str
        """

        self._insert_path = insert_path

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        if issubclass(DocxInsertImageRequest, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, DocxInsertImageRequest):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
