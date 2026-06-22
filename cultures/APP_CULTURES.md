# App : `cultures`

## Rôle

Digitalise le suivi des cycles agricoles de la ferme DAMS.
Remplace le flux WhatsApp (besoins en semences, engrais, phyto + rendements).
Chaque cycle est historisé de la mise en terre à la récolte.

---

## Rôles utilisateurs

| Acteur            | Dans dams_agro                                                   | Dans dams (lecture) |
|-------------------|------------------------------------------------------------------|---------------------|
| Agent de la ferme | Crée les fiches, saisit les intrants, enregistre les rendements  | —                   |
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

#### Phase résultat (après récolte)

| Champ                   | Type         | Notes                      |
|-------------------------|--------------|----------------------------|
| `rendement_reel`        | DecimalField | Rendement obtenu — null/blank |
| `date_recolte`          | DateField    | null/blank                 |
| `observation_direction` | TextField    | Annotation pour l'analyse  |

#### Propriétés calculées (non stockées)

| Propriété           | Formule                                              |
|---------------------|------------------------------------------------------|
| `unite_rendement`   | `culture.unite_rendement`                            |
| `duree_cycle_jours` | `date_recolte - fiche.date_debut` (None si pas récolté) |
| `ecart_rendement`   | `rendement_reel - rendement_estime`                  |
| `ecart_pct`         | `(reel - estime) / estime * 100`                     |

---

## Avancement d'une fiche (annotation BDD)

Dans `fiche_list`, le queryset est annoté par le moteur SQL :
```python
.annotate(
    nb_cultures=Count("besoins"),
    nb_recoltes=Count("besoins", filter=Q(besoins__date_recolte__isnull=False)),
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

| Formulaire             | Champs                                              |
|------------------------|-----------------------------------------------------|
| `CultureForm`          | `nom`, `unite_rendement`                            |
| `FicheCultureForm`     | `date_debut`, `superficie_ha`, `note`               |
| `BesoinCultureForm`    | `culture`, `semence_*`, `engrais`, `produit_phyto`, `rendement_estime` |
| `BesoinCultureFormSet` | `inlineformset_factory(FicheCulture, BesoinCulture, fk_name="fiche", extra=1, can_delete=True)` |
| `SuiviRendementForm`   | `rendement_reel`, `date_recolte`, `observation_direction` |

---

## Vues web

| Vue                   | URL                                       | Description                              |
|-----------------------|-------------------------------------------|------------------------------------------|
| `fiche_list`          | `GET /cultures/`                          | Liste avec badge avancement              |
| `fiche_create`        | `GET/POST /cultures/nouvelle/`            | Création + formset dynamique JS          |
| `fiche_detail`        | `GET /cultures/<pk>/`                     | Détail + durée cycle + écart % par culture |
| `saisir_rendement`    | `GET/POST /cultures/besoin/<pk>/rendement/` | Saisie rendement obtenu               |
| `culture_list_create` | `GET/POST /cultures/types/`               | Référentiel cultures — liste + ajout     |
| `base_connaissances`  | `GET /cultures/connaissances/`            | Historique filtré `fiche__technicien=request.user` |

> `base_connaissances` est filtré par agent connecté.
> L'agrégat global multi-agents est réservé à l'API `/api/cultures/connaissances/`.

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

**BesoinCultureSerializer** expose : `ecart_rendement`, `ecart_pct`, `duree_cycle_jours`, `unite_rendement`.
Le champ `observation` mappe vers `observation_direction`.

### `GET /api/cultures/<pk>/`

Détail complet d'une fiche.

### `GET /api/cultures/connaissances/`

Agrégat global (tous agents). Ne retourne que les cultures avec `rendement_reel` renseigné.

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
2. `rendement_reel` est saisi par l'agent après récolte — aucune restriction de rôle.
3. `Culture` est protégée à la suppression (PROTECT) si des `BesoinCulture` y font référence.
4. La fiche peut être créée a posteriori : `date_debut` est un champ manuel.
5. `saison_label` et `duree_cycle_jours` sont calculés à la volée — non stockés.
