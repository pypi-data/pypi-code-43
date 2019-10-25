from abc import ABC, abstractmethod
import traceback

from cogment.api.environment_pb2_grpc import EnvironmentServicer as Servicer
from cogment.api.environment_pb2 import (EnvStartRequest, EnvStartReply,
                                         EnvUpdateReply, EnvEndReply)
from cogment.api.common_pb2 import Feedback, ObservationData
from cogment.utils import list_versions

from types import SimpleNamespace, ModuleType
from typing import Any, Dict, Tuple

from cogment.trial import Trial


def create_action_data(settings):
    actions_by_actor_id = []
    actions_by_actor_class = SimpleNamespace()

    for actor_class, count in settings.environment.actors:
        actions_list = [actor_class.action_space() for _ in range(count)]

        actions_by_actor_id.extend(actions_list)
        setattr(actions_by_actor_class, actor_class.name, actions_list)

    return actions_by_actor_class, actions_by_actor_id


class Environment(ABC):
    VERSIONS: Dict[str, str]

    def __init__(self, trial: Trial):
        self.trial = trial

    def start(self, config):
        return self.trial.settings.environment.default_observation()

    def end(self):
        pass

    @abstractmethod
    def update(self, actions):
        pass


class EnvService(Servicer):
    def __init__(self, env_class, settings):
        assert issubclass(env_class, Environment)

        # We will be managing a pool of environments, keyed by their trial id.
        self._envs: Dict[str, Tuple[Any, Trial]] = {}
        self._env_config_type = settings.environment.config
        self._env_class = env_class
        self.settings: ModuleType = settings

        print("Environment service started")

    # The orchestrator is requesting a new environment
    def Start(self, request, context):
        try:
            trial_id = request.trial_id
            if not trial_id:
                raise Exception("You must send a trial_id")
            if trial_id in self._envs:
                raise Exception("trial already exists")

            print(f"spinning up new environment: {trial_id}")

            # build an action table.
            actions_by_actor_class, actions_by_actor_id = create_action_data(self.settings)

            # Instantiate the fresh environment
            trial = Trial(trial_id, self.settings)

            trial.actions_by_actor_class = actions_by_actor_class
            trial.actions_by_actor_id = actions_by_actor_id

            config = None
            if request.HasField("config"):
                if self._env_config_type is None:
                    raise Exception("This environment isn't expecting a config")

                config = self._env_config_type()
                config.ParseFromString(request.config.content)

            instance = self._env_class(trial)
            initial_observation = instance.start(config)

            self._envs[trial.id] = (instance, trial)

            # Send the initial state of the environment back to the client
            # (orchestrator, normally.)
            reply = EnvStartReply()
            reply.observation_set.tick_id = 0
            reply.observation_set.timestamp.GetCurrentTime()

            reply.observation_set.observations.append(ObservationData(
                content=initial_observation.SerializeToString(),
                snapshot=True
            ))

            reply.observation_set.actors_map.extend([0] * len(trial.actors.all))

            return reply
        except Exception:
            traceback.print_exc()
            raise

    def End(self, request, context):
        try:
            try:
                instance, trial = self._envs[request.trial_id]
                instance.end()
                del self._envs[request.trial_id]
                return EnvEndReply()
            except KeyError as err:
                raise Exception("trial does not exists")
        except Exception:
            traceback.print_exc()
            raise

    # The orchestrator is ready for the environemnt to move forward in time.
    def Update(self, request, context):
        try:
            try:
                instance, trial = self._envs[request.trial_id]
            except KeyError as err:
                raise Exception("trial does not exists")

            len_actions = len(request.action_set.actions)
            len_actors = len(trial.actions_by_actor_id)
            if len_actions != len_actors:
                raise Exception(f"Received {len_actions} actions but have {len_actors} actors")

            for i, action in enumerate(trial.actions_by_actor_id):
                action.ParseFromString(request.action_set.actions[i])

            # Advance time
            delta = instance.update(trial.actions_by_actor_class)

            # This must be done AFTER the update, as calls to
            # actor.add_feedback must refer to the past.
            trial.tick_id += 1

            # Send the reply to the requestor.
            reply = EnvUpdateReply()

            reply.observation_set.tick_id = trial.tick_id
            reply.observation_set.timestamp.GetCurrentTime()

            reply.observation_set.observations.append(ObservationData(
                content=delta.SerializeToString(),
                snapshot=False
            ))

            reply.observation_set.actors_map.extend([0] * len(trial.actors.all))
            reply.feedbacks.extend(trial._get_all_feedback())

            return reply
        except Exception:
            traceback.print_exc()
            raise

    def Version(self, request, context):
        try:
            return list_versions(self._env_class)
        except Exception:
            traceback.print_exc()
            raise
