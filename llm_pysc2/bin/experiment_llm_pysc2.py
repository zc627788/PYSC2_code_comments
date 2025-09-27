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

"""
LLM-PySC2 实验入口文件

功能：
1. 定义9个不同的PySC2实验任务
2. 为每个任务配置特定的智能体设置和任务目标
3. 支持文本和图像两种观察模式
4. 提供统一的实验启动接口

任务类型：
- Task 1-2: 骚扰任务（Adept/Phoenix骚扰虫族基地）
- Task 3: 防御任务（Stalker拦截空投）
- Task 4-6: 战斗任务（不同单位组合vs虫族）
- Task 7-8: 多智能体协作任务（异构智能体协作）
- Task 9: 高级骚扰任务（带通信的复杂骚扰）

作者：LLM-PySC2团队
"""

from llm_pysc2.agents.configs.llm_pysc2 import ConfigPysc2_Harass, ConfigPysc2_Defend, ConfigPysc2_Combat
from llm_pysc2.agents import MainAgent, LLMAgent
import os


def get_config(task):
  """
  根据任务编号获取对应的配置对象
  
  功能：
  - 为不同任务类型选择合适的基础配置
  - 为每个智能体团队设置具体的任务目标
  - 根据任务特点调整通信、超时等参数
  
  Args:
    task (int): 任务编号，范围1-9
    
  Returns:
    AgentConfig: 配置好的智能体配置对象
    
  Raises:
    AssertionError: 当任务编号不在有效范围内时
  """
  if task in [1, 2]:
    # Task 1-2: 骚扰任务 - 使用骚扰专用配置
    config = ConfigPysc2_Harass()
    # 为所有智能体的所有团队设置骚扰任务目标
    for agent_name in list(config.AGENTS.keys()):
      for team in config.AGENTS[agent_name]['team']:
        team['task'] = [
          # 第一阶段：移动到目标位置，避免被发现
          {'time': None, 'pos': [52, 32], 'info': "Go to minimap coordinate [52, 32], and try to avoid been detected or attacked before arrival."},
          # 第二阶段：尽可能多地击杀敌方工人
          {'time': None, 'pos': None, 'info': "Kill as much as enemy workers as possible."},
        ]
  elif task in [3]:
    # Task 3: 防御任务 - 使用防御专用配置
    config = ConfigPysc2_Defend()
    # 为CombatGroup1的所有团队设置防御任务目标
    for team in config.AGENTS['CombatGroup1']['team']:
      team['task'] = [
        # 游戏时间0:00 - 第一波空投防御
        {'time': '0:00', 'pos': None, 'info': "Protect our nexus and probes from enemy airdrops. At Game time 0:00, "
                                              "2 airdrops detected from minimap [24, 32] and [12, 24] to [16, 32]"},
        # 游戏时间0:10 - 第二波空投防御
        {'time': '0:10', 'pos': None, 'info': "Protect our nexus and probes from enemy airdrops. At Game time 0:10, "
                                              "2 airdrops detected from minimap [20, 24] and [20, 40] to [16, 32]"},
        # 游戏时间0:20 - 第三波空投防御
        {'time': '0:20', 'pos': None, 'info': "Protect our nexus and probes from enemy airdrops. At Game time 0:20, "
                                              "2 airdrops detected from minimap [24, 32] and [12, 40] to [16, 32]"},
        # 游戏时间0:30 - 第四波空投防御
        {'time': '0:30', 'pos': None, 'info': "Protect our nexus and probes from enemy airdrops. At Game time 0:30, "
                                              "2 airdrops detected from minimap [24, 32] and [10, 32] to [16, 32]"},
      ]
  elif task in [4, 5, 6]:
    # Task 4-6: 战斗任务 - 使用战斗专用配置
    config = ConfigPysc2_Combat()
    # 为所有智能体的所有团队设置战斗任务目标
    for agent_name in list(config.AGENTS.keys()):
      for team in config.AGENTS[agent_name]['team']:
        team['task'] = [
          # 第一阶段：移动到战场中心位置
          {'time': None, 'pos': [32, 32], 'info': "Go to minimap coordinate [32, 32]."},
          # 第二阶段：在游戏时间0:10后开始战斗
          {'time': '0:10', 'pos': None,
           'info': "Kill as much as enemy units as possible. If no enemy found, hold the position."},
        ]
  elif task in [7]:
    # Task 7: 多智能体协作任务 - 启用通信功能
    config = ConfigPysc2_Combat()
    # 启用智能体间通信功能
    config.ENABLE_COMMUNICATION = True
    # 设置LLM运行时错误超时时间为60秒
    config.MAX_LLM_RUNTIME_ERROR_TIME = 60
    # 启用指挥官智能体（从禁用列表中移除）
    config.AGENTS_ALWAYS_DISABLE.remove('Commander')
    # 为指挥官设置协作任务目标
    config.AGENTS['Commander']['team'][0]['task'] = [
      {'time': None, 'pos': None, 'info': "Organize frontline commanders to collaborate in defeating enemy troops, "
                                          "you should reach the goal and finish the battle before game time 1:30."},
    ]
  elif task in [8]:
    # Task 8: 多线作战任务 - 启用多个智能体协作
    config = ConfigPysc2_Combat()
    # 启用智能体间通信功能
    config.ENABLE_COMMUNICATION = True
    # 启用多个智能体：空降部队、指挥官、开发者
    config.AGENTS_ALWAYS_DISABLE.remove('Airborne')      # 启用空降部队
    config.AGENTS_ALWAYS_DISABLE.remove('Commander')     # 启用指挥官
    config.AGENTS_ALWAYS_DISABLE.remove('Developer')     # 启用开发者
    # 为指挥官设置多线作战任务目标
    config.AGENTS['Commander']['team'][0]['task'] = [
      {'time': None, 'pos': None, 'info': "Organize a multiline combat to defeat enemy troops and kill their workers, "
                                          "you should reach all the goals and finish the battle before game time 1:30."},
    ]
  elif task in [9]:
    # Task 9: 高级骚扰任务 - 带通信的复杂骚扰战术
    config = ConfigPysc2_Harass()
    # 启用智能体间通信功能
    config.ENABLE_COMMUNICATION = True
    # 设置更长的LLM运行时错误超时时间（10分钟）
    config.MAX_LLM_RUNTIME_ERROR_TIME = 600
    # 为所有智能体的所有团队设置高级骚扰任务目标
    for agent_name in list(config.AGENTS.keys()):
      for team in config.AGENTS[agent_name]['team']:
        team['task'] = [
          {'time': None, 'pos': [52, 32], 'info': "Kill as much enemy workers as possible near [52, 32] while trying to avoid you adepts being detected."
                                          "Distract all enemy combat units by moving your warp prism to minimap position [46, 48]."},
        ]
    # 注释掉的指挥官任务配置（可选）
    # config.AGENTS['Commander']['team'][0]['task'] = [
    #   {'time': None, 'pos': [52, 32], 'info': "Kill as much enemy workers as possible near [52, 32] while trying to avoid you adepts being detected."
    #                                       "Distract all enemy combat units by moving your warp prism to minimap position [46, 48]."},
    # ]
  else:
    # 任务编号不在有效范围内，抛出异常
    raise AssertionError("wrong task index")

  return config


