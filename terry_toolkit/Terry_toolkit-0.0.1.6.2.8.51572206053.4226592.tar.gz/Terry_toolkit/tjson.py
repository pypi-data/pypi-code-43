import json
class Json:
  """
  处理json信息函数
  """
  def __init__(self,file_path="data.json"):
    self.file_path=file_path
  def save(self,data):
    """
    保存数据函数
    逐行写入
    >>> data=[{'a':'ess'}]
    """
    with open(self.file_path, 'a+', encoding='utf-8') as f:
      for item in data:
        line = json.dumps(item, ensure_ascii=False)
        f.write(line+'\n')
  def load(self):
    """
    加载数据
    """
    # with open(self.file_path, "r") as json_file:
    #   data = json.load(json_file)
    #   return data
    f = open(self.file_path,"r")  
    # lines = f.readlines()#读取全部内容  
    lines=[]
    for line in f.readlines():
      # line.replace("\n","")
      lines.append(json.loads(line[:-1]))
    return lines

"""
#使用
data=[{'a':'ess'}]
Json().save(data)
print(Json().load())


"""


