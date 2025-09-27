from llm_pysc2.agents.configs.llm_pysc2 import ConfigPysc2_Harass, ConfigPysc2_Defend, ConfigPysc2_Combat, ConfigPysc2_Combat_Terran
from llm_pysc2.agents import MainAgent, LLMAgent
import os


def get_config(race,map):
  config=ConfigPysc2_Combat(race)()
  config.ENABLE_COMMUNICATION = True
  config.MAX_LLM_RUNTIME_ERROR_TIME = 600
  # 声东击西 (Make a Feint to the East While Attacking in the West) - 第6计
  # 策略：制造假象迷惑敌人，在东方佯攻，实际在西方发动真正攻击
  if map.lower() == "sdjx_te":
    for agent_name in list(config.AGENTS.keys()):
      for team in config.AGENTS[agent_name]['team']:
        if agent_name == 'CombatGroup3':
          team['task'] = [
            {'time': None, 'pos': None, 'info': "Coordinate with your team and use Make a Feint to the East While Attacking in the West to distract the enemy."},
          ]
        elif agent_name == 'CombatGroup2':
          team['task'] = [
            {'time': None, 'pos': None, 'info': "Coordinate with your team and use Make a Feint to the East While Attacking in the West to destory the enemy base."},
          ]

        
  # 暗度陈仓 (Openly repair the gallery roads, but sneak through the passage of Chencang) - 第8计
  # 策略：明修栈道，暗度陈仓。表面上做一件事，实际上暗中进行另一件事
  if map.lower() =="adcc_te":
    for agent_name in list(config.AGENTS.keys()):
      for team in config.AGENTS[agent_name]['team']:
        team['task'] = [
          {'time': None, 'pos': None, 'info': "use Openly repair the gallery roads, but sneak through the passage of Chencang to attack the enemy base at top right of the map"
                                            },
                                            #step by step instruction? 
        ]

  # 反客为主 (Make the Host and the Guest Exchange) - 第30计
  # 策略：变被动为主动，从客人变成主人，掌握主动权
  if map.lower() =="fkwz_te":
    config.AGENTS_ALWAYS_DISABLE=[
        'Airborne', 'Builder', 'Commander', 'Defender', 'CombatGroup4',
      ]
    for agent_name in list(config.AGENTS.keys()):
      for team in config.AGENTS[agent_name]['team']:
        team['task'] = [
          {'time': None, 'pos': None, 'info': "The enemy is trying to spaw in a overwhelming army at the bottom left of the map, Use Make the Host and the Guest Exchange to stop it."},
        ]

  # 调虎离山 (Lure the Tiger Out of the Mountains) - 第15计
  # 策略：引诱敌人离开有利位置，然后趁机攻击其薄弱环节
  if map.lower() =="dhls_te":
    for agent_name in list(config.AGENTS.keys()):
      for team in config.AGENTS[agent_name]['team']:
        team['task'] = [
          {'time': None, 'pos': None, 'info': "Use Lure the Tiger Out of the Mountains to get the enemy army away from the enemy base near minimap position [40, 15], then attack the enemy base"},
        ]
  # 金蝉脱壳 (Slough Off the Cicada's Shell) - 第21计
  # 策略：留下假象迷惑敌人，自己暗中撤退或转移
