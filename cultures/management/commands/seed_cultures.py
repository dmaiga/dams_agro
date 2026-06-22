"""
Commande de seed pour l'app cultures.

Crée des données réalistes sur plusieurs cycles / agents pour tester
tous les états de l'interface : terminé, partiel, en cours.

Usage :
    python manage.py seed_cultures
    python manage.py seed_cultures --reset   # efface les fiches existantes avant
"""
import datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from cultures.models import BesoinCulture, Culture, FicheCulture

User = get_user_model()

# ---------------------------------------------------------------------------
# Données de seed
# Format : liste de fiches, chaque fiche référence un user par index (0-based)
# dans la liste des users récupérés.
# ---------------------------------------------------------------------------

FICHES = [
    # ── Cycle 1 : Mahamadou · Juin 2025 · TERMINÉ (2/2) ──────────────────
    {
        "user_index": 0,
        "date_debut": datetime.date(2025, 6, 1),
        "superficie_ha": Decimal("0.50"),
        "note": "Première campagne hivernage — bonnes pluies cette année.",
        "besoins": [
            {
                "culture": "Maïs",
                "semence_quantite": Decimal("10"),
                "semence_unite": "kg",
                "engrais": "2 sacs NPK, 1 sac Urée",
                "produit_phyto": "Herbicide sélectif 1L",
                "rendement_estime": Decimal("1.50"),
                "rendement_reel": Decimal("1.70"),
                "date_recolte": datetime.date(2025, 8, 15),
                "observation_direction": "Bon rendement malgré le retard des pluies en début de cycle.",
            },
            {
                "culture": "Arachide",
                "semence_quantite": Decimal("50"),
                "semence_unite": "kg",
                "engrais": "1 sac DAP",
                "produit_phyto": "",
                "rendement_estime": Decimal("1.00"),
                "rendement_reel": Decimal("0.85"),
                "date_recolte": datetime.date(2025, 8, 20),
                "observation_direction": "Légère baisse due à la sécheresse en phase floraison.",
            },
        ],
    },
    # ── Cycle 2 : Mahamadou · Octobre 2025 · TERMINÉ (2/2) ───────────────
    {
        "user_index": 0,
        "date_debut": datetime.date(2025, 10, 5),
        "superficie_ha": Decimal("0.75"),
        "note": "Contre-saison oignon et niébé — irrigation manuelle.",
        "besoins": [
            {
                "culture": "Oignon",
                "semence_quantite": Decimal("500"),
                "semence_unite": "g",
                "engrais": "2 sacs NPK, 1 sac Urée, 1 sac Potasse",
                "produit_phyto": "Insecticide Dimétho 0.5L, Fongicide 0.3L",
                "rendement_estime": Decimal("8.00"),
                "rendement_reel": Decimal("10.20"),
                "date_recolte": datetime.date(2025, 12, 20),
                "observation_direction": "Excellent cycle. Prix de vente élevé en cette période.",
            },
            {
                "culture": "Niébé",
                "semence_quantite": Decimal("15"),
                "semence_unite": "kg",
                "engrais": "1 sac DAP",
                "produit_phyto": "Insecticide Dimétho 0.3L",
                "rendement_estime": Decimal("0.50"),
                "rendement_reel": Decimal("0.60"),
                "date_recolte": datetime.date(2025, 12, 10),
                "observation_direction": "",
            },
        ],
    },
    # ── Cycle 3 : Mahamadou · Mars 2026 · PARTIEL (1/3 récoltée) ─────────
    {
        "user_index": 0,
        "date_debut": datetime.date(2026, 3, 10),
        "superficie_ha": Decimal("1.00"),
        "note": "Grande parcelle — trois cultures en parallèle, cycles décalés.",
        "besoins": [
            {
                "culture": "Maïs",
                "semence_quantite": Decimal("20"),
                "semence_unite": "kg",
                "engrais": "3 sacs NPK, 2 sacs Urée",
                "produit_phyto": "Herbicide total 2L, Herbicide sélectif 1L",
                "rendement_estime": Decimal("2.00"),
                "rendement_reel": Decimal("1.90"),
                "date_recolte": datetime.date(2026, 5, 20),
                "observation_direction": "Légère verse sur 20 % de la parcelle en fin de cycle.",
            },
            {
                "culture": "Arachide",
                "semence_quantite": Decimal("60"),
                "semence_unite": "kg",
                "engrais": "2 sacs DAP",
                "produit_phyto": "",
                "rendement_estime": Decimal("1.20"),
                "rendement_reel": None,
                "date_recolte": None,
                "observation_direction": "",
            },
            {
                "culture": "Niébé",
                "semence_quantite": Decimal("20"),
                "semence_unite": "kg",
                "engrais": "1 sac DAP",
                "produit_phyto": "Insecticide Dimétho 0.5L",
                "rendement_estime": Decimal("0.70"),
                "rendement_reel": None,
                "date_recolte": None,
                "observation_direction": "",
            },
        ],
    },
    # ── Cycle 4 : Mahamadou · Juin 2026 · EN COURS (0/2) ─────────────────
    {
        "user_index": 0,
        "date_debut": datetime.date(2026, 6, 5),
        "superficie_ha": Decimal("0.50"),
        "note": "",
        "besoins": [
            {
                "culture": "Maïs",
                "semence_quantite": Decimal("10"),
                "semence_unite": "kg",
                "engrais": "2 sacs NPK, 1 sac Urée",
                "produit_phyto": "Herbicide sélectif 1L",
                "rendement_estime": Decimal("1.80"),
                "rendement_reel": None,
                "date_recolte": None,
                "observation_direction": "",
            },
            {
                "culture": "Oignon",
                "semence_quantite": Decimal("300"),
                "semence_unite": "g",
                "engrais": "2 sacs NPK, 1 sac Potasse",
                "produit_phyto": "Fongicide 0.2L",
                "rendement_estime": Decimal("6.00"),
                "rendement_reel": None,
                "date_recolte": None,
                "observation_direction": "",
            },
        ],
    },
    # ── Cycle 5 : Bamba (user 2) · Août 2025 · TERMINÉ (1/1) ─────────────
    {
        "user_index": 2,
        "date_debut": datetime.date(2025, 8, 1),
        "superficie_ha": Decimal("0.25"),
        "note": "Petite parcelle test — saisie a posteriori.",
        "besoins": [
            {
                "culture": "Maïs",
                "semence_quantite": Decimal("5"),
                "semence_unite": "kg",
                "engrais": "1 sac NPK",
                "produit_phyto": "",
                "rendement_estime": Decimal("0.80"),
                "rendement_reel": Decimal("0.65"),
                "date_recolte": datetime.date(2025, 10, 20),
                "observation_direction": "Parcelle ombragée en bordure — rendement réduit prévisible.",
            },
        ],
    },
    # ── Cycle 6 : Bamba (user 2) · Avril 2026 · EN COURS (0/2) ──────────
    {
        "user_index": 2,
        "date_debut": datetime.date(2026, 4, 15),
        "superficie_ha": Decimal("0.50"),
        "note": "Saisie effectuée 3 semaines après démarrage.",
        "besoins": [
            {
                "culture": "Niébé",
                "semence_quantite": Decimal("12"),
                "semence_unite": "kg",
                "engrais": "1 sac DAP",
                "produit_phyto": "",
                "rendement_estime": Decimal("0.60"),
                "rendement_reel": None,
                "date_recolte": None,
                "observation_direction": "",
            },
            {
                "culture": "Oignon",
                "semence_quantite": Decimal("400"),
                "semence_unite": "g",
                "engrais": "2 sacs NPK, 1 sac Urée",
                "produit_phyto": "Insecticide Dimétho 0.2L",
                "rendement_estime": Decimal("7.00"),
                "rendement_reel": None,
                "date_recolte": None,
                "observation_direction": "",
            },
        ],
    },
]


