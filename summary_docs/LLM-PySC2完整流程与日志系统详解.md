# LLM-PySC2 完整流程与日志系统详解

## 目录
1. [项目概述](#1-项目概述)
2. [从experiment_llm_36strat.py开始的完整流程](#2-从experiment_llm_36stratpy开始的完整流程)
3. [日志系统详解](#3-日志系统详解)
4. [游戏多轮对话上下文](#4-游戏多轮对话上下文)
5. [MainAgent和SubAgent详解](#5-mainagent和subagent详解)
6. [关键代码分析](#6-关键代码分析)
7. [实际运行示例](#7-实际运行示例)

---

## 1. 项目概述

LLM-PySC2是一个基于大语言模型(LLM)的星际争霸II多智能体决策系统，通过将游戏观察转换为文本描述，让LLM进行决策，然后将文本动作转换为PySC2可执行的函数调用。

### 核心特性
- **多智能体协作**：支持多个智能体同时协作
- **多轮对话**：保持游戏上下文，支持连续决策
- **多模态支持**：支持文本和图像观察
- **异步执行**：多线程并发LLM查询
- **完整日志**：记录观察、决策、执行、通信全过程
- **配置驱动**：通过配置文件控制智能体行为

---

## 2. 从experiment_llm_36strat.py开始的完整流程

### 2.1 实验启动流程

```python
# experiment_llm_36strat.py:146-150
if __name__ == "__main__":
    if not (enable_image_rgb or enable_image_feature):
        os.system(f"python -m pysc2.bin.agent --map {map_name} --agent_race {agent_race} --parallel 1 "
                  f"--agent llm_pysc2.bin.experiment_llm_36strat.MainAgentTSSPysc2 --render")
```

**执行步骤：**
1. 启动PySC2游戏环境
2. 加载指定地图（如"wzsy_te"无中生有地图）
3. 设置种族（如"protoss"神族）
4. 创建MainAgentTSSPysc2实例

### 2.2 主智能体初始化

```python
# experiment_llm_36strat.py:132-140
class MainAgentTSSPysc2(MainAgent):
    def __init__(self):
        config = get_config(agent_race, map_name)  # 获取配置
        config.reset_llm(None, None, None, enable_image_rgb, enable_image_feature)
        super(MainAgentTSSPysc2, self).__init__(config, LLMAgent)  # 初始化主智能体
```

**初始化流程：**
1. **配置加载**：根据种族和地图获取配置
2. **LLM设置**：配置LLM API参数和图像模式
3. **主智能体创建**：创建MainAgent实例

### 2.3 配置加载与任务设置

```python
# experiment_llm_36strat.py:6-125
def get_config(race, map):
    config = ConfigPysc2_Combat(race)()  # 基础配置
    config.ENABLE_COMMUNICATION = True   # 启用通信
    config.MAX_LLM_RUNTIME_ERROR_TIME = 600
    
    # 根据地图设置不同的三十六计任务
    if map.lower() == "wzsy_te":  # 无中生有
        for agent_name in list(config.AGENTS.keys()):
            for team in config.AGENTS[agent_name]['team']:
                team['task'] = [
                    {'time': None, 'pos': None, 'info': "use Create something from nothing to attack the enemy base"}
                ]
    # ... 其他地图配置
```

**配置内容：**
- **智能体配置**：CombatGroup1-6、Commander、Developer等
- **任务设置**：根据三十六计设置不同策略
- **通信设置**：启用智能体间通信
- **LLM配置**：API密钥、模型名称、超时时间等

### 2.4 主智能体初始化流程

```python
# llm_pysc2_agent_main.py:47-50
class MainAgent(base_agent.BaseAgent):
    def __init__(self, config=ProtossAgentConfig(), SubAgent=LLMAgent):
        super(MainAgent, self).__init__()
        self.start_time = str(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
        
        # 1. 基础信息设置
        self.config = config
        self.AGENT_NAMES = list(config.AGENTS.keys())
        self.race = config.race
        
        # 2. 变量初始化
        self.main_loop_step = 0
        self.agent_id = 0
        self.main_loop_lock = False
        
        # 3. 日志系统初始化
        self._initialize_logger()
        
        # 4. 智能体初始化
        self._initialize_agents(SubAgent)
        
        # 5. 配置自动检查
        self._auto_check_config()
```

**初始化步骤：**
1. **基础信息设置**：保存配置、智能体名称、种族
2. **变量初始化**：游戏循环步数、智能体ID、锁状态
3. **日志系统初始化**：创建日志目录和文件
4. **智能体初始化**：创建所有子智能体实例
5. **配置自动检查**：验证配置正确性

### 2.5 游戏主循环

```python
# llm_pysc2_agent_main.py:142-143
def step(self, obs):
    return super().step(obs)  # 调用MainAgent.step方法
```

**主循环被PySC2框架自动调用**，每次游戏步都会执行。

---

## 3. 主循环执行流程

### 3.1 初始化阶段

```python
# llm_pysc2_agent_main.py:200-300
def step(self, obs):
    # 步骤1: 初始化步骤（摄像头校准、单位分组等）
    if self.main_loop_step == 0:
        func_call = main_agent_func0(self, obs)  # 摄像头校准
        if func_call is not None:
            return func_call
    
    # 步骤2: 子智能体数据更新
    for agent_name in self.AGENT_NAMES:
        agent = self.agents[agent_name]
        agent.update(obs)  # 更新智能体状态
```

**初始化步骤：**
- **摄像头校准**：建立世界坐标与屏幕坐标的映射关系
- **单位分组**：将游戏单位分配给不同智能体
- **状态更新**：更新所有智能体的内部状态

### 3.2 观察收集阶段

```python
# llm_pysc2_agent_main.py:300-400
# 步骤3: 观察收集
for agent_name in self.AGENT_NAMES:
    agent = self.agents[agent_name]
    if agent.enable:
        # 收集每个团队的观察数据
        for team in agent.teams:
            team_obs = collect_team_observation(agent, team, obs)
            agent.team_unit_obs_list.append(team_obs)
```

**观察收集内容：**
- **游戏基础信息**：时间、资源、科技等
- **单位详细信息**：位置、血量、能量、技能等
- **任务目标信息**：当前任务和约束
- **有效动作列表**：当前可执行的动作
- **通信信息**：其他智能体的消息

### 3.3 LLM查询阶段

```python
# llm_pysc2_agent_main.py:400-500
# 步骤4: LLM查询
if not self._all_agent_query_llm_finished():
    if agent._is_all_my_teams_ready_to_query():
        # 启动多线程LLM查询
        agent.thread = threading.Thread(target=thread_act, args=(agent, obs))
        agent.thread.start()
        agent.query_llm_times += 1
```

**LLM查询流程：**
1. **检查查询状态**：确保所有智能体都准备好查询
2. **启动多线程**：每个智能体在独立线程中查询LLM
3. **异步执行**：多个智能体可以同时查询LLM
4. **等待响应**：主循环等待所有智能体完成查询

### 3.4 动作执行阶段

```python
# llm_pysc2_agent_main.py:500-600
# 步骤5: 动作执行
elif not self._all_agent_executing_finished():
    if len(agent.func_list) == 0 and len(agent.action_list) == 0 and len(agent.action_lists) > 0:
        # 从action_lists中取出动作
        agent.action_list = agent.action_lists.pop(0)
    
    # 获取PySC2函数调用
    func_id, func_call = agent.get_func(obs)
    
    # 验证并执行
    if func_id in obs.observation.available_actions:
        return func_call
```

**动作执行流程：**
1. **动作提取**：从action_lists中取出待执行的动作
2. **函数转换**：将文本动作转换为PySC2函数调用
3. **参数验证**：检查函数ID和参数的有效性
4. **执行返回**：返回PySC2函数调用给游戏环境

---

## 4. 日志系统详解

### 4.1 日志目录结构

```
llm_log/
├── 20250923100441-1/                    # 实验目录 (时间戳-日志ID)
│   ├── log_error.txt                    # 错误日志
│   ├── log_success.txt                  # 成功日志
│   ├── log_info.txt                     # 信息日志
│   ├── log_debug.txt                    # 调试日志
│   ├── CombatGroup1/                    # 智能体1日志目录
│   │   ├── o.txt                        # 观察日志
│   │   ├── a_raw.txt                    # LLM原始响应
│   │   ├── a_pro.txt                    # 处理后的动作
│   │   ├── a_his.txt                    # 动作执行历史
│   │   ├── c_inp.txt                    # 通信输入
│   │   ├── c_out.txt                    # 通信输出
│   │   ├── cost.txt                     # 成本统计
│   │   ├── prompt.txt                   # 提示词
│   │   ├── rgb_images/                  # RGB图像（如果启用）
│   │   └── fea_images/                  # 特征图像（如果启用）
│   ├── CombatGroup6/                    # 智能体6日志目录
│   │   └── ... (同上)
│   └── ...
```

### 4.2 日志文件详解

#### 4.2.1 观察日志 (`o.txt`)

**内容：** 记录每个游戏步的观察数据

```json
{"1": "Game Info:\n\tTime: 0:05\n\tMinerals: 50\n\tVespene: 0\n\nTeam Stalker-1 Info:\n\tTeam minimap position: [42, 42]\n\tControlled units: 2 Stalkers\n\tHealth: 160/160 (100%)\n\tEnergy: 0\n\nValid Actions:\n\tTeam Stalker-1 Valid Actions:\n\t\tMove_Screen([x, y])\n\t\tAttack_Unit(0x...)\n\nLast Step Actions:\n\tTeam Stalker-1:\n\t\t<Move_Screen([40, 60])>\n\nTasks:\n\tTeam Stalker-1' task: use Create something from nothing to attack the enemy base"}
```

**包含信息：**
- 游戏基础信息（时间、资源、科技等）
- 单位详细信息（位置、血量、能量、技能等）
- 有效动作列表
- 上次动作信息（多轮对话的关键）
- 任务目标信息

#### 4.2.2 LLM原始响应 (`a_raw.txt`)

**内容：** 记录LLM的原始响应

```json
{"1": "Analysis:\n  We are controlling a team called Stalker-1, consisting of 2 Stalkers. Our task is to attack the enemy base using the stratagem \"Create something from nothing\". We need to deceive the enemy with an illusion of a strong force.\n\nActions:\n  Team Stalker-1:\n    <Move_Screen([40, 60])>\n    <Attack_Unit(0x101100001)>\n\nCommunications:\n  <MessageTo(CombatGroup6, '''Prepare to attack the enemy base. We will create an illusion of a strong force to deceive the enemy.''')>"}
```

**包含信息：**
- LLM的分析和推理过程
- 生成的动作列表
- 通信消息（如果启用）

#### 4.2.3 处理后的动作 (`a_pro.txt`)

**内容：** 记录经过解析和验证的动作

```json
{"1": "Actions:\n\tTeam Stalker-1:\n\t\t<Move_Screen([40, 60])>\n\t\t<Attack_Unit(0x101100001)>"}
```

**包含信息：**
- 解析后的动作列表
- 去除无效动作
- 格式化的动作描述

#### 4.2.4 动作执行历史 (`a_his.txt`)

**内容：** 记录实际执行的PySC2函数调用

```json
{"1": "CombatGroup1;   loop1;   step1;   [Valid]  Move_Screen [40, 60]"}
{"2": "CombatGroup1;   loop1;   step2;   [Valid]  Attack_Unit 0x101100001"}
```

**包含信息：**
- 智能体名称
- 游戏循环步数
- 执行步数
- 动作状态（有效/无效）
- 实际执行的函数和参数

#### 4.2.5 通信输入 (`c_inp.txt`)

**内容：** 记录接收到的通信消息

```json
{"0": ""}
{"1": "\n\nCommunication information:\n\tFrom CombatGroup6: \n\t\tPrepare to attack the enemy base. We will create an illusion of a strong force to deceive the enemy."}
```

**包含信息：**
- 发送方智能体名称
- 消息内容
- 接收时间

#### 4.2.6 通信输出 (`c_out.txt`)

**内容：** 记录发送的通信消息

```json
{"1": "Communications:\n  <MessageTo(CombatGroup6, '''Prepare to attack the enemy base. We will create an illusion of a strong force to deceive the enemy.''')>"}
```

**包含信息：**
- 接收方智能体名称
- 消息内容
- 发送时间

#### 4.2.7 成本统计 (`cost.txt`)

**内容：** 记录LLM查询的成本信息

```json
{"1": "time=2.34, ave_time=2.34, token_in=1250, ave_token_in=1250.0, token_out=180, ave_token_out=180.0"}
```

**包含信息：**
- 查询时间
- 平均查询时间
- 输入token数量
- 平均输入token数量
- 输出token数量
- 平均输出token数量

#### 4.2.8 提示词 (`prompt.txt`)

**内容：** 记录完整的提示词模板

```
You are a Protoss commander controlling Stalkers...
-- example input prompt --
Game Info:
    Time: 0:05
    Minerals: 50
...
-- example output prompt --
Actions:
  Team Stalker-1:
    <Move_Screen([40, 60])>
    <Attack_Unit(0x101100001)>
```

**包含信息：**
- 系统提示词
- 示例输入格式
- 示例输出格式

### 4.3 日志系统初始化

```python
# llm_pysc2_agent_main.py:_initialize_logger
def _initialize_logger(self):
    global llm_pysc2_global_log_id
    time.sleep(random.random())
    base_log_dir = f"{os.path.dirname(os.path.abspath(__file__))}/../../llm_log"
    if not os.path.exists(base_log_dir):
        os.mkdir(base_log_dir)
    
    # 创建日志目录
    self.log_id = -1
    while True:
        self.log_id += 1
        self.log_dir_path = f"{os.path.dirname(os.path.abspath(__file__))}/../../llm_log/{self.start_time}-{self.log_id}"
        if not os.path.exists(self.log_dir_path) and self.log_id == llm_pysc2_global_log_id + 1:
            llm_pysc2_global_log_id += 1
            os.mkdir(self.log_dir_path)
            break
    
    # 创建日志文件
    self.log_error_path = self.log_dir_path + f"/log_error.txt"
    self.log_success_path = self.log_dir_path + f"/log_success.txt"
    self.log_debug_path = self.log_dir_path + f"/log_debug.txt"
    self.log_info_path = self.log_dir_path + f"/log_info.txt"
    
    # 配置日志记录器
    logger.add(self.log_error_path, level="ERROR", rotation="100 MB", catch=True)
    logger.add(self.log_success_path, level="SUCCESS", rotation="100 MB", catch=True)
    logger.add(self.log_debug_path, level="DEBUG", rotation="100 MB", catch=True)
    logger.add(self.log_info_path, level="INFO", rotation="100 MB", catch=True)
```

---

## 5. 游戏多轮对话上下文

### 5.1 上下文组成

#### 5.1.1 系统提示词 (`basic_prompt.sp`)

```python
# 包含智能体角色、任务描述、游戏规则等
"You are a Protoss commander controlling Stalkers. Your task is to attack the enemy base using the stratagem 'Create something from nothing'..."
```

**内容：**
- 智能体角色定义
- 任务描述和目标
- 游戏规则和约束
- 输出格式要求

#### 5.1.2 示例输入 (`basic_prompt.eip`)

```python
# 展示LLM应该接收的输入格式
"Game Info:\n\tTime: 0:05\n\tMinerals: 50\n\nTeam Stalker-1 Info:\n\tControlled units: 2 Stalkers..."
```

**内容：**
- 游戏信息格式
- 单位信息格式
- 有效动作格式
- 任务信息格式

#### 5.1.3 示例输出 (`basic_prompt.eop`)

```python
# 展示LLM应该输出的格式
"Actions:\n  Team Stalker-1:\n    <Move_Screen([40, 60])>\n    <Attack_Unit(0x101100001)>"
```

**内容：**
- 动作输出格式
- 通信输出格式
- 参数格式要求

#### 5.1.4 当前观察 (`text_o`)

```python
# 包含：
# 1. 游戏基础信息（时间、资源、科技等）
# 2. 单位详细信息（位置、血量、能量、技能等）
# 3. 任务目标和约束
# 4. 有效动作列表
# 5. 通信信息（如果启用）
# 6. 上次动作信息（多轮对话的关键）
```

**详细内容：**

**游戏基础信息：**
```
Game Info:
    Time: 0:05
    Minerals: 50
    Vespene: 0
    Supply Total: 15
    Supply Left: 5
```

**单位详细信息：**
```
Team Stalker-1 Info:
    Team minimap position: [42, 42]
    Controlled units: 2 Stalkers
    Health: 160/160 (100%)
    Energy: 0
    Weapon Ready
```

**有效动作列表：**
```
Valid Actions:
    Team Stalker-1 Valid Actions:
        Move_Screen([x, y])
        Attack_Unit(0x...)
        Ability_Blink_Screen([x, y])
```

**任务信息：**
```
Tasks:
    Team Stalker-1' task: use Create something from nothing to attack the enemy base
```

#### 5.1.5 上次动作信息 (`last_text_a_pro`)

```python
# 来自get_last_action_info函数
if isinstance(agent.last_text_a_pro, str) and len(agent.last_text_a_pro) > 0:
    text_last_action += f"\n\nLast Step {agent.last_text_a_pro}"
    text_last_action += f"\nYou need to confirm whether the previous action finished executing, and based on this, determine whether to continue the old strategy or immediately take other actions."
```

**内容：**
- 上一步执行的动作
- 动作执行状态确认
- 策略连续性指导

### 5.2 上下文包装

```python
# llm_pysc2_agent.py:402-417
def get_text_a(self, text_o: str, base64_image=None) -> str:
    # text_o 就是 obs_prompt，直接传递给LLM客户端
    if base64_image is None:
        text_a = self.client.query(text_o)  # 纯文本模式
    else:
        text_a = self.client.query(text_o, base64_image=base64_image)  # 多模态模式
    
    return text_a
```

**包装流程：**
1. **系统提示词**：在LLM客户端中提供角色和任务定义
2. **当前观察**：包含游戏状态和上次动作（仅上一次，不是全部历史）
3. **图像信息**：如果启用多模态，添加图像数据
4. **完整提示**：在客户端中组合所有信息发送给LLM

### 5.3 obs_prompt 的构建方式详解

#### 5.3.1 关键发现：只包含上一次历史记录

**重要结论：** `obs_prompt` 只包含上一次的历史记录，不是所有历史聊天记录。

#### 5.3.2 构建流程

```python
# llm_pysc2_agent.py:402-420
def get_text_a(self, text_o: str, base64_image=None) -> str:
    # text_o 就是 obs_prompt
    if base64_image is None:
        text_a = self.client.query(text_o)  # 直接传递 text_o 给 LLM
    else:
        text_a = self.client.query(text_o, base64_image=base64_image)
```

#### 5.3.3 text_o (即 obs_prompt) 的组成

```python
# llm_observation.py:771-820
def translate(self, agent) -> str:
    # 步骤2: 收集基础观察信息
    obs = obs_list[0]
    game_info = get_game_info(obs, agent)                    # 游戏基础信息
    units_info = get_teams_info_with_knowledge(agent)        # 单位详细信息
    valid_actions = get_valid_actions_from_obs(obs, agent)   # 有效动作列表
    last_action_info = get_last_action_info(agent)           # 上次动作信息 ← 关键！
    task_info = get_task_info(agent)                        # 任务目标信息
    
    # 步骤3: 组合所有观察信息
    text_obs = game_info + units_info + valid_actions + last_action_info + task_info
    
    # 步骤4: 添加通信信息（如果启用）
    if agent.config.ENABLE_COMMUNICATION:
        communication_info = get_communication_info(agent)
        text_obs += communication_info
    
    return text_obs
```

#### 5.3.4 关键：last_action_info 只包含上一次

```python
# llm_observation.py:604-609
def get_last_action_info(agent) -> str:
    text_last_action = ""
    if isinstance(agent.last_text_a_pro, str) and len(agent.last_text_a_pro) > 0:
        text_last_action += f"\n\nLast Step {agent.last_text_a_pro}"  # 只包含上一次！
        text_last_action += f"\nYou need to confirm whether the previous action finished executing, and based on this, determine whether to continue the old strategy or immediately take other actions."
    return text_last_action
```

#### 5.3.5 LLM客户端消息格式

```python
# llm_client.py:289-296
def wrap_message(self, obs_prompt, base64_image):
    # 纯文本消息格式
    self.messages = [
        {"role": "system", "content": self.system_prompt},      # 系统提示词
        {"role": "user", "content": self.example_i_prompt},     # 示例输入
        {"role": "assistant", "content": self.example_o_prompt}, # 示例输出
        {"role": "user", "content": obs_prompt}                 # 当前观察（包含上次动作）
    ]
```

#### 5.3.6 完整的 obs_prompt 内容

```python
obs_prompt = (
    game_info +           # 当前游戏信息（时间、资源等）
    units_info +          # 当前单位信息（位置、血量等）
    valid_actions +       # 当前有效动作列表
    last_action_info +    # 上一次动作信息（仅上一次！）
    task_info +           # 任务目标信息
    communication_info    # 通信信息（如果启用）
)
```

#### 5.3.7 历史记录机制

**只保存上一次动作：**
```python
# 每次LLM查询后更新
self.last_text_a_pro = processed_text_a  # 只保存上一次处理后的动作
```

**不保存完整历史：**
- ❌ 不保存所有历史聊天记录
- ❌ 不保存所有历史动作
- ✅ 只保存上一次动作的执行结果

#### 5.3.8 实际示例

**第一次查询：**
```
obs_prompt = 
"Game Info:
    Time: 0:05
    Minerals: 50

Team Stalker-1 Info:
    Controlled units: 2 Stalkers
    Health: 160/160

Valid Actions:
    Move_Screen([x, y])
    Attack_Unit(0x...)

Tasks:
    Team Stalker-1' task: use Create something from nothing to attack the enemy base"
```

**第二次查询：**
```
obs_prompt = 
"Game Info:
    Time: 0:10
    Minerals: 45

Team Stalker-1 Info:
    Controlled units: 2 Stalkers
    Health: 160/160

Valid Actions:
    Move_Screen([x, y])
    Attack_Unit(0x...)

Last Step Actions:
    Team Stalker-1:
        <Move_Screen([40, 60])>
You need to confirm whether the previous action finished executing, and based on this, determine whether to continue the old strategy or immediately take other actions.

Tasks:
    Team Stalker-1' task: use Create something from nothing to attack the enemy base"
```

#### 5.3.9 总结

**obs_prompt 的特点：**
- ✅ **只包含上一次动作信息**，不包含全部历史
- ✅ **每次查询都重置消息列表**，不保留历史对话
- ✅ **通过 last_text_a_pro 提供上下文**，包含上一次动作的执行结果
- ✅ **系统提示词和示例每次都重新发送**

**这样设计的原因：**
1. **控制Token使用**：避免上下文过长
2. **保持决策时效性**：专注于当前状态
3. **简化上下文管理**：减少复杂性
4. **避免历史干扰**：防止过时信息影响决策

### 5.4 多轮对话机制

**关键机制：**
- **状态保持**：通过`last_text_a_pro`保持动作历史（仅上一次）
- **上下文连续性**：每次查询都包含上次动作信息
- **策略一致性**：LLM可以基于历史动作调整策略
- **执行确认**：要求LLM确认上次动作的执行状态

---

## 6. MainAgent和SubAgent详解

### 6.1 MainAgent（主智能体）

#### 6.1.1 主要职责

**游戏循环控制：**
- 协调观察、决策、执行三个阶段
- 管理游戏主循环的执行顺序
- 控制智能体的启用和禁用

**多智能体管理：**
- 创建和管理所有子智能体
- 协调智能体间的协作
- 处理智能体间的通信

**资源管理：**
- 摄像头位置控制
- 单位分组和分配
- 坐标系统校准

**日志系统：**
- 初始化和管理日志系统
- 记录游戏执行过程
- 提供调试和分析支持

**配置管理：**
- 加载和验证配置
- 管理全局参数
- 处理配置更新

#### 6.1.2 核心方法

```python
class MainAgent(base_agent.BaseAgent):
    def __init__(self, config, SubAgent):
        """初始化主智能体"""
        # 基础信息设置
        # 变量初始化
        # 日志系统初始化
        # 智能体初始化
        # 配置自动检查
    
    def step(self, obs):
        """主循环：观察 -> 决策 -> 执行"""
        # 初始化步骤
        # 观察收集
        # LLM查询
        # 动作执行
    
    def _initialize_agents(self, SubAgent):
        """创建子智能体实例"""
        for agent_name in self.AGENT_NAMES:
            self.agents[agent_name] = SubAgent(agent_name, self.log_id, self.start_time, self.config)
    
    def _initialize_logger(self):
        """初始化日志系统"""
        # 创建日志目录
        # 配置日志记录器
        # 设置日志文件
    
    def _auto_check_config(self):
        """自动检查配置"""
        # 验证配置正确性
        # 检查必要参数
        # 设置默认值
```

#### 6.1.3 状态管理

```python
# 主循环状态
self.main_loop_step = 0      # 游戏循环步数
self.agent_id = 0           # 当前智能体ID
self.main_loop_lock = False # 主循环锁

# 智能体状态
self.agents = {}            # 智能体字典
self.agents_query_llm_times = {}  # 查询次数统计
self.agents_executing_times = {}  # 执行次数统计

# 游戏状态
self.unit_selected_tag_list = []  # 选中的单位标签
self.camera_threshold = 10        # 摄像头阈值
```

### 6.2 SubAgent（子智能体/LLMAgent）

#### 6.2.1 主要职责

**观察处理：**
- 将PySC2游戏观察转换为文本描述
- 提取单位信息、游戏状态、任务目标
- 处理多模态观察（文本+图像）

**LLM交互：**
- 构建完整的提示词
- 调用LLM API获取决策
- 处理LLM响应和错误

**动作转换：**
- 解析LLM生成的文本动作
- 转换为PySC2可执行的函数调用
- 验证动作的有效性

**通信处理：**
- 发送消息给其他智能体
- 接收和处理其他智能体的消息
- 维护通信状态

**状态管理：**
- 维护智能体内部状态
- 跟踪单位列表和团队信息
- 管理动作执行队列

#### 6.2.2 核心方法

```python
class LLMAgent:
    def __init__(self, name, log_id, start_time, config):
        """初始化子智能体"""
        # 基础信息设置
        # 组件初始化（提示词、转换器、通信器等）
        # 状态初始化
    
    def update(self, obs):
        """更新智能体状态"""
        # 更新屏幕和小地图尺寸
        # 动态启用/禁用智能体
        # 维护单位列表
        # 处理死亡单位
        # 初始化日志文件
    
    def query(self, obs):
        """LLM查询流程"""
        # 设置等待状态
        # 获取通信输入
        # 转换观察为文本
        # 调用LLM API
        # 转换动作为函数
        # 处理通信输出
        # 设置动作列表
    
    def get_text_o(self, obs):
        """观察转文本"""
        # 使用观察转换器
        # 记录观察日志
        # 返回文本描述
    
    def get_text_a(self, text_o):
        """LLM查询"""
        # 构建完整提示词
        # 调用LLM API
        # 记录原始响应
        # 返回LLM响应
    
    def get_func_a(self, raw_text_a):
        """动作转换"""
        # 使用动作转换器
        # 记录处理后的动作
        # 记录成本统计
        # 返回动作列表
    
    def get_func(self, obs):
        """获取PySC2函数调用"""
        # 从动作列表中取出动作
        # 转换为PySC2函数
        # 验证参数有效性
        # 返回函数调用
```

#### 6.2.3 状态管理

```python
# 基础状态
self.name = name                    # 智能体名称
self.log_id = log_id               # 日志ID
self.enable = False                # 启用状态
self.is_waiting = False            # 等待状态

# 游戏状态
self.size_screen = 0               # 屏幕尺寸
self.size_minimap = 0              # 小地图尺寸
self.unit_tag_list = []            # 单位标签列表
self.unit_raw_list = []            # 原始单位列表
self.teams = []                    # 团队列表

# 动作状态
self.action_lists = []             # 动作列表（多个团队）
self.action_list = []              # 当前团队动作列表
self.func_list = []                # PySC2函数列表
self.curr_action_name = ''         # 当前动作名称
self.curr_action_args = []         # 当前动作参数

# 通信状态
self.communication_message_i = {}  # 接收的消息
self.communication_message_o = {}  # 发送的消息
self.last_text_c_inp = ''          # 上次通信输入
self.last_text_c_tar = ''          # 上次通信目标

# 历史状态
self.last_text_a_raw = ''          # 上次LLM原始响应
self.last_text_a_pro = ''          # 上次处理后的动作
self.unit_tag_list_history = []    # 单位标签历史
```

### 6.3 协作关系

#### 6.3.1 创建关系

```python
# 主智能体创建子智能体
self.agents[agent_name] = SubAgent(agent_name, self.log_id, self.start_time, self.config)
```

#### 6.3.2 调度关系

```python
# 主智能体调度子智能体
for agent_name in self.AGENT_NAMES:
    agent = self.agents[agent_name]
    agent.update(obs)  # 更新状态
    
    if agent._is_all_my_teams_ready_to_query():
        agent.thread = threading.Thread(target=thread_act, args=(agent, obs))
        agent.thread.start()  # 启动LLM查询
```

#### 6.3.3 执行关系

```python
# 子智能体执行动作
func_id, func_call = agent.get_func(obs)
return func_call  # 返回给主智能体执行
```

#### 6.3.4 通信关系

```python
# 智能体间通信
def communication_info_transmission(self):
    for receiver_name in self.AGENT_NAMES:
        receiver_agent = self.agents[receiver_name]
        for sender_name in self.AGENT_NAMES:
            sender_agent = self.agents[sender_name]
            # 传输消息
            receiver_agent.communication_message_i = receiver_agent.communicator.receive(
                receiver_agent.communication_message_i, 
                sender_agent.communication_message_o, 
                receiver_name, 
                sender_name
            )
```

---

## 7. 关键代码分析

### 7.1 观察转换流程

```python
# llm_pysc2_agent.py:367-396
def get_text_o(self, obs) -> str:
    text_o = ''
    
    # 使用观察转换器进行转换
    text_o = self.translator_o.translate(self)
    
    # 记录观察日志
    if self.name not in self.config.AGENTS_ALWAYS_DISABLE and self.enable:
        with open(self.log_dir_path + f"/{self.name}/o.txt", "a", newline='\n') as f:
            print(json.dumps({self.main_loop_step: text_o}), file=f)
    
    return text_o
```

**转换过程：**
1. **调用转换器**：使用`CombatGroupTranslatorO.translate()`
2. **组合信息**：游戏信息 + 单位信息 + 有效动作 + 上次动作 + 任务信息
3. **添加通信**：如果启用通信，添加通信信息
4. **记录日志**：保存到`o.txt`文件

### 7.2 LLM查询流程

```python
# llm_pysc2_agent.py:402-420
def get_text_a(self, text_o: str, base64_image=None) -> str:
    text_a = ''
    
    if self.config.LLM_SIMULATION_TIME > 0:
        # 模拟模式
        time.sleep(self.config.LLM_SIMULATION_TIME)
        if self.name not in self.config.AGENTS_ALWAYS_DISABLE and self.enable:
            with open(self.log_dir_path + f"/{self.name}/a_inp.txt", "r") as f:
                text_a = f.read()
    else:
        # 真实LLM查询
        if base64_image is None:
            text_a = self.client.query(text_o)  # 纯文本模式
        else:
            text_a = self.client.query(text_o, base64_image=base64_image)  # 多模态模式
    
    self.last_text_a_raw = text_a
    return text_a
```

**查询过程：**
1. **检查模式**：模拟模式或真实LLM模式
2. **构建提示**：系统提示词 + 当前观察
3. **调用API**：发送给LLM API
4. **记录响应**：保存原始响应

### 7.3 动作转换流程

```python
# llm_pysc2_agent.py:423-450
def get_func_a(self, raw_text_a) -> (list, dict):
    new_action_lists = []
    action_list_dict = {}
    processed_text_a = ''
    
    try:
        new_action_lists, action_list_dict, processed_text_a = self.translator_a.translate(raw_text_a)
    except Exception as e:
        logger.error(f"[ID {self.log_id}] Error in {self.name} get_func_a(): {e}")
    
    self.last_text_a_pro = processed_text_a
    
    # 记录各种日志
    if self.name not in self.config.AGENTS_ALWAYS_DISABLE and self.enable:
        # 记录原始响应
        with open(self.log_dir_path + f"/{self.name}/a_raw.txt", "a", newline='\n') as f:
            print(json.dumps({self.main_loop_step: raw_text_a}), file=f)
        
        # 记录处理后的动作
        with open(self.log_dir_path + f"/{self.name}/a_pro.txt", "a", newline='\n') as f:
            print(json.dumps({self.main_loop_step: processed_text_a}), file=f)
        
        # 记录成本统计
        with open(self.log_dir_path + f"/{self.name}/cost.txt", "a", newline='\n') as f:
            c = self.client
            client_cost = f"time={c.query_time:.2f}, ave_time={c.ave_query_time:.2f}, " \
                          f"token_in={c.query_token_in}, ave_token_in={c.ave_query_token_in:.2f}, " \
                          f"token_out={c.query_token_out}, ave_token_out = {c.ave_query_token_out:.2f}"
            print(json.dumps({self.main_loop_step: client_cost}), file=f)
    
    return new_action_lists, action_list_dict
```

**转换过程：**
1. **解析动作**：使用`DefaultTranslatorA.translate()`
2. **验证动作**：检查动作名称是否在允许列表中
3. **转换参数**：将LLM参数转换为PySC2参数
4. **记录日志**：保存原始响应、处理后动作、成本统计

### 7.4 函数执行流程

```python
# llm_pysc2_agent.py:494-520
def get_func(self, obs):
    if len(self.func_list) == 0:
        action = self.action_list.pop(0)
        action = llm_action.add_func_for_select_workers(self, obs, action)
        action = llm_action.add_func_for_train_and_research(self, obs, action)
        self.func_list = action['func']
        self.curr_action_name = action['name']
        self.curr_action_args = action['arg']
    
    func_id, func, llm_pysc2_args = self.func_list.pop(0)
    func_call = None
    
    pysc2_args = []
    if func_id in obs.observation.available_actions:
        func_valid = True
        pysc2_args = []
        
        if len(llm_pysc2_args) == 0:
            func_call = func()
        elif len(llm_pysc2_args) > 0:
            # 处理参数
            for i in range(len(llm_pysc2_args)):
                llm_pysc2_arg = llm_pysc2_args[i]
                # 参数验证和转换逻辑
                # ...
                pysc2_args.append(pysc2_arg)
            
            if func_valid is True and 'error' not in pysc2_args:
                if len(pysc2_args) == 3:
                    func_call = func(pysc2_args[0], pysc2_args[1], pysc2_args[2])
                elif len(pysc2_args) == 2:
                    func_call = func(pysc2_args[0], pysc2_args[1])
                elif len(pysc2_args) == 1:
                    func_call = func(pysc2_args[0])
            else:
                func_id, func_call = (0, actions.FUNCTIONS.no_op())
        else:
            func_id, func_call = (0, actions.FUNCTIONS.no_op())
    
    return func_id, func_call
```

**执行过程：**
1. **取出动作**：从`action_list`中取出动作
2. **设置函数列表**：将动作的函数列表赋给`func_list`
3. **取出函数**：从`func_list`中取出PySC2函数
4. **验证函数**：检查函数ID是否在可用动作中
5. **处理参数**：验证和转换函数参数
6. **创建调用**：创建PySC2函数调用
7. **返回调用**：返回给主智能体执行

---

## 8. 实际运行示例

### 8.1 启动命令

```bash
python -m pysc2.bin.agent --map wzsy_te --agent_race protoss --parallel 1 --agent llm_pysc2.bin.experiment_llm_36strat.MainAgentTSSPysc2 --render
```

### 8.2 运行流程示例

#### 8.2.1 初始化阶段

```
[ID 1] INFO:root:MainAgent initialized
[ID 1] INFO:root:CombatGroup1 LLMAgent initialized
[ID 1] INFO:root:CombatGroup6 LLMAgent initialized
[ID 1] INFO:root:Commander LLMAgent initialized
[ID 1] INFO:root:Developer LLMAgent initialized
```

#### 8.2.2 观察收集阶段

```
[ID 1] INFO:root:7.1 Agent CombatGroup1: query status
[ID 1] INFO:root:7.1.2 Agent CombatGroup1: Obs prepared, try calling LLM api
[ID 1] SUCCESS:root:[ID 1] CombatGroup1 Start calling llm api!
```

#### 8.2.3 LLM查询阶段

```
[ID 1] SUCCESS:root:[ID 1] CombatGroup1 Get llm response!
[ID 1] INFO:root:7.2 All Agent waiting for response
```

#### 8.2.4 动作执行阶段

```
[ID 1] INFO:root:7.3.1 Agent CombatGroup1: executing status
[ID 1] SUCCESS:root:7.4 Agent CombatGroup1 Func Call: select_point(select, [42, 42])
[ID 1] SUCCESS:root:7.4 Agent CombatGroup1 Func Call: Train_Probe_quick(now)
[ID 1] SUCCESS:root:7.4 Agent CombatGroup1 Func Call: Rally_Workers_screen(now, [42, 42])
[ID 1] SUCCESS:root:7.4 Agent CombatGroup1 Func Call: Effect_ChronoBoostEnergyCost_screen(now, [42, 42])
```

### 8.3 日志文件示例

#### 8.3.1 观察日志 (`o.txt`)

```json
{"1": "Game Info:\n\tTime: 0:05\n\tMinerals: 50\n\tVespene: 0\n\nTeam Stalker-1 Info:\n\tTeam minimap position: [42, 42]\n\tControlled units: 2 Stalkers\n\tHealth: 160/160 (100%)\n\tEnergy: 0\n\nValid Actions:\n\tTeam Stalker-1 Valid Actions:\n\t\tMove_Screen([x, y])\n\t\tAttack_Unit(0x...)\n\nLast Step Actions:\n\tTeam Stalker-1:\n\t\t<Move_Screen([40, 60])>\n\nTasks:\n\tTeam Stalker-1' task: use Create something from nothing to attack the enemy base"}
```

#### 8.3.2 LLM原始响应 (`a_raw.txt`)

```json
{"1": "Analysis:\n  We are controlling a team called Stalker-1, consisting of 2 Stalkers. Our task is to attack the enemy base using the stratagem \"Create something from nothing\". We need to deceive the enemy with an illusion of a strong force.\n\nActions:\n  Team Stalker-1:\n    <Move_Screen([40, 60])>\n    <Attack_Unit(0x101100001)>\n\nCommunications:\n  <MessageTo(CombatGroup6, '''Prepare to attack the enemy base. We will create an illusion of a strong force to deceive the enemy.''')>"}
```

#### 8.3.3 动作执行历史 (`a_his.txt`)

```json
{"1": "CombatGroup1;   loop1;   step1;   [Valid]  Move_Screen [40, 60]"}
{"2": "CombatGroup1;   loop1;   step2;   [Valid]  Attack_Unit 0x101100001"}
```

#### 8.3.4 通信输入 (`c_inp.txt`)

```json
{"0": ""}
{"1": "\n\nCommunication information:\n\tFrom CombatGroup6: \n\t\tPrepare to attack the enemy base. We will create an illusion of a strong force to deceive the enemy."}
```

#### 8.3.5 成本统计 (`cost.txt`)

```json
{"1": "time=2.34, ave_time=2.34, token_in=1250, ave_token_in=1250.0, token_out=180, ave_token_out=180.0"}
```

---

## 9. 总结

LLM-PySC2项目是一个复杂而完整的多智能体决策系统，具有以下特点：

### 9.1 系统架构特点

1. **分层设计**：MainAgent负责协调，SubAgent负责执行
2. **多智能体协作**：支持多个智能体同时协作
3. **异步执行**：多线程并发LLM查询
4. **配置驱动**：通过配置文件控制行为

### 9.2 技术特点

1. **多模态支持**：支持文本和图像观察
2. **多轮对话**：保持游戏上下文，支持连续决策
3. **完整日志**：记录观察、决策、执行、通信全过程
4. **错误处理**：完善的异常处理和重试机制

### 9.3 应用特点

1. **策略多样性**：支持三十六计等复杂策略
2. **实时性**：支持实时游戏决策
3. **可扩展性**：易于添加新的智能体和策略
4. **可调试性**：完整的日志系统便于调试和分析

### 9.4 关键创新

1. **LLM游戏决策**：将大语言模型应用于实时游戏决策
2. **多智能体协作**：实现智能体间的通信和协作
3. **上下文保持**：通过多轮对话保持游戏状态
4. **动作验证**：确保LLM生成的动作在游戏中的有效性

这个项目展示了如何将大语言模型与实时游戏环境结合，实现复杂的多智能体协作决策，为AI游戏和智能体研究提供了有价值的参考。
