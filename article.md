# Optimizing University Course Scheduling: A Constraint Programming Approach

> The complete code for this article and more constraint programming examples are available on GitHub: [constraint-programming-examples](https://github.com/orico/constraint-programming-examples)

In today's complex educational landscape, universities face a challenging puzzle: how to efficiently schedule courses while maximizing revenue and satisfying numerous operational constraints. In this article, we'll explore how constraint programming can be used to solve this intricate optimization problem.

## The Challenge

Universities must juggle multiple moving parts when creating course schedules:
- Multiple professors with varying availability and expertise
- Limited classroom resources with different equipment
- Course duration requirements
- Room setup times
- Equipment compatibility
- Time slot conflicts
- Cost considerations
- Revenue optimization

Traditional manual scheduling approaches often lead to suboptimal solutions, leaving money on the table and creating operational inefficiencies.

## Choosing the Right Optimization Approach: Linear Programming vs. CP-SAT

Google OR-Tools provides two powerful approaches for solving optimization problems. Here's a comprehensive comparison:

| Aspect | Linear Programming (LP/MIP) | Constraint Programming (CP-SAT) |
|--------|---------------------------|--------------------------------|
| **Variable Types** | Continuous variables | Primarily boolean and integer variables |
| **Best For** | • Resource allocation with fractional values<br>• Production planning<br>• Financial optimization<br>• Supply chain optimization | • Scheduling problems<br>• Timetabling<br>• Resource assignment<br>• Configuration problems |
| **Constraint Expression** | Must be linear inequalities | Natural logical expressions and rich constraints |
| **Solution Strategy** | Continuous relaxation and branch-and-bound | Boolean satisfaction with learning |
| **Performance Focus** | Finding provably optimal solutions | Finding good solutions quickly |
| **Modeling Complexity** | Complex for logical constraints | Simple for logical and temporal constraints |
| **Built-in Constraints** | Basic linear constraints | Rich set (AllDifferent, Circuit, etc.) |
| **Typical Applications** | • Financial portfolio optimization<br>• Manufacturing planning<br>• Transportation routing | • Course scheduling<br>• Employee shifts<br>• Sports tournaments<br>• Equipment assignment |
| **Strengths** | • Exact optimal solutions<br>• Good with continuous variables<br>• Strong theoretical guarantees | • Natural modeling<br>• Efficient for scheduling<br>• Better with logical constraints<br>• Faster modeling iteration |
| **Limitations** | • Complex for logical constraints<br>• Can be slow for discrete problems | • May not find provably optimal solutions<br>• Less suitable for continuous variables |

### Why We Chose CP-SAT for Course Scheduling

Our university scheduling problem aligns perfectly with CP-SAT's strengths:

1. **Natural Problem Modeling**: Our constraints (no overlap, equipment requirements, professor availability) map directly to CP-SAT's constraint primitives.

2. **Discrete Time Structure**: Our 30-minute time slots fit CP-SAT's integer variable handling, making the model more intuitive and efficient.

3. **Complex Logic**: Our requirements include many logical relationships that would be cumbersome in LP:
   - IF room has equipment THEN course can be scheduled
   - Either course A OR course B can use a room at a time
   - Professor can't be in two places at once

4. **Solution Requirements**: We need good feasible solutions quickly rather than provably optimal solutions, matching CP-SAT's solving approach.

### Deep Dive: Boolean vs. Integer Variables in CP-SAT

CP-SAT offers both boolean and integer variables, each suited for different modeling needs:

| Aspect | Boolean Variables | Integer Variables |
|--------|------------------|-------------------|
| **Value Range** | Only 0 or 1 | Any integer within defined bounds |
| **Memory Usage** | More efficient | Uses more memory |
| **Solving Speed** | Faster to solve | Can be slower to solve |
| **Best For** | • Yes/No decisions<br>• Assignment problems<br>• Mutual exclusion | • Counting<br>• Resource levels<br>• Time slots<br>• Quantities |

#### When to Use Each Type

**Boolean Variables**:
- When modeling binary decisions (is course scheduled in this slot?)
- For mutual exclusion constraints (course can't be in two rooms)
- When you need maximum solving efficiency

Example from our scheduler:
```python
# Boolean: Is Math101 scheduled in Room101 on day 1 at time slot 4?
course_scheduled = model.NewBoolVar('math101_room101_d1_t4')
```

**Integer Variables**:
- When you need to count or accumulate values
- For representing quantities or levels
- When modeling time periods or durations

Example alternative approach:
```python
# Integer: Which time slot (0-15) is Math101 scheduled in Room101 on day 1?
time_slot = model.NewIntVar(0, 15, 'math101_room101_d1_time')
```

#### Real-World Impact

In our course scheduler, we chose boolean variables because:
1. We need to model yes/no decisions for each time slot
2. The problem naturally decomposes into binary choices
3. Boolean variables lead to faster solving times for our scheduling constraints

For example, our core assignment variable is boolean:
```python
self.course_assignment[(course, classroom, day, time)] = self.model.NewBoolVar(var_name)
```

This choice allows us to easily express constraints like:
- A course must be scheduled exactly once (sum of booleans = 1)
- No room conflicts (sum of overlapping booleans ≤ 1)
- Equipment requirements (if equipment missing, boolean = 0)

#### Edge Cases: When One Type Clearly Wins

Here are specific scenarios where one variable type has a clear advantage:

**Boolean Variables Win:**

1. **Sparse Assignment Problems**
```python
# GOOD: Boolean approach for sparse classroom assignments
# Is student i assigned to classroom j? (most combinations are invalid)
student_room[i, j] = model.NewBoolVar(f'student_{i}_room_{j}')
# Easy to add: Only valid combinations get a constraint
model.Add(student_room[invalid_pair] == 0)

# BAD: Integer approach
# Which room (0-100) is student i assigned to?
student_room[i] = model.NewIntVar(0, 100, f'student_{i}_room')
# Harder: Need complex constraints to prevent invalid assignments
model.Add(student_room[i].NotIn(invalid_rooms_for_student[i]))
```

2. **Multiple Independent Yes/No Choices**
```python
# GOOD: Boolean approach for equipment needs
has_projector = model.NewBoolVar('has_projector')
has_whiteboard = model.NewBoolVar('has_whiteboard')
has_computers = model.NewBoolVar('has_computers')
# Easy constraint: Need at least two pieces of equipment
model.Add(sum([has_projector, has_whiteboard, has_computers]) >= 2)

# BAD: Integer approach using bit flags
equipment = model.NewIntVar(0, 7, 'equipment_flags')  # 3 bits
# Complex constraints needed to check individual bits
```

**Integer Variables Win:**

1. **Cumulative Resources**
```python
# BAD: Boolean approach for student count
students_present = [model.NewBoolVar(f'student_{i}') for i in range(100)]
# Complex to enforce: Room capacity between 15-30 students
model.Add(sum(students_present) >= 15)
model.Add(sum(students_present) <= 30)

# GOOD: Integer approach
student_count = model.NewIntVar(15, 30, 'student_count')
# Simple and efficient
```

2. **Sequential Values with Arithmetic**
```python
# BAD: Boolean approach for sequential time slots
time_slots = [model.NewBoolVar(f'slot_{i}') for i in range(24)]
# Complex to ensure 3 consecutive slots
for i in range(22):
    model.Add(sum(time_slots[i:i+3]) == 3).OnlyEnforceIf(time_slots[i])

# GOOD: Integer approach
start_time = model.NewIntVar(0, 21, 'start_time')
# Simple constraint for 3-hour duration
end_time = start_time + 3
```

3. **Resource Allocation with Math**
```python
# BAD: Boolean approach for budget allocation
spend_amounts = [model.NewBoolVar(f'spend_{i*100}') for i in range(1000)]
# Complex to ensure total is exactly $50,000
model.Add(sum(amount * var for amount, var in zip(range(0,100000,100), spend_amounts)) == 50000)

# GOOD: Integer approach
budget = model.NewIntVar(0, 100000, 'budget')
# Simple constraint
model.Add(budget == 50000)
```

These edge cases demonstrate that:
- Boolean variables excel when dealing with yes/no decisions, especially with sparse valid combinations
- Integer variables are superior for representing quantities, ranges, and arithmetic relationships
- The choice can significantly impact both model complexity and solving efficiency

#### Theoretical Guarantees vs. Practical Solutions

**Boolean Variables (SAT Problems)**
- **Theoretical Guarantee**: Complete decision procedures exist
- **Complexity**: NP-complete (proven by Cook-Levin theorem)
- **Solver Behavior**: Will definitively tell you if a solution exists
- **Search Space**: Finite (2^n possible combinations for n variables)
```python
# Boolean formulation guarantees finding a solution if one exists
room_assignments = {
    (course, room): model.NewBoolVar(f'c{course}_r{room}')
    for course in courses for room in rooms
}
# Solver will definitively prove if this is satisfiable
model.Add(sum(room_assignments.values()) == len(courses))
```

**Integer Variables**
- **Theoretical Guarantee**: No complete decision procedure for general integer programming
- **Complexity**: Undecidable in the general case
- **Solver Behavior**: May not terminate for arbitrary constraints
- **Search Space**: Can be infinite for unbounded variables
```python
# Integer formulation might not have theoretical guarantees
start_times = {
    course: model.NewIntVar(0, max_time, f'start_{course}')
    for course in courses
}
# Complex arithmetic constraints might not have guaranteed solutions
model.Add(start_times['math'] + duration['math'] <= start_times['physics'])
```

**Practical Reality**
Despite these theoretical differences, both approaches work well in practice for most real-world problems:

1. **Modern Solvers**:
   - Sophisticated heuristics
   - Learning algorithms
   - Efficient pruning techniques
   - Hybrid approaches

2. **Bounded Problems**:
   - Most real problems have natural bounds
   - Time slots are finite
   - Resources are limited
   - This makes integer problems more tractable

3. **Solution Quality**:
   - Boolean models often find solutions faster
   - Integer models can be more natural to express
   - Both typically work well within reasonable timeouts

4. **Our Course Scheduler**:
   - Uses primarily boolean variables
   - Has natural bounds (time slots, rooms)
   - Consistently finds optimal solutions
   - Solves quickly (under 60 seconds)
```python
# Our approach: Bounded boolean model with timeout
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 60.0
status = solver.Solve(self.model)
# Reliably finds solutions in practice
```

## The Solution: Constraint Programming with OR-Tools

Our solution leverages Google's OR-Tools library, specifically its CP-SAT solver, to create an intelligent scheduling system. This approach allows us to:
1. Model complex real-world constraints
2. Find optimal or near-optimal solutions
3. Balance multiple competing objectives
4. Scale to handle realistic scheduling scenarios

## Key Components of the Solution

### 1. Decision Variables
The core of our model revolves around binary decision variables that represent whether a course is scheduled in a specific:
- Classroom
- Day
- Time slot

### 2. Constraint Types

Our model implements several critical constraints that work together to create a feasible and optimal schedule:

#### 2.1 Course Assignment Constraint
```python
# Each course must be scheduled exactly once
for course in courses:
    course_vars = []
    for classroom in classrooms:
        for day in range(self.num_days):
            for time in range(self.num_time_slots):
                course_vars.append(self.course_assignment[(course, classroom, day, time)])
    self.model.Add(sum(course_vars) == 1)
```
This fundamental constraint ensures that each course is scheduled exactly once across all possible combinations of classrooms, days, and time slots.

#### 2.2 Equipment Compatibility
```python
# Equipment Compatibility Check
for course in courses:
    for classroom in classrooms:
        required_equipment = course_required_equipment[course]
        available_equipment = classroom_equipment[classroom]
        if not all(eq in available_equipment for eq in required_equipment):
            for day in range(self.num_days):
                for time in range(self.num_time_slots):
                    self.model.Add(self.course_assignment[(course, classroom, day, time)] == 0)
```
Example from our scenario:
- Physics101 requires ['basic', 'lab_equipment']
- Room101 only has ['basic', 'projector']
- Therefore, Physics101 cannot be scheduled in Room101

#### 2.3 Time Slot Conflicts
```python
# Prevent overlapping courses in the same classroom
for classroom in classrooms:
    for day in range(self.num_days):
        for t1 in range(self.num_time_slots):
            for course1 in courses:
                duration1 = course_durations[course1]
                total_duration = duration1 + room_setup_time[classroom]
                
                for t2 in range(max(0, t1 - total_duration + 1), 
                              min(t1 + total_duration, self.num_time_slots)):
                    for course2 in courses:
                        if course1 != course2:
                            self.model.Add(
                                self.course_assignment[(course1, classroom, day, t1)] + 
                                self.course_assignment[(course2, classroom, day, t2)] <= 1
                            )
```
This complex constraint handles:
- Course duration (e.g., Chemistry101: 6 hours)
- Room setup time (Room101: 1 hour, Room102: 1.5 hours)
- Preventing overlaps between courses

#### 2.4 Professor Availability
```python
# Ensure professors aren't double-booked
for professor in professors:
    for day in range(self.num_days):
        for t1 in range(self.num_time_slots):
            professor_courses = []
            for course in courses:
                for classroom in classrooms:
                    if (professor, course) in professor_course_times:
                        duration = professor_course_times[(professor, course)]
                        for t2 in range(max(0, t1 - duration + 1), 
                                      min(t1 + duration, self.num_time_slots)):
                            professor_courses.append(
                                self.course_assignment[(course, classroom, day, t2)]
                            )
            
            if professor_courses:
                self.model.Add(sum(professor_courses) <= 1)
```
Example:
- Prof_Cohen teaches both Chemistry101 (6 hours) and Biology101 (5 hours)
- The constraint ensures these courses don't overlap in the professor's schedule

#### 2.5 Teaching Hours and Time Limits
```python
# Ensure courses fit within available time slots
for course in courses:
    for classroom in classrooms:
        for day in range(self.num_days):
            for time in range(self.num_time_slots):
                if time + course_durations[course] + room_setup_time[classroom] > self.num_time_slots:
                    self.model.Add(self.course_assignment[(course, classroom, day, time)] == 0)
```
This constraint prevents scheduling courses that would run past the available time slots, considering both course duration and setup time.

### 3. Revenue Optimization

The model maximizes net revenue by considering:
- Base course revenue
- Time period multipliers (morning: 1.0x, afternoon: 1.1x, night: 1.5x)
- Operational costs:
  - Professor costs per hour
  - Classroom usage costs
  - Setup costs

## Example Scenario

Our example includes:
- 3 professors (Prof. Smith, Jones, and Cohen)
- 2 classrooms (Room101 and Room102)
- 4 courses (Math101, Physics101, Chemistry101, Biology101)
- Different equipment requirements (basic, projector, lab equipment)
- Varying course durations (2-6 hours)
- Different cost structures and revenue potential

### Sample Course Parameters
- Math101: 2 hours, basic equipment, $5,000 base revenue
- Physics101: 3 hours, lab equipment, $7,500 base revenue
- Chemistry101: 6 hours, lab equipment, $12,000 base revenue
- Biology101: 5 hours, basic equipment, $9,000 base revenue

## Results and Analysis

The solver successfully produced an optimal schedule that maximizes net revenue while satisfying all constraints. Let's analyze the actual results:

### Optimized Schedule

| Course       | Classroom | Day | Time  | Duration | Net Revenue | Period |
|-------------|-----------|-----|-------|----------|-------------|---------|
| Chemistry101| Room102   | 1   | 08:30 | 6 hours  | $6,420.00  | Morning |
| Math101     | Room101   | 1   | 13:00 | 2 hours  | $4,000.00  | Afternoon |
| Biology101  | Room101   | 2   | 10:00 | 5 hours  | $4,900.00  | Morning |
| Physics101  | Room102   | 2   | 11:30 | 3 hours  | $4,770.00  | Morning |

**Total Net Revenue: $20,090.00**

### Key Observations

1. **Time Period Optimization**
   - Math101 is scheduled in the afternoon (1.1x multiplier)
   - Most courses are in morning slots (1.0x multiplier)
   - No courses scheduled during premium night hours (1.5x multiplier)

2. **Room Allocation**
   - Room102 (with lab equipment) is used for Chemistry101 and Physics101
   - Room101 (with projector) is used for Math101 and Biology101
   - Equipment requirements are perfectly matched

3. **Professor Scheduling**
   - Prof_Cohen's long courses (Chemistry101 and Biology101) are split across different days
   - No professor has overlapping schedules
   - Teaching loads are well-distributed

4. **Financial Breakdown Example (Chemistry101)**
   - Base Revenue: $12,000.00
   - Morning Multiplier: 1.0x
   - Setup Cost: $180.00
   - Professor Cost: $3,000.00
   - Net Revenue: $6,420.00

5. **Constraint Satisfaction**
   - All courses fit within working hours
   - Setup times are properly accounted for
   - No scheduling conflicts
   - All equipment requirements are met

The solution demonstrates how the constraint programming approach successfully balances multiple competing objectives while maintaining all operational requirements. The total net revenue of $20,090.00 represents the optimal achievable value given the constraints and cost structures.

## Summary

Constraint programming provides a powerful approach to solving complex university scheduling problems. By modeling real-world constraints and optimizing for revenue while respecting operational requirements, we can create more efficient and profitable course schedules.

The solution is flexible and can be adapted to different university settings by adjusting:
- Number of classrooms and their equipment
- Professor availability and expertise
- Course requirements and durations
- Cost structures and revenue models
- Time period preferences

This approach demonstrates how modern optimization techniques can transform traditional educational scheduling from a manual, time-consuming process into an automated, revenue-optimizing solution.
