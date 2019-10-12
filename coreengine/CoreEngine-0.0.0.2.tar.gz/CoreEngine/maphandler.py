import pygame


class Buffered2DMapHandler(object):
    def __init__(self,
                 data,  # containing DataAdapter instance
                 size,  # viewing rect size
                 clamp_camera=True
                 ):
        # default options
        self.data = data
        self.clamp_camera = clamp_camera

        # private attributes
        self._buffer = None
        self._map = None
        self._map_rect = None
        self._zoom_level = 1.0
        self.camera = pygame.Rect(0, 0, 0, 0)
        self._size = None

        self.data.prepare_data()
        self.set_size(size)

    def set_size(self, size):
        """
        sets size of screen init buffer etc - expensive function
        :param size: (width:int,height:int)
        :return: None
        """
        buffer_size = self._calculate_zoom_buffer_size(size, self._zoom_level)
        self._size = size
        self._initialize_buffers(buffer_size)

    @staticmethod
    def _calculate_zoom_buffer_size(size, value):
        """
        calculates zoom buffer size
        :param size: (width :int, height:int)
        :param value: zoom level int
        :return: zoom buffersize
        """
        if value <= 0:
            raise ValueError("zoom must'nt be zero or less")
        value = 1.0 / value
        return int(size[0] * value), int(size[1] * value)

    def _initialize_buffers(self, buffer_size):
        """
        initializes buffers
        :param buffer_size: (width :int,height:int)
        :return: None
        """
        tile_width, tile_height = self.data.tile_size  # get tile size
        map_width, map_height = self.data.map_size  # get map size
        self._map = pygame.Surface([map_width * tile_width, map_height * tile_height])  # create world buffer
        self._map_rect = self._map.get_rect()  # sets world rect

        self.data.force_redraw(self._map)  # force redraw of data_renderer

        self._create_buffers(buffer_size)

    def _create_buffers(self, buffer_size):
        """
        creates buffers
        :param buffer_size: (width,height)
        :return: None
        """
        # TODO set better values for camera topleft (zoom is zooming to topleft corner)
        self.camera = pygame.Rect(*self.camera.topleft, *buffer_size)
        self._buffer = pygame.Surface(buffer_size)  # sets map buffer

    def render(self, surface):
        """
        select render mode by zoom level
        :param surface: pygame.Surface to render
        :return: None
        """
        if self._zoom_level == 1.0:
            self.data.render_animated_tiles(self._map, self.camera)  # render animations
            self._render_map(surface)  # render map onto surface
            self.data.render(surface, self.camera)  # render other data as though sprites
        else:
            self.data.render_animated_tiles(self._map, self.camera)  # render animations
            self._render_map(self._buffer)  # render map onto buffer
            self.data.render(self._buffer, self.camera)  # render other data as though sprites
            pygame.transform.scale(self._buffer, surface.get_size(), surface)  # scale buffer and render on surface

    def _render_map(self, surface):
        """
        renders clip of _map to surface
        :param surface:  pygame.Surface
        :return: None
        """
        surface.blit(self._map, (0, 0), (*self.camera.topleft, *surface.get_size()))

    def update(self, delta=None):
        """
        updates sprites and tiles
        :param delta: delta time
        :return:
        """
        self.data.update(delta)

    def scroll(self, vector):
        """
        scroll by vector
        :param vector: (shiftvaluex,shiftvaluey)
        :return: None
        """
        self.center((vector[0] + self.camera.centerx, vector[1] + self.camera.centery))

    def center(self, coords):
        """
        center camera to coords
        :param coords: (float,float)
        :return: None
        """
        x, y = round(coords[0]), round(coords[1])
        self.camera.center = x, y

        if self.clamp_camera:
            self.camera.clamp_ip(self._map_rect)

    @property
    def zoom(self):
        """
        zoom property
        :return: None
        """
        return self._zoom_level

    @zoom.setter
    def zoom(self, value):
        """
        zoom setter
        :param value: zoom value increase/decrease
        :return: None
        """
        if value <= 0:
            print("[WARNING] ZOOM LEVEL IS 0 OR LESS - sizing to 0.25 ")
            value = .25
        zoom_buffer_size = self._calculate_zoom_buffer_size(self._size, value)
        self._zoom_level = value
        self._create_buffers(zoom_buffer_size)
        self.center((0, 0))
