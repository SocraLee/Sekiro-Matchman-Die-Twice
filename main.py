# -*- coding: utf-8 -*-
import pgzrun
import time
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
def 完美弹反(n=0):
    sounds.完美弹反.play(n)
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
SkillJudgeTime=1.5
SkillPeriod=2
BounceTime=0.6

bgmflag=True
eps = 1e-6

player1_key = {
    keys.J: 'atk',
    keys.K: 'def',
    keys.W: 'jump',
    keys.A: 'left',
    keys.D: 'right',
    keys.U:'dragonSlash',
    keys.I:'Immor',
    keys.O:'superCut'
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
        'Easy': Button((WIDTH / 2 - 110, HEIGHT * 64 / 100), 'buttoneasy'),
        'Normal': Button((WIDTH / 2 - 110, HEIGHT * 74 / 100), 'buttonnormal'),
        'Hard': Button((WIDTH / 2 - 110, HEIGHT * 84 / 100), 'buttonhard'),
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

difficulty = None

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
        global difficulty,ENEMYhp, ENEMYbalance, ENEMYattack
        # type = 'player' or 'enemy'
        self.type = type
        self.atk = 10
        self.hp = 100
        self.balance=0
        self.anger=0
        if type == 'player':
            self.body = Actor('left_body')
            self.sword = Actor('left_sword')
            self.body.bottomleft = (0, HEIGHT)
            self.sword.bottomleft = (0, HEIGHT)
        if type == 'enemy':
            self.body = Actor('right_body')
            self.sword = Actor('right_sword')

            if(difficulty=='Hard'):
                ENEMYhp = 200
                ENEMYbalance = 200
                ENEMYattack = 30
            elif(difficulty=='Normal'):
                ENEMYhp=150
                ENEMYbalance=150
                ENEMYattack=20
            elif(difficulty=='Easy'):
                ENEMYhp = 100
                ENEMYbalance = 100
                ENEMYattack = 10
            self.atk = ENEMYattack
            self.hp = ENEMYhp
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
        self.skillFlag=False#技能是否进行了攻击判定
        self.skillMove=False#技能是否已经完成突进
        self.defenseFlag=0
        self.skillChoice=""
        self.skill=["superCut","Immor","dragonSlash"]#
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
        if ( self.skillSchedule<0 and(('atk' not in action and 'def' not in action) or self.body.bottom < HEIGHT)):
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
        if(self.type=='enemy'):
            if t - self.action_last > ActionGap and self.attackSchedule<0 and self.skillSchedule<0 and 'atk' in action and t-self.bounced>=BounceTime:
                if(self.anger>10 or (difficulty=='Hard' and self.anger>6)):
                    self.anger=0
                    self.skillSchedule=time.time()
                    self.action_last=time.time()
                    self.skillFlag=False
                    self.skillMove=False
                    self.skillChoice=random.choice(self.skill)
                    #拍视频展示不同技能用
                    #self.skill.remove(self.skillChoice)
                    if(self.skillChoice=='dragonSlash'):一心()#英文命名反了，将错就错吧XD反正没人知道
                    elif(self.skillChoice=='Immor'):
                        不死斩()
                        self.skillMove=True
                    elif(self.skillChoice=='superCut'): 龙闪()

                else:
                    self.attackSchedule=time.time()
                    self.action_last=time.time()
                    self.attackFlag=False
        elif(self.type=='player'):
            if t - self.action_last > ActionGap and self.attackSchedule < 0 and self.skillSchedule < 0 and t - self.bounced >= BounceTime:
                if ('Immor' in action or "dragonSlash" in action or "superCut"in action):
                    self.anger = 0
                    self.skillSchedule = time.time()
                    self.action_last = time.time()
                    self.skillFlag = False
                    self.skillMove = False
                    #发动第一个按下的技能
                    for skill in action:
                        if (skill=='Immor' or skill== "dragonSlash" or skill=="superCut"):
                            self.skillChoice=skill
                            break
                    if (self.skillChoice == 'dragonSlash'):
                        一心()
                    elif (self.skillChoice == 'Immor'):
                        不死斩()
                        self.skillMove = True
                    elif (self.skillChoice == 'superCut'):
                        龙闪()

                elif('atk'in action):
                    self.attackSchedule = time.time()
                    self.action_last = time.time()
                    self.attackFlag = False


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
            if (time.time() - self.skillSchedule > SkillPeriod):
                self.skillSchedule = -10
        if (self.defendeSchedule > 0):
            if (time.time() - self.defendeSchedule > 0.5):
                self.defendeSchedule = -10
        if (self.attackSchedule > 0):
            if (time.time() - self.attackSchedule > AttackPeriod):
                self.attackSchedule = -10
        if (self.bounced >= 0):
            if (time.time() - self.bounced > BounceTime):
                self.bounced = -10

    #实际上，仅仅对普攻进行的sword和body分离是有意义的，但为了更好的判定，还是整体上进行了分离
    def img_update(self,text):
        if (self.bounced > 0 and time.time() - self.bounced < BounceTime):
            self.body.image = text + 'bounce_body'
            self.sword.image = text + 'bounce_sword'
        elif(self.skillSchedule>0 and  time.time()-self.skillSchedule<SkillPeriod):
            temp=time.time()-self.skillSchedule
            if(self.skillChoice=='dragonSlash'):
                if(temp<1.2):
                    self.body.image=text+'attack0'
                    self.sword.image=text+'attack0'
                elif(temp<1.4):
                    self.body.image=text+'attack1'
                    self.sword.image=text+'attack1'
                elif(temp<1.6):
                    self.body.image=text+'attack2_body'
                    self.sword.image=text+'attack2_sword'
                elif(temp<1.8):
                    self.body.image=text+'attack2_body'
                    self.sword.image=text+'attack2_sword'
                else:
                    self.body.image=text+'attack4'
                    self.sword.image=text+'attack4'
            elif(self.skillChoice=='Immor'):
                if(temp<0.8):
                    self.body.image=text+'attack0'
                    self.sword.image=text+'attack0'
                elif(temp<1.4):
                    self.body.image=text+'cut1'
                    self.sword.image=text+'cut1'
                else:
                    self.body.image=text+'attack22'
                    self.sword.image=text+'attack22'

            elif(self.skillChoice=='superCut'):
                if(temp<1.2):
                    self.body.image=text+'attack0'
                    self.sword.image=text+'attack0'
                elif(temp<1.4):
                    self.body.image=text+'attack1'
                    self.sword.image=text+'attack1'
                else:
                    self.body.image=text+'stab'
                    self.sword.image=text+'stab'
        elif (self.defendeSchedule < 0 and self.attackSchedule < 0 and self.skillSchedule < 0 and self.bounced < 0):
            if(self.body.bottom < HEIGHT):
                self.body.image = text + 'jump'
                self.sword.image = text + 'jump'
            else:
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
    global bgmflag,ENEMYhp,ENEMYattack,ENEMYbalance,difficulty
    if now_page == 'start':
        screen.clear()
        screen.blit("start",(0,0))
        if(bgmflag):
            music.play("startbgm")
            bgmflag=False

    if now_page == 'battle':
        if(bgmflag):
            music.stop()
            if(difficulty=="Hard"):
                music.play("isschinbgm.mp3")
            else:
                music.play("genichirobgm.mp3")
            bgmflag=False
        screen.clear()
        if(difficulty=='Hard'):screen.blit("pku",(0,0))
        else:screen.blit("bg",(0,0))#白色背景，适用于黑色火柴人


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
            if(difficulty!='Hard'):
                player1text='player1/player1left'
                player2text='player2/player2right'
            if(difficulty=='Hard'):
                player1text = 'player1/player1left'
                player2text = 'player2_cb/player2right'
        else:
            if(difficulty!='Hard'):
                player1text = 'player1/player1right'
                player2text = 'player2/player2left'
            if(difficulty=='Hard'):
                player1text = 'player1/player1right'
                player2text = 'player2_cb/player2left'


        #更新图像
        player1.img_update(player1text)
        player2.img_update(player2text)

    if now_page == 'battle_end':
        screen.clear()
        screen.fill((0, 0, 0))
        if player2.hp < eps or player2.balance>ENEMYbalance-eps:
            screen.blit("succeed",(0,0))
            player1.body.image='player1/player1leftstand'
            if(difficulty=='Hard'):player2.body.image='player2_cb/player2rightfalldown'
            else:player2.body.image='player2/player2rightfalldown'
            player2.body.draw()
            player1.body.draw()

        else:
            screen.blit("failed",(0,0))
            if(bgmflag==True):
                sounds.嘲讽.play()
                bgmflag=False

    
    for i, j in button[now_page].items():
        j.paint()

def attack(u, v):
    if(u.attackFlag==True):return
    攻击()
    if u.sword.colliderect(v.body):
        v.hp = max(v.hp - u.atk, 0)
        if(v.type=='player'):
            v.balance=min(v.balance+u.atk,100)
        else:
            v.balance=min(v.balance+u.atk,ENEMYbalance)
            v.anger+=4
        受伤()
        u.attackFlag=True

def attack_defended(u,v):
    if(u.attackFlag==True):return
    t=time.time()
    #不完美格挡
    if u.sword.colliderect(v.body):
        if(t-v.defendeSchedule>0.2):
            普通防御()
            if(v.type=='player'):v.balance=min(100,v.balance+u.atk)
            else:v.balance=min(ENEMYbalance,v.balance+u.atk)
            u.attackFlag=True
            v.anger+=4
            v.defenseFlag=1
    #完美格挡
        else:
            完美弹反()
            if (u.type == 'player'):
                u.balance = min(u.balance + u.atk * 2, 100)
            else:
                u.balance = min(u.balance + u.atk * 0.5, ENEMYbalance)
                u.anger+=3
            u.attackFlag=True
            u.action_last=t+0.5#从当前时间记，额外0.5s硬直
            u.bounced=t
            v.defenseFlag=2

def special_attack(u,v,text):
    #是否要进行判定
    if (u.skillFlag == True): return
    #是否要进行突进
    if(u.skillMove==False):
        u.skillMove==True
        delta=u.body.left-v.body.left
        if(delta>0):
            u.body.left-=min(delta,20)-3
            u.sword.left-=min(delta,20)-3
        else:
            u.body.left-=max(delta,-20)+3
            u.sword.left-=max(delta,-20)+3
        u.img_update(text)
    if u.sword.colliderect(v.body)or u.body.colliderect(v.body):

        if (v.type == 'player'):
            v.balance = min(v.balance + u.atk, 100)
            v.hp = max(v.hp - 2 * u.atk, 0)
        else:
            v.balance = min(v.balance + u.atk * 5, ENEMYbalance)
            v.hp = max(v.hp - 5 * u.atk, 0)
            v.anger += 3
        受伤()
        u.skillFlag = True

def special_defended(u,v,text):
    global ENEMYbalance,ENEMYhp,ENEMYattack
    #是否还要判定
    if (u.skillFlag == True): return
    #是否要突进
    if(u.skillMove==False):
        u.skillMove==True
        delta=u.body.left-v.body.left
        if(delta>0):
            u.body.left-=min(delta,20)-3
            u.sword.left-=min(delta,20)-3
        else:
            u.body.left-=max(delta,-20)+3
            u.sword.left-=max(delta,-20)+3
        u.img_update(text)
    t = time.time()
    # 不完美格挡
    if u.sword.colliderect(v.body)or u.body.colliderect(v.body):
        if (t - v.defendeSchedule > 0.15):
            普通防御()
            if(v.type=='player'): v.balance = min(100, v.balance + u.atk*2)
            else:v.balance = min(ENEMYbalance, v.balance + u.atk*2)
            #不死斩破防
            if(u.skillChoice=='Immor'):
                if(v.type=='player'):
                    v.hp=max(0,v.hp-u.atk)
                else:
                    v.hp = max(0, v.hp - 2*u.atk)
            u.skillFlag = True
            v.anger += 3
            v.defenseFlag = 1
        # 完美格挡
        else:
            #不死斩不会被弹反
            if(u.skillChoice=='Immor'):
                if(v.type=='player'):
                    v.hp=max(0,v.hp-u.atk)
                else:
                    v.hp = max(0, v.hp - 2*u.atk)
                return
            #产生两次弹反音效
            完美弹反(1)
            if (u.type == 'player'):
                u.balance = min(u.balance + u.atk, 100)
            else:
                u.balance = min(u.balance + min(u.atk * 2,45), ENEMYbalance)
                u.anger += 0
            u.skillFlag = True
            u.action_last = t + 1  # 从当前时间记，额外1s硬直
            u.bounced = t
            v.defenseFlag = 2

def update():
    global now_page, now_pressed_button, bgmflag, difficulty

    if now_page == 'start':
        if now_pressed_button in ['Easy', 'Normal', 'Hard']:
            difficulty = now_pressed_button
            bgmflag = True
            gameinit()
            now_page = 'battle'
            return

    if now_page == 'battle':
        player1.update()
        player2.update()

        t=time.time()

        #标记左右，用于技能动画
        player1text=''
        player2text=''
        if(player1.body.left<=player2.body.left):
            player1text='player1/player1left'
            player2text='player2/player2right'
        else:
            player1text='player1/player1right'
            player2text='player2/player2left'
        #判定普攻
        if player1.is_attacking() and not player2.is_defending():
            if(player1.attackSchedule>0):
                if(time.time()-player1.attackSchedule>=2*AttackUpdate):
                    attack(player1, player2)
            elif(player1.skillSchedule>0):
                if(time.time()-player1.skillSchedule>=SkillJudgeTime):
                    special_attack(player1,player2,player1text)
        elif player1.is_attacking() and player2.is_defending():
            if(player1.attackSchedule>0):
                if(time.time()-player1.attackSchedule>=2*AttackUpdate):
                    attack_defended(player1, player2)
            elif(player1.skillSchedule>0):
                if(time.time()-player1.skillSchedule>=SkillJudgeTime):
                    special_defended(player1,player2,player1text)
        #判定技能
        if player2.is_attacking() and not player1.is_defending():
            if(player2.attackSchedule>0):
                if(time.time()-player2.attackSchedule>=2*AttackUpdate):
                    attack(player2, player1)
            elif(player2.skillSchedule>0):
                if(time.time()-player2.skillSchedule>=SkillJudgeTime):
                    special_attack(player2,player1,player2text)
        elif player2.is_attacking() and player1.is_defending():
            if(player2.attackSchedule>0):
                if(time.time()-player2.attackSchedule>=2*AttackUpdate):
                    attack_defended(player2, player1)
            elif(player2.skillSchedule>0):
                if(time.time()-player2.skillSchedule>=SkillJudgeTime):
                    special_defended(player2,player1,player2text)

        if player1.hp < eps or player2.hp < eps or player1.balance>100-eps or player2.balance>ENEMYbalance-eps:
            bgmflag = True
            now_page = 'battle_end'

    if now_page == 'battle_end':
        if now_pressed_button == 'Back':
            bgmflag = True
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