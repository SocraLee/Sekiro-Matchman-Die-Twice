# -*- coding: utf-8 -*-
import pgzrun
import time
import wave
import pygame#仅用来放音乐！！！
import random
import platform


def 不死斩():
    sounds.不死斩.play()
def 攻击():
    sounds.攻击.play()
def 雷电():
    sounds.雷电.play()
def 龙闪():
    sounds.龙闪.play()
def 普通防御():
    sounds.普通防御.play()
def 受伤():
    sounds.受伤.play()
def 完美弹反():
    sounds.完美弹反.play()
def 一心():
    sounds.一心.play()


WIDTH = 1280
HEIGHT = 720

SYS = platform.system().lower()

pygame.mixer.init()
bgmflag=True
if SYS[:3] == 'win':
    track=pygame.mixer.music.load(".\sounds\startbgm.mp3")
else:
    track=pygame.mixer.music.load("./sounds/startbgm.mp3")
eps = 1e-6

player1_key = {
    keys.J: 'atk',
    keys.K: 'def',
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
    if act==1 or act==2: return 'def'
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
            self.body = Actor('left_body')
            self.sword = Actor('left_sword')
            self.body.bottomleft = (0, HEIGHT)
            self.sword.bottomleft = (0, HEIGHT)
        if type == 'enemy':
            self.body = Actor('right_body')
            self.sword = Actor('right_sword')
            self.body.bottomleft = (WIDTH, HEIGHT)
            self.sword.bottomleft = (WIDTH, HEIGHT)
        
        # 上次攻击和防御的时间
        # 用于内置cd和某些判定
        self.action_last = -10
        self.attackSchedule=-10
        self.defendeSchedule=-10
        # 在xy方向上的速度
        self.vx = 0
        self.vy = 0

    def get_action(self):
        if self.type == 'player':
            return [player1_key[i] for i in now_pressed_key if i in player1_key]
        else:
            return [agent()]
        
    def update(self):
        action = self.get_action()
        if ('atk' not in action and 'def' not in action) or self.body.bottom < HEIGHT:
            if 'left' in action and 'right' in action:
                self.vx = 0
            if 'left' in action and 'right' not in action:
                self.vx = -5
            if 'left' not in action and 'right' in action:
                self.vx = 5
            if 'left' not in action and 'right' not in action:
                self.vx = 0
            if 'jump' in action and self.body.bottom == HEIGHT:
                self.vy = -18
        else:
            self.vx = 0
        self.vy += 1

        self.body.left += self.vx
        self.body.bottom += self.vy
        self.body.bottom = min(self.body.bottom, HEIGHT)
        self.body.top = max(self.body.top, 0)
        self.body.right = min(self.body.right, WIDTH)
        self.body.left = max(self.body.left, 0)

        self.sword.left += self.vx
        self.sword.bottom += self.vy
        self.sword.bottom = min(self.sword.bottom, HEIGHT)
        self.sword.top = max(self.sword.top, 0)
        self.sword.right = min(self.sword.right, WIDTH)
        self.sword.left = max(self.sword.left, 0)

        if time.time() - self.action_last > 0.7 and 'atk' in action:
            self.attackSchedule=time.time()
            self.action_last=time.time()

        if time.time() - self.action_last > 0.7 and 'def' in action:
            self.defendeSchedule=time.time()
            self.action_last=time.time()

    def is_attacking(self):
        if self.attackSchedule<0:#并非攻击进行中
            return True
        else: return True

    def is_defending(self):
        if self.defendeSchedule<0:
            return True
        else: return True

player1 = Player('player')
player2 = Player('enemy')

def gameinit():
    global bgmflag, player1, player2
    player1 = Player('player')
    player2 = Player('enemy')
    bgmflag=True

def draw():
    global bgmflag
    if now_page == 'start':
        screen.clear()
        screen.blit("start",(0,0))
        if(bgmflag):
            if SYS[:3] == 'win':
                pygame.mixer.music.load(".\sounds\startbgm.mp3")
            else:
                pygame.mixer.music.load("./sounds/startbgm.mp3")
            pygame.mixer.music.play()
            bgmflag=False

    if now_page == 'setting':
        screen.clear()
        screen.fill((0, 0, 0))

    if now_page == 'battle':
        if(bgmflag):
            pygame.mixer.music.stop()
            if SYS[:3] == 'win':
                pygame.mixer.music.load(".\sounds\isschinbgm.mp3")
            else:
                pygame.mixer.music.load("./sounds/isschinbgm.mp3")
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

        #判断是否重置攻击防御动作
        t=time.time()
        if(player1.defendeSchedule>0):
            if(t-player1.defendeSchedule>0.5):
                player1.defendeSchedule=-10
        if(player1.attackSchedule>0):
            if(t-player1.attackSchedule>0.7):
                player1.attackSchedule=-10

        if(player2.defendeSchedule>0):
            if(t-player2.defendeSchedule>0.5):
                player2.defendeSchedule=-10
        if(player2.attackSchedule>0):
            if(t-player2.attackSchedule>0.7):
                player2.attackSchedule=-10

        #判断相对位置
        player1text=''
        player2text=''
        if(player1.body.left<=player2.body.left):
            player1text='player1/player1left'
            player2text='player2/player2right'
        else:
            player1text='player1/player1right'
            player2text='player2/player2left'
        #判断动作
        if(player1.defendeSchedule<0 and player1.attackSchedule<0):
            player1.body.image=player1text+'attack2_body'
            player1.sword.image=player1text+'attack2_sword'
        elif(player1.defendeSchedule>0):
            player1.body.image=player1text+'defense_body'
            player1.sword.image=player1text+'defense_sword'
        elif(player1.attackSchedule>0):
            if(t-player1.attackSchedule<=0.3):
                player1.body.image =player1text+ 'cut1_body'
                player1.sword.image = player1text+'cut1_sword'
            elif(t-player1.attackSchedule<=0.5):
                player1.body.image =player1text+ 'cut2_body'
                player1.sword.image = player1text+'cut2_sword'
            else:
                player1.body.image =player1text+ 'cut3_body'
                player1.sword.image = player1text+'cut3_sword'

        if (player2.defendeSchedule < 0 and player2.attackSchedule < 0):
            player2.body.image=player2text+'attack2_body'
            player2.sword.image=player2text+'attack2_sword'
        elif (player2.defendeSchedule > 0):
            player2.body.image =player2text+ 'defense_body'
            player2.sword.image =player2text+ 'defense_sword'
        elif (player2.attackSchedule > 0):
            if (t - player2.attackSchedule <= 0.3):
                player2.body.image = player2text + 'cut1_body'
                player2.sword.image = player2text + 'cut1_sword'
            elif (t - player2.attackSchedule <= 0.5):
                player2.body.image = player2text + 'cut2_body'
                player2.sword.image = player2text + 'cut2_sword'
            else:
                player2.body.image = player2text + 'cut3_body'
                player2.sword.image = player2text + 'cut3_sword'

        player1.body.draw()
        player1.sword.draw()
        player2.body.draw()
        player2.sword.draw()

    if now_page == 'battle_end':
        screen.clear()
        screen.fill((0, 0, 0))
        if player2.hp < eps or player2.balance>100-eps:
            screen.draw.text('player1 win', (WIDTH / 2, HEIGHT / 2))
        else:
            screen.blit("failed",(0,0))

    
    for i, j in button[now_page].items():
        j.paint()

def attack(u, v):
    #攻击
    攻击()
    if u.sword.colliderect(v.body):
        v.hp = max(v.hp - u.atk, 0)
        v.balance=min(v.balance+u.atk*0.5,100)
        受伤()
        u.attackSchedule=-10
        #
        #攻击应打断被攻击方动作
        #

def attack_defended(u, v):
    #不完美格挡
    t=time.time()
    if u.sword.colliderect(v.body):
        if(t-v.defendeSchedule>0.4):
            普通防御()
            v.balance=min(100,v.balance+u.atk)
            u.attackSchedule=-10
    #完美格挡
        else:
            完美弹反()
            u.balance=min(100,u.balance+v.atk*2)
            u.attackSchedule=-10
            u.action_last+=0.5#额外0.5s硬直

def update():
    global now_page, now_pressed_button

    if now_page == 'battle':
        player1.update()
        player2.update()

        t=time.time()
        if player1.is_attacking() and not player2.is_defending():
            if(t-player1.attackSchedule>=0.5):
                attack(player1, player2)
        elif player1.is_attacking() and player2.is_defending():
            if(t-player1.attackSchedule>=0.5):
                attack_defended(player1, player2)

        if player2.is_attacking() and not player1.is_defending():
            if(t-player2.attackSchedule>=0.5):
                attack(player2, player1)
        elif player2.is_attacking() and player1.is_defending():
            if(t-player2.attackSchedule>=0.5):
                attack_defended(player2, player1)

        if player1.hp < eps or player2.hp < eps or player1.balance>100-eps or player2.balance>100-eps:
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