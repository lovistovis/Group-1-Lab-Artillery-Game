from math import cos, radians, sin
from random import random

X_LOWER = -110
X_UPPER = 110
PLAYER_0_STARTING_X = -90
PLAYER_1_STARTING_X = 90
STARTING_AIM = (45, 40)
WIND_SELECTION_RANGE = 10


class Projectile:
    """Models a projectile (a cannonball, but could be used more generally)"""

    def __init__(
        self,
        angle: float,
        velocity: float,
        wind: float,
        xPos: float,
        yPos: float,
        xLower: float,
        xUpper: float,
    ):
        """
        Constructor parameters:
        angle and velocity: the initial angle and velocity of the projectile
            angle 0 means straight east (positive x-direction) and 90 straight up
        wind: The wind speed value affecting this projectile
        xPos and yPos: The initial position of this projectile
        xLower and xUpper: The lowest and highest x-positions allowed
        """

        self.wind = wind
        self.yPos = yPos
        self.xPos = xPos
        self.xLower = xLower
        self.xUpper = xUpper

        theta = radians(angle)
        self.xvel = velocity * cos(theta)
        self.yvel = velocity * sin(theta)

    def update(self, time: float) -> None:
        """
        Advance time by a given number of seconds
        (typically, time is less than a second,
        for large values the projectile may move erratically).
        """

        # Compute new velocity based on acceleration from gravity/wind
        yvel1 = self.yvel - 9.8 * time
        xvel1 = self.xvel + self.wind * time

        # Move based on the average velocity in the time period
        self.xPos = self.xPos + time * (self.xvel + xvel1) / 2.0
        self.yPos = self.yPos + time * (self.yvel + yvel1) / 2.0

        # make sure yPos >= 0
        self.yPos = max(self.yPos, 0)

        # Make sure xLower <= xPos <= mUpper
        self.xPos = max(self.xPos, self.xLower)
        self.xPos = min(self.xPos, self.xUpper)

        # Update velocities
        self.yvel = yvel1
        self.xvel = xvel1

    def isMoving(self) -> bool:
        """A projectile is moving as long as it has not hit the ground or moved outside the xLower and xUpper limits"""
        return 0 < self.getY() and self.xLower < self.getX() < self.xUpper

    def getX(self) -> float:
        """The current x-position of the projectile."""
        return self.xPos

    def getY(self) -> float:
        """The current y-position (height) of the projectile. Should never be below 0."""
        return self.yPos


class Player:
    """Models a player."""

    def __init__(
        self, game: "Game", isReversed: bool, size: int, xPos: float, color: str
    ):
        self.game = game
        self.isReversed = isReversed
        self.size = size
        self.pos = (xPos, self.size / 2.0)
        self.color = color

        self.score = 0
        self.aim = STARTING_AIM

    def fire(self, angle: float, velocity: float) -> Projectile:
        """
        Create and return a projectile starting at the centre of this players cannon.
        Replaces any previous projectile for this player.
        """

        if self.isReversed:
            angle = 180 - angle

        projectile = Projectile(
            angle=angle,
            velocity=velocity,
            wind=self.game.wind,
            xPos=self.pos[0],
            yPos=self.pos[1],
            xLower=X_LOWER,
            xUpper=X_UPPER,
        )

        self.aim = (angle, velocity)

        return projectile

    def projectileDistance(self, proj: Projectile) -> float:
        """
        Gives the x-distance from this players cannon to a projectile.
        If the cannon and the projectile touch (assuming the projectile
        is on the ground and factoring in both cannon and projectile size)
        this method should return 0
        """

        proj_half_size = self.game.getProjectileRadius()
        cannon_half_size = self.size / 2.0

        total_overlap_size = cannon_half_size + proj_half_size

        cannon_center = self.pos[0]
        proj_center = proj.getX()

        raw_distance = proj_center - cannon_center

        if abs(raw_distance) < total_overlap_size:
            return 0

        return raw_distance - total_overlap_size * (1 if raw_distance > 0 else -1)

    def increaseScore(self, n: int = 1) -> None:
        """Increase the score of this player by 1."""
        self.score += n

    def getScore(self) -> int:
        """The current score of this player."""
        return self.score

    def getColor(self) -> str:
        """Returns the color of this player (a string)."""
        return self.color

    def getX(self) -> float:
        """The x-position of the centre of this players cannon."""
        return self.pos[0]

    def getY(self) -> float:
        """The y-position of the centre of this players cannon."""
        return self.pos[1]

    def getAim(self) -> tuple[float, float]:
        """The angle and velocity of the last projectile this player fired, initially (45, 40)."""
        return self.aim


class Game:
    """This is the model of the game."""

    def __init__(self, cannonSize: int, projectileRadius: int):
        """Create a game with a given size of cannon (length of sides) and projectiles (radius)."""

        self.cannonSize = cannonSize
        self.projectileRadius = projectileRadius

        self.players = [
            Player(self, False, cannonSize, PLAYER_0_STARTING_X, "blue"),
            Player(self, True, cannonSize, PLAYER_1_STARTING_X, "red"),
        ]
        self.currentPlayer = 0
        self.wind = 0.0

    def getPlayers(self) -> list[Player]:
        """A list containing both players."""
        return self.players

    def getPlayer(self, player_nr: int) -> Player:
        """The player with nr player_nr."""
        return self.players[player_nr]

    def getCannonSize(self) -> int:
        """The height/width of the cannon."""
        return self.cannonSize

    def getProjectileRadius(self) -> int:
        """The radius of cannon balls."""
        return self.projectileRadius

    def getCurrentPlayer(self) -> Player:
        """The current player, i.e. the player whose turn it is."""
        return self.players[self.currentPlayer]

    def getOtherPlayer(self) -> Player:
        """The opponent of the current player."""
        return self.players[1] if self.currentPlayer == 0 else self.players[0]

    def getCurrentPlayerNumber(self) -> int:
        """The number (0 or 1) of the current player. This should be the position of the current player in getPlayers()."""
        return self.currentPlayer

    def nextPlayer(self) -> None:
        """Switch active player."""
        self.currentPlayer = 0 if self.currentPlayer == 1 else 1

    def setCurrentWind(self, wind) -> None:
        """Set the current wind speed, only used for testing."""
        self.wind = wind

    def getCurrentWind(self) -> float:
        """The current wind speed."""
        return self.wind

    def newRound(self) -> None:
        """Start a new round with a random wind value (-WIND_SELECTION_RANGE to +WIND_SELECTION_RANGE)."""
        self.wind = (random() * WIND_SELECTION_RANGE * 2) - WIND_SELECTION_RANGE
