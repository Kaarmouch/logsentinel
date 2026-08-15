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

---

## 2026-08-15 — Étape 2 : génération de logs

### Réalisé

**Serveur web cible**
- nginx installé dans la VM (les attaques web ciblent la VM, pas l'hôte
  qui tourne sous Apache)

**Principe : attaquer depuis l'hôte vers la VM**
- Les attaques sont lancées depuis l'hôte (`192.168.1.25`) vers la VM
  (`192.168.1.17`), pour obtenir une IP source externe identifiable
  plutôt que le loopback `::1`.

**Attaques web simulées (script `attack-web.sh`)**
- Scan de fichiers sensibles : `/admin`, `/wp-login.php`, `/.env`,
  `/.git/config`, `/phpmyadmin` → codes 404
- Path traversal `/../../etc/passwd` avec `curl --path-as-is` → code 400
- Injection SQL et XSS avec `curl -G --data-urlencode` → payloads
  correctement encodés dans les logs

**Bruteforce SSH (hydra depuis l'hôte)**
- `hydra -L users.txt -P wordlist.txt -t 4 ssh://192.168.1.17`
- 35 combinaisons testées, 0 réussite (accès par clé) — objectif :
  générer les échecs, pas entrer
- Traces dans journald : rafale de `Failed password` / `Invalid user`
  depuis une même IP en ~25 s

**Trafic normal (ligne de base)**
- Web : requêtes `GET /` répétées → codes 200
- SSH : connexion légitime → `Accepted publickey for arth`

**Jeu de données obtenu** : les quatre quadrants — web normal (200),
web malveillant (404/400), SSH normal (accepted), SSH malveillant
(failed) — avec IP sources identifiables.

### Obstacles rencontrés

- **Pas de `/var/log/auth.log`** : Ubuntu Server 24.04 utilise journald
  seul, sans rsyslog. Les échecs SSH se lisent avec
  `journalctl _COMM=sshd`, pas dans un fichier texte.
- **`curl` renvoyait `000` sur l'injection SQL** : les caractères
  spéciaux (`'`, espace) cassaient l'URL. Résolu avec
  `-G --data-urlencode`, qui encode proprement avant l'envoi.
- **`curl` normalisait le path traversal** : `/../../etc/passwd` arrivait
  comme `/etc/passwd` dans le log. Résolu avec `--path-as-is`.
- **Confusion hôte/VM** : `curl` vers `192.168.1.25` renvoyait Apache
  (l'hôte), pas nginx. L'IP de la VM (`.17`) se lit avec `ip -br addr`
  depuis l'intérieur de la VM.

### Note de conception

fail2ban volontairement **non installé** à ce stade : il bloquerait
hydra et réduirait la matière à analyser. Réservé à l'étape 5-6 comme
démonstration de contre-mesure.

### Prochaine étape

Étape 3 — ingestion : script Python qui lit les deux sources (journald
en JSON pour SSH, fichier texte pour nginx), extrait timestamp / IP
source / type d'événement / sévérité, et normalise dans un format commun.
