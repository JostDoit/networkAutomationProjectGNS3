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
