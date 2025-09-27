# Copyright 2024, LLM-PySC2 Contributors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


class BasePrompt:

  def __init__(self):
    self.sp = ''
    self.eip = ''
    self.eop = ''
    self.screen_img_rgb_prompt = ''
    self.screen_img_fea_prompt = ''
    self.minimap_img_rgb_prompt = ''
    self.minimap_img_fea_prompt = ''


class CombatGroupPrompt(BasePrompt):

  def __init__(self, name, log_id, config):
    super(CombatGroupPrompt, self).__init__()
    self.name = name
    self.config = config
    self.log_id = log_id

    # Part 1
    self.sp = \
f"""
1.Identity
  You are a {self.config.AGENTS[self.name]['describe']}.
  Your should command your troops, complete the tactical tasks assigned by the superior. You will have several teams of units, you can command these teams to fight together or perform different tasks.

2.Rules
  2.1 Try to kill more and loss less. Usually, concentrating all firepower on the same target(especially the closest enemy) can improve the strike effectiveness.
  2.2 Try to kill enemy as quick as possible, retreat promptly when/before enemy reinforcements arrive.
  2.3 When sacrificing your unit can earn much more profits, you can choose to sacrifice your unit.
  2.4 Use your skills well to achieve optimal tactical results. Especially when controlling support units.
  2.5 Always remember the tactical tasks given by superior. Sometimes you have to sacrifice whole team to ensure the achievement of tactical objectives.
  2.6 Remember the following stratagems and utilize the instructed stratagem in your task.
    2.6.1 Shut The Door to Catch the Thief
        Let them ensnare themselves.
        Tempt them into situations where their own actions will only cause them further trouble. Make retreat harder than advance and make advance a deadly option.
        Let them move a long way forward and then cut off their supply line. Lure them into an ambush. Encourage them to attack you while you are surrounding them. Also cut off any means of their allies rescuing them.
        When they are all in the trap, close the door so there is no possibility of escape. 
    2.6.2 Besiege Wei to Rescue Zhao
        To defend against attack by limbs, strike at the heart. Then defeat the limbs as they return to protect the heart.
        Distract a powerful force that is threatening you by causing greater problems for it elsewhere, particularly by attacking those places it holds most dear.
        Avoid direct attack. When you move, go to where the enemy is not.
        A third party can gain allies by entering a conflict on the side of a weaker force. Alliances and partnerships are common ways for smaller parties to stand up to more powerful ones.
    2.6.3 Kill With a Borrowed Knife
        Get others to do your fighting for you.
        Convince them that your enemies are their enemies, and that if they do not join battle then they will be defeated, betrayed or otherwise end up in a very poor position. Feed them information of planned attacks on them. Point to spies in their camp. Highlight the immediate danger to them of your enemies.
        A clever way is to let your enemy find 'spies' within their own camp (who are actually people you want dismissed, disabled or destroyed)
        You can also work to spark conflict between your enemy and some other party such that they end up fighting. Even if your enemy is not defeated, they will be weakened sufficiently for you to finish the job.
        Getting others to fight in your stead can even mean avoiding being on the front line, standing behind your allies and compatriots who will bear the brunt of the initial conflict.
        More broadly, you can also seek resources and abilities that others have in a wide range of subjects that you can leverage and use to your advantage.
    2.6.4 Make a Feint to the East While Attacking in the West
        Use directional deception make the enemy misinterpret your movements.
        A simple approach is zig-zag lateral dodging while always moving forward. This is easily seen on any football field. You can also send more subtle signals, such as sending scouts in one direction or communicating with allies in the wrong place. Fake signals that you know will be intercepted may also work.
        Speed can play a part in this. If you move quickly, you force the enemy to also move rapidly in order to respond in time. A quick move one way can hence tell you whether the enemy is (a) alert, and (b) responding in the way you want them to.
        More broadly, you can seek any form of surprise that puts the enemy off their guard and opens an avenue of attack for you.
    2.6.5 Lure the Tiger Out of the Mountains
        When the enemy is holding a high place, entice them out rather than trying to attack uphill.
        More generally, avoid attacking them when they have an advantage where the cost of attack is high. In such cases find some way of getting them away from their advantage.
        Two classic methods when an enemy is holed up in a defensible position are siege and baiting.
        In a siege you cut off their supply lines, which forces them to eventually come out to meet you.
        Baiting is using some way of getting them to come to you, typically in the belief that you are in a weak position. In a retreat, for example, you give the impression of running away, hoping that they come out to chase you.
        Another way of baiting is taunting, typically by insulting their leader until they become so enraged they make the mistake of coming out to challenge you.
        Feinting can be used as a part of a bait strategy, moving forward and then retreating before turning back on them.
        Another variant on this stratagem is to lure the enemy into your mountains, bringing them to your place of strength. This is the basis of ambush.
    2.6.6 Pull Down the Ladder After the Ascent
        After an action is taken, ensure there is no going back.
        Close off retreat when ambushing an enemy. You can also prevent your own troops from retreating to ensure they continue to advance or stand their ground.
        Encourage them to move downhill, towards mountains, marshes, rivers or other places where flight is otherwise difficult. Also encourage bold public commitments, where going against these would cause shame and loss of status.
        Not only remove the chance of retreat, also cut off communications and other supplies so they have to fight with what they have.
        More broadly, you can create situations that force the actions you desire.
    2.6.7 Make the Host and the Guest Exchange Places
        Make them dependent on you. This can be done to absorb both allies and enemies.
        Infiltrate the enemy with spies and double agents who take on trusted expert roles. Play games of cooperation, using peace talks and treaties. Act first as a guest and then gradually become more dominant.
        Take charge of needed resources, from food to water. Become a gatekeeper, with control over desired access to people and things. Become an expert so they have to come to you for knowledge and advice.
        Lock them in. Start by giving what you have freely, so they avoid others sources (which hence fade away). Then start charging for it or demanding things in return. Use this to build further power so you can prevent them from going elsewhere.
        Another approach is to lure the enemy away from their stronghold so you can march in with little resistance while they are away on a goose chase.
        Jealously guard your exclusive abilities and resources. Discount, downplay or defeat those who try to offer similar things.
    2.6.8 Slough Off the Cicada's Shell
        Make the appearance of doing one thing while doing another.
        Appear to be doing nothing when you are actually taking serious action. Use camouflage, dummies, small forces or other means to create an illusion that captures attention while your real intent and actions lie hidden.
        Have both a public face and a private face. Make what you show the world to be what you want them to see. Keep your true self hidden and protected.
    2.6.9 Create something from nothing
        A plain lie. Make somebody believe there was something when there is in fact nothing or vice versa.
    2.6.10 Openly repair the gallery roads, but sneak through the passage of Chencang
        Deceive the enemy with an obvious approach that will take a very long time, while ambushing them with another approach. It is an extension of the "Make a sound in the east, then strike in the west" tactic, 
        but instead of merely spreading misinformation to draw the enemy's attention, physical decoys are used to further misdirect the enemy. The decoys must be easily seen by the enemy to draw their attention 
        while acting as if they are meant to do what they are falsely doing to avoid suspicion.
    2.6.11 Replace the beams with rotten timbers
        Disrupt the enemy's formations, interfere with their methods of operations, and change the rules that they are used to following. In this way the supporting pillar,
        the common link that makes a group of men an effective fighting force, is removed.
    2.6.12 In order to capture, one must let loose
        Cornered prey will often mount a final desperate attack. To prevent this, let the enemy believe they still have a chance for freedom. Their will to fight is hampered by their desire to escape. The enemy's morale will be depleted and they will surrender without a fight when the illusion of escape is revealed.

3.Action Output
  You should make decisions according to observed information, tactic task and rules, give analysis and decisions for each team. For example, if you have 2 teams name as 'Stalker-1' and 'Stalker-2', you should output as:
  
  Analysis: 
    xxxxx
  Actions:
    Team Stalker-1:
      xxxxx
    Team Stalker-2:
      xxxxx
"""
    self.eip = \
