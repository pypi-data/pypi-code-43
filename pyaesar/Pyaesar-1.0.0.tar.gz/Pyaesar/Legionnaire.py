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




import multiprocessing
from pandas import DataFrame
from multiprocessing import Pool
from functools import partial
from Pyaesar.utils import split_array
import logging

class Legionnaire:
    '''
    Distributes work among the processors of a node.
    '''

    def __init__(self,
                 func,
                 size,
                 rank,
                 nproc=multiprocessing.cpu_count()):
        '''
        Args:

            func (function): Function to be applied on each data element
            size (int): Total number of MPI ranks launched
            rank (int): MPI rank of this process
            nproc (int): number of processors to use (default: total number of processors)
        '''
        self.func = func
        self.nproc = nproc
        if nproc > 1:
            self.pool = Pool(nproc)
        else:
            self.pool = None
        logging.info(
                "creating a pool of {} processes on rank:  {} out of size: {}".format(
                    nproc, rank, size))

    def prepare_orders(self, orders):
        '''
        Process orders before passing them to self.pool.

        Args:
            orders (list): List of data to be processed
        '''
        # Data frames need to be split up before getting sent to Pool
        if isinstance(orders, DataFrame):
            return split_array(orders, self.nproc)
        else:
            return orders

    def call(self, orders, *args):
        '''
        Runs self.func on each element of orders. If self.nproc is 1, the computation is done in
        serial. If self.nproc is greater than 1, a multiprocess map is runs the computation in
        parallel by distributing the work among the node's processors.

        Args:

            orders (list): List of data to be processed by applying self.func
            args (iterable): Constant arguments passed to self.func (i.e. arguments other than the data element).
        '''
        orders = self.prepare_orders(orders)

        # Construct single-argument function
        if len(args) > 1:
            func = partial(self.func, args)
        else:
            func = self.func

        # Map data
        if self.pool is None:
            res = [ func(x) for x in orders ]
        else:
            res = self.pool.map(func, orders)

        return res

    def call_async(self, orders, *args):
        '''
        Creates a multiprocess asynchronous map that runs self.func on each
        element of orders in parallel by distributing the work among the node's
        processors.

        Args:

            orders (list): List of data to be processed by applying self.func
            args (iterable): Constant arguments passed to self.func (i.e. arguments other than the data element).
        '''
        raise NotImplementedError

    def wait(self):
        '''
        Waits until all processes complete.
        '''
        if self.pool is not None:
            self.pool.close()
            self.pool.join()
