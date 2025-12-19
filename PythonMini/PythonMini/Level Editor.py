import pygame
from SpriteSheet import Sprite__Sheet
import json
pygame.init()
Screen=pygame.display.set_mode((1296,720))
clock=pygame.time.Clock()
font=pygame.font.Font(None,48)
class level_editor:
    def __init__(self):
        tile_sheet=Sprite__Sheet(r'Assets\tilemap.png')
        self.tiles=[]
        self.index=0
        self.dict_map={}
        for i in range (0,20):
            for j in range (0,9):
                self.tiles.append(tile_sheet.get_sprite(i * 19, j * 19, 18, 18, 48 / 18)) 
    def update(self):
        self.show_block(self.index)
        self.place()
        self.map(self.dict_map)
        self.remove()
        keys=pygame.key.get_pressed()
        if keys[pygame.K_s]:
            self.save()
        if keys[pygame.K_l]:
            self.load()
        #print(self.dict_map,pygame.mouse.get_pressed()[2])
    def map(self,map_dict):
        for (x,y) in map_dict:
            Screen.blit(self.tiles[map_dict[(x,y)]],(x*48,y*48))
    def show_block(self,index):
        pos=pygame.mouse.get_pos()
        Screen.blit(self.tiles[index],(int(pos[0]/48)*48,int(pos[1]/48)*48))
    def place(self):
        if pygame.mouse.get_pressed()[0]:
            pos=pygame.mouse.get_pos()
            self.dict_map[(int(pos[0]/48),int(pos[1]/48))]=self.index
    def remove(self):
        if pygame.mouse.get_pressed()[2]:
            pos=pygame.mouse.get_pos()
            try:self.dict_map.pop((int(pos[0]/48),int(pos[1]/48)))        
            except:pass
    def save(self):
        data={}
        for i in self.dict_map:
            data[str(i[0])+','+str(i[1])]=self.dict_map[i]
        with open('Map_json.json','w') as file:
            json.dump(data,file)
    def load(self):
                try:
                    with open('Map_json.json','r') as file:
                        loader= json.load(file)
                        pad= [(int(k.split(',')[0]), int(k.split(',')[1])) for k in loader]
                        for i in pad:
                            self.dict_map[i]=loader[str(int(i[0]))+','+str(int(i[1]))]
                except:pass

LE=level_editor()
while True:
    Screen.fill('black')
    Screen.blit(font.render(str(LE.index),False,'White'),(0,0))
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            pygame.quit()
            quit()
        if event.type==pygame.MOUSEWHEEL:
            if event.y>0:
                LE.index=min(179,LE.index+1)
            if event.y<0:
                LE.index=max(-179,LE.index-1)
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_q:
                LE.index=max(-179,LE.index-9)
            if event.key==pygame.K_e:
                LE.index=min(179,LE.index+9)
    LE.update()
    pygame.display.update()
    clock.tick(60)
