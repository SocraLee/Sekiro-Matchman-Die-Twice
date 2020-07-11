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
ENEMYhp=200#敌人生命值
ENEMYbalance=200#敌人平衡值
ENEMYattack=30#敌人攻击力
AttackPeriod=0.9# 攻击总耗时
AttackUpdate=0.3# 攻击阶段更新间隔
ActionGap=0.9# 从一个动作发起到另一个动作发起的间隔
BounceTime=0.6

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

    def __init__(self, pos, img):
        self.button = Actor(img)
        self.button.topleft = pos

    def paint(self):
        self.button.draw()

    # 判断p是否在按钮内
    def in_button(self, p):
        return self.button.collidepoint(p)

button = {
    'start': {
    },
    'setting': {
    },
    'battle': {
    },
    'battle_end': {
        'Back': Button((WIDTH / 2 - 110, HEIGHT * 7 / 8), 'backbutton'),
    },
}

now_pressed_key = set()
now_pressed_button = None

now_page = 'start'

#敌人的行为
def agent(player1,player2):
    if(player2.bounced>0):return 'def'
    if(player1.bounced>0):return 'atk'
    if(player1.attackSchedule>0):
        key=random.random()
        if(key>0.3 and time.time()-player1.attackSchedule<0.4):
            return 'left'
        elif(key<0.3 and time.time()-player1.attackSchedule>=0.4):
            return  'def'
    act=random.random()
    if(player1.body.right-player2.body.left<-3):
        if(act<0.8):
            return 'left'
        else:
            return 'atk'
    if(player1.body.left-player2.body.right>3):
        if (act < 0.8):
            return 'right'
        else:
            return 'atk'
    else: return 'atk'



