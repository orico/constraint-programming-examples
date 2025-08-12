from ortools.linear_solver import pywraplp

def solve_job_shop_mip():
    # Input data
    jobs = [
        [(0, 3), (1, 2), (2, 2)],  # job 0
        [(0, 2), (2, 1), (1, 4)],  # job 1
        [(1, 4), (2, 3)]           # job 2
    ]
    
    num_machines = 3
    
    # Create solver
    solver = pywraplp.Solver.CreateSolver('SCIP')
    
    # Calculate big M
    M = sum(duration for job in jobs for _, duration in job)
    
    # Variables
    start_times = {}
    sequence_vars = {}
    for i, job in enumerate(jobs):
        for j, (machine, duration) in enumerate(job):
            start_times[i,j] = solver.NumVar(0, M, f'start_{i}_{j}')
            
    # Binary variables for sequencing decisions
    for i1, job1 in enumerate(jobs):
        for j1, (m1, d1) in enumerate(job1):
            for i2, job2 in enumerate(jobs):
                for j2, (m2, d2) in enumerate(job2):
                    if i1 != i2 and m1 == m2:
                        sequence_vars[i1,j1,i2,j2] = solver.BoolVar(f'seq_{i1}_{j1}_{i2}_{j2}')
    
    # Precedence constraints
    for i, job in enumerate(jobs):
        for j in range(len(job)-1):
            solver.Add(start_times[i,j] + job[j][1] <= start_times[i,j+1])
    
    # No overlap constraints
    for i1, job1 in enumerate(jobs):
        for j1, (m1, d1) in enumerate(job1):
            for i2, job2 in enumerate(jobs):
                for j2, (m2, d2) in enumerate(job2):
                    if i1 != i2 and m1 == m2:
                        solver.Add(start_times[i1,j1] + d1 <= start_times[i2,j2] + 
                                 M * (1 - sequence_vars[i1,j1,i2,j2]))
                        solver.Add(start_times[i2,j2] + d2 <= start_times[i1,j1] + 
                                 M * sequence_vars[i1,j1,i2,j2])
    
    # Objective: minimize makespan
    makespan = solver.NumVar(0, M, 'makespan')
    for i, job in enumerate(jobs):
        solver.Add(start_times[i,len(job)-1] + job[-1][1] <= makespan)
    solver.Minimize(makespan)
    
    # Solve
    status = solver.Solve()
    
    if status == pywraplp.Solver.OPTIMAL:
        # Create schedule for formatting
        machine_schedule = {i: [] for i in range(num_machines)}
        
        for i, job in enumerate(jobs):
            for j, (machine, duration) in enumerate(job):
                start_time = round(start_times[i,j].solution_value())  # Round to nearest integer
                machine_schedule[machine].append({
                    'job': i,
                    'task': j,
                    'start': start_time,
                    'duration': duration,
                    'end': start_time + duration
                })

        # Sort tasks by start time for each machine
        for machine in machine_schedule:
            machine_schedule[machine].sort(key=lambda x: x['start'])

        # Print formatted output
        print("Solution:")
        print(f"Optimal Schedule Length: {round(makespan.solution_value())}")
        
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
    solve_job_shop_mip()