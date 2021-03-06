# Basic Structure of Q Learning Agents adapted from Assignment2.py
import Arena
import MalmoPython
import math
import time
import json
import pickle
import os, sys, random
from collections import defaultdict, deque

class GeneralBot:
    """GeneralBot will be given an AgentHost in its run method and use QTabular learning to attack enemies,
    ignoring enemy type for strategy"""
    def __init__(self, alpha=0.3, gamma=1, n=25, epsilon=0.3, fname=None):
        """Constructing an RL agent.

        Args
            alpha:   <float>  learning rate      (default = 0.3)
            gamma:   <float>  value decay rate   (default = 1)
            epsilon: <float>  random chance rate (default = 0.3)
            n:       <int>    number of back steps to update (default = 1)
            fname:   <string> filename to store resulting q-table in
        """
        self.fname = fname
        self.agent = None
        self.weapon = "sword"
        if fname:
            f = open(fname, "r")
            self.q_table = pickle.load(f)
        else:
            self.fname = "gb_qtable.p" if epsilon != 1 else "db_qtable.p"
            self.q_table = dict() # Create the Q-Table
            for dist in ["Close", "Melee", "Far"]:
                for health in ["Low", "Med", "Hi"]:
                    for weap in ["sword", "bow"]:
                        self.q_table[(dist,health,weap)] = {action : 0 for action in self.get_possible_actions(weap)}
        self.n, self.gamma, self.alpha, self.epsilon = n, gamma, alpha, epsilon
        self.history = []

    def get_curr_state(self, obs, ent):
        '''
            Discretize distance, player health, and current_weapon into states:
                Distance (melee, close, far), Health (<10%, 10-60%, 60-100%), current_weapon (sword, bow)
            Add a state for EnemyType in the Specialist
        '''
        if ent['name'] in Arena.HEIGHT_CHART.keys():
            dist = self.calcDist(ent['x'], ent['y'], ent['z'], obs['XPos'], obs['YPos'], obs['ZPos'], ent['name'])
            dist = "Close" if dist <= 2 else "Melee" if dist <= 4 else "Far" # Discretize the distance
            health = obs['Life']
            health = "Low" if health <= 5 else "Med" if health <= 12 else "Hi"
            weap = self.weapon
            return (dist, health, weap)
        return ("Finished",)

    def choose_action(self, curr_state, possible_actions, eps):
        """Chooses an action according to eps-greedy policy. """
        renegade = random.random()
        if renegade < eps:
            return random.choice(possible_actions)
        choice = []
        score = None
        for action in possible_actions:
            possible = self.q_table[curr_state][action]
            if possible > score:
                choice = [ action ]
                score = possible
            elif possible == score:
                choice.append(action)
        return random.choice(choice)

    def act(self, action):
        """"Sends a command to the agent to take the chosen course of action"""
        if action == "switch":
            switchCommand = "hotbar.2 1" if self.weapon == "sword" else "hotbar.1 1"
            self.agent.sendCommand(switchCommand)
            switchCommand = switchCommand[:-1]+"0"
            self.agent.sendCommand(switchCommand)
            self.weapon = "bow" if self.weapon == "sword" else "sword"
            self.agent.sendCommand("use 0")
            return
        self.agent.sendCommand(action)
        return

    def clearAction(self, action):
        """Send a command to negate the given action"""
        if "attack" in action:
            self.agent.sendCommand("attack 0")
        if "switch" in action:
            self.agent.sendCommand("attack 0")
        elif "strafe" in action:
            self.agent.sendCommand("strafe 0")
        elif "move" in action:
            self.agent.sendCommand("move 0")

    def calc_reward(self, time_taken, healthDelta, damageDelta):
        reward = 0
        reward += damageDelta * 15
        reward += healthDelta * 10
        return -10 if reward == 0 else reward

    def update_q_table(self, tau, S, A, R, T):
        """Performs relevant updates for state tau.
        Args
            tau: <int>  state index to update
            S:   <dequqe>   states queue
            A:   <dequqe>   actions queue
            R:   <dequqe>   rewards queue
            T:   <int>      terminating state index
        """
        curr_s = S.popleft()
        curr_a = A.popleft()
        curr_r = R.popleft()
        G = sum([self.gamma ** i * R[i] for i in range(len(S))])
        if tau + self.n < T:
            G += self.gamma ** self.n * self.q_table[S[-1]][A[-1]]

        old_q = self.q_table[curr_s][curr_a]
        self.q_table[curr_s][curr_a] = old_q + self.alpha * (G - old_q)

    def calcDist(self, ex, ey, ez, x, y, z, mob):
        dx = ex - x
        dz = ez - z
        dy = (ey+Arena.HEIGHT_CHART[mob]/2) - (y+1.8)
        return math.sqrt(dx**2 + dy**2 + dz**2)

    def track_target(self, obs, entity):
        if self.agent == None:
            return
        name = entity['name']
        if entity['name'] in Arena.HEIGHT_CHART.keys():
            ex, ey, ez = entity['x'], entity['y'], entity['z']
            x, y, z = obs['XPos'], obs['YPos'], obs['ZPos']
            selfyaw, selfpitch = obs['Yaw'], obs['Pitch']
            deltaYaw, deltaPitch = self.calcYawPitch(name, ex, ey, ez, selfyaw, selfpitch, x, y, z)
            self.agent.sendCommand("turn " + str(deltaYaw))
            self.agent.sendCommand("pitch " + str(deltaPitch))
        else:
            self.agent.sendCommand("turn 0")
            self.agent.sendCommand("pitch 0")
            self.agent.sendCommand("move 0")
            self.agent.sendCommand("attack 0")
            return

    def calcYawPitch(self, name, ex, ey, ez, selfyaw, selfpitch, x, y, z): #Adapted from cart_test.py
        ''' Find the mob we are following, and calculate the yaw we need in order to face it '''
        dx = ex - x
        dz = ez - z
        if self.weapon == "sword":
            dy = (ey+Arena.HEIGHT_CHART[name]/2) - (y+1.8) #calculate height difference between our eye level and center of mass for entity
        else:
            dy = (ey+Arena.HEIGHT_CHART[name]) - (y+1.8) #Aim a little upwards with the bow
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
        pitch = -180*math.atan2(dy, h_dist) / math.pi
        deltaPitch = pitch - selfpitch
        while deltaPitch < -180:
            deltaPitch += 360
        while deltaPitch > 180:
            deltaPitch -= 360
        deltaPitch /= 180.0
        return deltaYaw, deltaPitch

    def runOptimal(self, agent_host):
        roundTimeStart = time.time()
        self.agent = agent_host
        world_state = self.agent.getWorldState()
        kill = 0
        round_enemy = None
        enemyHealth = -1
        agentHealth = -1
        state = ("",)
        action = ""
        lastActionTime = 0
        while world_state.is_mission_running and state != ("Finished",):
            time.sleep(0.01)
            currentTime = time.time()
            world_state = self.agent.getWorldState()
            if world_state.number_of_observations_since_last_state > 0:
                obs = json.loads(world_state.observations[-1].text)
                if state == ("last check",):
                    state = ("Finished",)
                    agentHealth = obs['Life']
                    break
                if "Name" not in obs: #Edge case where we observe before load.
                    continue
                enemy = None
                for e in obs['entities']:
                    if e['name'] != obs['Name'] and 'life' in e:
                        round_enemy = e['name']
                        enemy = e
                        break
                if enemy == None:
                    state = ("last check",)
                    continue
                self.track_target(obs, enemy)
                if currentTime - lastActionTime >= 200:
                    agentHealth = obs['Life']
                    state = self.get_curr_state(obs, enemy)
                    self.clearAction(action)
                    p_actions = self.get_possible_actions(self.weapon)
                    action = self.choose_action(state, p_actions, 0)
                    self.act(action)
                if state == ("Finished",):
                    break
        timeInRound = time.time() - roundTimeStart
        if state == ("Finished",) and agentHealth != 0:
            kill = 1
            self.agent.sendCommand("quit")
        else:
            kill = 0
            if abs((Arena.TIMELIMIT/1000)-timeInRound) > 1:
                agentHealth = 0
        self.update_history(round_enemy, agentHealth, timeInRound, kill)
        return

    def get_possible_actions(self, weap):
        '''Returns a list of possible actions based on weapon type'''
        if weap == "bow":
            return ["move 1", "move -1", "strafe 1", "strafe -1", "use 1", "use 0", "switch"]
        else: #using sword
            return ["move 1", "move -1", "strafe 1", "strafe -1", "attack 1", "switch"]

    def run(self, agent_host):
        """Run the agent_host on the world, acting according to the epsilon-greedy policy"""
        roundTimeStart = time.time()
        kill = 0
        round_enemy = None
        self.agent = agent_host
        max_score = 0
        min_score = 100
        S, A, R = deque(), deque(), deque()
        world_state = self.agent.getWorldState()
        if world_state.number_of_observations_since_last_state > 0:
            obs = json.loads(world_state.observations[-1].text)

        t = 0
        enemyHealth = -1
        agentHealth = -1
        state = ("",)
        action = ""
        lastActionTime = 0
        while world_state.is_mission_running and state != ("Finished",):
            time.sleep(0.01)
            currentTime = time.time()
            world_state = self.agent.getWorldState()
            if world_state.number_of_observations_since_last_state > 0:
                obs = json.loads(world_state.observations[-1].text)
                if state == ("last check",):
                    state = ("Finished",)
                    agentHealth = obs['Life']
                    break
                if "Name" not in obs: #Edge case where we observe before load.
                    continue
                enemy = None
                for e in obs['entities']:
                    if e['name'] != obs['Name'] and 'life' in e:
                        round_enemy = e['name']
                        enemy = e
                        break
                if enemy == None:
                    state = ("last check",)
                    continue
                self.track_target(obs, enemy)
                if currentTime - lastActionTime >= 200:
                    state = self.get_curr_state(obs, enemy)
                    self.clearAction(action)
                    p_actions = self.get_possible_actions(self.weapon)
                    action = self.choose_action(state, p_actions, self.epsilon)
                    damageDelta = 0
                    healthDelta = 0
                    if enemyHealth == -1:
                        enemyHealth = enemy['life']
                    elif enemy['life'] != enemyHealth:
                        damageDelta = enemyHealth - enemy['life']
                        enemyHealth = enemy['life']
                    if agentHealth == -1:
                        agentHealth = obs['Life']
                    elif obs['Life'] != agentHealth:
                        healthDelta = obs['Life'] - agentHealth
                        agentHealth = obs['Life']
                    score = self.calc_reward(30, healthDelta, damageDelta)
                    if score > max_score:
                        max_score = score
                    if score < min_score:
                        min_score = score
                    R.append(score)
                    T = t - self.n + 1
                    if T >= 0:
                        self.update_q_table(t, S, A, R, T)
                    S.append(state)
                    A.append(action)
                    t += 1
                    self.act(action)
                if state == ("Finished",):
                    break

        timeInRound = time.time() - roundTimeStart
        if state == ("Finished",) and agentHealth != 0:
            kill = 1
            self.agent.sendCommand("quit")
        else:
            kill = 0
            if abs((Arena.TIMELIMIT/1000)-timeInRound) > 1:
                agentHealth = 0
        print ('max_score = {}, min_score = {}'.format(max_score, min_score))
        self.update_history(round_enemy, agentHealth, timeInRound, kill)
        return

    def update_history(self, enemy, health, time, kill):
        print('enemy={}, agentHealth={}, timeInRound={}, kill={}'.format(enemy, health, time, kill))
        if enemy != None:
            self.history.append((enemy, health, time, kill))
            return
        if health == -1:
            raise ValueError('Health is -1')
        return

    def log_Q(self):
        try:
            f = open(self.fname, 'w')
            pickle.dump(dict(self.q_table), f)
            f.close()
        except Exception as e:
            print e

    def log_results(self, filename, app=False):
        try:
            f = open(filename, 'a' if app else 'w')
            for result in self.history:
                f.write(str(result[0])+',')
                f.write(str(result[1])+',')
                f.write('{:5.3f},'.format(result[2]))
                f.write('{}'.format(result[3]))
                f.write('\n')
            f.close()
        except Exception as e:
            print e

def main():
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately
    GB = GeneralBot(fname='gb_qtable_start.p')
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
    encounters = len(Arena.ENTITY_LIST)*10
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
        if n % 5 == 0 and n != 0:
            print "Optimal Strategy so far..."
            GB.runOptimal(agent_host)
        else:
            GB.run(agent_host)
        print "Mission has stopped.\n"
        # -- clean up -- #
        time.sleep(2)  # (let the Mod reset)
    print "Done."
    GB.log_Q()
    GB.log_results('gb_results_base2.txt')

if __name__ == '__main__':
    main()
