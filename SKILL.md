---
name: ar4-robot-control
description: >
  Control the Annin Robotics AR4 6-DOF robot arm via ROS2 and MoveIt2. Use this skill whenever
  the user wants to command a robot arm, plan robot motions, move to positions, pick and place
  objects, control a gripper, run robot sequences, or automate physical tasks with the AR4. Also
  trigger when the user mentions "AR4", "robot arm", "move the arm", "pick up", "place", "gripper",
  "go to pose", "home position", "joint angles", "cartesian path", "MoveIt", or "ROS2 robot".
  This skill enables Claude Code to be the brain that translates natural language into real robot
  motion via ROS2 topics, services, and MoveIt2 planning.
---

# AR4 Robot Control via Claude Code

This skill enables Claude Code to control an Annin Robotics AR4 6-DOF robot arm through
ROS2 and MoveIt2. Claude interprets natural-language commands and translates them into
ROS2 actions: motion planning, joint commands, gripper control, and task sequences.

## Architecture Overview

```
User (natural language) → Claude Code → Python ROS2 scripts → MoveIt2 / AR4 Driver → Robot
```

Claude Code generates and executes Python scripts that communicate with the running ROS2
stack. The AR4 driver and MoveIt2 must already be running before Claude sends commands.

## Prerequisites

Before using this skill, the user must have:

1. **Hardware**: AR4 robot (MK1/MK2/MK3) assembled, wired, and calibrated
2. **Software stack running**:
   - ROS 2 Jazzy (Ubuntu 24.04) or Humble (Ubuntu 22.04)
   - `ar4_ros_driver` package built and sourced: https://github.com/ycheng517/ar4_ros_driver
   - AR4 driver launched (real or sim)
   - MoveIt2 launched

If the user hasn't started the stack, guide them through it (see `references/setup.md`).

## Quick Reference: Launch Commands

```bash
# Real robot
ros2 launch annin_ar4_driver driver.launch.py calibrate:=True ar_model:=mk3
ros2 launch annin_ar4_moveit_config moveit.launch.py ar_model:=mk3

# Simulation (Gazebo)
ros2 launch annin_ar4_gazebo gazebo.launch.py
ros2 launch annin_ar4_moveit_config moveit.launch.py use_sim_time:=true
```

## How Claude Code Controls the Robot

Claude generates standalone Python scripts that use **ROS2 CLI commands** and/or the
**MoveIt2 Python API (moveit_py)** or **ROS2 topic/service calls** to command the robot.

There are three primary control methods, in order of preference:

### Method 1: ROS2 CLI (Simplest — good for quick actions)

```bash
# Publish a gripper command
ros2 topic pub --once /gripper_controller/commands std_msgs/msg/Float64MultiArray "{data: [0.04]}"

# Call the E-Stop reset
ros2 run annin_ar4_driver reset_estop.sh mk3

# Check joint states
ros2 topic echo --once /joint_states
```

### Method 2: Python with subprocess ROS2 calls (Reliable, no import issues)

Generate a Python script that shells out to `ros2 action send_goal` or `ros2 topic pub`.
This avoids needing the ROS2 Python environment active in Claude Code's shell.

```python
import subprocess, json

def send_joint_goal(joint_positions):
    """Send a joint trajectory goal to the arm controller."""
    goal = {
        "trajectory": {
            "joint_names": [
                "joint_1", "joint_2", "joint_3",
                "joint_4", "joint_5", "joint_6"
            ],
            "points": [{
                "positions": joint_positions,
                "time_from_start": {"sec": 3, "nanosec": 0}
            }]
        }
    }
    cmd = [
        "ros2", "action", "send_goal",
        "/joint_trajectory_controller/follow_joint_trajectory",
        "control_msgs/action/FollowJointTrajectory",
        json.dumps(goal)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result.stdout, result.stderr
```

### Method 3: moveit_py Python API (Most powerful — full motion planning)

When the user needs collision-aware planning, Cartesian paths, or complex motions,
generate a script using the moveit_py API. See `references/moveit_py_patterns.md` for
complete patterns.

