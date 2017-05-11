# Fighter Class
# Creates an AgentHost as a local variable and attacks any nearby enemies.
# To be used with Arena_gen.py

import MalmoPython

import os
import sys
import time
import json
import math

import Arena

class BasicBot:
    """BasicBot will be given an AgentHost in its run method and just track down & attack various enemies"""
    def __init__(self):
        return

    def run(self, agent_host):
        """ Run the Agent on the world """
        agent_host.sendCommand("move 0.25")
        world_state = agent_host.getWorldState()
        while world_state.is_mission_running:
            #sys.stdout.write("*")
            time.sleep(0.1)
            world_state = agent_host.getWorldState()
            if world_state.number_of_observations_since_last_state > 0:
                msg = world_state.observations[-1].text
                ob = json.loads(msg)
                '''Obs has the following keys:
                ['PlayersKilled', 'TotalTime', 'Life', 'ZPos', 'IsAlive',
                'Name', 'entities', 'DamageTaken', 'Food', 'Yaw', 'TimeAlive',
                'XPos', 'WorldTime', 'Air', 'DistanceTravelled', 'Score', 'YPos',
                'Pitch', 'MobsKilled', 'XP']
                '''
                print ob.keys()

                xPos = ob['XPos']
                yPos = ob['YPos']
                zPos = ob['ZPos']
                yaw = ob['Yaw']
                pitch = ob['Pitch']
                target = self.getNextTarget(ob['entities'])
                if target == None or target['name'] not in Arena.HEIGHT_CHART.keys(): # No enemies nearby
                    if target != None:
                        sys.stdout.write("Not found: "+target['name'] + "\n")
                    agent_host.sendCommand("move 0") # stop moving
                    agent_host.sendCommand("attack 0") # stop attacking
                    agent_host.sendCommand("turn 0") # stop turning
                    agent_host.sendCommand("pitch 0") # stop looking up/down
                else:# enemy nearby, kill kill kill
                    deltaYaw, deltaPitch = Arena.calcYawPitch(target['name'], target['x'], target['y'], target['z'], yaw, pitch, xPos, yPos, zPos)
                    # And turn:
                    agent_host.sendCommand("turn " + str(deltaYaw))
                    agent_host.sendCommand("pitch " + str(deltaPitch))
                    agent_host.sendCommand("attack 1")

            for error in world_state.errors:
                print "Error:", error.text

    def getNextTarget(self, entities):
        for entity in entities:
            if entity['name'] != "MurderBot":
                return entity

    '''
    To Be Done:
        Discretize distance, player health, and current_weapon into states:
            Distance (melee, close, far), Health (<10%, 10-60%, 60-100%), current_weapon (sword, bow)
        Add a state for EnemyType in the Specialist
    '''



def main():
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately

    BB = BasicBot()
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

    encounters = len(Arena.ENTITY_LIST)
    for i in range(1): ###########################################################################################
        print
        print 'Mission %d of %d: %s' % (i + 1, encounters, Arena.malmoName(Arena.ENTITY_LIST[i]))

        # Create the mission using the preset XML function from arena_gen
        missxml = Arena.create_mission(Arena.malmoName(Arena.ENTITY_LIST[i]))
        my_mission = MalmoPython.MissionSpec(missxml, True)
        # my_mission.forceWorldReset() # RESET THE WORLD IN BETWEEN ENCOUNTERS

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
        BB.run(agent_host)
        print "Mission has stopped.\n"
        # -- clean up -- #
        time.sleep(2)  # (let the Mod reset)
    print "Done."


if __name__ == '__main__':
    main()
