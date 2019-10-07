from __future__ import division

def initialize():
    import common
    import codegen
    codegen.initialize()
    if common.use_gui:
        import floatspin_editor
        return floatspin_editor.initialize()
