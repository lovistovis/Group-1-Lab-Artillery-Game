from enum import Enum
from math import pi, tan

from gamemodel import *
from graphics import *

TEXT_Y_OFFSET_FACTOR = 0.7
TICKS_PER_SECOND = 60
Y_LOWER = -10
Y_UPPER = 155
WORLD_WIDTH = X_UPPER - X_LOWER
WORLD_HEIGHT = Y_UPPER - Y_LOWER
WIN_WIDTH = 640
WIN_HEIGHT = 480
WORLD_TO_WIN_X = WIN_WIDTH / WORLD_WIDTH
WORLD_TO_WIN_Y = WIN_HEIGHT / WORLD_HEIGHT
WIN_TO_WORLD_X = WORLD_WIDTH / WIN_HEIGHT
WIN_TO_WORLD_Y = WORLD_HEIGHT / WIN_HEIGHT
WIN_NAME = "Cannon Game"
BACKGROUND_LINES_ANGLE = pi / 16.0
BACKGROUND_LINES_SPACING = 15
BACKGROUND_LINES_SPEED = 5.0
BACKGROUND_LINES_TOP_OFFSET = (tan(BACKGROUND_LINES_ANGLE)) * WORLD_HEIGHT
BACKGROUND_LINES_COUNT = WIN_WIDTH // BACKGROUND_LINES_SPACING
BACKGROUND_LINES_SPACING = (
    WORLD_WIDTH + BACKGROUND_LINES_TOP_OFFSET
) / BACKGROUND_LINES_COUNT
BALL_DECAY_TIME = 0.5
BACKGROUND_LINES_COLOR = "#e3f8fc"
BACKGROUND_FILL_COLOR = "white"
CANNON_OUTLINE_COLOR = "black"
HIT_PARTICLE_COUNT = 50
HIT_PARTICLE_MAX_VELOCITY = 10
HIT_PARTICLE_MAX_HALF_SIZE = 1
HIT_PARTICLE_PLAYER_0_COLOR_FACTORS = (10, 10, 255)
HIT_PARTICLE_PLAYER_1_COLOR_FACTORS = (255, 10, 10)
WIND_PARTICLE_COUNT = 1000
WIND_PARTICLE_DRAG_X = 0.999
WIND_PARTICLE_DRAG_Y = 0.99
WIND_PARTICLE_COLOR_FACTORS = (50, 50, 50)
WIND_PARTICLE_Y_SPAWN_OFFSET = WORLD_HEIGHT * 0.05
WIND_PARTICLE_MAX_HALF_SIZE = 1
WIND_PARTICLE_WIND_FACTOR = 50.0
WIND_PARTICLE_Y_SPREAD_ON_EDGE_HIT = WORLD_HEIGHT * 0.3


