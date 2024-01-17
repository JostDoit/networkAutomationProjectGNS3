import json, os

f = open("./intentFileTestNetwork.json", "r")
intentFile = json.load(f)
f.close()

outputPath = "./configRouteurTestNetwork"

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
for id in asPrefix:
    dicoSousRes[id] = 0

# Initialisation d'une matrice contenant les numeros des sous-reseaux entre chaque routeur
matIdSousReseauxAs = [] 
for i in range(0,nbRouter):
    matIdSousReseauxAs.append([])
    for j in range(nbRouter):
        matIdSousReseauxAs[i].append(0)

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
    interfacesEGP = []
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
    res.write("version 15.2\n"
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
            else:
                isASBR = True                
                ip = "2001:101:"
                
            #Partie Sufixe
            # Si sous reseau pas encore initialise i.e premiere interface
            if matIdSousReseauxAs[id-1][neighbourID-1] == 0 and matIdSousReseauxAs[neighbourID-1][id-1]==0:                
                if link["protocol-type"] == "igp":
                    dicoSousRes[As] += 1
                    matIdSousReseauxAs[id-1][neighbourID-1], matIdSousReseauxAs[neighbourID-1][id-1] = dicoSousRes[As], dicoSousRes[As]           
                    ip += str(dicoSousRes[As])
                else:
                    compteurLienAS += 1
                    matIdSousReseauxAs[id-1][neighbourID-1], matIdSousReseauxAs[neighbourID-1][id-1] = compteurLienAS, compteurLienAS
                    neighborAddress = ip + str(compteurLienAS) + "::2"
                    neighborsAddressList.append([neighborAddress,neighbourAs])
                    ip += str(compteurLienAS) + "::1"            
            else: # sous reseau deja cree
                if link["protocol-type"] == "igp":
                    ip += str(matIdSousReseauxAs[id-1][neighbourID-1])
                else:
                    neighborAddress = ip + str(matIdSousReseauxAs[id-1][neighbourID-1]) + "::1"
                    neighborsAddressList.append([neighborAddress,neighbourAs])
                    ip += str(matIdSousReseauxAs[id-1][neighbourID-1]) + "::2"
            
            #Interface            
            res.write(f"interface {link['interface']}\n"
                      " no ip address\n"
                      " negotiation auto\n")
            if link["protocol-type"] == "egp":
                res.write(f"ipv6 address {ip}/96\n")
            else:
                res.write(f" ipv6 address {ip}/64 eui-64\n")
            
            res.write(" ipv6 enable\n")

            if link["protocol-type"] == "igp" and igp == "rip":
                res.write(f" ipv6 rip {ripName} enable\n")
            elif igp == "ospf":
                res.write(f" ipv6 ospf {ospfProcess} area 0\n")
                if link["protocol-type"] == "egp":
                    interfacesEGP.append(link['interface'])
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
    
    #A décocher pour tout annoncer pour les tests
    if isASBR:
        res.write("  redistribute connected\n")
        if(igp == "rip"):
            res.write(f"  redistribute rip {ripName}\n")
        if(igp == "ospf"):
            res.write(f"  redistribute ospf {ospfProcess}\n")
    
    #res.write(f"  aggregate-address {asPrefix[As]}:/48 summary-only\n")

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
                  f" router-id {id}.{id}.{id}.{id}\n")
        if isASBR:           
            for interfaceName in interfacesEGP:
                res.write(f" passive-interface {interfaceName}\n")
        if isASBR: #A decocher pour tout annoncer
            res.write(" redistribute connected\n")     
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

    print(f"Configuration du routeur {id} generee !") 