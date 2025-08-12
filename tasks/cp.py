from ortools.sat.python import cp_model
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
from enum import Enum, IntEnum
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

class SkillLevel(IntEnum):
    JUNIOR = 1
    INTERMEDIATE = 2
    SENIOR = 3
    EXPERT = 4

class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class Role(Enum):
    FULLSTACK = "Full Stack Developer"
    BACKEND = "Backend Developer"
    FRONTEND = "Frontend Developer"
    DESIGNER = "UX Designer"
    DEVOPS = "DevOps Engineer"
    DATA_SCIENTIST = "Data Scientist"
    PROGRAM_MANAGER = "Program Manager"
    COPYWRITER = "Copywriter"
    MARKETING = "Marketing Specialist"
    PRODUCT_MANAGER = "Product Manager"

class Task:
    def __init__(self, task_id: str, 
                 duration_days: int,
                 required_role: Role,
                 skill_level: SkillLevel,
                 priority: Priority,
                 dependencies: Optional[List[str]] = None):
        self.task_id = task_id
        self.duration_days = duration_days
        self.required_role = required_role
        self.skill_level = skill_level
        self.priority = priority
        self.dependencies = dependencies or []

def main():
    # Define project timeline
    project_start = datetime(2024, 1, 1)
    max_project_days = 31  # Maximum project duration in days
    
    # Create tasks with different roles, skill levels, and priorities
    tasks = [
        Task("Project_Kickoff", 2, Role.PROGRAM_MANAGER, SkillLevel.SENIOR, Priority.CRITICAL, []),
        Task("Stakeholder_Requirements", 2, Role.PRODUCT_MANAGER, SkillLevel.SENIOR, Priority.HIGH, ["Project_Kickoff"]),
        Task("System_Architecture", 2, Role.FULLSTACK, SkillLevel.EXPERT, Priority.HIGH, ["Stakeholder_Requirements"]),
        Task("Database_Schema", 2, Role.DATA_SCIENTIST, SkillLevel.SENIOR, Priority.HIGH, ["System_Architecture"]),
        Task("UI_UX_Design", 3, Role.DESIGNER, SkillLevel.SENIOR, Priority.HIGH, ["Stakeholder_Requirements"]),
        Task("API_Development", 4, Role.BACKEND, SkillLevel.SENIOR, Priority.HIGH, ["Database_Schema"]),
        Task("Frontend_Implementation", 4, Role.FRONTEND, SkillLevel.SENIOR, Priority.HIGH, ["UI_UX_Design"]),
        Task("Security_Implementation", 3, Role.DEVOPS, SkillLevel.EXPERT, Priority.CRITICAL, ["API_Development"]),
        Task("Performance_Optimization", 3, Role.FULLSTACK, SkillLevel.EXPERT, Priority.HIGH, ["Frontend_Implementation", "API_Development"]),
        Task("Content_Creation", 3, Role.COPYWRITER, SkillLevel.INTERMEDIATE, Priority.MEDIUM, ["UI_UX_Design"]),
        Task("Analytics_Integration", 3, Role.DATA_SCIENTIST, SkillLevel.SENIOR, Priority.MEDIUM, ["Frontend_Implementation"]),
        Task("User_Documentation", 3, Role.COPYWRITER, SkillLevel.SENIOR, Priority.MEDIUM, ["Content_Creation"]),
        Task("Market_Research", 3, Role.MARKETING, SkillLevel.SENIOR, Priority.MEDIUM, ["Content_Creation"]),
        Task("Beta_Testing", 4, Role.PRODUCT_MANAGER, SkillLevel.SENIOR, Priority.HIGH, ["Performance_Optimization", "Security_Implementation"]),
        Task("Feedback_Implementation", 3, Role.FULLSTACK, SkillLevel.SENIOR, Priority.HIGH, ["Beta_Testing"]),
        Task("Launch_Planning", 2, Role.MARKETING, SkillLevel.SENIOR, Priority.HIGH, ["Market_Research"]),
        Task("Infrastructure_Scaling", 3, Role.DEVOPS, SkillLevel.EXPERT, Priority.CRITICAL, ["Feedback_Implementation"]),
        Task("Final_Security_Audit", 2, Role.DEVOPS, SkillLevel.EXPERT, Priority.CRITICAL, ["Infrastructure_Scaling"]),
        Task("Production_Deployment", 2, Role.DEVOPS, SkillLevel.EXPERT, Priority.CRITICAL, ["Final_Security_Audit"]),
        Task("Launch_Marketing", 2, Role.MARKETING, SkillLevel.SENIOR, Priority.HIGH, ["Launch_Planning"])
    ]

    # Create the CP-SAT model
    model = cp_model.CpModel()

    # Create variables
    task_starts = {}
    task_ends = {}
    for task in tasks:
        task_starts[task.task_id] = model.NewIntVar(0, max_project_days, f'start_{task.task_id}')
        task_ends[task.task_id] = model.NewIntVar(0, max_project_days, f'end_{task.task_id}')
        
        # Add duration constraints
        model.Add(task_ends[task.task_id] == task_starts[task.task_id] + task.duration_days)

    # Add dependency constraints
    for task in tasks:
        for dep in task.dependencies:
            model.Add(task_starts[task.task_id] >= task_ends[dep])

    # Add resource constraints (prevent same role working on multiple tasks simultaneously)
    for i, task1 in enumerate(tasks):
        for task2 in tasks[i + 1:]:
            if task1.required_role == task2.required_role:
                b = model.NewBoolVar('b')
                model.Add(task_ends[task1.task_id] <= task_starts[task2.task_id]).OnlyEnforceIf(b)
                model.Add(task_ends[task2.task_id] <= task_starts[task1.task_id]).OnlyEnforceIf(b.Not())

    # Objective: Minimize the maximum end time while prioritizing critical tasks
    max_end = model.NewIntVar(0, max_project_days, 'max_end')
    for task in tasks:
        model.Add(max_end >= task_ends[task.task_id])
        
    # Weight by priority
    objective_terms = []
    for task in tasks:
        weight = task.priority.value
        objective_terms.append(task_ends[task.task_id] * weight)
    
    model.Minimize(max_end * 100 + sum(objective_terms))

    # Solve the model
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        # Create lists to store data for DataFrame
        schedule_data = []
        
        # Sort tasks by start time
        sorted_tasks = sorted(tasks, key=lambda x: solver.Value(task_starts[x.task_id]))
        
        project_start_date = project_start
        
        # Create a dictionary to store completion times for dependency checking
        task_end_times = {
            task.task_id: solver.Value(task_ends[task.task_id])
            for task in tasks
        }
        
        for task in sorted_tasks:
            start_day = solver.Value(task_starts[task.task_id])
            end_day = solver.Value(task_ends[task.task_id])
            
            start_date = project_start_date + timedelta(days=start_day)
            end_date = project_start_date + timedelta(days=end_day)
            
            # Check if dependencies are completed by comparing end times
            deps_status = []
            for dep in task.dependencies:
                # A dependency is completed if its end time is less than current task's start time
                deps_status.append(task_end_times[dep] <= start_day)
            
            # Format dependencies list
            deps_str = ", ".join(task.dependencies) if task.dependencies else "None"
            deps_status_str = ", ".join(["✓" if status else "✗" for status in deps_status]) if deps_status else "N/A"
            
            # Add data to list
            schedule_data.append({
                'Task': task.task_id,
                'Start Date': start_date.strftime('%Y-%m-%d'),
                'End Date': end_date.strftime('%Y-%m-%d'),
                'Duration (days)': task.duration_days,
                'Priority': task.priority.name,
                'Role': task.required_role.value,
                'Skill Level': task.skill_level.name,
                'Dependencies': deps_str,
                'Deps Status': deps_status_str
            })

        # Create DataFrame
        df = pd.DataFrame(schedule_data)
        
        # Print both traditional format and DataFrame
        print("\nTraditional Format:")
        print("\nTask                  Start Date       End Date         Priority    Role                    Skill Level    Dependencies                    Deps Status")
        print("-" * 140)
        
        for data in schedule_data:
            print(f"{data['Task']:<20} "
                  f"{data['Start Date']}  "
                  f"{data['End Date']}  "
                  f"{data['Priority']:<10} "
                  f"{data['Role']:<24} "
                  f"{data['Skill Level']:<12} "
                  f"{data['Dependencies']:<30} "
                  f"{data['Deps Status']}")

        print(f"\nProject Duration: {solver.Value(max_end)} days")
        
        print("\nPandas DataFrame Format:")
        # Print DataFrame with styling
        print(df.to_string(index=False))
        
        # Save to Excel and CSV
        # df.to_excel("project_schedule.xlsx", index=False)
        # df.to_csv("project_schedule.csv", index=False)
        
    else:
        print("No solution found.")

if __name__ == "__main__":
    main()