

#from views.auth import ppssauthpolicy,ACLRoot,getPrincipals
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
import transaction
import zope.sqlalchemy

from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.authentication import SessionAuthenticationPolicy
from .constants import Conf
from .models import initdb,PPSsuser
from .routes import configRoutes


from pyramid.security import (
    Everyone, Authenticated,
    remember,forget,
    Allow,
    Everyone,ALL_PERMISSIONS
    )


def initAuthDb(settings):
    engine = engine_from_config(settings, "sqlalchemy.")
    factory = sessionmaker()
    factory.configure(bind=engine)
    #dbsession = get_tm_session(session_factory, transaction.manager)
    dbsession = factory()
    zope.sqlalchemy.register(
        dbsession, transaction_manager=transaction.manager)
    with transaction.manager:
        initdb(dbsession,Conf.initdb)

def getLoggedUser(request):
    uid = request.session['user']['id'] if 'user' in request.session else False
    if uid:
        user = PPSsuser.byId(uid,request.dbsession)
        return user
    return None
    


configured = False
def includeme(config):
    global configured
    if configured:
        return
    configured = True
    #ppssauthpolicy = PPSSAuthenticationPolicy(config.get_settings())
    settings = config.get_settings()
    Conf.setup(settings)
    config.add_request_method(getLoggedUser,'loggeduser',reify=True)
    initAuthDb(settings)

    configRoutes(config,Conf)
    
    from .views.auth import getPrincipals,ACLRoot
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(SessionAuthenticationPolicy(callback=getPrincipals) )
    config.set_authorization_policy(ACLAuthorizationPolicy())
    config.set_root_factory(ACLRoot)
    config.scan("ppss_auth")
    pass
