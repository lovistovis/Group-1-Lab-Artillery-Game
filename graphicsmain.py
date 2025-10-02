from gamemodel import *
from graphics import *


TEXT_Y_OFFSET_FACTOR = 0.7

class GameGraphics:
    def __init__(self, game: Game):
        self.game = game

        self.win = GraphWin("Cannon game", 640, 480, autoflush=False)
        self.win.setCoords(-110, -10, 110, 155)

        self.player_size = game.getCannonSize()
        self.player_half_size = self.player_size / 2.0
        self.projectile_size = game.getProjectileRadius()

        self.draw_cannons = [self.drawCanon(0), self.drawCanon(1)]
        self.draw_scores = [self.drawScore(0), self.drawScore(1)]
        self.draw_projs: list[Circle | None] = [None, None]

        Line(Point(-110, 0), Point(110, 0)).draw(self.win)

    def drawCanon(self, playerNr: int) -> Rectangle:
        player = self.game.getPlayer(playerNr)

        p1 = Point(player.getX() - self.player_half_size, player.getY() - self.player_half_size)
        p2 = Point(player.getX() + self.player_half_size, player.getY() + self.player_half_size)

        rect = Rectangle(p1, p2)
        rect.draw(self.win)
        return rect

    def formatScore(self, score: int) -> str:
        return f"Score: {score}"

    def drawScore(self, playerNr: int) -> Text:
        player = self.game.getPlayer(playerNr)
        p = Point(player.getX(), player.getY() - self.player_size * TEXT_Y_OFFSET_FACTOR)
        text = Text(p, self.formatScore(player.getScore()))
        text.draw(self.win)
        return text

    def updateScore(self, playerNr: int) -> None:
        player = self.game.getPlayer(playerNr)
        self.draw_scores[playerNr].setText(self.formatScore(player.getScore()))

    def fire(self, angle: float, vel: float) -> Projectile:
        playerNr = self.game.getCurrentPlayerNumber()
        player = self.game.getPlayer(playerNr)
        proj = Projectile(
            angle, vel, 5, 10, 10, 1, 100
        )  # TODO: Replace with following: player.fire(angle, vel)

        circle_x = proj.getX()
        circle_y = proj.getY()

        old_proj = self.draw_projs[playerNr]
        if old_proj is not None:
            old_proj.undraw()
            self.draw_projs[playerNr] = None

        circle = Circle((Point(circle_x, circle_y)), self.projectile_size)
        circle.draw(self.win)
        self.draw_projs[playerNr] = circle

        while proj.isMoving():
            proj.update(1 / 50)

            circle.move(proj.getX() - circle_x, proj.getY() - circle_y)

            circle_x = proj.getX()
            circle_y = proj.getY()

            update(50)

        return proj

    def play(self) -> None:
        while True:
            player = self.game.getCurrentPlayer()
            oldAngle, oldVel = player.getAim()
            wind = self.game.getCurrentWind()
            self.updateScore(0)

            inp = InputDialog(oldAngle, oldVel, wind)

            angle, vel = None, None
            if inp.interact() == "Fire!":
                angle, vel = inp.getValues()
                inp.close()
            elif inp.interact() == "Quit":
                exit()
            else:
                raise RuntimeError("Invalid return from InputDialog")

            player = self.game.getCurrentPlayer()
            other = self.game.getOtherPlayer()
            proj = self.fire(angle, vel)
            distance = other.projectileDistance(proj)

            if distance == 0.0:
                player.increaseScore()
                self.updateScore(self.game.getCurrentPlayerNumber())
                self.game.newRound()

            self.game.nextPlayer()


class InputDialog:
    def __init__(self, angle: float, vel: float, wind: float):
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

        self.fire = Button(win, Point(1, 4), 1.25, 0.5, "Fire!")
        self.fire.activate()

        self.quit = Button(win, Point(3, 4), 1.25, 0.5, "Quit")
        self.quit.activate()

    def interact(self) -> str:
        while True:
            pt = self.win.getMouse()
            if self.quit.clicked(pt):
                return "Quit"
            if self.fire.clicked(pt):
                return "Fire!"

    def getValues(self) -> tuple[float, float]:
        a = float(self.angle.getText())
        v = float(self.vel.getText())
        return a, v

    def close(self) -> None:
        self.win.close()


class Button:
    def __init__(
        self, win: GraphWin, center: Point, width: float, height: float, label: str
    ):
        w, h = width / 2.0, height / 2.0
        x, y = center.getX(), center.getY()

        self.xmax, self.xmin = x + w, x - w
        self.ymax, self.ymin = y + h, y - h

        p1 = Point(self.xmin, self.ymin)
        p2 = Point(self.xmax, self.ymax)

        self.rect = Rectangle(p1, p2)
        self.rect.setFill("lightgray")
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
