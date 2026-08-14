# App : `cessions`

## Rôle

Permet de déclarer les produits agricoles cédés à **DAMS Distribution**.
Une cession est une **trace transactionnelle historique**, volontairement
isolée de `finance` : elle ne crée aucune `Operation`, n'est pas un revenu,
et ne modifie pas le solde de la ferme (voir `CLAUDE.md` — invariants
finance).

- **Phase 1** (saisie/historisation/lecture) : terminée.
- **Phase 2** (émission) : `dams_champs` transmet chaque cession créée à
  DAMS Distribution par HTTP, via une clé d'idempotence stable. **La
  création locale de la cession reste toujours acquise, indépendamment du
  succès de cette transmission** — voir `services.py`.

Reste hors périmètre : création du `LotEntrepot` côté DAMS Distribution
(traité par DAMS Distribution elle-même à réception), webhook, polling,
retry automatique/file d'attente, Celery/Redis.

---

## Vocabulaire dans les templates

Le terme `Cession`/`cession` reste le nom du modèle et des identifiants
techniques (urls, champs, service), mais n'apparaît plus dans les
templates web : trop abstrait pour un technicien. L'interface utilise
« envoi » / « envoyé à DAMS Distribution » (menu, titres, libellés,
messages) — voir `templates/cessions/list.html` et `form.html`.

---

## Seed de démo

`python manage.py seed_cessions` — crée le `ProduitAgricole` "concombre"
(`get_or_create`, nom aligné sur le `Produit` "concombre" déjà présent
côté `dams`), pour tester l'envoi de bout en bout : saisie ici →
`POST /api/cessions/` → `LotEntrepot` côté `dams`.

---

## Modèles

### `ProduitAgricole`

Référentiel simple du produit agricole cédé. Distinct de `finance.Produit`
(qui naît d'une opération de stock et sert au suivi des ventes internes) —
aucune relation entre les deux modèles, aucune relation avec `cultures`.

| Champ        | Type          | Notes            |
|--------------|---------------|-------------------|
| `nom`        | CharField     | unique            |
| `note`       | TextField     | blank             |
| `created_at` | DateTimeField | auto              |

### `Cession`

| Champ               | Type          | Notes                                              |
|----------------------|---------------|-----------------------------------------------------|
| `produit`            | FK `ProduitAgricole` | `on_delete=PROTECT` — related_name `cessions` |
| `quantite`           | DecimalField  |                                                      |
| `prix_cession`       | DecimalField  | **Prix unitaire** de cession (par unité de quantité, pas un montant total) |
| `date_cession`       | DateField     |                                                      |
| `note`               | TextField     | blank                                               |
| `idempotency_key`    | UUIDField     | `default=uuid.uuid4`, unique, non éditable. Indépendant de `id` — clé stable envoyée à DAMS Distribution pour éviter une double création de `LotEntrepot` si la même requête est renvoyée. |
| `statut`             | CharField     | `locale` (défaut) / `transmise` / `echec`           |
| `transmise_le`       | DateTimeField | null — renseigné au succès de la transmission       |
| `derniere_erreur`    | TextField     | blank — message de la dernière erreur de transmission |
| `created_at`         | DateTimeField | auto                                                |

Aucun champ financier dérivé (pas de dette, pas de recouvrement, pas de lien
`finance.Operation`).

---

## Règles métier

1. Une cession ne crée jamais d'`Operation` et n'impacte jamais le solde.
2. `produit` est protégé en suppression (`PROTECT`) pour préserver
   l'historique des cessions déjà enregistrées.
3. Pas de workflow d'approbation — saisie et historisation pures, comme
   `cultures.FicheCulture`.
4. Pas de connexion avec `cultures` — le produit agricole est un simple
   référentiel, sans traçabilité production → récolte → cession.
5. **La création locale d'une `Cession` ne dépend jamais de la
   disponibilité de DAMS Distribution.** La transmission (`services.py`)
   est une étape postérieure à l'enregistrement ; son échec (réseau, URL
   non configurée) ne supprime ni n'invalide jamais la cession déjà
   enregistrée — il ne fait que positionner `statut='echec'` et renseigner
   `derniere_erreur`.
6. Pas de retry automatique, pas de file d'attente : en cas d'échec,
   `statut` reste `echec` jusqu'à une action manuelle future (hors
   périmètre de cette phase).

---

## Transmission à DAMS Distribution (`services.py`)

### `construire_payload(cession)`

