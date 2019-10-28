from functools import reduce


class ShapeIterator:
    def __init__(self, shapes):
        self.shapes = shapes
        self.filter_fns = []
        self.iter = iter(self.shapes)

    def __iter__(self):
        self.iter = iter(self.shapes)
        return self

    def __next__(self):
        shape = self.iter.__next__()
        while not reduce(lambda prev, fn: prev and fn(shape), self.filter_fns, True):
            shape = self.iter.__next__()
        return shape

    def filter(self, fn):
        """
        Filter elements with function
        :param fn: (shape) => boolean
        :return: ShapeIterator
        """
        self.filter_fns.append(fn)
        return self

    def set_filter_fns(self, fns):
        self.filter_fns = fns
        return self


class ImageShapeIterator(ShapeIterator):
    def __init__(self, shapes, image, padding=None):
        ShapeIterator.__init__(self, shapes)
        self.image = image
        self.padding = padding
        self.post_process_fns = []

    def __next__(self):
        shape = super().__next__()
        img = shape.crop_image(self.image, self.padding)
        return reduce(lambda prev, fn: fn(prev), self.post_process_fns, img), shape

    def post_process(self, fn):
        """
        Filter elements with function
        :param fn: (shape) => boolean
        :return: ShapeIterator
        """
        self.post_process_fns.append(fn)
        return self

    def set_post_process_fns(self, fns):
        self.post_process_fns = fns
        return self


class CroppedImageIterator(ImageShapeIterator):
    def __init__(self, shapes, image, padding=None):
        ImageShapeIterator.__init__(self, shapes, image, padding)

    def __next__(self):
        img, _ = super().__next__()
        return img
