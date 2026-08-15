# Journal de bord

## 2026-08-14 — Étape 1 : socle d'infrastructure

### Réalisé

- Activation de VT-x dans le BIOS (i5-3330)
- VM Ubuntu Server 24.04 sous VirtualBox : 3 Go RAM, 2 vCPU, disque
  dynamique 40 Go, réseau en pont, accès SSH par clé
- Docker CE 29.7.2 depuis le dépôt officiel
- Ollama + ChromaDB via Compose, ports restreints à 127.0.0.1,
  volumes nommés pour la persistance
- Modèle qwen2.5:1.5b (986 Mo) testé, puis remplacé par le 0.5b

### Obstacles rencontrés

- **VirtualBox 6.1.50 incompatible avec le noyau 6.8** : Guru Meditation
  `VERR_VMM_SET_JMP_ABORTED_RESUME` au démarrage de tout VCPU.
  Résolu par migration vers 7.0.26 depuis le dépôt Oracle.
  Voir [ADR-001](decisions/001-virtualbox-7-noyau-6.8.md).
- **Swap créé en double** : l'installateur Ubuntu Server génère déjà un
  `/swap.img`. Le fichier ajouté a été retiré, swappiness fixée à 10.
- **`deploy.resources.limits` sans effet** : syntaxe Swarm. Remplacée par
  `cpus` et `mem_limit` au niveau du service.

### Mesures

| Élément | Valeur |
|---|---|
| RAM du conteneur pendant inférence (1.5b) | ~1 Go |
| Pic CPU sans limite | 350 % |
| RAM disponible au repos | 2,5 Go |

### Prochaine étape

Ajout de Promtail, Loki et Grafana. Écriture de la configuration de
parsing pour `auth.log`.
