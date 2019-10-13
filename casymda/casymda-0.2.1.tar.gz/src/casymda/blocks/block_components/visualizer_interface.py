"""interface for base block visualizer"""
from abc import ABC, abstractmethod


class AbstractBlockVisualizer(ABC):
    """visualizer called from the visualizable baseblock"""

    @abstractmethod
    def animate_block(self, component, direction=None):
        """animate_block"""
        raise NotImplementedError()

    @abstractmethod
    def change_block_state(self, component, state, new_value):
        """change_block_state"""
        raise NotImplementedError()

    @abstractmethod
    def animate_entity_flow(self, entity, from_comp, to_comp):
        """animate_entity_flow"""
        raise NotImplementedError()

    @abstractmethod
    def destroy_entity_anim(self, entity):
        """destroy_entity_anim"""
        raise NotImplementedError()
