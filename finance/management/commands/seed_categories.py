from django.core.management.base import BaseCommand

from finance.models import Categorie


class Command(BaseCommand):

    help = 'Créer les catégories d’opérations'

    def handle(self, *args, **kwargs):

        categories = [
        
            {
                'nom': 'Sachets - emballages',
                'usage_type': 'stock',
                'description': (
                    'Produits destinés à la vente.'
                )
            },

            {
                'nom': 'Matériel',
                'usage_type': 'both',
                'description': (
                    'Équipements et outils.'
                )
            },

            {
                'nom': 'Fonctionnement',
                'usage_type': 'depense',
                'description': (
                    'Dépenses courantes de fonctionnement.'
                )
            },

            {
                'nom': 'Personnel',
                'usage_type': 'depense',
                'description': (
                    'Paiement des agents et aides.'
                )
            },

            {
                'nom': 'Revenus',
                'usage_type': 'revenu',
                'description': (
                    'Recettes et encaissements.'
                )
            },

            {
                'nom': 'Divers',
                'usage_type': 'both',
                'description': (
                    'Autres opérations.'
                )
            },

        ]

        created_count = 0

        for categorie in categories:

            _, created = Categorie.objects.get_or_create(

                nom=categorie['nom'],

                defaults={

                    'usage_type': (
                        categorie['usage_type']
                    ),

                    'description': (
                        categorie['description']
                    )
                }
            )

            if created:
                created_count += 1

        self.stdout.write(

            self.style.SUCCESS(
                (
                    f'{created_count} catégories '
                    'créées avec succès.'
                )
            )
        )