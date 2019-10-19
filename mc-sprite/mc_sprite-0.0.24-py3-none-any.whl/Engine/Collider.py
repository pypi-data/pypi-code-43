
import pygame
class Collider:
    def __init__(self, obj):
        self.group=[]
        obj.isMianCol=True
        obj.mycol=self
        self.obj=obj.transform
        self.isCollision=False
        pass
    def Add(self, obj):
        obj.ColList.append(self.obj.parent.mycol)
        obj.isCol=True
        self.group.append(obj.transform)
        pass
    def Del(self, obj):
        obj.isCol=False
        for x in self.group:
            if x.parent.thisID == obj.thisID:
                self.group.remove(x)
        pass
    def collision(self):
        for x in self.group:
            if(pygame.sprite.collide_mask(self.obj,x)):
                #print(x.parent.priority,pygame.sprite.collide_mask(self.obj,x))
                self.isCollision=True
                return True
            else:
                self.isCollision=False

            #xoffset = self.obj.rect.x - x.rect.x
            #yoffset = self.obj.rect.y - x.rect.y

            #point = x.mask.overlap(self.obj.mask, (xoffset, yoffset))
            #someArea = x.mask.overlap_mask(self.obj.mask, (xoffset, yoffset))
            #if point:
                #px,py=point
                #cx,cy = px - x.rect.x, py - x.rect.y
                #pixel1=x.image.get_at((cx,cy))

                #qx,qy=px - self.obj.rect.x, py - self.obj.rect.y
                #pixel2=self.obj.image.get_at((qx,qy))

                #print(point,someArea,pixel1,pixel2)
        return False