"""
example.py — Demo del brazo robot.

INSTRUCCIONES:
1. Ejecutar: python example.py
2. El browser abre automaticamente http://127.0.0.1:8080
3. Esperar mensaje "[RobotArm] Esperando que el browser conecte... conectado."
4. El demo comienza automaticamente

Si el browser no abre solo: abrir manualmente http://127.0.0.1:8080

REQUISITO: ninguno (solo Python stdlib)
"""

import time
import math
from robot_arm import RobotArm

print("=" * 50)
print("  ROBOT ARM SIMULATOR DEMO")
print("=" * 50)
print("Iniciando servidor...")
print("Si el browser no abre, ir a: http://127.0.0.1:8080")
print()

arm = RobotArm()
print()

def sep(t): print(f"\n{'─'*40}\n  {t}\n{'─'*40}")
def wait(s=0.5): time.sleep(s)

# ── 1. Reset ──────────────────────────────────────
sep("1. Reset")
arm.reset(); wait(1)

# ── 2. Joints individuales ────────────────────────
sep("2. Joints individuales")

print("  J0 — base")
arm.sweep(0, 0, 90, steps=30, delay=0.04)
arm.sweep(0, 90, -90, steps=50, delay=0.03)
arm.sweep(0, -90, 0, steps=30, delay=0.04)
wait()

print("  J1 — hombro")
arm.sweep(1, 0, -60, steps=25, delay=0.05)
arm.sweep(1, -60, 0, steps=25, delay=0.05)
wait()

print("  J2 — codo")
arm.set_angle(1, -30)
arm.sweep(2, 0, 40, steps=20, delay=0.05)
arm.sweep(2, 40, -90, steps=30, delay=0.04)
arm.sweep(2, -90, 0, steps=30, delay=0.04)
arm.set_angle(1, 0); wait()

print("  J3 — roll muneca")
arm.set_angle(1, -30); arm.set_angle(2, 20)
arm.sweep(3, 0, 75, steps=25, delay=0.05)
arm.sweep(3, 75, -90, steps=40, delay=0.04)
arm.sweep(3, -90, 0, steps=25, delay=0.05)
wait()

print("  J4 — pitch muneca")
arm.sweep(4, 0, 80, steps=25, delay=0.05)
arm.sweep(4, 80, -100, steps=40, delay=0.04)
arm.sweep(4, -100, 0, steps=25, delay=0.05)
arm.set_angle(1, 0); arm.set_angle(2, 0); wait()

print("  J5 — roll fino")
arm.set_angle(1, -20); arm.set_angle(2, 15)
arm.sweep(5, 0, 180, steps=40, delay=0.04)
arm.sweep(5, 180, -180, steps=60, delay=0.03)
arm.sweep(5, -180, 0, steps=40, delay=0.04)
arm.reset(); wait()

# ── 3. Pinza ──────────────────────────────────────
sep("3. Pinza")
arm.set_angle(1, -30); arm.set_angle(2, 10); wait(0.4)
arm.open_gripper(); wait(0.6)
arm.close_gripper(); wait(0.6)
for v in [0,.2,.4,.6,.8,1,.8,.6,.4,.2,0]:
    arm.set_gripper(v); time.sleep(0.15)
arm.reset(); wait()

# ── 4. IK ─────────────────────────────────────────
sep("4. Cinematica inversa")
for x,y,z in [(15,0,25),(20,0,15),(10,10,20),(-10,10,20),(0,15,15),(15,0,10)]:
    print(f"    move_to({x},{y},{z})")
    arm.move_to(x,y,z); wait(0.7)
arm.reset(); wait()

# ── 5. Trayectoria ────────────────────────────────
sep("5. Trayectoria articular")
arm.trajectory([
    [  0,  0,  0, 0,  0,  0],
    [ 45,-20, 10, 0,  0,  0],
    [ 90,-40, 30, 0, 30,  0],
    [ 45,-50, 20, 0, 60, 45],
    [  0,-30,  0, 0, 30,  0],
    [-45,-20, 10, 0,  0,-45],
    [-90,-40, 30, 0, 30,  0],
    [  0,  0,  0, 0,  0,  0],
], delay=0.5); wait()

# ── 6. Onda sinusoidal ────────────────────────────
sep("6. Onda sinusoidal")
N = 60
for i in range(N+1):
    t = 2*math.pi*i/N
    arm.set_joints([70*math.sin(t), 40*math.sin(2*t), 25*math.sin(3*t),
                    60*math.cos(t), 50*math.sin(2*t+1), 80*math.cos(3*t)])
    arm.set_gripper(0.5+0.5*math.sin(t))
    time.sleep(0.05)
arm.close_gripper(); arm.reset(); wait()

# ── 7. Pick & place ───────────────────────────────
sep("7. Pick and place")

def approach(x,y,z,h=6): arm.move_to(x,y,z+h); wait(0.35)
def pick(x,y,z):
    approach(x,y,z); arm.open_gripper(); wait(0.2)
    arm.move_to(x,y,z); wait(0.2); arm.close_gripper(); wait(0.25)
    approach(x,y,z)
def place(x,y,z):
    approach(x,y,z); arm.move_to(x,y,z); wait(0.2)
    arm.open_gripper(); wait(0.25); approach(x,y,z)

arm.reset(); wait(0.4)
pick(12, 0, 10); place(-8,10,10); wait(0.2)
pick(-8,10,10); place(5,12,10); wait(0.2)
pick(5,12,10); place(12,0,10)
arm.reset(); wait()

# ── 8. Barrido 360 ───────────────────────────────
sep("8. Barrido 360 grados")
arm.set_angle(1,-25); arm.set_angle(2,15); wait(0.3)
arm.sweep(0,-180,180,steps=80,delay=0.03)
arm.sweep(0,180,0,steps=40,delay=0.03)
arm.reset(); wait()

sep("Demo completada")
print(f"  TCP:    {arm.get_tcp()}")
print(f"  Joints: {[round(j,1) for j in arm.get_joints()]}")
print()
print("  Presiona Ctrl+C para salir.")
try:
    while True: time.sleep(1)
except KeyboardInterrupt:
    arm.reset()
    print("Saliendo.")
