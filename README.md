# Constraint Programming Examples

This repository contains various implementations of constraint programming solutions using Google's OR-Tools library. Each project demonstrates different aspects of constraint programming and optimization techniques.

## What is Constraint Programming?

Constraint programming (CP) is a programming paradigm where relations between variables are stated in the form of constraints. It's particularly useful for solving complex combinatorial problems such as:
- Scheduling
- Resource allocation
- Planning
- Optimization

## Why Google OR-Tools?

Google's OR-Tools is a powerful open-source software suite for optimization that includes:
- Constraint Programming solver (CP-SAT)
- Linear/Mixed-Integer Programming solvers
- Vehicle Routing tools
- Graph algorithms

Key advantages:
- High performance
- Active development and maintenance
- Extensive documentation
- Support for multiple programming languages
- Free and open-source
- Industrial-grade reliability

## Projects Overview

### 1. Job Shop Scheduling (`google example/`)
**Problem:** Schedule multiple jobs across different machines while respecting constraints like machine availability and job dependencies.

**Solution Approaches:**
- Constraint Programming implementation (Google's example and Claude's version)
- Mixed Integer Programming implementation
- Demonstrates different mathematical approaches to the same problem

**Key Features:**
- Machine capacity handling
- Job dependency management
- Makespan minimization
- Different solver approaches comparison

### 2. University Course Scheduling (`university_scheduling/`)
**Problem:** Optimize course schedules in a university setting considering multiple constraints:
- Classroom availability
- Professor schedules
- Equipment requirements
- Setup times
- Revenue optimization

**Solution Evolution:**
1. Basic implementation (`cp.py`)
   - Simple time and distance optimization
   - Basic equipment constraints

2. Enhanced version (`cp-claude.py`)
   - Improved constraint modeling
   - Better data structures
   - More realistic scheduling parameters

3. Revenue-optimized version (`cp-claude-2-maximizingCost.py`)
   - Revenue maximization
   - Complex cost modeling
   - Time-based pricing
   - Comprehensive financial reporting

### 3. Project Task Scheduling (`tasks/`)
**Problem:** Schedule complex project tasks with multiple roles, skill levels, and dependencies while optimizing for time and priority.

**Solution Features:**
- Multi-role resource management
- Skill level requirements
- Task priority handling
- Dependency chain resolution
- Timeline optimization

**Key Innovations:**
- Sophisticated role and skill modeling
- Priority-based optimization
- Comprehensive output formats
- Real-world project management constraints

## Technical Implementation Details

### Common Patterns Across Projects
1. **Constraint Modeling**
   - Variable definition
   - Constraint specification
   - Objective function formulation

2. **Solver Usage**
   - CP-SAT solver for constraint programming
   - SCIP solver for mixed integer programming
   - Parameter tuning for performance

3. **Output Handling**
   - Structured data output (pandas DataFrames)
   - Human-readable formatting
   - Solution validation

### Key Differences Between Projects
1. **Problem Complexity**
   - Job Shop: Basic scheduling with clear constraints
   - University Courses: Complex real-world constraints with financial aspects
   - Project Tasks: Multi-dimensional resource management

2. **Optimization Goals**
   - Job Shop: Minimize completion time
   - University Courses: Maximize revenue while respecting constraints
   - Project Tasks: Balance duration and priorities

## Getting Started

### Prerequisites
```python
pip install ortools pandas numpy
```

### Running the Examples
Each directory contains standalone examples that can be run independently. See individual directory READMEs for specific instructions.

## Future Improvements
- Add visualization tools for schedules
- Implement real-time constraint updates
- Add more complex cost models
- Develop web interface for interactive scheduling
- Include more real-world constraints and scenarios

## References
- [Google OR-Tools Documentation](https://developers.google.com/optimization)
- [Constraint Programming Overview](https://en.wikipedia.org/wiki/Constraint_programming)
- [Job Shop Scheduling Problem](https://en.wikipedia.org/wiki/Job_shop_scheduling)
