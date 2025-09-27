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

from llm_pysc2.lib.llm_action import PROTOSS_ACTION_BUILD, \
  PROTOSS_BASIC_ACTION_1, PROTOSS_BASIC_ACTION_2, PROTOSS_BASIC_ACTION_3, \
  PROTOSS_ACTION_WARPTRAIN, PROTOSS_ACTION_TRAIN, PROTOSS_ACTION_RESEARCH, \
  TERRAN_ACTION_BUILD, TERRAN_BASIC_ACTION_1, TERRAN_BASIC_ACTION_2, \
  TERRAN_BASIC_ACTION_3, TERRAN_ACTION_TRAIN, TERRAN_ACTION_RESEARCH,\
  ZERG_BASIC_ACTION_1,ZERG_BASIC_ACTION_2,ZERG_BASIC_ACTION_3,ZERG_ACTION_TRAIN,\
  ZERG_ACTION_ABILITY,ZERG_ACTION_BUILD,ZERG_ACTION_RESEARCH, F

from llm_pysc2.lib.llm_client import vision_model_names  #, video_model_names

from pysc2.lib import units
from loguru import logger
import time




def wait(second, log_id, more_info=''):
  for i in range(5):
    logger.warning(f"[ID {log_id}] Experiment will start with UNSAFE settings in {5 - i} seconds. {more_info}")
    time.sleep(1)


class AgentConfig:

  def __init__(self):

    self.race = 'zerg'

    # self.model_name = 'gemini-2.5-pro'       # 'gpt-3.5-turbo'
    # self.api_base = 'https://generativelanguage.googleapis.com'           # 'https://hk.xty.app/v1'
    # self.api_key = 'AIzaSyDy_kSOwr_GEPpPQSVZOevhYE68zyFrUcY'     # 'xxxxxxxxxxxxxxxxxxxxxxxx....'
    # self.api_key = 'AIzaSyDZhccfUwphFD89VScI_vduhHRzdGLRiwE'
    # self.model_name = 'deepseek-r1-distill-qwen-32b'
    # self.api_base = 'http://localhost:1234/v1'
    # self.api_key = 'lm-studio'        

    # self.model_name = 'deepseek-v3'
    # self.api_base = 'https://qianfan.baidubce.com/v2'
    # self.api_key = 'bce-v3/ALTAK-jgRllKOpyNeaYf3GgEcoP/ca7ac071163b8b1aaaf3fcee4ae9a77bb504dabc'  
    self.model_name = 'gpt-3.5-turbo'
    self.api_base = 'https://api.openai.com/v1'
    self.api_key = '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'
    self.temperature = 0.1

    self.basic_prompt = 'default'
    self.translator_o = 'default'
    self.translator_a = 'default'
    self.communicator = 'default'

    # 是否启用游戏初始化步骤（自动执行开局动作序列）
    self.ENABLE_INIT_STEPS = True
    
    # 是否启用自动工人管理（自动分配工人采集资源）
    self.ENABLE_AUTO_WORKER_MANAGE = True
    
    # 是否启用自动工人训练（自动训练工人单位）
    self.ENABLE_AUTO_WORKER_TRAINING = True
    
    # 是否启用智能体间通信（允许智能体交换信息）
    self.ENABLE_COMMUNICATION = True

    # 是否启用RGB图像输入（彩色图像）
    self.ENABLE_IMAGE_RGB = False
    
    # 是否启用图像特征输入（图像特征提取）
    self.ENABLE_IMAGE_FEATURE = True
    
    # 是否保存游戏图像（用于分析和调试）
    self.ENABLE_SAVE_IMAGES = True

    # LLM模拟时间（秒）- 0表示不限制
    self.LLM_SIMULATION_TIME = 0
    
    # 最大LLM查询次数（防止无限循环）
    self.MAX_LLM_QUERY_TIMES = 5
    
    # 最大LLM等待时间（秒）- 超时处理
    self.MAX_LLM_WAITING_TIME = 15
    
    # 最大LLM运行时错误时间（秒）- 错误恢复
    self.MAX_LLM_RUNTIME_ERROR_TIME = 600
    
    # 最大LLM决策频率（每秒决策次数）
    self.MAX_LLM_DECISION_FREQUENCY = 1
    
    # 最大动作数量（每步最多执行的动作数）
    self.MAX_NUM_ACTIONS = 1

    self.AGENTS = []
    self.AGENTS_ALWAYS_DISABLE = []

  def reset_llm(self, model_name=None, api_base=None, api_key=None, ENABLE_IMAGE_RGB=None, ENABLE_IMAGE_FEATURE=None):
    if model_name is not None and model_name != 'YOUR-MODEL-NAME':
      self.model_name = model_name
    if api_base is not None and api_base != 'YOUR-API-BASE':
      self.api_base = api_base
    if api_key is not None and api_key != 'YOUR-API-KEY':
      self.api_key = api_key
    if ENABLE_IMAGE_RGB is not None:
      self.ENABLE_IMAGE_RGB = ENABLE_IMAGE_RGB
    if ENABLE_IMAGE_FEATURE is not None:
      self.ENABLE_IMAGE_FEATURE = ENABLE_IMAGE_FEATURE
    if ENABLE_IMAGE_RGB is True and ENABLE_IMAGE_FEATURE is True:
      raise AssertionError("Do not support ENABLE_IMAGE_RGB and ENABLE_IMAGE_FEATURE at the same time, currently")
    for agent_name in self.AGENTS.keys():
      self.AGENTS[agent_name]['llm']['model_name'] = self.model_name
      self.AGENTS[agent_name]['llm']['api_base'] = self.api_base
      self.AGENTS[agent_name]['llm']['api_key'] = self.api_key
      if self.ENABLE_IMAGE_RGB:
        self.AGENTS[agent_name]['llm']['img_rgb'] = True
        self.AGENTS[agent_name]['llm']['img_fea'] = False
      elif self.ENABLE_IMAGE_FEATURE:
        self.AGENTS[agent_name]['llm']['img_rgb'] = False
        self.AGENTS[agent_name]['llm']['img_fea'] = True
      else:
        self.AGENTS[agent_name]['llm']['img_rgb'] = False
        self.AGENTS[agent_name]['llm']['img_fea'] = False

  def auto_check(self, log_id):
    if not isinstance(self.LLM_SIMULATION_TIME, (int, float)) or self.LLM_SIMULATION_TIME <= 0:
      error_in_llm_setting = False
      if self.model_name == '' or self.model_name == 'YOUR-MODEL-NAME':
        self.reset_llm(model_name='gpt-3.5-turbo')
        logger.error(f"[ID {log_id}] No model_name set, please specify model_name in the config.")
        self.LLM_SIMULATION_TIME = 5
        error_in_llm_setting = True
      if self.api_key == '' or self.api_key == 'YOUR-API-KEY':
        logger.error(f"[ID {log_id}] No api_key set, please specify your api_key in the config.")
        self.LLM_SIMULATION_TIME = 5
        error_in_llm_setting = True
      if self.model_name == '' or self.api_key == '':
        self.LLM_SIMULATION_TIME = 5
        error_in_llm_setting = True
      if error_in_llm_setting:
        wait(5, log_id, "(in LLM SIMULATION MODE)")

    if self.ENABLE_IMAGE_RGB or self.ENABLE_IMAGE_FEATURE:
      if self.ENABLE_IMAGE_RGB and self.ENABLE_IMAGE_FEATURE:
        logger.error(f"[ID {log_id}] can not enable config.ENABLE_IMAGE_RGB and config.ENABLE_IMAGE_FEATURE together.")
        AssertionError(f"config.ENABLE_IMAGE_RGB and config.ENABLE_IMAGE_FEATURE can not be True together")
      if self.model_name not in vision_model_names:
        logger.error(f"[ID {log_id}] config.ENABLE_IMAGE_RGB/FEATURE with large models that do not support images.")
        wait(5, log_id)
      if self.model_name in vision_model_names:
        logger.warning(f"[ID {log_id}] You are using a vision model with image obs, this may cost a lot, be cautious.")
        wait(5, log_id)
    else:
      if self.model_name in vision_model_names:
        logger.warning(f"[ID {log_id}] You are using a vision avaliable model without using any image obs.")
        wait(5, log_id)

