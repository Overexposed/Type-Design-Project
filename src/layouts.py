from PIL import Image, ImageChops
import numpy as np

IMAGES_WIDTH = 1000
IMAGES_HEIGTH = 1000
IMAGES_SIZE = (IMAGES_WIDTH, IMAGES_HEIGTH)

class BoundingBox():

    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy

    def __str__(self):
        return str((self.x, self.y, self.dx, self.dy))

    def getSize(self):
        return (self.dx,self.dy)

    def getBoxOutline(self):
        return (self.x, self.y, self.x + self.dx, self.y + self.dy)

layouts = {
    0: [(0,0,1,1)],
    1: [(0,0,0.5,1), (0.5,0,0.5,1)],
    2: [(0,0,1,0.5), (0,0.5,1,0.5)],
    3: [(0,0,1,1), (0.5,0.5,0.5,0.5)],
    4: [(0,0,1,1), (0.5,0,0.5,0.5)],
    5: [(0,0,1,1), (0,0.5,0.5,0.5)],
    6: [(0,0,1,1), (0.25,0.5,0.5,0.5)],
    7: [(0,0,1,1), (0.25,0,0.5,0.5)],
    8: [(0,0,1,1), (0.5,0.25,0.5,0.5)],
    9: [(0,0,1,1), (0.25,0.25,0.5,0.5)],
    10: [(0,0,0.33,1), (0.33,0,0.34,1), (0.67,0,0.33,1)],
    11: [(0,0,1,0.33), (0,0.33,1,0.34), (0,0.67,1,0.33)],
    12: [(0,0,1,0.5), (0,0.5,0.5,0.5), (0.5,0.5,0.5,0.5)],
    13: [(0,0,0.5,0.5), (0.5,0,0.5,0.5), (0,0.5,1,0.5)],
    14: [(0,0,1,1), (0,0.25,0.5,0.5), (0.5,0.25,0.5,0.5)],
    15: [(0,0,0.5,0.5), (0.5,0,0.5,0.5), (0,0.5,0.5,0.5), (0.5,0.5,0.5,0.5)],
    16: [(0,0,1,0.33), (0,0.33,0.5,0.34), (0.5,0.33,0.5,0.34), (0,0.67,1,0.33)],
    17: [(0,0,1,0.25), (0,0.25,1,0.25), (0,0.5,0.33,0.5), (0.33,0.5,0.34,0.5), (0.67,0.5,0.33,0.5)],
    18: [(0,0,0.5,0.33), (0.5,0,0.5,0.33), (0,0.33,1,0.34), (0,0.67,0.5,0.33), (0.5,0.67,0.5,0.33)],
    19: [(0,0,1,0.33), (0,0.33,0.33,0.34), (0.33,0.33,0.34,0.34), (0.67,0.33,0.33,0.34), (0,0.67,1,0.33)],
    20: [(0,0,1,1), (0.33,0,0.34,1)],
    21: [(0,0,0.5,0.5), (0,0.5,0.5,0.5), (0.5,0,0.5,1)],
    22: [(0,0,0.5,1), (0.5,0,0.5,0.5), (0.5,0.5,0.5,0.5)],
    23: [(0,0,1,1), (0.33,0.33,0.67,0.34), (0.33,0.67,0.67,0.33)],
    24: [(0,0,1,1), (0.33,0.33,0.34,0.67), (0.67,0.33,0.33,0.67)],
    25: [(0,0,1,1), (0,0,0.5,0.5), (0.5,0,0.5,0.5)],
    26: [(0,0,1,0.25), (0,0.25,1,0.25), (0,0.5,1,0.25), (0,0.75,1,0.25)],
    27: [(0,0,1,1), (0,0,0.5,0.5), (0.5,0,0.5,0.5), (0,0.5,0.5,0.5), (0.5,0.5,0.5,0.5)],
}

def findBoundingBox(image):
    img = np.invert(np.asarray(image))
    rows = np.any(img, axis=1)
    cols = np.any(img, axis=0)
    ymin, ymax = np.where(rows)[0][[0, -1]]
    xmin, xmax = np.where(cols)[0][[0, -1]]
    return BoundingBox(xmin, ymin, xmax-xmin, ymax-ymin)

def findCutout(targetB, charB):
    if targetB.dx == 1000:
        x = 0
        dx = 1000
    else:
        x = charB.x
        dx = charB.dx
        while dx < targetB.dx - 1 and x > 0 and x < 999:
            x = x-1
            dx = dx+2
        if dx == targetB.dx - 1 and x > 0:
            x = x-1
            dx = dx+1
        elif dx == targetB.dx - 1:
            dx = dx+1
        if x == 0 and dx < targetB.dx:
            dx = targetB.dx
        elif x == 999 and dx < targetB.dx:
            dx = targetB.dx
            x = 999 - dx
    if targetB.dy == 1000:
        y = 0
        dy = 1000
    else:
        y = charB.y
        dy = charB.dy
        while dy < targetB.dy - 1 and y > 0 and y < 999:
            y = y-1
            dy = dy+2
        if dy == targetB.dy - 1 and y > 0:
            y = y-1
            dy = dy+1
        elif dy == targetB.dy -1:
            dy = dy+1
        if y == 0 and dy < targetB.dy:
            dy = targetB.dy
        elif y == 999 and dy < targetB.dy:
            dy = targetB.dy
            y = 999 - dy
    return (x,y,x+dx,y+dy) 

def needsResizing(targetB, charB):
    return (targetB.dx < charB.dx or targetB.dy < charB.dy)

def applyLayout(layout, images):
    comps = layouts.get(layout, layouts.get(0))
    if (len(images) != len(comps)):
        print("incorrect lengths")
        # Throw error
    else:
        outImage = Image.new("1", IMAGES_SIZE, 1)
        for i in range(len(images)):
            comp = comps[i]
            image = images[i]
            targetBox = BoundingBox(int(comp[0]*IMAGES_WIDTH), int(comp[1]*IMAGES_HEIGTH), int(comp[2]*IMAGES_WIDTH), int(comp[3]*IMAGES_HEIGTH))
            charBox = findBoundingBox(image)
            if needsResizing(targetBox, charBox):
                tempImage = image.resize(targetBox.getSize())
            else:
                cutout = findCutout(targetBox, charBox)
                tempImage = image.crop(cutout)
                #tempImage = image.resize(targetBox.getSize())
            outImage.paste(tempImage, targetBox.getBoxOutline(), ImageChops.invert(tempImage))
    return outImage

def applyPreciseLayout(boxes, images):
    if (len(images) != len(boxes)):
        print("incorrect lengths")
        # Throw error
    else:
        outImage = Image.new("1", IMAGES_SIZE, 1)
        for i in range(len(images)):
            image = images[i]
            targetBox = boxes[i]
            charBox = findBoundingBox(image)
            char = image.crop(charBox.getBoxOutline()).resize(targetBox.getSize())
            outImage.paste(char, targetBox.getBoxOutline(), ImageChops.invert(char))
    return outImage