class GameGraphics:
    def __init__(self, game: Game):
        self.game = game

        self.win = GraphWin(WIN_NAME, WIN_WIDTH, WIN_HEIGHT, autoflush=False)
        self.win.setCoords(X_LOWER, Y_LOWER, X_UPPER, Y_UPPER)

        self.player_size = game.getCannonSize()
        self.player_half_size = self.player_size / 2.0
        self.projectile_radius = game.getProjectileRadius()
        self.particles: list[tuple[Projectile, Rectangle]] = []

        self.drawFrame()

    def drawFrame(self) -> None:
        self.drawStripedBackground()
        self.drawWindParticles()
        self.drawGround()
        self.draw_cannons = [self.drawCanon(0), self.drawCanon(1)]
        self.draw_scores = [self.drawScore(0), self.drawScore(1)]
        self.draw_projs: list[Circle | None] = [None, None]

    def updateFrame(self) -> None:
        if self.win.isClosed():
            exit()

        self.updateStripedBackground()
        self.updateParticles()
        self.updateWindParticles()
        update(TICKS_PER_SECOND)

    def updateStripedBackground(self) -> None:
        for line in self.striped_background_lines:
            line.move(BACKGROUND_LINES_SPEED / TICKS_PER_SECOND, 0)
            if line.getP2().getX() > X_UPPER + BACKGROUND_LINES_TOP_OFFSET:
                line.move(-WORLD_WIDTH - BACKGROUND_LINES_TOP_OFFSET, 0)

    def drawStripedBackground(self) -> None:
        background_fill = Rectangle(Point(X_LOWER, Y_LOWER), Point(X_UPPER, Y_UPPER))
        background_fill.setOutline(BACKGROUND_FILL_COLOR)
        background_fill.setFill(BACKGROUND_FILL_COLOR)
        background_fill.draw(self.win)
        self.striped_background_lines: list[Line] = []
        for i in range(BACKGROUND_LINES_COUNT):
            x_pos = X_LOWER - BACKGROUND_LINES_TOP_OFFSET + i * BACKGROUND_LINES_SPACING
            line = Line(
                Point(x_pos, Y_LOWER),
                Point(x_pos + BACKGROUND_LINES_TOP_OFFSET, Y_UPPER),
            )
            line.setWidth(BACKGROUND_LINES_SPACING / 2.0 * WORLD_TO_WIN_X)
            line.setFill(BACKGROUND_LINES_COLOR)
            line.draw(self.win)
            self.striped_background_lines.append(line)

    def drawGround(self) -> None:
        line = Rectangle(Point(X_LOWER, Y_LOWER), Point(X_UPPER, 0))
        line.setOutline("pink")
        line.setFill("pink")
        line.draw(self.win)

    def drawCanon(self, player_nr: int) -> Rectangle:
        player = self.game.getPlayer(player_nr)

        p1 = Point(
            player.getX() - self.player_half_size, player.getY() - self.player_half_size
        )
        p2 = Point(
            player.getX() + self.player_half_size, player.getY() + self.player_half_size
        )

        rect = Rectangle(p1, p2)
        rect.setFill(player.color)
        rect.setOutline(CANNON_OUTLINE_COLOR)
        rect.draw(self.win)
        return rect

    def generateWindParticlePos(
        self, initial_spawn: bool = False
    ) -> tuple[float, float]:
        x = (random() - 0.5) * 1 * WORLD_WIDTH
        y = (
            random() * WORLD_HEIGHT
            if initial_spawn
            else Y_UPPER + WIND_PARTICLE_Y_SPAWN_OFFSET
        )
        return x, y

    def drawWindParticles(self) -> None:
        self.wind_particles: list[tuple[Projectile, Rectangle]] = []
        for _ in range(WIND_PARTICLE_COUNT):
            x, y = self.generateWindParticlePos(True)
            p = Projectile(
                angle=0.0,
                velocity=0.0,
                wind=self.game.wind * WIND_PARTICLE_WIND_FACTOR,
                x_pos=x,
                y_pos=y,
                x_lower=X_LOWER,
                x_upper=X_UPPER,
            )
            half_size = random() * WIND_PARTICLE_MAX_HALF_SIZE
            rect = Rectangle(
                Point(x - half_size, y - half_size),
                Point(x + half_size, y + half_size),
            )
            f = WIND_PARTICLE_COLOR_FACTORS
            color = color_rgb(
                255 - round(random() * f[0]),
                255 - round(random() * f[1]),
                255 - round(random() * f[2]),
            )
            rect.setFill(color)
            rect.setOutline(color)
            rect.draw(self.win)
            self.wind_particles.append((p, rect))

    def spawnParticles(self, pos: tuple[float, float]) -> None:
        self.particles: list[tuple[Projectile, Rectangle]] = []
        for _ in range(HIT_PARTICLE_COUNT):
            p = Projectile(
                angle=random() * 360.0,
                velocity=random() * HIT_PARTICLE_MAX_VELOCITY,
                wind=self.game.wind,
                x_pos=pos[0],
                y_pos=pos[1],
                x_lower=X_LOWER,
                x_upper=X_UPPER,
            )
            half_size = random() * HIT_PARTICLE_MAX_HALF_SIZE
            rect = Rectangle(
                Point(pos[0] - half_size, pos[1] - half_size),
                Point(pos[0] + half_size, pos[1] + half_size),
            )
            # Reversed as the other player to the current is the one getting hit
            f = (
                HIT_PARTICLE_PLAYER_0_COLOR_FACTORS
                if self.game.getCurrentPlayerNumber() == 1
                else HIT_PARTICLE_PLAYER_1_COLOR_FACTORS
            )
            color = color_rgb(
                round(random() * f[0]), round(random() * f[1]), round(random() * f[2])
            )
            rect.setFill(color)
            rect.setOutline(color)
            rect.draw(self.win)
            self.particles.append((p, rect))

    def updateParticles(self) -> None:
        for i, t in enumerate(self.particles):
            p, rect = t
            p.update(1.0 / TICKS_PER_SECOND)
            if p.getY() < 0.0:
                self.particles.pop(i)
            else:
                rect.move(p.xvel / TICKS_PER_SECOND, p.yvel / TICKS_PER_SECOND)

    def updateWindParticles(self) -> None:
        for t in self.wind_particles:
            p, rect = t
            x_old, y_old = p.x_pos, p.y_pos
            p.update(
                1.0 / TICKS_PER_SECOND, WIND_PARTICLE_DRAG_X, WIND_PARTICLE_DRAG_Y, True
            )
            if p.getY() <= 0.0:
                p.x_pos, p.y_pos = self.generateWindParticlePos()
            elif p.getX() <= X_LOWER - 2:
                p.x_pos = X_UPPER + 1
                p.y_pos += (random() - 0.5) * WIND_PARTICLE_Y_SPREAD_ON_EDGE_HIT
            elif p.getX() >= X_UPPER + 2:
                p.x_pos = X_LOWER - 1
                p.y_pos += (random() - 0.5) * WIND_PARTICLE_Y_SPREAD_ON_EDGE_HIT
            rect.move(p.x_pos - x_old, p.y_pos - y_old)

    def updateWindParticleWindSpeed(self, wind: float) -> None:
        for p, _ in self.wind_particles:
            p.wind = wind

    def formatScore(self, score: int) -> str:
        return f"Score: {score}"

    def drawScore(self, player_nr: int) -> Text:
        player = self.game.getPlayer(player_nr)
        p = Point(
            player.getX(), player.getY() - self.player_size * TEXT_Y_OFFSET_FACTOR
        )
        text = Text(p, self.formatScore(player.getScore()))
        text.draw(self.win)
        return text

    def redrawScores(self) -> None:
        self.draw_scores[0].undraw()
        self.draw_scores[1].undraw()
        self.draw_scores[0].draw(self.win)
        self.draw_scores[1].draw(self.win)

    def updateScore(self, player_nr: int) -> None:
        player = self.game.getPlayer(player_nr)
        self.draw_scores[player_nr].setText(self.formatScore(player.getScore()))

    def fire(self, angle: float, vel: float) -> Projectile:
        player_nr = self.game.getCurrentPlayerNumber()
        player = self.game.getPlayer(player_nr)
        proj = player.fire(angle, vel)

        circle_x = proj.getX()
        circle_y = proj.getY()

        old_proj = self.draw_projs[player_nr]
        if old_proj is not None:
            old_proj.undraw()
            self.draw_projs[player_nr] = None

        circle = Circle((Point(circle_x, circle_y)), self.projectile_radius)
        circle.setFill(player.color)
        circle.setOutline(player.color)
        circle.draw(self.win)
        self.draw_projs[player_nr] = circle

        # Redraw scores to place them in front of ball
        self.redrawScores()

        other_player = self.game.getOtherPlayer()
        collided = False
        while proj.isMoving():
            proj.update(1.0 / TICKS_PER_SECOND)

            if not collided and other_player.collisionCheck(proj):
                collided = True
                circle.undraw()
                closest_point = other_player.closestPoint(proj.getX(), proj.getY())
                self.spawnParticles(closest_point)

            if not collided:
                circle.move(proj.getX() - circle_x, proj.getY() - circle_y)

                circle_x = proj.getX()
                circle_y = proj.getY()

            self.updateFrame()

        return proj

    def play(self) -> None:
        while True:
            player = self.game.getCurrentPlayer()
            old_angle, old_vel = player.getAim()
            wind = self.game.getCurrentWind()
            self.updateScore(0)

            inp = InputDialog(self, old_angle, old_vel, wind)
            action = inp.interact()

            angle, vel = None, None
            match action:
                case InteractAction.QUIT:
                    exit()
                case InteractAction.FIRE:
                    angle, vel = inp.getValues()
                    inp.close()

            player = self.game.getCurrentPlayer()
            other = self.game.getOtherPlayer()
            proj = self.fire(angle, vel)
            distance = other.projectileDistance(proj)

            if distance == 0.0:
                player.increaseScore()
                self.updateScore(self.game.getCurrentPlayerNumber())
                self.game.newRound()
                self.updateWindParticleWindSpeed(self.game.wind)

            self.game.nextPlayer()


