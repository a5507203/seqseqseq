import logging
import asyncio
from typing import Dict
import sys
import time
import argparse
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
        logging.FileHandler("app.log", encoding="utf-8")  # Optional file output
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


def get_task_by_name(task_name: str) -> str:
    """
    Get task prompt by name from task_prompt.py
    """
    available_tasks = {
        'mle_lecture': mle_lecture,
        'nips_website': nips_website, 
        'pac_tank': pac_tank,
        'puzzle_game_electrical_circuits': puzzle_game_electrical_circuits,
        'quiz_platform_metroidvania': quiz_platform_metroidvania,
        'snake_chess': snake_chess,
        'task_manager_rpg': task_manager_rpg,
        'tetris_bjeweled': tetris_bjeweled,
        'travel_plan': travel_plan
    }
    
    if task_name not in available_tasks:
        raise ValueError(f"Task '{task_name}' not found. Available tasks: {list(available_tasks.keys())}")
    
    return available_tasks[task_name]


async def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run multi-agent task execution')
    parser.add_argument('--task', type=str, default='pac_tank',
                       help='Task name to execute (default: pac_tank)')
    parser.add_argument('--max_rounds', type=int, default=30,
                       help='Maximum number of rounds (default: 30)')
    parser.add_argument('--output', type=str, default='example.txt',
                       help='Output file name (default: example.txt)')
    parser.add_argument('--list-tasks', action='store_true',
                       help='List all available tasks')
    
    args = parser.parse_args()
    
    # List available tasks if requested
    if args.list_tasks:
        available_tasks = ['mle_lecture', 'nips_website', 'pac_tank', 'puzzle_game_electrical_circuits',
                          'quiz_platform_metroidvania', 'snake_chess', 'task_manager_rpg', 
                          'tetris_bjeweled', 'travel_plan']
        print("Available tasks:")
        for task in available_tasks:
            print(f"  - {task}")
        return
    
    # Ensure stdout uses UTF-8 encoding
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

    # Load agents
    agents = load_agents(memory_capacity=Config.MEMORY_CAPACITY if hasattr(Config, 'MEMORY_CAPACITY') else None)
    logger.info(f"Loaded agents: {list(agents.keys())}")
    
    # Get the task prompt
    try:
        current_task = get_task_by_name(args.task)
        logger.info(f"Running task: {args.task}")
    except ValueError as e:
        logger.error(str(e))
        return

    # Create TaskExecuter with desired parameters
    executor = TaskExecuter(
        agents=agents,
        current_task=current_task,
        max_rounds=args.max_rounds
    )

    # Execute tasks and gather final result
    start_time = time.time()
    await executor.run(agent_ids=list(agents.keys()))
    result = agents[0].memory.get_all()
    # Save the result to file
    output_file = args.output
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result or "")
    logger.info(f"Wrote final result to {output_file}")

    elapsed_time = time.time() - start_time
    logger.info(f"Elapsed time: {elapsed_time:.2f} seconds")
    logger.info(f"Task '{args.task}' completed successfully")


if __name__ == "__main__":
    asyncio.run(main())