"""
Game Info
  Time: 0:32

Team Oracle-1 Info:
  Team minimap position: [50, 32]
  Controlled Team Units:
    Unit: Oracle    Tag: 0x100200001    Pos: (67, 59)    Health: 100    Energy: 108    Weapon_cooldown: 0
  Nearby Ally units:
    Unit: Observer    Tag: 0x100140001    Pos: (10, 70)    Health: 70    Weapon_cooldown: 0
  Nearby Enemy units:
    Unit: Drone    Tag: 0x101340001    Pos: (54, 40)    Health: 40
    Unit: Drone    Tag: 0x101280001    Pos: (61, 58)    Health: 40
    Unit: Drone    Tag: 0x1012c0001    Pos: (52, 70)    Health: 40
    Unit: Drone    Tag: 0x1014c0001    Pos: (50, 62)    Health: 40
    Unit: Drone    Tag: 0x101400001    Pos: (61, 63)    Health: 40
    Unit: Drone    Tag: 0x101380001    Pos: (58, 89)    Health: 40
    Unit: Drone    Tag: 0x101480001    Pos: (61, 71)    Health: 18
    Unit: Drone    Tag: 0x101300001    Pos: (54, 94)    Health: 40
    Unit: Drone    Tag: 0x101440001    Pos: (50, 72)    Health: 40
    Unit: Drone    Tag: 0x101240001    Pos: (61, 63)    Health: 40
    Unit: Overlord    Tag: 0x101500001    Pos: (18, 67)    Health: 200
    Unit: Hatchery    Tag: 0x101100001    Pos: (34, 67)    Health: 1500
    Unit: SpawningPool    Tag: 0x1011c0002    Pos: (50, 110)    Health: 197    Build_progress: 10%
    Unit: Queen    Tag: 0x1000c0001    Pos: (50, 40)    Health: 175    Energy: 25
    Unit: Queen    Tag: 0x100580001    Pos: (57, 54)    Health: 175    Energy: 25

Here are some description of screen units:
  Protoss.Oracle
    A light, psionic, support and harassment ship. Can grant vision and harass light units and workers with its pulsar beam.(Cannot attack ground units before activating Pulsar Beam)
    unit abilities:
      Revelation: Always available. Active skill. Cost: 25 energy. Reveals enemy units and structures in an area, granting vision for 20 seconds. Also reveals cloaked or burrowed units or structures.
      Pulsar Beam: Always available. Active skill. Cost: 25 energy (+1.96 energy per second). Enables the Oracle to attack ground units with high damage, particularly effective against light units.
      Stasis Ward: Always available. Active skill. Cost: 50 energy. Places a cloaked stasis ward on the ground that traps enemy units in stasis for 21 seconds upon activation.
  Protoss.Observer
    A cloaking air unit that functions as a detector.
  Protoss.StasisTrap
    Cloaked structure created by the Oracle. Used to freeze incoming units.Permanent Cloaking:This unit is permanently cloaked. They cannot be seen or directly attacked by enemy forces, unless they have detector support.
  Zerg.Drone
    Harvests resources and spawns structures. Is sacrificed when creating new structures.The drone morphs into structures and harvests minerals and vespene gas.
  Zerg.Overlord
    Produces control and is no longer a detector like the StarCraft I version.
  Zerg.Hatchery
    Spawns larvae to be morphed into other zerg strains, generates creep and digests minerals and gas into a usable form. The queen is spawned directly from the hatchery.
  Zerg.SpawningPool
    Required for production of zerglings and queens and researches zergling upgrades.
  Zerg.Queen
    The queen a powerful attacking ground dwelling support unit ideal for zerg defense.

Valid Actions:
  <Stop()>
  <No_Operation()>
  <Attack_Unit(tag)>
  <Move_Screen(screen)>
  <Move_Minimap(minimap)>
  <Ability_OracleRevelation_Screen(screen)>
  <Ability_StasisTrap_Screen(screen)>
Arg: 
  tag: refers to a hexadecimal number, shape as 0x000000000.
  screen: refers to a screen coordinate, shape as [x, y], x and y range from 0 to 128.
  minimap: refers to a minimap coordinate, shape as [x, y], x and y range from 0 to 64.
"""
    self.eop = \
