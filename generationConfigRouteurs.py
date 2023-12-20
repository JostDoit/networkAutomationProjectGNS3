import json, os

def loadJSON():
    f = open("./intentFile.json", "r")
    data = json.load(f)
    f.close()
    return data

intentFile = loadJSON()
outputPath = "./configRouteur"

#Lecture du Intent File
#Routeurs
routers = intentFile["routers"]
nbRouter = len(routers)

#AS
asList = intentFile["as"]
nbAs = len(asList)
asPrefix = {}               #Dictionnaire contenant les couples idAs / Préfixe réseau associé
for i in range(nbAs):
    asInfos = asList[i]
    asPrefix[asInfos["id"]] = asInfos["ip-prefix"]

dicoSousRes = {} #Dictionnaire contenant les index des derniers sous-reseaux utilises pour chaque AS.
for index in asPrefix:
    dicoSousRes[index] = 0

# Initialisation d'une matrice contenant les numeros des sous-reseaux entre chaque routeur
matIdSousReseauxAs = [] 
for i in range(0,nbRouter):
    matIdSousReseauxAs.append([])
    for j in range(nbRouter):
        matIdSousReseauxAs[i].append(0)

# Initialisation d'un matrice contenant les numeros des sous-reseaux entre chaque AS
matAdjAs = [] 
for k in range(0,nbAs):
    matAdjAs.append([])
    for j in range(nbAs):
        matAdjAs[k].append(0)

compteurLienAS = 0



#Constantes
egp = intentFile["constantes"]["egp"]
ripName = intentFile["constantes"]["ripName"]
ospfProcess = str(intentFile["constantes"]["ospfPid"])



