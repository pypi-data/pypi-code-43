name = "ghee"
__version__ = '0.0.1'


from .ghee import Ghee


def main():
    import sys
    _, url, *message = sys.argv

    message = ' '.join(message)

    print(f'Sending: {message}')
    print(f'via: {url}')
    print(Ghee(url).echo(message))