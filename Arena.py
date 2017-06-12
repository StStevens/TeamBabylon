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
    "Ghast":4, "Zombie Pigman":1.95, "Cave Spider":1, "Silverfish":0.3,
    "Blaze":2, "Witch":1.95, "Endermite":0.3, "Wolf": 0.85
}

NAME_MAPPING = {
    "Zombie Pigman" : "PigZombie",
    "Cave Spider" : "CaveSpider",
}


def malmoName(minecraftName):
    '''returns the malmo-appropriate name of a given entity'''
    if minecraftName not in NAME_MAPPING.keys():
        return minecraftName
    return NAME_MAPPING[minecraftName]

TRACK_WIDTH = 30
TRACK_BREADTH = 30
TRACK_HEIGHT = 30
TIMELIMIT = 25000
ENTITY_LIST = HEIGHT_CHART.keys()
AGENT_NAME = "MurderBot"

def malmoName(minecraftName):
    '''returns the malmo-appropriate name of a given entity'''
    if minecraftName not in NAME_MAPPING.keys():
        return minecraftName
    return NAME_MAPPING[minecraftName]

def create_mission(entity, agent_name=AGENT_NAME, trackw=TRACK_WIDTH, trackb=TRACK_BREADTH, trackh=TRACK_HEIGHT, timelimit=TIMELIMIT):
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
                    <DrawCuboid type="bedrock" x1="0" y1="4" z1="0" x2="0" y2="12" z2="30"/>
                    <DrawCuboid type="bedrock" x1="0" y1="4" z1="0" x2="30" y2="12" z2="0"/>
                    <DrawCuboid type="bedrock" x1="30" y1="4" z1="30" x2="0" y2="12" z2="30"/>
                    <DrawCuboid type="bedrock" x1="30" y1="4" z1="30" x2="30" y2="12" z2="0"/>
                    <DrawCuboid type="glowstone" x1="0" y1="14" z1="0" x2="30" y2="12" z2="30"/>
                    <DrawEntity x="18.0" y="4.0" z="10" type="@@@"/>
                  </DrawingDecorator>
                  <ServerQuitWhenAnyAgentFinishes description="server sees murder happen"/>
                </ServerHandlers>
              </ServerSection>
              <AgentSection mode="Survival">
                <Name>''' + agent_name + '''</Name>
                <AgentStart>
                  <Placement x="15" y="4.0" z="20" pitch="0" yaw="-180"/>
                  <Inventory>
                    <InventoryObject slot="0" type="wooden_sword" quantity="1"/>
                    <InventoryObject slot="1" type="bow" quantity="1"/>
                    <InventoryObject slot="2" type="arrow" quantity="64"/>
                  </Inventory>
                </AgentStart>
                <AgentHandlers>
                  <MissionQuitCommands
                    quitDescription="finished murdering">
                      <ModifierList
                        type='allow-list'>
                          <command>quit</command>
                      </ModifierList>
                  </MissionQuitCommands>
                  <ObservationFromFullStats/>
                  <AgentQuitFromTimeUp timeLimitMs="'''+str(timelimit)+'''" description="out_of_time"/>
                  <ContinuousMovementCommands turnSpeedDegs="900"/>
                  <InventoryCommands>
                    <ModifierList type = "deny-list">
                        <command>discardCurrentItem</command>
                    </ModifierList>
                  </InventoryCommands>
                  <ObservationFromNearbyEntities>
                    <Range name="entities" xrange="'''+str(trackw)+'''" yrange="'''+str(trackh)+'''" zrange="'''+str(trackb)+'''" />
                  </ObservationFromNearbyEntities>
                  <ObservationFromHotBar/>
                </AgentHandlers>
              </AgentSection>
            </Mission>'''
    missionXML = missionXML.replace("@@@", entity)
    return missionXML
