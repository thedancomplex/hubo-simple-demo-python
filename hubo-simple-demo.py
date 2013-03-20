#!/usr/bin/env python
import hubo_ach
import ach
import sys
import time
from ctypes import *

# Create Hubo-Ach object
ha = hubo_ach

# Open Hubo-Ach feed-forward and feed-back (reference and state) channels
s = ach.Channel(ha.HUBO_CHAN_STATE_NAME)
r = ach.Channel(ha.HUBO_CHAN_REF_NAME)
s.flush()
r.flush()

# feed-forward will now be refered to as "state"
state = ha.HUBO_STATE()

# feed-back will now be refered to as "ref"
ref = ha.HUBO_REF()

# Get the current feed-forward (state) 
[statuss, framesizes] = s.get(state, wait=False, last=False)

#Set Left Elbow Bend (LEB) and Right Shoulder Pitch (RSP) to  -0.2 rad and 0.1 rad respectively
ref.ref[ha.LEB] = -0.2
ref.ref[ha.RSP] = 0.1

# Print out the actual position of the LEB
print "Joint = ", state.joint[ha.LEB].pos

# Print out the Left foot torque in X
print "Mx = ", state.imu[HUBO_FT_L_FOOT].m_x

# Write to the feed-forward channel
r.put(ref)

# Close the connection to the channels
r.close()
s.close()

