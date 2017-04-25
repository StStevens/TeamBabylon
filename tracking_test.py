import MalmoPython
import os
import sys
import time
import json
import math

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately

# More interesting generator string: "3;7,44*49,73,35:1,159:4,95:13,35:13,159:11,95:10,159:14,159:6,35:6,95:6;12;"

TRACK_WIDTH = 20
TRACK_BREADTH = 20
PLAYER_NAME = "Killer"
missionXML='''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
            <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">

              <About>
                <Summary>Hello world!</Summary>
              </About>

              <ServerSection>
                <ServerInitialConditions>
                    <AllowSpawning>true</AllowSpawning>
                    <Time>
                        <StartTime>6000</StartTime>
                        <AllowPassageOfTime>false</AllowPassageOfTime>
                    </Time>
                </ServerInitialConditions>
                <ServerHandlers>
                  <FlatWorldGenerator generatorString="3;7,220*1,5*3,2;3;,biome_1"/>
                  <DrawingDecorator>
                    <DrawEntity x="2.0" y="227.0" z="10" type="Pig"/>
                  </DrawingDecorator>
                  <ServerQuitFromTimeUp timeLimitMs="30000"/>
                  <ServerQuitWhenAnyAgentFinishes/>

                </ServerHandlers>
              </ServerSection>

              <AgentSection mode="Survival">
                <Name>''' + PLAYER_NAME + '''</Name>
                <AgentStart>
                    <Placement x="0.5" y="227" z="0.5"/>
                    <Inventory>
                    </Inventory>
                </AgentStart>
                <AgentHandlers>
                  <ObservationFromFullStats/>
                  <ContinuousMovementCommands turnSpeedDegs="360"/>
                  <ObservationFromNearbyEntities>
                    <Range name="entities" xrange="'''+str(TRACK_WIDTH)+'''" yrange="2" zrange="'''+str(TRACK_BREADTH)+'''" />
                  </ObservationFromNearbyEntities>
                </AgentHandlers>
              </AgentSection>
            </Mission>'''

# Create default Malmo objects:

def calcYawToMob(entity, x, z): #Borrowed from cart_test.py
    ''' Find the mob we are following, and calculate the yaw we need in order to face it '''
    dx = entity['x'] - x
    dz = entity['z'] - z
    yaw = -180 * math.atan2(dx, dz) / math.pi
    return yaw

def getNextTarget(entities):
    for entity in entities:
        if entity['name'] != PLAYER_NAME:
            return entity

agent_host = MalmoPython.AgentHost()
try:
    agent_host.parse( sys.argv )
except RuntimeError as e:
    print 'ERROR:',e
    print agent_host.getUsage()
    exit(1)
if agent_host.receivedArgument("help"):
    print agent_host.getUsage()
    exit(0)

my_mission = MalmoPython.MissionSpec(missionXML, True)
my_mission_record = MalmoPython.MissionRecordSpec()

# Attempt to start a mission:
max_retries = 3
for retry in range(max_retries):
    try:
        agent_host.startMission( my_mission, my_mission_record )
        break
    except RuntimeError as e:
        if retry == max_retries - 1:
            print "Error starting mission:",e
            exit(1)
        else:
            time.sleep(2)

# Loop until mission starts:
print "Waiting for the mission to start ",
world_state = agent_host.getWorldState()
while not world_state.has_mission_begun:
    sys.stdout.write(".")
    time.sleep(0.1)
    world_state = agent_host.getWorldState()
    for error in world_state.errors:
        print "Error:",error.text

print
print "Mission running ",

# Loop until mission ends:
while world_state.is_mission_running:
    sys.stdout.write(".")
    print
    time.sleep(0.1)
    world_state = agent_host.getWorldState()
    if world_state.number_of_observations_since_last_state > 0:
        msg = world_state.observations[-1].text
        ob = json.loads(msg)
        xPos = ob['XPos']
        zPos = ob['ZPos']
        yaw = ob['Yaw']
        target = getNextTarget(ob['entities'])
        yaw_to_mob = calcYawToMob(target, xPos, zPos)
        deltaYaw = yaw_to_mob - yaw
        while deltaYaw < -180:
            deltaYaw += 360;
        while deltaYaw > 180:
            deltaYaw -= 360;
        deltaYaw /= 180.0;
        # And turn:
        agent_host.sendCommand("turn " + str(deltaYaw))


    for error in world_state.errors:
        print "Error:",error.text

print
print "Mission ended"
# Mission has ended.
