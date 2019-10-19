from lino_xl.lib.courses.workflows import *

from .choicelists import ReminderStates

ReminderStates.draft.add_transition(required_states="ok final")
ReminderStates.sent.add_transition(required_states="draft")
ReminderStates.ok.add_transition(required_states="sent")
ReminderStates.final.add_transition(required_states="sent")
ReminderStates.cancelled.add_transition(
    required_states="draft sent ok final")
