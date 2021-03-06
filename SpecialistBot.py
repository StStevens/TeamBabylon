# Basic Structure of Q Learning Agents adapted from Assignment2.py

import Arena
import MalmoPython
import math
import time
import json
import pickle
import os, sys, random
from collections import defaultdict, deque
from GeneralBot import GeneralBot

class SpecialistBot(GeneralBot):
    """SpecialistBot will be given an AgentHost in its run method and use QTabular learning to attack enemies,
    caring about enemy type for strategy"""
    def __init__(self, alpha=0.3, gamma=1, n=25, epsilon=0.3, fname=None):
        """Constructing an RL agent.

        Args
            alpha:   <float>  learning rate      (default = 0.3)
            gamma:   <float>  value decay rate   (default = 1)
            epsilon: <float>  random chance rate (default = 0.3)
            n:       <int>    number of back steps to update (default = 1)
            fname:   <string> filename to store resulting q-table in
        """
        self.weapon = "sword" #or "bow"
        self.fname = fname
        self.agent = None
        self.epsilon = 0.2  # chance of taking a random action instead of the best
        if fname:
            f = open(fname, "r")
            self.q_table = pickle.load(f)
        else:
            self.fname = "sb_qtable.p" if epsilon != 1 else "db_qtable.p"
            self.q_table = dict() # Create the Q-Table
            for dist in ["Close", "Melee", "Far"]:
                for health in ["Low", "Med", "Hi"]:
                    for weap in ["sword", "bow"]:
                        for enemy in Arena.ENTITY_LIST:
                            self.q_table[(dist,health,weap,str(enemy))] = {action : 0 for action in self.get_possible_actions(weap)}
        self.n, self.gamma, self.alpha, self.epsilon = n, gamma, alpha, epsilon
        self.history = []

    def get_curr_state(self, obs, ent):
        '''
            Discretize distance, player health, and current_weapon into states:
                Distance (melee, close, far), Health (<10%, 10-60%, 60-100%), current_weapon (sword, bow)
            Add a state for EnemyType in the Specialist
        '''
        state = GeneralBot.get_curr_state(self, obs, ent)
        state = state if state == ("Finished",) else state + (str(ent['name']),)
        return state

def main():
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately
    SB = SpecialistBot(fname="sb_qtable.p")
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
    encounters = len(Arena.ENTITY_LIST)*3
    for n in range(encounters):
        i = n%len(Arena.ENTITY_LIST)
        enemy = Arena.malmoName(Arena.ENTITY_LIST[i]) #"Zombie" if you want to run it exclusively
                                                    # against Zombies
        print
        print 'Mission %d of %d: %s' % (n+1, encounters, enemy)

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
        SB.run(agent_host)
        print "Mission has stopped.\n"
        # -- clean up -- #
        time.sleep(2)  # (let the Mod reset)
    print "Done."
    SB.log_Q()
    SB.log_results('sb_results_base.txt')

if __name__ == '__main__':
    main()
