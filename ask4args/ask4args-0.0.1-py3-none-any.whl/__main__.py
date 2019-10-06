
from .cli import choose_class

def main():
    cls = choose_class()
    cls().run()

if __name__ == "__main__":
    main()
