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

# Tutorial sample #2: Run simple mission using raw XML

import MalmoPython
import os
import sys
import time
import json

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately

TRACK_WIDTH = 20
TRACK_BREADTH = 20
ENTITY_LIST = ["Pig","Cow","Creeper","Zombie"]
missionXML='''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
            <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
              <About>
                <Summary>@@@ Fighting Simulator</Summary>
              </About>
              <ServerSection>
              <!-- #Test Mission XML without AllowSpawning# -->
                <ServerInitialConditions>
                    <Time>
                        <StartTime>1000</StartTime>
                           <AllowPassageOfTime>false</AllowPassageOfTime>
                        </Time>
                    <AllowSpawning>false</AllowSpawning>
                </ServerInitialConditions>
                <ServerHandlers>
                  <FlatWorldGenerator generatorString="3;1*minecraft:bedrock,3*minecraft:obsidian;1;"/>
                  <DrawingDecorator>
                    <DrawCuboid type="bedrock" x1="0" y1="4" z1="0" x2="50" y2="15" z2="50"/>
                    <DrawCuboid type="air" x1="1" y1="4" z1="1" x2="49" y2="15" z2="49"/>
                    <DrawEntity x="25.0" y="4.0" z="35" type="@@@"/>
                  </DrawingDecorator>
                  <ServerQuitFromTimeUp timeLimitMs="5000"/>
                </ServerHandlers>
              </ServerSection>
              <AgentSection mode="Survival">
                <Name>MurderBot</Name>
                <AgentStart>
                  <Placement x="25" y="4.0" z="25" pitch="0" yaw="0"/>
                </AgentStart>
                <AgentHandlers>
                  <ObservationFromFullStats/>
                  <ContinuousMovementCommands turnSpeedDegs="180"/>
                  <ObservationFromNearbyEntities>
                    <Range name="entities" xrange="'''+str(TRACK_WIDTH)+'''" yrange="2" zrange="'''+str(TRACK_BREADTH)+'''" />
                  </ObservationFromNearbyEntities>
                </AgentHandlers>
              </AgentSection>
            </Mission>'''
#"3;7,220*1,5*3,2;3;,biome_1"
'''
                    <DrawLine type="stone" x1="0" y1="5" z1="0" x2="10" y2="10" z2="10"/>
                    <DrawLine type="stone" x1="0" y1="5" z1="0" x2="10" y2="10" z2="10"/>
                    <DrawLine type="stone" x1="0" y1="5" z1="0" x2="10" y2="10" z2="10"/>'''
def next_mission(x):
    '''create the next missionXML doc'''
    return missionXML.replace("@@@", ENTITY_LIST[x])

agent_host = MalmoPython.AgentHost()
try:
    agent_host.parse(sys.argv)
except RuntimeError as e:
    print 'ERROR:', e
    print agent_host.getUsage()
    exit(1)
if agent_host.receivedArgument("help"):
    print agent_host.getUsage()
    exit(0)


my_mission_record = MalmoPython.MissionRecordSpec()
encounters = len(ENTITY_LIST)

for i in range(encounters):
    print
    print 'Mission %d of %d' % (i + 1, encounters)

    missxml = next_mission(i)
    my_mission = MalmoPython.MissionSpec(missxml, True)
    my_mission.forceWorldReset()
    max_retries = 3
    for retry in range(max_retries):
        try:
            agent_host.startMission(my_mission, my_mission_record)
            break
        except RuntimeError as e:
            if retry == max_retries - 1:
                print "Error starting mission:", e
                exit(1)
            else:
                time.sleep(2)

    print "Waiting for the mission to start",
    world_state = agent_host.getWorldState()
    while not world_state.has_mission_begun:
        sys.stdout.write(".")
        time.sleep(0.1)
        world_state = agent_host.getWorldState()
        for error in world_state.errors:
            print "Error:", error.text
    print

    # -- run the agent in the world -- #
    while world_state.is_mission_running:
        sys.stdout.write("*")
        agent_host.sendCommand("jump 1")
        time.sleep(0.1)
        world_state = agent_host.getWorldState()
        for error in world_state.errors:
            print "Error:", error.text
    print "Mission has stopped.\n"
    # -- clean up -- #
    time.sleep(1)  # (let the Mod reset)

print "Done."

print
