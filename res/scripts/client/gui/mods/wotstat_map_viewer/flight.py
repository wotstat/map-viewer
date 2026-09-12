# coding: utf-8
import math


def flightOffset(yaw, pitch, forward, right, up, distance):
    sy, cy = math.sin(yaw), math.cos(yaw)
    x = forward * sy + right * cy
    y = up
    z = forward * cy - right * sy
    length = math.sqrt(x*x + y*y + z*z)
    if length < 1e-8:
        return (0, 0, 0)
    scale = distance / length
    return (x * scale, y * scale, z * scale)


def advanceVelocity(velocity, direction, maxSpeed, dt, acceleration=None):
    """debug-utils acceleration and exponential coasting, in world axes."""
    if any(direction):
        acceleration = maxSpeed * 5.0 if acceleration is None else acceleration
        velocity = tuple(v + d * dt * acceleration for v, d in zip(velocity, direction))
    else:
        if sum(v*v for v in velocity) < 0.0001 ** 2:
            return (0, 0, 0)
        velocity = tuple(v * 0.985 ** (dt * 1000.0) for v in velocity)
    length = math.sqrt(sum(v*v for v in velocity))
    if length > maxSpeed:
        velocity = tuple(v * maxSpeed / length for v in velocity)
    return velocity


class FlightController(object):
    """Horizontal inertial flight adapted from debug-utils WotstatFreeCamera."""
    def __init__(self, camera, position, speed=60.0):
        import Math
        self.camera = camera
        self.position = Math.Vector3(position)
        self.yaw, self.pitch = 0.0, 0.5
        self.speed = speed
        self.keys = set()
        self.horizontalVelocity = (0, 0, 0)
        self.verticalVelocity = (0, 0, 0)
        self.zoomLevel = 1.0
        self.baseFov = math.radians(70.0)
        self.camera.fixed = True
        self.apply()

    def key(self, event):
        import Keys
        if event.isKeyDown():
            self.keys.add(event.key)
            speedKeys = (Keys.KEY_1, Keys.KEY_2, Keys.KEY_3, Keys.KEY_4,
                         Keys.KEY_5, Keys.KEY_6, Keys.KEY_7, Keys.KEY_8, Keys.KEY_9)
            if event.key in speedKeys:
                self.speed = (1., 2., 5., 10., 15., 20., 30., 50., 75.)[speedKeys.index(event.key)]
        else:
            self.keys.discard(event.key)
        if event.key == Keys.KEY_Z and not event.isRepeatedEvent():
            self.setZoom(3.0 if event.isKeyDown() else 1.0)

    def mouse(self, event):
        import Keys
        sensitivity = 0.002 / self.zoomLevel
        self.yaw = (self.yaw + event.dx * sensitivity) % (2 * math.pi)
        self.pitch = max(-math.pi / 2, min(math.pi / 2, self.pitch + event.dy * sensitivity))
        if event.dz:
            if Keys.KEY_Z in self.keys:
                self.setZoom(max(1.0, min(2000.0, self.zoomLevel * (1.1 if event.dz > 0 else 0.9))))
            else:
                self.speed = max(1.0, min(500.0, self.speed * (1.25 if event.dz > 0 else 0.8)))
        self.apply()

    def setZoom(self, level, rampTime=0.1):
        import BigWorld
        if self.zoomLevel != level:
            self.zoomLevel = level
            BigWorld.projection().rampFov(self.baseFov / level, rampTime)

    def update(self, dt):
        import Keys
        import Math
        keys = self.keys
        forward = int(Keys.KEY_W in keys) - int(Keys.KEY_S in keys)
        right = int(Keys.KEY_D in keys) - int(Keys.KEY_A in keys)
        up = int(Keys.KEY_E in keys or Keys.KEY_SPACE in keys) - int(
            Keys.KEY_Q in keys or Keys.KEY_LSHIFT in keys or Keys.KEY_RSHIFT in keys)
        speed = self.speed * (0.25 if Keys.KEY_C in keys else 1.0)
        verticalSpeed = min(max(speed / 1.5, 5.0), speed)
        dt = max(0.0, min(0.1, dt))
        direction = flightOffset(self.yaw, self.pitch, forward, right, 0, 1.0)
        self.horizontalVelocity = advanceVelocity(self.horizontalVelocity, direction, speed, dt)
        self.verticalVelocity = advanceVelocity(self.verticalVelocity, (0, up, 0), verticalSpeed, dt, speed * 5.0)
        self.position += (Math.Vector3(self.horizontalVelocity) + Math.Vector3(self.verticalVelocity)) * dt
        self.apply()

    def clear(self, stopMotion=True):
        self.keys.clear()
        if stopMotion:
            self.horizontalVelocity = (0, 0, 0)
            self.verticalVelocity = (0, 0, 0)
        self.setZoom(1.0, 0.0)
        self.camera.resetKeys()

    def apply(self):
        import Math
        matrix = Math.Matrix()
        matrix.setRotateYPR((self.yaw, self.pitch, 0.0))
        matrix.translation = self.position
        matrix.invert()
        self.camera.set(matrix)
