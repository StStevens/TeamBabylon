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
    def __init__(self, alpha=0.3, gamma=1, n=5, epsilon=0.2, fname=None):
        """Constructing an RL agent.

        Args
            alpha:  <float>  learning rate      (default = 0.3)
            gamma:  <float>  value decay rate   (default = 1)
            n:      <int>    number of back steps to update (default = 5)
            epsilon: <float> chance to take a random action (default = 0.2)
            fname:  <string> filename to store resulting q-table in
        """
        self.Movement = ["move 1", "move 0", "move -1", "strafe 1", "strafe -1"]
        self.actionDelay = 0.2
        self.fname = fname
        self.agent = None
        self.weapon = "sword"
        self.epsilon = epsilon  # chance of taking a random action instead of the best
        if fname:
            f = open(fname, "r")
            q_tables = pickle.load(f)
            self.q_table = q_tables['action']
            self.qMovement = q_tables['movement']
        else:
            self.fname = "gb_qtable.p"
            self.q_table = dict() # Create the Q-Table
            self.qMovement = dict()
            for dist in ["Close", "Melee", "Far"]:
                for health in ["Low", "Med", "Hi"]:
                    for weap in ["sword", "draw 1", "draw 2", "draw 3", "draw 4", "draw 5", "fire"]:
                        self.q_table[(dist,health,weap)] = {action : 0 for action in self.get_possible_actions(weap)}
                        self.qMovement[(dist,health, weap)] = {action : 0 for action in self.Movement}
        self.n, self.gamma, self.alpha = n, gamma, alpha
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

    def choose_movement(self, curr_state, eps):
        """ Chooses a movement accordning to eps-greedy policy. """
        renegade = random.random()
        if renegade <eps:
            return random.choice(self.Movement)
        choice = []
        score = None
        for action in self.Movement:
            possible = self.qMovement[curr_state][action]
            if possible > score:
                choice = [ action ]
                score = possible
            elif possible == score:
                choice.append(action)
        return random.choice(choice)

    def act(self, action):
        """"Sends a command to the agent to take the chosen course of action"""
        location = ""
        if action == "sword":
            if self.weapon != "sword":
                self.agent.sendCommand("hotbar.1 1")
                self.agent.sendCommand("hotbar.1 0")
                self.agent.sendCommand("use 0");
            self.agent.sendCommand("attack 1")
            self.weapon = action
        elif "draw" in action:
            if self.weapon == "sword":
                self.agent.sendCommand("attack 0")
                self.agent.sendCommand("hotbar.2 1")
                self.agent.sendCommand("hotbar.2 0")
                self.agent.sendCommand("use 1")
            if self.weapon == "fire":
                self.agent.sendCommand("use 1")
            self.weapon = action
        elif action == "fire":
            self.agent.sendCommand("use 0")
            self.weapon = action
        else:
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
        if reward == 0:
            reward -= 1
        return reward

    def update_q_table(self, tau, S, A, M, R, T):
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
        curr_m = M.popleft()
        G = sum([self.gamma ** i * R[i] for i in range(len(S))])
        action_G = G
        move_G = G
        if tau + self.n < T:
            action_G += self.gamma ** self.n * self.q_table[S[-1]][A[-1]]
            move_G += self.gamma ** self.n * self.qMovement[S[-1]][M[-1]]

        old_action = self.q_table[curr_s][curr_a]
        old_move = self.qMovement[curr_s][curr_m]
        self.q_table[curr_s][curr_a] = old_action + self.alpha * (action_G - old_action)
        self.qMovement[curr_s][curr_m] = old_move + self.alpha * (move_G - old_move)

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
        return self.run(agent_host, optimal=True)

    def get_possible_actions(self, weap):
        '''Returns a list of possible actions based on weapon type'''
        if weap == "sword":
            return ["sword", "draw 1"]
        elif "draw" in weap:
            nextDraw = int(weap[-1]) + 1
            if nextDraw > 5:
                return [ "fire" ]
            else:
                return [ "fire", "draw " + str(nextDraw) ]
        elif weap == "fire":
            return ["sword", "draw 1"]
            

    def run(self, agent_host, optimal=False):
        """Run the agent_host on the world, acting according to the epsilon-greedy policy"""
        roundTimeStart = time.time()
        kill = 0
        round_enemy = None
        self.agent = agent_host
        max_score = 0
        min_score = 100
        S, A, M, R = deque(), deque(), deque(), deque()
        world_state = self.agent.getWorldState()
        if world_state.number_of_observations_since_last_state > 0:
            obs = json.loads(world_state.observations[-1].text)

        t = 0
        enemyHealth = -1
        agentHealth = -1
        state = ("",)
        action = ""
        movement = ""
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
                if currentTime - lastActionTime >= self.actionDelay:
                    lastActionTime = currentTime
                    state = self.get_curr_state(obs, enemy)
                    self.clearAction(action)
                    p_actions = self.get_possible_actions(self.weapon)
                    if optimal:
                        action = self.choose_action(state, p_actions, 0)
                        movement = self.choose_movement(state, 0)
                    else:
                        action = self.choose_action(state, p_actions, self.epsilon)
                        movement = self.choose_movement(state, self.epsilon)
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
                    if T >= 0 and not optimal:
                        self.update_q_table(t, S, A, M, R, T)
                    S.append(state)
                    A.append(action)
                    M.append(movement)
                    t += 1
                    self.act(action)
                    self.act(movement)
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

    def log_Q(self):
        try:
            q_tables = {}
            q_tables['action'] = self.q_table
            q_tables['movement'] = self.qMovement
            f = open(self.fname, 'w')
            pickle.dump(q_tables, f)
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
