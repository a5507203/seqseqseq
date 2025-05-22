from typing import Dict, Any, List

class Task:
    def __init__(self,
                 objective: str,
                 agent_ids: List[int],
                 ):

        self.objective = objective
        self.agent_ids = agent_ids


    def to_dict(self) -> Dict[str, Any]:
        return {
            'objective': self.objective,
            "agent_ids": self.agent_ids,
        }


