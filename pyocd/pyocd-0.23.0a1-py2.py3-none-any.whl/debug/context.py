# pyOCD debugger
# Copyright (c) 2016-2019 Arm Limited
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ..core.memory_interface import MemoryInterface
from pyocd.coresight.component import CoreSightCoreComponent
from ..coresight.cortex_m import (
    CORE_REGISTER,
    register_name_to_index,
    is_single_float_register,
    is_double_float_register
    )
from ..utility import conversion

class DebugContext(MemoryInterface):
    """! @brief Viewport for inspecting the system being debugged.
    
    A debug context is used to access target registers and memory. It enables these accesses to be
    redirected to different locations. For instance, if you want to read registers from a call frame
    that is not the topmost, then a context would redirect those reads to locations on the stack.
    
    A context always has both a parent context and a specific core associated with it, neither of
    which can be changed after the context is created. The parent context is passed into the
    constructor. For the top-level debug context, the parent *is* the core. For other contexts that
    have a context as their parent, the core is set to the topmost parent's core.
    
    The DebugContext class itself is meant to be used as a base class. It's primary purpose is to
    provide the default implementation of methods to forward calls up to the parent and eventually
    to the core.
    """
    
    def __init__(self, parent):
        """! @brief Debug context constructor.
        
        @param self
        @param parent The parent of this context. Can be either a core (CoreSightCoreComponent) or
            another DebugContext instance.
        """
        self._parent = parent
        
        if isinstance(self._parent, CoreSightCoreComponent):
            self._core = parent
        else:
            self._core = parent.core

    @property
    def parent(self):
        return self._parent

    @property
    def core(self):
        return self._core

    def write_memory(self, addr, value, transfer_size=32):
        return self._parent.write_memory(addr, value, transfer_size)

    def read_memory(self, addr, transfer_size=32, now=True):
        return self._parent.read_memory(addr, transfer_size, now)

    def write_memory_block8(self, addr, value):
        return self._parent.write_memory_block8(addr, value)

    def write_memory_block32(self, addr, data):
        return self._parent.write_memory_block32(addr, data)

    def read_memory_block8(self, addr, size):
        return self._parent.read_memory_block8(addr, size)

    def read_memory_block32(self, addr, size):
        return self._parent.read_memory_block32(addr, size)

    def read_core_register(self, reg):
        """! @brief Read CPU register
        
        Unpack floating point register values
        """
        regIndex = register_name_to_index(reg)
        regValue = self.read_core_register_raw(regIndex)
        # Convert int to float.
        if is_single_float_register(regIndex):
            regValue = conversion.u32_to_float32(regValue)
        elif is_double_float_register(regIndex):
            regValue = conversion.u64_to_float64(regValue)
        return regValue

    def read_core_register_raw(self, reg):
        """! @brief Read a core register.
        
        If reg is a string, find the number associated to this register
        in the lookup table CORE_REGISTER
        """
        vals = self.read_core_registers_raw([reg])
        return vals[0]

    def read_core_registers_raw(self, reg_list):
        return self._parent.read_core_registers_raw(reg_list)

    def write_core_register(self, reg, data):
        """! Write a CPU register.
        
        Will need to pack floating point register values before writing.
        """
        regIndex = register_name_to_index(reg)
        # Convert float to int.
        if is_single_float_register(regIndex) and type(data) is float:
            data = conversion.float32_to_u32(data)
        elif is_double_float_register(regIndex) and type(data) is float:
            data = conversion.float64_to_u64(data)
        self.write_core_register_raw(regIndex, data)

    def write_core_register_raw(self, reg, data):
        """! @brief Write a core register.
        
        If reg is a string, find the number associated to this register
        in the lookup table CORE_REGISTER
        """
        self.write_core_registers_raw([reg], [data])

    def write_core_registers_raw(self, reg_list, data_list):
        self._parent.write_core_registers_raw(reg_list, data_list)

    def flush(self):
        self._core.flush()

