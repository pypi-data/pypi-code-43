from conlog import Conlog


from .EnvVar import EnvVar

def test_all_instance():
    conlog = Conlog(__name__, Conlog.DEBUG, enabled=True)

    env_var = conlog.new(EnvVar, {'ping': 'pong'})
    env_var.setVar('test', 'foo')
    env_var.getVar('test')

def test_one_instance():
    pass