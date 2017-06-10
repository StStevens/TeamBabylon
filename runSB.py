from SpecialistBot import SpecialistBot
import Arena
import sys, os
import os.path
import MalmoPython
import time
from datetime import timedelta

def main():
    flag = len(sys.argv) > 1
    mode = None
    if flag:
        try:
            if sys.argv[1] == 'L':
                mode = 'LEARN'
            else:
                mode = 'OPTIMAL'
            rounds = int(sys.argv[2])
        except:
            print('terminal arg must be a number')
            flag = 0
    if flag == 0:
        try:
            rounds = int(input('number of rounds = '))
        except:
            print('needs to be a number')
            return

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
            SB.run(agent_host)
        else:
            SB.runOptimal(agent_host)
        print "Mission has stopped.\n"
        if  ((n+1)%len(Arena.ENTITY_LIST) == 0):
            print "Saving {}...\n".format("Q-Table & Results" if mode == "LEARN" else "Results")
            if mode == "LEARN":
                SB.log_Q()
            SB.log_results("temp_osb_results.txt", app=True)
        # -- clean up -- #
        time.sleep(2)  # (let the Mod reset)
    print "Done."
    if mode == "LEARN":
        SB.log_Q()
    f_str = 'results_sb_optimal@.txt'
    count = 1
    new_f = f_str.replace('@',str(count))
    while os.path.isfile(new_f):
        count += 1
        new_f = f_str.replace('@',str(count))
    SB.log_results(new_f)


if __name__ == '__main__':
    startingtime = time.time()
    main()
    elapsed = timedelta(seconds=time.time()-startingtime)
    print "Total time taken: ",str(elapsed)
