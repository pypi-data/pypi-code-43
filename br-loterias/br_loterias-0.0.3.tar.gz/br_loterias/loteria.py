import requests
from bs4 import BeautifulSoup 
import pandas as pd


class Loteria:

    def __init__(self):
        self.url = "https://noticias.uol.com.br/loterias/{}/"
        self.jogos = [ 'mega-sena', 'quina', 'lotofacil', 'lotomania', 'dupla-sena',\
                'timemania', 'dia-de-sorte', 'loteca', 'loteria-federal','lotogol' ]
        self.columns = ['concurso','data','numeros','ganhador','valor','url']        

    def jogos(self):
        page  = requests.get(self.url.format("mega-sena"),headers = {'User-Agent': 'Mozilla/5.0'})
        soup  = BeautifulSoup(page.text,'html.parser')
        return [li.text.strip().replace(' ','-') for li in soup.find(class_='content-scroll').find_all('li')]

    def jogos2(self):
        return self.jogos

    def megasena(self):
        return self.premio('mega-sena')

    def quina(self):
        return self.premio('quina')

    def lotofacil(self):
        return self.premio('lotofacil') 

    def lotomania(self):
        return self.premio('lotomania')

    def duplasena(self):
        return self.premio('dupla-sena')

    def timemania(self):
        return self.premio('timemania')

    def diadesorte(self):
        return self.premio('dia-de-sorte')

    def loteriafederal(self):
        page = requests.get(self.url.format("loteria-federal"),headers = {'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(page.text,'html.parser')

        info    = soup.find_all('div',class_='lottery-info')
        # numbers = [s.text for s in soup.find_all('div',class_="lt-result")[0].find_all('div')]
        # winners = soup.find('div',class_='winners')
        acc_value = soup.find('div',class_='alignCenterValor')
        
        return (*info[0].text.split(' | '),'','', acc_value.text,self.url.format("loteria-federal")) 

    def loteca(self):
        page = requests.get(self.url.format("loteca"),headers = {'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(page.text,'html.parser')

        info    = soup.find_all('div',class_='lottery-info')
        numbers = [s.text for s in soup.find_all('div',class_="linecard")]
        winners = soup.find('div',class_='winners').text
        acc_value = soup.find('div',class_='alignCenterValor')
        
        return (*info[0].text.split(' | '), numbers, winners, acc_value.text,self.url.format("loteca")) 

    def lotogol(self):
        page = requests.get(self.url.format("lotogol"),headers = {'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(page.text,'html.parser')

        info    = soup.find_all('div',class_='lottery-info')
        numbers = [s.text for s in soup.find_all('div',class_="card")]
        winners = soup.find('div',class_='winners').text
        acc_value = soup.find('div',class_='alignCenterValor')
        
        return (*info[0].text.split(' | '),numbers,winners, acc_value.text, self.url.format("loteca"))         

    def premio(self,jogo):
        """
            'mega-sena',
            'quina',
            'lotofacil',
            'lotomania',
            'dupla-sena',
            'timemania',
            'dia-de-sorte',
            'loteria-federal',
            'loteca',
            'lotogol'
        """
        page = requests.get(self.url.format(jogo),headers = {'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(page.text,'html.parser')

        info    = soup.find_all('div',class_='lottery-info')

        if jogo == 'loteria-federal':
            numbers = []
            winners = ''
        elif jogo == 'loteca':
            numbers = [s.text for s in soup.find_all('div',class_="linecard")]
            winners = soup.find('div',class_='winners').text
        elif jogo == 'lotogol':
            numbers = [s.text for s in soup.find_all('div',class_="card")]
            winners = soup.find('div',class_='winners').text
        else:
            numbers = [s.text for s in soup.find_all('div',class_="lt-result")[0].find_all('div')]
            winners = soup.find('div',class_='winners').text
            
        acc_value = soup.find('div',class_='alignCenterValor')
        
        return (*info[0].text.split(' | '), numbers, winners, acc_value.text, self.url.format(jogo))  


    def to_df(self):
        jogos = self.jogos
        names = self.columns
        data = []
        for j in jogos:
            try:
                data.append( self.premio(j) )
            except:
                data.append(names)

        return pd.DataFrame(data=data,columns=names, index=jogos)