#Ecriture de la configuration pour chaque routeur
for router in routers:
    
    #Recuperation des infos du routeur
    id = router["id"]
    As = router["as"]
    neighborsAddressList = []
    isASBR = False
    for i in asList:
        if i["id"] == As:
            igp = i["igp"]
    
    #Creation du fichier de configuration du routeur
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)
    res = open(f"{outputPath}/i{id}_startup-config.cfg", "w")

    #Ecriture de l'en-tete
    res.write(f"#{igp} sur R{id} - routeur avec {len(router['adj'])} interfaces utilisees : \n")
    res.write(f"version 15.2\n"
              "service timestamps debug datetime msec\n"
              "service timestamps log datetime msec\n"
              f"hostname R{id}\n"
              "boot-start-marker\n"
              "boot-end-marker\n"
              "no aaa new-model\n"
              "no ip icmp rate-limit unreachable\n"
              "ip cef\n"
              "no ip domain lookup\n"
              "ipv6 unicast-routing\n"
              "ipv6 cef\n"
              "multilink bundle-name authenticated\n"
              "ip tcp synwait-time 5\n")
    res.write("!\n!\n!\n!\n!\n")

    #Interface de Loopback
    res.write("interface Loopback0\n"
              " no ip address\n"
              f" ipv6 address {id}::{id}/128\n"
              " ipv6 enable\n")
    if(igp == "rip"):
        res.write(f" ipv6 rip {ripName} enable\n")
    elif(igp == "ospf"):
        res.write(f" ipv6 ospf {ospfProcess} area 0\n")
    res.write("!\n")

    #Interfaces
    for adj in router["adj"]:
        neighbourID = adj["neighbor"]
        for router in routers:
            if router["id"]==neighbourID:           
                neighbourAs = router["as"]
        
        for link in adj["links"]:
            #Generation de l'addresse IP
            #Cas IGP
            #Partie Prefixe
            if link["protocol-type"] == "igp":
                ip = asPrefix[As]
                #Partie Sufixe
                # Si sous reseau pas encore initialise i.e premiere interface
                if matIdSousReseauxAs[id-1][neighbourID-1] == 0 and matIdSousReseauxAs[neighbourID-1][id-1]==0:
                    dicoSousRes[As] += 1
                    matIdSousReseauxAs[id-1][neighbourID-1], matIdSousReseauxAs[neighbourID-1][id-1] = dicoSousRes[As], dicoSousRes[As]
                    ip += ":0:" + str(matIdSousReseauxAs[id-1][neighbourID-1]) + ":0:1"
                
                else: # sous reseau deja cree
                    ip += ":0:" + str(matIdSousReseauxAs[id-1][neighbourID-1]) + ":0:2"

            #Cas EGP
            else:
                isASBR = True
                ip = "2001:100:1:"

                if matAdjAs[As - 64513][neighbourAs - 64513] == 0:
                    compteurLienAS += 1
                    matAdjAs[As - 64513][neighbourAs - 64513] = compteurLienAS
                    neighborAddress = ip + str(compteurLienAS) + "::2"
                    neighborsAddressList.append([neighborAddress,neighbourAs])
                    ip += str(compteurLienAS) + "::1"                   

                else: # sous reseau deja cree
                    neighborAddress = ip + str(matAdjAs[As - 64513][neighbourAs - 64513]) + "::1"
                    neighborsAddressList.append([neighborAddress,neighbourAs])
                    ip += str(matAdjAs[As - 64513][neighbourAs - 64513]) + "::2"
            
            #Interface            
            res.write(f"interface {link['interface']}\n"
                      " no ip address\n"
                      " negotiation auto\n"
                      f" ipv6 address {ip}/96\n"
                      " ipv6 enable\n")

            if link["protocol-type"] == "igp" :
                if igp == "rip":
                    res.write(f" ipv6 rip {ripName} enable\n")
                if igp == "ospf":
                    res.write(f" ipv6 ospf {ospfProcess} area 0\n")                               
            res.write("!\n")
    #EGP
    res.write(f"router bgp {As}\n"
              f" bgp router-id {id}.{id}.{id}.{id}\n"
              " bgp log-neighbor-changes\n"
              " no bgp default ipv4-unicast\n")

    for router in routers:
        if router["as"] == As:
            routerID = router["id"]
            if routerID != id:                
                res.write(f" neighbor {routerID}::{routerID} remote-as {As}\n")
                res.write(f" neighbor {routerID}::{routerID} update-source Loopback0\n")
    if isASBR :
        for egpNeighborsAddress in neighborsAddressList:
            ipNeighb = egpNeighborsAddress[0]
            asNeighb = egpNeighborsAddress[1]
            res.write(f" neighbor {ipNeighb} remote-as {asNeighb}\n")
    
    res.write(" !\n"
              " address-family ipv4\n"
              " exit-address-family\n"
              " !\n"
              " address-family ipv6\n")
    
    for router in routers:
        if router["as"] == As:
            routerID = router["id"]
            if routerID != id:
                res.write(f"  neighbor {routerID}::{routerID} activate\n")
    
    if isASBR:
        for egpNeighborsAddress in neighborsAddressList:
            res.write(f"  neighbor {egpNeighborsAddress[0]} activate\n")
    
    res.write(" exit-address-family\n!\n")

    res.write("ip forward-protocol nd\n"
              "no ip http server\n"
              "no ip http secure-server\n"
              "!\n")

    # IGP
    if(igp == "rip"):
        res.write(f"ipv6 router rip {ripName}\n"
                  " redistribute connected\n")
                  
    if(igp == "ospf"):
        res.write(f"ipv6 router ospf {ospfProcess}\n"
                  " router-id {id}.{id}.{id}.{id}\n")        
    res.write("!\n")

    res.write("control-plane\n"
              "line con 0\n"
              " exec-timeout 0 0\n"
              " privilege level 15\n"
              " logging synchronous\n"
              " stopbits 1\n"
              "line aux 0\n"
              " exec-timeout 0 0\n"
              " privilege level 15\n"
              " logging synchronous\n"
              " stopbits 1\n"
              "line vty 0 4\n"
              " login\n"
              "!\n"
              "end")
    
    res.close()

    print(f"Router {id} generated") 