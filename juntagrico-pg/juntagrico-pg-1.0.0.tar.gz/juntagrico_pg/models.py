from django.db import models


class JuntagricoPGRoles(models.Model):
    '''
    No instances should be created of this class it is just the place to create permissions
    '''

    class Meta:
        permissions = (('can_sql', 'juntagrico_pg'),)
