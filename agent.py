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


    async def validate_async(self, task: str, fragment: str) -> Dict[str, Any]:
        """
        Validates a fragment and returns both result and justify information.
        Returns: {"result": bool, "justify": str}
        """
        user_content = f"# task:\n{task}\n\n---\n\n# generated output fragment so far:\n{fragment}\n"
        logger.info(f"[DEBUG] validation input [Agent {self.id}]: {user_content}")
        prompt = [
            {"role": "system", "content": OBJECTIVE_VALIDATOR_PROMPT},
            {"role": "user", "content": user_content}
        ]
        try:
            data = json.loads(await self.llm.a_chat_completion(prompt))
            result = (data.get("result", "")).lower()
            justify = data.get("justify", "")
            logger.info(f"[Agent {self.id}] Validation result: {data}")
            
            return {
                "result": "true" in result,
                "justify": justify
            }
        except Exception as e:
            logger.info(f"[error][Agent {self.id}] Validation failed: {e}")
            return {"result": False, "justify": f"Validation error: {str(e)}"}

    async def step_async(self, task: str) -> Dict[str, Any]:
        prior = self.memory.get_all()
        jf = self.memory.get_short_justify_str()
        validation_feedback = self.memory.get_validation_feedback_str()
        
        # Construct user content with clear separation
        user_content = f"# task:\n{task}\n\n---\n\n"
        
        if jf.strip():
            user_content += f"# previously generated justifications:\n{jf}\n\n---\n\n"
        
        if validation_feedback.strip():
            user_content += f"# validation feedback from other agents:\n{validation_feedback}\n\n---\n\n"
        
        user_content += f"# previous all generated segments:\n{prior}\n"
        
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

            logger.info(f"[DEBUG][Agent {self.id}] Generated content preview: \n\n---\n\n justify: {justify} \n\n---\n\n new content \n {new_content}\n Step status: {status} \n\n---\n\n mode: {mode}\n")

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


    async def vote_async(self, task: str, versions: List[str]) -> List[int]:

        versions_block = "\n\n".join(   
            f"## Version {i}\n{v} \n --- \n"
            for i, v in enumerate(versions)
        )
        user_content = f"# task:\n{task}\n\n---\n\n# Different versions of answers for task: \n{versions_block}\n\n---\n\n"
       
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
