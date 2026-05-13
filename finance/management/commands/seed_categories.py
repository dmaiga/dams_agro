from django.core.management.base import BaseCommand

from finance.models import Categorie


class Command(BaseCommand):

    help = 'Créer les catégories de dépenses'

    def handle(self, *args, **kwargs):

        categories = [

            {
                'nom': 'Essence',
                'description': (
                    'Achat carburant pour moto, véhicule ou groupe.'
                )
            },

            {
                'nom': 'Transport',
                'description': (
                    'Déplacement, transport marchandises ou livraison.'
                )
            },

            {
                'nom': 'Réparation',
                'description': (
                    'Réparation frigo, matériel ou équipement.'
                )
            },

            {
                'nom': 'Électricité',
                'description': (
                    'Dépenses liées au courant ou énergie.'
                )
            },

            {
                'nom': 'Sachets',
                'description': (
                    'Achat sachets pour emballage.'
                )
            },

            {
                'nom': 'Emballage',
                'description': (
                    'Cartons, emballages et protection produits.'
                )
            },

            {
                'nom': 'Eau',
                'description': (
                    'Achat eau ou dépenses liées à l’eau.'
                )
            },


            {
                'nom': 'Matériel',
                'description': (
                    'Petit matériel et équipements.'
                )
            },

            {
                'nom': 'Nettoyage',
                'description': (
                    'Produits nettoyage et entretien.'
                )
            },

            {
                'nom': 'Main d’oeuvre',
                'description': (
                    'Paiement aide terrain ou manutention.'
                )
            },

            {
                'nom': 'Téléphone',
                'description': (
                    'Communication et appels.'
                )
            },

            {
                'nom': 'Recharge',
                'description': (
                    'Recharge téléphonique ou internet.'
                )
            },

            {
                'nom': 'Livraison',
                'description': (
                    'Dépenses liées aux livraisons.'
                )
            },

            {
                'nom': 'Location',
                'description': (
                    'Location matériel ou espace.'
                )
            },

            {
                'nom': 'Taxes',
                'description': (
                    'Taxes, frais administratifs ou autorisations.'
                )
            },

            {
                'nom': 'Divers',
                'description': (
                    'Dépenses diverses non catégorisées.'
                )
            },
        ]

        created_count = 0

        for categorie in categories:

            _, created = Categorie.objects.get_or_create(

                nom=categorie['nom'],

                defaults={
                    'description': categorie['description']
                }
            )

            if created:
                created_count += 1

        self.stdout.write(

            self.style.SUCCESS(
                f'{created_count} catégories créées avec succès.'
            )
        )