class Player(object):

    def __init__(self, type):
        # type = 'player' or 'enemy'
        self.type = type
        self.atk = 10
        self.hp = 100
        self.balance=0
        self.anger=10
        if type == 'player':
            self.body = Actor('left_body')
            self.sword = Actor('left_sword')
            self.body.bottomleft = (0, HEIGHT)
            self.sword.bottomleft = (0, HEIGHT)
        if type == 'enemy':
            self.body = Actor('right_body')
            self.sword = Actor('right_sword')
            self.atk=ENEMYattack
            self.hp=ENEMYhp
            self.body.bottomleft = (WIDTH, HEIGHT)
            self.sword.bottomleft = (WIDTH, HEIGHT)
        
        # 上次攻击和防御的时间
        # 用于内置cd和某些判定
        self.action_last = -10#上一个动作的起始时间1
        self.attackSchedule=-10#攻击动作的起始时间
        self.defendeSchedule=-10#防御动作的起始时间
        self.skillSchedule=-10#技能释放的起始时间
        self.bounced=-10#记录被弹开的起始时间
        self.attackFlag=False#是否成功进行了攻击判定
        self.defenseFlag=0
        # 在xy方向上的速度
        self.vx = 0
        self.vy = 0

    def get_action(self):
        if self.type == 'player':
            return [player1_key[i] for i in now_pressed_key if i in player1_key]
        else:
            return [agent(player1,self)]
        
    def update(self):
        action = self.get_action()
        #若要求释放技能时不能移动，则更新if条件
        if ( ('atk' not in action and 'def' not in action) or self.body.bottom < HEIGHT):
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

        t=time.time()
        if t - self.action_last > ActionGap and self.attackSchedule<0 and 'atk' in action and t-self.bounced>=BounceTime:
            self.attackSchedule=time.time()
            self.action_last=time.time()
            self.attackFlag=False

        if t - self.action_last > ActionGap and self.defendeSchedule<0 and 'def' in action and t-self.bounced>=BounceTime:
            self.defendeSchedule=time.time()
            self.action_last=time.time()
            self.defenseFlag=0

    def is_attacking(self):
        if self.attackSchedule<0 and self.skillSchedule<0:#并非攻击进行中
            return False
        else: return True

    def is_defending(self):
        if self.defendeSchedule<0:
            return False
        else: return True

    def state_update(self):
        if (self.skillSchedule > 0):
            if (time.time() - self.skillSchedule > 0.6):
                self.skillSchedule = -10
        if (self.defendeSchedule > 0):
            if (time.time() - self.defendeSchedule > 0.5):
                self.defendeSchedule = -10
        if (self.attackSchedule > 0):
            if (time.time() - self.attackSchedule > 0.8):
                self.attackSchedule = -10
        if (self.bounced >= 0):
            if (time.time() - self.bounced > 0.5):
                self.bounced = -10

    def img_update(self,text):
        if (self.bounced > 0 and time.time() - self.bounced < BounceTime):
            self.body.image = text + 'bounce_body'
            self.sword.image = text + 'bounce_sword'
            # elif(player2.anger>=10 and player2.skillSchedule<0):
            #     player2.skillSchedule=time.time()
            #     player2.action_last =time.time()
            #     龙闪()
            #     player2.anger=0
            # elif(t-player2.skillSchedule<0.5):
            #     temp=t-player2.skillSchedule
            #     if(temp<0.3):
            #         player2.body.image=player2text+'attack0'
            #         player2.sword.image=player2text+'attack0'
            #     elif(temp<0.4):
            #         player2.body.image=player2text+'attack1'
            #         player2.sword.image=player2text+'attack1'
            #     elif(temp<0.47):
            #         player2.body.image=player2text+'attack2'
            #         player2.sword.image=player2text+'attack2'
            #     elif(temp<0.57):
            #         player2.body.image=player2text+'attack3'
            #         player2.sword.image=player2text+'attack3'
            #     else:
            #         player2.body.image=player2text+'attack4'
            #         player2.sword.image=player2text+'attack4'
        elif (self.defendeSchedule < 0 and self.attackSchedule < 0 and self.skillSchedule < 0 and self.bounced < 0):
            self.body.image = text + 'stand'
            self.sword.image = text + 'stand'
        elif (self.defendeSchedule > 0):
            if (self.defenseFlag == 0):
                self.body.image = text + 'defense'
                self.sword.image = text + 'defense'
            if (self.defenseFlag == 1):
                self.body.image = text + 'normaldefense_body'
                self.sword.image = text + 'normaldefense_sword'
            if (self.defenseFlag == 2):
                self.body.image = text + 'perfectdefense'
                self.sword.image = text + 'perfectdefense'
        if (self.attackSchedule > 0):
            if (time.time() - self.attackSchedule <= AttackUpdate):
                self.body.image = text + 'cut1_body'
                self.sword.image = text + 'cut1_sword'
            elif (time.time() - self.attackSchedule <= 2*AttackUpdate):
                self.body.image = text + 'cut2_body'
                self.sword.image = text + 'cut2_sword'
            else:
                self.body.image = text + 'cut3_body'
                self.sword.image = text + 'cut3_sword'
        self.body.draw()
        self.sword.draw()


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
        if player1.hp >= eps:
            screen.draw.filled_rect(Rect((25, 15), (500 * player1.hp / 100, 50)), (254, 67, 60))
            screen.draw.filled_rect(Rect((25, 65), (40+460 * player1.balance / 100, 30)), (255, 255-55*player1.balance/100, 20))
        screen.draw.text(str(player1.hp), (30, 20))
        screen.draw.text(str(player1.balance), (30, 70),color='black')
        #敌人血条
        if player2.hp >= eps:
            screen.draw.filled_rect(Rect((1280 - 25 - 500 * player2.hp / ENEMYhp, 15), (500 * player2.hp / ENEMYhp, 50)), (254, 67, 60))
            screen.draw.filled_rect(Rect((1280 - 25 - 460 * player2.balance / ENEMYbalance-40, 65), (40+460 * player2.balance / ENEMYbalance, 30)), (255, 255-55*player2.balance/ENEMYbalance, 20))
        screen.draw.text(str(player2.hp), (1280 - 60, 20))
        screen.draw.text(str(player2.balance), (1280-60, 70),color='black')

        #更新状态
        player1.state_update()
        player2.state_update()

        #判断相对位置
        player1text=''
        player2text=''
        if(player1.body.left<=player2.body.left):
            player1text='player1/player1left'
            player2text='player2/player2right'
        else:
            player1text='player1/player1right'
            player2text='player2/player2left'

        #更新图像
        player1.img_update(player1text)
        player2.img_update(player2text)

    if now_page == 'battle_end':
        screen.clear()
        screen.fill((0, 0, 0))
        if player2.hp < eps or player2.balance>200-eps:
            screen.blit("succeed",(0,0))
        else:
            screen.blit("failed",(0,0))

    
    for i, j in button[now_page].items():
        j.paint()

