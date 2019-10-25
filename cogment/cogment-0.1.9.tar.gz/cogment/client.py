from cogment.api.orchestrator_pb2 import (
    TrialStartRequest, TrialFeedbackRequest, TrialActionRequest,
    TrialEndRequest)

from cogment.api.orchestrator_pb2_grpc import TrialStub
from cogment.api.common_pb2 import Action

from cogment.delta_encoding import DecodeObservationData

from cogment.trial import Trial
import grpc


class ClientTrial(Trial):
    def __init__(self, conn, trial_start_rep, settings, actor_class,
                 initial_observation):
        super().__init__(trial_start_rep.trial_id, settings)
        self.connection = conn
        self.observation = initial_observation
        self.actor_id = trial_start_rep.actor_id
        self.actor_class = actor_class

    # Perform an action on the trial, and advance time
    def do_action(self, action):
        self.flush_feedback()

        # Send the update to the orchestrator
        update = self.connection.stub.Action(TrialActionRequest(
            trial_id=self.id,
            actor_id=self.actor_id,
            action=Action(content=action.SerializeToString())))

        self.observation = DecodeObservationData(
            self.actor_class,
            update.observation.data,
            self.observation)

        self.tick_id = update.observation.tick_id
        # Return the latest observation
        return self.observation

    # Kill the trial
    def end(self):
        self.flush_feedback()
        self.connection.stub.End(TrialEndRequest(trial_id=self.id))

    def flush_feedback(self):
        feedbacks = list(self._get_all_feedback())

        if feedbacks:
            req = TrialFeedbackRequest(trial_id=self.id)

            req.feedbacks.extend(feedbacks)
            self.connection.stub.GiveFeedback(req)


class _Connection_impl:
    def __init__(self, stub, settings):
        if not settings:
            raise Exception("missing settings")

        if not stub:
            raise Exception("missing grpc connection stub")

        self.stub = stub
        self.settings = settings

    def start_trial(self, actor_class, env_cfg=None):
        req = TrialStartRequest()

        if env_cfg:
            print("encoding config")
            req.config.content = env_cfg.SerializeToString()

        rep = self.stub.Start(req)

        observation = DecodeObservationData(
            actor_class, rep.observation.data)

        return ClientTrial(
            self, rep, self.settings, actor_class, observation)


class Connection(_Connection_impl):
    def __init__(self, settings, endpoint):
        channel = grpc.insecure_channel(endpoint)
        stub = TrialStub(channel)
        super().__init__(stub, settings)
