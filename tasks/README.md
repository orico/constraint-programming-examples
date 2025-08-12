# Tasks Directory

This directory contains an implementation of a project task scheduler using constraint programming with Google's OR-Tools library.

## File Overview

### `cp.py`
A sophisticated project management and task scheduling system designed for complex projects with multiple roles and dependencies.

Key features:
- Comprehensive task modeling with:
  - Multiple professional roles (Full Stack, Backend, Frontend, DevOps, etc.)
  - Skill levels (Junior to Expert)
  - Task priorities (Low to Critical)
  - Task dependencies
  - Duration estimates

### Technical Details

#### Class Structure
1. **Enums**
   - `SkillLevel`: JUNIOR, INTERMEDIATE, SENIOR, EXPERT
   - `Priority`: LOW, MEDIUM, HIGH, CRITICAL
   - `Role`: Various professional roles (FULLSTACK, BACKEND, FRONTEND, etc.)

2. **Task Class**
   - Encapsulates task properties:
     - Task ID
     - Duration
     - Required role
     - Skill level
     - Priority
     - Dependencies

#### Key Features
1. **Project Timeline Management**
   - Handles project start dates
   - Manages task dependencies
   - Calculates realistic timelines

2. **Resource Constraints**
   - Prevents role conflicts (same role can't work on multiple tasks simultaneously)
   - Respects skill level requirements
   - Handles task dependencies

3. **Optimization**
   - Minimizes project duration
   - Prioritizes critical tasks
   - Balances resource utilization

4. **Output Formats**
   - Traditional text format
   - Pandas DataFrame
   - Optional Excel/CSV export

#### Scheduling Algorithm
- Uses CP-SAT solver
- Creates variables for task start and end times
- Implements constraints for:
  - Task dependencies
  - Resource availability
  - Project timeline
- Optimizes for both project duration and task priorities

## Usage
The file includes example project data and can be run directly. It will output a detailed project schedule showing:
- Task assignments
- Start and end dates
- Dependencies and their status
- Role assignments
- Skill level requirements
- Priority levels

The output is provided in both traditional text format and as a pandas DataFrame for further analysis or export.
