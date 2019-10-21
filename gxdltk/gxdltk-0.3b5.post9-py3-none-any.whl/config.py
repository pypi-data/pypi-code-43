class TrainConfig(object):
    """
    Config in Training Mode
    """

    def __init__(self):
        self.lr = 0.0
        self.l2norm = 0.0
        self.epoch = 1
        self.batch_size = 1
        self.device = -1 # set >0 to use GPU

    def display(self):
        print("***Train Config details***")
        print(f"learning rate: {self.lr}")
        print(f"Weight decay: {self.l2norm}")
        print(f"GPU Support: {'YES' if self.device>0 else 'NO'}")
        print(f"Batch Size: {self.batch_size}")
        print(f"Training Epoch: {self.epoch}")


class ModelConfig(object):
    """
    Configuration in model setting
    """
    def __init__(self):
        self.input_size = 0
        self.hidden_size = 0
        self.embd_size = 0
        self.output_size = 0
    def display(self):
        pass


class DataConfig(object):
    """
    Data Config
    """
    def __init__(self):
        self.kg = ""
        self.text = ""
        self.question = ""
        self.process = dict()

    def set_process(self, **kwargs):
        """
        Config process data
        """
        for k in kwargs.keys():
            self.process[k] = kwargs[k]

    def display(self):
        pass


class Config(object):
    """
    Total Model and Training Config Class
    """

    def __init__(self, train_cfg: TrainConfig=None,
                 model_cfg: ModelConfig=None,
                 data_cfg: DataConfig=None):
        self.train_cfg = TrainConfig()
        self.model_cfg = ModelConfig()
        self.data_cfg = DataConfig()

    def display(self):
        self.data_cfg.display()
        self.model_cfg.display()
        self.train_cfg.display()
