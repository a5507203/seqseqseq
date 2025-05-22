import logging
from typing import Dict, List, Set, Tuple, Any, Coroutine

import prompt
from config import Config
from llmClient import LLMClient

# -----------------------------------------------------------------------------
# Configuration and Logging Setup
# -----------------------------------------------------------------------------
# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Set log level

# Define log format
formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Output to console
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Output to file
file_handler = logging.FileHandler("app.log", mode="a", encoding="utf-8")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# -----------------------------------------------------------------------------
# Utils functions
# -----------------------------------------------------------------------------

AGENT_CONFIGS = [
    {"provider": "openai", "model": Config.GPT_MODEL},
    {"provider": "openai", "model": Config.GPT_MODEL1},
    {"provider": "openai", "model": Config.GPT_MODEL2}
]

async def cross_validate(current_task: str, overall_task: str, agent_id: int,
                        another_agent_result: str, current_result: str,
                        indent: str = "") -> bool:
    """Perform cross-validation between agent results."""
    config = AGENT_CONFIGS[agent_id % len(AGENT_CONFIGS)]

    # logger.info(f"another_agent_result: {another_agent_result}")
    # logger.info(f"current_result: {current_result}")

    if not another_agent_result:
        return False

    client = LLMClient(
        provider=config["provider"],
        model=config["model"]
    )

    evaluation_prompt = f"""
### overall objective
{overall_task}

### current task description 
{current_task}

### aggregated previous output
{current_result}

### current output fragment
{another_agent_result}
    """

    try:
        messages = [
            {"role": "system", "content": prompt.OBJECTIVE_VALIDATOR_PROMPT},
            {"role": "user", "content": evaluation_prompt}
        ]

        evaluation = await client.a_chat_completion(
            messages=messages,
            max_tokens=16
        )
    
        result = evaluation.strip().lower()
        return "false" not in result and "true" in result

    except Exception as e:
        logger.error(f"{indent}Validation by Agent {agent_id} failed: {str(e)}")
        return ""





async def validate_results(current_task: str, overall_task: str, results: Dict[int, str],
                          current_results: Dict[int, str], agent_ids: Set[int],indent: str = "") -> Dict[int, bool]:
    """Validate results between agents using cross-validation."""
    validation_tasks = []
    validation_map = {}
    for validator_id in list(agent_ids):
        for validatee_id, validatee_result in results.items():
            # Skip self-validation and completed agents validating themselves
            if validator_id == validatee_id:
                continue
            task = asyncio.create_task(
                cross_validate(
                    current_task=current_task,
                    overall_task=overall_task,
                    agent_id=validator_id,
                    another_agent_result=validatee_result, # validatee 新生成的结果
                    current_result=current_results[validatee_id],  # validatee的累积结果
                    indent=indent
                )
            )

            logger.info(f"validation_tasks: {validator_id}, {validatee_id}")
            validation_tasks.append((validator_id, validatee_id, task))

    if not validation_tasks:
        return {}

    validation_results = await asyncio.gather(
        *[task for _, _, task in validation_tasks],
        return_exceptions=False
    ) # True, False, True

    # Build validation map
    '''
    validation_map = {
        2: [True, False, True]  # 来自agent1,3,4的验证结果
    }
    '''
    for (validator_id, validatee_id, _), result in zip(validation_tasks, validation_results):
        if validatee_id not in validation_map:
            validation_map[validatee_id] = []
        validation_map[validatee_id].append(result)

    # Convert to majority vote
    '''
    validation_map = {
        2: True  # 原始列表被替换为最终布尔值
    }
    '''
    return {
        validatee_id: sum(results) > len(results) / 2
        for validatee_id, results in validation_map.items()
    }




async def generate_agent_results(current_task: str, overall_task: str,
                                 agent_ids: List[int], current_results: Dict[int, str],
                                 indent: str = "") -> tuple[dict[Any, dict], dict[Any, Any]]:
    """Generate results from multiple agents in parallel using asyncio.create_task."""
    tasks = []
    for agent_id in agent_ids:
        config = AGENT_CONFIGS[agent_id % len(AGENT_CONFIGS)]
        client = LLMClient(
            provider=config["provider"],
            model=config["model"],
            temperature=0.7
        )

        messages = [
            {"role": "system", "content": prompt.TASK_EXECUTION_PROMPT},
            {"role": "user", "content": f"""
## overall objective
{overall_task}

## current Subtask
{current_task}

## prior output
{current_results.get(agent_id, "")}
            """}
        ]

        # Create task for each agent instead of using gather directly
        task = asyncio.create_task(
            generate_single_result(client, messages, agent_id, indent)
        )
        tasks.append(task)

    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks, return_exceptions=False)

    return process_generation_results(results)


