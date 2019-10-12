import requests

class Bot:

    def botlink(self, bot_id):
        url = "https://mdbl.ml/botok/{}/data.json".format(bot_id)
        link = requests.get(url).json()
        return link['link']


if __name__ == '__main__':
    main()