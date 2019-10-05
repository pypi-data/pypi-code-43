"""
    PyJAMAS is Just A More Awesome Siesta
    Copyright (C) 2018  Rodrigo Fernandez-Gonzalez (rodrigo.fernandez.gonzalez@utoronto.ca)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from pyjamas.rimage.rimclassifier.rimclassifier import rimclassifier
from pyjamas.rml.rneuralnetmlp import RNeuralNetMLP


class nnmlp(rimclassifier):

    N_HIDDEN: int = 30
    L2: float = 0.
    EPOCHS: int = 100
    ETA: float = 0.001
    SHUFFLE: bool = True
    MINIBATCH_SIZE: int = 50

    def __init__(self, parameters: dict = None):
        super().__init__(parameters)

        n_hidden = parameters.get('n_hidden', nnmlp.N_HIDDEN)
        l2: float = parameters.get('l2', nnmlp.L2)
        epochs: int = parameters.get('epochs', nnmlp.EPOCHS)
        eta: float = parameters.get('eta', nnmlp.ETA)
        shuffle: bool = parameters.get('shuffle', nnmlp.SHUFFLE)
        minibatch_size: int = parameters.get('minibatch_size', nnmlp.MINIBATCH_SIZE)

        # Neural network/multilayer perceptron-specific parameters.
        self.classifier = parameters.get('classifier', RNeuralNetMLP(n_hidden, l2, epochs, eta,
                                                                     shuffle, minibatch_size,
                                                                     rimclassifier.DEFAULT_SEED))