class Command(BaseCommand):
    help = "Seed de démonstration pour l'app cultures (plusieurs cycles / agents)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Supprime toutes les FicheCulture existantes avant de seeder.",
        )

    def handle(self, *args, **options):
        users = list(User.objects.order_by("id"))
        if not users:
            raise CommandError("Aucun utilisateur trouvé. Créez au moins un compte.")

        if options["reset"]:
            deleted, _ = FicheCulture.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"  {deleted} fiche(s) supprimée(s)."))

        created_fiches = 0
        created_besoins = 0

        for data in FICHES:
            idx = data["user_index"]
            user = users[idx] if idx < len(users) else users[0]

            fiche = FicheCulture.objects.create(
                technicien=user,
                date_debut=data["date_debut"],
                superficie_ha=data["superficie_ha"],
                note=data["note"],
            )
            created_fiches += 1

            for b in data["besoins"]:
                try:
                    culture = Culture.objects.get(nom=b["culture"])
                except Culture.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f"  Culture '{b['culture']}' absente, ignorée.")
                    )
                    continue

                BesoinCulture.objects.create(
                    fiche=fiche,
                    culture=culture,
                    semence_quantite=b["semence_quantite"],
                    semence_unite=b["semence_unite"],
                    engrais=b["engrais"],
                    produit_phyto=b["produit_phyto"],
                    rendement_estime=b["rendement_estime"],
                    rendement_reel=b["rendement_reel"],
                    date_recolte=b["date_recolte"],
                    observation_direction=b["observation_direction"],
                )
                created_besoins += 1

            self.stdout.write(
                f"  OK {fiche.saison_label} - {user.first_name or user.phone_number} "
                f"- {len(data['besoins'])} culture(s)"
            )

        self.stdout.write(self.style.SUCCESS(
            f"\n{created_fiches} fiches et {created_besoins} lignes créées."
        ))
