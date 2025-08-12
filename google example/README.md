# Google Example Directory

This directory contains examples of constraint programming and linear programming implementations using Google's OR-Tools library.

## Files Overview

### `job scheduler google.py`
An implementation of a job shop scheduling problem using Google's OR-Tools CP-SAT solver. This is the original example from Google's documentation.

Key features:
- Uses CP-SAT solver for constraint satisfaction
- Schedules jobs across multiple machines
- Handles job dependencies and machine constraints
- Minimizes makespan (total completion time)
- Includes detailed output formatting

### `job scheduler_claude.py`
A reimplementation of the job shop scheduling problem with a cleaner structure and additional features.

Key features:
- Similar core functionality to Google's example
- Improved code organization
- Enhanced output formatting
- More intuitive variable naming
- Clearer constraint definitions

### `linear programming by claude.py`
An alternative implementation of the job shop scheduling problem using Mixed Integer Programming (MIP) instead of Constraint Programming.

Key features:
- Uses SCIP solver for mixed integer programming
- Different mathematical approach to the same problem
- Binary variables for sequencing decisions
- Big-M formulation for disjunctive constraints
- Similar output format for comparison

## Technical Details

### Common Features Across Files
- All implementations handle:
  - Multiple jobs with varying durations
  - Multiple machines with different capabilities
  - Job precedence constraints
  - Machine capacity constraints
  - Makespan minimization

### Key Differences
1. **CP vs MIP Approach**
   - CP (job scheduler files): Uses constraint programming with interval variables
   - MIP (linear programming file): Uses binary variables and big-M constraints

2. **Solver Usage**
   - CP-SAT solver for constraint programming implementations
   - SCIP solver for mixed integer programming implementation

3. **Performance Characteristics**
   - CP approach: Better for scheduling problems with complex time constraints
   - MIP approach: More suitable for problems with linear relationships

## Usage
Each file can be run independently. They all include example data and will output a formatted schedule showing the optimal assignment of jobs to machines over time.
