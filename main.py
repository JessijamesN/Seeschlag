from random import randint

print("\033[34m\033[40m\033[5m {}".format("Игра, морской бой"))


class Punkt:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return "Punkt({}, {})" .format(self.x, self.y)

class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"

class BoardWrongShipException(BoardException):
    pass


"""
    nase - точка носа корабля
    lange - длинна корабля
    wohin - направление
    boot_punkt - перечень координат корабля
    feuer - огонь, schiss - выстрел
"""

class Boot:
    def __init__(self, nase, lange, wohin):
        self.nase = nase
        self.lange = lange
        self.wohin = wohin
        self.lives = lange

    @property
    def punkt(self):
        boot_punkt = []
        for j in range(self.lange):
            curs_x = self.nase.x
            curs_y = self.nase.y

            if self.wohin == 0:
                curs_x += j
            elif self.wohin == 1:
                curs_y += j
            boot_punkt.append(Punkt(curs_x, curs_y))

        return boot_punkt

    def feuer(self, schiss):
        return schiss in self.punkt

"""
        verbot - видим не видим
        grose - размер
        tax - количество уничтоженных кораблей
        besetz - список занятых всех точек
        schiffe - корабли
"""
class Tafel:
    def __init__(self, verbot=False, grosse=9):
        self.grosse = grosse
        self.verbot = verbot
        self.tax = 0
        self.platz = [["~"] * grosse for _ in range(grosse)]
        self.besetz = []
        self.schiffe = []

    def plus_boot(self, boot):
        for d in boot.punkt:
            if self.drausen(d) or d in self.besetz:
                raise BoardWrongShipException()
        for d in boot.punkt:
            self.platz[d.x][d.y] = "ø"
            self.besetz.append(d)
        self.schiffe.append(boot)
        self.kontur(boot)

    def kontur(self, boot, verb= False):
        nahe = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0 , 1), (1, -1), (1, 0), (1, 1)]
        for d in boot.punkt:       # "Если не стоит проперти тот тут две кавычки"
            for dx, dy in nahe:
                curs = Punkt(d.x + dx, d.y + dy)
                if not(self.drausen(curs)) and curs not in self.besetz:
                    if verb:
                        self.platz[curs.x][curs.y] = "\033[32m{}\033[34m".format("¤")
                    self.besetz.append(curs)

    def __str__(self):
        mase = ""
        mase += "   | 1  2  3  4  5  6  7  8  9 |"
        for i, www in enumerate(self.platz):
            mase += f"\n{i + 1}  | " + "  ".join(www) + " |"
        if self.verbot:
            mase = mase.replace("ø", "~")
        return mase

    def drausen(self, d):
        return not((0<= d.x < self.grosse) and (0 <= d.y < self.grosse))

    def shot(self, d):
        if self.drausen(d):
            raise BoardOutException()

        if d in self.besetz:
            raise BoardUsedException()

        self.besetz.append(d)

        for boot in self.schiffe:
            if d in boot.punkt:
                boot.lives -= 1
                self.platz[d.x][d.y] = "\033[31m{}\033[34m".format("X")
                if boot.lives == 0:
                    self.tax += 1
                    self.kontur(boot, verb=True)
                    print("\033[33m{}\033[34m".format("Корабль уничтожен!"))
                    return False
                else:
                    print("\033[33m{}\033[34m".format("Корабль поврежден!"))
                    return True

        self.platz[d.x][d.y] = "\033[32m{}\033[34m".format("¤")
        print("Промах")
        return False

    def begin(self):
        self.besetz = []

class Spieler:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()   #ziel
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class AI(Spieler):
    def ask(self):
        d = Punkt(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d

class User(Spieler):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue
            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите число! ")
                continue

            x, y = int(x), int(y)
            return Punkt(x - 1, y - 1)


class Spiel:
    def __init__(self, grosse=9):
        self.grosse = grosse
        pl = self.random_board()
        co = self.random_board()
        co.verbot = True
        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def try_board(self):
        lens = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        board = Tafel(grosse=self.grosse)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 1000:
                    return None
                boot = Boot(Punkt(randint(0, self.grosse), randint(0, self.grosse)), l, randint(0, 1))
                try:
                    board.plus_boot(boot)
                    break
                except BoardWrongShipException:
                    pass

        board.begin()
        return board

    def loop(self):
        nummer = 0
        while True:
            print("-" * 32)
            print("Доска игрока:")
            print(self.us.board)
            print("-" * 32)
            print("Доска компьютера:")
            print(self.ai.board)

            if nummer % 2 == 0:
                print("-" * 32)
                print("Ходит игрок!")
                repeat = self.us.move()
            else:
                print("-" * 32)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                nummer -= 1

            if self.ai.board.tax == 10:
                print("-" * 32)
                print("Игрок победил!")
                break

            if self.us.board.tax == 10:
                print("-" * 32)
                print("Скайнэт выиграл!")
                break
            nummer += 1

    def start(self):
        self.loop()


g = Spiel()
g.start()
