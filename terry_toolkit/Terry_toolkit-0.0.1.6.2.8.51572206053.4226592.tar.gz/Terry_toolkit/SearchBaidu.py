from MagicBaidu import MagicBaidu
import pprint

class SearchBaidu:
    """SearchBaidu 百度搜索结果抓取
    
    使用https://github.com/napoler/MagicBaidu
    """

    def __init__(self):
        print('kaishi')
        # self.text = text
        # self.salary = salary
        # Employee.empCount += 1

        # """ 你的 APPID AK SK """
    def get(self, keyword,start=0):
        """获取百度搜索结果

        >>> get(keyword)
        
        """
        mb = MagicBaidu()
        li=[]
        for i in mb.search(query=keyword,start=start):
            
            # print(mb.get_real_url(i['url']))
            i['url']=mb.get_real_url(i['url'])
            # print(i)
            li.append(i)
        # pprint.pprint(li)
        return li