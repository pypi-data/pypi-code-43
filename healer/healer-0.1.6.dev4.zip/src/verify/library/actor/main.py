
import pykka


class Greeter(pykka.ThreadingActor):

    def on_receive(self, message):
        print(f'message: {message}')


actor_ref = Greeter.start()

actor_ref.tell("hello")

actor_ref.stop
