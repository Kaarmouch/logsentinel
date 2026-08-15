# Journal de bord

## 2026-08-14 — Étape 1 : environnement

### Réalisé

**Hôte (PC fixe, Ubuntu 22.04, i5-3330, 8 Go)**
- Activation de VT-x dans le BIOS (`grep -c vmx` passé de 0 à 8)
- Migration de VirtualBox 6.1.50 vers 7.0.26 (dépôt Oracle),
  modules noyau recompilés via `vboxconfig`

**VM `logsentinel` (Ubuntu Server 24.04)**
- 3 Go RAM, 2 vCPU, disque VDI dynamique 40 Go
- Réseau en pont avec adaptateur virtio, partitionnement sans LVM
- OpenSSH, accès par clé depuis l'hôte
- Swap : `/swap.img` de l'installateur conservé (doublon retiré),
  `vm.swappiness` fixée à 10

**Docker**
- Docker CE 29.7.2 depuis le dépôt officiel (+ containerd, buildx,
  plugin compose v2)
- Utilisateur `arth` dans le groupe `docker`, service activé au boot
- `overlayfs` + cgroups v2 confirmés

**Services**
- `docker-compose.yml` : Ollama + ChromaDB, ports bindés sur
  `127.0.0.1`, volumes nommés, `restart: unless-stopped`
- Modèle qwen2.5:1.5b (986 Mo) testé, puis 0.5b pour alléger
- Persistance vérifiée : `down` puis `up`, modèle conservé
- Isolation réseau confirmée : ports inaccessibles hors tunnel SSH

**Snapshots** : `base-ok` (système propre), `docker-ok` (stack testée)

### Obstacles rencontrés

- **VirtualBox 6.1.50 incompatible avec le noyau 6.8** : Guru Meditation
  `VERR_VMM_SET_JMP_ABORTED_RESUME` au démarrage de tout VCPU.
  Diagnostiqué via `VBox.log`, résolu par migration en 7.0.26.
  Voir [ADR-001](decisions/001-virtualbox-7-noyau-6.8.md).
- **Swap créé en double** : l'installateur Ubuntu Server génère déjà un
  `/swap.img`. Fichier ajouté retiré, une seule zone conservée.
- **`deploy.resources.limits` sans effet** : syntaxe réservée à Swarm.
  Remplacée par `cpus` et `mem_limit` au niveau du service.
- **URL de remote Git mal formée** : mélange des syntaxes SSH et HTTPS
  (`git@github.com:https://...`). Corrigé avec `git remote set-url`.

### Mesures

| Élément | Valeur |
|---|---|
| RAM du conteneur pendant inférence (1.5b) | ~1 Go |
| Pic CPU sans limite | 350 % |
| RAM disponible au repos | 2,5 Go |

### Prochaine étape

Étape 2 — génération de logs : trafic HTTP normal via nginx, attaques
simulées (bruteforce SSH avec hydra, scan de ports avec nmap, requêtes
web malveillantes), capture d'un jeu de données daté.
