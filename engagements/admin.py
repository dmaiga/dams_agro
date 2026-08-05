from django.contrib import admin

from engagements.models import EngagementFinancier, RemboursementEngagement


class RemboursementEngagementInline(admin.TabularInline):
    model = RemboursementEngagement
    extra = 0
    readonly_fields = ('operation_generee', 'created_at')


@admin.register(EngagementFinancier)
class EngagementFinancierAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'nature',
        'reference_superviseur',
        'montant_initial',
        'montant_rembourse',
        'reste_a_rembourser',
        'etat',
        'date_engagement',
    )
    list_filter = ('nature',)
    readonly_fields = ('operation_generee', 'created_at')
    inlines = [RemboursementEngagementInline]


@admin.register(RemboursementEngagement)
class RemboursementEngagementAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'engagement', 'montant', 'date_remboursement')
    readonly_fields = ('operation_generee', 'created_at')