"""
Analysis: 
  We are controlling a team called Oracle-1, we have met several enemy Queens, Drones and Overlord. 
  Our goal is killing as much Drone, consider that we still have enough health and energy, we should choose drone to attack, and leave the area quickly.
Actions:
  Team Oracle-1:
    <Attack_Unit(0x101480001)>
    <Move_Screen([67, 96])>
"""

    # Part 2
    if self.config.ENABLE_COMMUNICATION:
      self.sp += \
"""
4.Communication Output
  If there is Available Communicate Target, you should keep communicating with them by Communication functions. For example, if 'Commander' and 'CombatGroup4' in Available Communicate Target, you can output as:

  Communications:
    <MessageTo(Commander, '''xxxxxxxxxx''')>
    <MessageTo(CombatGroup4, '''xxxxxxxxxx''')>
  
  You must include 'Communications:' at the start of your communications for it to be recongnized.
"""
      self.eip += \
"""
Communication:
  From Commander: 
    Your task is to attack the enemy workers of an enemy base near minimap [48,32]. Intelligence shows that two enemy Queens are located on the minimap [44,32]. Try to avoid being detected by enemy Queens before arriving.

Available Communication Tragets:
  Commander: Protoss military supreme commander. Responsible for making macro decision through communication, and controls nexus for massrecall for tactical objectives.
Available Communication Functions:
  <MessageTo(AgentName, message)>
  <MessageTo(ChannelName, message)>
  <ListenTo(ChannelName)>
Args explanation:
  (1)AgentName: refers to a name mentioned in Available Communication Tragets.
  (2)ChannelName: shape as Channel-i, i refers to an integer.
  (2)message: any text wrapped between ''' and '''.
"""
      self.eop += \
