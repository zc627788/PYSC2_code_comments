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
LLM客户端核心模块 - 负责与各种大语言模型API进行交互

主要功能：
1. 支持多种主流LLM模型（GPT、Claude、Llama、GLM、DeepSeek、Gemini等）
2. 统一的消息格式和查询接口
3. 多模态支持（文本+图像）
4. 重试机制和错误处理
5. 性能统计和监控

作者：LLM-PySC2团队
"""

import google.generativeai as genai
from llamaapi import LlamaAPI
from zhipuai import ZhipuAI
import openai

from loguru import logger
import threading
import random
import time
# import json


def gpt_query_runtime(self, ):
  """
  GPT系列模型的查询运行时函数
  
  功能：
  - 调用OpenAI GPT API进行文本生成
  - 统计输入和输出的token数量
  - 返回LLM响应内容
  
  Args:
    self: 客户端实例，包含模型配置和消息
  
  Returns:
    无返回值，直接设置self.llm_response
  """
  llm_response = openai.ChatCompletion.create(
    model=self.model_name,
    messages=self.messages,
    temperature=self.temperature
  )
  # 统计token使用量
  self.query_token_in = llm_response["usage"]["prompt_tokens"]
  self.query_token_out = llm_response["usage"]["completion_tokens"]
  # 提取LLM回复内容
  self.llm_response = llm_response["choices"][0]["message"]["content"]

def claude_query_runtime(self, ):
  """
  Claude系列模型的查询运行时函数
  
  功能：
  - 调用Anthropic Claude API进行文本生成
  - 统计token使用量
  - 返回LLM响应内容
  
  注意：Claude使用OpenAI兼容的API接口
  """
  llm_response = openai.ChatCompletion.create(
    model=self.model_name,
    messages=self.messages,
    temperature=self.temperature
  )
  # Claude API返回格式略有不同
  self.query_token_in = llm_response.usage.prompt_tokens
  self.query_token_out = llm_response.usage.completion_tokens
  self.llm_response = llm_response.choices[0].message.content

def llama_query_runtime(self, ):
  """
  Llama系列模型的查询运行时函数
  
  功能：
  - 调用LlamaAPI进行文本生成
  - 处理可能的token统计缺失情况
  - 返回LLM响应内容
  
  注意：LlamaAPI可能不返回usage信息
  """
  llm_response = self.client.run({
    'model': self.model_name,
    'messages': self.messages,
    'temperature': self.temperature,}
  ).json()
  # 安全获取token统计，如果不存在则设为0
  self.query_token_in = llm_response["usage"]["prompt_tokens"] if 'usage' in llm_response.keys() else 0
  self.query_token_out = llm_response["usage"]["completion_tokens"] if 'usage' in llm_response.keys() else 0
  self.llm_response = llm_response['choices'][0]["message"]["content"]

def glm_query_runtime(self, ):
  """
  智谱AI GLM系列模型的查询运行时函数
  
  功能：
  - 调用智谱AI GLM API进行文本生成
  - 注意：GLM API不返回token统计信息
  
  注意：智谱AI的API格式与其他提供商略有不同
  """
  llm_response = self.client.chat.completions.create(
    model=self.model_name,  # 填写需要调用的模型名称
    messages=self.messages,
    temperature=self.temperature
  )
  # GLM API不提供token统计，设为0
  self.query_token_in = 0
  self.query_token_out = 0
  self.llm_response = llm_response.choices[0].message.content

def glm4v_query_runtime(self, ):
  """
  智谱AI GLM-4V多模态模型的查询运行时函数
  
  功能：
  - 调用智谱AI GLM-4V API进行多模态生成（文本+图像）
  - 支持图像输入的多模态对话
  - 提供token统计信息
  
  注意：GLM-4V是支持视觉的模型版本
  """
  llm_response = self.client.chat.completions.create(
    model=self.model_name,  # 填写需要调用的模型名称
    messages=self.messages,
    temperature=self.temperature
  )
  # GLM-4V提供token统计
  self.query_token_in = llm_response.usage.prompt_tokens
  self.query_token_out = llm_response.usage.completion_tokens
  self.llm_response = llm_response.choices[0].message.content

def deepseek_query_runtime(self, ):
    """
    DeepSeek系列模型的查询运行时函数
    
    功能：
    - 调用DeepSeek API进行文本生成
    - 包含完整的错误处理机制
    - 安全获取token统计信息
    
    注意：DeepSeek使用OpenAI兼容的API格式
    """
    try:
        llm_response = openai.ChatCompletion.create(
            model=self.model_name,
            messages=self.messages,
            temperature=self.temperature
        )
        # 安全获取token统计，如果不存在则设为0
        self.query_token_in = llm_response.usage.prompt_tokens if hasattr(llm_response, 'usage') else 0
        self.query_token_out = llm_response.usage.completion_tokens if hasattr(llm_response, 'usage') else 0
        self.llm_response = llm_response.choices[0].message.content
    except Exception as e:
        logger.error(f"[ID {self.log_id}] {self.agent_name} Error in deepseek_query_runtime: {str(e)}")
        raise

def gemini_query_runtime(self, ):
    """
    Google Gemini系列模型的查询运行时函数
    
    功能：
    - 调用Google Gemini API进行文本生成
    - 支持多模态输入（文本+图像）
    - 使用Google的生成配置
    
    注意：Gemini使用特殊的API格式和消息结构
    """
    llm_response = self.client.generate_content(
        self.messages,
        generation_config={
            "temperature": self.temperature
        }
    )
    # Gemini API不提供详细的token统计
    self.llm_response = llm_response.text


# def qwen2_query_runtime(self, ):
#   llm_response = openai.ChatCompletion.create(
#     model=self.model_name,  # 填写需要调用的模型名称
#     messages=self.messages,
#     temperature=self.temperature
#   )
#   self.query_token_in = llm_response.usage.prompt_tokens
#   self.query_token_out = llm_response.usage.completion_tokens
#   self.llm_response = llm_response.choices[0].message.content

class GptClient:
  """
  GPT客户端基础类 - 所有LLM客户端的父类
  
  功能：
  1. 统一的LLM查询接口
  2. 多模态消息支持（文本+图像）
  3. 重试机制和错误处理
  4. 性能统计和监控
  5. 异步查询支持
  
  支持的模型：GPT系列、Claude系列、Llama系列等
  """

  def __init__(self, name, log_id, config):
    """
    初始化GPT客户端
    
    Args:
      name (str): 智能体名称
      log_id (int): 日志ID，用于区分不同的实验实例
      config: 配置对象，包含模型参数和API设置
    """

    # 从配置中获取模型参数
    self.model_name = config.AGENTS[name]['llm']['model_name']
    self.api_base = config.AGENTS[name]['llm']['api_base']
    self.api_key = config.AGENTS[name]['llm']['api_key']
    self.temperature = config.temperature

    # 设置OpenAI API配置
    openai.api_base = self.api_base
    openai.api_key = self.api_key

    # 基础属性
    self.agent_name = name
    self.log_id = log_id
    self.config = config
    
    # 消息相关属性
    self.system_prompt = ''        # 系统提示词
    self.example_i_prompt = ''     # 示例输入
    self.example_o_prompt = ''     # 示例输出
    self.messages = []             # 消息列表
    self.llm_response = None       # LLM响应
    
    # 设置查询运行时函数
    self.query_runtime = gpt_query_runtime
    
    # 初始化日志
    if 'gpt' in self.model_name or self.model_name == 'default':
      logger.info(f"[ID {self.log_id}] {self.agent_name} {self.model_name} GptClient initialized")

    # 统计相关属性
    self.num_query = 0              # 查询次数
    self.query_time = 0            # 单次查询时间
    self.query_token_in = 0        # 单次输入token数
    self.query_token_out = 0       # 单次输出token数
    self.total_query_time = 0      # 总查询时间
    self.total_query_token_in = 0  # 总输入token数
    self.total_query_token_out = 0 # 总输出token数
    self.ave_query_time = 0        # 平均查询时间
    self.ave_query_token_in = 0    # 平均输入token数
    self.ave_query_token_out = 0   # 平均输出token数

  def wrap_message(self,  obs_prompt, base64_image):
    """
    包装消息格式，支持文本和图像输入
    
    功能：
    1. 根据模型是否支持视觉选择消息格式
    2. 处理多模态消息结构
    3. 包含系统提示词和示例
    
    Args:
      obs_prompt (str): 观察提示词（游戏状态描述）
      base64_image (str): Base64编码的图像数据，可选
    """
    # 检查模型是否支持图像输入
    if (base64_image is not None) and (self.model_name not in vision_model_names):
      logger.warning(f"[ID {self.log_id}] {self.agent_name} {self.model_name}: Model do not accept img, img discarded")
    if (base64_image is None) and (self.model_name in vision_model_names):
      logger.warning(f"[ID {self.log_id}] {self.agent_name} {self.model_name}: Vision available but img disabled")

    if (base64_image is None) or (self.model_name not in vision_model_names):
      # 纯文本消息格式
      self.messages = [
        {"role": "system", "content": self.system_prompt},
        {"role": "user", "content": self.example_i_prompt},
        {"role": "assistant", "content": self.example_o_prompt},
        {"role": "user", "content": obs_prompt}
      ]
    else:
      # 多模态消息格式（文本+图像）
      self.messages = [
        {"role": "system", "content": self.system_prompt},
        {"role": "user", "content": self.example_i_prompt},
        {"role": "assistant", "content": self.example_o_prompt},
        # TODO: Incorrect img usage, to be update in recent commit
        {"role": "user", "content": [
          {"type": "text", "text": obs_prompt},   # obs_prompt
          {"type": "image_url", "image_url": {
            "url": f"data:image/png;base64,{base64_image}"
          }}
        ]},
      ]

  def query(self, obs_prompt, base64_image=None):
    """
    核心查询方法 - 向LLM发送请求并获取回复
    
    功能：
    1. 包装消息格式
    2. 异步查询LLM API
    3. 重试机制和错误处理
    4. 超时控制
    5. 性能统计
    
    Args:
      obs_prompt (str): 观察提示词（游戏状态描述）
      base64_image (str): Base64编码的图像数据，可选
      
    Returns:
      str: LLM的回复内容
    """
    # 重置消息列表
    self.wrap_message(obs_prompt, base64_image)

    # 尝试发送请求并获取回复
    max_retries = self.config.MAX_LLM_QUERY_TIMES
    for retries in range(max_retries):
      try:
        logger.success(f"[ID {self.log_id}] {self.agent_name} Start calling llm api!")
        logger.debug(f"[ID {self.log_id}] {self.agent_name} input prompt: \n{obs_prompt}")

        # 使用多线程异步查询，避免阻塞主线程
        self.thread = threading.Thread(target=self.query_runtime, args=(self,))#保留"，"
        self.thread.start()

        # 超时控制 - 防止查询无限等待
        query_start_time = float(time.time())
        while not isinstance(self.llm_response, str):
          time.sleep(0.1)
          if float(time.time()) - query_start_time > self.config.MAX_LLM_RUNTIME_ERROR_TIME:
            logger.error(f"[ID {self.log_id}] {self.agent_name} LLM query runtime error")
            raise RuntimeError(f"{self.agent_name} LLM query runtime error")

        # 成功获取回复，更新统计信息
        if isinstance(self.llm_response, str):
          self.num_query += 1
          self.query_time = float(time.time()) - query_start_time
          self.total_query_time += self.query_time
          self.total_query_token_in += self.query_token_in
          self.total_query_token_out += self.query_token_out
          self.ave_query_time = self.total_query_time / self.num_query
          self.ave_query_token_in = self.total_query_token_in / self.num_query
          self.ave_query_token_out = self.total_query_token_out / self.num_query

        answer = self.llm_response
        logger.success(f"[ID {self.log_id}] {self.agent_name} Get llm response!")
        logger.debug(f"[ID {self.log_id}] {self.agent_name} llm response: \n{answer}")
        self.llm_response = None  # 重置响应，准备下次查询

        return answer
        
      except Exception as e:
        # 输出错误信息
        logger.error(f"[ID {self.log_id}] {self.agent_name} Error when calling the OpenAI API: {e}")

        # 如果达到最大尝试次数，返回错误回复
        if retries >= max_retries - 1:
          logger.error \
            (f"[ID {self.log_id}] {self.agent_name} Maximum number of retries reached. The OpenAI API is not responding.")
          return "I'm sorry, but I am unable to provide a response at this time due to technical difficulties."

        # 指数退避重试策略 - 避免频繁重试
        sleep_time = min((2 ** retries) + random.random(), 8 + random.random())
        logger.info(f"[ID {self.log_id}] {self.agent_name} Waiting for {sleep_time} seconds before retrying...")
        time.sleep(sleep_time)

    logger.error(f"[ID {self.log_id}] {self.agent_name} Can not get llm response after try {max_retries} times!")
    return f'[ID {self.log_id}] {self.agent_name} Can not get llm response after try {max_retries} times!'

class O1Client(GptClient):
  """
  OpenAI O1系列专用客户端
  
  功能：
  - 专门处理OpenAI O1系列模型（o1-mini, o1-preview）
  - 固定temperature=1（O1系列只支持默认值）
  - 特殊的消息格式处理
  
  注意：O1系列是OpenAI的推理优化模型
  """
  def __init__(self, name, log_id, config):
    super(O1Client, self).__init__(name, log_id, config)
    self.query_runtime = gpt_query_runtime
    self.temperature = 1  # Only the default (1) value is supported.
    self.client = openai
    logger.info(f"[ID {self.log_id}] {self.agent_name} {self.model_name} O1Client initialized")

  def wrap_message(self, obs_prompt, base64_image):
    """
    O1系列的特殊消息格式
    
    注意：O1系列使用不同的消息结构，不包含system role
    """
    super().wrap_message(obs_prompt, base64_image)
    # O1系列的特殊消息格式
    self.messages = [
      {"role": "user", "content": self.system_prompt},
      {"role": "assistant", "content": "Understand."},
      {"role": "user", "content": self.example_i_prompt},
      {"role": "assistant", "content": self.example_o_prompt},
      {"role": "user", "content": obs_prompt}
    ]


class ClaudeClient(GptClient):
  """
  Anthropic Claude系列专用客户端
  
  功能：
  - 专门处理Anthropic Claude系列模型
  - 使用OpenAI兼容的API接口
  - 支持Claude-3系列模型
  
  注意：Claude使用OpenAI兼容的API格式
  """
  def __init__(self, name, log_id, config):
    super(ClaudeClient, self).__init__(name, log_id, config)
    self.query_runtime = claude_query_runtime
    self.client = openai
    logger.info(f"[ID {self.log_id}] {self.agent_name} {self.model_name} ClaudeClient initialized")

class LlamaClient(GptClient):
  """
  Meta Llama系列专用客户端
  
  功能：
  - 专门处理Meta Llama系列模型
  - 使用LlamaAPI库进行查询
  - 支持Llama3系列模型
  
  注意：LlamaAPI可能不返回usage统计信息
  """
  def __init__(self, name, log_id, config):
    super(LlamaClient, self).__init__(name, log_id, config)
    self.query_runtime = llama_query_runtime
    self.client = LlamaAPI(self.api_key, hostname=self.api_base)
    logger.info(f"[ID {self.log_id}] {self.agent_name} {self.model_name} LlamaClient initialized")

class GlmClient(GptClient):
  """
  智谱AI GLM系列专用客户端
  
  功能：
  - 专门处理智谱AI GLM系列模型
  - 使用ZhipuAI库进行查询
  - 支持GLM-4系列模型
  
  注意：GLM API不提供token统计信息
  """
  def __init__(self, name, log_id, config):
    super(GlmClient, self).__init__(name, log_id, config)
    self.query_runtime = glm_query_runtime
    self.client = ZhipuAI(api_key=self.api_key)
    logger.info(f"[ID {self.log_id}] {self.agent_name} {self.model_name} GlmClient initialized")

class DeepSeekClient(GptClient):
    """
    DeepSeek系列专用客户端
    
    功能：
    - 专门处理DeepSeek系列模型
    - 使用OpenAI兼容的API接口
    - 支持DeepSeek-Chat、DeepSeek-R1等模型
    
    注意：DeepSeek使用OpenAI兼容的API格式
    """
    def __init__(self, name, log_id, config):
        super(DeepSeekClient, self).__init__(name, log_id, config)
        self.query_runtime = deepseek_query_runtime
        self.client = openai

class GeminiClient(GptClient):
    """
    Google Gemini系列专用客户端
    
    功能：
    - 专门处理Google Gemini系列模型
    - 使用Google Generative AI库
    - 支持多模态输入（文本+图像）
    - 自定义消息格式处理
    
    注意：Gemini使用特殊的API格式和消息结构
    """
    def __init__(self, name, log_id, config):
        super(GeminiClient, self).__init__(name, log_id, config)
        self.query_runtime = gemini_query_runtime
        self.client = genai.GenerativeModel(model_name=self.model_name)
        genai.configure(api_key=self.api_key)
        logger.info(f"[ID {self.log_id}] {self.agent_name} {self.model_name} GeminiClient initialized")

    def wrap_message(self, obs_prompt, base64_image):
        """
        Gemini系列的特殊消息格式
        
        注意：Gemini使用不同的消息结构，支持多模态输入
        """
        if base64_image is None:
            self.messages = obs_prompt
        else:
            self.messages = [
                obs_prompt,
                {"mime_type": "image/png", "data": base64_image}
            ]

# class QWen2Client(GptClient):
#   def __init__(self, name, log_id, config):
#     super(QWen2Client, self).__init__(name, log_id, config)
#     self.query_runtime = qwen2_query_runtime
#     self.client = openai

# ==================== 模型配置和工厂 ====================

# 支持视觉（图像输入）的模型列表
# 这些模型可以处理文本+图像的混合输入
vision_model_names = [
  'gpt-4o', 'gpt-4-1106-vision-preview', 'gpt-4v-1106', 'gpt-4v-0409',
  'glm-4v', 'glm-4v-plus','gemini-1.5-flash',
]

# 支持视频输入的模型列表（目前为空，未来可能扩展）
video_model_names = []

# 模型工厂字典 - 根据模型名称自动选择对应的客户端类
# 这是工厂模式的实现，用于动态创建合适的LLM客户端
FACTORY = {
  # OpenAI GPT系列
  'default': GptClient,
  'gpt-3.5-turbo': GptClient,
  'gpt-3.5-turbo-1106': GptClient,
  'gpt-4o': GptClient,
  'gpt-4o-mini': GptClient,
  'gpt-4-turbo': GptClient,

  # OpenAI O1系列（推理优化模型）
  'o1-mini': O1Client,
  'o1-preview': O1Client,

  # Anthropic Claude系列
  'claude-3-opus': ClaudeClient,
  'claude-3-haiku': ClaudeClient,
  'claude-3-sonnet': ClaudeClient,

  # Meta Llama系列
  'llama3-8b': LlamaClient,
  'llama3-70b': LlamaClient,
  'llama3.1-8b': LlamaClient,
  'llama3.1-70b': LlamaClient,
  'llama3.1-405b': LlamaClient,

  # 智谱AI GLM系列
  'glm-4': GlmClient,
  'glm-4-plus': GlmClient,
  'glm-4-air': GlmClient,
  'glm-4-airx': GlmClient,
  'glm-4-flash': GlmClient,
  'glm-4-flashx': GlmClient,

  # DeepSeek系列
  'deepseek-chat': DeepSeekClient,
  'deepseek-reasoner': DeepSeekClient,
  'deepseek-r1': DeepSeekClient,
  'deepseek-v3': DeepSeekClient,
  'deepseek-r1-distill-llama-8b': DeepSeekClient,
  'deepseek-r1-distill-qwen-1.5b': DeepSeekClient,
  'deepseek-r1-distill-qwen-32b': DeepSeekClient,

  # Google Gemini系列
  'gemini-1.5-flash': GeminiClient,
  'gemini-2.5-pro': GeminiClient,

  # 注释掉的模型（可能暂时不支持或正在开发中）
  # 'glm-4v': GlmClient,
  # 'glm-4v-plus': GlmClient,
  # 'qwen2.5-7b-instruct': QWen2Client,
  # 'qwen2:72b': QWen2Client,  # debug for LAN LLM
}
