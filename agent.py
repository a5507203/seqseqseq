import json
from typing import List, Dict, Any, Optional
from llmClient import LLMClient
from memory import Memory
from prompt import *





import logging
logger = logging.getLogger(__name__)

class Agent:
    """
    An Agent that uses an LLMClient to process tasks with validation, voting, and incremental execution,
    while storing context in GeneralMemory.
    """
    def __init__(
        self,
        llm_client: LLMClient,
        id: int,    
        execute_prompt: str = "",
        memory_capacity: Optional[int] = None,
    ):
        self.llm = llm_client
        self.id = id
        self.memory = Memory(long_term_capacity=memory_capacity)
        self.status = "ongoing"  # Status of the agent
        self.execute_prompt = execute_prompt

    def setNewTask(self, task: str) -> None:
        """
        Set the current task for the agent.
        """
        self.memory.clean_short()
        self.memory.set_task(task)
        self.status = "ongoing"


    async def validate_async(self, overall: str, task: str, fragment: str) -> bool:

        user_content = f"# overall objective:\n{overall}\n\n---\n\n# current task:\n{task}\n\n---\n\n# generated output fragment so far:\n{fragment}\n"
        logger.info(f"[DEBUG] validation input [Agent {self.id}]: {user_content}")
        prompt = [
            {"role": "system", "content": OBJECTIVE_VALIDATOR_PROMPT},
            {"role": "user", "content": user_content}
        ]
        try:
            data = json.loads(await self.llm.a_chat_completion(prompt))
            result = (data.get("result", "")).lower()
            logger.info(f"[Agent {self.id}] Validation result: {data}")
            
            return "true" in result
        except Exception as e:
            logger.info(f"[error][Agent {self.id}] Validation failed: {e}")
            return False

    async def step_async(self, overall: str, task: str) -> Dict[str, Any]:
        prior = self.memory.get_all()
        jf = self.memory.get_short_justify_str()
        user_content = f"# overall objective:\n{overall}\n\n---\n\n# current task:\n{task}\n\n---\n\n# previously generated justifications: \n{jf}\n\n---\n\n# previous all generated segments:\n{prior}\n"
        logger.info(f"[DEBUG] step input [Agent {self.id}]: {user_content}")

        prompt = [
            {"role": "system", "content": TASK_EXECUTION_PROMPT},
            {"role": "user", "content": user_content}
        ]
        try:
            raw_response = await self.llm.a_chat_completion(prompt)
  
      
            data = json.loads(raw_response)
            justify = data.get("justify", "")
            new_content = data.get("new_content", "")
            status = data.get("status", "").lower()
            mode = data.get("mode", "").lower()

            logger.info(f"[DEBUG][Agent {self.id}] Generated content preview: \n\n---\n\n jf: {justify} \n\n---\n\n new content \n {new_content}\n Step status: {status} \n\n---\n\n mode: {mode}\n")

            if "complete" in status:
                self.status = "complete"
            else:
                self.status = "ongoing"

            if "override" in mode:
                self.memory.replace_all(new_content,justify)
            else:                
                self.memory.add_short(new_content,justify)
            logger.info(f"[DEBUG][Agent {self.id}] Added new content to memory.")
            return data

        except json.JSONDecodeError as e:
            logger.info(f"[error][Agent {self.id}] JSON decoding failed: {e}")
            self.status = "fail"
            raise RuntimeError(f"Agent {self.id} failed to parse LLM response as JSON.")

        except Exception as e:
            logger.info(f"[error][Agent {self.id}] Unexpected error during step_async: {e}")
            self.status = "fail"
            raise RuntimeError(f"Agent {self.id} encountered an error: {e}")


    async def vote_async(self, overall: str, task: str, versions: List[str]) -> List[int]:

        versions_block = "\n\n".join(   
            f"## Version {i}\n{v} \n --- \n"
            for i, v in enumerate(versions)
        )
        user_content = f"# Overall objective:\n{overall}\n\n---\n\n# current task:\n{task}\n\n---\n\n# Different versions of answers for current task: \n{versions_block}\n\n---\n\n"
       
        logger.info(f"[DEBUG] vote input [Agent {self.id}]: {user_content}")
        prompt = [
            {"role": "system", "content": VOTING_PROMPT},
            {"role": "user", "content": user_content}
        ]
        raw = await self.llm.a_chat_completion(prompt)

        data = json.loads(raw)
        votes = data.get("votes", [])

        logger.info(f"[DEBUG][Agent {self.id}] Voting result: {votes}")
        return votes
