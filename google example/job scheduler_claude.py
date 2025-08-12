from ortools.sat.python import cp_model

def solve_job_shop():
    # Input data
    jobs = [
        [(0, 3), (1, 2), (2, 2)],  # job 0
        [(0, 2), (2, 1), (1, 4)],  # job 1
        [(1, 4), (2, 3)]           # job 2
    ]
    
    num_machines = 3
    all_machines = range(num_machines)

    # Model
    model = cp_model.CpModel()
    
    # Variables
    tasks = {}
    intervals = {}
    for job_id, job in enumerate(jobs):
        for task_id, (machine, duration) in enumerate(job):
            start = model.NewIntVar(0, 1000, f'start_{job_id}_{task_id}')
            end = model.NewIntVar(0, 1000, f'end_{job_id}_{task_id}')
            interval = model.NewIntervalVar(start, duration, end, f'interval_{job_id}_{task_id}')
            tasks[job_id, task_id] = (start, end, interval, machine, duration)
            intervals[job_id, task_id] = interval

    # Precedence constraints
    for job_id, job in enumerate(jobs):
        for task_id in range(len(job) - 1):
            model.Add(tasks[job_id, task_id][1] <= tasks[job_id, task_id + 1][0])

    # No overlap constraints
    for machine in all_machines:
        machine_intervals = []
        for job_id, job in enumerate(jobs):
            for task_id, (machine_id, _) in enumerate(job):
                if machine_id == machine:
                    machine_intervals.append(intervals[job_id, task_id])
        model.AddNoOverlap(machine_intervals)

    # Objective: minimize makespan
    makespan = model.NewIntVar(0, 1000, 'makespan')
    for job_id, job in enumerate(jobs):
        model.Add(tasks[job_id, len(job)-1][1] <= makespan)
    model.Minimize(makespan)

    # Solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL:
        # Create schedule for formatting
        machine_schedule = {i: [] for i in range(num_machines)}
        
        for job_id, job in enumerate(jobs):
            for task_id, (machine, duration) in enumerate(job):
                start_time = solver.Value(tasks[job_id, task_id][0])
                machine_schedule[machine].append({
                    'job': job_id,
                    'task': task_id,
                    'start': start_time,
                    'duration': duration,
                    'end': start_time + duration
                })

        # Sort tasks by start time for each machine
        for machine in machine_schedule:
            machine_schedule[machine].sort(key=lambda x: x['start'])

        # Print formatted output
        print("Solution:")
        print(f"Optimal Schedule Length: {solver.ObjectiveValue()}")
        
        for machine in range(num_machines):
            # Print machine header
            print(f"Machine {machine}:", end=" ")
            
            # Calculate maximum task string length for padding
            tasks_str = [f"job_{t['job']}_task_{t['task']}" for t in machine_schedule[machine]]
            max_len = max(len(s) for s in tasks_str) if tasks_str else 0
            
            # Print task names
            print("  ".join(s.ljust(max_len) for s in tasks_str))
            
            # Print intervals
            intervals_str = [f"[{t['start']},{t['end']}]" for t in machine_schedule[machine]]
            print(" " * len(f"Machine {machine}:"), end=" ")
            print("  ".join(s.ljust(max_len) for s in intervals_str))
            
            print()  # Empty line between machines

if __name__ == '__main__':
    solve_job_shop()