import logging
import asyncio
from typing import Dict
import sys
import time
from taskexecuter import TaskExecuter
from config import Config
from llmClient import LLMClient
from agent import Agent
from task_prompt import *
# -----------------------------------------------------------------------------
# Logging Configuration
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),  # Console output
        logging.FileHandler("app2.log", encoding="utf-8")  # Optional file output
    ]
)
logger = logging.getLogger(__name__) 


def load_agents(memory_capacity: int = None) -> Dict[int, Agent]:
    """
    Instantiate a set of Agents based on Config model settings.

    :param memory_capacity: Optional cap for each agent's long-term memory.
    :return: A dict mapping agent IDs to Agent instances.
    """
    agents: Dict[int, Agent] = {}
    # Collect config attributes starting with GPT_MODEL
    model_attrs = [attr for attr in dir(Config) if attr.startswith("GPT_MODEL")]
    model_attrs.sort(key=lambda x: (len(x), x))

    for idx, attr in enumerate(model_attrs):
        model_name = getattr(Config, attr)
        logger.info(f"Initializing Agent {idx} with model '{model_name}'")
        client = LLMClient(
            provider="openai",
            api_key=Config.OPENAI_API_KEY,
            model=model_name,
            temperature=Config.TEMPERATURE,
        )
        agent = Agent(
            llm_client=client,
            id=idx,
            memory_capacity=memory_capacity
        )
        agents[idx] = agent
    return agents


async def main():
    # Ensure stdout uses UTF-8 encoding
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

    # Load agents
    agents = load_agents(memory_capacity=Config.MEMORY_CAPACITY if hasattr(Config, 'MEMORY_CAPACITY') else None)
    logger.info(f"Loaded agents: {list(agents.keys())}")



    # Create TaskExecuter with desired parameters
    executor = TaskExecuter(
        agents=agents,
        current_task=quiz_platform_metroidvania,
        max_rounds=30,
        max_recursion_depth=10
    )

    # Execute tasks and gather final result
    start_time = time.time()
    await executor.branching_recursive_execution(agent_ids=list(agents.keys()))
    result = agents[0].memory.get_long_str()
    # Save the result to file
    output_file = "example2.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result or "")
    logger.info(f"Wrote final result to {output_file}")

    elapsed_time = time.time() - start_time
    logger.info(f"Elapsed time: {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    asyncio.run(main())
