#!/bin/bash

# Script to run all tasks 3 times each
# Usage: ./run_all_tasks.sh

# Array of all available tasks
tasks=(
    "mle_lecture"
    "nips_website" 
    "pac_tank"
    "puzzle_game_electrical_circuits"
    "quiz_platform_metroidvania"
    "snake_chess"
    "task_manager_rpg"
    "tetris_bjeweled"
    "travel_plan"
)

# Number of runs per task
num_runs=3

# Create results directory if it doesn't exist
results_dir="results"
mkdir -p "$results_dir"

echo "Starting batch execution of all tasks..."
echo "Tasks to run: ${#tasks[@]}"
echo "Runs per task: $num_runs"
echo "Total executions: $((${#tasks[@]} * num_runs))"
echo "Results will be saved to: $results_dir/"
echo "----------------------------------------"

# Counter for tracking progress
total_executions=$((${#tasks[@]} * num_runs))
current_execution=0

# Run each task multiple times
for task in "${tasks[@]}"; do
    echo ""
    echo "Running task: $task"
    echo "----------------------------------------"
    
    for run in $(seq 1 $num_runs); do
        current_execution=$((current_execution + 1))
        
        echo "[$current_execution/$total_executions] Executing $task (run $run/$num_runs)..."
        
        # Create output filename with task name and run number
        output_file="$results_dir/${task}_run${run}.txt"
        log_file="$results_dir/${task}_run${run}.log"
        
        # Record start time
        start_time=$(date +%s)
        
        # Run the task and capture both stdout and stderr
        python main.py --task "$task" --output "$output_file" > "$log_file" 2>&1
        exit_code=$?
        
        # Record end time and calculate duration
        end_time=$(date +%s)
        duration=$((end_time - start_time))
        
        if [ $exit_code -eq 0 ]; then
            echo "  ✓ Completed successfully in ${duration}s -> $output_file"
        else
            echo "  ✗ Failed with exit code $exit_code (${duration}s) -> see $log_file"
        fi
        
        # Add a small delay between runs to prevent overwhelming the system
        sleep 2
    done
done

echo ""
echo "----------------------------------------"
echo "Batch execution completed!"
echo "Results saved in: $results_dir/"
echo ""
echo "Summary of output files:"
for task in "${tasks[@]}"; do
    echo "  $task:"
    for run in $(seq 1 $num_runs); do
        output_file="$results_dir/${task}_run${run}.txt"
        log_file="$results_dir/${task}_run${run}.log"
        if [ -f "$output_file" ]; then
            size=$(wc -c < "$output_file")
            echo "    run $run: $output_file (${size} bytes)"
        else
            echo "    run $run: FAILED - see $log_file"
        fi
    done
done