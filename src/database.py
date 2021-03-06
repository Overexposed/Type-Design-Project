import sys
import csv
from layouts import layouts, BoundingBox
from findPosition_v2 import findBoxes, findBestBox
from PIL import Image

UNICODE_DIC = {}
CHAR_DIC = {}
READABLE_CHAR_DIC = {}
IMAGES_DIC = {}
CHARACTER_DATABASE_PATH = ""
OUTPUT_DATABASE_PATH = ""
IMAGES_PATH = ""

class CharDef:
    def __init__(self, lid, compChars, preciseDef):
        self.lid = lid
        self.compChars = compChars
        self.preciseDef = preciseDef

class IdCharDef:
    def __init__(self, lid, compIds, preciseDef=False, boxes=None):
        self.lid = lid
        self.compIds = compIds
        self.preciseDef = preciseDef
        self.boxes = boxes

def getCompIds(compChars):
    global UNICODE_DIC
    compIds = []
    for char in compChars:
        Id = UNICODE_DIC.get(char)
        compIds.append(Id)
    return compIds

def createCharDic():
    global CHAR_DIC
    global UNICODE_DIC
    with open(CHARACTER_DATABASE_PATH, encoding="utf16") as csvfile:
        fileReader = csv.reader(csvfile, delimiter='\t')
        count = 0
        for row in fileReader:
            if count == 0:
                count += 1
                continue
            try:
                lid = int(row[3][3:])
            except Exception as error:
                break
            print(count)
            count += 1
            char = row[0]
            Id = row[1]
            preciseDef = row[2]
            compsLenght = len(layouts.get(lid))
            compChars = []
            for i in range(compsLenght):
                compChars.append(row[i + 4])
            charDef = CharDef(lid, compChars, preciseDef != "FALSE")
            UNICODE_DIC.update({char: Id})
            CHAR_DIC.update({Id: charDef})

def loadImage(Id):
    global IMAGES_DIC
    if Id in IMAGES_DIC:
        im = IMAGES_DIC.get(Id)
    else:
        im = Image.open(IMAGES_PATH + Id + ".png")
        IMAGES_DIC.update({Id: im})
    return im

def computeBoxes(Id, compIds):
    im = loadImage(Id)
    baseBoxes = findBoxes(im)
    boxes = []
    for compId in compIds:
        compIm = loadImage(compId)
        box = findBestBox(im, baseBoxes, compIm)
        boxes.append(box)
    return boxes

def createReadableCharDic():
    global READABLE_CHAR_DIC
    for k,v in CHAR_DIC.items():
        lid = v.lid
        compIds = getCompIds(v.compChars)
        none = False
        for Id in compIds:
            if Id == None:
                none = True
                break
        if none:
            lid = 0
            compIds = [k]
            charDef = IdCharDef(lid, compIds)
        elif v.preciseDef:
            boxes = computeBoxes(k,compIds)
            charDef = IdCharDef(lid, compIds, True, boxes)
        else:
            charDef = IdCharDef(lid, compIds)
        READABLE_CHAR_DIC.update({k: charDef})

def saveToCsv():
    with open(OUTPUT_DATABASE_PATH + "database.csv", "w", newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for k,v in READABLE_CHAR_DIC.items():
            toWrite = [k, v.lid]
            for Id in v.compIds:
                toWrite.append(Id)
            if v.preciseDef:
                toWrite.append(1)
                for box in v.boxes:
                    toWrite.append(box.x)
                    toWrite.append(box.y)
                    toWrite.append(box.dx)
                    toWrite.append(box.dy)
            else:
                toWrite.append(0)
            writer.writerow(toWrite)

def createDatabaseCSV():
    createCharDic()
    createReadableCharDic()
    saveToCsv()


    

def main():
    if len(sys.argv) != 4:
        print("Wrong number of arguments, please provide:")
        print("1) the filename (with path) of the character database")
        print("2) the path for the newly created character database")
        print("3) the path with all the character images")
    else:
        global CHARACTER_DATABASE_PATH
        global OUTPUT_DATABASE_PATH
        global IMAGES_PATH
        CHARACTER_DATABASE_PATH = sys.argv[1]
        OUTPUT_DATABASE_PATH = sys.argv[2]
        IMAGES_PATH = sys.argv[3]
        createDatabaseCSV()

if __name__ == "__main__":
    main()