# networkAutomationProjectGNS3

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

### Ne pas propager les mises à jour contenant 111 afin de ne pas propager l'AS 111 et ainsi éviter le profit de bande passante

ip as-path access-list 1 permit _111_
route-map map_tag deny 20
  match as-path 1
route-map map_tag permit 50
neighbor @voisin route-map map_tag out

### AS_PATH Prepending
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
- pour partager les network avec BGP soit une route statique sur le router avec un prefix plus grd que le réseau qu'on annonce et normalement tt le monde aura access depuis l'exétérieur aux routeur internes ou utilisation de no syncronization (se renseigner) --> propage le préfixe sans rien de plus EZ (objectif de donner les préfixe globale et rendre tt acessible si pas devoir être accessible sur internet JE NE SAIS PLUS COMMENT IL A DIT)
  
