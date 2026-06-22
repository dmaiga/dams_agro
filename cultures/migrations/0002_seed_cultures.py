from django.db import migrations


CULTURES = [
    ("Maïs", "t"),
    ("Arachide", "t"),
    ("Niébé", "t"),
    ("Oignon", "t"),
]


def seed(apps, schema_editor):
    Culture = apps.get_model("cultures", "Culture")
    for nom, unite in CULTURES:
        Culture.objects.get_or_create(nom=nom, defaults={"unite_rendement": unite})


def unseed(apps, schema_editor):
    Culture = apps.get_model("cultures", "Culture")
    Culture.objects.filter(nom__in=[c[0] for c in CULTURES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("cultures", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
