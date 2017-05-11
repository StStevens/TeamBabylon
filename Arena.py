# Arena Methods Python
# Used Tutorial 2 and 6 for sampling
# Usage:
#   Generate the XML schema for a given entity encounter
#   Contains the definitions for enemy heights and the Minecraft/Malmo name-mapping function
#   calculates the delta yaw and delta pitch from an entity to our player
#
import math

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
TIMELIMIT = 3000
ENTITY_LIST = ["Zombie", "Zombie"]#HEIGHT_CHART.keys()

def malmoName(minecraftName):
    '''returns the malmo-appropriate name of a given entity'''
    if minecraftName not in NAME_MAPPING.keys():
        return minecraftName
    return NAME_MAPPING[minecraftName]

def create_mission(entity, trackw=TRACK_WIDTH, trackb=TRACK_BREADTH, trackh=TRACK_HEIGHT, timelimit=TIMELIMIT):
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
                        <StartTime>18000</StartTime>
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
                    <DrawEntity x="25.0" y="4.0" z="25" type="@@@"/>
                  </DrawingDecorator>
                </ServerHandlers>
              </ServerSection>
              <AgentSection mode="Survival">
                <Name>MurderBot</Name>
                <AgentStart>
                  <Placement x="25" y="4.0" z="35" pitch="0" yaw="-180"/>
                  <Inventory>
                    <InventoryObject slot="0" type="wooden_sword" quantity="1"/>
                    <InventoryObject slot="1" type="bow" quantity="1"/>
                    <InventoryObject slot="2" type="arrow" quantity="64"/>
                  </Inventory>
                </AgentStart>
                <AgentHandlers>
                  <ObservationFromFullStats/>
                  <RewardForMissionEnd rewardForDeath="-100">
                    <Reward description="out_of_time" reward="-10" />
                  </RewardForMissionEnd>
                  <AgentQuitFromTimeUp timeLimitMs="'''+str(timelimit)+'''" description="out_of_time"/>
                  <ContinuousMovementCommands turnSpeedDegs="1080"/>
                  <ObservationFromNearbyEntities>
                    <Range name="entities" xrange="'''+str(trackw)+'''" yrange="'''+str(trackh)+'''" zrange="'''+str(trackb)+'''" />
                  </ObservationFromNearbyEntities>
                </AgentHandlers>
              </AgentSection>
            </Mission>'''
    missionXML = missionXML.replace("@@@", entity)
    return missionXML

def calcYawPitch(name, ex, ey, ez, selfyaw, selfpitch, x, y, z): #Adapted from cart_test.py
    ''' Find the mob we are following, and calculate the yaw we need in order to face it '''
    dx = ex - x
    dz = ez - z
    dy = (ey+HEIGHT_CHART[name]/2) - (y+1.8) #calculate height difference between our eye level and center of mass for entity
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