import re

async def generate_single_result(client: LLMClient, messages: List[Dict],
                                 agent_id: int, indent: str = "") -> tuple[int, None, Exception, None] | tuple[
    int, Any, None, Any] | tuple[int, None, ValueError, None]:
    """Generate result from a single agent."""
    try:
        result = await client.a_chat_completion_json(
            messages=messages
        )
        try:
            logger.info(f"----current response segment by agent {agent_id} :\n{result}")
            # Extract JSON content between ```json and ``` markers if they exist
                   # 1. Remove any leading ``` or ```json
            clean = re.sub(r"^```(?:json)?\s*", "", result)

            # 2. Remove any trailing ```
            clean = re.sub(r"```$", "", clean).strip()
            # Parse JSON and extract votes
            result_json = json.loads(clean)
            # .group(1) 表示提取第一个捕获组（即 (.*?) 匹配到的内容）
    
            return (
                agent_id,
                result_json.get("new_content", ""),
                None,
                result_json.get("status", "ongoing")
            )
        except json.JSONDecodeError:
            logger.error(f"{indent}❌ Agent {agent_id} returned invalid JSON format")
            return agent_id, None, ValueError("Invalid JSON format"), None
    except Exception as e:
        logger.error(f"{indent}❌ Agent {agent_id} generation failed: {str(e)}")
        return agent_id, None, e, None


def process_generation_results(results: List[Tuple]) -> tuple[dict[Any, dict], dict[Any, Any]]:
    """Process generation results into usable formats."""
    processed_results = {}
    agent_statuses = {}

    for agent_id, new_text, error, status in results:
        if error or not new_text:
            continue
        processed_results[agent_id] = new_text
        agent_statuses[agent_id] = status


    return processed_results, agent_statuses




import json
from typing import List

async def voting(overall_task: str, agent_id: int, versions:  List[str]) -> List[int]:
    """Perform cross-validation between agent results and return list of votes."""
    config = AGENT_CONFIGS[agent_id % len(AGENT_CONFIGS)]


    client = LLMClient(
        provider=config["provider"],
        model=config["model"],
        temperature=0.0
    )
    versions_block = "\n\n".join(   
        f"### Version {i}\n{v}"
        for i, v in enumerate(versions)
    )
    evaluation_prompt = f"""
### overall objective
{overall_task}


### Different versions of answers
{versions_block}

"""

    try:
        messages = [
            {"role": "system", "content": prompt.VOTING_PROMPT},
            {"role": "user", "content": evaluation_prompt}
        ]

        # Get the raw JSON response from the LLM
        evaluation = await client.a_chat_completion(
            messages=messages,
            max_tokens=64
        )

        # 1. Remove any leading ``` or ```json
        clean = re.sub(r"^```(?:json)?\s*", "", evaluation)

        # 2. Remove any trailing ```
        clean = re.sub(r"```$", "", clean).strip()
        # Parse JSON and extract votes
        data = json.loads(clean)
        votes = [int(v) for v in data.get("votes", [])]
        return votes

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}")
        return []
    except Exception as e:
        logger.error(f"Validation by Agent {agent_id} failed: {e}")
        return []



import asyncio
from collections import Counter
from typing import List

async def select_best_result(
    overall_task: str,
    candidate_results: List[str],
    agent_ids: List[int]
) -> str:
    """
    Select the best result from multiple candidates using cross-validation.
    Each agent in `agent_ids` votes for the best version via the `voting` function.
    """

    # 1. Launch one voting task per validator
    tasks = [
        asyncio.create_task(
            voting(
                overall_task=overall_task,
                agent_id=validator_id,
                versions=candidate_results
            )
        )
        for validator_id in agent_ids
    ]

    # 2. Wait for all votes
    validation_results: List[List[int]] = await asyncio.gather(*tasks)

    # 3. Flatten all votes into a single list
    all_votes = [vote for votes in validation_results for vote in votes]

    # 4. If no votes returned, default to the first candidate
    if not all_votes:
        return candidate_results[0]

    # 5. Count votes per version number (1-based)
    vote_counts = Counter(all_votes)
    best_version_number = vote_counts.most_common(1)[0][0]


    return candidate_results[best_version_number]
