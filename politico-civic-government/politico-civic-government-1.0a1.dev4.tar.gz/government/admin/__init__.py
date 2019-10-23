# Imports from Django.
from django.contrib import admin


# Imports from government.
from government.admin.body import BodyAdmin
from government.admin.jurisdiction import JurisdictionAdmin
from government.admin.office import OfficeAdmin
from government.admin.party import PartyAdmin
from government.models import Body
from government.models import Jurisdiction
from government.models import Office
from government.models import Party


admin.site.register(Body, BodyAdmin)
admin.site.register(Jurisdiction, JurisdictionAdmin)
admin.site.register(Office, OfficeAdmin)
admin.site.register(Party, PartyAdmin)