```python
#!/usr/bin/env python3
"""Example: Move AR4 to a named pose using moveit_py."""
import rclpy
from rclpy.node import Node
from moveit.planning import MoveItPy

def main():
    rclpy.init()
    ar4 = MoveItPy(node_name="ar4_claude_commander")
    arm = ar4.get_planning_component("ar_manipulator")

    # Plan to a named target (defined in SRDF)
    arm.set_start_state_to_current_state()
    arm.set_goal_state(configuration_name="home")
    plan_result = arm.plan()

    if plan_result:
        ar4.execute(plan_result.trajectory, controllers=[])
        print("SUCCESS: Moved to home position")
    else:
        print("ERROR: Planning failed")

    rclpy.shutdown()

if __name__ == "__main__":
    main()
```

## AR4 Robot Specifications

| Property | Value |
|---|---|
| DOF | 6 |
| Reach | 24.75 in (62.9 cm) |
| Payload | 4.15 lb (1.9 kg) |
| Repeatability | 0.2 mm |
| Weight (aluminum) | 27 lb (12.25 kg) |
| Controller | Teensy 4.1 |
| Gripper controller | Arduino Nano |
| Communication | USB Serial (Teensy: /dev/ttyACM0, Nano: /dev/ttyUSB0) |

## Joint Names and Planning Groups

The AR4 URDF defines these joints and groups:

**Planning group**: `ar_manipulator`
**Joints**: `joint_1`, `joint_2`, `joint_3`, `joint_4`, `joint_5`, `joint_6`
**End effector link**: `link_6` (or `gripper_link` if gripper is attached)
**Base link**: `base_link`

**Gripper group** (if servo gripper installed): `ar_gripper`
- Gripper open: position ~0.04
- Gripper closed: position ~0.0

## Common Command Patterns

When the user says something like the commands below, generate the appropriate script:

| User says | Claude does |
|---|---|
| "go home" / "home position" | Plan and execute to named target "home" |
| "move to [x, y, z]" | Set pose goal with position, plan, execute |
| "move joint 3 to 45 degrees" | Set joint goal with specific joint angle |
| "open/close gripper" | Publish to gripper controller topic |
| "pick up the object at [x,y,z]" | Sequence: approach → open gripper → move down → close → lift |
| "move in a straight line to [x,y,z]" | Compute Cartesian path, execute |
| "what's the current position?" | Read /joint_states or compute FK |
| "stop" / "e-stop" | Call emergency stop service |
| "calibrate" | Guide through calibration launch |
| "slower" / "faster" | Adjust velocity/acceleration scaling factors |

## Safety Rules

ALWAYS follow these rules when generating robot commands:

1. **Never skip planning** — Always plan before executing. Never publish raw joint
   positions without going through a trajectory controller.
2. **Use conservative speeds** — Default to `max_velocity_scaling_factor=0.3` and
   `max_acceleration_scaling_factor=0.3`. Only increase if user explicitly asks.
3. **Confirm destructive actions** — Before first execution on real hardware, ask
   user to confirm. Print the planned trajectory summary before executing.
4. **Check joint states first** — Before planning, read current joint states to
   verify the robot is in a known state.
5. **Gripper safety** — When picking objects, always verify gripper is open before
   approaching, and closed before lifting.
6. **E-Stop awareness** — If execution fails, suggest checking E-Stop state and
   offer the reset command.
7. **Workspace limits** — The AR4 has 24.75" reach. Reject goals clearly outside
   the workspace rather than letting the planner fail silently.

## Workflow for Handling a User Command

1. Parse the intent (move, pick, place, query state, configure, etc.)
2. Check if the ROS2 stack is presumed running (ask if first interaction)
3. Choose the appropriate control method (CLI, subprocess, moveit_py)
4. Generate a complete, self-contained Python script
5. Show the user what the script will do in plain English
6. Execute the script (or let the user run it if they prefer)
7. Report the result and current robot state

## Reference Files

Read these for detailed patterns and troubleshooting:

- `references/setup.md` — Full setup and launch instructions
- `references/moveit_py_patterns.md` — MoveIt2 Python API code patterns
- `references/ros2_topics_services.md` — All available ROS2 topics, services, actions
- `references/troubleshooting.md` — Common errors and fixes
