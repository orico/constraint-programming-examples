# University Course Scheduling Directory

This directory contains implementations of a university course scheduling system using constraint programming with Google's OR-Tools library.

## Files Overview

### `cp.py`
The base implementation of a course scheduling system.

Key features:
- Schedules courses across multiple classrooms and days
- Handles multiple professors with different specialties
- Basic constraints for classroom equipment compatibility
- Simple objective function focusing on minimizing time and distance

### `cp-claude.py`
An enhanced version of the course scheduler with more sophisticated constraints and data structures.

Key features:
- Object-oriented implementation with `CourseScheduler` class
- Comprehensive constraint handling:
  - Equipment compatibility
  - Time slot conflicts
  - Professor availability
  - Teaching hours
- Detailed scheduling output using pandas DataFrame
- More realistic scheduling parameters

### `cp-claude-2-maximizingCost.py`
The most advanced implementation focusing on revenue optimization and cost management.

Key features:
- Builds upon the previous implementation
- Advanced revenue modeling including:
  - Course base revenue
  - Professor hourly rates
  - Classroom usage costs
  - Setup costs
  - Time period multipliers (morning/afternoon/night)
- Comprehensive financial reporting
- Enhanced scheduling constraints
- Detailed output with financial metrics

## Technical Details

### Common Features Across Files
All implementations include:
- Multiple classrooms
- Multiple professors
- Equipment constraints
- Setup time handling
- Time slot management

### Key Differences
1. **Objective Functions**
   - `cp.py`: Minimizes total time and distance
   - `cp-claude.py`: Minimizes total duration with weighted priorities
   - `cp-claude-2-maximizingCost.py`: Maximizes revenue while considering costs

2. **Constraint Complexity**
   - Progressively more sophisticated constraints from `cp.py` to `cp-claude-2-maximizingCost.py`
   - More realistic business rules in later versions

3. **Output Detail**
   - Basic output in `cp.py`
   - Structured DataFrame output in `cp-claude.py`
   - Comprehensive financial and scheduling reports in `cp-claude-2-maximizingCost.py`

## Usage
Each file can be run independently and includes example data. The later versions (`cp-claude.py` and `cp-claude-2-maximizingCost.py`) provide more detailed and useful output for real-world applications.