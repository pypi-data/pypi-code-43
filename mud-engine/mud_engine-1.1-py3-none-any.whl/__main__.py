if __name__ == "__main__":
    import sys
    import os
    from .game import Game
    import logging
    logging.basicConfig(level=logging.DEBUG)
    host = "127.0.0.1" if not (len(sys.argv) > 2 and sys.argv[1]) else sys.argv[1]
    port = 5000 if not (len(sys.argv) > 2 and sys.argv[2]) else sys.argv[2]
    mud = Game()
    mud.admins.append(os.environ.get('ADMIN', 'ben'))
    mud.run()
    sys.exit(0)
