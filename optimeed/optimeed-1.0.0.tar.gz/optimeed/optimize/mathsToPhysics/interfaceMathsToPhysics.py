from abc import ABCMeta, abstractmethod
from optimeed.core.options import Option_class


class InterfaceMathsToPhysics(Option_class, metaclass=ABCMeta):
    """Interface to transform output from the optimizer to meaningful variables of the device"""

    @abstractmethod
    def fromMathsToPhys(self, xVector, theMachine, opti_variables):
        """
        Transforms an input vector coming from the optimization (e.g. [0.23, 4, False]) to "meaningful" variable (ex: length, number of poles, flag).

        :param xVector: List of optimization variables from the optimizer
        :param theMachine: :class:`~optimeed.InterfaceDevice.InterfaceDevice`
        :param opti_variables: list of :class:`~optimeed.optimize.OptimizationVariable.OptimizationVariable`
        """
        pass

    @abstractmethod
    def fromPhysToMaths(self, theMachine, opti_variables):
        """
        Extracts a mathematical vector from meaningful variable of the Device

        :param theMachine: :class:`~optimeed.InterfaceDevice.InterfaceDevice`
        :param opti_variables: list of :class:`~optimeed.optimize.OptimizationVariable.OptimizationVariable`
        :return: List of optimization variables
        """
        pass
