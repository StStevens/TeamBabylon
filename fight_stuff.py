# Calculate yaw to a given mob, turn towards it and attack.

import MalmoPython
import os
import sys
import time
import json
import math
import time

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately
trackw = 20
trackb = 20
trackh = 20
PLAYER_NAME = "DumbBot"
timelimit = 20000


def malmoName(minecraftName):
    '''returns the malmo-appropriate name of a given entity'''
    if minecraftName not in NAME_MAPPING.keys():
        return minecraftName
    return NAME_MAPPING[minecraftName]

HEIGHT_CHART = {
    "Creeper":1.7, "Skeleton":1.95, "Spider":1, "Zombie":1.95,
    "Ghast":4, "Zombie Pigman":1.95, "Cave Spider":1, "Silverfish":0.3,
    "Blaze":2, "Witch":1.95, "Endermite":0.3, "Wolf": 0.85
}

NAME_MAPPING = {
    "Zombie Pigman" : "PigZombie",
    "Cave Spider" : "CaveSpider",
}

ENTITY_LIST = HEIGHT_CHART.keys()

missionXML=missionXML='''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
        <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
          <About>
            <Summary>@@@ Fighting Simulator</Summary>
            <Description>Defeat the @@@ to Continue!</Description>
          </About>
          <ServerSection>
            <ServerInitialConditions>
                <Time>
                    <StartTime>18000</StartTime>
                       <AllowPassageOfTime>false</AllowPassageOfTime>
                    </Time>
                <AllowSpawning>false</AllowSpawning>
            </ServerInitialConditions>
            <ServerHandlers>
              <FlatWorldGenerator generatorString="3;1*minecraft:bedrock,3*minecraft:obsidian;1;"/>
              <DrawingDecorator>
                <DrawCuboid type="bedrock" x1="0" y1="4" z1="0" x2="50" y2="14" z2="50"/>
                <DrawCuboid type="air" x1="1" y1="4" z1="1" x2="49" y2="14" z2="49"/>
                <DrawCuboid type="glowstone" x1="0" y1="14" z1="0" x2="50" y2="14" z2="50"/>
                <DrawEntity x="25.0" y="4.0" z="25" type="@@@"/>
              </DrawingDecorator>
              <ServerQuitWhenAnyAgentFinishes description="server sees murder happen"/>
            </ServerHandlers>
          </ServerSection>
          <AgentSection mode="Survival">
            <Name>''' + PLAYER_NAME + '''</Name>
            <AgentStart>
              <Placement x="25" y="4.0" z="35" pitch="0" yaw="-180"/>
              <Inventory>
                <InventoryObject slot="0" type="wooden_sword" quantity="1"/>
                <InventoryObject slot="1" type="bow" quantity="1"/>
                <InventoryObject slot="2" type="arrow" quantity="64"/>
              </Inventory>
            </AgentStart>
            <AgentHandlers>
              <MissionQuitCommands
                quitDescription="finished murdering">
                  <ModifierList
                    type='allow-list'>
                      <command>quit</command>
                  </ModifierList>
              </MissionQuitCommands>
              <ObservationFromFullStats/>
              <AgentQuitFromTimeUp timeLimitMs="'''+str(timelimit)+'''" description="out_of_time"/>
              <ContinuousMovementCommands turnSpeedDegs="900"/>
              <ObservationFromNearbyEntities>
                <Range name="entities" xrange="'''+str(trackw)+'''" yrange="'''+str(trackh)+'''" zrange="'''+str(trackb)+'''" />
              </ObservationFromNearbyEntities>
              <ObservationFromHotBar/>
            </AgentHandlers>
          </AgentSection>
        </Mission>'''

def next_mission(x):
    '''create the next missionXML doc'''
    return missionXML.replace("@@@", malmoName(ENTITY_LIST[x]))

def calcYawToMob(entity, x, z): #Borrowed from cart_test.py
    ''' Find the mob we are following, and calculate the yaw we need in order to face it '''
    dx = entity['x'] - x
    dz = entity['z'] - z
    yaw = -180 * math.atan2(dx, dz) / math.pi
    return yaw

def getNextTarget(entities):
    for entity in entities:
        if entity['name'] != PLAYER_NAME and entity['name'] in HEIGHT_CHART.keys():
            return entity

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
encounters = len(ENTITY_LIST)*2
history = []
for n in range(encounters):
    i = n%len(ENTITY_LIST)
    print
    print 'Mission %d of %d' % (n + 1, encounters)

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

    agent_host.sendCommand("move .65")
    # -- run the agent in the world -- #
    starttime = time.time()
    total_time = -1
    agentHealth = -1
    kill = 0
    enemy = 'None'
    done = False
    while world_state.is_mission_running:
        sys.stdout.write("*")
        agent_host.sendCommand("attack 0")
        time.sleep(.5)
        world_state = agent_host.getWorldState()
        if world_state.number_of_observations_since_last_state > 0:
            msg = world_state.observations[-1].text
            ob = json.loads(msg)
            xPos = ob['XPos']
            zPos = ob['ZPos']
            yaw = ob['Yaw']
            agentHealth = ob['Life']
            target = getNextTarget(ob['entities'])
            if target == None:
                if not done:
                    done = True
                    kill=1
                    total_time = time.time() - starttime
                agent_host.sendCommand("attack 0")
                agent_host.sendCommand("turn 0")
                agent_host.sendCommand("move 0")
                continue
            enemy=target['name']
            yaw_to_mob = calcYawToMob(target, xPos, zPos)
            deltaYaw = yaw_to_mob - yaw
            while deltaYaw < -180:
                deltaYaw += 360;
            while deltaYaw > 180:
                deltaYaw -= 360;
            deltaYaw /= 180.0;
            # And turn:
            agent_host.sendCommand("turn " + str(deltaYaw))
            agent_host.sendCommand("attack 1")


        for error in world_state.errors:
            print "Error:", error.text
    print "Mission has stopped.\n"
    if total_time == -1:
        total_time = time.time()-starttime
    history.append([enemy,agentHealth,total_time,kill])
    # -- clean up -- #
    time.sleep(1)  # (let the Mod reset)

try:
    f = open("baseline_results.txt", 'w')
    for result in history:
        if ' ' in result[0]:
            result[0] = result[0].replace(' ','-')
        f.write(str(result[0])+' ')
        f.write(str(result[1])+' ')
        f.write('{:5.3f} '.format(result[2]))
        f.write('{}'.format(result[3]))
        f.write('\n')
    f.close()
except Exception as e:
    print e

print "Done."

print
