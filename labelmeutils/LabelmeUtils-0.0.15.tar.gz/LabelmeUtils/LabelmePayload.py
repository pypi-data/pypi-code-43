from .Shapes import ShapeFactory
from .ShapeIterator import ImageShapeIterator, CroppedImageIterator
import json
from PIL import Image
from io import BytesIO
import base64


class LabelmePayload:

    def __init__(self):
        self.version = "3.11.2"
        self.flags = {}
        self.shapes = []
        self.imagePath = ""
        self.imageData = ""
        self.imageHeight = 0
        self.imageWidth = 0
        self.lineColor = [0, 255, 0, 128]
        self.fillColor = [255, 0, 0, 128]
        self.otherData = {}

    @staticmethod
    def from_json(json_payload, strict=True):
        hold = LabelmePayload()
        hold._set_data_from_json(json_payload, strict=strict)
        return hold

    @staticmethod
    def from_file_path(file_path, strict=True):
        import json
        hold = LabelmePayload()
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                hold._set_data_from_json(data, strict=strict)
            return hold
        except FileNotFoundError:
            return None

    @staticmethod
    def from_json_bytes(json_bytes, strict=True):
        if len(json_bytes) <= 0:
            return None
        try:
            json_payload = json.loads(json_bytes.decode('utf8'))
            return LabelmePayload.from_json(json_payload, strict)
        except AssertionError:
            return None

    @staticmethod
    def from_file_handler(file_handler, strict=True):
        import json
        hold = LabelmePayload()
        data = json.load(file_handler)
        hold._set_data_from_json(data, strict=strict)
        return hold

    @staticmethod
    def load_pil_image(file_path):
        blank_payload = LabelmePayload()
        with open(file_path) as p:
            image_data = json.load(p)["imageData"]
        blank_payload.imageData = image_data
        return blank_payload.get_image()

    def to_dict(self):
        return {
            "version": self.version,
            "flags": self.flags,
            "shapes": [shape.to_dict() for shape in self.shapes],
            "imagePath": self.imagePath,
            "imageData": self.imageData,
            "imageHeight": self.imageHeight,
            "imageWidth": self.imageWidth,
            "lineColor": self.lineColor,
            "fillColor": self.fillColor,
            **self.otherData,
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    def _set_data_from_json(self, json_payload, strict=True):
        attrib_fields = ["version", "flags"]
        for field in attrib_fields:
            assert not strict or field in json_payload, "Json payload does not contain:" + field
            setattr(self, field, json_payload[field])

        required_fields = ["imagePath", "imageData", "imageHeight", "imageWidth", "lineColor", "fillColor"]
        for field in required_fields:
            assert not strict or field in json_payload, "Json payload does not contain:" + field
            setattr(self, field, json_payload[field])

        self._load_shapes_from_json(json_payload)

        for key, value in json_payload.items():
            if key not in required_fields and key not in required_fields and key != "shapes":
                self.otherData[key] = value

    def _load_shapes_from_json(self, json_payload):
        if "shapes" not in json_payload:
            return
        shapes = json_payload["shapes"]
        assert isinstance(shapes, (list,)), "Shapes object is not of type list"

        self.shapes = []
        for shape_json in shapes:
            self.shapes.append(ShapeFactory.from_json(shape_json))

    def get_image(self):
        return Image.open(BytesIO(base64.b64decode(self.imageData)))

    def draw_shapes(self):
        hold = self.get_image()
        for shape in self.shapes:
            shape.draw_shape(hold)
        return hold

    def get_cropped_images(self, padding=None):
        return list(self.cropped_image_generator(padding))

    def cropped_image_generator(self, padding=None, return_shape=False):
        return ImageShapeIterator(self.shapes, self.get_image(), padding) if return_shape else \
            CroppedImageIterator(self.shapes, self.get_image(), padding)

    def update_image(self, image):
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        b64str = base64.b64encode(buffered.getvalue())

        self.imageData = str(b64str, "utf-8")
        self.imageHeight = image.height
        self.imageWidth = image.width
