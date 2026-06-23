# App : `cultures`

## Rôle

Digitalise le suivi des cycles agricoles de la ferme DAMS.
Remplace le flux WhatsApp (besoins en semences, engrais, phyto + rendements).
Chaque cycle est historisé de la mise en terre à la récolte.

---

## Rôles utilisateurs

| Acteur            | Dans dams_agro                                                   | Dans dams (lecture) |
|-------------------|------------------------------------------------------------------|---------------------|
| Agent de la ferme | Crée les fiches, saisit les intrants, enregistre les récoltes    | —                   |
| Direction         | Aucune vue dédiée                                                | GET + analyse via API |

Pas de workflow d'approbation. Toute saisie est terrain, y compris a posteriori.

---

## Modèles

### `Culture` — référentiel

| Champ             | Type         | Notes                             |
|-------------------|--------------|-----------------------------------|
| `nom`             | CharField    | Unique. Ex : "Maïs"               |
| `unite_rendement` | CharField    | Default "t". Ex : "kg", "t", "sac"|
| `actif`           | BooleanField | Filtre les selects dans les forms  |

Cultures seedées : Maïs, Arachide, Niébé, Oignon.
Les agents ajoutent de nouvelles cultures via `/cultures/types/`.

---

### `FicheCulture` — en-tête d'un cycle

| Champ          | Type          | Notes                                                        |
|----------------|---------------|--------------------------------------------------------------|
| `technicien`   | FK User       | Agent qui crée la fiche (`related_name="fiches_culture"`)    |
| `date_debut`   | DateField     | Date réelle de mise en culture — saisie manuelle, peut être a posteriori |
| `superficie_ha`| DecimalField  | Default 0.5 ha                                               |
| `note`         | TextField     | Observations libres (optionnel)                              |
| `created_at`   | DateTimeField | Horodatage technique auto                                    |

**Pas de** `titre`, `statut`, `saison` ni `date_demande` — supprimés (migration 0003).

**Propriété calculée :**
- `saison_label` → `"Juin 2026"` dérivé de `date_debut` (non stocké)

---

### `BesoinCulture` — une ligne par culture dans la fiche

**FK :** `fiche` → `FicheCulture` (`related_name="besoins"`)

#### Phase saisie (intrants fournis)

| Champ              | Type         | Notes                           |
|--------------------|--------------|---------------------------------|
| `culture`          | FK Culture   | PROTECT à la suppression        |
| `semence_quantite` | DecimalField | null/blank                      |
| `semence_unite`    | CharField    | Default "kg"                    |
| `engrais`          | TextField    | Texte libre (format WhatsApp)   |
| `produit_phyto`    | TextField    | Texte libre                     |
| `rendement_estime` | DecimalField | Objectif au démarrage — null/blank |

#### Phase résultat (récolte échelonnée — sprint 05)

| Champ                   | Type         | Notes                                                          |
|-------------------------|--------------|----------------------------------------------------------------|
| `rendement_reel`        | DecimalField | Figé à la clôture = `total_passages()`. null/blank avant clôture |
| `date_recolte`          | DateField    | Fixé automatiquement à `date.today()` lors de la clôture      |
| `recolte_cloturee`      | BooleanField | Default False. True = récolte terminée, plus de passage possible |
| `observation_direction` | TextField    | Annotation saisie lors de la clôture                          |

#### Propriétés calculées (non stockées)

| Propriété           | Formule                                              |
|---------------------|------------------------------------------------------|
| `unite_rendement`   | `culture.unite_rendement`                            |
| `duree_cycle_jours` | `date_recolte - fiche.date_debut` (None si pas clôturé) |
| `ecart_rendement`   | `rendement_reel - rendement_estime`                  |
| `ecart_pct`         | `(reel - estime) / estime * 100`                     |
| `total_passages()`  | `Sum("passages_recolte__quantite")` — total en cours avant clôture |

---

### `RapportCulture` — bilan de fin de cycle (sprint 06)

**OneToOne :** `besoin` → `BesoinCulture` (`related_name="rapport_culture"`)

| Champ             | Type         | Notes                                      |
|-------------------|--------------|--------------------------------------------|
| `bilan_activites` | TextField    | Résumé des travaux effectués               |
| `problemes`       | TextField    | Difficultés rencontrées                    |
| `solutions`       | TextField    | Solutions appliquées                       |
| `resultats`       | TextField    | Résultats obtenus                          |
| `perspectives`    | TextField    | Perspectives pour le prochain cycle        |
| `created_at`      | DateTimeField| Auto                                       |

Créé via `get_or_create` — modifiable après la clôture.

---

### `ParticipationCulture` — évaluation d'un agent sur un cycle (sprint 06)

**FK :** `rapport` → `RapportCulture` (`related_name="participations"`)

