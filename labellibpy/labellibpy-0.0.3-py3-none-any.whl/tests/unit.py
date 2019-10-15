from labellibpy.labellib import LabelService

def test_verify_stuff():
    havereturned = LabelService().getThese(['T002', 'T003'])
    assert havereturned.status_code == 200