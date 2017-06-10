from SpecialistBot import SpecialistBot
from GeneralBot import GeneralBot
import Arena
import sys, os
import os.path
import MalmoPython
import time
from datetime import timedelta

def main():
    flag = (len(sys.argv) == 4)
    mode = None
    Bot = None
    if flag:
        try:
            #Determine run type
            if sys.argv[2] == 'O':
                mode = 'OPTIMAL'
            else:
                mode = 'LEARN'
            #Determine Bot type
            if sys.argv[1] == 'GB':
                Bot = GeneralBot(fname="gb_qtable.p" if mode != "LEARN" else None)
            elif sys.argv[1] == 'SB':
                Bot = SpecialistBot(fname="sb_qtable.p" if mode != "LEARN" else None)
            else:
                Bot = GeneralBot(epsilon=1)
            #Determine Round number
            rounds = int(sys.argv[3])
        except Exception e:
            print 'something went wrong:', e
            return
    else:
        raise TypeError("Not enough args: ['SB'/'GB'/'DB'] ['L'/'O'/] [int numRounds]")

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
    encounters = len(Arena.ENTITY_LIST)*rounds
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
        if mode == "LEARN":
            Bot.run(agent_host)
        else:
            Bot.runOptimal(agent_host)
        print "Mission has stopped.\n"
        if  ((n+1)%len(Arena.ENTITY_LIST) == 0):
            print "Saving {}...\n".format("Q-Table & Results" if mode == "LEARN" else "Results")
            if mode == "LEARN":
                Bot.log_Q()
            Bot.log_results("temp_"+sys.argv[1]+"_results.txt")
        # -- clean up -- #
        time.sleep(2)  # (let the Mod reset)
    print "Done."
    if mode == "LEARN":
        Bot.log_Q()
    f_str = 'results_'+sys.argv[1]+"_optimal@.txt'
    count = 1
    new_f = f_str.replace('@',str(count))
    while os.path.isfile(new_f):
        count += 1
        new_f = f_str.replace('@',str(count))
    Bot.log_results(new_f)

if __name__ == '__main__':
    startingtime = time.time()
    main()
    elapsed = timedelta(seconds=time.time()-startingtime)
    print "Total time taken: ",str(elapsed)
