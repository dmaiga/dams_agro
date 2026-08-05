# App : `engagements`

## Rôle

Intégration avec **DAMS Distribution** (application externe des superviseurs).
Permet à un superviseur, qui n'a pas de compte dans dams_agro, de déclarer un
engagement financier au profit du champ et d'en suivre les remboursements.

C'est le **seul module du repo consommé en écriture** par une application
externe — tous les autres endpoints `/api/...` restent GET uniquement, réservés
au repo `dams` (dashboards direction, session Django). Voir `rules/ARCHITECTURE.md`.

La création d'un engagement se fait **exclusivement via l'API** (DAMS
Distribution). Aucune création web : l'interface web (réservée au responsable
financier) ne sert qu'à consulter les engagements et enregistrer leurs
remboursements.

---

## Contexte métier

Un superviseur peut intervenir financièrement de deux manières :

| Nature              | Le champ reçoit du cash ? | Impact sur le solde |
|---------------------|---------------------------|----------------------|
| `avance_tresorerie` | Oui                       | Augmente (Operation revenu générée) |
| `depense_compte`    | Non (le superviseur paie directement le fournisseur) | Aucun (aucune Operation générée) |

Dans les deux cas, une dette envers le superviseur est créée
(`montant_initial`), remboursable en une ou plusieurs fois. Le remboursement
est toujours une sortie de cash réelle du champ → génère systématiquement une
`Operation` dépense, quelle que soit la nature de l'engagement d'origine.

---

## Modèles

### `EngagementFinancier`

| Champ                  | Type            | Notes                                                          |
|-------------------------|-----------------|-----------------------------------------------------------------|
| `nature`                | CharField       | `avance_tresorerie`, `depense_compte`                          |
| `reference_superviseur`| CharField       | Identifiant/nom du superviseur côté DAMS Distribution (pas de FK — aucun compte dans dams_agro) |
| `reference_externe`    | CharField       | Référence de l'engagement côté DAMS Distribution               |
| `technicien`            | FK `users.User` | Technicien dams_agro concerné, si connu (optionnel)             |
| `montant_initial`       | DecimalField    |                                                                  |
| `label`                 | CharField       | Motif de l'engagement                                           |
| `date_engagement`       | DateField       |                                                                  |
| `note`                  | TextField       | blank                                                            |
| `operation_generee`     | FK `finance.Operation` | Operation revenu auto-créée, uniquement si `avance_tresorerie` |
| `created_at`             | DateTimeField   | auto                                                             |

Propriétés calculées (jamais stockées — même logique que `Operation.real_amount`) :
`montant_rembourse`, `reste_a_rembourser`, `etat` (`ouvert` / `partiel` / `solde`).

### `RemboursementEngagement`

| Champ               | Type                   | Notes                                   |
|----------------------|------------------------|-------------------------------------------|
| `engagement`         | FK `EngagementFinancier` | `related_name='remboursements'`         |
| `montant`            | DecimalField           |                                          |
| `date_remboursement` | DateField              |                                          |
| `reference_externe`  | CharField              | Référence côté DAMS Distribution         |
| `note`               | TextField              | blank                                    |
| `operation_generee`  | FK `finance.Operation` | Operation dépense auto-créée, systématique |
| `created_at`          | DateTimeField          | auto                                      |

---

## Articulation avec `finance` — invariant respecté

Aucune modification de `finance/models.py`. Le service `engagements/services.py`
ne fait que **créer** de nouvelles `Operation` (jamais en modifier une
existante, jamais toucher `corrects_operation`) :

- Création d'un engagement `avance_tresorerie` → `Operation(type='revenu')`.
- Création d'un engagement `depense_compte` → aucune `Operation`.
- Tout remboursement (quelle que soit la nature) → `Operation(type='depense')`.

Les catégories `"Avance superviseur (engagement)"` et
`"Remboursement engagement"` sont créées automatiquement (`get_or_create`)
la première fois — DAMS Distribution n'a pas besoin de connaître les ids de
`Categorie` internes.

