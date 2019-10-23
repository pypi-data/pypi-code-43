class Conf():


    @classmethod
    def setup(cls,settings):
        cls.adminname   =settings.get("ppss_auth.adminname","admin")
        cls.adminpass   =settings.get("ppss_auth.adminpass","")
        cls.initdb = settings.get("ppss_auth.initdb","true").lower() == 'true'

        # routes
        cls.loginurl = settings.get("ppss_auth.login_url","/login")
        cls.logouturl = settings.get("ppss_auth.logout_url","/logout")

        cls.postlogoutroute = settings.get("ppss_auth.post_logout_route","home")
        cls.postloginroute = settings.get("ppss_auth.post_login_route","home")
        cls.postloginfollow = settings.get("ppss_auth.post_login_follow","true").lower() == 'true'
        
        cls.saltforhash = settings.get("ppss_auth.salt","ImTheSaltOfThisLife")

        cls.forbiddentologin = settings.get("ppss_auth.forbidden_to_login","true").lower() == 'true'


        #password enforcement
        cls.passwordpreviousdifferent = int(settings.get("ppss_auth.password_previuos_diff","3"))
        cls.passwordrelist = list(settings.get("ppss_auth.password_relist",["[A-Z]+","[a-z]+","[0-9]+","[!,.?\\/;:_-+*]+"]) )
        cls.passwordwrongmessage = 'La nuova password deve essere differente dalle precedenti 3 e avere almeno una maiuscola, una minuscola, un numero e un carattere fra "!,.?\\/;:_-+*".'

        #public templates
        cls.logintemplate = settings.get("ppss_auth.logintemplate","ppss_auth:/templates/login.mako")
        cls.changepasswordtemplate = settings.get("ppss_auth.changepasswordtemplate","ppss_auth:/templates/change.mako")
        cls.publictemplateinherit = settings.get("ppss_auth.publictemplateinherit","ppss_auth:/templates/layouts/public.mako")
        
        #bo template
        cls.listusertemplate = settings.get("ppss_auth.listusertemplate","ppss_auth:/templates/listuser.mako")
        cls.editusertemplate = settings.get("ppss_auth.editusertemplate","ppss_auth:/templates/edituser.mako")
        cls.listgrouptemplate = settings.get("ppss_auth.listgrouptemplate","ppss_auth:/templates/listgroup.mako")
        cls.editgrouptemplate = settings.get("ppss_auth.editgrouptemplate","ppss_auth:/templates/editgroup.mako")
        cls.listpermtemplate = settings.get("ppss_auth.listpermtemplate","ppss_auth:/templates/listperm.mako")
        cls.editpermtemplate = settings.get("ppss_auth.editpermtemplate","ppss_auth:/templates/editperm.mako")

        cls.botemplateinherit = settings.get("ppss_auth.botemplateinherit","ppss_auth:/templates/layouts/public.mako")
                

        #bo template inheritance
        cls.mastertemplateinherit = settings.get("ppss_auth.mastertemplateinherit","ppss_auth:/templates/layouts/masterlayout.mako")
        cls.sectiontemplateinherit = settings.get("ppss_auth.sectiontemplateinherit","ppss_auth:/templates/layouts/midlayout.mako")
        

        cls.testurl = settings.get("ppss_auth.testurl","/test")

        

        