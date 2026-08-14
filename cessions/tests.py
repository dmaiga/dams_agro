from datetime import date
from decimal import Decimal
from unittest.mock import patch

import requests
from django.test import TestCase, override_settings

from cessions.models import Cession, ProduitAgricole
from cessions.services import construire_payload, transmettre_cession
from finance.models import Operation


class CessionModelTests(TestCase):

    def setUp(self):
        self.produit = ProduitAgricole.objects.create(nom='Concombre')

    def _creer_cession(self):
        return Cession.objects.create(
            produit=self.produit,
            quantite=Decimal('100'),
            prix_cession=Decimal('250.00'),
            date_cession=date(2026, 8, 1),
        )

    def test_idempotency_key_generee_automatiquement(self):
        cession = self._creer_cession()
        self.assertIsNotNone(cession.idempotency_key)

    def test_deux_cessions_ont_des_idempotency_key_distinctes(self):
        cession_1 = self._creer_cession()
        cession_2 = self._creer_cession()
        self.assertNotEqual(cession_1.idempotency_key, cession_2.idempotency_key)

    def test_creation_ne_cree_aucune_operation(self):
        self.assertEqual(Operation.objects.count(), 0)
        self._creer_cession()
        self.assertEqual(Operation.objects.count(), 0)

    def test_creation_ne_modifie_pas_le_solde(self):
        def solde_actuel():
            revenus = sum(
                op.real_amount for op in Operation.objects.all()
                if op.operation_type == 'revenu'
            )
            depenses = sum(
                op.real_amount for op in Operation.objects.all()
                if op.operation_type in ('depense', 'stock')
            )
            return revenus - depenses

        solde_avant = solde_actuel()
        self._creer_cession()
        self.assertEqual(solde_actuel(), solde_avant)

    def test_statut_par_defaut_est_locale(self):
        cession = self._creer_cession()
        self.assertEqual(cession.statut, Cession.STATUT_LOCALE)


class CessionTransmissionTests(TestCase):

    def setUp(self):
        self.produit = ProduitAgricole.objects.create(nom='Concombre')
        self.cession = Cession.objects.create(
            produit=self.produit,
            quantite=Decimal('100'),
            prix_cession=Decimal('250.00'),
            date_cession=date(2026, 8, 1),
        )

    def test_payload_contient_les_champs_attendus(self):
        payload = construire_payload(self.cession)

        self.assertEqual(payload['idempotency_key'], str(self.cession.idempotency_key))
        self.assertEqual(payload['produit'], 'Concombre')
        self.assertEqual(payload['quantite'], '100')
        self.assertEqual(payload['prix_cession'], '250.00')
        self.assertEqual(payload['date_cession'], '2026-08-01')

    @override_settings(DAMS_DISTRIBUTION_CESSIONS_URL='')
    def test_transmission_echoue_proprement_si_url_non_configuree(self):
        with patch('cessions.services.requests.post') as mock_post:
            resultat = transmettre_cession(self.cession)

        mock_post.assert_not_called()
        self.assertFalse(resultat)
        self.cession.refresh_from_db()
        self.assertEqual(self.cession.statut, Cession.STATUT_ECHEC)
        # La cession reste bien acquise localement malgré l'échec.
        self.assertTrue(Cession.objects.filter(pk=self.cession.pk).exists())

    @override_settings(DAMS_DISTRIBUTION_CESSIONS_URL='https://dams-distribution.example/api/cessions/')
    def test_erreur_reseau_ne_supprime_pas_la_cession_locale(self):
        with patch(
            'cessions.services.requests.post',
            side_effect=requests.ConnectionError('boom'),
        ):
            resultat = transmettre_cession(self.cession)

        self.assertFalse(resultat)
        self.cession.refresh_from_db()
        self.assertEqual(self.cession.statut, Cession.STATUT_ECHEC)
        self.assertIn('boom', self.cession.derniere_erreur)
        self.assertTrue(Cession.objects.filter(pk=self.cession.pk).exists())

    @override_settings(DAMS_DISTRIBUTION_CESSIONS_URL='https://dams-distribution.example/api/cessions/')
    def test_transmission_reussie_marque_le_statut_transmise(self):
        mock_response = type('Resp', (), {'raise_for_status': lambda self: None})()

        with patch('cessions.services.requests.post', return_value=mock_response):
            resultat = transmettre_cession(self.cession)

        self.assertTrue(resultat)
        self.cession.refresh_from_db()
        self.assertEqual(self.cession.statut, Cession.STATUT_TRANSMISE)
        self.assertIsNotNone(self.cession.transmise_le)


class CessionAPITests(TestCase):

    def setUp(self):
        self.produit = ProduitAgricole.objects.create(nom='Concombre')
        self.cession = Cession.objects.create(
            produit=self.produit,
            quantite=Decimal('100'),
            prix_cession=Decimal('250.00'),
            date_cession=date(2026, 8, 1),
        )

    def test_liste_api_cessions(self):
        response = self.client.get('/api/cessions/')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['idempotency_key'], str(self.cession.idempotency_key))
        self.assertEqual(data[0]['produit_nom'], 'Concombre')

    def test_detail_api_cession(self):
        response = self.client.get(f'/api/cessions/{self.cession.pk}/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['id'], self.cession.pk)

    def test_dashboard_api_cessions(self):
        Cession.objects.create(
            produit=self.produit,
            quantite=Decimal('50'),
            prix_cession=Decimal('100.00'),
            date_cession=date(2026, 8, 2),
        )

        response = self.client.get('/api/cessions/dashboard/')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['nombre_cessions'], 2)
        self.assertEqual(Decimal(str(data['quantite_totale'])), Decimal('150'))
        # 100 * 250.00 + 50 * 100.00 = 25000.00 + 5000.00
        self.assertEqual(Decimal(str(data['montant_total'])), Decimal('30000.00'))

    def test_dashboard_api_cessions_compte_toutes_les_statuts(self):
        Cession.objects.create(
            produit=self.produit,
            quantite=Decimal('10'),
            prix_cession=Decimal('10.00'),
            date_cession=date(2026, 8, 3),
            statut=Cession.STATUT_ECHEC,
        )

        response = self.client.get('/api/cessions/dashboard/')

        self.assertEqual(response.json()['nombre_cessions'], 2)