Fonction pure, sans effet de bord ni réseau — construit le payload
conceptuel envoyé à DAMS Distribution :

```json
{
  "idempotency_key": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "produit": "Concombre",
  "quantite": "100",
  "prix_cession": "250.00",
  "date_cession": "2026-08-01"
}
```

> **Le nom exact des champs (`produit`, etc.) et le format ne sont pas
> figés par un contrat DAMS Distribution existant** — ce payload est un
> point de branchement isolé, à ajuster dès que ce contrat sera publié.
> Ne pas supposer qu'il est stable.

### `transmettre_cession(cession)`

Effectue un `POST` HTTP vers `settings.DAMS_DISTRIBUTION_CESSIONS_URL`
avec le header `X-Api-Key: settings.DAMS_DISTRIBUTION_OUTBOUND_API_KEY`
(clé distincte de `DAMS_DISTRIBUTION_API_KEY`, qui elle authentifie DAMS
Distribution *vers* `dams_champs` sur `/api/engagements/`).

- Si `DAMS_DISTRIBUTION_CESSIONS_URL` est vide (contrat pas encore défini)
  → échec immédiat, sans appel réseau, `statut='echec'`.
- Si l'appel réseau échoue (`requests.RequestException`) → `statut='echec'`,
  `derniere_erreur` renseignée avec le détail.
- Si l'appel réussit → `statut='transmise'`, `transmise_le=now()`.

Appelée depuis `views.cession_create` juste après `form.save()` — jamais
avant, pour garantir que la cession existe déjà en base au moment de la
tentative de transmission.

### Configuration (`.env`)

| Variable                              | Rôle                                                    |
|-----------------------------------------|----------------------------------------------------------|
| `DAMS_DISTRIBUTION_CESSIONS_URL`        | URL de l'endpoint DAMS Distribution recevant les cessions (vide par défaut) |
| `DAMS_DISTRIBUTION_OUTBOUND_API_KEY`    | Clé envoyée en en-tête `X-Api-Key` lors de la transmission |

---

## Autorisation

Réservé au responsable financier (`type_user='finance'`, branche `else` du
menu dans `users/templates/base.html`, comme le module `engagements`) : un
superviseur (`user.est_superviseur`) reçoit un `403 PermissionDenied` sur
les vues `cession_list` et `cession_create`, même en accédant directement à
l'URL.

---

## Interface web

| URL                  | Vue              | Rôle                          |
|-----------------------|------------------|--------------------------------|
| `/cessions/`           | `cession_list`    | Liste des cessions enregistrées |
| `/cessions/creer/`     | `cession_create`  | Formulaire de déclaration       |

Deux templates uniquement (`cessions/list.html`, `cessions/form.html`),
layout Bootstrap 5 réutilisé du reste du projet.

---

## API REST (lecture seule)

Consommée par `dams` — session Django, GET uniquement, pas de filtre par
utilisateur (voir `rules/ARCHITECTURE.md`).

### `GET /api/cessions/` *(DateFilter sur `date_cession`)*

Liste des cessions. Filtre additionnel : `produit` (FK `ProduitAgricole`).

**Sérialiseur :** `CessionSerializer`

Champs : `id`, `idempotency_key`, `produit`, `produit_nom`, `quantite`,
`prix_cession`, `date_cession`, `statut`, `statut_display`, `transmise_le`,
`note`, `created_at`

### `GET /api/cessions/<pk>/`

Détail d'une cession.

### `GET /api/cessions/dashboard/` *(DateFilter sur `date_cession`)*

Indicateurs agrégés — même logique que `finance`'s `/api/dashboard/` et
`engagements`'s `/api/engagements/dashboard/`. Sert notamment à `dams`
(analyse_champ) à afficher un KPI « CA total » sans dupliquer le calcul de
la valeur des cessions côté `dams`.

Réponse :
```json
{
  "nombre_cessions": 3,
  "quantite_totale": "300.00",
  "montant_total": "75000.00"
}
```

`montant_total` = somme de `quantite × prix_cession` sur toutes les
cessions de la période, **quel que soit `statut`** — le statut de
transmission à DAMS Distribution n'affecte pas ce calcul (règle 5
ci-dessus : la cession est un fait économique dès sa création).

---

## Articulation avec les autres apps

- Aucune modification de `finance/models.py` ni de `Operation`.
- Aucune relation avec `cultures` en phase 1.
- `ProduitAgricole` ≠ `finance.Produit` — ne pas confondre les deux
  référentiels, ils ne partagent aucune donnée.
