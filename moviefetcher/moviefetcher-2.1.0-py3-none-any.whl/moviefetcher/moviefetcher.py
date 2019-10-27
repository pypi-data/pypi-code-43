try:
    from bs4 import BeautifulSoup
    from urllib.request import urlopen
    import pandas as pd

except Exception as e:
    print("Some Modules are Missing {}".format(e))


class Stack(object):
    def __init__(self):
        self.data = []


class WebCrawler(object):

    def __init__(self, year):

        self.year = year
        self.base_url = "https://www.rottentomatoes.com/top/bestofrt/?year="+str(self.year)
        self.client = urlopen(self.base_url)
        self.stack = Stack()

    def scrapper(self):

        page_html=self.client.read()
        soup=BeautifulSoup(page_html, 'html.parser')
        self.client.close()
        containe = soup.find('table',  class_='table')

        movie_names = containe.find_all(class_='unstyled articleLink')
        movie_ratings=containe.find_all('span',class_='tMeterScore')

        for i in range(0,100):

            data = "{}={}".format(movie_names[i].string.strip(),
                                  movie_ratings[i].string)

            data = tuple(data.split("="))
            self.stack.data.append(data)

        return self.stack


class MovieRatings(object):

    def __init__(self, year):
        self.year = year
        self.webcrawler = WebCrawler(year=year)
        self.stack = self.webcrawler.scrapper()

    def PrintData(self):
        print(self.stack.data)
        df = pd.DataFrame(self.stack.data, columns=["Title", "Ratings"])
        print(df)

    def saveAsCsv(self):
        df = pd.DataFrame(self.stack.data, columns=["Title", "Ratings"])
        df.to_csv("Movies.csv")
        print("Created csv File ")

    def saveAsJson(self):
        df = pd.DataFrame(self.stack.data, columns=["Title", "Ratings"])
        df.to_json("Movie.json")
        print("saved a json file ")

