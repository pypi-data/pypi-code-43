from PIL import Image as PILImage
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser, FileUploadParser
from rest_framework.response import Response
import simplejson

from orionframework.media.serializers import *
from orionframework.media.services import ServiceDocument, ServiceImage
from orionframework.utils import lists


class MediaServiceMixin(object):
    """
    shared functionality for services to create and destroy media objects
    """

    def create_media(self, record, file, category=None, **kwargs):
        """
        @param record: parent record that the media belongs to

        @param file: file that is being attached as a document/image

        @param category: multiple types of files can be uploaded to a record and
                         when this happens we need to pass in the file category
        """

        try:
            image = PILImage.open(file)
            image.verify()
            image.close()

            service = record.images

        except:
            service = record.documents

        media = service.create(category=category, file=file, **kwargs)

        return media

    def update_media(self, record, media_id, media_type, **kwargs):
        """
        Update media information such as name or description for the given
        media object within the given record.

        Note that updating media's file is not supported. This can only be done
        by deleting the existing file and adding a new media record instead.
        """

        service = record.media_service_from_type(media_type)

        media = service.filter(id=media_id).get()

        service.update(media, **kwargs)

    def destroy_media(self, record, media_id, media_type):

        service = record.media_service_from_type(media_type)

        service.delete(id__in=[media_id])


class MediaViewMixin(object):
    list_media_serializer_class = MediaSerializer
    create_media_serializer_class = MediaSerializer
    update_media_serializer_class = DocumentSerializer
    media_service_class = MediaServiceMixin
    """
    shared functionality for views to interact with media objects
    """

    @action(detail=True, methods=["get"], url_path="media")
    def list_media(self, request, pk):

        return self.list_media_by_type(request, pk, None)

    @action(detail=True, methods=["get"], url_path="media/(?P<media_type>[-\w]+)")
    def list_media_by_type(self, request, pk, media_type):
        """
        Retrieve all media documents attached to the underlying record.

        @param media_type: the type of media (image|document)
        """

        instance = self.get_object()

        media = instance.get_media(media_type)

        serializer = self.list_media_serializer_class(instance=media, many=True)

        return Response(serializer.data)

    @action(detail=True, methods=["delete"], url_path="media/destroy/(?P<media_id>[\d+]+)/(?P<media_type>[-\w]+)")
    def destroy_media(self, request, pk, media_id, media_type):
        """
        Destroys an existing media entry within the given object, permanently 
        deleting all of its metadata and attached files - including thumbnails 
        for images.
        
        @param media_id: the media's primary key
        
        @param media_type: the type of media (image|document)
        """

        instance = self.get_object()

        service = self.media_service_class()

        service.destroy_media(instance, media_id, media_type)

        return Response({})

    @action(detail=True, methods=["post"], url_path="media/create",
            parser_classes=(FormParser, MultiPartParser, FileUploadParser))
    def create_media(self, request, pk, *args, **kwargs):
        """
        Attach a new media content to the bounding record.
                    
        @param metadata: An array of objects (JSON), each object containing name
            of the document being uploaded. Note that while sending multiple files,
            both file and metadata should match size and order.
        """

        record = self.get_object()

        service = self.media_service_class()

        metadata = simplejson.loads(request.data.get("metadata")) if "metadata" in request.data else None

        documents = list()

        i = 0

        for file in request.data.values():

            if not hasattr(file, "file"):
                continue

            params = {}

            if metadata:
                params.update(metadata[i])

            documents.append(service.create_media(record, file, **params))

            i += 1

        serializer = self.create_media_serializer_class(instance=documents, many=True)

        return Response(serializer.data, status=201)

    @action(detail=True, methods=["patch"], url_path="media/update/(?P<media_id>[\d+]+)/(?P<media_type>[-\w]+)")
    def update_media(self, request, pk, media_id, media_type, *args, **kwargs):
        """
        Update data for an existing media record. Notice that updating the
        file itself is not supported.
        """

        record = self.get_object()

        service = self.media_service_class()

        serializer = self.update_media_serializer_class(data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)

        service.update_media(record, media_id, media_type, **serializer.data)

        return Response(status=status.HTTP_200_OK)


class MediaCategorizedViewMixin(MediaViewMixin):
    @action(detail=True, methods=["put"], url_path="media/create/(?P<category>[^/.]+)",
            parser_classes=(FormParser, MultiPartParser, FileUploadParser))
    def create_media(self, request, pk, category, *args, **kwargs):
        """
        Attach a new media content to the bounding record under a given category.
        
        @param category: the media category used to indicate the type of asset being 
            attached to the record. 
                    
        @param metadata: An array of objects (JSON), each object containing name
            of the document being uploaded. Note that while sending multiple files,
            both file and metadata should match size and order.
        """

        metadata = simplejson.loads(request.data.get("metadata")) if request.data.has_key("metadata") else None

        instance = self.get_object()

        category = int(category)

        entries = list()

        i = 0

        for file in request.FILES.values():

            params = {}

            if metadata:
                params["name"] = metadata[i].get("name", None)
                params["description"] = metadata[i].get("description", None)

            entries.append(self.service.create_media(instance, file, category, **params))

            i += 1

        serializer = self.list_media_serializer_class(entries, many=True)

        return Response(serializer.data, status=201)


class MediaModelMixin(object):
    """
    shared functionality for models that manage orion media objects. 
    """

    def __init__(self, *args, **kwargs):

        super(MediaModelMixin, self).__init__(*args, **kwargs)

        # install services for retrieving case images and documents
        self.documents = ServiceDocument(parent=self)
        self.images = ServiceImage(parent=self)

    def media_service_from_type(self, media_type):
        """
        Look up for a media service based on its type
        
        @param type: the type of media service
        
        @return service for the given media type (either ServiceImage or ServiceDocument)
        """

        if media_type == "image":
            return self.images

        if media_type == "document":
            return self.documents

        raise Exception("Expected 'document' and 'image' as media type. Got instead: " + type)

    def get_media(self, media_type=None):

        media = self.media_service_from_type(media_type).all() if media_type else self.media

        media.sort(key=lambda item: item.filename)

        return media

    @property
    def media(self):
        """
        Encapsulate all media documents and images. If there are different categories
        of documents this method will need to be overriden.
        """
        return lists.flatten(self.documents.all(), self.images.all())

    def copy(self, **kwargs):
        """
        Copies all underlying documents under new instances/paths in the remote server.
        :param kwargs:
        :return:
        """

        new_model = super(MediaModelMixin, self).copy(**kwargs)

        for document in self.media:
            document.copy(parent_id=new_model.id)

        return new_model
