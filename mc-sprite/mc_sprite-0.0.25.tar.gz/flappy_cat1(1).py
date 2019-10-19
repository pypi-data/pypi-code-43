import pygame
import sys
import mc_sprite
import time
from random import randint

SCREEN_SIZE = [900, 600]
RES_PATH = "C:\\Users\\wang1\\Desktop\\lv3_03\\"

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("飞天小猫")

mc_sprite.Engine.isUseEngineCtrl=True

mc_sprite.Time.SetFPS(90)#设定帧数 默认 60

mc_sprite.Engine.Start(screen)

pygame.mixer.music.load(RES_PATH + "BGM.wav")
pygame.mixer.music.play(-1, 0.0)

bg1 = mc_sprite.GameObject(RES_PATH + "bg.png", 1)
bg2 = mc_sprite.GameObject(RES_PATH + "bg.png", 2)

bg1.transform.position.Set(0, 0)
bg2.transform.position.Set(1333, 0)

airship_role = mc_sprite.GameObject(RES_PATH + "airship_role.png", 3)
airship_role.transform.position.Set((SCREEN_SIZE[0] - airship_role.transform.width) // 2, 200)
airship = mc_sprite.GameObject(RES_PATH + "airship.png", 4)
airship.transform.position.Set((SCREEN_SIZE[0] - airship.transform.width) // 2, 100)

airship_direction = mc_sprite.Vector.down

cat = mc_sprite.GameObject(RES_PATH + "cat_01.png", 5)
cat.Add(RES_PATH + "cat_02.png")
cat.transform.position.Set((SCREEN_SIZE[0] - cat.transform.width) // 2, 330)

info_type = mc_sprite.GameObject(RES_PATH + "info_tap.png", 6)
info_type.transform.position.Set(750, 550)

collider = mc_sprite.Collider(cat)

wall_list = []
for i in range(5):
    wall_list.append(mc_sprite.GameObject(RES_PATH + "wall.png", i + 7))
    wall_list[i].transform.Translate(60, 60)
    wall_list[i].transform.position.Set(900 + i * 400, 0)
    pass
#print(wall_list[0].transform.image.get_at((50,400)))

for i in range(5):
    collider.Add(wall_list[i])#添加碰撞对象
    pass
collider.Del(wall_list[3])#移除碰撞对象


mc_sprite.Engine.RegisterCollider(collider)

game_status = 0
cat_speed = 0

mc_sprite.Engine.isDrawColliderRect=True#显示碰撞框

while True:
    if mc_sprite.Engine.isMouseDown():
        if game_status == 0:
            game_status = 1
        else:
            cat.Set(1)
            pygame.mixer.Sound(RES_PATH + "bubble.wav").play()
    else:
        cat.Set(0)

    if bg1.transform.position.x < float(-1333):
        bg1.transform.position.x = 1333
    else:
        bg1.transform.position = mc_sprite.Vector.Move(bg1.transform.position, 80, mc_sprite.Vector.left)

    if bg2.transform.position.x < float(-1333):
        bg2.transform.position.x = 1333
    else:
        bg2.transform.position = mc_sprite.Vector.Move(bg2.transform.position, 80, mc_sprite.Vector.left)

    if game_status == 0:
        if airship.transform.position.y < float(50):
            airship_direction = mc_sprite.Vector.down
        if airship.transform.position.y > float(150):
            airship_direction = mc_sprite.Vector.up
        
        airship.transform.position = mc_sprite.Vector.Move(airship.transform.position, 50, airship_direction)
        airship_role.transform.position = mc_sprite.Vector.Move(airship_role.transform.position, 50, airship_direction)
        cat.transform.position = mc_sprite.Vector.Move(cat.transform.position, 50, airship_direction)

    elif game_status == 1:
        airship.SetActive(False)
        airship_role.SetActive(False)
        info_type.SetActive(False)
        #print(str(wall_list[0].transform.position.value)+" : "+str(wall_list[1].transform.position.value)+" : "+str(wall_list[2].transform.position.value)+" : "+str(wall_list[3].transform.position.value)+" : "+str(wall_list[4].transform.position.value))
        for i in range(len(wall_list)):
            wall_list[i].transform.position = mc_sprite.Vector.Move(wall_list[i].transform.position, 80, mc_sprite.Vector.left)
            if wall_list[i].transform.position.x < -200:
                if i != 0:
                    wall_list[i].transform.position.Set(wall_list[i - 1].transform.position.x + 400, 0)
                else:
                    wall_list[i].transform.position.Set(wall_list[len(wall_list) - 1].transform.position.x + 400, 0)
       
        if collider.isCollision:
            print('a')
            
    mc_sprite.Engine.Draw()

        
