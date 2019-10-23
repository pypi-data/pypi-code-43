import six
if six.PY3: unicode = str

from sqlalchemy import (
    Table,
    Column,
    Index,
    Integer,
    Text,
    Unicode,UnicodeText,
    DateTime,
    ForeignKey,
    desc, asc,UniqueConstraint
)
from sqlalchemy.orm import relationship, backref

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import MetaData
NAMING_CONVENTION = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

from datetime import datetime,timedelta

import logging,uuid,hashlib

metadata = MetaData(naming_convention=NAMING_CONVENTION)
Base = declarative_base(metadata=metadata)

from .constants import Conf


l = logging.getLogger('ppssauth.models')


##the caller must commit this
def initdb(session=None,createdefault=False,engine = None):
    if engine is None:
        engine = session.get_bind()
    Base.metadata.create_all( engine )
    if createdefault:
        l.info("creating default")
        if session.query(PPSsuser).filter(PPSsuser.username == u'admin').first():
            ##there is already an admin in DB. Skip further configuration
            l.info("Admin exists. Exiting ppss_auth population")
            return 1
        user = PPSsuser(username = u'admin').setPassword(u'admin')
        session.add(user)
        group = PPSsgroup(name = u"admin")
        user.groups.append(group)
        session.add(group)
        #perm = 
        perms = {#PPSspermission(name = u"admin"),
                'modify':PPSspermission(name = u"edituser",permtype=1),
                'list':PPSspermission(name = u"listuser",permtype=1),
                'login':PPSspermission(name = u"login",permtype=1),
                'sysadmin':PPSspermission(name = u"sysadmin",permtype=1),
                }
        for k in perms.keys():
            group.permissions.append(perms[k]) 
            session.add(perms[k])

        group = PPSsgroup(name = u"user")
        session.add(group)
        group.permissions.append(perms['login']) 
        
        group = PPSsgroup(name = u"sysadmin")
        session.add(group)
        for k in perms.keys():
            group.permissions.append(perms[k]) 
            session.add(perms[k])
        user.groups.append(group)

        return 0
    return 0

ppssuserlkppssgroup = Table('ppssuser_lk_ppssgroup', Base.metadata,
    Column('user_id',Integer,ForeignKey('ppss_user.id')),
    Column('group_id',Integer,ForeignKey('ppss_group.id') )
)
ppssgrouplkppsspermission = Table('ppssgroup_lk_ppsspermission', Base.metadata,
    Column('group_id',Integer,ForeignKey('ppss_group.id')),
    Column('permission_id',Integer,ForeignKey('ppss_permission.id') )
)
#ppssuserlkppsspermission = Table('ppssuser_lk_ppsspermission', Base.metadata,
#    Column('user_id',UnicodeText,ForeignKey('ppss_user.id')),
#    Column('permission_id',Integer,ForeignKey('ppss_permission.id') )
#)


class commonTable():
    @classmethod
    def byId(cls,id,dbsession):
        return dbsession.query(cls).filter(cls.id == id).first()

    @classmethod
    def all(cls,dbsession):
        return dbsession.query(cls).all()


class PPSsuser(Base,commonTable):
    __tablename__   = 'ppss_user'
    id              = Column(Integer, primary_key=True)
    username        = Column(Unicode(128))
    password        = Column(Unicode(1024))
    insertdt        = Column(DateTime,default=datetime.now)
    updatedt        = Column(DateTime,default=datetime.now,onupdate=datetime.now)
    lastlogin       = Column(DateTime)
    enabled         = Column(Integer,default=1)
    magicnumber     = Column(Text(),default=uuid.uuid5(uuid.uuid4(),"bidibibodibibu" ).hex )   #Conf.saltforhash
    createdby       = Column(Integer)
    disabledby      = Column(Integer)

    groups = relationship("PPSsgroup",secondary=ppssuserlkppssgroup,lazy='select', 
        backref=backref('users',lazy='select',order_by='PPSsuser.username'))

    @classmethod
    def checkLogin(cls,user,password,dbsession):
        s = hashlib.sha512(password.encode('utf-8'))
        res = dbsession.query(cls).filter(cls.username==user).filter(cls.password==s.hexdigest()).all()
        return res[0] if len(res)==1 else None

    @classmethod
    def checkCryptedLogin(cls,user,password,dbsession):
        res = dbsession.query(cls).filter(cls.username==user).filter(cls.password==password).all()
        return res[0] if len(res)==1 else None

    def todict(self):
        return { "id": self.id, "username":self.username,"enabled":self.enabled}

    def setPassword(self,password):
        s = hashlib.sha512(password.encode('utf-8'))
        self.password=s.hexdigest()
        return self

    def getPermissions(self):
        result = set()
        for g in self.groups:
            if g.enabled:
                for p in g.permissions:
                    result.add( (p.id, p.name, p.permtype) )
        return result
        # return set([p.name for p in [g.permissions for g in self.groups if g.enabled]] )

    def isSuperUser(self):
        for p in self.getPermissions():
            if p[2]==1 and p[1] == u'sysadmin':
                return True
        return False

    def __unicode__(self):
        return u"<PPSsuser ({id}-{name},{enabled})>".format(id=self.id,name=self.username, enabled=self.enabled)

    def __str__(self): 
        return self.__unicode__()

class PPSspasswordhistory(Base):
    __tablename__   = 'ppss_passwordhistory'
    id              = Column(Integer, primary_key=True)
    user_id         = Column(Integer, ForeignKey('ppss_user.id'))
    insertdt        = Column(DateTime,default=datetime.now)
    password        = Column(Unicode(1024))

    user = relationship("PPSsuser", backref=backref('passowrdhistory',order_by="PPSspasswordhistory.id"))

class PPSsloginhistory(Base):
    __tablename__   = 'ppss_loginhistory'
    id              = Column(Integer, primary_key=True)
    user_id         = Column(Integer, ForeignKey('ppss_user.id'))
    ipaddress       = Column(Unicode(128))
    insertdt        = Column(DateTime,default=datetime.now)


class PPSsgroup(Base,commonTable):
    __tablename__   = 'ppss_group'
    id     = Column(Integer, primary_key=True)
    name   = Column(Unicode(128))
    enabled= Column(Integer,default=1)
    permissions = relationship("PPSspermission",secondary=ppssgrouplkppsspermission  ,backref=backref('groups'))

    def __unicode__(self):
        return u"<PPSsgroup {name} ({id})>".format(name=self.name,id=self.id)
    def __str__(self):
        return self.__unicode__()

    def todict(self):
        return {'id':self.id,"name":self.name}

    def userdict(self):
        return [x.todict() for x in self.users]

    def permdict(self):
        return [x.todict() for x in self.permissions]

class PPSspermission(Base,commonTable):
    __tablename__   = 'ppss_permission'
    id     = Column(Integer, primary_key=True)
    name   = Column(Unicode(128))
    permtype   = Column(Integer,default=0)  #1 is for built-in permissions
    systemperm = Column(Unicode(4),default=u'y')

    def __unicode__(self):
        return u"<PPSspermission {name} ({id})>".format(name=self.name,id=self.id)
    def __str__(self):
        return self.__unicode__()

    def todict(self):
        return {'id':self.id,"name":self.name,"permtype":self.permtype}

class DBVersion(Base):
    __tablename__   = 'module_db_version'
    modulename = Column(Unicode(128),primary_key=True)
    moduleversion = Column(Unicode(64),primary_key=True)
    dbversion = Column(Unicode(64))
    insertdt  = Column(DateTime,default=datetime.now,onupdate=datetime.now)

