from ortools.sat.python import cp_model
import pandas as pd
from typing import List, Dict, Tuple
import numpy as np

class CourseScheduler:
    def __init__(self, num_days: int, num_time_slots: int):
        self.model = cp_model.CpModel()
        self.num_days = num_days
        self.num_time_slots = num_time_slots
        
    def setup_data_structures(self,
                            professors: List[str],
                            classrooms: List[str],
                            courses: List[str],
                            course_durations: Dict[str, int],
                            professor_course_times: Dict[Tuple[str, str], int],
                            classroom_equipment: Dict[str, List[str]],
                            course_required_equipment: Dict[str, List[str]],
                            room_setup_time: Dict[str, int],
                            preparation_times: Dict[str, int],
                            room_staff: Dict[str, List[str]],
                            student_classroom_distances: Dict[Tuple[str, str], int],
                            course_base_revenue: Dict[str, float],
                            professor_cost_per_hour: Dict[str, float],
                            classroom_cost_per_hour: Dict[str, float],
                            setup_cost_per_hour: Dict[str, float],
                            time_period_multipliers: Dict[str, float]
                            ):
        
        # Store all input data as class attributes
        self.professors = professors
        self.classrooms = classrooms
        self.courses = courses
        self.course_durations = course_durations
        self.professor_course_times = professor_course_times
        self.classroom_equipment = classroom_equipment
        self.course_required_equipment = course_required_equipment
        self.room_setup_time = room_setup_time
        self.preparation_times = preparation_times
        self.room_staff = room_staff
        self.student_classroom_distances = student_classroom_distances
        self.course_base_revenue = course_base_revenue
        self.professor_cost_per_hour = professor_cost_per_hour
        self.classroom_cost_per_hour = classroom_cost_per_hour
        self.setup_cost_per_hour = setup_cost_per_hour
        self.time_period_multipliers = time_period_multipliers

        # Decision Variables
        self.course_assignment = {}
        for course in courses:
            for classroom in classrooms:
                for day in range(self.num_days):
                    for time in range(self.num_time_slots):
                        var_name = f'course_{course}_classroom_{classroom}_day_{day}_time_{time}'
                        self.course_assignment[(course, classroom, day, time)] = self.model.NewBoolVar(var_name)

        # Each course must be scheduled exactly once
        for course in courses:
            course_vars = []
            for classroom in classrooms:
                for day in range(self.num_days):
                    for time in range(self.num_time_slots):
                        course_vars.append(self.course_assignment[(course, classroom, day, time)])
            self.model.Add(sum(course_vars) == 1)

        # Equipment Compatibility
        for course in courses:
            for classroom in classrooms:
                required_equipment = course_required_equipment[course]
                available_equipment = classroom_equipment[classroom]
                if not all(eq in available_equipment for eq in required_equipment):
                    for day in range(self.num_days):
                        for time in range(self.num_time_slots):
                            self.model.Add(self.course_assignment[(course, classroom, day, time)] == 0)

        # Time Slot Conflicts
        for classroom in classrooms:
            for day in range(self.num_days):
                for t1 in range(self.num_time_slots):
                    for course1 in courses:
                        duration1 = course_durations[course1]
                        total_duration = duration1 + room_setup_time[classroom]
                        
                        for t2 in range(max(0, t1 - total_duration + 1), min(t1 + total_duration, self.num_time_slots)):
                            for course2 in courses:
                                if course1 != course2:
                                    self.model.Add(
                                        self.course_assignment[(course1, classroom, day, t1)] + 
                                        self.course_assignment[(course2, classroom, day, t2)] <= 1
                                    )

        # Professor Availability
        for professor in professors:
            for day in range(self.num_days):
                for t1 in range(self.num_time_slots):
                    professor_courses = []
                    for course in courses:
                        for classroom in classrooms:
                            if (professor, course) in professor_course_times:
                                duration = professor_course_times[(professor, course)]
                                for t2 in range(max(0, t1 - duration + 1), min(t1 + duration, self.num_time_slots)):
                                    professor_courses.append(self.course_assignment[(course, classroom, day, t2)])
                    
                    if professor_courses:
                        self.model.Add(sum(professor_courses) <= 1)

        # Teaching Hours
        for course in courses:
            for classroom in classrooms:
                for day in range(self.num_days):
                    for time in range(self.num_time_slots):
                        if time + course_durations[course] + room_setup_time[classroom] > self.num_time_slots:
                            self.model.Add(self.course_assignment[(course, classroom, day, time)] == 0)

        # Revenue Maximization Objective
        obj_terms = []
        for course in courses:
            for classroom in classrooms:
                for day in range(self.num_days):
                    for time in range(self.num_time_slots):
                        revenue_value = self.calculate_revenue(course, classroom, time)
                        assignment_var = self.course_assignment[(course, classroom, day, time)]

                        # Create an intermediate variable for the revenue contribution
                        revenue_term = self.model.NewIntVar(-10000000, 10000000, f'revenue_{course}_{classroom}_{day}_{time}')

                        # Link the revenue term to the assignment variable
                        self.model.Add(revenue_term == assignment_var * revenue_value)

                        obj_terms.append(revenue_term)

        self.model.Maximize(sum(obj_terms))

    def calculate_revenue(self, course, classroom, time):
        """Calculate the net revenue for a course"""
        time_period = self.get_time_period(time)
        period_multiplier = self.time_period_multipliers[time_period]
        
        # Revenue
        revenue = self.course_base_revenue[course] * period_multiplier
        
        # Costs
        duration_hours = self.course_durations[course] / 2
        classroom_cost = self.classroom_cost_per_hour[classroom] * duration_hours
        setup_cost = self.setup_cost_per_hour[classroom] * (self.room_setup_time[classroom] / 2)
        
        # Find assigned professor
        assigned_professor = next(professor for professor in self.professors 
                              if (professor, course) in self.professor_course_times)
        professor_cost = self.professor_cost_per_hour[assigned_professor] * duration_hours
        
        return int((revenue - (classroom_cost + setup_cost + professor_cost)) * 100)  # Convert to cents for integer optimization

    def get_time_period(self, time_slot):
        """Determine time period based on time slot"""
        hour = 8 + (time_slot * 30) // 60
        if 8 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 17:
            return 'afternoon'
        else:
            return 'night'

    def solve(self):
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 60.0
        status = solver.Solve(self.model)
        
        print(f"Solver status: {status}")
        print(f"Optimal? {status == cp_model.OPTIMAL}")
        print(f"Feasible? {status == cp_model.FEASIBLE}")
        
        def format_time(time_slot):
            hours = 8 + (time_slot * 30) // 60
            minutes = (time_slot * 30) % 60
            return f"{hours:02d}:{minutes:02d}"
        
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            schedule = []
            total_revenue = 0
            
            for course in self.courses:
                for classroom in self.classrooms:
                    for day in range(self.num_days):
                        for time in range(self.num_time_slots):
                            if solver.Value(self.course_assignment[(course, classroom, day, time)]) == 1:
                                time_period = self.get_time_period(time)
                                period_multiplier = self.time_period_multipliers[time_period]
                                duration_hours = self.course_durations[course] / 2
                                
                                base_revenue = self.course_base_revenue[course] * period_multiplier
                                classroom_cost = self.classroom_cost_per_hour[classroom] * duration_hours
                                setup_cost = self.setup_cost_per_hour[classroom] * (self.room_setup_time[classroom] / 2)
                                assigned_professor = next(professor for professor in self.professors 
                                                     if (professor, course) in self.professor_course_times)
                                professor_cost = self.professor_cost_per_hour[assigned_professor] * duration_hours
                                net_revenue = base_revenue - (classroom_cost + setup_cost + professor_cost)
                                
                                schedule.append({
                                    'Course': course,
                                    'Classroom': classroom,
                                    'Day': day + 1,
                                    'Start_Time': format_time(time),
                                    'End_Time': format_time(time + self.course_durations[course]),
                                    'Time_Period': time_period,
                                    'Duration': f"{duration_hours:.1f} hours",
                                    'Base_Revenue': f"${base_revenue:,.2f}",
                                    'Classroom_Cost': f"${classroom_cost:,.2f}",
                                    'Setup_Cost': f"${setup_cost:,.2f}",
                                    'Professor_Cost': f"${professor_cost:,.2f}",
                                    'Net_Revenue': f"${net_revenue:,.2f}",
                                    'Period_Multiplier': f"{period_multiplier:.1f}x"
                                })
                                total_revenue += net_revenue
            
            df = pd.DataFrame(schedule)
            df = df.sort_values(['Day', 'Start_Time'])
            print(f"\nTotal Net Revenue: ${total_revenue:,.2f}")
            return df
        else:
            print("No solution found!")
            return None

