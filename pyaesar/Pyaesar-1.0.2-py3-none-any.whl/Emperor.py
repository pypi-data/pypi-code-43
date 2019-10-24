# copyright 2019. Triad National Security, LLC.
# All rights reserved.
#
# This program was produced under U.S.
# Government contract 89233218CNA000001
# for Los Alamos National Laboratory (LANL),
# which is operated by Triad National Security, LLC
# for the U.S. Department of Energy/National Nuclear Security Administration.
# All rights in the program are reserved by Triad National Security, LLC,
# and the U.S. Department of Energy/National Nuclear Security Administration.
# The Government is granted for itself and others acting on its behalf a
# nonexclusive, paid-up, irrevocable worldwide license in this material
# to reproduce, prepare derivative works, distribute copies to the public,
# perform publicly and display publicly, and to permit others to do so.
#
#
#
#
# This program is open source under the BSD-3 License.
#
# Redistribution and use in source and binary forms, with or
# without modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above
#     copyright notice, this list of conditions and the following disclaimer.
# 2.Redistributions in binary form must reproduce the above
#     copyright notice, this list of conditions and the
#     following disclaimer in the documentation and/or
#     other materials provided with the distribution.
# 3.Neither the name of the copyright holder nor the names
#     of its contributors may be used to endorse or promote
#     products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
#  THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


'''
This class is analogous to the multiprocess class. It distributes work among
the processors of the allocated nodes. The user can specify how many processors
they wish to use on each node. The verbosity of output (used for testing) can
also be specified
'''




import multiprocessing
import itertools
from mpi4py import MPI
import Pyaesar.Legions as Legions
from Pyaesar.utils import split_array
import logging

class Emperor():
    '''
    Distributes work among all the available processors.
    '''

    def __init__(
            self,
            nproc=multiprocessing.cpu_count(),
            default_logger=False):
        '''
        Args:
            nproc (int): number of processors to use for each rank
            verbose (bool): log additional information
        '''
        assert type(default_logger) == bool, "default_logger must be a boolean"
        assert type(nproc) == int, "Processors must be an int"

        if not default_logger:
            logging.basicConfig(filename='Deafult_Pyaesar_Logger.log',  level=logging.DEBUG)

        self.data = None
        self.comm = MPI.COMM_WORLD
        self.size = self.comm.Get_size()  # total ranks
        self.rank = self.comm.Get_rank()  # current one
        self.dataframe = None
        self.timeout = -1
        self.processor = nproc
        logging.info("current rank: {}".format(self.rank))
        logging.info("out of size:  {}".format(self.size))

    def command(self, orders, method, *args, order_args=None):
        '''
        Distributes commands evenly among the MPI ranks, waits for each rank to finish processing,
        collects each rank's output, and returns the results.

        Args:
            orders (function): Returns the data to be distributed
            method (function): Function to be applied on each data element
            args (iterable): Constant arguments passed to method (i.e. arguments other than the data element).
            order_args (iterable): The arguments to be passed to orders

        Returns:
            (tuple): tuple containing:

                data (list):
                    - On rank 0: the data that was retrieved with orders() and distributed
                    - On other ranks: None
                answer (list):
                    - On rank 0: the result of appling method to each element of data
                    - On other ranks: None
                rank (int):
                    the MPI rank of the process
        '''
        if self.rank == 0:
            logging.info("This is the Emperor with rank 0")
            logging.info("This Emperor also does work and will make its own Legion soon...")

            # Subdivide orders into equally sized chunks
            if order_args:
                self.data = orders(*order_args)
            else:
                self.data = orders()
            orders_data = split_array(self.data, self.size)
        else:
            orders_data = None

        orders = self.comm.scatter(orders_data, root=0)
        L = Legions.Legions(
            orders,
            self.size,
            self.rank,
            self.processor)
        data = L.process_parallel(method, args)
        # TODO: Should this be an allgather?
        answer = self.comm.gather(data, root=0)
        if self.rank == 0:
            return self.data, list(itertools.chain.from_iterable(answer)), self.rank
        return None, None, self.rank
