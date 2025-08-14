@echo off
setlocal enabledelayedexpansion

rem Script to run all tasks 3 times each
rem Usage: run_all_tasks.bat

echo Starting batch execution of all tasks...

rem Array of all available tasks
set tasks=mle_lecture nips_website pac_tank puzzle_game_electrical_circuits quiz_platform_metroidvania snake_chess task_manager_rpg tetris_bjeweled travel_plan

rem Number of runs per task
set num_runs=3

rem Create results directory if it doesn't exist
set results_dir=results
if not exist "%results_dir%" mkdir "%results_dir%"

rem Count total tasks
set task_count=0
for %%i in (%tasks%) do set /a task_count+=1

set /a total_executions=%task_count% * %num_runs%
set current_execution=0

echo Tasks to run: %task_count%
echo Runs per task: %num_runs%
echo Total executions: %total_executions%
echo Results will be saved to: %results_dir%\
echo ----------------------------------------

rem Run each task multiple times
for %%t in (%tasks%) do (
    echo.
    echo Running task: %%t
    echo ----------------------------------------
    
    for /l %%r in (1,1,%num_runs%) do (
        set /a current_execution+=1
        
        echo [!current_execution!/%total_executions%] Executing %%t ^(run %%r/%num_runs%^)...
        
        rem Create output filename with task name and run number
        set output_file=%results_dir%\%%t_run%%r.txt
        set log_file=%results_dir%\%%t_run%%r.log
        
        rem Record start time
        set start_time=%time%
        
        rem Run the task and capture output
        python main.py --task %%t --output !output_file! > !log_file! 2>&1
        
        if !errorlevel! equ 0 (
            echo   ✓ Completed successfully -^> !output_file!
        ) else (
            echo   ✗ Failed with exit code !errorlevel! -^> see !log_file!
        )
        
        rem Add a small delay between runs
        timeout /t 2 /nobreak > nul
    )
)

echo.
echo ----------------------------------------
echo Batch execution completed!
echo Results saved in: %results_dir%\
echo.
echo Summary of output files:
for %%t in (%tasks%) do (
    echo   %%t:
    for /l %%r in (1,1,%num_runs%) do (
        set output_file=%results_dir%\%%t_run%%r.txt
        set log_file=%results_dir%\%%t_run%%r.log
        if exist "!output_file!" (
            for %%s in ("!output_file!") do (
                echo     run %%r: !output_file! ^(%%~zs bytes^)
            )
        ) else (
            echo     run %%r: FAILED - see !log_file!
        )
    )
)

pause