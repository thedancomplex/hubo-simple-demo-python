#!/usr/bin/env python
# /* -*-  indent-tabs-mode:t; tab-width: 8; c-basic-offset: 8  -*- */
# /*
# Copyright (c) 2013, Daniel M. Lofaro
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the author nor the names of its contributors may
#       be used to endorse or promote products derived from this software
#       without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# */



import hubo_ach as ha
import ach
import sys
import time
import numpy as np
from ctypes import *

class ikClass(object):

    def ik(self,x,Le):
        xAP = -np.arccos((x/2.0)/Le)
        xHP = xAP
        xKN = -xAP*2.0
        a = [0,0,0]
#        a[0] = xAP
#        a[1] = xHP
#        a[2] = xKN
        a[0] = xAP
        a[1] = xHP
        a[2] = abs(2.0*xAP)
	print 'rad = ', a
        return a


def main():
    
    ik = ikClass()

    # Open Hubo-Ach feed-forward and feed-back (reference and state) channels
    s = ach.Channel(ha.HUBO_CHAN_STATE_NAME)
    r = ach.Channel(ha.HUBO_CHAN_REF_NAME)
    s.flush()
    r.flush()

    # feed-forward will now be refered to as "state"
    state = ha.HUBO_STATE()

    # feed-back will now be refered to as "ref"
    ref = ha.HUBO_REF()


    # trigger
    ts = ach.Channel(ha.HUBO_CHAN_VIRTUAL_TO_SIM_NAME)
    ts.flush()
    sim = ha.HUBO_VIRTUAL()


    T = 0.5  # time between steps

    N = int(np.ceil(T/ha.HUBO_LOOP_PERIOD))
    Le = 0.3 # length of thigh
    x0 = Le*2.0*0.8
    x1 = x0*0.95
    x2 = Le*2.0
    

    # Start Pos
    R = ik.ik(x0,Le)
    ref.ref[ha.RAP] = R[0]
    ref.ref[ha.RHP] = R[1]
    ref.ref[ha.RKN] = R[2]
   
    L = ik.ik(x0,Le)
    ref.ref[ha.LAP] = L[0]
    ref.ref[ha.LHP] = L[1]
    ref.ref[ha.LKN] = L[2]
 
    r.put(ref)

    phase = 0;
    rad = -0.2;
    while(1):
        for q in range(0,N):
            [statuss, framesizes] = ts.get(sim, wait=True, last=False)

        # Get the current feed-forward (state) 
        [statuss, framesizes] = s.get(state, wait=False, last=False)
        if(0 == phase):    # Right leg up
            R = ik.ik(x1,Le)
            ref.ref[ha.RAP] = R[0]
            ref.ref[ha.RHP] = R[1]
            ref.ref[ha.RKN] = R[2]
   
            L = ik.ik(x0,Le)
            ref.ref[ha.LAP] = L[0]
            ref.ref[ha.LHP] = L[1]
            ref.ref[ha.LKN] = L[2]
           
            tmp = rad

            ref.ref[ha.RHR] = tmp
            ref.ref[ha.RAR] = -tmp
            ref.ref[ha.LHR] = tmp
            ref.ref[ha.LAR] = -tmp
            phase = 1
        elif(1 == phase):  #both feet down
            R = ik.ik(x0,Le)
            ref.ref[ha.RAP] = R[0]
            ref.ref[ha.RHP] = R[1]
            ref.ref[ha.RKN] = R[2]
   
            L = ik.ik(x0,Le)
            ref.ref[ha.LAP] = L[0]
            ref.ref[ha.LHP] = L[1]
            ref.ref[ha.LKN] = L[2]

            tmp = 0

            ref.ref[ha.RHR] = tmp
            ref.ref[ha.RAR] = -tmp
            ref.ref[ha.LHR] = tmp
            ref.ref[ha.LAR] = -tmp
            phase = 2
        elif(2 == phase):    # left leg up
            R = ik.ik(x0,Le)
            ref.ref[ha.RAP] = R[0]
            ref.ref[ha.RHP] = R[1]
            ref.ref[ha.RKN] = R[2]
   
            L = ik.ik(x1,Le)
            ref.ref[ha.LAP] = L[0]
            ref.ref[ha.LHP] = L[1]
            ref.ref[ha.LKN] = L[2]

            tmp = -rad

            ref.ref[ha.RHR] = tmp
            ref.ref[ha.RAR] = -tmp
            ref.ref[ha.LHR] = tmp
            ref.ref[ha.LAR] = -tmp
            phase = 3
        elif(3 == phase):  #both feet down
            R = ik.ik(x0,Le)
            ref.ref[ha.RAP] = R[0]
            ref.ref[ha.RHP] = R[1]
            ref.ref[ha.RKN] = R[2]
   
            L = ik.ik(x0,Le)
            ref.ref[ha.LAP] = L[0]
            ref.ref[ha.LHP] = L[1]
            ref.ref[ha.LKN] = L[2]
            
            tmp = 0

            ref.ref[ha.RHR] = tmp
            ref.ref[ha.RAR] = -tmp
            ref.ref[ha.LHR] = tmp
            ref.ref[ha.LAR] = -tmp
            phase = 0    

        r.put(ref)
  
        # Write to the feed-forward channel
        print 'Set Ref Now Phase =', phase


# Close the connection to the channels
    r.close()
    s.close()

if __name__=='__main__':
    main()
