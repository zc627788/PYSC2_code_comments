from llm_pysc2.agents.configs.llm_pysc2 import ConfigPysc2_Harass, ConfigPysc2_Defend, ConfigPysc2_Combat, ConfigPysc2_Combat_Terran
from llm_pysc2.agents import MainAgent, LLMAgent
import os


def get_config(race,map):
  config=ConfigPysc2_Combat(race)()
  config.ENABLE_COMMUNICATION = True
  config.MAX_LLM_RUNTIME_ERROR_TIME = 600
  print(config.__dict__)
  if map.lower() == "sdjx_te":
    for agent_name in list(config.AGENTS.keys()):
      for team in config.AGENTS[agent_name]['team']:
        if agent_name == 'CombatGroup3':
          team['task'] = [
            {'time': None, 'pos': None, 'info': "Coordinate with your team and decide which strategem to use for the ultimate goal of destorying the enemy's base."},
          ]
        elif agent_name == 'CombatGroup2':
          team['task'] = [
            {'time': None, 'pos': None, 'info': "Coordinate with your team and decide which strategem to use for the ultimate goal of destorying the enemy's base."},
          ]

        
  if map.lower() =="adcc_te":
    for agent_name in list(config.AGENTS.keys()):
      for team in config.AGENTS[agent_name]['team']:
        team['task'] = [
          {'time': None, 'pos': None, 'info': "There is an overwhelming enemy force marching your way, decide which strategem to use to attack the enemy base at top right of the map"
                                            },
                                            #step by step instruction? 
        ]

  if map.lower() =="fkwz_te":
    for agent_name in list(config.AGENTS.keys()):
      for team in config.AGENTS[agent_name]['team']:
        team['task'] = [
          {'time': None, 'pos': None, 'info': "The enemy is trying to spaw in a overwhelming army at the bottom left of the map, decide which strategem to use to stop them."},
        ]

  if map.lower() =="dhls_te":
    for agent_name in list(config.AGENTS.keys()):
      for team in config.AGENTS[agent_name]['team']:
        team['task'] = [
          {'time': None, 'pos': None, 'info': "Decide which strategem to use to attack the enemy base near minimap position [40, 15], It's guarded by an large army."},
        ]
#need improvement
  if map.lower() =="jctq_te":
    for agent_name in list(config.AGENTS.keys()):
      for team in config.AGENTS[agent_name]['team']:
        team['task'] = [
          {'time': None, 'pos': None, 'info': "decide which strategem to use to escape."
                                            },
        ]

  if map.lower() =="jdsr_te":
    for agent_name in list(config.AGENTS.keys()):
      for team in config.AGENTS[agent_name]['team']:
        team['task'] = [
          {'time': None, 'pos': None, 'info': "decude which strategem to use to defeat the enemy army."
                                            },
        ]

  if map.lower() =="tlhz_te":
    for agent_name in list(config.AGENTS.keys()):
      for team in config.AGENTS[agent_name]['team']:
        team['task'] = [
          {'time': None, 'pos': None, 'info': "Decide which strategem to use to destory the enemy buildings"},
        ]
  if map.lower() =="swct_te":
    for agent_name in list(config.AGENTS.keys()):
      for team in config.AGENTS[agent_name]['team']:
        team['task'] = [
          {'time': None, 'pos': None, 'info': "Decide which strategem to use to attack enemy base near minimap position (37,35)."},
        ]
  
  
  #need to remove RL units
  if map.lower() =="wwjz_te":
    for agent_name in list(config.AGENTS.keys()):
      for team in config.AGENTS[agent_name]['team']:
        team['task'] = [
          {'time': None, 'pos': None, 'info': "Decide which strategem to use to defeat the enemy. The enemy army is atacking your base and the unguarded enemy command center near minimap position (60,50)."},
        ]

  if map.lower() =="wzsy_te":
    for agent_name in list(config.AGENTS.keys()):
      for team in config.AGENTS[agent_name]['team']:
        team['task'] = [
          {'time': None, 'pos': None, 'info': "Decide which strategem to use to defeat the enemy and destory their base"},
        ]


  if map.lower() =="yqgz_te":
    for agent_name in list(config.AGENTS.keys()):
      for team in config.AGENTS[agent_name]['team']:
        team['task'] = [
          {'time': None, 'pos': None, 'info': "Decide which strategem to use to defeat the enemy. There are multiple seige tanks and a group of marines at the bottom left of the map"
          },
        ]
    # config.AGENTS['Commander']['team'][0]['task'] = [
    #   {'time': None, 'pos': [52, 32], 'info': "Kill as much enemy workers as possible near [52, 32] while trying to avoid you adepts being detected."
    #                                       "Distract all enemy combat units by moving your warp prism to minimap position [46, 48]."},
    # ]
  if map.lower() =="gmzz_te":
    for agent_name in list(config.AGENTS.keys()):
      for team in config.AGENTS[agent_name]['team']:
        if agent_name == 'CombatGroup1':
          team['task'] = [
            {'time': None, 'pos': None, 'info': "Coordinate with your team and decide which strategem to use to defeat the zerg army."},
             #"You are to lure the enemy to the supply depot and let them through. Do not try to block their path."},
          ]
        elif agent_name == 'CombatGroup2':
          team['task'] = [
            {'time': None, 'pos': None, 'info': "Coordinate with your team and decide which strategem to use to defeat the zerg army."},
            #  "First stay where you are, if any zerglings approaches, kill them."},
          ]
        
        

  return config

map_name = "tlhz_te"
agent_race = "zerg"
enable_image_rgb = False
enable_image_feature = False
 
class MainAgentTSSPysc2(MainAgent):
  def __init__(self):
    config = get_config(agent_race, map_name) 
    model_name = 'YOUR-MODEL-NAME'
    api_base = 'YOUR-API-BASE'
    api_key = 'YOUR-API-KEY'
    config.reset_llm(model_name, api_base, api_key, enable_image_rgb, enable_image_feature)
    super(MainAgentTSSPysc2, self).__init__(config, LLMAgent)

  def step(self, obs):
    return super().step(obs)


if __name__ == "__main__":

  if not (enable_image_rgb or enable_image_feature):
    os.system(f"python -m pysc2.bin.agent --map {map_name} --agent_race {agent_race} --parallel 1 "
              f"--agent llm_pysc2.bin.experiment_llm_36strat.MainAgentTSSPysc2")
  elif enable_image_rgb:
    os.system(f"python -m pysc2.bin.agent --map {map_name} --agent_race {agent_race} --parallel 1 "
              f"--agent llm_pysc2.bin.experiment_llm_pysc2.MainAgentTSSPysc2 "
              f"--feature_screen_size 256 --feature_minimap_size 64 "
              f"--rgb_screen_size 256 --rgb_minimap_size 64 "
              f"--action_space RGB")
  elif enable_image_feature:  # parallel experiments with feature map obs do not available currently, set --parallel 1
    os.system(f"python -m pysc2.bin.agent --map {map_name} --agent_race {agent_race} --parallel 1 "  
              f"--agent llm_pysc2.bin.experiment_llm_pysc2.MainAgentTSSPysc2 "
              f"--feature_screen_size 256 --feature_minimap_size 64 "
              f"--rgb_screen_size 0 --rgb_minimap_size 0 "
              f"--render")
  else:
    print("Can not enable_image_rgb and enable_image_feature at the same time")
