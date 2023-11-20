# assistants-api

## Introduction

Ce répo a pour but de tester le fonctionnement de l'API de OpenAI pour créer des assistants. Qui utiliserai code_interpreter et des json de données de l'unil pour répondre à des questions sur les statistiques de l'unil

## Préréquis

- Python 3.8
- environnement virtuel python
- pip
- git
- un compte openai
- un fichier .env avec
  - OPENAI_API_KEY
  - SYSTEM_MESSAGE

## Installation

1. Cloner le répo
2. Créer un environnement virtuel python
   1. faire `python3 -m venv venv` pour créer l'environnement virtuel
   2. activer l'environnement virtuel avec `source venv/bin/activate`
3. Installer les dépendances avec `pip install -r requirements.txt`

## Utilisation

1. Activer l'environnement virtuel avec `source venv/bin/activate`
2. Pour créer les fichiers json nécessaires pour l'API, il faut lancer le script `python3 create_json.py`

## Données

Les données utilisées pour l'API sont des données de base sous la forme de csv. Elles sont dans le dossier `data/csv`. Le script `create_json.py` va créer des fichiers json à partir de ces données. Ces fichiers json sont dans le dossier `data/json`.

Données sous la forme :

```csv
annee; femmes; hommes; etranger; CH; total
2011; 1519; 1085; 556; 2048; 2604
2012; 1555; 1170; 626; 2099; 2725
2013; 1645; 1209; 692; 2162; 2854
2014; 1699; 1270; 734; 2235; 2969
2015; 1735; 1288; 750; 2273; 3023
2016; 1911; 1309; 792; 2428; 3220
2017; 1993; 1375; 858; 2510; 3368
2018; 2112; 1369; 869; 2612; 3481
2019; 2250; 1438; 905; 2783; 3688
2020; 2477; 1506; 979; 3004; 3983
2021; 2578; 1530; 1039; 3069; 4108
```

Devient :

```json
{
    "contexte": "Ce document retrace les statistiques du nombres d'étudiant(nationalité, sexe, nationalité) inscrit au semestre d'automne en FBM depuis 2012 a l'université de Lausanne.",
    "2011": {
        "femmes": 1519,
        "hommes": 1085,
        "etranger": 556,
        "CH": 2048,
        "total": 2604
    },
    "2012": {
        "femmes": 1555,
        "hommes": 1170,
        "etranger": 626,
        "CH": 2099,
        "total": 2725
    },
    "2013": {
        "femmes": 1645,
        "hommes": 1209,
        "etranger": 692,
        "CH": 2162,
        "total": 2854
    },
    "2014": {
        "femmes": 1699,
        "hommes": 1270,
        "etranger": 734,
        "CH": 2235,
        "total": 2969
    },
    "2015": {
        "femmes": 1735,
        "hommes": 1288,
        "etranger": 750,
        "CH": 2273,
        "total": 3023
    },
    "2016": {
        "femmes": 1911,
        "hommes": 1309,
        "etranger": 792,
        "CH": 2428,
        "total": 3220
    },
    "2017": {
        "femmes": 1993,
        "hommes": 1375,
        "etranger": 858,
        "CH": 2510,
        "total": 3368
    },
    "2018": {
        "femmes": 2112,
        "hommes": 1369,
        "etranger": 869,
        "CH": 2612,
        "total": 3481
    },
    "2019": {
        "femmes": 2250,
        "hommes": 1438,
        "etranger": 905,
        "CH": 2783,
        "total": 3688
    },
    "2020": {
        "femmes": 2477,
        "hommes": 1506,
        "etranger": 979,
        "CH": 3004,
        "total": 3983
    },
    "2021": {
        "femmes": 2578,
        "hommes": 1530,
        "etranger": 1039,
        "CH": 3069,
        "total": 4108
    }
}
```

## Test depuis le playground

Tout d'abord je vais tester le fonctionnement des assistants api depuis le playground sans y deployer depuis l'api pour voir si les résultats sont autant satisfaisant que depuis data analysis.

![playground](./images/playground.png)

A noté que l'instruction est :

`Tu est un assistant data scientist et tu dois répondre au différentes questions en te basant sur les chiffres contenu dans les json que tu auras à ta disposition, ils sont composée de données concernant les Etudiant·e·s inscrit·e·sa au semestre d’automne par faculté selon le sexe et la nationalité a l'université de lausanne (UNIL)`

### Test 1

![test1](./images/test1.png)

La question étais : **Combien il y a t'il d'étudiant en FTSR en 2020 ?**

Il a bien répondu a la question mais je pense que nous pourrions améliorer la rapidité en formtant mieux les données.

### Test 2

![test2](./images/test2.png)

La question étais : **Combien il y a t'il d'étudiant en HEC en 2020 ?**

De ce que je vois chat-gpt s'attend a un autre type de schéma dans le json mais surtour il ne comprend pas quel fichier correspond a quel faculté. Il faudrait donc lui donner plus d'information sur les données dans le json.

Je vais essayer de reformater les données pour voir si cela change quelque chose. Je vais donc créer un nouveau json avec les données de toutes les facultés, sous la forme :

```json
{
	"contexte": "Ce document retrace les statistiques du nombres d'étudiant(nationalité, sexe, nationalité) inscrit au semestre d'automne depuis 2012 a l'université de Lausanne.",
	"FTSR": {
		"2011": {
			"femmes": 1519,
			"hommes": 1085,
			"etranger": 556,
			"CH": 2048,
			"total": 2604
		},
		"2012": {
			"femmes": 1555,
			"hommes": 1170,
			"etranger": 626,
			"CH": 2099,
			"total": 2725
		},
		...
	},
	"HEC": {
		"2011": {
			"femmes": 1519,
			"hommes": 1085,
			"etranger": 556,
			"CH": 2048,
			"total": 2604
		},
		"2012": {
			"femmes": 1555,
			"hommes": 1170,
			"etranger": 626,
			"CH": 2099,
			"total": 2725
		},
		...
	},
	...
}
```
