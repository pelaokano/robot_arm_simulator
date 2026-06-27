# Robot Arm Simulator

Simulador 3D de brazo robot de 6 DOF controlable desde Python. Basado en [glumb/robot-gui](https://github.com/glumb/robot-gui), con cinemática inversa analítica, pinza tipo langosta y control via HTTP desde cualquier script Python.

![Robot Arm Simulator](https://img.shields.io/badge/Python-3.8%2B-blue) ![No dependencies](https://img.shields.io/badge/dependencies-none-green) ![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

---

## Estructura del proyecto

```
robot_arm/
├── robot_arm.py          # Clase principal de control
├── server.py             # Servidor HTTP (stdlib, sin dependencias)
├── robot_simulator.html  # Simulador 3D (Three.js)
├── example.py            # Demo completo de movimientos
└── README.md
```

---

## Requisitos

- Python 3.8 o superior
- Sin dependencias externas — solo biblioteca estándar de Python
- Cualquier browser moderno (Chrome, Firefox, Edge)

---

## Inicio rápido

```bash
python example.py
```

El simulador abre automáticamente en el browser. El demo recorre todos los movimientos disponibles.

---

## Uso desde tu propio script

```python
from robot_arm import RobotArm
import time

arm = RobotArm()      # abre browser y espera conexión
time.sleep(1)

# Control de joints
arm.set_angle(0, 45)       # J0 base: 45 grados
arm.set_angle(1, -30)      # J1 hombro: -30 grados
arm.set_angle(2, 20)       # J2 codo: 20 grados

# Cinemática inversa
arm.move_to(15, 5, 20)     # mover TCP a posición (x, y, z)

# Pinza
arm.open_gripper()
arm.set_gripper(0.5)       # 50% abierto
arm.close_gripper()

# Trayectorias
arm.sweep(0, -90, 90)      # barrido de J0 de -90 a 90 grados

arm.reset()
```

---

## Arquitectura

```
[Tu script Python]
       |
   robot_arm.py   ──→  encola comandos
       |
   server.py      ──→  HTTP server en puerto 8080
       |
   browser        ──→  robot_simulator.html
                        polling /state cada 80ms
                        Three.js renderiza el robot
```

El browser hace polling HTTP al servidor cada 80ms. No requiere WebSocket — funciona con VPN y cualquier configuración de red local.

---

## API de RobotArm

### Inicialización

```python
arm = RobotArm()
```

Lanza el servidor HTTP, abre el browser y espera a que conecte antes de continuar.

---

### Control de joints

| Método | Descripción |
|--------|-------------|
| `arm.set_angle(joint, deg)` | Mueve un joint a la posición indicada en grados |
| `arm.set_joints([j0, j1, j2, j3, j4, j5])` | Establece los 6 joints simultáneamente |
| `arm.get_joints()` | Retorna lista con los 6 ángulos actuales en grados |
| `arm.reset()` | Todos los joints a cero, pinza cerrada |

**Límites de cada joint:**

| Joint | Descripción       | Rango        |
|-------|-------------------|--------------|
| J0    | Base (yaw)        | -190° a +190° |
| J1    | Hombro (pitch)    | -90° a +90°  |
| J2    | Codo (pitch)      | -135° a +45° |
| J3    | Muñeca roll       | -90° a +75°  |
| J4    | Muñeca pitch      | -139° a +90° |
| J5    | Muñeca roll fino  | -188° a +181° |

---

### Cinemática inversa

```python
arm.move_to(x, y, z)                    # orientación por defecto
arm.move_to(x, y, z, rx, ry, rz)        # con orientación TCP en radianes
tcp = arm.get_tcp()                      # retorna [x, y, z] del TCP actual
```

---

### Pinza

```python
arm.open_gripper()         # abrir completamente
arm.close_gripper()        # cerrar completamente
arm.set_gripper(0.5)       # apertura parcial: 0.0 cerrado — 1.0 abierto
v = arm.get_gripper()      # retorna apertura actual (0.0 - 1.0)
```

---

### Trayectorias

```python
# Barrido suave de un joint
arm.sweep(joint, start_deg, end_deg, steps=30, delay=0.04)

# Lista de posiciones articulares
arm.trajectory([
    [  0,   0,   0, 0,  0,  0],
    [ 45, -20,  10, 0,  0,  0],
    [ 90, -40,  30, 0, 30,  0],
    [  0,   0,   0, 0,  0,  0],
], delay=0.4)

# Lista de posiciones cartesianas
arm.cartesian_trajectory([
    [15,  0, 25],
    [10, 10, 20],
    [-10, 10, 20],
], delay=0.5)
```

---

## Demo incluido

El archivo `example.py` ejecuta 8 secuencias en orden:

1. Reset a posición inicial
2. Movimiento individual de cada joint (J0 a J5)
3. Control de apertura de pinza
4. Cinemática inversa — visita 6 posiciones cartesianas
5. Trayectoria articular con 8 waypoints
6. Animación con onda sinusoidal en todos los joints
7. Ciclo pick & place
8. Barrido de base 360°

---

## Créditos

- Cinemática inversa analítica basada en [glumb/robot-gui](https://github.com/glumb/robot-gui) (MIT License)
- Renderizado 3D: [Three.js](https://threejs.org/) r134
