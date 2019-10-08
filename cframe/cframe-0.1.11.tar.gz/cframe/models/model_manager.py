class ModelManager(object):
    @classmethod
    def get_model(cls, config=None):
        # model_config = MODEL_DICT[config['name']]
        return config['model'](config['config'])

    @classmethod
    def get_loss(cls, config=None):
        # loss_config = LOSS_DICT[config['name']]
        return config['loss'](**config['config'])

