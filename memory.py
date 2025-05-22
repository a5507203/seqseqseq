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


    def add_segment(self, segment: str):
        """Add a new response segment to the current task."""
        self.short_term["segments"].append(segment)

    def add_short(self, segment: str, justify:str):
        """Add a new response segment to the current task."""
   
        self.short_term["segments"].append(segment)
        self.short_term["justify"]=[]
        self.short_term["justify"].append(justify)

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

    def record_long(self, entry: Dict[str, Any]):
        """
        Directly record an arbitrary entry into long-term memory.
        """
        self.long_term.append(entry)
        if self.capacity is not None and len(self.long_term) > self.capacity:
            self.long_term.pop(0)

    def query_long(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Query long-term memory entries by matching key-value pairs.
        """
        def match(e: Dict[str, Any]) -> bool:
            for k, v in kwargs.items():
                if e.get(k) != v:
                    return False
            return True
        return [e for e in self.long_term if match(e)]

    def get_short(self) -> Dict[str, Any]:
        """Return a copy of the current short-term memory."""
        return self.short_term.copy()


    def get_short_str(self) -> Dict[str, Any]:
        """Return a copy of the current short-term memory."""
        return  "### all previous justifications:" + self.get_short_justify_str   +  "### previous results"+   self.get_short_segment_str + "\n"


    def get_short_justify_str(self) -> str:
        """Return the raw concatenation of all segments in short-term memory."""
        return "".join(self.short_term.get("justify", []))
    
    def get_short_segment_str(self) -> str:
        """Return the raw concatenation of all segments in short-term memory."""
        return "\n".join(self.short_term.get("segments", []))

    def get_lastest_segment_str(self) -> str:
        """Return the raw concatenation of all segments in short-term memory."""
        return self.short_term["segments"][-1]


    
    def get_long(self) -> List[Dict[str, Any]]:
        """Return all entries from long-term memory."""
        return list(self.long_term)

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


    def get_all_with_justify(self) -> str:

        """
        Concatenate and return all 'result' strings from  memory.
        """
        # Join each result entry, converting to string in case it's not already
        return self.get_long_str()+self.get_short_segment_str()
    

    def clean_all(self) -> None:
        """Clear all response segments in short-term memory, keeping the task description."""
        self.clean_short()
        self.long_term: List[Dict[str, Any]] = []

    def replace_all(self, seg,justify):
        self.long_term: List[Dict[str, Any]] = []
        self.short_term["segments"] = [seg]
        self.short_term["justify"] = [justify]

    def clean_short(self) -> None:
        """Clear all response segments in short-term memory, keeping the task description."""
        self.short_term =  {"task": "", "segments": [],"justify":[]}

