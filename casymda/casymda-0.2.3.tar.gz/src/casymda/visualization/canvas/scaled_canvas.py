"""canvas"""

from abc import abstractmethod


class ScaledCanvas():
    """overview of canvas methods called from visualizer"""

    @abstractmethod
    def load_image_file(self, path: str):
        """takes file path and returns loaded image file reference"""

    @abstractmethod
    def create_image(self, x_coord: int, y_coord: int, image_file, anchor="c"):
        """places image on canvas and returns image reference"""

    @abstractmethod
    def create_text(self, x_coord: int, y_coord: int,
                    text: str = "", anchor: str = "se",
                    fill: str = "black", font: str = "Helvetica 16"):
        """places text on canvas and returns reference"""

    @abstractmethod
    def delete(self, element_id: int) -> bool:
        """deletes element and returns True if deleted"""

    @abstractmethod
    def set_coords(self, element_id: int, x_y: tuple):
        """places the given element at a given position"""

    @abstractmethod
    def set_text_value(self, element_id: int, text: str):
        """changes the elements text"""

    @abstractmethod
    def get_width(self) -> int:
        """returns width"""

    @abstractmethod
    def get_height(self) -> int:
        """returns heigth"""

    @staticmethod
    def _scale_coords(x_y: tuple, scale: float):
        """returns tuple values multiplied by factor"""
        return tuple(map(lambda c: int(c * scale), x_y))
