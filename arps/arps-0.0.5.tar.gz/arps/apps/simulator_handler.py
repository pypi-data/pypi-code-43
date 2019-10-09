import logging
import os
import asyncio
import time
import pathlib
from functools import partial
from contextlib import contextmanager
import json
from zipfile import ZipFile
import io

from arps.core.clock import Clock
from arps.core.simulator.simulator import Simulator


class SimulatorHandler:
    '''
    Class to encapsute operations of the simulator
    '''

    def __init__(self, clock: Clock, simulator_environment) -> None:
        self.clock = clock
        event_queue = simulator_environment.event_queue_loader.queue()
        self.resources_table = simulator_environment.resources_table
        self.simulator = Simulator(event_queue, self.clock)
        self.clock.add_listener(self.simulator.step)
        self.sim_log_name = None
        self.simulator_results_path = simulator_environment.results_path
        self.running = False
        self.clock_run_task = None
        self.logger = logging.getLogger(self.__class__.__name__)

    def run(self):
        '''
        starts epoch run and simulator

        Return message about the status
        '''
        self.logger.info('starting sim handler')

        if not self.running:
            asyncio.create_task(self.async_run())
            self.clock_run_task = asyncio.ensure_future(self.clock.run())

        self.running = True
        self.logger.info(f'Simulator is running')

    async def async_run(self):
        '''Setup sim to run asynchronously

        '''

        self.logger.info('Waiting for sim to finish')

        with self.setup():
            await self.simulator._finished.wait()
            await self.clock.wait_for_notified_tasks()

            self.logger.info('Sim has finished')

            # wait 10 steps until finish the
            future = self.clock.epoch_time.epoch + 10
            while self.clock.epoch_time.epoch < future:
                await asyncio.sleep(0)

            self.stop()

    @contextmanager
    def setup(self):
        '''
        Prepare the environment for running a new simulation
        '''
        if not os.path.exists(self.simulator_results_path):
            self.logger.info(f'Saving sim result to {self.simulator_results_path}')
            os.makedirs(self.simulator_results_path)

        current_time = time.strftime('%Y%m%d-%H%M%S')
        LOG_TEMPLATE = '{time}_{pid}_sim_results.log'
        self.sim_log_name = os.path.join(self.simulator_results_path,
                                         LOG_TEMPLATE.format(time=current_time, pid=os.getpid()))

        self.logger.info(f'Sim result log filename is {self.sim_log_name}')
        sim_log_file = open(self.sim_log_name, 'a')
        sim_log_file.write('env;identifier;epoch;value;category;modifier;type\n')

        def log_resources_modification(log_file, event):
            entry = f'{event.env};{event.identifier};{event.epoch};{event.value};{event.name};{str(event.modifier_id)};{event.type}\n'
            log_file.write(entry)

        track_resources_modification = partial(log_resources_modification,
                                               sim_log_file)
        self.simulator.reset()
        self.resources_table.reset()

        self.logger.info(f'adding resources tracking')
        self.resources_table.add_resources_listener(track_resources_modification)

        yield

        self.logger.info(f'close file name {sim_log_file.name}')
        sim_log_file.close()
        self.logger.info(f'removing resources tracking')
        self.resources_table.remove_resources_listener(track_resources_modification)

    def status(self):
        '''Retrieve the current state of the simulation, i. e., running or
        stopped

        '''
        state = 'running' if self.running else 'stopped'
        self.logger.info(f'On sim status invocation: {state}')

        return state

    def stop(self):
        '''Stop simulation
        '''
        if self.running:
            self.clock_run_task.cancel()

        self.running = False

    def simulation_results(self):
        '''Return the path to the result of the simulation.

        If the simulation is still running, or the log is nowhere to
        be found, raise RuntimeError

        '''
        if self.running:
            raise RuntimeError('Simulation is still running; request stop before requesting result')

        if not (self.sim_log_name and os.path.exists(self.sim_log_name)):
            raise RuntimeError('Simulation log not found')

        return self.sim_log_name

    def metadata(self):
        '''Returns a dictionary containing the resource as key and how to
        interpret it as value

        '''
        metadata = dict()
        for env in self.resources_table.environments.values():
            for resources in env.categories.values():
                for resource in resources.values():
                    resource_name = resource.__class__.__name__
                    valid_range = resource.category.valid_range
                    value_type = resource.category.value_type.name
                    metadata[resource_name] = {'range': valid_range, 'type': value_type}
        return metadata

    def result(self):
        sim_results_location = pathlib.Path(self.simulation_results())
        zip_file = io.BytesIO()
        with ZipFile(zip_file, 'w') as result_bundle:
            result_bundle.write(sim_results_location)
            result_bundle.writestr(str(sim_results_location.with_suffix('.json')), json.dumps(self.metadata()))
        zip_file.seek(0)
        return zip_file.getvalue(), str(sim_results_location.with_suffix('.zip'))

    def save(self, agent_managers):
        '''
        Save actions performed by agent managers and return it for
        future execution

        '''
        result = {}
        for agent_manager_id, tracked_actions in agent_managers.items():
            commands = list()
            for action, params in tracked_actions:
                command = {'command': action,
                           'params': {k: v for (k, v) in params}}
                commands.append(command)
            result[agent_manager_id] = commands
        return result
