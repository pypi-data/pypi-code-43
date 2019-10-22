from .clickbot import Clickbot as Bot

def main():
    bot = Bot()
    bot.configure()
    bot.run()

if __name__ == "__main__":
    main()