def create_example_schedule():
    scheduler = CourseScheduler(num_days=2, num_time_slots=16)  # 8-hour days, 30-min slots
    
    professors = ['Prof_Smith', 'Prof_Jones', 'Prof_Cohen']
    classrooms = ['Room101', 'Room102']
    courses = ['Math101', 'Physics101', 'Chemistry101', 'Biology101']
    
    course_durations = {
        'Math101': 4,  # 2 hours (4 30-min slots)
        'Physics101': 6,  # 3 hours
        'Chemistry101': 12, # 6 hours
        'Biology101': 10, # 5 hours
    }
    
    professor_course_times = {
        ('Prof_Smith', 'Math101'): 4,
        ('Prof_Jones', 'Physics101'): 6,
        ('Prof_Cohen', 'Chemistry101'): 13,
        ('Prof_Cohen', 'Biology101'): 7,
    }
    
    classroom_equipment = {
        'Room101': ['basic', 'projector'],
        'Room102': ['basic', 'lab_equipment'],
    }
    
    course_required_equipment = {
        'Math101': ['basic'],
        'Physics101': ['basic', 'lab_equipment'],
        'Chemistry101': ['basic', 'lab_equipment'],
        'Biology101': ['basic'],
    }
    
    room_setup_time = {
        'Room101': 2,  # 1 hour
        'Room102': 3,
    }
    
    preparation_times = {
        'Math101': 1,  # 30 min
        'Physics101': 2,
        'Chemistry101': 0.5,
        'Biology101': 1.5,
    }
    
    room_staff = {
        'Room101': ['assistant1', 'assistant2'],
        'Room102': ['assistant3', 'assistant4'],
    }
    
    student_classroom_distances = {
        ('Math101', 'Room101'): 1,
        ('Math101', 'Room102'): 2,
        ('Physics101', 'Room101'): 1,
        ('Physics101', 'Room102'): 2,
        ('Chemistry101', 'Room101'): 0.5,
        ('Biology101', 'Room102'): 2,
    }
    
    course_base_revenue = {
        'Math101': 5000.0,  # Base revenue for each course
        'Physics101': 7500.0,
        'Chemistry101': 12000.0,
        'Biology101': 9000.0,
    }
    
    professor_cost_per_hour = {
        'Prof_Smith': 400.0,  # Hourly rate for each professor
        'Prof_Jones': 450.0,
        'Prof_Cohen': 500.0,
    }
    
    classroom_cost_per_hour = {
        'Room101': 300.0,  # Hourly usage cost for each classroom
        'Room102': 400.0,
    }
    
    setup_cost_per_hour = {
        'Room101': 100.0,  # Hourly setup cost for each classroom
        'Room102': 120.0,
    }
    
    time_period_multipliers = {
        'morning': 1.0,    # Normal rate (8:00-12:00)
        'afternoon': 1.1,  # 10% premium (12:00-17:00)
        'night': 1.5,      # 50% premium (17:00+)
    }
    
    scheduler.setup_data_structures(
        professors=professors,
        classrooms=classrooms,
        courses=courses,
        course_durations=course_durations,
        professor_course_times=professor_course_times,
        classroom_equipment=classroom_equipment,
        course_required_equipment=course_required_equipment,
        room_setup_time=room_setup_time,
        preparation_times=preparation_times,
        room_staff=room_staff,
        student_classroom_distances=student_classroom_distances,
        course_base_revenue=course_base_revenue,
        professor_cost_per_hour=professor_cost_per_hour,
        classroom_cost_per_hour=classroom_cost_per_hour,
        setup_cost_per_hour=setup_cost_per_hour,
        time_period_multipliers=time_period_multipliers
    )
    
    return scheduler.solve()

if __name__ == "__main__":
    print("Testing scheduler...")
    result = create_example_schedule()
    print("\nSchedule:")
    print(result)