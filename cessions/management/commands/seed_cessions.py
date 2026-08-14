from django.core.management.base import BaseCommand

from cessions.models import ProduitAgricole


class Command(BaseCommand):

    help = (
        'Crée les produits agricoles de démo pour tester les envois vers '
        'DAMS Distribution (nom aligné sur le Produit "concombre" déjà '
        'présent côté dams).'
    )

    def handle(self, *args, **kwargs):

        produits = [
            'concombre',
        ]

        created_count = 0

        for nom in produits:

            _, created = ProduitAgricole.objects.get_or_create(nom=nom)

            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'{created_count} produit(s) agricole(s) créé(s) avec succès.'
            )
        )
