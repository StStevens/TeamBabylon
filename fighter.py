# Fighter Class
# Creates an AgentHost as a local variable and attacks any nearby enemies.
# To be used with Arena_gen.py

import MalmoPython

import os
import sys
import time
import json
import math

import arena_gen

HEIGHT_CHART = {
    "Creeper":1.7, "Skeleton":1.95, "Spider":1, "Zombie":1.95,
    "Slime":1, "Ghast":4, "Zombie Pigman":1.95, "Enderman":2.9, "Cave Spider":1, "Silverfish":0.3,
    "Blaze":2, "Magma Cube":1, "Bat":0.9, "Witch":1.95, "Endermite":0.3,
    "Pig":0.875, "Wolf":0.85
}

NAME_MAPPING = {
    "Zombie Pigman" : "PigZombie",
    "Cave Spider" : "CaveSpider",
    "Magma Cube" : "LavaSlime"
}

TRACK_WIDTH = 20
TRACK_BREADTH = 20
TRACK_HEIGHT = 20
TIMELIMIT = 10000
ENTITY_LIST = HEIGHT_CHART.keys()
PLAYER_NAME= "MurderBot"

class MurderBot:
    """MurderBot will be given an AgentHost in its run method and a file to log learned behavior,
    and will use tabular q-learning to train itself on tracking down & attacking various enemies"""
    def __init__(self):
        return

    def run(self, agent_host):
        """ Run the Agent on the world """
        agent_host.sendCommand("move 0.75")
        world_state = agent_host.getWorldState()
        while world_state.is_mission_running:
            #sys.stdout.write("*")
            time.sleep(0.1)
            world_state = agent_host.getWorldState()
            if world_state.number_of_observations_since_last_state > 0:
                msg = world_state.observations[-1].text
                ob = json.loads(msg)
                xPos = ob['XPos']
                yPos = ob['YPos']
                zPos = ob['ZPos']
                yaw = ob['Yaw']
                pitch = ob['Pitch']
                target = self.getNextTarget(ob['entities'])
                if target == None or target['name'] not in HEIGHT_CHART.keys(): # No enemies nearby
                    if target != None:
                        sys.stdout.write("Not found: "+target['name'] + "\n")
                    agent_host.sendCommand("move 0") # stop moving
                    agent_host.sendCommand("attack 0") # stop attacking
                    agent_host.sendCommand("turn 0") # stop turning
                    agent_host.sendCommand("pitch 0") # stop looking up/down
                else:# enemy nearby, kill kill kill
                    deltaYaw, deltaPitch = self.calcYawPitch(target, yaw, pitch, xPos, yPos, zPos)
                    # And turn:
                    agent_host.sendCommand("turn " + str(deltaYaw))
                    agent_host.sendCommand("pitch " + str(deltaPitch))
                    agent_host.sendCommand("attack 1")

            for error in world_state.errors:
                print "Error:", error.text

    def calcYawPitch(self, entity, selfyaw, selfpitch, x, y, z): #Adapted from cart_test.py
        ''' Find the mob we are following, and calculate the yaw we need in order to face it '''
        dx = entity['x'] - x
        dz = entity['z'] - z
        dy = (entity['y']+HEIGHT_CHART[entity['name']]/2) - (y+1.8) #calculate height difference between our eye level and center of mass for entity
        # print 'Dx %f \nDy %f \nDz %f\n' % (dx, dy, dz)
        #-- calculate deltaYaw
        yaw = -180 * math.atan2(dx, dz) / math.pi
        deltaYaw = yaw - selfyaw
        while deltaYaw < -180:
            deltaYaw += 360
        while deltaYaw > 180:
            deltaYaw -= 360
        deltaYaw /= 180.0
        #-- calculate deltaPitch
        h_dist = math.sqrt(dx**2 + dz**2)
        pitch = 180*math.atan2(y, h_dist) / math.pi
        deltaPitch = pitch - selfpitch
        while deltaPitch < -180:
            deltaPitch += 360
        while deltaPitch > 180:
            deltaPitch -= 360
        deltaPitch /= 180.0
        return deltaYaw, deltaPitch

    def getNextTarget(self, entities):
        for entity in entities:
            if entity['name'] != PLAYER_NAME:
                return entity

def malmoName(minecraftName):
    '''returns the malmo-appropriate name of a given entity'''
    if minecraftName not in NAME_MAPPING.keys():
        print("minecraftName = " + minecraftName)
        return minecraftName
    return NAME_MAPPING[minecraftName]

def main():
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately

    MB = MurderBot()
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
        print 'Mission %d of %d: %s' % (i + 1, encounters, malmoName(ENTITY_LIST[i]))

        # Create the mission using the preset XML function from arena_gen
        missxml = arena_gen.create_mission(TRACK_WIDTH, TRACK_BREADTH, TRACK_HEIGHT, ENTITY_LIST[i], TIMELIMIT)
        my_mission = MalmoPython.MissionSpec(missxml, True)
        my_mission.forceWorldReset() # RESET THE WORLD IN BETWEEN ENCOUNTERS

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
        MB.run(agent_host)
        print "Mission has stopped.\n"
        # -- clean up -- #
        time.sleep(2)  # (let the Mod reset)
    print "Done."


if __name__ == '__main__':
    main()
