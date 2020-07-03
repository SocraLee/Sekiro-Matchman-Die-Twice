import pgzrun

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

        # 在xy方向上的速度
        self.vx = 0
        self.vy = 0

    def get_action(self):
        if self.type == 'player':
            return [player1_key[i] for i in now_pressed_key if i in player1_key]
        else:
            #return agent()
            return ''
        
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

player1 = Player('player')
player2 = Player('enemy')

def draw():
    if now_page == 'start':
        screen.clear()
        screen.fill((0, 0, 0))

    if now_page == 'battle':
        screen.clear()
        screen.fill((0, 0, 0))
        player1.actor.draw()
        player2.actor.draw()

    if now_page == 'setting':
        screen.clear()
        screen.fill((0, 0, 0))

count = 0

def update():
    global count
    count += 1
    print(count)
    player1.pos_update()
    player2.pos_update()

def on_mouse_down(pos):
    pass

def on_key_down(key):
    now_pressed_key.add(key)

def on_key_up(key):
    now_pressed_key.remove(key)

pgzrun.go()

# test github desktop