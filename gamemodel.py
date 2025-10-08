from math import cos, radians, sin
from random import random

X_LOWER = -110
X_UPPER = 110
PLAYER_0_STARTING_X = -90
PLAYER_1_STARTING_X = 90
PLAYER_0_COLOR = "blue"
PLAYER_1_COLOR = "red"
STARTING_AIM = (45, 40)
WIND_SELECTION_RANGE = 10


class Projectile:
    def __init__(
        self,
        angle: float,
        velocity: float,
        wind: float,
        x_pos: float,
        y_pos: float,
        x_lower: float,
        x_upper: float,
    ):
        self.wind = wind
        self.y_pos = y_pos
        self.x_pos = x_pos
        self.x_lower = x_lower
        self.x_upper = x_upper

        theta = radians(angle)
        self.xvel = velocity * cos(theta)
        self.yvel = velocity * sin(theta)

    def update(
        self,
        time: float,
        drag_x: float = 1.0,
        drag_y: float = 1.0,
        ignore_x_limits: bool = False,
    ) -> None:
        # Compute new velocity based on acceleration from gravity/wind
        yvel1 = self.yvel - 9.8 * time
        xvel1 = self.xvel + self.wind * time

        # Move based on the average velocity in the time period
        self.x_pos = self.x_pos + time * (self.xvel + xvel1) / 2.0
        self.y_pos = self.y_pos + time * (self.yvel + yvel1) / 2.0

        # make sure yPos >= 0
        self.y_pos = max(self.y_pos, 0)

        if not ignore_x_limits:
            # Make sure xLower <= xPos <= mUpper
            self.x_pos = max(self.x_pos, self.x_lower)
            self.x_pos = min(self.x_pos, self.x_upper)

        # Update velocities
        self.xvel = xvel1 * drag_x
        self.yvel = yvel1 * drag_y

    def isMoving(self) -> bool:
        return 0 < self.getY() and self.x_lower < self.getX() < self.x_upper

    def getX(self) -> float:
        return self.x_pos

    def getY(self) -> float:
        return self.y_pos


class Player:
    def __init__(
        self, game: "Game", is_reversed: bool, size: int, x_pos: float, color: str
    ):
        self.game = game
        self.is_reversed = is_reversed
        self.size = size
        self.pos = (x_pos, self.size / 2.0)
        self.color = color

        self.score = 0
        self.aim = STARTING_AIM

    def fire(self, angle: float, velocity: float) -> Projectile:
        projectile = Projectile(
            angle=180 - angle if self.is_reversed else angle,
            velocity=velocity,
            wind=self.game.wind,
            x_pos=self.pos[0],
            y_pos=self.pos[1],
            x_lower=X_LOWER,
            x_upper=X_UPPER,
        )

        self.aim = (angle, velocity)

        return projectile

    def projectileDistance(self, proj: Projectile) -> float:
        proj_half_size = self.game.getProjectileRadius()
        cannon_half_size = self.size / 2.0

        total_overlap_size = cannon_half_size + proj_half_size

        cannon_center = self.pos[0]
        proj_center = proj.getX()

        raw_distance = proj_center - cannon_center

        if abs(raw_distance) < total_overlap_size:
            return 0

        return raw_distance - total_overlap_size * (1 if raw_distance > 0 else -1)

    def collisionCheck(self, proj: Projectile) -> float:
        circle_distance_x = abs(proj.getX() - self.pos[0])
        circle_distance_y = abs(proj.getY() - self.pos[1])

        projectile_r = self.game.getProjectileRadius()
        half_size = self.size / 2.0
        if circle_distance_x > (half_size + projectile_r) or circle_distance_y > (
            half_size + projectile_r
        ):
            return False

        if circle_distance_x <= half_size or circle_distance_y <= half_size:
            return True

        corner_distance_sq = (circle_distance_x - half_size) ** 2 + (
            circle_distance_y - half_size
        ) ** 2

        return corner_distance_sq <= (projectile_r**2)

    def closestPoint(self, x: float, y: float) -> tuple[float, float]:
        half_size = self.size / 2.0
        return (
            max(self.pos[0] - half_size, min(x, self.pos[0] + half_size)),
            max(self.pos[1] - half_size, min(y, self.pos[1] + half_size)),
        )

    def increaseScore(self, n: int = 1) -> None:
        self.score += n

    def getScore(self) -> int:
        return self.score

    def getColor(self) -> str:
        return self.color

    def getX(self) -> float:
        return self.pos[0]

    def getY(self) -> float:
        return self.pos[1]

    def getAim(self) -> tuple[float, float]:
        return self.aim


class Game:
    def __init__(self, cannon_size: int, projectile_radius: int):
        self.cannon_size = cannon_size
        self.projectile_radius = projectile_radius

        self.players = [
            Player(self, False, cannon_size, PLAYER_0_STARTING_X, PLAYER_0_COLOR),
            Player(self, True, cannon_size, PLAYER_1_STARTING_X, PLAYER_1_COLOR),
        ]
        self.current_player = 0
        self.wind = 0.0

    def getPlayers(self) -> list[Player]:
        return self.players

    def getPlayer(self, player_nr: int) -> Player:
        return self.players[player_nr]

    def getCannonSize(self) -> int:
        return self.cannon_size

    def getProjectileRadius(self) -> int:
        return self.projectile_radius

    def getCurrentPlayer(self) -> Player:
        return self.players[self.current_player]

    def getOtherPlayer(self) -> Player:
        return self.players[1] if self.current_player == 0 else self.players[0]

    def getCurrentPlayerNumber(self) -> int:
        return self.current_player

    def nextPlayer(self) -> None:
        self.current_player = 0 if self.current_player == 1 else 1

    def setCurrentWind(self, wind) -> None:
        self.wind = wind

    def getCurrentWind(self) -> float:
        return self.wind

    def newRound(self) -> None:
        self.wind = (random() * WIND_SELECTION_RANGE * 2) - WIND_SELECTION_RANGE
