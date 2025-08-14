import logging
import asyncio
from typing import List, Dict, Optional
from agent import Agent
import copy
import asyncio
from collections import Counter
import time

logger = logging.getLogger(__name__)


class TaskExecuter:
    """
    Orchestrates branching recursive execution of tasks across multiple Agents,
    leveraging each Agent's short- and long-term memory for result storage and fallback.
    """
    def __init__(
        self,
        agents: Dict[int, Agent],
        current_task: str,
        max_rounds: int = 5,
    ):
        self.agents = agents
        self.current_task = current_task
        self.max_rounds = max_rounds

    async def step(self,rnd, active_agents):
        """
        Execute the current task using all agents, with a fallback to memory if needed.
        """
        if not active_agents:
            logger.info(f"No active agents left at round {rnd+1}.")
            return None
        logger.info(f"↻ Round {rnd+1}/{self.max_rounds}, active={[a.id for a in active_agents]}")

        step_tasks = [
            agent.step_async(self.current_task)
            for agent in active_agents
        ]
        step_results = await asyncio.gather(*step_tasks, return_exceptions=False)
    

        return step_results

    async def cros_model_val(self, active_agents):
        """
        Phase 2: cross-model validation by majority vote with justification extraction.
        All agents (excluding the producer) validate each new fragment concurrently.
        """
        # Map each producer agent to its validation task
        success_count = 0
        validation_map = []  # list of (agent, validation_task)
        agent_validation_results = {}  # Store validation results for each agent
        
        for agent in active_agents:
            segs = agent.memory.get_all()
            if not segs:
                continue
            validators = [v for v in self.agents.values() if v.id != agent.id]
            task = asyncio.gather(
                *(v.validate_async(self.current_task, segs)
                for v in validators),
                return_exceptions=True
            )
            validation_map.append((agent, task))

        # Run all validations in parallel
        results = await asyncio.gather(*(task for _, task in validation_map))

        # Apply majority rule and collect validation feedback
        total_validators = len(self.agents) - 1
        winner_mem = None
        best_agent_score = -1
        best_agent = None
        
        for (agent, _), votes in zip(validation_map, results):
            # Extract validation results and justifications
            valid_votes = 0
            all_justifications = []
            
            for vote_result in votes:
                if isinstance(vote_result, dict):
                    if vote_result.get("result", False):
                        valid_votes += 1
                    all_justifications.append(vote_result.get("justify", ""))
                elif isinstance(vote_result, bool) and vote_result:  # Backward compatibility
                    valid_votes += 1
            
            agent_validation_results[agent.id] = {
                "valid_votes": valid_votes,
                "total_votes": total_validators,
                "justifications": all_justifications
            }
            
            # Track best agent for fallback scenario
            if valid_votes > best_agent_score:
                best_agent_score = valid_votes
                best_agent = agent
            
            # Store validation feedback regardless of pass/fail status
            feedback_items = [j for j in all_justifications if j.strip()]
            if feedback_items:
                # Add all validation feedback to help guide future iterations
                for feedback in feedback_items:
                    agent.memory.add_validation_justification(feedback)
            
            if valid_votes < total_validators / 2:
                # Agent failed validation
                agent.status = "fail"
                logger.warning(
                    f"Agent {agent.id} fragment failed cross-validation "
                    f"({valid_votes}/{total_validators} votes) - {len(feedback_items)} feedback items collected"
                )
            else:
                success_count += 1
                winner_mem = copy.deepcopy(agent.memory.short_term)
                logger.info(
                    f"Agent {agent.id} fragment passed cross-validation "
                    f"({valid_votes}/{total_validators} votes) - {len(feedback_items)} feedback items collected"
                )
        
        # Handle the case where all agents fail
        if success_count == 0 and best_agent is not None:
            logger.warning("All agents failed validation. Selecting best performing agent as fallback.")
            winner_mem = copy.deepcopy(best_agent.memory.short_term)
            best_agent.status = "ongoing"  # Reset status for the best agent
            success_count = 1
        
        self.replace_fail(winner_mem)
        return success_count

    def replace_fail(self, winner_mem):

        if winner_mem != None:
            for agent in self.agents.values():
                if agent.status == "fail":
                    logger.info(f"replace Agent {agent.id} short term memory.")
                    agent.memory.short_term = copy.deepcopy(winner_mem)
                    agent.status = "ongoing"

    async def select_best(self, agent_ids: List[int]):
        """
        Vote to pick the best agent, then copy its entire long-term memory
        into every agent (preserving all past tasks), and clear short-term.
        Returns the winner's full long-term memory as a single string.
        """
        # 1) Gather each agent’s full long-term text for voting
        candidates = []
        for aid in agent_ids:
            text = self.agents[aid].memory.get_all()
            # concatenate all results for that agent
            candidates.append(text)

        # 2) If no one has any long-term memory yet, fall back to short-term
        if not any(candidates):
            # simple concatenation of short_term
            return ""

        # 3) Vote across agents in parallel
        vote_tasks = [
            self.agents[aid].vote_async(self.current_task, candidates)
            for aid in agent_ids
        ]
        vote_results = await asyncio.gather(*vote_tasks, return_exceptions=True)

        # 4) tally each agent's top choice (first in its votes list)
        top_choices = []
        for vr in vote_results:
            if isinstance(vr, list) and vr:
                top = vr[0]
                if 0 <= top < len(candidates):
                    top_choices.append(top)
        if not top_choices:
            winner_idx = 0
        else:
            winner_idx, _ = Counter(top_choices).most_common(1)[0]
        # 5) identify winner’s full long-term memory
        winner_id = agent_ids[winner_idx]
        self.agents[winner_id].memory.archive_task()
        winner_mem = copy.deepcopy(self.agents[winner_id].memory.long_term)
        # 6) copy that memory into every agent, clear short-term
        for agent in self.agents.values():
            agent.memory.long_term = copy.deepcopy(winner_mem)
            agent.memory.clean_short()

        return candidates[winner_idx]

    
    async def run(
        self,
        agent_ids: List[int],

    ) -> str:
        indent = "  "

        # reset all agents to "ongoing" status
        for agent in self.agents.values():
            agent.setNewTask(self.current_task)
        # Iterative rounds of generation
        for rnd in range(self.max_rounds):

            active_agents = [agent for agent in self.agents.values() if agent.status == "ongoing"]

            # Phase 1: fire off all agent steps concurrently
            start_phase1 = time.time()
            if await self.step(rnd, active_agents) is None:
                break
            end_phase1 = time.time()
            logger.info(f"{indent}Phase 1 (agent steps) completed in {end_phase1 - start_phase1:.2f} seconds")

            # Phase 2: cross model validation based on the agents status not failed and not complete one need to be vlidated by all others, if majority say fail then it is failed.
            start_phase2 = time.time()
            success_count = await self.cros_model_val(active_agents) 
            success_count += len([agent for agent in self.agents.values() if agent.status == "complete"])
            end_phase2 = time.time()
            logger.info(f"{indent}Phase 2 (cross validation) completed in {end_phase2 - start_phase2:.2f} seconds")
          

        # Phase 3: All done or fallback to memory
        await self.select_best(agent_ids)

        return None

