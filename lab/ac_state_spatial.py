from typing import Tuple

import enum

AutonomousCarSpatialPosition = Tuple[int, int]

class AutonomousCarSpatialDirection(enum.Enum):
    FRONT = 0 # (0, 1)
    RIGHT = 1 # (1, 0)
    BACK = 2 # (0, -1)
    LEFT = 3 # (-1, 0)

    def cw(self, turns=1):
        return AutonomousCarSpatialDirection((self.value + turns) % 4)

    def ccw(self, turns=1):
        return AutonomousCarSpatialDirection((self.value - turns) % 4)
    
    def rel_to_abs(self, other: "AutonomousCarSpatialDirection"):
        # return relative of other relative to self
        return AutonomousCarSpatialDirection((self.value + other.value) % 4)

    def abs_to_rel(self, other: "AutonomousCarSpatialDirection"):
        # return relative of other relative to self
        return AutonomousCarSpatialDirection((other.value - self.value) % 4)

    def vec(self):
        # return direction vector
        match self:
            case AutonomousCarSpatialDirection.FRONT:
                return (0, 1)
            case AutonomousCarSpatialDirection.RIGHT:
                return (1, 0)
            case AutonomousCarSpatialDirection.BACK:
                return (0, -1)
            case AutonomousCarSpatialDirection.LEFT:
                return (-1, 0)

    def transform(self, pos: AutonomousCarSpatialPosition):
        # assuming world coordinates, convert to spatial relative
        # i.e. [5, 0] -> [0, 5] (right), [-5, 0] (back), [0, -5] (left)
        x, y = pos

        match self:
            case AutonomousCarSpatialDirection.FRONT:
                return (x, y)
            case AutonomousCarSpatialDirection.RIGHT:
                return (y, x)
            case AutonomousCarSpatialDirection.BACK:
                return (-x, y)
            case AutonomousCarSpatialDirection.LEFT:
                return (y, -x)

    
    def __repr__(self):
        return self.name