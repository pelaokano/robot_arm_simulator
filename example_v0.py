"""
example.py — Example usage of RobotArm class.
Run: python example.py
"""
import time
import math
from robot_arm import RobotArm

arm = RobotArm()
time.sleep(1.0)  # wait for browser to open

# ── Basic joint control ───────────────────────────────────
arm.reset()
time.sleep(0.5)

arm.set_angle(0, 60)    # rotate base
time.sleep(0.3)
arm.set_angle(1, -30)   # shoulder down
time.sleep(0.3)
arm.set_angle(2, 20)    # elbow
time.sleep(0.3)

# ── Gripper ───────────────────────────────────────────────
arm.open_gripper()
time.sleep(0.4)
arm.close_gripper()
time.sleep(0.4)

# ── Sweep animation ───────────────────────────────────────
arm.sweep(0, -90, 90, steps=40, delay=0.03)

# ── Trajectory ────────────────────────────────────────────
arm.trajectory([
    [0,    0,   0, 0, 0, 0],
    [30, -20,  10, 0, 0, 0],
    [60, -40,  30, 0, 0, 0],
    [90, -30,  20, 0, 0, 0],
    [0,    0,   0, 0, 0, 0],
], delay=0.3)

# ── IK cartesian move ─────────────────────────────────────
arm.move_to(15, 5, 20)
time.sleep(0.5)
print("TCP:", arm.get_tcp())
print("Joints:", arm.get_joints())

# ── Pick & place pattern ──────────────────────────────────
def pick(x, y, z):
    arm.move_to(x, y, z + 5)
    time.sleep(0.3)
    arm.open_gripper()
    arm.move_to(x, y, z)
    time.sleep(0.2)
    arm.close_gripper()
    time.sleep(0.2)

def place(x, y, z):
    arm.move_to(x, y, z + 5)
    time.sleep(0.3)
    arm.move_to(x, y, z)
    time.sleep(0.2)
    arm.open_gripper()
    time.sleep(0.2)

pick(12, 0, 10)
place(-8, 10, 10)
arm.reset()
