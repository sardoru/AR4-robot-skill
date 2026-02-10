#!/usr/bin/env python3
"""
AR4 ROS2 Stack Health Check
Run this to verify the AR4 ROS2 stack is ready for commands.
"""
import subprocess
import sys
import json


def run(cmd, timeout=10):
    """Run a shell command and return stdout."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return result.stdout.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "TIMEOUT", -1


def check_nodes():
    """Check for essential ROS2 nodes."""
    stdout, rc = run("ros2 node list")
    if rc != 0:
        return False, "Cannot communicate with ROS2. Is ROS2 running?"

    nodes = stdout.split("\n")
    checks = {
        "move_group": False,
        "controller_manager": False,
        "robot_state_publisher": False,
    }

    for node in nodes:
        for key in checks:
            if key in node:
                checks[key] = True

    missing = [k for k, v in checks.items() if not v]
    if missing:
        return False, f"Missing nodes: {', '.join(missing)}"
    return True, f"All essential nodes found ({len(nodes)} total)"


def check_joint_states():
    """Check if joint states are being published."""
    stdout, rc = run("ros2 topic echo --once /joint_states", timeout=5)
    if rc != 0 or "TIMEOUT" in stdout:
        return False, "No joint states received (is the driver running?)"
    return True, "Joint states OK"


def check_controllers():
    """Check if controllers are active."""
    stdout, rc = run("ros2 control list_controllers")
    if rc != 0:
        return False, "Cannot list controllers"

    if "joint_trajectory_controller" not in stdout:
        return False, "joint_trajectory_controller not found"

    if "[active]" not in stdout:
        return False, "Controllers not active"

    return True, "Controllers OK"


def check_moveit():
    """Check if MoveIt planning service is available."""
    stdout, rc = run("ros2 service list | grep plan_kinematic_path")
    if rc != 0 or "plan_kinematic_path" not in stdout:
        return False, "MoveIt planning service not available"
    return True, "MoveIt OK"


def main():
    print("=" * 50)
    print("AR4 ROS2 Stack Health Check")
    print("=" * 50)

    checks = [
        ("ROS2 Nodes", check_nodes),
        ("Joint States", check_joint_states),
        ("Controllers", check_controllers),
        ("MoveIt2", check_moveit),
    ]

    all_ok = True
    results = {}

    for name, check_fn in checks:
        ok, msg = check_fn()
        status = "✓" if ok else "✗"
        print(f"  {status} {name}: {msg}")
        results[name] = {"ok": ok, "message": msg}
        if not ok:
            all_ok = False

    print("=" * 50)
    if all_ok:
        print("✓ Stack is READY — all checks passed")
    else:
        print("✗ Stack NOT READY — fix the issues above")
        print("\nQuick fix:")
        print("  # Terminal 1: Start driver")
        print("  ros2 launch annin_ar4_driver driver.launch.py calibrate:=True")
        print("  # Terminal 2: Start MoveIt")
        print("  ros2 launch annin_ar4_moveit_config moveit.launch.py")

    # Output machine-readable result
    print(f"\n__RESULT__:{json.dumps({'ready': all_ok, 'checks': results})}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
