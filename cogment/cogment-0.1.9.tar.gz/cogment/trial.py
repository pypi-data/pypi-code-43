from types import SimpleNamespace
from cogment.api.common_pb2 import Feedback


class Actor:
    def __init__(self, actor_class, actor_id, id_in_class, trial):
        self.actor_class = actor_class
        self.actor_id = actor_id
        self.id_in_class = id_in_class

        self._feedback = []
        self.trial = trial

    def add_feedback(self, value, confidence, tick_id=None, user_data=None):
        if tick_id is None:
            tick_id = -1

        self._feedback.append((tick_id, value, confidence, user_data))


class Trial:
    def __init__(self, id, settings):
        self.id = id
        self.actors = SimpleNamespace(all=[])
        self.settings = settings
        self.tick_id = 0

        actor_id = 0
        for actor_class, count in self.settings.environment.actors:
            actor_list = []
            id_in_class = 0
            for i in range(count):
                actor = Actor(actor_class, actor_id, id_in_class, self)
                actor_list.append(actor)
                self.actors.all.append(actor)
                actor_id += 1
                id_in_class += 1

            setattr(self.actors, actor_class.name, actor_list)

    def _get_all_feedback(self):
        for actor in self.actors.all:
            a_fb = actor._feedback
            actor._feedback = []

            for fb in a_fb:
                re = Feedback(
                    actor_id=actor.actor_id,
                    tick_id=fb[0],
                    value=fb[1],
                    confidence=fb[2]
                )
                if fb[3] is not None:
                    re.content = fb[3].SerializeToString()

                yield re
