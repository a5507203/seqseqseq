# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the System

### Basic Execution
```bash
python main.py
```

The system will:
- Load agents with different OpenAI models (o4-mini, o3-mini, o4-mini-2025-04-16)
- Execute the current task defined in `main.py:70`
- Generate output to `example.txt`
- Log execution details to `app.log`

### Configuration
- API keys and model settings are in `config.py` 
- Current task is selected in `main.py:70` from predefined tasks in `task_prompt.py`
- Adjust `max_rounds` (default: 30) and `max_recursion_depth` (default: 10) in TaskExecuter initialization
- **SECURITY WARNING**: The `config.py` file contains hardcoded API keys that should be moved to environment variables

## System Architecture

### Core Components

**TaskExecuter** (`taskexecuter.py`): Orchestrates multi-agent execution with three phases:
1. **Agent Steps**: Multiple agents work on task concurrently  
2. **Cross-Model Validation**: Agents validate each other's outputs via majority voting
3. **Best Result Selection**: Final voting determines winning output

**Agent** (`agent.py`): Individual processing unit with:
- LLM client integration (OpenAI models)
- Memory management (short-term and long-term)
- Three async operations: `step_async()`, `validate_async()`, `vote_async()`
- Status tracking ("ongoing", "complete", "fail")

**Memory** (`memory.py`): Hierarchical storage:
- **Short-term**: Current task segments and justifications
- **Long-term**: Archived completed tasks
- **Accumulation**: Results propagate through recursive calls

### Execution Flow

1. **Initialization**: Agents loaded with different models from Config
2. **Task Assignment**: Current task set from task_prompt.py definitions
3. **Iterative Refinement**: Up to 30 rounds of:
   - Concurrent agent execution
   - Cross-validation by peer agents  
   - Memory updates and status management
4. **Result Selection**: Best result chosen via agent voting
5. **Output**: Final result written to example.txt

### Task Definitions

Tasks are defined in `task_prompt.py` with specific output formats:
- `mle_lecture`: LaTeX lecture slides
- `nips_website`: HTML+CSS conference website
- `pac_tank`: Python Pac-Man/Tank fusion game
- `puzzle_game_electrical_circuits`: HTML5+CSS3+JS puzzle game
- `quiz_platform_metroidvania`: HTML+CSS+JS quiz-gated game
- `snake_chess`: Python Snake/Chess hybrid
- `task_manager_rpg`: HTML+CSS+JS task management RPG
- `tetris_bjeweled`: Python Tetris/Bejeweled fusion
- `travel_plan`: LaTeX travel itinerary

### Multi-Agent Collaboration

- **Concurrent Processing**: Multiple agents work simultaneously on the same task
- **Validation System**: Each agent's output validated by all other agents
- **Fallback Mechanism**: Failed agents replaced with successful agent's memory
- **Quality Control**: Only outputs passing majority validation proceed
- **Result Accumulation**: Best results from each round preserved and built upon

## Development Notes

### Key Implementation Details
- System uses JSON-structured prompts defined in `prompt.py`
- All agent communication is JSON-based with strict schema validation
- Memory system supports both incremental ("continue") and replacement ("override") modes
- Cross-validation prevents low-quality outputs from propagating
- The system is designed for complex, multi-step content generation tasks

### Agent Loading
Agents are loaded dynamically based on `Config` attributes starting with "GPT_MODEL":
- `Config.GPT_MODEL` → Agent 0 (o4-mini)
- `Config.GPT_MODEL1` → Agent 1 (o3-mini)  
- `Config.GPT_MODEL2` → Agent 2 (o4-mini-2025-04-16)

### Experimentation
The `experiments/` directory contains comparative results from different approaches:
- `aflow/`: A-Flow methodology results
- `atom/`: ATOM methodology results  
- `flow/`: Flow methodology results
- `o4-mini-high/`: High-temperature o4-mini results
- `ours/`: This system's results with execution times

### Debugging and Monitoring
- All execution details logged to `app.log` with UTF-8 encoding
- Agent status tracked as "ongoing", "complete", or "fail"
- Cross-model validation results logged for transparency
- Final results written to `example.txt`