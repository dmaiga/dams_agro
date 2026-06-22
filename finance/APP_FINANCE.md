# App : `finance`

## Rôle

Socle transactionnel de DAMS Agro. Centralise les mouvements financiers,
les achats et entrées de stock, le suivi des quantités, la répartition
de la production entre agents, et les corrections comptables.

---

## Modèles

### `Categorie`

| Champ  | Type      | Notes                                    |
|--------|-----------|------------------------------------------|
| `nom`  | CharField |                                          |
| `type` | CharField | `revenu`, `depense`, `stock`, `both`     |

Les formulaires filtrent automatiquement par type selon l'opération en cours.

---

### `Operation`

| Champ               | Type          | Notes                                              |
|---------------------|---------------|----------------------------------------------------|
| `operation_type`    | CharField     | `revenu`, `depense`, `stock`                       |
| `categorie`         | FK Categorie  |                                                    |
| `label`             | CharField     | Libellé de l'opération                             |
| `quantity`          | DecimalField  |                                                    |
| `unit_price`        | DecimalField  |                                                    |
| `amount`            | DecimalField  | Calculé : `quantity × unit_price` (ou manuel)      |
| `is_manual_amount`  | BooleanField  | Si True, `amount` est saisi directement            |
| `operation_date`    | DateField     |                                                    |
| `note`              | TextField     | blank                                              |
| `corrects_operation`| FK self       | Pointe vers l'opération corrigée (null si initiale)|
| `created_at`        | DateTimeField | auto                                               |

**Règle de correction :** une opération validée n'est jamais modifiée.
Une correction crée une nouvelle opération pointant vers l'originale via `corrects_operation`.
Le montant effectif est toujours celui de la dernière correction.

> Ne jamais modifier `corrects_operation` ni la logique de correction — c'est le cœur de la traçabilité.

---

### `Produit`

Créé automatiquement lors d'une opération de type `stock`.

| Champ               | Type         | Notes                             |
|---------------------|--------------|-----------------------------------|
| `quantite_initiale` | DecimalField |                                   |
| `quantite_vendue`   | DecimalField |                                   |
| `quantite_perdue`   | DecimalField |                                   |
| `quantite_offerte`  | DecimalField |                                   |

**Stock restant** = `quantite_initiale - quantite_vendue - quantite_perdue`

**Contrainte :** `vendu + perdu + offert ≤ quantite_initiale`

---

### `ProductionAgent`

| Champ      | Type       | Notes                               |
|------------|------------|-------------------------------------|
| `produit`  | FK Produit |                                     |
| `agent`    | FK Agent   |                                     |
| `quantite` | DecimalField |                                   |

**Équilibre :** `sum(quantites agents) == quantite_vendue + quantite_offerte`
→ `production_est_equilibree = True`

---

### `ParametreFinancier` — singleton

| Champ           | Type          | Notes                                         |
|-----------------|---------------|-----------------------------------------------|
| `solde_ajuster` | DecimalField  | Ajustement +/- au solde calculé. Default 0.   |
| `note`          | TextField     | Justification de l'ajustement                 |
| `updated_at`    | DateTimeField | auto_now                                      |

**Singleton :** `pk=1` forcé dans `save()`. Méthode `get_solo()` pour accéder.
Éditable uniquement via l'admin Django (superuser).
Suppression bloquée dans l'admin. Ajout bloqué si instance existe déjà.

---

## Formule du solde

```
solde = revenus - dépenses + ParametreFinancier.solde_ajuster
```

`ajustement_solde` peut être négatif.

---

## API REST

### `GET /api/dashboard/`

| Clé                 | Description                                  |
|---------------------|----------------------------------------------|
| `revenus`           | Somme des opérations `revenu`                |
| `depenses`          | Somme des opérations `depense`               |
| `solde`             | `revenus - dépenses + ajustement`            |
| `ajustement_solde`  | `ParametreFinancier.solde_ajuster`           |
| `resultat`          | `revenus - dépenses` (brut, sans ajustement) |
| `nombre_operations` | Nombre d'opérations sur la période           |
| `nombre_produits`   | Nombre de produits                           |
| `nombre_agents`     | Agents distincts avec production             |

Supporte `DateFilterMixin` : `?period=month`, `?date_from=`, `?date_to=`.

### `GET /api/operations/`
### `GET /api/operations/<pk>/`
### `GET /api/categories/`
### `GET /api/produits/`
### `GET /api/produits/<pk>/`
### `GET /api/agents/`  — performances agents (nb interventions, quantité totale)

---

## Règles métier

1. Une opération validée reste historisée — jamais modifiée directement.
2. Les corrections créent de nouvelles opérations référençant l'originale.
3. Un produit naît obligatoirement d'une opération de type `stock`.
4. Les quantités de stock doivent rester cohérentes (vendu + perdu + offert ≤ initial).
5. Les contributions agents doivent équilibrer ventes + offertes.
6. `ParametreFinancier` est un singleton — un seul enregistrement, pk=1 forcé.
