from .base import ReboticsBaseProvider, remote_service


class ShelfCameraManagerProvider(ReboticsBaseProvider):
    @remote_service('')
    def send_new_file(self):
        self.session.post(

        )

    @remote_service('/api/token-auth/')
    def token_auth(self, username, password):
        json_data = self.session.post(data={
            'username': username,
            'password': password
        })
        self.set_token(json_data['token'])
        return json_data

    @remote_service('/api/folders/')
    def get_root_folders(self):
        return self.session.get()

    @remote_service('/api/camera-settings/')
    def camera_settings_options(self):
        return self.session.options()

    @remote_service('/api/camera-settings/')
    def camera_settings_list(self):
        return self.session.get()

    @remote_service('/api/camera-settings/')
    def add_camera_settings(self, retailer_codename, store_id, token, camera_type, folder, rotation=0):
        """
        Create camera settings entry.
        :param str retailer_codename:
        :param int store_id:
        :param str token:
        :param int camera_type:
        :param str folder:
        :return:
        """
        options = self.camera_settings_options()
        camera_type_choices = options['actions']['POST']['camera_type']['choices']
        assert camera_type in [i['value'] for i in camera_type_choices], \
            'You need to set camera_type based on choices {}'.format(
                [(i['value'], i['display_name']) for i in camera_type_choices]
            )

        return self.session.post(data={
            'retailer': retailer_codename,
            'store_id': store_id,
            'token': token,
            'camera_type': camera_type,
            'camera_folder': folder,
            'rotation': rotation,
        })

    @remote_service('/api/camera-settings/{camera_settings_id}/')
    def camera_settings_detail(self, camera_settings_id):
        return self.session.get(camera_settings_id=camera_settings_id)

    @remote_service('/api/camera-settings/{camera_settings_id}/add_roi/')
    def add_camera_roi(self, camera_settings_id,
                       aisle, section=None,
                       store_planogram_id=None, coordinates=None):
        data = {
            'aisle': aisle,
        }
        if section is not None:
            data['section'] = section

        if store_planogram_id is not None:
            data['store_planogram_id'] = store_planogram_id

        if coordinates is not None:
            assert len(coordinates) == 4, 'Coordinates should iterable and in format [x_min, y_min, x_max, y_max]'
            x_min, y_min, x_max, y_max = coordinates
            data.update({
                'x_min': x_min,
                'y_min': y_min,
                'x_max': x_max,
                'y_max': y_max,
            })

        return self.session.post(camera_settings_id=camera_settings_id, data=data)
