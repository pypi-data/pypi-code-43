from numpy import zeros, array_equal

from ubcs_auxiliary import save_object, load_object

def test_save_load(tmpdir):
    arr_in = zeros((10,5))
    str_in = 'this is string'
    dict_in = {'1':1,'2':2}
    list_in = [1,2,3,4]
    compound_in = {}
    compound_in['arr'] = arr_in
    compound_in['str'] = str_in
    compound_in['dict'] = dict_in
    compound_in['list'] = list_in

    # save to a file
    save_object(tmpdir+'arr.extension',arr_in)
    save_object(tmpdir+'str.extension',str_in)
    save_object(tmpdir+'dict.extension',dict_in)
    save_object(tmpdir+'list.extension',list_in)
    save_object(tmpdir+'compound.extension',compound_in)

    # Load to a file
    arr_out = load_object(tmpdir+'arr.extension')
    str_out = load_object(tmpdir+'str.extension')
    dict_out = load_object(tmpdir+'dict.extension')
    list_out = load_object(tmpdir+'list.extension')
    compound_out = load_object(tmpdir+'compound.extension')

    #run tests
    assert array_equal(arr_in, arr_out)
    assert str_in == str_out
    assert dict_in == dict_out
    assert list_in == list_out
    assert compound_in.keys() == compound_out.keys()
