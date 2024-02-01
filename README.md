# networkAutomationProjectGNS3

> https://www.cisco.com/c/en/us/support/docs/ip/border-gateway-protocol-bgp/26634-bgp-toc.html#toc-hId--463182681

### Définition d'une interface sur internet en utilisant des adresses IPv6 unicast globales : 

2001:0db8:3c4d:0015:1234:5678:9abc:def0 > exemple d'une adresse sur internet attribuée à l'interface d'un hôte
Le préfixe d'un site/AS : en /48 > 2001:0db8:3c4d::/48
Un sous réseau : en /64 > 2001:0db8:3c4d:0015::/64

### Les configurations vues en cours : 

#### Faire des route map pour deny un prefix réseau

ipv6 access-list reseauLAN
  permit ipv6 2001:200:200:201::/64 any          //préfixe réseau bloqué
route-map mytag deny 20
  match ipv6 address reseauLAN
route-map mytag permit 50

router bgp 64512
  address-family ipv6 unicast
    neighbor @voisin route-map mytag in

#### Set local pref

route-map test permit 10
  set local-preference 150                      //plus grd mieux c'est, à appliquer au neighbor

router bgp 64512
  address-family ipv6 unicast
    neighbor @voisin route-map test in

#### Ne pas propager les mises à jour contenant 111 afin de ne pas propager l'AS 111 et ainsi éviter le profit de bande passante

ip as-path access-list 1 permit _111_
route-map map_tag deny 20
  match as-path 1
route-map map_tag permit 50
neighbor @voisin route-map map_tag out

#### AS_PATH Prepending
--> appliqué à un préfixe (un seul préfixe prendra plus de sauts)
access-list 10 permit @prefix
route-map cisco permit 20
  match ipv6 address 10                            //appliquer à un préfixe
  set as-path prepend AS_number AS_number ...      //l'AS PATH prepending --> pour aller à une dst prend plus de sauts
route-map cisco permit 50                           // tjrs mettre un permit any afin dene pas bloquer le reste
neigh @voisin route-map cisco out

--> appliqué à tt le monde
route-map cisco permit 20
  set as-path prepend AS_number AS_number ...      //l'AS PATH prepending --> pour aller à une dst prend plus de sauts
route-map cisco permit 50                           // tjrs mettre un permit any afin dene pas bloquer le reste -> ~~ (pas sur que la commande soit nécessaire car la première est matché dans tous les cas ??)
neigh @voisin route-map cisco out


- mettre des community
> A. un peer est propagé au client, pas un provider ni un peer

> B. en sortie permit et enlever la commu du chemin afin de ne pas le propager --> envoie par au reste du monde la commu

> C. utiliser set communi et mettre en place des règles de filtrage OUT

> D. local pref 1 client 2 peer 3 provider (le client paye pour recevoir du traffic donc normal de lui envoiyer en premier)
- pour partager les network avec BGP soit une route statique sur le router avec un prefix plus grd que le réseau qu'on annonce et normalement tt le monde aura access depuis l'exétérieur aux routeur internes ou utilisation de no syncronization (se renseigner) --> propage le préfixe sans rien de plus EZ (objectif de donner les préfixe globale et rendre tt acessible si pas devoir être accessible sur internet JE NE SAIS PLUS COMMENT IL A DIT) -> exemple d'orange espagne en TD
> "A prefix is synchronized in BGP if there is a matching prefix in the IGP. If a BGP learned prefix is not synchronized, the prefix will not be inserted into the routing table and will not be advertised to external peers...". "Usually, a BGP speaker does not advertise a route to an external neighbor unless that route is local or exists in the IGP. The no synchronization command allows the Cisco IOS software to advertise a network route without waiting for the IGP. "


→ finalement j'ai utilisé une commande qui le fait automatiquement, il faut juste ajouter redistribute connected pour être trkl ->  :

address-family ipv6

  redistribute connected







 address-family ipv6
  redistribute connected
  aggregate-address 2001:100:1:3::/64 summary-only
  
  aggregate-address 2001:100:1:3::/64 summary-only

# Règles de Communautés CISCO

Ce projet met en avant dans deux situations distinctes l'utilisation efficace des politiques de routage BGP et des valeurs de communautés.

## Contexte

### 1. Routes entre Deux AS en Relation PEER-PEER

Dans cette première situation, nous abordons le scénario où deux Autonomous Systems (AS) maintiennent une relation PEER-PEER. Les AS impliqués ont décidé de ne pas échanger les routes de leurs clients et celles apprises de leurs fournisseurs de services respectifs. Pour atteindre cet objectif, chaque AS définit une règle de communauté spécifique qu'il propage à ses routeurs de bordure. Cette communauté est ensuite associée à une route qui bloque l'envoi des routes concernées.

### 2. Contrôle Régional des Routes

La deuxième situation se concentre sur un contexte régional. Dans cet exemple, un client souhaite communiquer uniquement avec un AS voisin de son fournisseur de services, excluant les autres AS. Pour réaliser cela, le client associe ses routes à une communauté spécifique définie par son fournisseur de services. Ce dernier autorise uniquement l'envoi des routes du client à l'AS concerné, c'est-à-dire dans la région spécifiée. Ce type de contrat est souvent établi entre un fournisseur de services et son pair. Il est important de noter que si un client envoie sa route avec une étiquette, le pair intermédiaire avec le fournisseur de services étiquettera également sa route avec la même valeur de communauté.

## Comment Utiliser ce Projet

Pour implémenter ces règles de communauté CISCO dans votre propre infrastructure, suivez ces étapes simples :

1. **Configuration PEER-PEER :** Adaptez les règles de communauté pour répondre à vos besoins spécifiques, en prenant en compte les AS impliqués et les politiques de non-partage de routes clients.

2. **Contrôle Régional des Routes :** Personnalisez les valeurs de communauté associées aux routes pour définir des contrôles régionaux, permettant une communication sélective entre clients et AS voisins.

## Remarque Importante

Assurez-vous de comprendre les implications de chaque règle de communauté avant de les déployer dans votre infrastructure. Certaines règles bloquent le traffic dans certaines directions donc les communanautés sont à utiliser en connaissance de cause.

Nous espérons que ce projet vous sera utile dans la mise en œuvre de politiques de routage BGP efficaces et dans la gestion avancée des communautés CISCO. 