| Champ        | Type                   | Notes                                              |
|--------------|------------------------|----------------------------------------------------|
| `agent`      | FK Agent               | `related_name="participations_culture"`            |
| `implication`| PositiveSmallIntegerField | Choices : 1 Faible … 5 Excellente              |
| `maitrise`   | PositiveSmallIntegerField | Choices : 1 Débutant … 5 Expert                |
| `observation`| CharField(255)         | blank=True                                         |

`unique_together = ("rapport", "agent")` — un agent une seule fois par rapport.

**Choices NiveauImplication / NiveauMaitrise** : mêmes labels que `rapports.ParticipationAgent`.

---

### `PassageRecolte` — un passage de récolte (sprint 05)

**FK :** `besoin` → `BesoinCulture` (`related_name="passages_recolte"`)

| Champ          | Type         | Notes                              |
|----------------|--------------|------------------------------------|
| `date_passage` | DateField    | Date du passage de récolte         |
| `quantite`     | DecimalField | Quantité récoltée ce jour          |
| `observation`  | CharField    | max_length=255, blank=True         |
| `created_at`   | DateTimeField| Auto                               |

Ordonné par `date_passage`. Interdit d'ajout si `besoin.recolte_cloturee=True`.

---

## Workflow récolte échelonnée

```
fiche_detail
  └─ BesoinCulture
       ├─ [Bouton] "Passage de récolte" → ajouter_passage (GET/POST)
       │    Form : date_passage + quantite + observation
       │    Guard : si recolte_cloturee → redirect avec warning
       │
       ├─ Liste des passages (date, quantité, obs) + total en cours
       │
       └─ [Bouton] "Clôturer" → cloturer_recolte (GET/POST)
            Visible uniquement si recolte_cloturee=False et passages >= 1
            GET : récapitulatif passages + total + champ observation
            POST : rendement_reel = total_passages()
                   date_recolte = date.today()
                   recolte_cloturee = True
                   → redirect fiche_detail
```

---

## Avancement d'une fiche (annotation BDD)

Dans `fiche_list`, le queryset est annoté par le moteur SQL :
```python
.annotate(
    nb_cultures=Count("besoins"),
    nb_recoltes=Count("besoins", filter=Q(besoins__recolte_cloturee=True)),
)
```

| Condition                          | Affichage                          |
|------------------------------------|------------------------------------|
| `nb_cultures == 0`                 | —                                  |
| `nb_recoltes == 0`                 | badge gris "N cultures · en cours" |
| `0 < nb_recoltes < nb_cultures`    | badge orange "X/N récoltée(s)"     |
| `nb_recoltes == nb_cultures`       | badge vert "Terminée (N/N)"        |

---

## Formulaires

| Formulaire                    | Champs / notes                                                                  |
|-------------------------------|---------------------------------------------------------------------------------|
| `CultureForm`                 | `nom`, `unite_rendement`                                                        |
| `FicheCultureForm`            | `date_debut`, `superficie_ha`, `note`                                           |
| `BesoinCultureForm`           | `culture`, `semence_*`, `engrais`, `produit_phyto`, `rendement_estime`          |
| `BesoinCultureFormSet`        | `inlineformset_factory(FicheCulture, BesoinCulture, extra=1, can_delete=True)`  |
| `SuiviRendementForm`          | Conservé (non utilisé dans le flux principal — saisie directe obsolète)         |
| `PassageRecolteForm`          | `date_passage`, `quantite`, `observation`                                       |
| `RapportCultureForm`          | `bilan_activites`, `problemes`, `solutions`, `resultats`, `perspectives`        |
| `ParticipationCultureForm`    | `agent`, `implication`, `maitrise`, `observation`                               |
| `ParticipationCultureFormSet` | `inlineformset_factory(RapportCulture, ParticipationCulture, extra=1, can_delete=True)` |

---

## Vues web

| Vue                      | URL                                          | Description                                                   |
|--------------------------|----------------------------------------------|---------------------------------------------------------------|
| `fiche_list`             | `GET /cultures/`                             | Liste avec badge avancement (recolte_cloturee)                |
| `fiche_create`           | `GET/POST /cultures/nouvelle/`               | Création + formset dynamique JS                               |
| `fiche_detail`           | `GET /cultures/<pk>/`                        | Détail + passages + rapport + badge "Rapport manquant"        |
| `ajouter_passage`        | `GET/POST /cultures/besoin/<pk>/passage/`    | Enregistre un passage (date + quantité)                       |
| `cloturer_recolte`       | `GET/POST /cultures/besoin/<pk>/cloturer/`   | Clôture → redirect vers `rapport_culture_create`              |
| `rapport_culture_create` | `GET/POST /cultures/besoin/<pk>/rapport/`    | Bilan de clôture + évaluation agents (get_or_create)          |
| `saisir_rendement`       | `GET /cultures/besoin/<pk>/rendement/`       | Redirect 302 vers `cloturer_recolte` (compat URL)             |
| `culture_list_create`    | `GET/POST /cultures/types/`                  | Référentiel cultures — liste + ajout                          |
| `base_connaissances`     | `GET /cultures/connaissances/`               | Stats globales tous agents : rendements + évaluations         |

