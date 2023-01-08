import json
import os

class Stockpile():
    def __init__(self, name, filename = "stockpileddefault.txt", NewStockpile = True) -> None:
        if filename == "stockpile.txt":
            filename = "stockpileddefault.txt"
        self.messageID = None
        self.name = name
        self.filename = filename
        self.hexes = dict()
        if NewStockpile:
            f = open("stockpiles/stockpile.txt", "a+")
            f.write(filename + '\n')
            f.close()
    
    def updateMessageID (self, newID):
        self.messageID = newID
    
    def getMessageID(self):
        return self.messageID
    
    def addHex(self, hex):
        self.hexes[hex] = dict()
    
    def removeHex(self, hex):
        try:
            del self.hexes[hex]
        except:
            #probably doesnt exist, do nothing
            return
    
    def addDepot(self, hex, depot):
        self.hexes[hex][depot] = dict()
    
    def removeDepot(self, hex, depot):
        try:
            del self.hexes[hex][depot]
        except:
            #probably doesnt exist, do nothing
            return
        if len(self.hexes[hex].keys()) <= 0: #the hex has no active depots
            self.removeHex(hex)


    def addStockpile(self, hex, depot, name, code):
        #we need to make sure everything exists
        if hex not in self.hexes:
            self.addHex(hex)
        if depot not in self.hexes[hex]:
            self.addDepot(hex, depot)
        
        self.hexes[hex][depot][name] = code

    def removeStockpile(self, hex, depot, name):
        try:
            del self.hexes[hex][depot][name]
        except:
            #stockpile name doesnt exist, return
            return
        if len(self.hexes[hex][depot].keys()) <= 0: #the depot does not have any stockpiles, remove it
            self.removeDepot(hex, depot)
    
    def delete(self):
        f = open("stockpiles/stockpile.txt", "w+")
        lines = f.readlines()
        for line in lines:
            line.replace(self.filename+'\n', '')
        f.writelines(lines)
        f.close()
        os.remove(self.filename)
    
    def loadJson(self, filename = None):
        if filename == None:
            filename = self.filename
            f = open(filename, "r")
    
        filelines = f.readlines()
        self.messageID = filelines[0].strip('\n')
        self.name = filelines[1].strip('\n')
        jsontext = filelines[2].strip('\n') #"\n".join(filelines[2:])

        self.hexes = json.loads(jsontext)
        f.close()

    def saveJson(self, filename = None):
        if filename == None:
            filename = self.filename
        filetext = f"{self.messageID}\n{self.name}\n{json.dumps(self.hexes)}"
        f = open(filename, "w")
        f.write(filetext)
        f.close()
        

    def discordText(self):
        message = f"__**{self.name}:**__\n"
        for hex in self.hexes:
            message += f"**{hex}:**\n"
            for depot in self.hexes[hex]:
                message += f"__{depot}:__\n"
                for name in self.hexes[hex][depot]:
                    message += f"\t {name}: {self.hexes[hex][depot][name]}\n"
        print(f"returning:\n {message}")
        return message

    def gabyDiscordText(self):
        message = "```yaml\n"
        divider = '—'*30 +'\n'
        message += divider
        for hex in self.hexes:
            message += f"Region: {hex}\n"
            for depot in self.hexes[hex]:
                message += f"\tDepot: {depot}\n"
                for name in self.hexes[hex][depot]:
                    message += f"\t\t{name}: {self.hexes[hex][depot][name]}\n"
            message += divider
        message += "```"
        #print(f"returning:\n {message}")
        return message
