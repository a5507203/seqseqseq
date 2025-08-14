from typing import List, Dict, Any, Optional, Union

class Memory:
    """
    General memory structure with separate short-term and long-term storage.

    Short-term memory:
      - Holds the current task description and accumulated response segments.
    Long-term memory:
      - A list of dicts, each entry saving a completed task's description, segments, and optional result.
    """

    def __init__(self, long_term_capacity: Optional[int] = None):
        """
        :param long_term_capacity: Optional maximum number of entries in long-term memory.
        """
        self.short_term: Dict[str, Any] = {"task": "", "segments": [],"justify":[]}
        self.long_term: List[Dict[str, Any]] = []
        self.capacity = long_term_capacity

    def set_task(self, task_description: str):
        """Initialize a new current task, clearing any previous segments."""
        self.clean_short()
        self.short_term["task"] = task_description

    def add_short(self, segment: str, justify:str):
        """Add a new response segment to the current task."""
   
        self.short_term["segments"].append(segment)
        self.short_term["justify"]=[]
        self.short_term["justify"].append(justify)
        # Clear validation feedback since we have new content that hasn't been validated yet
        self.short_term["validation_feedback"] = []
    
    def add_validation_justification(self, justify: str):
        """Add validation justification that can guide future execution."""
        if "validation_feedback" not in self.short_term:
            self.short_term["validation_feedback"] = []
        self.short_term["validation_feedback"].append(justify)

    def archive_task(self, result: Any = None):
        """
        Archive the current task and its segments into long-term memory.
        :param result: Optional final result or summary of the task.
        """
        entry: Dict[str, Any] = {
            "task": self.short_term.get("task"),
            "result": self.get_short_segment_str(),
        }
        if result is not None:
            entry["result"] = result
        self.long_term.append(entry)
        # clear short-term memory
        self.clean_short()

    def get_short_justify_str(self) -> str:
        """Return the raw concatenation of all justifications in short-term memory."""
        justifications = self.short_term.get("justify", [])
        return "\n".join(justifications)
    
    def get_validation_feedback_str(self) -> str:
        """Return validation feedback as a separate string."""
        validation_feedback = self.short_term.get("validation_feedback", [])
        return "\n".join(validation_feedback)
    
    def get_short_segment_str(self) -> str:
        """Return the raw concatenation of all segments in short-term memory."""
        return "\n".join(self.short_term.get("segments", []))

    def get_long_str(self) -> str:
        """
        Concatenate and return all 'result' strings from long-term memory.
        """
        # Join each result entry, converting to string in case it's not already
        return "\n".join(str(entry.get("result", "")) for entry in self.long_term)

    def get_all(self) -> str:

        """
        Concatenate and return all 'result' strings from  memory.
        """
        # Join each result entry, converting to string in case it's not already
        return self.get_long_str()+"\n"+self.get_short_segment_str()

    def replace_all(self, seg,justify):
        self.long_term: List[Dict[str, Any]] = []
        self.short_term["segments"] = [seg]
        self.short_term["justify"] = [justify]
        # Clear validation feedback since we have completely new content
        self.short_term["validation_feedback"] = []

    def clean_short(self) -> None:
        """Clear all response segments in short-term memory, keeping the task description."""
        self.short_term =  {"task": "", "segments": [],"justify":[], "validation_feedback": []}