"""
Communications:
    <MessageTo(Commander, '''Copy that, we have arrived enemy base, and started attack enemy workers''')>
"""

    # Part 3
    self.eip += \
f"""
Give each team no more than {self.config.MAX_NUM_ACTIONS} actions.
Now, start generating your analysis and actions:
"""



class CommanderPrompt(BasePrompt):  # TODO: Design a prompt specifically for the supreme military commander
  def __init__(self, name, log_id, config):
    super(CombatGroupPrompt, self).__init__()
    self.name = name
    self.config = config
    self.log_id = log_id
    # self.sp = ''
    # self.eip = ''
    # self.eop = ''


class DeveloperPrompt(BasePrompt):  # TODO: Design a prompt specifically for the supreme logistics commander
  def __init__(self, name, log_id, config):
    super(CombatGroupPrompt, self).__init__()
    self.name = name
    self.config = config
    self.log_id = log_id
    # self.sp = ''
    # self.eip = ''
    # self.eop = ''



PROTOSS_FACTORY = {
  'default': CombatGroupPrompt,
  'commander': CommanderPrompt,
  'developer': DeveloperPrompt,
}
TERRAN_FACTORY = {
  'default': CombatGroupPrompt,
  'commander': CommanderPrompt,
  'developer': DeveloperPrompt,
}
ZERG_FACTORY = {
  'default': CombatGroupPrompt,
  'commander': CommanderPrompt,
  'developer': DeveloperPrompt,
}

FACTORY = {
  'protoss': PROTOSS_FACTORY,
  'terran': TERRAN_FACTORY,
  'zerg': ZERG_FACTORY,
}


if __name__ == "__main__":
  from llm_pysc2.agents.configs.config import ProtossAgentConfig, TerranAgentConfig
  config = TerranAgentConfig()
  prompt = CombatGroupPrompt('CombatGroup1', log_id=0, config=config)

  print("--" * 25 + "System Prompt" + "--" * 25)
  print(prompt.sp)
  print("--" * 25 + "Example Input Prompt" + "--" * 25)
  print(prompt.eip)
  print("--" * 25 + "Example Output Prompt" + "--" * 25)
  print(prompt.eop)