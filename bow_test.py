import Arena
import MalmoPython
import math
import time
import json
import pickle
import os, sys, random
from collections import defaultdict, deque
from GeneralBot import GeneralBot

def main():
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately
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


    ##########################################################
    ## Modify the below code in order to change the encounters
    ##########################################################
    enemy = "Zombie"
    # Create the mission using the preset XML function fromarena_gen
    missxml = Arena.create_mission(enemy)
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
    if world_state.is_mission_running:
        agent_host.sendCommand("hotbar.2 1")
        agent_host.sendCommand("hotbar.2 0")
        world_state = agent_host.getWorldState()
    while world_state.is_mission_running:
        world_state = agent_host.getWorldState()
        agent_host.sendCommand("use 1")
        time.sleep(0.5)
        agent_host.sendCommand("use 0")
        #agent_host.sendCommand("attack 1")
        time.sleep(1)
        print '.',
    print "Mission has stopped.\n"
    # -- clean up -- #
    time.sleep(2)  # (let the Mod reset)
    print "Done."

if __name__ == '__main__':
    main()
