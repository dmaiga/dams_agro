from decimal import Decimal
from datetime import datetime
from django.core.management.base import BaseCommand
from finance.models import Operation, Categorie

class Command(BaseCommand):
    help = 'Importer revenus et dépenses réels avec prix unitaires'

    def handle(self, *args, **kwargs):
        # On nettoie la table avant l'import
        Operation.objects.all().delete()

        # --- REVENUS ---
        revenus = [
            ('18/04/2026', 2, 150, 300),
            ('19/04/2026', 7, 150, 1050),
            ('20/04/2026', 32, 100, 3200),
            ('21/04/2026', 12, 150, 1800),
            ('22/04/2026', 8, 150, 1200),
            ('23/04/2026', 20, 100, 2000),
            ('24/04/2026', 13, 150, 1950),
            ('25/04/2026', 11, 150, 1650),
            ('26/04/2026', 19, 150, 2850),
            ('27/04/2026', 13, 150, 1950),
            ('28/04/2026', 12, 150, 1800),
            ('29/04/2026', 20, 100, 2000),
            ('30/04/2026', 15, 150, 2250),
        ]

        # --- DEPENSES (Structure: Date, Motif, Quantité, Prix Unitaire, Montant) ---
        depenses = [
            ('20/04/2026', 'emballage', '2', 200, 400),
            ('21/04/2026', 'sache normal', '3', 300, 900),
            ('21/04/2026', 'essence', '1L', 1250, 1250),
            ('21/04/2026', 'Chiffon', '1', 100, 100),
            ('25/04/2026', 'ventilateur', '1', 4000, 4000),
            ('25/04/2026', 'sache normal', '3', 300, 900),
            ('25/04/2026', 'frais de réparation', '1', 3000, 3000),
            ('26/04/2026', 'essence', '1L', 1250, 1250),
            ('27/04/2026', 'emballage', '2', 200, 400),
            ('27/04/2026', 'sache normal', '3', 300, 900),
            ('29/04/2026', 'essence', '1L', 1250, 1250),
        ]

        mapping_categories = {
            'emballage': 'Emballage',
            'sache normal': 'Sachets',
            'essence': 'Essence',
            'Chiffon': 'Nettoyage',
            'ventilateur': 'Matériel',
            'frais de réparation': 'Réparation',
        }

        # --- CREATION REVENUS ---
        self.stdout.write(self.style.SUCCESS('Création revenus...'))
        for (date_str, quantity, unit_price, amount) in revenus:
            Operation.objects.create(
                operation_type='revenu',
                categorie=None,
                label='Vente glace',
                quantity=Decimal(str(quantity)),
                unit_price=Decimal(str(unit_price)),
                amount=Decimal(str(amount)),
                is_manual_amount=False,
                operation_date=datetime.strptime(date_str, '%d/%m/%Y').date(),
                note='Import venant du fichier excel'
            )

        # --- CREATION DEPENSES ---
        self.stdout.write(self.style.SUCCESS('Création dépenses...'))
        for (date_str, motif, qty_str, up_val, amount_val) in depenses:
            
            # Nettoyage de la quantité (ex: "1L" -> "1")
            clean_qty = qty_str.replace('L', '').strip()
            
            categorie_nom = mapping_categories.get(motif, 'Divers')
            categorie = Categorie.objects.filter(nom=categorie_nom).first()

            Operation.objects.create(
                operation_type='depense',
                categorie=categorie,
                label=motif,
                quantity=Decimal(clean_qty) if clean_qty else Decimal('1'),
                unit_price=Decimal(str(up_val)),
                amount=Decimal(str(amount_val)),
                is_manual_amount=True,
                operation_date=datetime.strptime(date_str, '%d/%m/%Y').date(),
                note='Import venant du fichier excel'
            )

        self.stdout.write(self.style.SUCCESS('Import terminé avec succès.'))