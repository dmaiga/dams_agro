import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('cultures', '0002_seed_cultures'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # 1. Renommer le modèle (conserve la table, met à jour les FK)
        migrations.RenameModel('DemandeCulture', 'FicheCulture'),

        # 2. Ajouter date_debut (default one-off pour les éventuels enregistrements existants)
        migrations.AddField(
            model_name='ficheculture',
            name='date_debut',
            field=models.DateField(
                verbose_name='Date de démarrage',
                help_text='Date réelle de mise en culture (peut être renseignée après coup)',
                default=datetime.date(2026, 1, 1),
            ),
            preserve_default=False,
        ),

        # 3. Supprimer les champs remplacés / supprimés
        migrations.RemoveField(model_name='ficheculture', name='titre'),
        migrations.RemoveField(model_name='ficheculture', name='statut'),
        migrations.RemoveField(model_name='ficheculture', name='saison'),
        migrations.RemoveField(model_name='ficheculture', name='date_demande'),

        # 4. Mettre à jour le verbose_name de note
        migrations.AlterField(
            model_name='ficheculture',
            name='note',
            field=models.TextField(blank=True, verbose_name='Observations'),
        ),

        # 5. Renommer la FK dans BesoinCulture (demande → fiche)
        migrations.RenameField(
            model_name='besoinculture',
            old_name='demande',
            new_name='fiche',
        ),

        # 6. Mettre à jour les verbose_name de BesoinCulture
        migrations.AlterField(
            model_name='besoinculture',
            name='semence_quantite',
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=10, null=True,
                verbose_name='Quantité semences',
            ),
        ),
        migrations.AlterField(
            model_name='besoinculture',
            name='engrais',
            field=models.TextField(blank=True, verbose_name='Engrais fournis'),
        ),
        migrations.AlterField(
            model_name='besoinculture',
            name='produit_phyto',
            field=models.TextField(blank=True, verbose_name='Produits phytosanitaires'),
        ),
        migrations.AlterField(
            model_name='besoinculture',
            name='rendement_estime',
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=10, null=True,
                verbose_name='Objectif de rendement',
            ),
        ),
        migrations.AlterField(
            model_name='besoinculture',
            name='rendement_reel',
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=10, null=True,
                verbose_name='Rendement obtenu',
            ),
        ),
        migrations.AlterField(
            model_name='besoinculture',
            name='date_recolte',
            field=models.DateField(blank=True, null=True, verbose_name='Date de récolte'),
        ),
        migrations.AlterField(
            model_name='besoinculture',
            name='observation_direction',
            field=models.TextField(blank=True, verbose_name='Observation'),
        ),
    ]
