# AR4 ROS2 Topics, Services, and Actions

## Topics

### Published by the Driver

| Topic | Type | Description |
|---|---|---|
| `/joint_states` | `sensor_msgs/msg/JointState` | Current joint positions, velocities, efforts |
| `/robot_description` | `std_msgs/msg/String` | URDF robot model |
| `/tf` | `tf2_msgs/msg/TFMessage` | Transform tree |
| `/tf_static` | `tf2_msgs/msg/TFMessage` | Static transforms |

### Controller Topics

| Topic | Type | Description |
|---|---|---|
| `/joint_trajectory_controller/joint_trajectory` | `trajectory_msgs/msg/JointTrajectory` | Direct trajectory input |
| `/joint_trajectory_controller/state` | `control_msgs/msg/JointTrajectoryControllerState` | Controller state |
| `/gripper_controller/commands` | `std_msgs/msg/Float64MultiArray` | Gripper position command |

### MoveIt Topics

| Topic | Type | Description |
|---|---|---|
| `/move_group/display_planned_path` | `moveit_msgs/msg/DisplayTrajectory` | Planned path for RViz |
| `/monitored_planning_scene` | `moveit_msgs/msg/PlanningScene` | Current planning scene |
| `/planning_scene` | `moveit_msgs/msg/PlanningScene` | Planning scene updates |

## Actions

| Action | Type | Description |
|---|---|---|
| `/joint_trajectory_controller/follow_joint_trajectory` | `control_msgs/action/FollowJointTrajectory` | Execute a joint trajectory |
| `/move_action` | `moveit_msgs/action/MoveGroup` | MoveIt move group action |

## Services

| Service | Type | Description |
|---|---|---|
| `/compute_ik` | `moveit_msgs/srv/GetPositionIK` | Inverse kinematics |
| `/compute_fk` | `moveit_msgs/srv/GetPositionFK` | Forward kinematics |
| `/get_planning_scene` | `moveit_msgs/srv/GetPlanningScene` | Get current planning scene |
| `/apply_planning_scene` | `moveit_msgs/srv/ApplyPlanningScene` | Modify planning scene |
| `/plan_kinematic_path` | `moveit_msgs/srv/GetMotionPlan` | Plan a motion |

## Useful CLI Commands

### Checking System State

```bash
# List all running nodes
ros2 node list

# List all topics
ros2 topic list

# List active controllers
ros2 control list_controllers

# Check joint states (single reading)
ros2 topic echo --once /joint_states

# Monitor joint states (continuous)
ros2 topic echo /joint_states

# Check controller state
ros2 topic echo --once /joint_trajectory_controller/state
```

### Inspecting the Robot Model

```bash
# Get URDF
ros2 topic echo --once /robot_description

# List all TF frames
ros2 run tf2_tools view_frames

# Check specific transform
ros2 run tf2_ros tf2_echo base_link link_6
```

### Calling Services

```bash
# Compute forward kinematics
ros2 service call /compute_fk moveit_msgs/srv/GetPositionFK \
  "{header: {frame_id: 'base_link'}, fk_link_names: ['link_6'], robot_state: {joint_state: {name: ['joint_1','joint_2','joint_3','joint_4','joint_5','joint_6'], position: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]}}}"

# Get planning scene
ros2 service call /get_planning_scene moveit_msgs/srv/GetPlanningScene "{}"
```

### Sending Commands

```bash
# Send a joint trajectory goal
ros2 action send_goal /joint_trajectory_controller/follow_joint_trajectory \
  control_msgs/action/FollowJointTrajectory \
  "{trajectory: {joint_names: ['joint_1','joint_2','joint_3','joint_4','joint_5','joint_6'], points: [{positions: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], time_from_start: {sec: 3}}]}}"

# Open gripper
ros2 topic pub --once /gripper_controller/commands std_msgs/msg/Float64MultiArray "{data: [0.04]}"

# Close gripper
ros2 topic pub --once /gripper_controller/commands std_msgs/msg/Float64MultiArray "{data: [0.0]}"

# E-Stop reset
ros2 run annin_ar4_driver reset_estop.sh mk3
```

## Joint Names Reference

| Joint | Name | Description |
|---|---|---|
| J1 | `joint_1` | Base rotation |
| J2 | `joint_2` | Shoulder |
| J3 | `joint_3` | Elbow |
| J4 | `joint_4` | Wrist rotation |
| J5 | `joint_5` | Wrist pitch |
| J6 | `joint_6` | Tool rotation |
| Gripper | `gripper_joint` | Servo gripper (if installed) |

## Frame IDs

| Frame | Description |
|---|---|
| `base_link` | Robot base (world-fixed) |
| `link_1` | After joint 1 |
| `link_2` | After joint 2 |
| `link_3` | After joint 3 |
| `link_4` | After joint 4 |
| `link_5` | After joint 5 |
| `link_6` | End effector / tool mount |
| `gripper_link` | Gripper tip (if gripper attached) |
