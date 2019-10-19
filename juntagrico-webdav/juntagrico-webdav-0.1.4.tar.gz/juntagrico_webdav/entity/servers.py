from django.db import models


class WebdavServer(models.Model):
    '''
    Webdav Server configuration
    '''
    name = models.CharField('Name', max_length=100, default='')
    url = models.CharField('Server URL', max_length=100, default='')
    path = models.CharField('Ordner Pfad', max_length=100, default='')
    username = models.CharField('Benutzer Name', max_length=100, default='')
    password = models.CharField('Passwort', max_length=100, default='')
    menu_title = models.CharField('Menu Titel', max_length=100, default='')
    active = models.BooleanField('aktiv', default=True)
    type = models.PositiveIntegerField('Typ', choices=((1,'User'),(2,'Admin')))
