import json
class Json:
  """
  处理json信息函数
  """
  def __init__(self,file_path="data.json"):
    self.file_path=file_path
  def save(self,token):
    """
    保存数据函数
    """
    with open(self.file_path,"w") as f:
      json.dump(token,f)
      # print("加载入文件完成...")
  def load(self):
    """
    加载数据
    """
    with open(self.file_path, "r") as json_file:
      data = json.load(json_file)
      return data


"""
#使用

Json().save_json(token)
Json().load_json()


"""