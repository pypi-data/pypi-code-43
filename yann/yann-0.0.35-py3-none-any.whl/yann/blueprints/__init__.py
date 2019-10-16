from typing import Dict



class Blueprint:
  @classmethod
  def from_state_dict(cls, d):
    pass

  def state_dict(self):
    pass

  def save(self):
    pass

  def load(self):
    pass

  def info(self) -> Dict:
    pass

  def train(self):
    pass

  def predict(self, inputs):
    pass

  def evaluate(self):
    pass