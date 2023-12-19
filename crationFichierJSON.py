import json

networkRIP = {}
networkOSPF = {}

addressRIPNetwork = "2001:100:1:1:0:0::1/96"
addressOSPFNetwork = "2001:100:1:2:0:0::/96"

for i in range(1,8):
    addressRIPNetwork = addressRIPNetwork[:15]+str(i)+addressRIPNetwork[16:]
    if i == 1:
        interfaces = {}
        for j in range(1,3):
            addressRIPNetwork = addressRIPNetwork[:18]+str(j)+addressRIPNetwork[19:]
            interfaces["GigabitEthernet"+str(j)+"/0"] = addressRIPNetwork
    elif 1<i<6:
        for j in range(4):
            interfaces = {}
            for k in range(1,4):
                addressRIPNetwork = addressRIPNetwork[:18]+str(k)+addressRIPNetwork[19:]
                interfaces["GigabitEthernet"+str(k)+"/0"] = addressRIPNetwork
    else:
        for j in range(2):
            interfaces = {}
            for k in range(1,5):
                addressRIPNetwork = addressRIPNetwork[:18]+str(k)+addressRIPNetwork[19:]
                interfaces["GigabitEthernet"+str(k)+"/0"] = addressRIPNetwork
    networkRIP["Routeur"+str(i)] = interfaces

for i in range(1,8):
    addressRIPNetwork = addressRIPNetwork[:15]+str(i)+addressRIPNetwork[16:]
    if i == 1:
        interfaces = {}
        for j in range(1,3):
            addressRIPNetwork = addressRIPNetwork[:18]+str(j)+addressRIPNetwork[19:]
            interfaces["GigabitEthernet"+str(j)+"/0"] = addressRIPNetwork
    elif 1<i<6:
        for j in range(4):
            interfaces = {}
            for k in range(1,4):
                addressRIPNetwork = addressRIPNetwork[:18]+str(k)+addressRIPNetwork[19:]
                interfaces["GigabitEthernet"+str(k)+"/0"] = addressRIPNetwork
    else:
        for j in range(2):
            interfaces = {}
            for k in range(1,5):
                addressRIPNetwork = addressRIPNetwork[:18]+str(k)+addressRIPNetwork[19:]
                interfaces["GigabitEthernet"+str(k)+"/0"] = addressRIPNetwork
    networkOSPF["Routeur"+str(i)] = interfaces

data = {}
data["ReseauRIP"] = networkRIP
data["ReseauOSPF"] = networkRIP

with open("./confReseau.json", "w") as f:
    json.dump(data, f, indent=4)