def attack(u, v):
    if(u.attackFlag==True):return
    #攻击
    if(u.skillSchedule>0):
        if(u.sword.colliderect(v.body)):
            v.hp=max(v.hp - 2*u.atk, 0)
            if (v.type == 'player'):
                v.balance = min(v.balance + u.atk, 100)
            else:
                v.balance = min(v.balance + u.atk * 0.5, 200)
            受伤()
            if(v.action_last<0):
                v.action_last=time.time()+0.2
            else:
                v.action_last=v.action_last+0.2
    else:
        攻击()
        if u.sword.colliderect(v.body):
            v.hp = max(v.hp - u.atk, 0)
            if(v.type=='player'):
                v.balance=min(v.balance+u.atk*0.5,100)
            else:
                v.balance=min(v.balance+u.atk*0.3,200)
            受伤()
            u.attackFlag=True
            #
            #除非防御，攻击应打断被攻击方动作
            #

def attack_defended(u,v):
    if(u.attackFlag==True):return
    t=time.time()
    #弹技能
    if (u.skillSchedule > 0):
        if u.sword.colliderect(v.body):
            if(t-v.defendeSchedule>0.2):
                普通防御()
                v.balance=min(100,v.balance+u.atk)
                v.hp=min(100,v.hp-u.atk*0.3)
                u.skillSchedule=-10
                v.anger+=3
        #完美格挡
            else:
                完美弹反()
                if (u.type == 'player'):
                    u.balance = min(u.balance + u.atk * 2, 100)
                else:
                    u.balance = min(u.balance + u.atk * 0.3, 200)
                    u.anger+=3
                u.skillSchedule=-10
                u.action_last=t+1#从当前时间记，额外1s硬直
                u.bounced=t+1
    #弹普攻
    else:
        #不完美格挡
        if u.sword.colliderect(v.body):
            if(t-v.defendeSchedule>0.3):
                普通防御()
                v.balance=min(100,v.balance+u.atk)
                u.attackFlag=True
                v.anger+=3
                v.defenseFlag=1
        #完美格挡
            else:
                完美弹反()

                if (u.type == 'player'):
                    u.balance = min(u.balance + u.atk * 2, 100)
                else:
                    u.balance = min(u.balance + u.atk * 0.5, 200)
                    u.anger+=3
                u.attackFlag=True
                u.action_last=t+0.5#从当前时间记，额外0.5s硬直
                u.bounced=t
                v.defenseFlag=2

def special_attack(u,v):
    pass

def special_defended(u,v):
    pass

def update():
    global now_page, now_pressed_button

    if now_page == 'battle':
        player1.update()
        player2.update()

        t=time.time()
        if player1.is_attacking() and not player2.is_defending():
            if(time.time()-player1.attackSchedule>=0.4):
                attack(player1, player2)
        elif player1.is_attacking() and player2.is_defending():
            if(time.time()-player1.attackSchedule>=0.4):
                attack_defended(player1, player2)

        if player2.is_attacking() and not player1.is_defending():
            if(time.time()-player2.attackSchedule>=0.6):
                attack(player2, player1)
        elif player2.is_attacking() and player1.is_defending():
            if(time.time()-player2.attackSchedule>=0.6):
                attack_defended(player2, player1)

        if player1.hp < eps or player2.hp < eps or player1.balance>100-eps or player2.balance>200-eps:
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