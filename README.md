# AR4 Robot Control — Claude Code Skill

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill that lets you control an **Annin Robotics AR4 6-DOF robot arm** using natural language. Claude interprets your commands and translates them into ROS2 actions — motion planning, joint moves, gripper control, pick-and-place sequences, and more — through MoveIt2 and the AR4 ROS driver.

```
You (natural language) → Claude Code → Python / ROS2 CLI → MoveIt2 / AR4 Driver → Robot
```

## Demo

```
> move the arm to home position
> pick up the object at [0.3, 0.1, 0.05] and place it at [0.3, -0.1, 0.05]
> open the gripper
> move joint 3 to 45 degrees
> what's the current position?
```

Claude generates and executes the appropriate ROS2 commands or MoveIt2 Python scripts for each request.

---

## Prerequisites

| Requirement | Details |
|---|---|
| **Hardware** | AR4 robot (MK1, MK2, or MK3) — assembled, wired, and calibrated |
| **OS** | Ubuntu 24.04 (Jazzy) or Ubuntu 22.04 (Humble) |
| **ROS 2** | Jazzy or Humble installed and sourced |
| **AR4 driver** | [`ar4_ros_driver`](https://github.com/ycheng517/ar4_ros_driver) built in a colcon workspace |
| **Claude Code** | Installed and working ([docs](https://docs.anthropic.com/en/docs/claude-code)) |

> No physical robot? You can use the **Gazebo simulation** or the **MoveIt demo** mode (see [Setup](#launching-the-ros2-stack)).

---

## Installation

### 1. Install the Skill

Clone this repo into your Claude Code skills directory:

```bash
# Create the skills directory if it doesn't exist
mkdir -p ~/.claude/skills

# Clone
git clone https://github.com/sardoru/AR4-robot-skill.git ~/.claude/skills/ar4-robot-control
```

The skill is active immediately — restart Claude Code or start a new session to pick it up.

### 2. Install the AR4 ROS2 Stack (if not already done)

```bash
mkdir -p ~/ar4_ws/src
cd ~/ar4_ws/src
git clone https://github.com/ycheng517/ar4_ros_driver

cd ~/ar4_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build
source install/setup.bash

# Add to shell startup
echo "source ~/ar4_ws/install/setup.bash" >> ~/.bashrc
```

Enable serial port access (log out and back in afterwards):

```bash
sudo addgroup $USER dialout
```

See [`references/setup.md`](references/setup.md) for the full setup guide including firmware flashing and Docker options.

---

## Launching the ROS2 Stack

Before talking to Claude, the AR4 driver and MoveIt2 must be running.

### Real Robot

```bash
# Terminal 1 — Driver
ros2 launch annin_ar4_driver driver.launch.py \
    calibrate:=True ar_model:=mk3 include_gripper:=True

# Terminal 2 — MoveIt + RViz
ros2 launch annin_ar4_moveit_config moveit.launch.py \
    ar_model:=mk3 include_gripper:=True
```

### Simulation (Gazebo)

```bash
# Terminal 1 — Gazebo
ros2 launch annin_ar4_gazebo gazebo.launch.py

# Terminal 2 — MoveIt
ros2 launch annin_ar4_moveit_config moveit.launch.py use_sim_time:=true
```

### MoveIt Demo Only (no hardware or sim)

```bash
ros2 launch annin_ar4_moveit_config demo.launch.py
```

### Verify the Stack

Run the included health check:

```bash
python3 ~/.claude/skills/ar4-robot-control/references/health_check.py
```

Expected output when everything is running:

```
==================================================
AR4 ROS2 Stack Health Check
==================================================
  ✓ ROS2 Nodes: All essential nodes found
  ✓ Joint States: Joint states OK
  ✓ Controllers: Controllers OK
  ✓ MoveIt2: MoveIt OK
==================================================
✓ Stack is READY — all checks passed
```

---

## Usage

Once the stack is running, open Claude Code and give natural-language commands:

| You say | Claude does |
|---|---|
| "go home" | Plans and executes move to the SRDF-defined home pose |
| "move to [0.3, 0.0, 0.2]" | Sets a Cartesian pose goal, plans, and executes |
| "move joint 3 to 45 degrees" | Sets a joint-space goal for joint\_3 |
| "open gripper" / "close gripper" | Publishes to the gripper controller topic |
| "pick up the object at [x,y,z]" | Runs a full pick sequence: approach, open, descend, close, lift |
| "place it at [x,y,z]" | Runs a place sequence: move, descend, open, retreat |
| "move in a straight line to [x,y,z]" | Computes and executes a Cartesian path |
| "what's the current position?" | Reads `/joint_states` or computes forward kinematics |
| "stop" / "e-stop" | Calls the emergency stop reset service |
| "slower" / "faster" | Adjusts velocity and acceleration scaling factors |

Claude chooses the best control method automatically:

1. **ROS2 CLI** — for quick, simple actions (gripper, echo joint states)
2. **Python + subprocess** — for reliable trajectory commands without needing ROS2 Python packages in Claude's shell
3. **moveit\_py API** — for full motion planning with collision avoidance, Cartesian paths, and complex sequences

---

## Robot Specifications

| Property | Value |
|---|---|
| Degrees of freedom | 6 |
| Reach | 62.9 cm (24.75 in) |
| Payload | 1.9 kg (4.15 lb) |
| Repeatability | 0.2 mm |
| Weight (aluminum) | 12.25 kg (27 lb) |
| Controller board | Teensy 4.1 |
| Gripper controller | Arduino Nano |
| Communication | USB Serial — Teensy: `/dev/ttyACM0`, Nano: `/dev/ttyUSB0` |

### Joint Layout

| Joint | ROS Name | Function |
|---|---|---|
| J1 | `joint_1` | Base rotation |
| J2 | `joint_2` | Shoulder |
| J3 | `joint_3` | Elbow |
| J4 | `joint_4` | Wrist rotation |
| J5 | `joint_5` | Wrist pitch |
| J6 | `joint_6` | Tool rotation |
| Gripper | `gripper_joint` | Servo gripper (optional) |

**Planning group**: `ar_manipulator`
**End effector link**: `link_6` (or `gripper_link` with gripper)
**Base link**: `base_link`

---

## Safety

The skill enforces these rules on every command:

1. **Always plan before executing** — raw joint positions are never published directly
2. **Conservative default speeds** — velocity and acceleration scaling default to 0.3 (30%)
3. **Confirmation on first real-hardware execution** — Claude prints the planned trajectory and asks before moving
4. **Joint state check** — current state is read before every plan to ensure the robot is in a known configuration
5. **Gripper safety** — gripper is verified open before approaching an object, and closed before lifting
6. **E-Stop awareness** — if execution fails, Claude suggests checking and resetting the E-Stop
7. **Workspace enforcement** — goals clearly outside the 62.9 cm reach are rejected before planning

---

## File Structure

```
ar4-robot-control/
├── SKILL.md                            # Skill definition (loaded by Claude Code)
├── README.md                           # This file
└── references/
    ├── setup.md                        # Full installation & launch guide
    ├── moveit_py_patterns.md           # MoveIt2 Python API code templates
    ├── ros2_topics_services.md         # All ROS2 topics, services, and actions
    ├── troubleshooting.md              # Common errors and fixes
    └── health_check.py                 # Stack readiness checker
```

### Reference Docs

| File | Contents |
|---|---|
| [`setup.md`](references/setup.md) | ROS2 installation, workspace build, driver launch, Gazebo sim, Docker, calibration notes |
| [`moveit_py_patterns.md`](references/moveit_py_patterns.md) | Ready-to-use Python patterns: named poses, joint goals, Cartesian goals, straight-line paths, gripper control, pick-and-place, collision objects, multi-waypoint trajectories, and subprocess fallbacks |
| [`ros2_topics_services.md`](references/ros2_topics_services.md) | Complete listing of every ROS2 topic, service, and action exposed by the AR4 driver and MoveIt2, plus useful CLI commands |
| [`troubleshooting.md`](references/troubleshooting.md) | Fixes for planning failures, controller issues, serial port problems, E-Stop, gripper, Gazebo crashes, and performance tuning |
| [`health_check.py`](references/health_check.py) | Python script that checks nodes, joint states, controllers, and MoveIt availability — run before sending commands |

---

## Troubleshooting

| Problem | Quick Fix |
|---|---|
| Planning fails immediately | Check MoveIt is running: `ros2 node list \| grep move_group` |
| Robot doesn't move after plan | Reset E-Stop: `ros2 run annin_ar4_driver reset_estop.sh mk3` |
| "No IK solution" | Target is outside 62.9 cm reach or orientation is infeasible |
| Serial port permission denied | `sudo addgroup $USER dialout` then log out/in |
| Gripper unresponsive | Verify Arduino Nano is connected and `include_gripper:=True` was passed |
| Controllers inactive | `ros2 control set_controller_state joint_trajectory_controller active` |

See [`references/troubleshooting.md`](references/troubleshooting.md) for the full guide.

---

## Links

- [Annin Robotics AR4](https://www.anninrobotics.com/) — official site
- [ar4_ros_driver](https://github.com/ycheng517/ar4_ros_driver) — ROS2 driver by ycheng517
- [MoveIt2 Documentation](https://moveit.picknik.ai/main/index.html)
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code)

---

## License

This skill is provided as-is for use with Claude Code. The AR4 hardware design is by [Annin Robotics](https://www.anninrobotics.com/). The ROS2 driver is maintained by [ycheng517](https://github.com/ycheng517/ar4_ros_driver). Refer to their respective licenses for terms.
