# ------------------------------------------------------------------------------------------------
# Copyright (c) 2016 Microsoft Corporation
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
# NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# ------------------------------------------------------------------------------------------------

# A sample that demonstrates a two-agent mission with discrete actions to dig and place blocks

import GeneralBot
import Arena
import thread

import MalmoPython
import json
import logging
import math
import os
import random
import sys
import time

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately

# -- set up two agent hosts --
agent_host1 = MalmoPython.AgentHost()
agent_host2 = MalmoPython.AgentHost()

try:
    agent_host1.parse( sys.argv )
except RuntimeError as e:
    print 'ERROR:',e
    print agent_host1.getUsage()
    exit(1)
if agent_host1.receivedArgument("help"):
    print agent_host1.getUsage()
    exit(0)

my_mission = MalmoPython.MissionSpec(Arena.create_pvp_mission("MurderBot", "OtherMurderBot", timelimit=60000) ,True)

client_pool = MalmoPython.ClientPool()
client_pool.add( MalmoPython.ClientInfo('127.0.0.1',10000) )
client_pool.add( MalmoPython.ClientInfo('127.0.0.1',10001) )

agent_host1.startMission( my_mission, client_pool, MalmoPython.MissionRecordSpec(), 0, '' )
time.sleep(10)
agent_host2.startMission( my_mission, client_pool, MalmoPython.MissionRecordSpec(), 1, '' )

bots = []
Arena.HEIGHT_CHART["MurderBot"] = 1.95
Arena.HEIGHT_CHART["OtherMurderBot"] = 1.95

for agent_host in [ agent_host1, agent_host2 ]:
    print "Waiting for the mission to start",
    world_state = agent_host.peekWorldState()
    while not world_state.has_mission_begun:
        sys.stdout.write(".")
        time.sleep(0.1)
        world_state = agent_host.peekWorldState()
        for error in world_state.errors:
            print "Error:",error.text
    newGB = GeneralBot.GeneralBot()
    bots.append(newGB)
    thread.start_new_thread(newGB.run, (agent_host,))
    print

# perform a few actions

    
# wait for the missions to end    
while agent_host1.peekWorldState().is_mission_running or agent_host2.peekWorldState().is_mission_running:
    time.sleep(1)


