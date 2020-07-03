# -*- coding: utf-8 -*-
import pgzrun
import time
import wave
import pygame#仅用来放音乐！！！
import random
WIDTH = 1280
HEIGHT = 720

pygame.mixer.init()
bgmflag=True
track=pygame.mixer.music.load(".\sounds\startbgm.mp3")
eps = 1e-6

player1_key = {
    keys.J: 'atk',
    keys.S: 'def',
    keys.W: 'jump',
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
        'Back': Button(((WIDTH - 60, HEIGHT - 35), (60, 30)), (254, 67, 107), 'Back'),
    },
}

now_pressed_key = set()
now_pressed_button = None

now_page = 'start'

#敌人的行为
def agent():
    act=random.randint(1,12)
    if act>=8: return  'atk'
    if act==1: return 'def'
    if act==2: return 'jump'
    if act==3: return 'right'
    if 5<=act<=7: return 'left'

class Player(object):

    def __init__(self, type):
        # type = 'player' or 'enemy'
        self.type = type
        self.atk = 10
        self.hp = 100
        self.balance=0
        if type == 'player':
            self.actor = Actor('player1_block')
            self.actor.bottomleft = (0, HEIGHT)
        if type == 'enemy':
            self.actor = Actor('player2_block')
            self.actor.bottomright = (WIDTH, HEIGHT)
        
        # 上次攻击和防御的时间
        # 用于内置cd和某些判定
        self.action_last = -10
        self.action_last = -10

        # 在xy方向上的速度
        self.vx = 0
        self.vy = 0

    def get_action(self):
        if self.type == 'player':
            return [player1_key[i] for i in now_pressed_key if i in player1_key]
        else:
            return [agent()]
        
    def pos_update(self):
        action = self.get_action()
        if 'atk' not in action and 'def' not in action:
            if 'left' in action and 'right' in action:
                self.vx = 0
            if 'left' in action and 'right' not in action:
                self.vx = -5
            if 'left' not in action and 'right' in action:
                self.vx = 5
            if 'left' not in action and 'right' not in action:
                self.vx = 0
            if 'jump' in action and self.actor.bottom == HEIGHT:
                self.vy = -18
        else:
            self.vx = 0
        self.vy += 1

        self.actor.left += self.vx
        self.actor.bottom += self.vy
        self.actor.bottom = min(self.actor.bottom, HEIGHT)
        self.actor.top = max(self.actor.top, 0)
        self.actor.right = min(self.actor.right, WIDTH)
        self.actor.left = max(self.actor.left, 0)

    def is_attacking(self):
        return time.time() - self.action_last > 1 and 'atk' in self.get_action()

    def is_defending(self):
        return time.time() - self.action_last > 1 and 'def' in self.get_action()

player1 = Player('player')
player2 = Player('enemy')
def gameinit():
    global bgmflag
    player1.hp=100
    player2.hp=100
    player1.balance=0
    player2.balance=0
    player1.actor.bottomleft = (0, HEIGHT)
    player2.actor.bottomright = (WIDTH, HEIGHT)
    bgmflag=True
def draw():
    global bgmflag
    if now_page == 'start':
        screen.clear()
        screen.blit("start",(0,0))
        if(bgmflag):
            pygame.mixer.music.play()
            bgmflag=False

    if now_page == 'setting':
        screen.clear()
        screen.fill((0, 0, 0))

    if now_page == 'battle':
        if(bgmflag):
            pygame.mixer.music.stop()
            pygame.mixer.music.load(".\sounds\isschinbgm.mp3")
            pygame.mixer.music.play()
            bgmflag=False
        screen.clear()
        screen.fill((255,255,255))#白色背景，适用于黑色火柴人
        #玩家血条
        #screen.draw.filled_rect(Rect((25, 15), (500, 50)), (255, 255, 255))
        if player1.hp >= eps:
            screen.draw.filled_rect(Rect((25, 15), (500 * player1.hp / 100, 50)), (254, 67, 60))
            screen.draw.filled_rect(Rect((25, 65), (40+460 * player1.balance / 100, 30)), (255, 255-55*player1.balance/100, 20))
        screen.draw.text(str(player1.hp), (30, 20))
        screen.draw.text(str(player1.balance), (30, 70),color='black')
        #敌人血条
        #screen.draw.filled_rect(Rect((1280 - 525, 15), (500, 50)), (255, 255, 255))
        if player2.hp >= eps:
            screen.draw.filled_rect(Rect((1280 - 25 - 500 * player2.hp / 100, 15), (500 * player2.hp / 100, 50)), (254, 67, 60))
            screen.draw.filled_rect(Rect((1280 - 25 - 460 * player2.balance / 100-40, 65), (40+460 * player2.balance / 100, 30)), (255, 255-55*player1.balance/100, 20))
        screen.draw.text(str(player2.hp), (1280 - 60, 20))
        screen.draw.text(str(player2.balance), (1280-60, 70),color='black')

        player1.actor.draw()
        player2.actor.draw()

    if now_page == 'battle_end':
        screen.clear()
        screen.fill((0, 0, 0))
        if player2.hp < eps:
            screen.draw.text('player1 win', (WIDTH / 2, HEIGHT / 2))
        else:
            screen.blit("failed",(0,0))

    
    for i, j in button[now_page].items():
        j.paint()

def attack(u, v):
    if u.actor.colliderect(v.actor):
        v.hp = max(v.hp - u.atk, 0)
        v.balance=min(v.balance+u.atk,100)
        u.action_last = time.time()

def attack_defended(u, v):
    if u.actor.colliderect(v.actor):
        v.hp = max(v.hp - u.atk * 0.1, 0)
        u.action_last = time.time()

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
            pygame.mixer.music.stop()
            gameinit()
            now_pressed_button = None

def on_mouse_down(pos):
    global now_pressed_button

    for i, j in button[now_page].items():
        if j.in_button(pos):
            now_pressed_button = i

def on_key_down(key):
    global now_page,bgmflag
    if now_page=="start":
        now_page="battle"
        bgmflag=True
    now_pressed_key.add(key)

def on_key_up(key):
    now_pressed_key.remove(key)

pgzrun.go()