# ==================== 实验配置参数 ====================

# 当前实验任务编号（1-9）
task = 9
# 任务难度等级（1-3）
level = 1
# 生成地图名称：pvz_task{task}_level{level}
map_name = f"pvz_task{task}_level{level}"
# 是否启用RGB图像观察模式
enable_image_rgb = False
# 是否启用特征图观察模式
enable_image_feature = False

class MainAgentLLMPysc2(MainAgent):
  """
  LLM-PySC2主智能体类
  
  功能：
  - 继承自MainAgent，负责与PySC2环境交互
  - 管理多个LLM子智能体
  - 协调观察收集、LLM查询、动作执行等流程
  
  注意：需要配置正确的LLM API信息才能运行
  """
  def __init__(self):
    # 获取任务对应的配置对象
    config = get_config(task)
    
    # LLM API配置（需要用户自行设置）
    model_name = 'YOUR-MODEL-NAME'    # 模型名称，如 'gpt-3.5-turbo'
    api_base = 'YOUR-API-BASE'        # API基础URL，如 'https://api.openai.com/v1'
    api_key = 'YOUR-API-KEY'          # API密钥
    
    # 重置LLM配置，设置模型参数和观察模式
    config.reset_llm(model_name, api_base, api_key, enable_image_rgb, enable_image_feature)
    
    # 调用父类构造函数，初始化主智能体
    super(MainAgentLLMPysc2, self).__init__(config, LLMAgent)

  def step(self, obs):
    """
    游戏步骤执行函数
    
    功能：
    - 接收游戏观察
    - 执行主智能体的决策逻辑
    - 返回游戏动作
    
    Args:
      obs: 游戏观察对象，包含当前游戏状态
    
    Returns:
      游戏动作，用于控制游戏中的单位
    """
    return super().step(obs)


if __name__ == "__main__":
  """
  主程序入口
  
  功能：
  - 根据观察模式选择不同的启动命令
  - 调用PySC2框架启动游戏环境
  - 加载LLM智能体进行游戏
  
  启动模式：
  1. 纯文本模式：只使用文本观察
  2. RGB图像模式：使用RGB图像观察
  3. 特征图模式：使用特征图观察
  """

  if not (enable_image_rgb or enable_image_feature):
    # 模式1：纯文本观察模式
    # 只使用文本描述进行观察，不使用图像
    os.system(f"python -m pysc2.bin.agent --map {map_name} --agent_race protoss --parallel 1 "
              f"--agent llm_pysc2.bin.experiment_llm_pysc2.MainAgentLLMPysc2")
              
  elif enable_image_rgb:
    # 模式2：RGB图像观察模式
    # 使用RGB图像进行观察，支持多模态LLM
    os.system(f"python -m pysc2.bin.agent --map {map_name} --agent_race protoss --parallel 1 "
              f"--agent llm_pysc2.bin.experiment_llm_pysc2.MainAgentLLMPysc2 "
              f"--feature_screen_size 256 --feature_minimap_size 64 "
              f"--rgb_screen_size 256 --rgb_minimap_size 64 "
              f"--action_space RGB")
              
  elif enable_image_feature:
    # 模式3：特征图观察模式
    # 使用特征图进行观察，启用渲染显示
    # 注意：特征图模式目前不支持并行实验，强制设置为--parallel 1
    os.system(f"python -m pysc2.bin.agent --map {map_name} --agent_race protoss --parallel 1 "  
              f"--agent llm_pysc2.bin.experiment_llm_pysc2.MainAgentLLMPysc2 "
              f"--feature_screen_size 256 --feature_minimap_size 64 "
              f"--rgb_screen_size 0 --rgb_minimap_size 0 "
              f"--render")
              
  else:
    # 错误：不能同时启用RGB和特征图模式
    print("Can not enable_image_rgb and enable_image_feature at the same time")
