# Stack de Monitoring - Grafana + Loki + Promtail

## 📊 Vue d'ensemble

Cette stack de monitoring permet de centraliser et visualiser tous les logs de vos conteneurs Docker.

### Composants

- **Grafana** (port 3000) : Interface de visualisation et dashboards
- **Loki** : Agrégation et stockage des logs
- **Promtail** : Agent de collecte des logs des conteneurs Docker

## 🚀 Accès

Une fois les conteneurs démarrés :

- **Grafana** : http://localhost:3000
  - Username : `admin`
  - Password : `admin` (vous serez invité à le changer)

## 📝 Utilisation

### Connexion à Grafana

1. Accédez à http://localhost:3000
2. Connectez-vous avec `admin` / `admin`
3. Le datasource Loki est automatiquement configuré

### Visualiser les logs

1. Cliquez sur "Explore" (icône boussole) dans le menu latéral
2. Sélectionnez "Loki" comme datasource
3. Utilisez les requêtes LogQL pour filtrer :

**Exemples de requêtes :**

```logql
# Tous les logs du backend
{service="backend"}

# Logs d'erreur du backend
{service="backend"} |= "ERROR"

# Logs du frontend en temps réel
{service="frontend"}

# Logs de la base de données
{service="db"}

# Logs du reverse proxy
{service="reverseproxy"}

# Filtrer par environnement
{environment="dev"}

# Combinaison
{service="backend", environment="prod"} |= "error" or "exception"
```

### Créer un Dashboard

1. Cliquez sur "Dashboards" → "New Dashboard"
2. Ajoutez un panel
3. Sélectionnez Loki comme datasource
4. Entrez votre requête LogQL
5. Sauvegardez

## 🔧 Configuration

### Rétention des logs

Par défaut : **30 jours** (720 heures)

Pour modifier, éditez `monitoring/loki-config.yml` :

```yaml
limits_config:
  retention_period: 720h  # Modifiez cette valeur
```

### Filtres personnalisés

Les logs sont automatiquement taggés avec :
- `container` : nom du conteneur
- `service` : nom du service compose
- `project` : nom du projet
- `environment` : dev ou prod

## 📁 Structure des fichiers

```
monitoring/
├── loki-config.yml           # Configuration de Loki
├── promtail-config.yml       # Configuration de Promtail
├── grafana-datasources.yml   # Datasources auto-configurés
├── grafana-dashboards.yml    # Configuration des dashboards
└── README.md                 # Ce fichier
```

## � Export des logs

Trois scripts sont disponibles pour exporter les logs en différents formats :

### 1. Export brut (TXT)

```bash
cd monitoring
./export-logs.sh [service] [période]

# Exemples
./export-logs.sh reverseproxy 24h    # Logs nginx des dernières 24h
./export-logs.sh backend 1h          # Logs backend de la dernière heure
./export-logs.sh all 30m             # Tous les logs des 30 dernières minutes
```

**Périodes valides** : `1h`, `24h`, `7d`, `30m`, etc.

### 2. Export JSON

```bash
cd monitoring
./export-logs-json.sh [période]

# Exemple
./export-logs-json.sh 24h    # Logs nginx en JSON des dernières 24h
```

Produit un fichier JSON avec un objet par ligne (format NDJSON).

### 3. Export CSV

```bash
cd monitoring
./export-logs-csv.sh [période]

# Exemple
./export-logs-csv.sh 24h     # Logs nginx en CSV des dernières 24h
```

Produit un fichier CSV importable dans Excel, LibreOffice, ou tout outil d'analyse de données.

**Colonnes** : timestamp, method, uri, status, bytes_sent, request_time, remote_addr, user_agent, upstream_time

### Via Grafana (interface)

1. Allez dans **Explore**
2. Sélectionnez votre requête LogQL
3. Cliquez sur **Inspector** → **Data**
4. **Download CSV** ou **Download JSON**

### Directement via Docker

```bash
# Logs d'un service
docker-compose logs reverseproxy > nginx-logs.txt

# Logs des dernières 24h
docker-compose logs --since 24h reverseproxy > nginx-24h.txt

# Logs en temps réel
docker-compose logs -f reverseproxy
```

## 🐛 Troubleshooting

### Grafana ne démarre pas

Vérifiez les permissions du volume :
```bash
docker-compose logs grafana
```

### Pas de logs dans Loki

1. Vérifiez que Promtail tourne :
   ```bash
   docker-compose logs promtail
   ```

2. Vérifiez que Promtail peut accéder au socket Docker :
   ```bash
   docker-compose exec promtail ls -la /var/run/docker.sock
   ```

### Loki consomme trop de disque

Réduisez la rétention dans `loki-config.yml` ou purgez manuellement :
```bash
docker-compose exec loki rm -rf /loki/chunks/*
```

## 🎯 Best Practices

1. **Créez des dashboards spécifiques** pour chaque service
2. **Configurez des alertes** pour les erreurs critiques
3. **Utilisez les labels** pour filtrer efficacement
4. **Sauvegardez vos dashboards** régulièrement
5. **Surveillez l'utilisation du disque** de Loki

## 📚 Ressources

- [Documentation Loki](https://grafana.com/docs/loki/latest/)
- [Documentation Promtail](https://grafana.com/docs/loki/latest/clients/promtail/)
- [Documentation Grafana](https://grafana.com/docs/grafana/latest/)
- [LogQL - Langage de requête](https://grafana.com/docs/loki/latest/logql/)
