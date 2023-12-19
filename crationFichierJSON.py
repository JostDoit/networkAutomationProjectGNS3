import json

class Graph :
    def __init__(self):
        self.routeurs = []
        self.prochainNetwork = 1
    
    def addRouteur(self, numeroRouteur):
        new_routeur = Routeur(numeroRouteur)
        self.routeurs.append(new_routeur)

    def removeRouteur(self, numeroRouteur):
        for i in range(len(self.routeurs)):
            if self.routeurs[i].numeroRouteur == numeroRouteur:
                self.routeurs.pop(i)
    
    def addConnexion(self, numeroRouteur1, numeroRouteur2):
        r1Existe = False
        r2Existe = False
        for routeur in self.routeurs:
            if routeur.numeroRouteur == numeroRouteur1:
                routeur1 = routeur
                r1Existe = True
            elif routeur.numeroRouteur == numeroRouteur2:
                routeur2 = routeur
                r2Existe = True
        if (not r1Existe):
            print(f"Impossible d'ajouter cette arrete, le routeur {numeroRouteur1} n'existe pas !")
        elif (not r2Existe):
            print(f"Impossible d'ajouter cette arrete, le routeur {numeroRouteur2} n'existe pas !")
        else:
            routeur1.addArrete(self.prochainNetwork, 1)
            routeur2.addArrete(self.prochainNetwork, 2)
            self.prochainNetwork += 1

    def save(self):
        pass

    def load(self):
        pass
    
class Routeur :
    def __init__(self, numeroRouteur):
        self.numeroRouteur = numeroRouteur
        self.nbInterfacesUtilisees = 0
        self.nbMaxInterfaces = 4
        self.interfaces = []

    def addArrete(self, addresseReseauDeConnexion, nbInterfacesSurLeReseau):
        if self.nbInterfacesUtilisees < self.nbMaxInterfaces:
            self.nbInterfacesUtilisees += 1
            new_interface = Interface(len(self.interfaces), addresseReseauDeConnexion, nbInterfacesSurLeReseau)
            self.interfaces.append(new_interface)
        else:
            print("Impossible d'ajouter une interface, ce routeur n'en a plus de disponible !\n")

class Interface :
    def __init__(self, ID, addresseReseauDeConnexion, nbInterfacesSurLeReseau):
        self.ID = ID
        self.addresseReseau = addresseReseauDeConnexion        
        self.addresseHote = nbInterfacesSurLeReseau + 1

networkRIP = {}

addressRIPNetwork = "2001:100:1:1:0:X::1/96"

for i in range(1,8):
    addressRIPNetwork = addressRIPNetwork[:15]+str(i)+addressRIPNetwork[16:]
    if i == 1:
        interfaces = {}
        for j in range(1,3):
            addressRIPNetwork = addressRIPNetwork[:18]+str(j)+addressRIPNetwork[19:]
            interfaces[j] = addressRIPNetwork
    elif 1<i<6:
        for j in range(4):
            interfaces = {}
            for k in range(1,4):
                addressRIPNetwork = addressRIPNetwork[:18]+str(k)+addressRIPNetwork[19:]
                interfaces[k] = addressRIPNetwork
    else:
        for j in range(2):
            interfaces = {}
            for k in range(1,5):
                addressRIPNetwork = addressRIPNetwork[:18]+str(k)+addressRIPNetwork[19:]
                interfaces[k] = addressRIPNetwork
    networkRIP["Routeur"+str(i)] = interfaces

   
data = {}
data["ReseauRIP"] = networkRIP

with open("./confReseau.json", "w") as f:
    json.dump(data, f, indent=4)