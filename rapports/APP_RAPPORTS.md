# App : `rapports`

## Rôle

Collecte de données opérationnelles de la ferme DAMS.
Permet aux superviseurs de consigner quotidiennement les activités,
documenter les incidents terrain, et évaluer nominativement les agents.

---

## Modèles

### `RapportJournalier`

| Champ              | Type          | Notes                        |
|--------------------|---------------|------------------------------|
| `superviseur`      | FK User       | `related_name="rapports"`    |
| `date`             | DateField     | Date effective des travaux   |
| `activite_realisee`| TextField     | Résumé des travaux           |
| `probleme`         | TextField     | Problème rencontré (blank)   |
| `solution`         | TextField     | Solution appliquée (blank)   |
| `resultat_obtenu`  | TextField     | Résultat concret (blank)     |
| `created_at`       | DateTimeField | auto                         |

---

### `ParticipationAgent`

Ligne d'évaluation nominative : un agent par rapport.

**Contrainte :** `unique_together = (rapport, agent)`

| Champ         | Type                   | Notes                            |
|---------------|------------------------|----------------------------------|
| `rapport`     | FK RapportJournalier   | `related_name="participants"`    |
| `agent`       | FK Agent               | `related_name="participations"`  |
| `implication` | PositiveSmallIntegerField | Choices 1–5 (voir ci-dessous)  |
| `maitrise`    | PositiveSmallIntegerField | Choices 1–5 (voir ci-dessous)  |
| `observation` | CharField(255)         | Note libre (blank)               |

#### `NiveauImplication` (IntegerChoices)

| Valeur | Label          |
|--------|----------------|
| 1      | 1 - Faible     |
| 2      | 2 - Moyenne    |
| 3      | 3 - Bonne      |
| 4      | 4 - Très bonne |
| 5      | 5 - Excellente |

#### `NiveauMaitrise` (IntegerChoices)

| Valeur | Label              |
|--------|--------------------|
| 1      | 1 - Débutant       |
| 2      | 2 - En apprentissage |
| 3      | 3 - Autonome       |
| 4      | 4 - Bonne maîtrise |
| 5      | 5 - Expert         |

Le préfixe numérique est intentionnel pour la lisibilité directe dans les selects et l'API.
Côté `dams` : afficher `implication_display` tel quel → `"Moussa : 1 - Faible"`.

---

## Isolation des données

- Liste : `filter(superviseur=request.user)`
- Détail : `get_object_or_404(RapportJournalier, pk=pk, superviseur=request.user)` (anti-IDOR)
- Agents dans le formset : `Agent.objects.filter(superviseur=request.user, actif=True)`

---

## API REST

### `GET /api/rapports/`

Pagination : 20/page (`RapportPagination`).
`select_related("superviseur")` + `prefetch_related("participants", "participants__agent")`.

**Filtres :** `?period=today|week|month|year`, `?date_from=`, `?date_to=`, `?superviseur=<id>`

### `GET /api/rapports/<pk>/`

Détail complet avec `nombre_participants` (champ calculé dans le serializer).

### `GET /api/superviseurs/`

Retourne les users ayant au moins un rapport (`rapports__isnull=False`, distinct).
Utilisé pour alimenter les filtres côté `dams`.

---

## Serializers

### `ParticipationAgentSerializer`

| Champ               | Description                              |
|---------------------|------------------------------------------|
| `implication`       | Valeur entière (1–5)                     |
| `implication_display` | Label complet ex : `"1 - Faible"`     |
| `maitrise`          | Valeur entière (1–5)                     |
| `maitrise_display`  | Label complet ex : `"3 - Autonome"`     |

---

## Règles métier

1. Un superviseur ne voit que ses propres rapports (isolation stricte).
2. L'évaluation (implication, maîtrise) est nominative et par rapport.
3. Un couple `(rapport, agent)` est unique — pas de doublon par journée.
4. Les labels incluent le chiffre en préfixe pour comparaison directe.
