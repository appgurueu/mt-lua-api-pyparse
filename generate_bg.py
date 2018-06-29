import PIL
import random
from PIL import Image

size=(60,40)
dirtlevel=3*16
gravellevel=5*16

dirt=Image.open("default_dirt.png")
gravel=Image.open("default_gravel.png")
grass=Image.open("default_grass_side.png")
stone=Image.open("default_stone.png")
orechance=0.1

minerals=["gold","iron","copper","coal","diamond","mese","tin"]
minimgs=[]

for mineral in minerals:
    minimgs.append(Image.open("default_mineral_"+mineral+".png").convert("RGBA"))

result=Image.new("RGBA",(size[0]*16,size[1]*16))

for x in range(0,size[0]*16,16):
    for y in range(0,size[1]*16,16):
        if (y <= dirtlevel):
            result.paste(dirt,(x,y))
        elif (y <= gravellevel):
            result.paste(gravel,(x,y))
        else:
            result.paste(stone,(x,y))
            r=random.random()
            if (r < orechance):
                i=int(round(random.random()*(len(minimgs)-1),0))
                result.paste(minimgs[i],(x,y),minimgs[i])
        if (y == 0):
            result.paste(grass,(x,y),grass)
result.save("background.png")
