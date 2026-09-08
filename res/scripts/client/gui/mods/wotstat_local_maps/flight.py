# coding: utf-8
import math


def flightOffset(yaw, pitch, forward, right, up, distance):
    sy, cy = math.sin(yaw), math.cos(yaw)
    cp, sp = math.cos(pitch), math.sin(pitch)
    x = forward * sy * cp + right * cy
    y = -forward * sp + up
    z = forward * cy * cp - right * sy
    length = math.sqrt(x*x + y*y + z*z)
    if length < 1e-8:
        return (0, 0, 0)
    scale = distance / length
    return (x * scale, y * scale, z * scale)


class FlightController(object):
    """Six-axis navigation; the renderer and matrix provider stay FreeCamera."""
    def __init__(self, camera, position, speed=60.0):
        import Math
        self.camera = camera
        self.position = Math.Vector3(position)
        self.yaw, self.pitch = 0.0, 0.5
        self.speed = speed
        self.keys = set()
        self.camera.fixed = True
        self.apply()

    def key(self, event):
        if event.isKeyDown():
            self.keys.add(event.key)
        else:
            self.keys.discard(event.key)

    def mouse(self, event):
        self.yaw = (self.yaw + event.dx * 0.002) % (2 * math.pi)
        self.pitch = max(-1.55, min(1.55, self.pitch + event.dy * 0.002))
        if event.dz:
            self.speed = max(5.0, min(500.0, self.speed * (1.25 if event.dz > 0 else 0.8)))
        self.apply()

    def update(self, dt):
        import Keys
        import Math
        keys = self.keys
        forward = int(Keys.KEY_W in keys) - int(Keys.KEY_S in keys)
        right = int(Keys.KEY_D in keys) - int(Keys.KEY_A in keys)
        up = int(Keys.KEY_E in keys) - int(Keys.KEY_Q in keys)
        factor = 4.0 if Keys.KEY_LSHIFT in keys or Keys.KEY_RSHIFT in keys else 1.0
        if Keys.KEY_C in keys:
            factor *= 0.25
        if forward or right or up:
            self.position += Math.Vector3(flightOffset(self.yaw, self.pitch,
                forward, right, up, self.speed * factor * max(0.0, min(0.1, dt))))
            self.apply()

    def clear(self):
        self.keys.clear()
        self.camera.resetKeys()

    def apply(self):
        import Math
        matrix = Math.Matrix()
        matrix.setRotateYPR((self.yaw, self.pitch, 0.0))
        matrix.translation = self.position
        matrix.invert()
        self.camera.set(matrix)
