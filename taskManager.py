import json
import logging
import re
from config import Config
from task import Task
from llmClient import LLMClient  # 替换原来的GPTClient
import prompt
import asyncio
# -----------------------------------------------------------------------------
# Configuration and Logging Setup
# -----------------------------------------------------------------------------
# 创建 logger
logger = logging.getLogger(__name__)



# -----------------------------------------------------------------------------
# Task manager
# -----------------------------------------------------------------------------

class TaskManager:
    """使用LLM优化和更新工作流的类"""

    def __init__(self, objective: str, current_task:str):
        self.objective = objective
        self.Task: Task | None = None
        self.system_prompt = prompt.WORKFLOW_DECOMPOSER_PROMPT
        self.current_task=current_task
        # 定义多个LLM客户端配置
        self.llm_configs = [
            {"provider": "openai", "model": Config.GPT_MODEL},  # 主客户端
            {"provider": "openrouter", "model": "meta-llama/llama-3.1-8b-instruct:free"},
            {"provider": "openrouter", "model": "mistralai/mistral-7b-instruct:free"}
        ]

        self.main_client = LLMClient(
            provider=self.llm_configs[0]["provider"],
            model="o4-mini",
            temperature=Config.TEMPERATURE
        )

    async def task_decomposer(self) -> dict:
        """分解为子任务"""
        user_content = f"##  ## The task need to be splited: \n{self.current_task}\n\n"
        logger.info(f"SPLITING>>>[DEBUG] {user_content}\n\n ")
        # 构造消息队列
        messages = [
            {'role': 'system', 'content': self.system_prompt},
            {'role': 'user', 'content': user_content}
        ]

        # 调用主客户端
        try:
            response = await self.main_client.a_chat_completion(messages)
   
            logger.info(f"LLM Response: {response}")

            # 验证是否是有效的JSON
            try:
                return json.loads(response) 
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON format in response: {e}\nResponse: {response}")
                raise ValueError("The response does not contain valid JSON") from e
        except Exception as e:
            logger.error(f"Error in task_decomposer: {e}")
            raise

