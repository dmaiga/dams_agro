# App : `users`

## Rôle

Authentification et gestion des ressources humaines de la ferme DAMS.
Fournit le modèle `User` (login par téléphone) et le modèle `Agent`
(ressource opérationnelle suivie dans les autres apps).

---

## Modèles

### `User` — compte de connexion

Authentification par numéro de téléphone (pas de username).

| Champ          | Type      | Notes                                         |
|----------------|-----------|-----------------------------------------------|
| `phone_number` | CharField | Identifiant unique de connexion               |
| `first_name`   | CharField | Prénom                                        |
| `last_name`    | CharField | Nom                                           |
| `type_user`    | CharField | Type de compte (superviseur, responsable financier, etc.) |
| `is_staff`     | BooleanField | Accès admin Django                          |
| `is_superuser` | BooleanField | Droits complets                             |
| `is_active`    | BooleanField | Compte actif                                |

**Relations inverses issues des autres apps :**
- `agents` → Agent supervisés (`related_name="agents"` sur Agent.superviseur)
- `rapports` → RapportJournalier créés
- `fiches_culture` → FicheCulture créées
- `demandes_culture` → (deprecated, remplacé par `fiches_culture`)

**Gestionnaire personnalisé :** `UserManager`
- `create_user(phone_number, password, ...)` — validation + hash du mot de passe
- `create_superuser(...)` — idem + `is_staff=True`, `is_superuser=True`

---

### `Agent` — ressource opérationnelle

Représente les agents de terrain suivis par un superviseur.
N'a pas de compte de connexion — est une FK dans les autres apps.

| Champ        | Type      | Notes                                          |
|--------------|-----------|------------------------------------------------|
| `superviseur`| FK User   | `related_name="agents"` — propriétaire         |
| `prenom`     | CharField |                                                |
| `nom`        | CharField |                                                |
| `telephone`  | CharField | blank                                          |
| `actif`      | BooleanField | Default True — les inactifs restent historisés |
| `note`       | TextField | blank                                          |
| `created_at` | DateTimeField | auto                                       |

**Relations inverses :**
- `productions` → ProductionAgent
- `participations` → ParticipationAgent (rapports)

---

## Isolation des données

Chaque superviseur ne voit et ne peut assigner que ses propres agents :
```python
Agent.objects.filter(superviseur=request.user, actif=True)
```

---

## Authentification

- Login via `phone_number` + `password`
- `AUTHENTICATION_BACKENDS` utilise `phone_number` comme USERNAME_FIELD
- Les mots de passe sont hashés via le système Django standard

---

## Formulaires

| Formulaire  | Champs                          | Usage                         |
|-------------|---------------------------------|-------------------------------|
| `LoginForm` | phone_number, password          | Connexion                     |
| `AgentForm` | prenom, nom, telephone, actif, note | Création / modification agent |

---

## Règles métier

1. Le numéro de téléphone est l'identifiant unique de connexion.
2. Chaque agent appartient à un seul superviseur (`superviseur` FK non-null).
3. Les agents inactifs (`actif=False`) restent dans l'historique mais
   n'apparaissent plus dans les formulaires de saisie.
4. Les mots de passe sont stockés hashés — jamais en clair.
5. Toutes les autres apps utilisent `Agent` comme référence opérationnelle.