> `base_connaissances` est **global** (tous agents). Filtre user supprimé en sprint-06.

---

## API REST

### `GET /api/cultures/`

| Paramètre    | Exemple                     | Description                         |
|--------------|-----------------------------|-------------------------------------|
| `annee`      | `?annee=2026`               | `date_debut__year`                  |
| `mois`       | `?mois=6`                   | `date_debut__month`                 |
| `technicien` | `?technicien=3`             | Fiches d'un agent spécifique        |
| `date_from`  | `?date_from=2026-01-01`     | `date_debut >= date_from`           |
| `date_to`    | `?date_to=2026-12-31`       | `date_debut <= date_to`             |

**Sérialiseur :** `FicheCultureSerializer` — expose `saison_label`, `nb_cultures`, `besoins` imbriqués.

**`BesoinCultureSerializer`** expose :
- `ecart_rendement`, `ecart_pct`, `duree_cycle_jours`, `unite_rendement`
- `recolte_cloturee` (bool)
- `passages_recolte` → liste de `PassageRecolteSerializer`
- `rapport_culture` → `RapportCultureSerializer` (bilan + participations imbriquées)
- `observation` mappe vers `observation_direction`

**`RapportCultureSerializer`** expose : tous les champs texte + `participations` (liste de `ParticipationCultureSerializer`).

**`ParticipationCultureSerializer`** expose : `agent_prenom`, `agent_nom`, `implication_display`, `maitrise_display`, `observation`.

### `GET /api/cultures/<pk>/`

Détail complet d'une fiche — prefetch `besoins__passages_recolte`.

### `GET /api/cultures/rapports/`

Liste paginée de tous les `RapportCulture` — pour la direction (`dams`).

| Paramètre     | Exemple             | Description                          |
|---------------|---------------------|--------------------------------------|
| `culture`     | `?culture=Maïs`     | Filtre `besoin__culture__nom__icontains` |
| `technicien`  | `?technicien=3`     | Filtre par technicien de la fiche    |

**Sérialiseur :** `RapportCultureListSerializer` — expose `culture_nom`, `saison_label`,
`rendement_reel`, `bilan_activites`, `problemes`, `solutions`, `resultats`, `perspectives`,
`technicien_id`, `participations` (agents avec implication/maîtrise).

### `GET /api/cultures/connaissances/`

Agrégat global (tous agents). Retourne par culture :
- Rendements (`nb_campagnes`, `moy_estime`, `moy_reel`, `ecart_pct`)
- `agents` : liste des agents avec `moy_implication`, `moy_maitrise`, `nb_cycles`

Les cultures sans rendement mais avec participations apparaissent également (union des deux ensembles).

---

## Seed de démonstration

```bash
python manage.py seed_cultures          # Crée 6 fiches sur 2 agents
python manage.py seed_cultures --reset  # Efface les fiches existantes et recrée
```

| Cycle             | Agent      | Avancement  |
|-------------------|------------|-------------|
| Juin 2025         | Mahamadou  | Terminée 2/2 |
| Octobre 2025      | Mahamadou  | Terminée 2/2 |
| Mars 2026         | Mahamadou  | Partielle 1/3 |
| Juin 2026         | Mahamadou  | En cours 0/2  |
| Août 2025         | Bamba      | Terminée 1/1  |
| Avril 2026        | Bamba      | En cours 0/2  |

---

## Règles métier

1. `engrais` et `produit_phyto` sont en texte libre — structuration prévue en phase 4.
2. `rendement_reel` est figé lors de la clôture (`total_passages()`) — ne pas modifier manuellement.
3. `recolte_cloturee=True` bloque tout ajout de passage supplémentaire (guard dans `ajouter_passage`).
4. `date_recolte` est fixé automatiquement à `date.today()` lors de la clôture — pas de saisie manuelle.
5. La clôture exige au moins un passage enregistré (guard dans `cloturer_recolte`).
6. `Culture` est protégée à la suppression (PROTECT) si des `BesoinCulture` y font référence.
7. La fiche peut être créée a posteriori : `date_debut` est un champ manuel.
8. `saison_label` et `duree_cycle_jours` sont calculés à la volée — non stockés.
9. Données pré-sprint 05 : les `BesoinCulture` avec `rendement_reel` déjà renseigné restent valides ; `recolte_cloturee` restera False sauf clôture manuelle via admin.
10. `RapportCulture` est créé via `get_or_create` — la page rapport est idempotente et modifiable.
11. `ParticipationCulture` : un agent ne peut apparaître qu'une fois par rapport (`unique_together`). Le formset agents est restreint au superviseur connecté.
12. `base_connaissances` est globale — tous agents, pas de filtre user. Différent de `fiche_list` qui affiche toutes les fiches sans filtre non plus.
