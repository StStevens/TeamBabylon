# Arena Generation Python Sample
# Used Tutorial 2 and 6 for sampling
# Usage: Generate the XML schema for a given

import MalmoPython
import os
import sys
import time
import json

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately
def arena_mission():
    '''Runs the multiple-encounter Arena mission, with the Agent doing nothing each time.'''
    TRACK_WIDTH = 20
    TRACK_BREADTH = 20
    ENTITY_LIST = ["Zombie","Creeper","Spider","Ghast"]
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

        missxml = create_mission(TRACK_WIDTH, TRACK_BREADTH, ENTITY_LIST[i], 15000)
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
            time.sleep(0.3)
            world_state = agent_host.getWorldState()
            for error in world_state.errors:
                print "Error:", error.text
        print

        # -- AGENT ACTIONS BELONG HERE -- #
        while world_state.is_mission_running:
            sys.stdout.write("*")
            time.sleep(0.5)
            world_state = agent_host.getWorldState()
            for error in world_state.errors:
                print "Error:", error.text
        print "Mission has stopped."
        print("")
        # -- END AGENT ACTIONS -- #

        time.sleep(3)  # (let the Mod reset)

    print "Done."

def create_mission(trackw, trackb, entity, timelimit):
    '''Creates the xml for a given encounter:
    arguments:
        - trackw: the width of observation grid
        - trackb: the breadth of observation grid
        - entity: the mob type to spawn
        - timelimit: the time limit in ms for the encounter'''
    missionXML='''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
            <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
              <About>
                <Summary>@@@ Fighting Simulator</Summary>
                <Description>Defeat the @@@ to Continue!</Description>
              </About>
              <ServerSection>
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
                    <DrawCuboid type="bedrock" x1="0" y1="4" z1="0" x2="50" y2="14" z2="50"/>
                    <DrawCuboid type="air" x1="1" y1="4" z1="1" x2="49" y2="14" z2="49"/>
                    <DrawCuboid type="glowstone" x1="0" y1="14" z1="0" x2="50" y2="14" z2="50"/>
                    <DrawEntity x="25.0" y="4.0" z="35" type="@@@"/>
                  </DrawingDecorator>
                </ServerHandlers>
              </ServerSection>
              <AgentSection mode="Survival">
                <Name>MurderBot</Name>
                <AgentStart>
                  <Placement x="25" y="4.0" z="25" pitch="0" yaw="0"/>
                  <Inventory>
                    <InventoryObject slot="0" type="wooden_sword" quantity="1"/>
                    <InventoryObject slot="1" type="bow" quantity="1"/>
                    <InventoryObject slot="2" type="arrow" quantity="64"/>
                    <InventoryObject slot="3" type="arrow" quantity="64"/>
                  </Inventory>
                </AgentStart>
                <AgentHandlers>
                  <ObservationFromFullStats/>
                  <RewardForMissionEnd rewardForDeath="-10000">
                    <Reward description="out_of_time" reward="-1000" />
                  </RewardForMissionEnd>
                  <AgentQuitFromTimeUp timeLimitMs="'''+str(timelimit)+'''" description="out_of_time"/>
                  <ContinuousMovementCommands turnSpeedDegs="180"/>
                  <ObservationFromNearbyEntities>
                    <Range name="entities" xrange="'''+str(trackw)+'''" yrange="2" zrange="'''+str(trackb)+'''" />
                  </ObservationFromNearbyEntities>
                </AgentHandlers>
              </AgentSection>
            </Mission>'''
    missionXML = missionXML.replace("@@@", entity)
    return missionXML

if __name__ == "__main__":
    arena_mission()
