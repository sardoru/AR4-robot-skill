# AR4 Troubleshooting Guide

## Common Issues and Fixes

### "No executors available" / Planning fails immediately

**Cause**: MoveIt2 or the driver is not running.

**Fix**:
```bash
# Check if move_group is running
ros2 node list | grep move_group

# Check if driver is running
ros2 node list | grep ar4

# Relaunch if needed (see references/setup.md)
```

### "Could not find controller" / Controller not active

**Cause**: ros2_control controllers not loaded or inactive.

**Fix**:
```bash
# List controllers and their states
ros2 control list_controllers

# If joint_trajectory_controller is inactive:
ros2 control set_controller_state joint_trajectory_controller active
```

### Robot doesn't move after "plan succeeded"

**Cause**: Often an E-Stop condition or controller issue.

**Fix**:
```bash
# Reset E-Stop
ros2 run annin_ar4_driver reset_estop.sh mk3

# Check controller state
ros2 topic echo --once /joint_trajectory_controller/state
```

### "No IK solution found" / Planning fails for pose goal

**Cause**: Target pose is outside the robot's workspace or unreachable.

**Fix**:
- Verify the target is within the 62.9 cm (24.75 in) reach
- Try a different orientation — some orientations are kinematically infeasible
- Check if collision objects are blocking the path
- Try joint-space goal instead of Cartesian pose

### Serial port permission denied

**Cause**: User not in dialout group.

**Fix**:
```bash
sudo addgroup $USER dialout
# Then log out and log back in
```

### Serial port not found (/dev/ttyACM0 or /dev/ttyUSB0)

**Cause**: Teensy or Arduino not connected, or different port assigned.

**Fix**:
```bash
# List serial ports
ls -la /dev/ttyACM* /dev/ttyUSB*

# Check dmesg for recent USB connections
dmesg | grep -i tty | tail -20

# Adjust launch arguments:
ros2 launch annin_ar4_driver driver.launch.py serial_port:=/dev/ttyACM1
```

### Joint offsets / Robot looks misaligned after homing

**Cause**: Joint offsets need tuning.

**Fix**: Edit the offset file for your model:
```bash
# For MK3:
nano ~/ar4_ws/src/ar4_ros_driver/annin_ar4_driver/config/joint_offsets/mk3.yaml
```
Adjust values and rebuild: `colcon build --packages-select annin_ar4_driver`

### Gazebo crashes or physics unstable

**Fix**:
- Ensure you're using the correct Gazebo version for your ROS2 distro
- Check GPU drivers are properly installed
- Try reducing the real-time factor

### MoveIt planning is very slow

**Fix**:
- Reduce the number of planning attempts
- Use a faster planner (RRTConnect is usually fast)
- Reduce collision objects in the scene
- Set a shorter planning time limit

### Gripper doesn't respond

**Cause**: Arduino Nano not connected or firmware not flashed.

**Fix**:
```bash
# Check if Arduino is connected
ls /dev/ttyUSB*

# Verify gripper controller is loaded
ros2 control list_controllers | grep gripper

# Ensure include_gripper:=True was passed to launch files
```

### Velocity Control vs Position Control

By default the driver uses velocity-based control (smoother, faster). If you have
issues, switch to position control:

Edit `~/ar4_ws/src/ar4_ros_driver/annin_ar4_driver/config/driver.yaml`:
```yaml
velocity_control_enabled: false
```

Then rebuild and relaunch. Note: with position control, reduce velocity and
acceleration scaling for larger motions.

## Diagnostic Commands

```bash
# Full system check
echo "=== Nodes ==="
ros2 node list

echo "=== Controllers ==="
ros2 control list_controllers

echo "=== Joint States ==="
ros2 topic echo --once /joint_states

echo "=== TF Frames ==="
ros2 run tf2_ros tf2_echo base_link link_6
```

## Logs

```bash
# View move_group logs
ros2 node info /move_group

# Check ROS2 log files
ls ~/.ros/log/latest/
```
