# AR4 Robot Setup & Launch Guide

## Installation

### 1. Install ROS 2

For Ubuntu 24.04, install ROS 2 Jazzy:
```bash
# Follow: https://docs.ros.org/en/jazzy/Installation.html
```

For Ubuntu 22.04, install ROS 2 Humble:
```bash
# Follow: https://docs.ros.org/en/humble/Installation.html
# Use the humble branch: https://github.com/ycheng517/ar4_ros_driver/tree/humble
```

### 2. Clone and Build the AR4 ROS Driver

```bash
mkdir -p ~/ar4_ws/src
cd ~/ar4_ws/src
git clone https://github.com/ycheng517/ar4_ros_driver
cd ~/ar4_ws

# Install dependencies
rosdep install --from-paths src --ignore-src -r -y

# Build
colcon build
source install/setup.bash

# Add to bashrc for convenience
echo "source ~/ar4_ws/install/setup.bash" >> ~/.bashrc
```

### 3. Enable Serial Port Access

```bash
sudo addgroup $USER dialout
# Log out and back in for this to take effect
```

### 4. Flash Firmware

Flash the Teensy and Arduino Nano using Arduino IDE following the standard AR4 procedure.
The firmware sketches are in `annin_ar4_firmware/`. You need the Bounce2 library installed
in Arduino IDE.

## Launching the Robot

### Real Robot

Terminal 1 — Start the driver (with calibration on first run):
```bash
source ~/ar4_ws/install/setup.bash
ros2 launch annin_ar4_driver driver.launch.py \
    calibrate:=True \
    ar_model:=mk3 \
    include_gripper:=True \
    serial_port:=/dev/ttyACM0 \
    arduino_serial_port:=/dev/ttyUSB0
```

Terminal 2 — Start MoveIt and RViz:
```bash
source ~/ar4_ws/install/setup.bash
ros2 launch annin_ar4_moveit_config moveit.launch.py \
    ar_model:=mk3 \
    include_gripper:=True
```

### Simulated Robot (Gazebo)

Terminal 1 — Start Gazebo:
```bash
source ~/ar4_ws/install/setup.bash
ros2 launch annin_ar4_gazebo gazebo.launch.py
```

Terminal 2 — Start MoveIt:
```bash
source ~/ar4_ws/install/setup.bash
ros2 launch annin_ar4_moveit_config moveit.launch.py \
    use_sim_time:=true \
    include_gripper:=True
```

### MoveIt Demo Only (No Hardware or Sim)

```bash
source ~/ar4_ws/install/setup.bash
ros2 launch annin_ar4_moveit_config demo.launch.py
```

## Launch Arguments Reference

### driver.launch.py
| Argument | Default | Description |
|---|---|---|
| `ar_model` | `mk3` | Robot model: mk1, mk2, mk3 |
| `calibrate` | `False` | Run joint calibration on startup |
| `include_gripper` | `True` | Enable servo gripper |
| `serial_port` | `/dev/ttyACM0` | Teensy serial port |
| `arduino_serial_port` | `/dev/ttyUSB0` | Arduino Nano serial port |

### moveit.launch.py
| Argument | Default | Description |
|---|---|---|
| `ar_model` | `mk3` | Robot model: mk1, mk2, mk3 |
| `include_gripper` | `True` | Enable servo gripper |
| `use_sim_time` | `False` | Use Gazebo sim time |

## Calibration Notes

- Calibration is **required** after flashing firmware or power cycling the robot/Teensy
- Can skip on subsequent runs with `calibrate:=False`
- The robot will move each joint to its limit switch during calibration
- Keep the workspace clear during calibration

## Docker Option

```bash
cd ~/ar4_ws/src/ar4_ros_driver
docker build -t ar4_ros_driver .

# Requires rocker: pip install rocker
rocker --ssh --x11 \
    --devices /dev/ttyUSB0 /dev/ttyACM0 \
    --volume $(pwd):/ar4_ws/src/ar4_ros_driver -- \
    ar4_ros_driver bash
```

## Verifying the Stack is Running

Claude Code should verify these before sending commands:

```bash
# Check if driver node is running
ros2 node list | grep -i ar4

# Check joint states are being published
ros2 topic echo --once /joint_states

# Check MoveIt is running
ros2 node list | grep move_group

# Check available controllers
ros2 control list_controllers
```

## E-Stop

Press the physical E-Stop button to immediately halt the robot. To reset:
```bash
ros2 run annin_ar4_driver reset_estop.sh mk3
```
