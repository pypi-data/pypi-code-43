import hashlib
import uuid


class DocumentContentNode(object):
    """
    A Document Content Node identifies a section of the document containing logical
    grouping of information

    The node will have both text and HTML representation and can include n number of
    features
    """

    def __init__(self, content, content_html, children):
        self.content = content
        self.content_html = content_html

        self.children = children

        self.checksum = hashlib.md5(self.content.encode('utf-8')).hexdigest()
        self.features = []
        self.uuid = str(uuid.uuid1())

        self.add_feature("outline", "uuid", self.uuid)

    def add_feature(self, feature_type, name, value):
        if self.has_feature(feature_type, name):
            self.features.remove(self.get_feature(feature_type, name))

        self.features.append(DocumentContentNodeFeature(feature_type, name, value))

    def get_feature(self, feature_type, name):
        results = [i for i in self.features if i.feature_type == feature_type and i.name == name]
        return results[0] if len(results) > 0 else None

    def has_feature(self, feature_type, name):
        results = [i for i in self.features if i.feature_type == feature_type and i.name == name]
        return len(results) > 0

    def get_feature_value(self, feature_type, name):
        feature = self.get_feature(feature_type, name)
        return None if feature is None else feature.value


class DocumentContentNodeFeature(object):
    """
    A feature that has been added to a DocumentContentNode
    """

    def __init__(self, feature_type, name, value, description=None):
        self.feature_type = feature_type
        self.name = name
        self.value = value
        self.description = description
