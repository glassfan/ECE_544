#   Copyright (c) 2016, Xilinx, Inc.
#   All rights reserved.
# 
#   Redistribution and use in source and binary forms, with or without 
#   modification, are permitted provided that the following conditions are met:
#
#   1.  Redistributions of source code must retain the above copyright notice, 
#       this list of conditions and the following disclaimer.
#
#   2.  Redistributions in binary form must reproduce the above copyright 
#       notice, this list of conditions and the following disclaimer in the 
#       documentation and/or other materials provided with the distribution.
#
#   3.  Neither the name of the copyright holder nor the names of its 
#       contributors may be used to endorse or promote products derived from 
#       this software without specific prior written permission.
#
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#   AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
#   THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
#   PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
#   EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
#   PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
#   OR BUSINESS INTERRUPTION). HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
#   WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
#   OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
#   ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

__author__      = "Samuel K Burkhart"
__copyright__   = "Copyright 2016, PSU"
__email__       = "samuel.burkhart@gmail.com"


import time
import struct
from pynq import MMIO
from pynq.iop import request_iop
from pynq.iop import iop_const
from pynq.iop import PMODA
from pynq.iop import PMODB

PMOD_HB3_PROGRAM = "pmod_hb3.bin"

class Pmod_HB3(object):
    """This class uses the PWM and GPIO to create an HB3 peripheral.

    Attributes
    ----------
    iop : _IOP
        I/O processor instance used by Pmod_HB3.
    mmio : MMIO
        Memory-mapped I/O instance to read and write instructions and data.
            
    """
    def __init__(self, if_id, index): 
        """Return a new instance of an HB3 object. 
        
        Parameters
        ----------
        if_id : int
            The interface ID (1, 2) corresponding to (PMODA, PMODB).
        index : int
            The specific pin that runs PWM.
            
        """
        if not if_id in [PMODA, PMODB]:
            raise ValueError("No such IOP for Pmod device.")
        if not index in range(8):
            raise ValueError("Valid pin indexes are 0 - 7.")
        
        print("Setting up IOP")
        self.iop = request_iop(if_id, PMOD_HB3_PROGRAM)
        
        print("Setting up MMIO")
        self.mmio = self.iop.mmio
        
        print("Starting IOP")
        self.iop.start()
        
        # Write PWM pin config
        print("Writing PWM pin configuration")
        self.mmio.write(iop_const.MAILBOX_OFFSET, index)
        
        
        # Write configuration and wait for ACK
        self.mmio.write(iop_const.MAILBOX_OFFSET +
                        iop_const.MAILBOX_PY2IOP_CMD_OFFSET, 0x1)
                        
        print("Waiting for acknowledge.")
        while not (self.mmio.read(iop_const.MAILBOX_OFFSET +
                                  iop_const.MAILBOX_PY2IOP_CMD_OFFSET) == 0):
            pass
            
        print("Got acknowledge.")
            
    def generate(self,period,duty_cycle):
        """Generate pwm signal with desired period and percent duty cycle.
        
        Parameters
        ----------
        period : int
            The period of the tone (us), between 1 and 65536.
        duty_cycle : int
            The duty cycle in percentage.
        
        Returns
        -------
        None
                
        """
        if period not in range(1,65536):
            raise ValueError("Valid tone period is between 1 and 65536.")
        if duty_cycle not in range(1,99):
            raise ValueError("Valid duty cycle is between 1 and 99.")
            
        self.mmio.write(iop_const.MAILBOX_OFFSET, period)
        self.mmio.write(iop_const.MAILBOX_OFFSET+0x4, duty_cycle)
        self.mmio.write(iop_const.MAILBOX_OFFSET +
                        iop_const.MAILBOX_PY2IOP_CMD_OFFSET, 0x3)
        while not (self.mmio.read(iop_const.MAILBOX_OFFSET +
                                  iop_const.MAILBOX_PY2IOP_CMD_OFFSET) == 0):
            pass
            
    def read(self):
        print("Reading data direction.")
        self.mmio.write(iop_const.MAILBOX_OFFSET +
                iop_const.MAILBOX_PY2IOP_CMD_OFFSET, 0x9)
                        
        print("Waiting for response.")
        while not (self.mmio.read(iop_const.MAILBOX_OFFSET +
                                  iop_const.MAILBOX_PY2IOP_CMD_OFFSET) == 0x9):
            pass
        print("Got acknowledge")
        return self.mmio.read(iop_const.MAILBOX_OFFSET)
    
    
    def write(self, direction):
        """ writes the direction of the motor to the HB3 device.
        
        Parameters
        ----------
        period : int
            The motor direction, 0 or 1.
        
        Returns
        -------
        None
        """
        print("Writing direction to Pmod HB3: {}".format(direction))
        self.mmio.write(iop_const.MAILBOX_OFFSET, direction)
        
        # print("Reading state to Pmod HB3: {}".format(direction))
        self.mmio.write(iop_const.MAILBOX_OFFSET +
                        iop_const.MAILBOX_PY2IOP_CMD_OFFSET, 0x7)
                        
        print("Waiting for response.")
        while not (self.mmio.read(iop_const.MAILBOX_OFFSET +
                                  iop_const.MAILBOX_PY2IOP_CMD_OFFSET) == 0):
            pass
        print("Got acknowledge")
        # return self.mmio.read(iop_const.MAILBOX_OFFSET)
        
    def stop(self):
        """Stops PWM generation.
            
        Returns
        -------
        None
        
        """
        self.mmio.write(iop_const.MAILBOX_OFFSET +
                        iop_const.MAILBOX_PY2IOP_CMD_OFFSET, 0x5)
        while not (self.mmio.read(iop_const.MAILBOX_OFFSET +
                                  iop_const.MAILBOX_PY2IOP_CMD_OFFSET) == 0):
            pass
            