Validation : un remboursement doit être `> 0` et `<= reste_a_rembourser` de
l'engagement (`ValidationError` → 400 côté API).

---

## Authentification API

Endpoints protégés par `HasDamsDistributionAPIKey` (`engagements/permissions.py`) :
en-tête `X-Api-Key` comparé (temps constant, `hmac.compare_digest`) à la
variable d'environnement `DAMS_DISTRIBUTION_API_KEY`. Rien en dur, secret
configurable via `.env`.

---

## API REST

### `POST /api/engagements/`

Crée un engagement. Payload : `nature`, `montant_initial`, `label`,
`reference_superviseur`, `reference_externe` (optionnel), `technicien`
(optionnel), `date_engagement` (optionnel, défaut aujourd'hui), `note`
(optionnel).

### `GET /api/engagements/`

Liste (filtres `nature`, `technicien`, `reference_superviseur`, `etat`, +
`DateFilterMixin` sur `date_engagement`). `reference_superviseur` permet à un
superviseur DAMS Distribution de ne récupérer que ses propres engagements
sans tout paginer côté client.

### `GET /api/engagements/dashboard/`

Indicateurs agrégés — même logique que `finance`'s `/api/dashboard/`.
Filtrable par `reference_superviseur` (vue superviseur) ou global (vue
direction), + `DateFilterMixin` sur `date_engagement`.

Réponse :
```json
{
  "nombre_engagements": 2,
  "total_engage": "100000.00",
  "total_avance_tresorerie": "50000.00",
  "total_depense_compte": "50000.00",
  "total_rembourse": "72000.00",
  "reste_a_rembourser": "28000.00",
  "nombre_ouverts": 0,
  "nombre_partiels": 1,
  "nombre_soldes": 1
}
```

### `GET /api/engagements/<pk>/`

Détail complet avec `remboursements` imbriqués.

### `POST /api/engagements/<pk>/remboursements/`

Enregistre un remboursement partiel ou total. Payload : `montant`,
`date_remboursement` (optionnel), `reference_externe` (optionnel), `note`
(optionnel). Retourne 400 si le montant dépasse le reste à rembourser.

### `GET /api/engagements/<pk>/remboursements/`

Liste les remboursements d'un engagement.

---

## Interface web (responsable financier uniquement)

Accessible via le menu **Engagements**, affiché uniquement pour le rôle
`type_user='finance'` (branche `else` du menu dans `users/templates/base.html`).
Ce module est **exclusivement réservé au responsable financier** : un
technicien (`user.est_superviseur`) reçoit un `403 PermissionDenied` sur
n'importe laquelle de ces vues, même en accédant directement à l'URL — il n'a
aucun accès à la gestion des dettes/engagements. N'affecte en rien les
templates/vues `finance` existants (Opérations, Produits, Catégories restent
inchangés).

| URL                              | Vue                     | Rôle                              |
|------------------------------------|-------------------------|--------------------------------------|
| `/engagements/`                    | `engagement_list`        | Liste (lecture seule)                |
| `/engagements/<pk>/`               | `engagement_detail`      | Détail + historique remboursements   |
| `/engagements/<pk>/rembourser/`    | `remboursement_create`   | Formulaire de remboursement           |

Aucune vue de création côté web : `engagements/forms.py` ne contient que
`RemboursementForm`, qui appelle `engagements/services.py.enregistrer_remboursement`
— la même fonction que l'API, aucune logique dupliquée.

---

## Règles métier

1. `depense_compte` ne génère jamais d'`Operation` — le solde ne doit pas augmenter.
2. `avance_tresorerie` génère toujours une `Operation` revenu à la création.
3. Tout remboursement génère toujours une `Operation` dépense.
4. Un remboursement ne peut jamais dépasser le reste à rembourser.
5. `montant_rembourse`, `reste_a_rembourser`, `etat` sont calculés, jamais stockés.
6. Seul module du repo acceptant POST/PATCH — authentifié par clé API dédiée.