class TerranAgentConfig(AgentConfig):
    def __init__(self):
        super(TerranAgentConfig, self).__init__()
        
        self.race = 'terran'
        self.AGENTS_ALWAYS_DISABLE = []
        self.AGENTS = {
            'CombatGroup1': {
                'describe': "Terran supply depo commander, controls raising and lowering supply depos",#infantry commander, controls Marines and Medivacs. Responsible for harass 
                'llm': {
                    'basic_prompt': self.basic_prompt,
                    'translator_o': self.translator_o,
                    'translator_a': self.translator_a,
                    'img_fea': self.ENABLE_IMAGE_FEATURE,
                    'img_rgb': self.ENABLE_IMAGE_RGB,
                    'model_name': self.model_name,
                    'api_base': self.api_base,
                    'api_key': self.api_key,
                },
                'team': [
                    # {'name': 'Marine-1', 'unit_type': [units.Terran.Marine],
                    #  'game_group': 1, 'select_type': 'group'},
                    # {'name': 'Medivac-1', 'unit_type': [units.Terran.Medivac],
                    #  'game_group': 6, 'select_type': 'group'},
                     {'name': 'SupplyDepo-1', 'unit_type': [units.Terran.SupplyDepot,units.Terran.SupplyDepotLowered],
                     'game_group': 6, 'select_type': 'group'},
                ],
                'action': {
                    # units.Terran.Marine: TERRAN_BASIC_ACTION_2,
                    # units.Terran.Medivac: TERRAN_BASIC_ACTION_3,
                    units.Terran.SupplyDepot: TERRAN_BASIC_ACTION_1 + [
                      {'name': 'Morph_SupplyDepot_Lower', 'arg': [],
                       'func': [(318, F.Morph_SupplyDepot_Lower_quick, ('queued'))]},],
                    units.Terran.SupplyDepotLowered: TERRAN_BASIC_ACTION_1 + [
                      {'name': 'Morph_SupplyDepot_Raise', 'arg': [],
                       'func': [(319, F.Morph_SupplyDepot_Raise_quick, ('queued'))]},],
                },
            },
            'CombatGroup2': {
                'describe': "infantry commander, controls Marines. Responsible for harass ",
                'llm': {
                    'basic_prompt': self.basic_prompt,
                    'translator_o': self.translator_o,
                    'translator_a': self.translator_a,
                    'img_fea': self.ENABLE_IMAGE_FEATURE,
                    'img_rgb': self.ENABLE_IMAGE_RGB,
                    'model_name': self.model_name,
                    'api_base': self.api_base,
                    'api_key': self.api_key,
                },
                'team': [
                    {'name': 'Marine-1', 'unit_type': [units.Terran.Marine],
                     'game_group': 1, 'select_type': 'group'},
                    # {'name': 'Medivac-1', 'unit_type': [units.Terran.Medivac],
                    #  'game_group': 6, 'select_type': 'group'},

                ],
                'action': {
                    units.Terran.Marine: TERRAN_BASIC_ACTION_2,
                    # units.Terran.Medivac: TERRAN_BASIC_ACTION_3,
                },
            },
            'CombatGroup3': {
                'describe': "Medivac commander, controls Medivacs. Responsible for harass ",
                'llm': {
                    'basic_prompt': self.basic_prompt,
                    'translator_o': self.translator_o,
                    'translator_a': self.translator_a,
                    'img_fea': self.ENABLE_IMAGE_FEATURE,
                    'img_rgb': self.ENABLE_IMAGE_RGB,
                    'model_name': self.model_name,
                    'api_base': self.api_base,
                    'api_key': self.api_key,
                },
                'team': [
                    # {'name': 'Marine-1', 'unit_type': [units.Terran.Marine],
                    #  'game_group': 1, 'select_type': 'group'},
                    {'name': 'Medivac-1', 'unit_type': [units.Terran.Medivac],
                     'game_group': 6, 'select_type': 'group'},

                ],
                'action': {
                    # units.Terran.Marine: TERRAN_BASIC_ACTION_2,
                    units.Terran.Medivac: TERRAN_BASIC_ACTION_3,
                },
            },
            'Commander': {
                'describe': "Terran military supreme commander. Responsible for making macro decisions through communication, "
                           "and controls OrbitalCommand for Scanner Sweep, MULE, and Extra Supplies.",
                'llm': {
                    'basic_prompt': self.basic_prompt,
                    'translator_o': 'commander',
                    'translator_a': self.translator_a,
                    'img_fea': self.ENABLE_IMAGE_FEATURE,
                    'img_rgb': self.ENABLE_IMAGE_RGB,
                    'model_name': self.model_name,
                    'api_base': self.api_base,
                    'api_key': self.api_key,
                },
                'team': [
                    {'name': 'Command-1', 'unit_type': [units.Terran.OrbitalCommand],
                     'game_group': -1, 'select_type': 'select'},
                ],
                'action': {
                    units.Terran.OrbitalCommand: TERRAN_BASIC_ACTION_1 + [
                        {'name': 'Ability_CalldownMULE_Screen', 'arg': ['screen'],
                        'func': [(183, F.Effect_CalldownMULE_screen, ('queued', 'screen'))]},
                        {'name': 'Ability_Scan_Screen', 'arg': ['screen'],
                        'func': [(227, F.Effect_Scan_screen, ('queued', 'screen'))]},
                        {'name': 'Ability_SupplyDrop_Unit', 'arg': ['tag'],
                        'func': [(239, F.Effect_SupplyDrop_screen, ('queued', 'screen_tag'))]},
                    ],
                },
            },

            'Builder': {
                'describe': "Terran builder, controls several SCVs. Responsible for building structures and repairing units",
                'llm': {
                    'basic_prompt': self.basic_prompt,
                    'translator_o': self.translator_o,
                    'translator_a': self.translator_a,
                    'img_fea': self.ENABLE_IMAGE_FEATURE,
                    'img_rgb': self.ENABLE_IMAGE_RGB,
                    'model_name': self.model_name,
                    'api_base': self.api_base,
                    'api_key': self.api_key,
                },
                'team': [
                    {'name': 'Builder-SCV-1', 'unit_type': [units.Terran.SCV],
                     'game_group': -1, 'select_type': 'select'},
                ],
                'action': {
                    units.Terran.SCV: TERRAN_BASIC_ACTION_2 + TERRAN_ACTION_BUILD + [
                        {'name': 'Ability_Repair_Unit', 'arg': ['tag'],
                        'func': [(220, F.Effect_Repair_screen, ('queued', 'screen_tag'))]},
                    ],
                },
            },

            'Developer': {
                'describe': "Terran logistics commander. Responsible for unit training and technology upgrades.",
                'llm': {
                    'basic_prompt': self.basic_prompt,
                    'translator_o': 'developer',
                    'translator_a': self.translator_a,
                    'img_fea': self.ENABLE_IMAGE_FEATURE,
                    'img_rgb': self.ENABLE_IMAGE_RGB,
                    'model_name': self.model_name,
                    'api_base': self.api_base,
                    'api_key': self.api_key,
                },
                'team': [
                    {'name': 'Empty', 'unit_type': [],
                     'game_group': -1, 'select_type': 'select'},
                ],
                'action': {
                    'EmptyGroup': TERRAN_BASIC_ACTION_1 + TERRAN_ACTION_RESEARCH + TERRAN_ACTION_TRAIN,
                },
            },

            'InfantryCommander': {
                'describe': "Terran infantry commander, controls Marines and Marauders. Responsible for early game defense "
                           "and mid-game bio compositions.",
                'llm': {
                    'basic_prompt': self.basic_prompt,
                    'translator_o': self.translator_o,
                    'translator_a': self.translator_a,
                    'img_fea': self.ENABLE_IMAGE_FEATURE,
                    'img_rgb': self.ENABLE_IMAGE_RGB,
                    'model_name': self.model_name,
                    'api_base': self.api_base,
                    'api_key': self.api_key,
                },
                'team': [
                    {'name': 'Marine-1', 'unit_type': [units.Terran.Marine],
                     'game_group': 1, 'select_type': 'group'},
                    {'name': 'Marauder-1', 'unit_type': [units.Terran.Marauder],
                     'game_group': 2, 'select_type': 'group'},
                ],
                'action': {
                    units.Terran.Marine: TERRAN_BASIC_ACTION_2 + [
                        {'name': 'Ability_Stim', 'arg': [],
                       'func': [(234, F.Effect_Stim_quick, ('queued'))]},
                    ],
                    units.Terran.Marauder: TERRAN_BASIC_ACTION_2 + [
                        {'name': 'Ability_Stim', 'arg': [],
                        'func': [(234, F.Effect_Stim_quick, ('queued'))]},
                    ],
                },
            },

            'MechCommander': {
                'describe': "Terran mechanized force commander, controls Tanks, Thors, Cyclones and Hellions. "
                           "Responsible for main ground combat operations.",
                'llm': {
                    'basic_prompt': self.basic_prompt,
                    'translator_o': self.translator_o,
                    'translator_a': self.translator_a,
                    'img_fea': self.ENABLE_IMAGE_FEATURE,
                    'img_rgb': self.ENABLE_IMAGE_RGB,
                    'model_name': self.model_name,
                    'api_base': self.api_base,
                    'api_key': self.api_key,
                },
                'team': [
                    {'name': 'Tank-1', 'unit_type': [units.Terran.SiegeTank, units.Terran.SiegeTankSieged],
                     'game_group': 3, 'select_type': 'group'},
                    {'name': 'Thor-1', 'unit_type': [units.Terran.Thor,units.Terran.ThorHighImpactMode],
                     'game_group': 4, 'select_type': 'group'},
                    {'name': 'Hellion-1', 'unit_type': [units.Terran.Hellion, units.Terran.Hellbat],
                     'game_group': 5, 'select_type': 'group'},
                    {'name': 'Cyclone-1', 'unit_type': [units.Terran.Cyclone],
                     'game_group': 5, 'select_type': 'group'},
                ],
                'action': {
                    units.Terran.SiegeTank: TERRAN_BASIC_ACTION_2 + [
                        {'name': 'Morph_SiegeMode', 'arg': [],
                         'func': [(317, F.Morph_SiegeMode_quick, ('queued'))]},
                    ],
                    units.Terran.SiegeTankSieged: TERRAN_BASIC_ACTION_1 + [
                        {'name': 'Morph_Unsiege', 'arg': [],
                         'func': [(322, F.Morph_Unsiege_quick, ('queued'))]},
                    ],
                    units.Terran.Thor: TERRAN_BASIC_ACTION_2,
                    units.Terran.Hellion: TERRAN_BASIC_ACTION_2 + [
                        {'name': 'Morph_Hellbat', 'arg': [],
                         'func': [(300, F.Morph_Hellbat_quick, ('queued'))]},
                    ],
                    units.Terran.Hellbat: TERRAN_BASIC_ACTION_2 + [
                        {'name': 'Morph_Hellion', 'arg': [],
                         'func': [(301, F.Morph_Hellion_quick, ('queued'))]},
                    ],
                },
            },

            'AirCommander': {
                'describe': "Terran air force commander, controls Medivacs, Vikings, Liberators and Battlecruisers. "
                           "Responsible for air superiority and drop operations.",
                'llm': {
                    'basic_prompt': self.basic_prompt,
                    'translator_o': self.translator_o,
                    'translator_a': self.translator_a,
                    'img_fea': self.ENABLE_IMAGE_FEATURE,
                    'img_rgb': self.ENABLE_IMAGE_RGB,
                    'model_name': self.model_name,
                    'api_base': self.api_base,
                    'api_key': self.api_key,
                },
                'team': [
                    {'name': 'Medivac-1', 'unit_type': [units.Terran.Medivac],
                     'game_group': 6, 'select_type': 'group'},
                    {'name': 'Viking-1', 'unit_type': [units.Terran.VikingFighter, units.Terran.VikingAssault],
                     'game_group': 7, 'select_type': 'group'},
                    {'name': 'Battlecruiser-1', 'unit_type': [units.Terran.Battlecruiser],
                     'game_group': 8, 'select_type': 'group'},
                ],
                'action': {
                    units.Terran.Medivac: TERRAN_BASIC_ACTION_3 + [
                        {'name': 'Load_Unit', 'arg': ['tag'],
                         'func': [(287, F.Load_screen, ('queued', 'screen_tag'))]},
                        {'name': 'Unload_Screen', 'arg': ['screen'],
                         'func': [(516, F.UnloadAllAt_screen, ('queued', 'screen'))]},
                    ],
                    units.Terran.VikingFighter: TERRAN_BASIC_ACTION_2 + [
                        {'name': 'Morph_VikingAssaultMode', 'arg': [],
                         'func': [(326, F.Morph_VikingAssaultMode_quick, ('queued'))]},
                    ],
                    units.Terran.VikingAssault: TERRAN_BASIC_ACTION_2 + [
                        {'name': 'Morph_VikingFighterMode', 'arg': [],
                         'func': [(327, F.Morph_VikingFighterMode_quick, ('queued'))]},
                    ],
                    units.Terran.Battlecruiser: TERRAN_BASIC_ACTION_2 + [
                        {'name': 'Effect_TacticalJump_Screen', 'arg': ['screen'],
                         'func': [(240, F.Effect_TacticalJump_screen, ('queued', 'screen'))]},
                        {'name': 'Effect_YamatoGun_Unit', 'arg': ['tag'],
                         'func': [(247, F.Effect_YamatoGun_screen, ('queued', 'screen_tag'))]},
                    ],
                },
            },

            'SpecialOps': {
                'describe': "Terran special operations commander, controls Ghosts, Reapers and Ravens. "
                           "Responsible for infiltration, nuclear strikes, and harassment.",
                'llm': {
                    'basic_prompt': self.basic_prompt,
                    'translator_o': self.translator_o,
                    'translator_a': self.translator_a,
                    'img_fea': self.ENABLE_IMAGE_FEATURE,
                    'img_rgb': self.ENABLE_IMAGE_RGB,
                    'model_name': self.model_name,
                    'api_base': self.api_base,
                    'api_key': self.api_key,
                },
                'team': [
                    {'name': 'Ghost-1', 'unit_type': [units.Terran.Ghost],
                     'game_group': 9, 'select_type': 'group'},
                    {'name': 'Reaper-1', 'unit_type': [units.Terran.Reaper],
                     'game_group': 10, 'select_type': 'group'},
                    {'name': 'Raven-1', 'unit_type': [units.Terran.Raven],
                     'game_group': 11, 'select_type': 'group'},
                ],
                'action': {
                    units.Terran.Ghost: TERRAN_BASIC_ACTION_2 + [
                        {'name': 'Effect_Cloak', 'arg': [],
                         'func': [(172, F.Behavior_CloakOn_quick, ('queued'))]},
                        {'name': 'Effect_Decloak', 'arg': [],
                         'func': [(169, F.Behavior_CloakOff_quick, ('queued'))]},
                        {'name': 'Effect_EMP_Screen', 'arg': ['screen'],
                         'func': [(190, F.Effect_EMP_screen, ('queued', 'screen'))]},
                        {'name': 'Effect_Snipe_Unit', 'arg': ['tag'],
                         'func': [(195, F.Effect_GhostSnipe_screen, ('queued', 'screen_tag'))]},
                    ],
                    units.Terran.Reaper: TERRAN_BASIC_ACTION_2,
                    units.Terran.Raven: TERRAN_BASIC_ACTION_3 + [
                        {'name': 'Effect_AutoTurret_Screen', 'arg': ['screen'],
                         'func': [(178, F.Effect_AutoTurret_screen, ('queued', 'screen'))]},
                        {'name': 'Effect_AntiArmorMissile_Unit', 'arg': ['tag'],
                         'func': [(526, F.Effect_AntiArmorMissile_screen, ('queued', 'screen_tag'))]},
                    ],
                },
            },
            'CombatGroup10': {
                'describe': "Terran reaper commander, controls Reapers for harassment and scouting. "
                           "Responsible for early game harassment, worker harassment, and map control.",
                'llm': {
                    'basic_prompt': self.basic_prompt,
                    'translator_o': self.translator_o,
                    'translator_a': self.translator_a,
                    'img_fea': self.ENABLE_IMAGE_FEATURE,
                    'img_rgb': self.ENABLE_IMAGE_RGB,
                    'model_name': self.model_name,
                    'api_base': self.api_base,
                    'api_key': self.api_key,
                },
                'team': [
                    {'name': 'Reaper-1', 'unit_type': [units.Terran.Reaper],
                     'game_group': -1, 'select_type': 'select_all_type'},
                ],
                'action': {
                    units.Terran.Reaper: TERRAN_BASIC_ACTION_2 + [
                        {'name': 'Effect_KD8Charge_Screen', 'arg': ['screen'],
                         'func': [(255, F.Effect_KD8Charge_screen, ('queued', 'screen'))]},
                    ],
                },
            },
        }

