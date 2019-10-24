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




from mpi4py import MPI
import Pyaesar.Legionnaire as Legionnaire
import logging

class Legions():
    '''
    Receives orders from the Emperor and distributes them to the Legionnaire.
    '''
    
    def __init__(
            self,
            data,
            size,
            rank,
            nproc):
        '''
        Args: 

            data (list): List of data to be processed
            size (int): Total number of MPI ranks launched
            rank (int): MPI rank of this process 
            nproc (int): Number of processes to use for each rank
        '''
        self.rank = rank
        self.size = size
        self.data = data
        self.output = []
        self.nproc = nproc
        logging.info("Spawned a Legion on Node: {}".format(self.rank))
        logging.info(
                "{} is processing data of length: {}".format(
                    self.rank, len(
                        self.data)))


    def process_parallel(self, method, *args):
        '''
        Distribute the work among self.nproc processors on the node, and
        process the data in parallel. 

        Args:
            
            method (function): Function that will be run on each data element
            args (iterable): Constant arguments passed to method (i.e. arguments other than the data element).
        '''

        conglomerate = Legionnaire.Legionnaire(
            method,
            self.size,
            self.rank,
            self.nproc)

        logging.info('Processed data: {} on rank: {} out of {}. Host name: '.format(
                len(self.data), self.rank, self.size, MPI.Get_processor_name()))

        output = conglomerate.call(self.data, args)

        conglomerate.wait()

        return output