class InteractAction(Enum):
    QUIT = 0
    FIRE = 1


class InputDialog:
    def __init__(
        self, game_graphics: GameGraphics, angle: float, vel: float, wind: float
    ):
        self.game_graphics = game_graphics
        self.win = win = GraphWin("Fire", 200, 300)
        win.setCoords(0, 4.5, 4, 0.5)

        Text(Point(1, 1), "Angle").draw(win)
        self.angle = Entry(Point(3, 1), 5).draw(win)
        self.angle.setText(str(angle))

        Text(Point(1, 2), "Velocity").draw(win)
        self.vel = Entry(Point(3, 2), 5).draw(win)
        self.vel.setText(str(vel))

        Text(Point(1, 3), "Wind").draw(win)
        self.height = Text(Point(3, 3), 5).draw(win)
        self.height.setText("{0:.2f}".format(wind))

        self.fire = Button(win, Point(1, 4), 1.25, 0.5, "Fire!", "green")
        self.fire.activate()

        self.quit = Button(win, Point(3, 4), 1.25, 0.5, "Quit", "lightgray")
        self.quit.activate()

    def interact(self) -> InteractAction:
        while True:
            self.game_graphics.updateFrame()

            if self.win.isClosed():
                exit()

            pt = self.win.checkMouse()
            if pt == None:
                continue
            if self.quit.clicked(pt):
                return InteractAction.QUIT
            elif self.fire.clicked(pt):
                return InteractAction.FIRE

    def getValues(self) -> tuple[float, float]:
        a = float(self.angle.getText())
        v = float(self.vel.getText())
        return a, v

    def close(self) -> None:
        self.win.close()


class Button:
    def __init__(
        self,
        win: GraphWin,
        center: Point,
        width: float,
        height: float,
        label: str,
        color: str,
    ):
        w, h = width / 2.0, height / 2.0
        x, y = center.getX(), center.getY()

        self.xmax, self.xmin = x + w, x - w
        self.ymax, self.ymin = y + h, y - h

        p1 = Point(self.xmin, self.ymin)
        p2 = Point(self.xmax, self.ymax)

        self.rect = Rectangle(p1, p2)
        self.rect.setFill(color)
        self.rect.draw(win)

        self.label = Text(center, label)
        self.label.draw(win)

        self.deactivate()

    def clicked(self, p: Point) -> bool:
        return (
            self.active
            and self.xmin <= p.getX() <= self.xmax
            and self.ymin <= p.getY() <= self.ymax
        )

    def getLabel(self) -> Text:
        return self.label.getText()

    def activate(self) -> None:
        self.label.setFill("black")
        self.rect.setWidth(2)
        self.active = True

    def deactivate(self) -> None:
        self.label.setFill("darkgrey")
        self.rect.setWidth(1)
        self.active = False


def main() -> None:
    GameGraphics(Game(10, 3)).play()


if __name__ == "__main__":
    main()
