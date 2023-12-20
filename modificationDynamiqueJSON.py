import json

def loadJSON():
    with open("./confReseau.json", "w") as f:
        data = json.load(f)
        return data

reseau = loadJSON()
