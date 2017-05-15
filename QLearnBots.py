# Basic Structure of Q Learning Agents adapted from Assignment2.py

import Arena
import MalmoPython
import math
import time
import json
import os, sys, random
from collections import defaultdict, deque

general_states = set()
spec_states = set()
possible_actions = ["move 0.75", "move 0", "move -0.75", "strafe 0.75", "strafe 0", "strafe -0.75", "attack 1", "switch"]

class GeneralBot:
    """GeneralBot will be given an AgentHost in its run method and use QTabular learning to attack enemies,
    ignoring enemy type for strategy"""
    def __init__(self, alpha=0.3, gamma=1, n=1):
        """Constructing an RL agent.

        Args
            alpha:  <float>  learning rate      (default = 0.3)
            gamma:  <float>  value decay rate   (default = 1)
            n:      <int>    number of back steps to update (default = 1)
        """
        self.agent = None
        self.epsilon = 0.2  # chance of taking a random action instead of the best
        self.q_table = defaultdict(lambda : {action: 0 for action in possible_actions}) #Did I mention how much I love comprehenions?
        self.n, self.gamma, self.alpha = n, alpha, gamma

    def get_curr_state(self, obs): # Not sure if
        '''
            Discretize distance, player health, and current_weapon into states:
                Distance (melee, close, far), Health (<10%, 10-60%, 60-100%), current_weapon (sword, bow)
            Add a state for EnemyType in the Specialist
        '''
        ent = None
        for mob in obs['entities']:
            if mob['name'] != obs['Name']:
                ent = mob
                break
        self.track_target(obs, mob)
        dist = self.calcDist(ent['x'], ent['y'], ent['z'], obs['XPos'], obs['YPos'], obs['ZPos'], mob['name'])
        dist = 0 if dist <= 2 else 1 if dist <= 10 else 2 # Discretize the distance
        health = obs['Life']
        health = "L" if health <= 2 else "M" if health <= 12 else "H"
        weap = None #de
        pass
        return (dist, health)

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
        self.agent.sendCommand(action)
        return

    def update_q_table(self, tau, S, A, R, T):
        """Performs relevant updates for state tau.
        Args
            tau: <int>  state index to update
            S:   <dequqe>   states queue
            A:   <dequqe>   actions queue
            R:   <dequqe>   rewards queue
            T:   <int>      terminating state index
        """
        curr_s, curr_a, curr_r = S.popleft(), A.popleft(), R.popleft()
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
        ex, ey, ez = entity['x'], entity['y'], entity['z']
        x, y, z = obs['XPos'], obs['YPos'], obs['ZPos']
        selfyaw, selfpitch = obs['Yaw'], obs['Pitch']
        try:
            deltaYaw, deltaPitch = self.calcYawPitch(name, ex, ey, ez, selfyaw, selfpitch, x, y, z)
            self.agent.sendCommand("turn " + str(deltaYaw))
            self.agent.sendCommand("pitch " + str(deltaPitch))
        except(KeyError e):
            print "Unidentified entity!", e
        
    def calcYawPitch(self, name, ex, ey, ez, selfyaw, selfpitch, x, y, z): #Adapted from cart_test.py
        ''' Find the mob we are following, and calculate the yaw we need in order to face it '''
        dx = ex - x
        dz = ez - z
        dy = (ey+Arena.HEIGHT_CHART[name]/2) - (y+1.8) #calculate height difference between our eye level and center of mass for entity
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


    def run(self, agent_host):
        """Run the agent_host on the world, acting according to the epilon-greedy policy"""
        self.agent = agent_host
        world_state = self.agent.getWorldState()
        while world_state.is_mission_running:
            time.sleep(0.1)
            world_state = self.agent.getWorldState()
            if world_state.number_of_observations_since_last_state > 0:
                obs = json.loads(world_state.observations[-1].text)
                state =  self.get_curr_state(obs)
                action = self.choose_action(state, possible_actions, self.epsilon)
                self.act(action)
                print action
        return

    def log_results():
        return

class SpecialistBot(GeneralBot):
    """SpecialistBot will be given an AgentHost in its run method and use QTabular learning to attack enemies,
    caring about enemy type for strategy"""
    def __init__(self, alpha=0.3, gamma=1, n=1):
        super().__init__(alpha, gamma, n)

    def get_curr_state(self, obs, ent): # Not sure if
        '''
            Discretize distance, player health, and current_weapon into states:
                Distance (melee, close, far), Health (<10%, 10-60%, 60-100%), current_weapon (sword, bow)
            Add a state for EnemyType in the Specialist
        '''

        dist = calcDist(ent['x'], ent['x'], ent['x'], obs['x'], obs['x'], obs['x'])
        dist = 0 if dist <= 2 else 1 if dist <= 10 else 2
        return

def main():
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately
    GB = GeneralBot()
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
    for i in range(encounters):
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
        GB.run(agent_host)
        print "Mission has stopped.\n"
        # -- clean up -- #
        time.sleep(2)  # (let the Mod reset)
    print "Done."

if __name__ == '__main__':
    main()