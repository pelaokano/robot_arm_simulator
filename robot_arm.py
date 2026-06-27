"""
robot_arm.py — Clase Python para controlar el simulador 3D de brazo robot.

Uso:
    from robot_arm import RobotArm
    import time

    arm = RobotArm()           # abre browser y espera conexión
    arm.set_angle(0, 45)
    arm.move_to(15, 5, 20)
    arm.open_gripper()
"""

import time
import math
import webbrowser
import threading

import server

_started     = False
_start_lock  = threading.Lock()


def _ensure_server():
    global _started
    with _start_lock:
        if not _started:
            server.start()
            webbrowser.open("http://127.0.0.1:8080")
            print("[RobotArm] Esperando que el browser conecte...", end="", flush=True)
            ok = server.wait_for_browser(timeout=30)
            if ok:
                print(" conectado.")
            else:
                print(" timeout (verifica que el browser abrió http://127.0.0.1:8080)")
            _started = True


class RobotArm:
    """
    Controla el simulador 3D del brazo robot via WebSocket.

    Joints:
        J0  base yaw        [-190, +190] deg
        J1  shoulder pitch  [ -90,  +90] deg
        J2  elbow pitch     [-135,  +45] deg
        J3  forearm roll    [ -90,  +75] deg
        J4  wrist pitch     [-139,  +90] deg
        J5  wrist roll      [-188, +181] deg

    Gripper: 0.0 = cerrado, 1.0 = completamente abierto
    """

    LIMITS = [
        (-190, 190), (-90, 90), (-135, 45),
        (-90,   75), (-139, 90), (-188, 181),
    ]

    def __init__(self):
        _ensure_server()
        self._angles  = [0.0] * 6
        self._gripper = 0.0
        self.reset()

    # ── interno ───────────────────────────────────────────────

    def _send(self, msg: dict):
        server.send(msg)
        time.sleep(0.025)   # dar tiempo al browser para procesar

    def _clamp(self, j: int, deg: float) -> float:
        lo, hi = self.LIMITS[j]
        return max(lo, min(hi, deg))

    # ── control de joints ─────────────────────────────────────

    def reset(self):
        """Todos los joints a cero, pinza cerrada."""
        self._angles  = [0.0] * 6
        self._gripper = 0.0
        self._send({"type": "set_joints", "angles": self._angles})
        self._send({"type": "set_gripper", "value": 0.0})
        return self

    def set_angle(self, joint: int, deg: float):
        """Mueve un joint a la posición indicada en grados."""
        if not 0 <= joint <= 5:
            raise ValueError(f"joint debe ser 0-5, recibido: {joint}")
        self._angles[joint] = self._clamp(joint, deg)
        self._send({"type": "set_joints", "angles": self._angles})
        return self

    def set_joints(self, angles: list):
        """Establece los 6 joints simultáneamente (grados)."""
        if len(angles) != 6:
            raise ValueError("Se necesitan exactamente 6 ángulos")
        self._angles = [self._clamp(i, a) for i, a in enumerate(angles)]
        self._send({"type": "set_joints", "angles": self._angles})
        return self

    def get_joints(self) -> list:
        """Retorna los ángulos actuales en grados."""
        return list(self._angles)

    # ── cinemática inversa ────────────────────────────────────

    def move_to(self, x: float, y: float, z: float,
                rx: float = math.pi, ry: float = 0.0, rz: float = 0.0):
        """Mueve el TCP a la posición cartesiana usando IK."""
        self._send({"type": "move_to",
                    "x": x, "y": y, "z": z,
                    "rx": rx, "ry": ry, "rz": rz})
        return self

    def get_tcp(self) -> list:
        """Retorna la posición del TCP [x, y, z] calculada con FK."""
        return self._fk(self._angles)

    # ── pinza ─────────────────────────────────────────────────

    def open_gripper(self):
        return self.set_gripper(1.0)

    def close_gripper(self):
        return self.set_gripper(0.0)

    def set_gripper(self, opening: float):
        """0.0 = cerrada, 1.0 = completamente abierta."""
        self._gripper = max(0.0, min(1.0, opening))
        self._send({"type": "set_gripper", "value": self._gripper})
        return self

    def get_gripper(self) -> float:
        return self._gripper

    # ── trayectorias ──────────────────────────────────────────

    def sweep(self, joint: int, start: float, end: float,
              steps: int = 30, delay: float = 0.04):
        """Mueve un joint de start a end en pasos suaves."""
        for i in range(steps + 1):
            t = i / steps
            self.set_angle(joint, start + (end - start) * t)
            time.sleep(delay)
        return self

    def trajectory(self, waypoints: list, delay: float = 0.4):
        """Lista de posiciones articulares (cada una: 6 ángulos en grados)."""
        for wp in waypoints:
            self.set_joints(wp)
            time.sleep(delay)
        return self

    def cartesian_trajectory(self, points: list, delay: float = 0.4):
        """Lista de posiciones cartesianas [x,y,z]."""
        for pt in points:
            self.move_to(*pt)
            time.sleep(delay)
        return self

    # ── FK local ──────────────────────────────────────────────

    def _fk(self, deg: list) -> list:
        GEO = [[4.8,0,7.3],[0,0,13],[1,0,2],[12.6,0,0],[3.6,0,0]]
        R = [d * math.pi / 180 for d in deg]
        a,b = math.cos(R[0]),math.sin(R[0])
        c,d_,e = GEO[0]
        f,g = math.cos(R[1]),math.sin(R[1])
        h,i_,j = GEO[1]
        k,l = math.cos(R[2]),math.sin(R[2])
        m,n,o = GEO[2]
        p,q = math.cos(R[3]),math.sin(R[3])
        r,s,t = GEO[3]
        u,v = math.cos(R[4]),math.sin(R[4])
        w,x,y = GEO[4]
        J = [[0]*3 for _ in range(6)]
        J[1] = [a*c-b*d_, b*c+a*d_, e]
        J[2] = [J[1][0]+a*f*h-b*i_+a*g*j,
                J[1][1]+b*f*h+a*i_+b*g*j,
                J[1][2]-g*h+f*j]
        J[3] = [J[2][0]+a*f*k*m-a*g*l*m-b*n+a*g*k*o+a*f*l*o,
                J[2][1]+b*f*k*m-b*g*l*m+a*n+b*g*k*o+b*f*l*o,
                J[2][2]-g*k*m-f*l*m+f*k*o-g*l*o]
        J[4] = [J[3][0]+a*f*k*r-a*g*l*r-b*p*s+a*g*k*q*s+a*f*l*q*s+a*g*k*p*t+a*f*l*p*t+b*q*t,
                J[3][1]+b*f*k*r-b*g*l*r+a*p*s+b*g*k*q*s+b*f*l*q*s+b*g*k*p*t+b*f*l*p*t-a*q*t,
                J[3][2]-g*k*r-f*l*r+f*k*q*s-g*l*q*s+f*k*p*t-g*l*p*t]
        J[5] = [
            J[4][0]+a*f*k*u*w-a*g*l*u*w-a*g*k*p*v*w-a*f*l*p*v*w-b*q*v*w
                   -b*p*x+a*g*k*q*x+a*f*l*q*x+a*g*k*p*u*y+a*f*l*p*u*y+b*q*u*y+a*f*k*v*y-a*g*l*v*y,
            J[4][1]+b*f*k*u*w-b*g*l*u*w-b*g*k*p*v*w-b*f*l*p*v*w+a*q*v*w
                   +a*p*x+b*g*k*q*x+b*f*l*q*x+b*g*k*p*u*y+b*f*l*p*u*y-a*q*u*y+b*f*k*v*y-b*g*l*v*y,
            J[4][2]-g*k*u*w-f*l*u*w-f*k*p*v*w+g*l*p*v*w+f*k*q*x
                   -g*l*q*x+f*k*p*u*y-g*l*p*u*y-g*k*v*y-f*l*v*y
        ]
        return [round(J[5][0],3), round(J[5][1],3), round(J[5][2],3)]

    # ── context manager ───────────────────────────────────────

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.reset()
