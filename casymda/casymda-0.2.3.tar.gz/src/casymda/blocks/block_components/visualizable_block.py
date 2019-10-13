""" visualizable block """
from abc import abstractmethod
from typing import Dict, Optional, Tuple

from simpy import Environment

from casymda.blocks.block_components.block import Block
from casymda.blocks.block_components.visualizer_interface import \
    BlockVisualizer


class VisualizableBlock(Block):
    """ extends block by visualization-related behavior """

    def __init__(self, env: Environment,
                 name: str,
                 block_capacity=float('inf'),
                 xy: Tuple[int, int] = None,
                 ways: Dict = None
                 ):

        super().__init__(env, name,
                         block_capacity=block_capacity)

        # injected later if required:
        self.visualizer: Optional[BlockVisualizer] = None

        self.ways = ways
        self.xy_position = xy

        self.queuing: bool = True  # read by visualizer

    def on_block_change(self):
        """ animates the block, including e.g. it's contents """
        super().on_block_change()
        if self.visualizer is not None:
            self.visualizer.animate_block(self)

    def on_block_state_change(self, state, new_value):
        super().on_block_state_change(state, new_value)
        if self.visualizer is not None:
            self.visualizer.change_block_state(self, state, new_value)

    def on_entity_movement(self, entity, successor):
        super().on_entity_movement(entity, successor)
        if self.visualizer is not None:
            self.visualizer.animate_entity_flow(entity, self, successor)

    @abstractmethod
    def actual_processing(self, entity):
        raise NotImplementedError()
