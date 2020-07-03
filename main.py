import pgzrun
import time

WIDTH = 1280
HEIGHT = 720

eps = 1e-6

player1_key = {
    keys.J: 'atk',
    keys.S: 'def',
    keys.K: 'jump',
    keys.A: 'left',
    keys.D: 'right',
}

class Button(object):

    def __init__(self, pos, color, text):
        self.pos = pos
        self.color = color
        self.text = text

    def paint(self):
        screen.draw.filled_rect(Rect(self.pos[0], self.pos[1]), self.color)
        screen.draw.text(self.text, self.pos[0])

    # 判断p是否在按钮内
    def in_button(self, p):
        return 0 <= p[0] - self.pos[0][0] <= self.pos[1][0] and 0 <= p[1] - self.pos[0][1] <= self.pos[1][1]

button = {
    'start': {
    },
    'setting': {
    },
    'battle': {
    },
    'battle_end': {
        'Back': Button(((WIDTH / 2 - 30, HEIGHT * 2 / 3 - 15), (60, 30)), (255, 0, 0), 'Back'),
    },
}

now_pressed_key = set()
now_pressed_button = None

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
        return time.time() - self.atk_last > 0.2 and 'atk' in self.get_action()

    def is_defending(self):
        return time.time() - self.def_last > 0.2 and 'def' in self.get_action()

player1 = Player('player')
player2 = Player('enemy')

def draw():
    if now_page == 'start':
        screen.clear()
        screen.fill((0, 0, 0))

    if now_page == 'setting':
        screen.clear()
        screen.fill((0, 0, 0))

    if now_page == 'battle':
        screen.clear()
        screen.fill((0, 0, 0))

        screen.draw.filled_rect(Rect((25, 15), (500, 50)), (255, 255, 255))
        if player1.hp >= eps:
            screen.draw.filled_rect(Rect((25, 15), (500 * player1.hp / 100, 50)), (255, 0, 0))
        screen.draw.text(str(player1.hp), (30, 20))

        screen.draw.filled_rect(Rect((1280 - 525, 15), (500, 50)), (255, 255, 255))
        if player2.hp >= eps:
            screen.draw.filled_rect(Rect((1280 - 25 - 500 * player2.hp / 100, 15), (500 * player2.hp / 100, 50)), (255, 0, 0))
        screen.draw.text(str(player2.hp), (1280 - 60, 20))

        player1.actor.draw()
        player2.actor.draw()

    if now_page == 'battle_end':
        screen.clear()
        screen.fill((0, 0, 0))
        if player2.hp < eps:
            screen.draw.text('player1 win', (WIDTH / 2, HEIGHT / 2))
        else:
            screen.draw.text('player2 win', (WIDTH / 2, HEIGHT / 2))
    
    for i, j in button[now_page].items():
        j.paint()

def attack(u, v):
    if u.actor.colliderect(v.actor):
        v.hp = max(v.hp - u.atk, 0)
        u.atk_last = time.time()

def attack_defended(u, v):
    if u.actor.colliderect(v.actor):
        v.hp = max(v.hp - u.atk * 0.1, 0)
        u.atk_last = time.time()

def update():
    global now_page, now_pressed_button

    if now_page == 'battle':
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

        if player1.hp < eps or player2.hp < eps:
            now_page = 'battle_end'

    if now_page == 'battle_end':
        if now_pressed_button == 'Back':
            now_page = 'start'
            now_pressed_button = None

def on_mouse_down(pos):
    global now_pressed_button

    for i, j in button[now_page].items():
        if j.in_button(pos):
            now_pressed_button = i

def on_key_down(key):
    now_pressed_key.add(key)

def on_key_up(key):
    now_pressed_key.remove(key)

pgzrun.go()