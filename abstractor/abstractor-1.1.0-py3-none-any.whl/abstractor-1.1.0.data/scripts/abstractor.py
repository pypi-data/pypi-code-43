import argparse

class Abstractor():

    def __init__(self):

        parser = argparse.ArgumentParser(description="Generate AskOmics abstraction from a SPARQL endpoint")
        
        parser.add_argument("-e", "--endpoint", type=str, help="SPARQL enpoint url")
        parser.add_argument("-p", "--prefix", type=str, help="SPARQL prefix")        
        parser.add_argument("-u", "--uri", type=str, help="Prefix URI for :")

        self.args = parser.parse_args()

    def main(self):

        print("COUCOU")



if __name__ == '__main__':

    Abstractor().main()