class ProtossAgentConfig(AgentConfig):

  def __init__(self):
    super(ProtossAgentConfig, self).__init__()

    # Program control parameters in class AgentConfig (above)

    # 始终禁用的智能体列表（用于调试或特定场景）
    self.AGENTS_ALWAYS_DISABLE = []
    
    # 多智能体系统配置 - 定义所有参与游戏的智能体
    # 每个智能体包含：描述、LLM配置、团队配置、动作配置
    self.AGENTS = {
      # 智能体1：空降指挥官 - 负责空降作战和快速增援
      'Airborne': {
        # 智能体描述：为LLM提供角色定位和职责说明
        'describe': "Protoss airborne commander, controls units airborne/warptrain from WarpPrism. "
                    "Responsible for quick reinforcing nearby units or executing multiline combat.",
        
        # LLM配置：定义智能体与LLM的交互参数
        'llm': {
          'basic_prompt': self.basic_prompt,        # 基础提示词模板
          'translator_o': self.translator_o,        # 观察转换器（游戏状态→文本）
          'translator_a': self.translator_a,        # 动作转换器（文本→游戏动作）
          'img_fea': self.ENABLE_IMAGE_FEATURE,     # 是否启用图像特征
          'img_rgb': self.ENABLE_IMAGE_RGB,         # 是否启用RGB图像
          'model_name': self.model_name,             # LLM模型名称
          'api_base': self.api_base,                 # API基础URL
          'api_key': self.api_key,                   # API密钥
        },
        
        # 团队配置：定义智能体控制的游戏单位
        'team': [
          {'name': 'Airborne-Zealot-1',              # 单位名称
           'unit_type': [units.Protoss.Zealot],      # 单位类型（追猎者）
           'game_group': -1,                         # 游戏分组（-1表示未分组）
           'select_type': 'select_all_type'},        # 选择类型（选择所有同类型单位）
        ],
        
        # 动作配置：定义智能体可以执行的动作
        'action': {
          units.Protoss.Zealot: PROTOSS_BASIC_ACTION_2,  # 追猎者的基础动作集合
        },
      },

      # 智能体2：建造者 - 负责建筑建造和资源管理
      'Builder': {
        # 智能体描述：建造者的职责说明
        'describe': "Protoss builder, controls several Probe. Responsible for build buildings",
        
        # LLM配置：与其他智能体相同的LLM参数
        'llm': {
          'basic_prompt': self.basic_prompt,
          'translator_o': self.translator_o,
          'translator_a': self.translator_a,
          'img_fea': self.ENABLE_IMAGE_FEATURE,
          'img_rgb': self.ENABLE_IMAGE_RGB,
          'model_name': self.model_name,
          'api_base': self.api_base,
          'api_key': self.api_key,
        },
        
        # 团队配置：控制探机进行建造
        'team': [
          {'name': 'Builder-Probe-1',                  # 建造者探机
           'unit_type': [units.Protoss.Probe],         # 单位类型（探机）
           'game_group': -1,                           # 游戏分组
           'select_type': 'select'},                   # 选择类型（单个选择）
        ],
        
        # 动作配置：探机的基础动作+建造动作
        'action': {
          units.Protoss.Probe: PROTOSS_BASIC_ACTION_2 + PROTOSS_ACTION_BUILD,  # 基础动作+建造动作
        },
      },

      # 智能体3：军事指挥官 - 负责宏观决策和战术指挥
      'Commander': {
        # 智能体描述：指挥官的职责和决策范围
        'describe': "Protoss military supreme commander. "
                    "Responsible for making macro decision through communication, and controls nexus for massrecall "
                    "for tactical objectives. When make deployment, describe the time, location, and objectives of the "
                    "mission as clearly as possible",
        
        # LLM配置：使用专门的指挥官观察转换器
        'llm': {
          'basic_prompt': self.basic_prompt,
          'translator_o': 'commander',               # 使用指挥官专用的观察转换器
          'translator_a': self.translator_a,
          'img_fea': self.ENABLE_IMAGE_FEATURE,
          'img_rgb': self.ENABLE_IMAGE_RGB,
          'model_name': self.model_name,
          'api_base': self.api_base,
          'api_key': self.api_key,
        },
        
        # 团队配置：指挥官不直接控制单位，但可以访问所有信息
        'team': [
          {'name': 'Empty',                           # 空团队（不控制具体单位）
           'unit_type': [],                          # 无单位类型
           'game_group': -1,                         # 游戏分组
           'select_type': 'select'},                 # 选择类型
        ],
        
        # 动作配置：指挥官不执行具体动作，主要通过通信协调
        'action': {
          'EmptyGroup': [],                           # 空动作组
        },
      },

      # 智能体4：后勤指挥官 - 负责单位训练、科技升级和建造指令
      'Developer': {
        # 智能体描述：后勤指挥官的职责范围
        'describe': "Protoss logistics commander. "
                    "Responsible for unit trainning, unit warp trainning, technology upgrade and order the Builder "
                    "to build.",
        
        # LLM配置：使用专门的后勤观察转换器
        'llm': {
          'basic_prompt': self.basic_prompt,
          'translator_o': 'developer',                # 使用后勤专用的观察转换器
          'translator_a': self.translator_a,
          'img_fea': self.ENABLE_IMAGE_FEATURE,
          'img_rgb': self.ENABLE_IMAGE_RGB,
          'model_name': self.model_name,
          'api_base': self.api_base,
          'api_key': self.api_key,
        },
        
        # 团队配置：控制折跃门进行单位训练
        'team': [
          {'name': 'WarpGate-1',                       # 折跃门
           'unit_type': [units.Protoss.WarpGate],      # 单位类型（折跃门）
           'game_group': -1,                           # 游戏分组
           'select_type': 'select_all_type'},          # 选择类型（选择所有折跃门）
          {'name': 'Empty',                            # 空团队（用于其他操作）
           'unit_type': [],                            # 无单位类型
           'game_group': -1,                           # 游戏分组
           'select_type': 'select'},                   # 选择类型
        ],
        
        # 动作配置：折跃门训练动作+其他后勤动作
        'action': {
          units.Protoss.WarpGate: PROTOSS_ACTION_WARPTRAIN,  # 折跃门训练动作
          'EmptyGroup': PROTOSS_BASIC_ACTION_1 + PROTOSS_ACTION_RESEARCH + PROTOSS_ACTION_TRAIN + [
            # 停止建造单位动作（用于取消训练）
            {'name': 'Stop_Building_Unit', 'arg': ['tag'],
             'func': [(573, F.llm_pysc2_move_camera, ('world_tag')),      # 移动摄像头到目标位置
                      (3, F.select_rect, ('select', 'screen1_tag', 'screen2_tag')),  # 选择区域
                      (454, F.Stop_Building_quick, ('queued'))]}          # 停止建造
          ],
        },
      },

      # 智能体5：防御指挥官 - 负责基地防御和拦截敌军
      'Defender': {
        # 智能体描述：防御指挥官的职责
        'describe': "Protoss garrison troops commander, controls several Stalkers. "
                    "Responsible for intercepting enemy infiltrating forces.",
        
        # LLM配置：使用标准配置
        'llm': {
          'basic_prompt': self.basic_prompt,
          'translator_o': self.translator_o,
          'translator_a': self.translator_a,
          'img_fea': self.ENABLE_IMAGE_FEATURE,
          'img_rgb': self.ENABLE_IMAGE_RGB,
          'model_name': self.model_name,
          'api_base': self.api_base,
          'api_key': self.api_key,
        },
        
        # 团队配置：控制追猎者进行防御(有什么兵种）
        'team': [
          {'name': 'Stalker-1',                         # 防御追猎者
           'unit_type': [units.Protoss.Stalker],        # 单位类型（追猎者）
           'game_group': 1,                             # 游戏分组（分组1）
           'select_type': 'group'},                     # 选择类型（按分组选择）
        ],
        
        # 动作配置：追猎者的基础动作+闪现技能(有什么兵种）
        'action': {
          units.Protoss.Stalker: PROTOSS_BASIC_ACTION_2 + [
            # 闪现技能动作
            {'name': 'Ability_Blink_Screen', 'arg': ['screen'],
             'func': [(180, F.Effect_Blink_screen, ('queued', 'screen'))]},  # 闪现到屏幕位置
            {'name': 'Select_Unit_Blink_Screen', 'arg': ['tag', 'screen'],
             'func': [(3, F.select_rect, ('select', 'screen1_tag', 'screen2_tag')),  # 选择单位
                      (180, F.Effect_Blink_screen, ('now', 'screen'))]}              # 立即闪现
          ]
        },
      },

      # 智能体6：战斗组0 - 前线指挥官（狂战士）
      'CombatGroup0': {
        # 智能体描述：前线指挥官的职责
        'describe': "Protoss frontline commander, controls several Zealots. "
                    "Responsible for providing cover for the main force and executing multi line combat.",
        
        # LLM配置：使用标准配置
        'llm': {
          'basic_prompt': self.basic_prompt,
          'translator_o': self.translator_o,
          'translator_a': self.translator_a,
          'img_fea': self.ENABLE_IMAGE_FEATURE,
          'img_rgb': self.ENABLE_IMAGE_RGB,
          'model_name': self.model_name,
          'api_base': self.api_base,
          'api_key': self.api_key,
        },
        
        # 团队配置：控制多个狂战士小组
        'team': [
          {'name': 'Zealot-1',                         # 狂战士小组1
           'unit_type': [units.Protoss.Zealot],        # 单位类型（狂战士）
           'game_group': 2,                            # 游戏分组（分组2）
           'select_type': 'group'},                    # 选择类型（按分组选择）
          {'name': 'Zealot-2',                         # 狂战士小组2
           'unit_type': [units.Protoss.Zealot],        # 单位类型（狂战士）
           'game_group': 3,                            # 游戏分组（分组3）
           'select_type': 'group'},                    # 选择类型（按分组选择）
        ],
        
        # 动作配置：狂战士的基础动作
        'action': {
          units.Protoss.Zealot: PROTOSS_BASIC_ACTION_2,  # 狂战士的基础动作集合
        },
      },

      # 智能体7：战斗组1 - 前线指挥官（追猎者）
      'CombatGroup1': {
        # 智能体描述：前线指挥官的职责
        'describe': "Protoss frontline commander, controls several Stalkers. "
                    "Responsible for providing cover for the main force and restraining enemy forces.",
        
        # LLM配置：使用标准配置
        'llm': {
          'basic_prompt': self.basic_prompt,
          'translator_o': self.translator_o,
          'translator_a': self.translator_a,
          'img_fea': self.ENABLE_IMAGE_FEATURE,
          'img_rgb': self.ENABLE_IMAGE_RGB,
          'model_name': self.model_name,
          'api_base': self.api_base,
          'api_key': self.api_key,
        },
        
        # 团队配置：控制多个追猎者小组
        'team': [
          {'name': 'Stalker-1',                         # 追猎者小组1
           'unit_type': [units.Protoss.Stalker],        # 单位类型（追猎者）
           'game_group': 4,                             # 游戏分组（分组4）
           'select_type': 'group'},                     # 选择类型（按分组选择）
          {'name': 'Stalker-2',                         # 追猎者小组2
           'unit_type': [units.Protoss.Stalker],        # 单位类型（追猎者）
           'game_group': 5,                             # 游戏分组（分组5）
           'select_type': 'group'},                     # 选择类型（按分组选择）
          {'name': 'Stalker-3',                         # 追猎者小组3
           'unit_type': [units.Protoss.Stalker],        # 单位类型（追猎者）
           'game_group': 6,                             # 游戏分组（分组6）
           'select_type': 'group'},                     # 选择类型（按分组选择）
        ],
        
        # 动作配置：追猎者的基础动作+闪现技能
        'action': {
          units.Protoss.Stalker: PROTOSS_BASIC_ACTION_2 + [
            # 闪现技能动作
            {'name': 'Ability_Blink_Screen', 'arg': ['screen'],
             'func': [(180, F.Effect_Blink_screen, ('queued', 'screen'))]},  # 闪现到屏幕位置
            {'name': 'Select_Unit_Blink_Screen', 'arg': ['tag', 'screen'],
             'func': [(3, F.select_rect, ('select', 'screen1_tag', 'screen2_tag')),  # 选择单位
                      (180, F.Effect_Blink_screen, ('now', 'screen'))]}              # 立即闪现
          ]
        },
      },

      # 智能体8：战斗组2 - 地面主力指挥官（不朽者、巨像、执政官）
      'CombatGroup2': {
        # 智能体描述：地面主力指挥官的职责
        'describe': "Protoss frontline commander, controls ground main force such as Immortal, Colossus and Archon. "
                    "Responsible for frontal combat.",
        'llm': {
          'basic_prompt': self.basic_prompt,
          'translator_o': self.translator_o,
          'translator_a': self.translator_a,
          'img_fea': self.ENABLE_IMAGE_FEATURE,
          'img_rgb': self.ENABLE_IMAGE_RGB,
          'model_name': self.model_name,
          'api_base': self.api_base,
          'api_key': self.api_key,
        },
        'team': [
          {'name': 'Immortal-1', 'unit_type': [units.Protoss.Immortal],
           'game_group': -1, 'select_type': 'select_all_type'},
          # {'name': 'Immortal-2', 'unit_type': [units.Protoss.Immortal],
          #  'game_group': -1, 'select_type': 'select_all_type'},  # more than 1 select_all_type not currently supported
          {'name': 'Colossus-1', 'unit_type': [units.Protoss.Colossus],
           'game_group': -1, 'select_type': 'select_all_type'},
          # {'name': 'Colossus-2', 'unit_type': [units.Protoss.Colossus],
          #  'game_group': -1, 'select_type': 'select_all_type'},  # more than 1 select_all_type not currently supported
          {'name': 'Archon-1', 'unit_type': [units.Protoss.Archon],
           'game_group': -1, 'select_type': 'select_all_type'},
          # {'name': 'Archon-2', 'unit_type': [units.Protoss.Archon],
          #  'game_group': -1, 'select_type': 'select_all_type'},  # more than 1 select_all_type not currently supported
        ],
        'action': {
          units.Protoss.Immortal: PROTOSS_BASIC_ACTION_2,
          units.Protoss.Colossus: PROTOSS_BASIC_ACTION_2,
          units.Protoss.Archon: PROTOSS_BASIC_ACTION_2,
        },
      },

      # 智能体9：战斗组3 - 空中主力指挥官（虚空辉光舰、航母、风暴战舰）
      'CombatGroup3': {
        # 智能体描述：空中主力指挥官的职责
        'describe': "Protoss frontline commander, controls air main force such as VoidRay, Carrier and Tempest. "
                    "Responsible for frontal combat.",
        'llm': {
          'basic_prompt': self.basic_prompt,
          'translator_o': self.translator_o,
          'translator_a': self.translator_a,
          'img_fea': self.ENABLE_IMAGE_FEATURE,
          'img_rgb': self.ENABLE_IMAGE_RGB,
          'model_name': self.model_name,
          'api_base': self.api_base,
          'api_key': self.api_key,
        },
        'team': [
          {'name': 'VoidRay-1', 'unit_type': [units.Protoss.VoidRay],
           'game_group': -1, 'select_type': 'select_all_type'},
          # {'name': 'VoidRay-2', 'unit_type': [units.Protoss.VoidRay],
          #  'game_group': -1, 'select_type': 'select_all_type'},  # more than 1 select_all_type not currently supported
          {'name': 'Carrier-1', 'unit_type': [units.Protoss.Carrier],
           'game_group': -1, 'select_type': 'select_all_type'},
          # {'name': 'Carrier-2', 'unit_type': [units.Protoss.Carrier],
          #  'game_group': -1, 'select_type': 'select_all_type'},  # more than 1 select_all_type not currently supported
          {'name': 'Tempest-1', 'unit_type': [units.Protoss.Tempest],
           'game_group': -1, 'select_type': 'select_all_type'},
          # {'name': 'Tempest-2', 'unit_type': [units.Protoss.Tempest],
          #  'game_group': -1, 'select_type': 'select_all_type'},  # more than 1 select_all_type not currently supported
        ],
        'action': {
          units.Protoss.Carrier: PROTOSS_BASIC_ACTION_2,
          units.Protoss.Tempest: PROTOSS_BASIC_ACTION_2,
          units.Protoss.VoidRay: PROTOSS_BASIC_ACTION_2 + [
            {'name': 'Ability_PrismaticAlignment', 'arg': [],
             'func': [(244, F.Effect_VoidRayPrismaticAlignment_quick, ('queued'))]},
          ],
        },
      },

      # 智能体10：战斗组4 - 侦察指挥官（探机、观察者）
      'CombatGroup4': {
        # 智能体描述：侦察指挥官的职责
        'describe': "Protoss reconnaissance commander, controls Observer and several Probe. "
                    "Responsible for providing reconnaissance infomation and detect cloak unit for main force",
        'llm': {
          'basic_prompt': self.basic_prompt,
          'translator_o': self.translator_o,
          'translator_a': self.translator_a,
          'img_fea': self.ENABLE_IMAGE_FEATURE,
          'img_rgb': self.ENABLE_IMAGE_RGB,
          'model_name': self.model_name,
          'api_base': self.api_base,
          'api_key': self.api_key,
        },
        'team': [
          {'name': 'Probe', 'unit_type': [units.Protoss.Probe],
           'game_group': -1, 'select_type': 'select'},
          {'name': 'Observer', 'unit_type': [units.Protoss.Observer, units.Protoss.ObserverSurveillanceMode],
           'game_group': -1, 'select_type': 'select'},
        ],
        'action': {
          units.Protoss.Probe: PROTOSS_BASIC_ACTION_2 + [
            {'name': 'Lock_Nexus_Near', 'arg': ['tag'],
             'func': [(70, F.Build_Pylon_screen, ('queued', 'screen_tag'))]},
            {'name': 'Lock_Assimilator_Near', 'arg': ['tag'],
             'func': [(40, F.Build_Assimilator_screen, ('queued', 'screen_tag'))]},
          ],
          units.Protoss.Observer: PROTOSS_BASIC_ACTION_3 + [
            {'name': 'Morph_SurveillanceMode', 'arg': [],
             'func': [(538, F.Morph_SurveillanceMode_quick, ('queued'))]},
          ],
          units.Protoss.ObserverSurveillanceMode: [
            {'name': 'Continuously_Monitor_Here', 'arg': [],
             'func': [(0, F.no_op, ())]},
            {'name': 'Morph_ObserverMode', 'arg': [],
             'func': [(535, F.Morph_ObserverMode_quick, ('queued'))]},
          ],
        },
      },

      # 智能体11：战斗组5 - AOE伤害指挥官（高阶圣堂武士、干扰者）
      'CombatGroup5': {
        # 智能体描述：AOE伤害指挥官的职责
        'describe': "Protoss AOE commander, controls HighTemplar and Disruptor. "
                    "Responsible for dealing high damage to clustered enemies",
        'llm': {
          'basic_prompt': self.basic_prompt,
          'translator_o': self.translator_o,
          'translator_a': self.translator_a,
          'img_fea': self.ENABLE_IMAGE_FEATURE,
          'img_rgb': self.ENABLE_IMAGE_RGB,
          'model_name': self.model_name,
          'api_base': self.api_base,
          'api_key': self.api_key,
        },
        'team': [
          {'name': 'HighTemplar-1', 'unit_type': [units.Protoss.HighTemplar],
           'game_group': 7, 'select_type': 'group'},
          {'name': 'Disruptor-1', 'unit_type': [units.Protoss.Disruptor],
           'game_group': 8, 'select_type': 'group'},
        ],
        'action': {
          units.Protoss.HighTemplar: PROTOSS_BASIC_ACTION_2 + [
            {'name': 'Ability_PsiStorm_Screen', 'arg': ['screen'],
             'func': [(218, F.Effect_PsiStorm_screen, ('queued', 'screen'))]},
            {'name': 'Ability_PsiStorm_Attack_Unit', 'arg': ['tag'],
             'func': [(218, F.Effect_PsiStorm_screen, ('queued', 'screen_tag'))]},
            {'name': 'Morph_Archon', 'arg': [],
             'func': [(296, F.Morph_Archon_quick, ('queued'))]},
            {'name': 'Select_Two_Unit_Morph_Archon', 'arg': ['tag', 'tag'],
             'func': [(3, F.select_rect, ('select', 'screen1_tag', 'screen2_tag')),
                      (3, F.select_rect, ('add', 'screen1_tag2', 'screen2_tag2')),
                      (296, F.Morph_Archon_quick, ('queued'))]},
          ],
          units.Protoss.Disruptor: PROTOSS_BASIC_ACTION_3 + [
            {'name': 'Ability_PurificationNova_Attack_Unit', 'arg': ['tag'],
             'func': [(219, F.Effect_PurificationNova_screen, ('queued', 'screen_tag'))]},
          ],
          # units.Protoss.DisruptorPhased: PROTOSS_BASIC_ACTION_2,
        },
      },

      # 智能体12：战斗组6 - 战术支援指挥官（哨兵、母舰、折跃棱镜）
      'CombatGroup6': {
        # 智能体描述：战术支援指挥官的职责
        'describe': "Protoss tactical support commander, controls Sentry and Mothership. "
                      "Responsible for providing tactical support by using skills",
        'llm': {
          'basic_prompt': self.basic_prompt,
          'translator_o': self.translator_o,
          'translator_a': self.translator_a,
          'img_fea': self.ENABLE_IMAGE_FEATURE,
          'img_rgb': self.ENABLE_IMAGE_RGB,
          'model_name': self.model_name,
          'api_base': self.api_base,
          'api_key': self.api_key,
        },
        'team': [
          {'name': 'Sentry-1', 'unit_type': [units.Protoss.Sentry],
           'game_group': 9, 'select_type': 'group'},
          {'name': 'Mothership', 'unit_type': [units.Protoss.Mothership],
           'game_group': -1, 'select_type': 'select'},
          {'name': 'WarpPrism', 'unit_type': [units.Protoss.WarpPrism, units.Protoss.WarpPrismPhasing],
           'game_group': -1, 'select_type': 'select'},
        ],
        'action': {
          units.Protoss.Sentry: PROTOSS_BASIC_ACTION_2 + [
            {'name': 'Ability_ForceField_Screen', 'arg': ['screen'],
             'func': [(193, F.Effect_ForceField_screen, ('queued', 'screen'))]},
            {'name': 'Ability_GuardianShield', 'arg': [],
             'func': [(197, F.Effect_GuardianShield_quick, ('queued'))]},
            # # Hallucination not supported in pysc2
            # {'name': 'Hallucination_Adept',             'arg': [],
            #  'func': [(248, F.Hallucination_Adept_quick, ('queued'))]},
            # {'name': 'Hallucination_Archon',            'arg': [],
            #  'func': [(249, F.Hallucination_Archon_quick, ('queued'))]},
            # {'name': 'Hallucination_Colossus',          'arg': [],
            #  'func': [(250, F.Hallucination_Colossus_quick, ('queued'))]},
            # {'name': 'Hallucination_Disruptor',         'arg': [],
            #  'func': [(251, F.Hallucination_Disruptor_quick, ('queued'))]},
            # {'name': 'Hallucination_HighTemplar',       'arg': [],
            #  'func': [(252, F.Hallucination_HighTemplar_quick, ('queued'))]},
            # {'name': 'Hallucination_Immortal',          'arg': [],
            #  'func': [(253, F.Hallucination_Immortal_quick, ('queued'))]},
            # {'name': 'Hallucination_Oracle',            'arg': [],
            #  'func': [(254, F.Hallucination_Oracle_quick, ('queued'))]},
            # {'name': 'Hallucination_Phoenix',           'arg': [],
            #  'func': [(255, F.Hallucination_Phoenix_quick, ('queued'))]},
            # {'name': 'Hallucination_Probe',             'arg': [],
            #  'func': [(256, F.Hallucination_Probe_quick, ('queued'))]},
            # {'name': 'Hallucination_Stalker',           'arg': [],
            #  'func': [(257, F.Hallucination_Stalker_quick, ('queued'))]},
            # {'name': 'Hallucination_VoidRay',           'arg': [],
            #  'func': [(258, F.Hallucination_VoidRay_quick, ('queued'))]},
            # {'name': 'Hallucination_WarpPrism',         'arg': [],
            #  'func': [(259, F.Hallucination_WarpPrism_quick, ('queued'))]},
            # {'name': 'Hallucination_Zealot',            'arg': [],
            #  'func': [(260, F.Hallucination_Zealot_quick, ('queued'))]},
          ],
          units.Protoss.Mothership: PROTOSS_BASIC_ACTION_3 + [
            # Ability_CloakingField not supported in pysc2
            # Ability_MothershipMassRecall not neccessary in simple combat tasks
            # {'name': 'Ability_MothershipMassRecall_Near', 'arg': ['tag'],
            #  'func': [(573, F.llm_pysc2_move_camera, ('world_tag')), (208, F.Effect_MassRecall_screen, ('queued', 'screen_tag'))]},
            {'name': 'Ability_TimeWarp_Attack', 'arg': ['tag'],
             'func': [(241, F.Effect_TimeWarp_screen, ('queued', 'screen_tag'))]},
            {'name': 'Ability_TimeWarp_Screen', 'arg': ['screen'],
             'func': [(241, F.Effect_TimeWarp_screen, ('queued', 'screen'))]},
          ],
           units.Protoss.WarpPrism: PROTOSS_BASIC_ACTION_3 + [
            {'name': 'Load_Unit', 'arg': ['tag'], 'func': [(287, F.Load_screen, ('queued', 'screen_tag'))]},
            {'name': 'Unload_Screen', 'arg': ['screen'],
             'func': [(516, F.UnloadAllAt_screen, ('queued', 'screen'))]},
           ],
        },
      },

      # 智能体13：战斗组7 - 特种部队指挥官（使徒、黑暗圣堂武士）
      'CombatGroup7': {
        # 智能体描述：特种部队指挥官的职责
        'describe': "Protoss special force commander, controls Adept and DarkTemplar. "
                    "Responsible for infiltrating the enemy's rear and disrupt economic production, sometimes "
                    "collecting reconnaissance infomation, participating in frontline combat.",
        'llm': {
          'basic_prompt': self.basic_prompt,
          'translator_o': self.translator_o,
          'translator_a': self.translator_a,
          'img_fea': self.ENABLE_IMAGE_FEATURE,
          'img_rgb': self.ENABLE_IMAGE_RGB,
          'model_name': self.model_name,
          'api_base': self.api_base,
          'api_key': self.api_key,
        },
        'team': [
          {'name': 'Adept-1', 'unit_type': [units.Protoss.Adept],
           'game_group': -1, 'select_type': 'select_all_type'},
          {'name': 'AdeptPhase-1', 'unit_type': [units.Protoss.AdeptPhaseShift],
           'game_group': -1, 'select_type': 'select_all_type'},
          {'name': 'DarkTemplar-1', 'unit_type': [units.Protoss.DarkTemplar],
           'game_group': -1, 'select_type': 'select_all_type'},
          # {'name': 'DarkTemplar-2', 'unit_type': [units.Protoss.DarkTemplar],
          #  'game_group': -1, 'select_type': 'select_all_type'},  # more than one select_all_type not currently supported
        ],
        'action': {
          units.Protoss.AdeptPhaseShift: PROTOSS_BASIC_ACTION_3,
          units.Protoss.Adept: PROTOSS_BASIC_ACTION_2 + [
            {'name': 'Ability_AdeptPhaseShift_Screen', 'arg': ['screen'],
             'func': [(177, F.Effect_AdeptPhaseShift_screen, ('queued', 'screen'))]},
            {'name': 'Ability_AdeptPhaseShift_Minimap', 'arg': ['minimap'],
             'func': [(547, F.Effect_AdeptPhaseShift_minimap, ('queued', 'minimap'))]},
            {'name': 'Ability_CancelPhaseShift', 'arg': [], 'func': [(141, F.Cancel_AdeptPhaseShift_quick, ('queued'))]},
          ],
          units.Protoss.DarkTemplar: PROTOSS_BASIC_ACTION_2 + [
            {'name': 'Ability_ShadowStride_Unit', 'arg': ['tag'],
             'func': [(182, F.Effect_ShadowStride_screen, ('queued', 'screen_tag'))]},
            {'name': 'Morph_Archon', 'arg': [],
             'func': [(296, F.Morph_Archon_quick, ('queued'))]},
            {'name': 'Select_Two_Unit_Morph_Archon', 'arg': ['tag', 'tag'],
             'func': [(3, F.select_rect, ('select', 'screen1_tag', 'screen2_tag')),
                      (3, F.select_rect, ('add', 'screen1_tag2', 'screen2_tag2')),  # screen1/2_tag2 not realized yet
                      (296, F.Morph_Archon_quick, ('queued'))]},
          ],
        },
      },

      # 智能体14：战斗组8 - 空中特种部队指挥官（先知、凤凰）
      'CombatGroup8': {
        # 智能体描述：空中特种部队指挥官的职责
        'describe': "Protoss air special force commander, controls Oracle and Phoenix. "
                    "Responsible for infiltrating the enemy's rear and disrupt economic production, sometimes "
                    "collecting reconnaissance infomation, participating in frontline combat, or build StasisTrap "
                    "to block the enemy's main force.",
        'llm': {
          'basic_prompt': self.basic_prompt,
          'translator_o': self.translator_o,
          'translator_a': self.translator_a,
          'img_fea': self.ENABLE_IMAGE_FEATURE,
          'img_rgb': self.ENABLE_IMAGE_RGB,
          'model_name': self.model_name,
          'api_base': self.api_base,
          'api_key': self.api_key,
        },
        'team': [
          {'name': 'Oracle-1', 'unit_type': [units.Protoss.Oracle],
           'game_group': -1, 'select_type': 'select_all_type'},
          {'name': 'Phoenix-1', 'unit_type': [units.Protoss.Phoenix],
           'game_group': -1, 'select_type': 'select_all_type'},
        ],
        'action': {
          units.Protoss.Oracle: PROTOSS_BASIC_ACTION_2 + [
            {'name': 'Ability_PulsarBeamOn', 'arg': [],
             'func': [(38, F.Behavior_PulsarBeamOn_quick, ('queued'))]},
            {'name': 'Ability_OracleRevelation_Screen', 'arg': ['screen'],
             'func': [(214, F.Effect_OracleRevelation_screen, ('queued', 'screen'))]},
            {'name': 'Build_StasisTrap_Screen', 'arg': ['screen'],
             'func': [(90, F.Build_StasisTrap_screen, ('queued', 'screen'))]},
            {'name': 'Select_Unit_Ability_PulsarBeamOn', 'arg': ['tag'],
             'func': [(3, F.select_rect, ('select', 'screen1_tag', 'screen2_tag')),
                      (38, F.Behavior_PulsarBeamOn_quick, ('queued'))]},
            {'name': 'Select_Unit_OracleRevelation_Screen', 'arg': ['tag', 'screen'],
             'func': [(3, F.select_rect, ('select', 'screen1_tag', 'screen2_tag')),
                      (214, F.Effect_OracleRevelation_screen, ('queued', 'screen'))]},
            {'name': 'Select_Unit_Build_StasisTrap_Screen', 'arg': ['tag', 'screen'],
             'func': [(3, F.select_rect, ('select', 'screen1_tag', 'screen2_tag')),
                      (90, F.Build_StasisTrap_screen, ('queued', 'screen'))]},
          ],
          units.Protoss.Phoenix: PROTOSS_BASIC_ACTION_2 + [
            {'name': 'Ability_GravitonBeam_Unit', 'arg': ['tag'],
             'func': [(196, F.Effect_GravitonBeam_screen, ('queued', 'screen_tag'))]},
            {'name': 'Select_Unit_Ability_GravitonBeam_Unit', 'arg': ['tag', 'tag'],
             'func': [(3, F.select_rect, ('select', 'screen1_tag', 'screen2_tag')),
                      (196, F.Effect_GravitonBeam_screen, ('queued', 'screen_tag2'))]},
          ],
        },
      },

      # 智能体15：战斗组9 - 空降指挥官（折跃棱镜）
      'CombatGroup9': {
        # 智能体描述：空降指挥官的职责
        'describe': "Protoss airborne commander, controls WarpPrism and airborne units like Zealots, Stalkers."
                    "Responsible for supplement troops on the front line, or executing multi line combat. "
                    "Keep stability as much as possible in WarpRismPhashing mode to provide stable power field for "
                    "unit warpping.",
        'llm': {
          'basic_prompt': self.basic_prompt,
          'translator_o': self.translator_o,
          'translator_a': self.translator_a,
          'img_fea': self.ENABLE_IMAGE_FEATURE,
          'img_rgb': self.ENABLE_IMAGE_RGB,
          'model_name': self.model_name,
          'api_base': self.api_base,
          'api_key': self.api_key,
        },
        'team': [
          {'name': 'WarpPrism', 'unit_type': [units.Protoss.WarpPrism, units.Protoss.WarpPrismPhasing],
           'game_group': -1, 'select_type': 'select'},
        ],
        'action': {
          units.Protoss.WarpPrism: PROTOSS_BASIC_ACTION_3 + [
            {'name': 'Morph_WarpPrismPhasingMode', 'arg': [],
             'func': [(329, F.Morph_WarpPrismPhasingMode_quick, ('queued'))]},
            {'name': 'Load_Unit', 'arg': ['tag'], 'func': [(287, F.Load_screen, ('queued', 'screen_tag'))]},
            {'name': 'Unload_Screen', 'arg': ['screen'],
             'func': [(516, F.UnloadAllAt_screen, ('queued', 'screen'))]},
          ],
          units.Protoss.WarpPrismPhasing: [
            {'name': 'Wait_For_Unit_Warp', 'arg': [], 'func': [(0, F.no_op, ())]},
            {'name': 'Morph_WarpPrismTransportMode', 'arg': [],
             'func': [(330, F.Morph_WarpPrismTransportMode_quick, ('queued'))]},
          ],
        },
      },
      
      # 智能体16：战斗组10 - 综合特种部队指挥官（使徒、黑暗圣堂武士、折跃棱镜）
      'CombatGroup10': {
        # 智能体描述：综合特种部队指挥官的职责
        'describe': "Protoss special force commander, controls Adept, DarkTemplar and WarpPrism. "
                    "Responsible for infiltrating the enemy's rear and disrupt economic production, sometimes "
                    "collecting reconnaissance infomation, participating in frontline combat.",
        'llm': {
          'basic_prompt': self.basic_prompt,
          'translator_o': self.translator_o,
          'translator_a': self.translator_a,
          'img_fea': self.ENABLE_IMAGE_FEATURE,
          'img_rgb': self.ENABLE_IMAGE_RGB,
          'model_name': self.model_name,
          'api_base': self.api_base,
          'api_key': self.api_key,
        },
        'team': [
          {'name': 'Adept-1', 'unit_type': [units.Protoss.Adept],
           'game_group': -1, 'select_type': 'select_all_type'},
          {'name': 'AdeptPhase-1', 'unit_type': [units.Protoss.AdeptPhaseShift],
           'game_group': -1, 'select_type': 'select_all_type'},
          {'name': 'DarkTemplar-1', 'unit_type': [units.Protoss.DarkTemplar],
           'game_group': -1, 'select_type': 'select_all_type'},
          {'name': 'WarpPrism', 'unit_type': [units.Protoss.WarpPrism, units.Protoss.WarpPrismPhasing],
           'game_group': -1, 'select_type': 'select'},
          # {'name': 'DarkTemplar-2', 'unit_type': [units.Protoss.DarkTemplar],
          #  'game_group': -1, 'select_type': 'select_all_type'},  # more than one select_all_type not currently supported
        ],
        'action': {
          units.Protoss.AdeptPhaseShift: PROTOSS_BASIC_ACTION_3,
          units.Protoss.Adept: PROTOSS_BASIC_ACTION_2 + [
            {'name': 'Ability_AdeptPhaseShift_Screen', 'arg': ['screen'],
             'func': [(177, F.Effect_AdeptPhaseShift_screen, ('queued', 'screen'))]},
            {'name': 'Ability_AdeptPhaseShift_Minimap', 'arg': ['minimap'],
             'func': [(547, F.Effect_AdeptPhaseShift_minimap, ('queued', 'minimap'))]},
            {'name': 'Ability_CancelPhaseShift', 'arg': [], 'func': [(141, F.Cancel_AdeptPhaseShift_quick, ('queued'))]},
          ],
          units.Protoss.DarkTemplar: PROTOSS_BASIC_ACTION_2 + [
            {'name': 'Ability_ShadowStride_Unit', 'arg': ['tag'],
             'func': [(182, F.Effect_ShadowStride_screen, ('queued', 'screen_tag'))]},
            {'name': 'Morph_Archon', 'arg': [],
             'func': [(296, F.Morph_Archon_quick, ('queued'))]},
            {'name': 'Select_Two_Unit_Morph_Archon', 'arg': ['tag', 'tag'],
             'func': [(3, F.select_rect, ('select', 'screen1_tag', 'screen2_tag')),
                      (3, F.select_rect, ('add', 'screen1_tag2', 'screen2_tag2')),  # screen1/2_tag2 not realized yet
                      (296, F.Morph_Archon_quick, ('queued'))]},
          ],
          units.Protoss.WarpPrism: PROTOSS_BASIC_ACTION_3 + [
            {'name': 'Morph_WarpPrismPhasingMode', 'arg': [],
             'func': [(329, F.Morph_WarpPrismPhasingMode_quick, ('queued'))]},
            {'name': 'Load_Unit', 'arg': ['tag'], 'func': [(287, F.Load_screen, ('queued', 'screen_tag'))]},
            {'name': 'Unload_Screen', 'arg': ['screen'],
             'func': [(516, F.UnloadAllAt_screen, ('queued', 'screen'))]},
          ],
          units.Protoss.WarpPrismPhasing: [
            {'name': 'Wait_For_Unit_Warp', 'arg': [], 'func': [(0, F.no_op, ())]},
            {'name': 'Morph_WarpPrismTransportMode', 'arg': [],
             'func': [(330, F.Morph_WarpPrismTransportMode_quick, ('queued'))]},
          ],
        },
      },
    }


