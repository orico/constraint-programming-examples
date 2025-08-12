from ortools.sat.python import cp_model

# Create the model
model = cp_model.CpModel()

# Define constants and parameters
num_courses = 10
num_professors = 5
num_classrooms = 4
num_days = 30  # Planning is done every month (30 days)

# Example data
course_durations = [90, 120, 60, 45, 75, 30, 110, 50, 95, 80]  # in minutes
professor_efficiency = [1.0, 1.2, 1.1, 0.9, 1.3]  # teaching efficiency multipliers
room_setup_times = [30, 20, 25, 15]  # in minutes
course_equipment_requirements = [0, 1, 2, 0, 1, 3, 2, 1, 0, 3]  # 0: basic, 1: computer lab, 2: science lab, 3: multimedia
classroom_equipment_types = [0, 1, 2, 3]  # matching equipment types
classroom_distances = [5, 10, 3, 8, 7, 6, 2, 4, 9, 1]  # distance from main building

# Variables
assignment = {}
start_times = {}
end_times = {}

for day in range(num_days):
    for course in range(num_courses):
        for professor in range(num_professors):
            for classroom in range(num_classrooms):
                assignment[(day, course, professor, classroom)] = model.NewBoolVar(
                    f'assignment_d{day}_c{course}_p{professor}_r{classroom}'
                )
        start_times[(day, course)] = model.NewIntVar(0, 1440, f'start_time_d{day}_c{course}')
        end_times[(day, course)] = model.NewIntVar(0, 1440, f'end_time_d{day}_c{course}')

# Constraints

# Each course must be assigned to one professor and one classroom on a given day
for day in range(num_days):
    for course in range(num_courses):
        model.Add(sum(assignment[(day, course, professor, classroom)]
                      for professor in range(num_professors)
                      for classroom in range(num_classrooms)) == 1)

# Each classroom can only handle one course at a time per day
# for day in range(num_days):
#     for classroom in range(num_classrooms):
#         for time_slot in range(1440):  # Time slots in a day (in minutes)
#             model.Add(
#                 sum(assignment[(day, course, professor, classroom)]
#                     for course in range(num_courses)
#                     for professor in range(num_professors)
#                     if time_slot >= start_times[(day, course)] and time_slot < end_times[(day, course)]) <= 1
#             )

for day in range(num_days):
    for classroom in range(num_classrooms):
        for time_slot in range(1440):  # Time slots in a day (in minutes)
            # Create a Boolean variable for whether the classroom is used at this time slot
            is_classroom_used = model.NewBoolVar(f'is_classroom_{classroom}_used_at_{time_slot}_day_{day}')
            
            # Sum of courses assigned to this classroom at this time slot should be <= 1
            model.Add(
                sum(
                    assignment[(day, course, professor, classroom)]
                    for course in range(num_courses)
                    for professor in range(num_professors)
                ) <= 1
            ).OnlyEnforceIf(is_classroom_used)


# Enforce classroom equipment compatibility
for day in range(num_days):
    for course in range(num_courses):
        for classroom in range(num_classrooms):
            if course_equipment_requirements[course] != classroom_equipment_types[classroom]:
                model.Add(
                    sum(assignment[(day, course, professor, classroom)]
                        for professor in range(num_professors)) == 0
                )

# Calculate end times based on start times, course durations, and professor efficiency
# for day in range(num_days):
#     for course in range(num_courses):
#         for professor in range(num_professors):
#             duration = int(course_durations[course] / professor_efficiency[professor])
#             model.Add(end_times[(day, course)] == start_times[(day, course)] + duration).OnlyEnforceIf(
#                 sum(assignment[(day, course, professor, classroom)]
#                     for classroom in range(num_classrooms)) >= 1
#             )
for day in range(num_days):
    for course in range(num_courses):
        for professor in range(num_professors):
            for classroom in range(num_classrooms):
                is_assigned = assignment[(day, course, professor, classroom)]

                # Define the duration adjustment based on professor efficiency
                duration = int(course_durations[course] / professor_efficiency[professor])

                # Ensure `start_times` and `end_times` are linked to assignments
                model.Add(end_times[(day, course)] == start_times[(day, course)] + duration).OnlyEnforceIf(is_assigned)

                # Ensure courses not assigned to this professor/classroom are ignored
                model.Add(start_times[(day, course)] == 0).OnlyEnforceIf(is_assigned.Not())
                model.Add(end_times[(day, course)] == 0).OnlyEnforceIf(is_assigned.Not())


# Objective: Minimize the total time and distance
model.Minimize(
    sum(end_times[(day, course)] - start_times[(day, course)] for day in range(num_days) for course in range(num_courses)) +
    sum(classroom_distances[classroom] * assignment[(day, course, professor, classroom)]
        for day in range(num_days)
        for course in range(num_courses)
        for professor in range(num_professors)
        for classroom in range(num_classrooms))
)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print solution
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print('Optimal schedule:')
    for day in range(num_days):
        for course in range(num_courses):
            for professor in range(num_professors):
                for classroom in range(num_classrooms):
                    if solver.Value(assignment[(day, course, professor, classroom)]):
                        print(f'Day {day}: Course {course} assigned to Professor {professor} in Classroom {classroom}')
                        print(f'Start Time: {solver.Value(start_times[(day, course)])}')
                        print(f'End Time: {solver.Value(end_times[(day, course)])}')
else:
    print('No solution found.')