#need improvement
  if map.lower() =="jctq_te":
    for agent_name in list(config.AGENTS.keys()):
      for team in config.AGENTS[agent_name]['team']:
        team['task'] = [
          {'time': None, 'pos': None, 'info': "Use Slough Off the Cicada's Shell to escape"
                                            },
        ]

  # 借刀杀人 (Kill With a Borrowed Knife) - 第3计
  # 策略：利用他人之力来达到自己的目的，避免直接冲突
  if map.lower() =="jdsr_te":
    for agent_name in list(config.AGENTS.keys()):
      for team in config.AGENTS[agent_name]['team']:
        team['task'] = [
          {'time': None, 'pos': None, 'info': "Use Kill With a Borrowed Knife to defeat the enemy army"
                                            },
        ]

  # 偷梁换柱 (Replace the beams with rotten timbers) - 第25计
  # 策略：暗中调换关键部分，使敌人失去支撑，从内部瓦解
  if map.lower() =="tlhz_te":
    config.AGENTS_ALWAYS_DISABLE=[
        'Airborne', 'Commander',  'Defender', 'CombatGroup4',
      ]
    for agent_name in list(config.AGENTS.keys()):
      for team in config.AGENTS[agent_name]['team']:
        team['task'] = [
          {'time': None, 'pos': None, 'info': "Use Replace the beams with rotten timbers to destory the enemy buildings."},
        ]
  # 上屋抽梯 (Pull Down the Ladder After the Ascent) - 第28计
  # 策略：引诱敌人进入绝境，然后切断其退路，使其无法逃脱
  if map.lower() =="swct_te":
    for agent_name in list(config.AGENTS.keys()):
      for team in config.AGENTS[agent_name]['team']:
        team['task'] = [
          {'time': None, 'pos': None, 'info': "use Pull Down the Ladder After the Ascent to attack enemy base near bottom right of the map."},
        ]
  # use Pull Down the Ladder After the Ascent to attack enemy base near minimap position (37,35).
  
  # 围魏救赵 (Besiege Wei to Rescue Zhao) - 第2计
  # 策略：攻击敌人的要害，迫使其放弃当前目标，从而解救被围困的友军
  #need to remove RL units
  if map.lower() =="wwjz_te":
    for agent_name in list(config.AGENTS.keys()):
      for team in config.AGENTS[agent_name]['team']:
        team['task'] = [
          {'time': None, 'pos': None, 'info': "There is an enemy army attacking your base, Use Besiege Wei to Rescue Zhao to defeat them. The enemy base is at bottom right of the map"},
        ]

  # 无中生有 (Create something from nothing) - 第7计
  # 策略：制造假象迷惑敌人，让敌人以为有威胁，实际上可能是虚张声势
  if map.lower() =="wzsy_te":
    for agent_name in list(config.AGENTS.keys()):
      for team in config.AGENTS[agent_name]['team']:
        team['task'] = [
          {'time': None, 'pos': None, 'info': "use Create something from nothing to attack the enemy base"},
        ]


  # 欲擒故纵 (In order to capture, one must let loose) - 第16计
  # 策略：想要抓住敌人，先故意放松，让敌人放松警惕，然后突然出击
  if map.lower() =="yqgz_te":
    for agent_name in list(config.AGENTS.keys()):
      for team in config.AGENTS[agent_name]['team']:
        team['task'] = [
          {'time': None, 'pos': None, 'info': "Use In order to capture, one must let loose to defeat the enemy."
          },
        ]
    # config.AGENTS['Commander']['team'][0]['task'] = [
    #   {'time': None, 'pos': [52, 32], 'info': "Kill as much enemy workers as possible near [52, 32] while trying to avoid you adepts being detected."
    #                                       "Distract all enemy combat units by moving your warp prism to minimap position [46, 48]."},
    # ]
  # 关门捉贼 (Shut The Door to Catch the Thief) - 第22计
  # 策略：切断敌人的退路，将其困在绝境中，然后集中力量消灭
  if map.lower() =="gmzz_te":
    for agent_name in list(config.AGENTS.keys()):
      for team in config.AGENTS[agent_name]['team']:
        if agent_name == 'CombatGroup1':
          team['task'] = [
            {'time': None, 'pos': None, 'info': "Use the strategy Shut The Door to Catch the Thief to defeat the zerg army"},
             #"You are to lure the enemy to the supply depot and let them through. Do not try to block their path."},
          ]
        elif agent_name == 'CombatGroup2':
          team['task'] = [
            {'time': None, 'pos': None, 'info': "Use the strategy Shut The Door to Catch the Thief to defeat the zerg army"},
            #  "First stay where you are, if any zerglings approaches, kill them."},
          ]
        
        

  return config

map_name = "fkwz_te"
agent_race = "protoss"
enable_image_rgb = False
enable_image_feature = False
 
class MainAgentTSSPysc2(MainAgent):
  def __init__(self):
    config = get_config(agent_race, map_name) 
    # 使用config.py中的默认配置，不需要重新设置
    # model_name = 'gpt-3.5-turbo'  # 已在config.py中设置
    # api_base = 'https://api.openai.com/v1'  # 已在config.py中设置  
    # api_key = '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'  # 已在config.py中设置
    config.reset_llm(None, None, None, enable_image_rgb, enable_image_feature)
    # 添加地图和种族信息到配置中，用于日志目录命名
    config.map_name = map_name
    config.agent_race = agent_race
    super(MainAgentTSSPysc2, self).__init__(config, LLMAgent)

  def step(self, obs):
    return super().step(obs)


if __name__ == "__main__":

  if not (enable_image_rgb or enable_image_feature):
    os.system(f"python -m pysc2.bin.agent --map {map_name} --agent_race {agent_race} --parallel 1 "
              f"--agent llm_pysc2.bin.experiment_llm_36strat.MainAgentTSSPysc2 --render")
  elif enable_image_rgb:
    os.system(f"python -m pysc2.bin.agent --map {map_name} --agent_race {agent_race} --parallel 1 "
              f"--agent llm_pysc2.bin.experiment_llm_pysc2.MainAgentTSSPysc2 --render"
              f"--feature_screen_size 256 --feature_minimap_size 64 "
              f"--rgb_screen_size 256 --rgb_minimap_size 64 "
              f"--action_space RGB")
  elif enable_image_feature:  # parallel experiments with feature map obs do not available currently, set --parallel 1
    os.system(f"python -m pysc2.bin.agent --map {map_name} --agent_race {agent_race} --parallel 1 "  
              f"--agent llm_pysc2.bin.experiment_llm_pysc2.MainAgentTSSPysc2 --render"
              f"--feature_screen_size 256 --feature_minimap_size 64 "
              f"--rgb_screen_size 0 --rgb_minimap_size 0 "
              f"--render")
  else:
    print("Can not enable_image_rgb and enable_image_feature at the same time")
