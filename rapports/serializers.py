from rest_framework import serializers

from .models import (
    RapportJournalier,
    ParticipationAgent
)

from users.models import User

class SuperviseurSerializer( serializers.ModelSerializer):

    class Meta:
        model = User

        fields = (
            "id",
            "first_name",
            "last_name",
            "phone_number",
        )

class ParticipationAgentSerializer(serializers.ModelSerializer):
    agent = serializers.StringRelatedField()
    implication_display = serializers.CharField(
        source="get_implication_display",
        read_only=True
    )
    maitrise_display = serializers.CharField(
        source="get_maitrise_display",
        read_only=True
    )
    class Meta:
        model = ParticipationAgent
        fields = (
            "id",
            "agent",
            "implication",
            "implication_display",
            "maitrise",
            "maitrise_display",
            "observation",
        )


class RapportJournalierSerializer(serializers.ModelSerializer):
    superviseur = SuperviseurSerializer(
        read_only=True
    )
    participants = ParticipationAgentSerializer(
        many=True,
        read_only=True
    )
    nombre_participants = serializers.SerializerMethodField()
    class Meta:
        model = RapportJournalier
        fields = (
            "id",
            "date",
            "superviseur",
            "activite_realisee",
            "probleme",
            "solution",
            "resultat_obtenu",
            "participants",
            "nombre_participants",
            "created_at",
        )
    def get_nombre_participants(self, obj):
        return obj.participants.count()