# ZergAgentConfig part undergoing
class ZergAgentConfig(AgentConfig):
  def __init__(self):
    super(ZergAgentConfig, self).__init__()
    self.race = "zerg"
    self.AGENTS = {
            'CombatGroup0': {
                'describe': "Zerg frontline commander, controls Zerglings and Roaches. "
                           "Responsible for early aggression and map control.",
                'llm': {
                    'basic_prompt': self.basic_prompt,
                    'translator_o': self.translator_o,
                    'translator_a': self.translator_a,
                    'img_fea': self.ENABLE_IMAGE_FEATURE,
                    'img_rgb': self.ENABLE_IMAGE_RGB,
                    'model_name': self.model_name,
                    'api_base': self.api_base,
                    'api_key': self.api_key,
                },
                'team': [
                    {'name': 'Zergling-1', 'unit_type': [units.Zerg.Zergling, units.Zerg.ZerglingBurrowed],
                     'game_group': 1, 'select_type': 'group'},
                    {'name': 'Roach-1', 'unit_type': [units.Zerg.Roach, units.Zerg.RoachBurrowed],
                     'game_group': 2, 'select_type': 'group'},
                    {'name': 'Infestor-1', 'unit_type': [units.Zerg.Infestor],
                     'game_group': 6, 'select_type': 'group'},
                ],
                'action': {
                    units.Zerg.Zergling: ZERG_BASIC_ACTION_2 + [
                         {'name': 'Ability_BurrowDown', 'arg': [],
                         'func': [(103, F.BurrowDown_quick, ('queued'))]},],
                    units.Zerg.ZerglingBurrowed: [
                         {'name': 'Ability_BurrowUp', 'arg': [],
                         'func': [(117, F.BurrowUp_quick, ('queued'))]},],
                    units.Zerg.Roach: ZERG_BASIC_ACTION_2 + [
                         {'name': 'Ability_BurrowDown', 'arg': [],
                         'func': [(103, F.BurrowDown_quick, ('queued'))]},],
                    units.Zerg.RoachBurrowed: ZERG_BASIC_ACTION_3 + [
                         {'name': 'Ability_BurrowUp', 'arg': [],
                         'func': [(117, F.BurrowUp_quick, ('queued'))]},],
                    units.Zerg.Infestor: ZERG_BASIC_ACTION_3 + [
                         {'name': 'Ability_NeuralParasite', 'arg': ['screen'],'func': [(212, F.Effect_NeuralParasite_screen, ('queued', 'screen'))]},
                    ],
                },
            },

            'CombatGroup1': {
                'describe': "Zerg air commander, controls Mutalisks and Hydralisks. "
                           "Responsible for air superiority and harassment.",
                'llm': {
                    'basic_prompt': self.basic_prompt,
                    'translator_o': self.translator_o,
                    'translator_a': self.translator_a,
                    'img_fea': self.ENABLE_IMAGE_FEATURE,
                    'img_rgb': self.ENABLE_IMAGE_RGB,
                    'model_name': self.model_name,
                    'api_base': self.api_base,
                    'api_key': self.api_key,
                },
                'team': [
                    {'name': 'Mutalisk-1', 'unit_type': [units.Zerg.Mutalisk],
                     'game_group': 3, 'select_type': 'group'},
                    {'name': 'Hydralisk-1', 'unit_type': [units.Zerg.Hydralisk],
                     'game_group': 4, 'select_type': 'group'},
                ],
                'action': {
                    units.Zerg.Mutalisk: ZERG_BASIC_ACTION_2,
                    units.Zerg.Hydralisk: ZERG_BASIC_ACTION_2,
                },
            },

            'CombatGroup2': {
                'describe': "Zerg support commander, controls Infestors. "
                           "Responsible for sneaking, harassing, and spellcasting.",
                'llm': {
                    'basic_prompt': self.basic_prompt,
                    'translator_o': self.translator_o,
                    'translator_a': self.translator_a,
                    'img_fea': self.ENABLE_IMAGE_FEATURE,
                    'img_rgb': self.ENABLE_IMAGE_RGB,
                    'model_name': self.model_name,
                    'api_base': self.api_base,
                    'api_key': self.api_key,
                },
                'team': [
                    # {'name': 'Queen-1', 'unit_type': [units.Zerg.Queen],
                    #  'game_group': 5, 'select_type': 'group'},
                    {'name': 'Infestor-1', 'unit_type': [units.Zerg.Infestor, units.Zerg.InfestorBurrowed],
                     'game_group': 6, 'select_type': 'group'},
                ],
                'action': {
                    # units.Zerg.Queen: ZERG_BASIC_ACTION_3 + [
                    #     {'name': 'Ability_InjectLarva', 'arg': ['tag'],
                    #      'func': [(527, F.Effect_InjectLarva_screen, ('queued', 'screen_tag'))]},
                    # ],
                    units.Zerg.Infestor: ZERG_BASIC_ACTION_3 + [
                        # {'name': 'Ability_FungalGrowth', 'arg': ['screen'],
                        #  'func': [(214, F.Effect_FungalGrowth_screen, ('queued', 'screen'))]},
                        {'name': 'Ability_InfestedTerrans', 'arg': ['screen'],
                         'func': [(203, F.Effect_InfestedTerrans_screen, ('queued', 'screen'))]},
                        {'name': 'Ability_BurrowDown', 'arg': [],
                         'func': [(103, F.BurrowDown_quick, ('queued'))]},
                    ],
                     units.Zerg.InfestorBurrowed: ZERG_BASIC_ACTION_3 + [
                        # {'name': 'Ability_FungalGrowth', 'arg': ['screen'],
                        #  'func': [(214, F.Effect_FungalGrowth_screen, ('queued', 'screen'))]},
                        {'name': 'Ability_InfestedTerrans', 'arg': ['screen'],
                         'func': [(203, F.Effect_InfestedTerrans_screen, ('queued', 'screen'))]},
                        {'name': 'Ability_BurrowUp', 'arg': [],
                         'func': [(117, F.BurrowUp_quick, ('queued'))]},
                    ],
                    units.Zerg.InfestedTerran: ZERG_BASIC_ACTION_2,
                },
            },
            'Builder': {
                'describe': "Zerg builder, controls several Drones. Responsible for building structures.",
                'llm': {
                    'basic_prompt': self.basic_prompt,
                    'translator_o': self.translator_o,
                    'translator_a': self.translator_a,
                    'img_fea': self.ENABLE_IMAGE_FEATURE,
                    'img_rgb': self.ENABLE_IMAGE_RGB,
                    'model_name': self.model_name,
                    'api_base': self.api_base,
                    'api_key': self.api_key,
                },
                'team': [
                    {'name': 'Builder-Drone-1', 'unit_type': [units.Zerg.Drone],
                     'game_group': -1, 'select_type': 'select'},
                ],
                'action': {
                    units.Zerg.Drone: ZERG_BASIC_ACTION_3 + ZERG_ACTION_BUILD,
                },
            },
            'Developer': {
                'describe': "Zerg logistics commander. Responsible for unit training and technology upgrades.",
                'llm': {
                    'basic_prompt': self.basic_prompt,
                    'translator_o': 'developer',
                    'translator_a': self.translator_a,
                    'img_fea': self.ENABLE_IMAGE_FEATURE,
                    'img_rgb': self.ENABLE_IMAGE_RGB,
                    'model_name': self.model_name,
                    'api_base': self.api_base,
                    'api_key': self.api_key,
                },
                'team': [
                    {'name': 'Developer-Larva-1', 'unit_type': [units.Zerg.Larva],
                     'game_group': -1, 'select_type': 'select'},
                ],
                'action': {
                    units.Zerg.Larva: ZERG_BASIC_ACTION_1 + ZERG_ACTION_TRAIN,  
                },
            },
        }
        
        # ==================== AGENTS配置总结 ====================
        # 
        # 本配置定义了完整的多智能体系统，包含以下核心组件：
        # 
        # 1. 智能体类型：
        #    - Airborne: 空降指挥官（控制追猎者进行空降作战）
        #    - Builder: 建造者（控制探机进行建筑建造）
        #    - Commander: 军事指挥官（负责宏观决策和战术指挥）
        #    - Developer: 后勤指挥官（负责单位训练和科技升级）
        #    - Defender: 防御指挥官（控制追猎者进行基地防御）
        #    - CombatGroup0: 前线指挥官（控制狂战士进行多线作战）
        #    - CombatGroup1: 前线指挥官（控制追猎者进行前线压制）
        #    - CombatGroup2: 地面主力指挥官（控制不朽者、巨像、执政官）
        #    - CombatGroup3: 空中主力指挥官（控制虚空辉光舰、航母、风暴战舰）
        #    - CombatGroup4: 侦察指挥官（控制探机、观察者进行侦察）
        #    - CombatGroup5: AOE伤害指挥官（控制高阶圣堂武士、干扰者）
        #    - CombatGroup6: 战术支援指挥官（控制哨兵、母舰、折跃棱镜）
        #    - CombatGroup7: 特种部队指挥官（控制使徒、黑暗圣堂武士进行渗透）
        #    - CombatGroup8: 空中特种部队指挥官（控制先知、凤凰进行空中骚扰）
        #    - CombatGroup9: 空降指挥官（控制折跃棱镜进行空降作战）
        #    - CombatGroup10: 综合特种部队指挥官（控制使徒、黑暗圣堂武士、折跃棱镜）
        # 
        # 2. 配置结构：
        #    - describe: 智能体描述（为LLM提供角色定位）
        #    - llm: LLM配置（模型参数、API配置、转换器设置）
        #    - team: 团队配置（控制的单位类型、分组、选择方式）
        #    - action: 动作配置（可执行的动作和技能）
        # 
        # 3. 协作机制：
        #    - 指挥官和开发者可以访问其他智能体的信息
        #    - 各智能体通过通信系统协调作战
        #    - 不同智能体控制不同分组的单位，实现分工合作
        # 
        # 4. 游戏集成：
        #    - 每个智能体对应特定的游戏单位类型
        #    - 动作配置直接映射到PySC2函数调用
        #    - 支持复杂的技能组合和战术操作
        # 
        # ========================================================