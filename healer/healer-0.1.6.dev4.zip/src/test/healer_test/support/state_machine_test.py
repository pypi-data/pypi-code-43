import enum

from healer.support.state_machine import *


@enum.unique
class Event(EventEnum):
    START = enum.auto()
    FINISH = enum.auto()


@enum.unique
class StateFun(StateEnum):
    IDLE = enum.auto()
    WORKING = enum.auto()
    TERMINATED = enum.auto()


class Machine(MachineBase):

    def process_start(self):
        print("process_start")
        raise RuntimeError(f"Bada-Boom")

    def process_finish(self):
        print("process_finish")

    Event.START.when(StateFun.IDLE).then(StateFun.WORKING).invoke(process_start)
    Event.FINISH.when(StateFun.WORKING).then(StateFun.TERMINATED).invoke(process_finish)


def test_base():
    print()

    print(list(Event))
    print(list(StateFun))

    machine = Machine(state=StateFun.IDLE)
    print(machine)
    print(machine.machine_table)

    machine.machine_fire_event(Event.FINISH)

    machine.machine_fire_event(Event.START)
    machine.machine_fire_event(Event.START)

    machine.machine_fire_event(Event.FINISH)
    machine.machine_fire_event(Event.FINISH)

    machine.machine_fire_event(Event.START)
