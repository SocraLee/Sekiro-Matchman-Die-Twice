import pgzrun
import time

WIDTH = 1280
HEIGHT = 720

player1_key = {
    keys.J: 'atk',
    keys.S: 'def',
    keys.K: 'jump',
    keys.A: 'left',
    keys.D: 'right',
}

now_pressed_key = set()

now_page = 'battle'

class Player(object):

    def __init__(self, type):
        # type = 'player' or 'enemy'
        self.type = type
        self.atk = 10
        self.hp = 100
        if type == 'player':
            self.actor = Actor('player1_block')
            self.actor.bottomleft = (0, HEIGHT)
        if type == 'enemy':
            self.actor = Actor('player2_block')
            self.actor.bottomright = (WIDTH, HEIGHT)
        
        # 上次攻击和防御的时间
        # 用于内置cd和某些判定
        self.atk_last = -10
        self.def_last = -10

        # 在xy方向上的速度
        self.vx = 0
        self.vy = 0

    def get_action(self):
        if self.type == 'player':
            return [player1_key[i] for i in now_pressed_key if i in player1_key]
        else:
            #return agent()
            return ['atk']
        
    def pos_update(self):
        action = self.get_action()
        if 'atk' not in action and 'def' not in action:
            if 'left' in action and 'right' in action:
                self.vx = 0
            if 'left' in action and 'right' not in action:
                self.vx = -100
            if 'left' not in action and 'right' in action:
                self.vx = 100
            if 'left' not in action and 'right' not in action:
                self.vx = 0
            if 'jump' in action:
                self.vy = -100
        else:
            self.vx = 0
        self.vy += 10

        self.actor.left += self.vx
        self.actor.bottom += self.vy
        self.actor.bottom = min(self.actor.bottom, HEIGHT)
        self.actor.top = max(self.actor.top, 0)
        self.actor.right = min(self.actor.right, WIDTH)
        self.actor.left = max(self.actor.left, 0)

    def is_attacking(self):
        return time.time() - self.atk_last > 0.5 and 'atk' in self.get_action()

    def is_defending(self):
        return time.time() - self.def_last > 0.5 and 'def' in self.get_action()

player1 = Player('player')
player2 = Player('enemy')

def draw():
    if now_page == 'start':
        screen.clear()
        screen.fill((0, 0, 0))

    if now_page == 'battle':
        screen.clear()
        screen.fill((0, 0, 0))

        screen.draw.filled_rect(Rect((20, 10), (500, 50)), (0, 0, 0))
        screen.draw.filled_rect(Rect((25, 15), (495, 45)), (255, 255, 255))
        if player1.hp >= 1e-6:
            screen.draw.filled_rect(Rect((25, 15), ((495 - 25) * player1.hp / 100 + 25, 45)), (255, 0, 0))
        screen.draw.text(str(player1.hp), (30, 20))

        screen.draw.filled_rect(Rect((1280 - 500, 10), (1280 - 20, 50)), (0, 0, 0))
        screen.draw.filled_rect(Rect((1280 - 495, 15), (1280 - 25, 45)), (255, 255, 255))
        if player2.hp >= 1e-6:
            screen.draw.filled_rect(Rect((1280 - 25 - (495 - 25) * player2.hp / 100, 15), (1280 - 25, 45)), (255, 0, 0))
        screen.draw.text(str(player2.hp), (1280 - 45, 20))

        player1.actor.draw()
        player2.actor.draw()

    if now_page == 'setting':
        screen.clear()
        screen.fill((0, 0, 0))

def attack(u, v):
    if u.actor.colliderect(v.actor):
        v.hp = max(v.hp - u.atk, 0)
        u.atk_last = time.time()

def attack_defended(u, v):
    if u.actor.colliderect(v.actor):
        v.hp = max(v.hp - u.atk * 0.1, 0)
        u.atk_last = time.time()

def update():
    player1.pos_update()
    player2.pos_update()

    if player1.is_attacking() and not player2.is_defending():
        attack(player1, player2)
    if player1.is_attacking() and player2.is_defending():
        attack_defended(player1, player2)

    if player2.is_attacking() and not player1.is_defending():
        attack(player2, player1)
    if player2.is_attacking() and player1.is_defending():
        attack_defended(player2, player1)


def on_mouse_down(pos):
    pass

def on_key_down(key):
    now_pressed_key.add(key)

def on_key_up(key):
    now_pressed_key.remove(key)

pgzrun.go()