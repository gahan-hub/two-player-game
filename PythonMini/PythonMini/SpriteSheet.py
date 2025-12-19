import pygame
class Sprite__Sheet:
    def __init__(self,filename):
        self.filename=filename
        self.Sprite_Sheet=pygame.image.load(filename).convert_alpha()
    def get_sprite(self,x,y,w,h,scale):
        sprite=pygame.Surface((w,h))
        sprite.set_colorkey((0,0,0))
        sprite.blit(self.Sprite_Sheet,(0,0),(x,y,w,h))
        sprite=pygame.transform.scale(sprite,(w*scale,h*scale))
        return sprite
