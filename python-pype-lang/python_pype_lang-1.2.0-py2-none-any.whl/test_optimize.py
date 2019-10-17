'''
python3 test_optimize.py

Or, to test with updated optimized.py, from python-pype-lang:

./reinstall_from_source.sh ; python3 pype/test_optimize.py
'''
from pype import pype as p
from pype.optimize import optimize
from pype import _,_0,_1
from pype.vals import PypeVal as v
import numpy as np

def test_xedni_arg(ls):

    return p( 1,
              v(ls)[_])

def test_xedni_2_args(lsls):

    print(f'{v(lsls)[_,0]} is v(lsls)[_,0]')

    return p( 1,
              v(lsls)[_,0])

@optimize
def test_xedni_arg_opt(ls):

    return p( 1,
              v(ls)[_])


def test_xedni_arg_numpy(a):

    return p( 1,
              v(a)[_])


def test_xedni_arg_with_index_arg(ls):

    return p( [0,1],
              v(ls)[_0])


def test_xedni_2_arg(lsls):

    return p( 1,
              v(lsls)[_,0])


@optimize
def test_xedni_2_arg_opt(lsls):

    return p( 1,
              v(lsls)[_,0])

def test_index_arg(ls):

    return p( ls,
              _0)

@optimize
def test_index_arg_opt(ls):

    return p( ls,
              _0)


def test_bracket_index(ls):

    return p( ls,
              _[0],
           )

@optimize
def test_bracket_index_opt(ls):

    return p( ls,
              _[0],
           )


def test_bracket_dct(dct):

    return p( dct,
              _['a'],
            )


@optimize
def test_bracket_dct_opt(dct):

    return p( dct,
              _['a'],
            )


def test_dot_dct(dct):

    return p( dct,
              _.a,
            )


@optimize
def test_dot_dct_opt(dct):

    return p( dct,
              _.a,
            )


def test_obj_method(ob):

    return p( ob,
              _.method,
            )


@optimize
def test_obj_method_opt(ob):

    return p( ob,
              _.method,
            )


def test_obj_method_in_lambda(ob):

    return p( ob,
              (_.method_with_arg,1),
            )


@optimize
def test_obj_method_in_lambda_opt(ob):


    return p( ob,
              (_.method_with_arg,1),
            )


@optimize
def test_obj_method_in_lambda_opt(ob):

    return p( ob,
              (_.method_with_arg,1),
            )

def test_2d_numpy(npArray):

    return p( npArray,
              _[0,1])

@optimize
def test_2d_numpy_opt(npArray):

    return p( npArray,
              _[0,1])


def sm(x,y): return x+y


def test_lambda(z):

    return p( z,
              (sm,_,_+1))

@optimize
def test_lambda_opt(z):

    return p( z,
              (sm,_,1))


@optimize
def test_reduce_opt(ls):

    return p( ls,
              [(sm,),ls])


@optimize
def test_reduce_startval_opt(ls):

    return p( ls,
              [(sm,),10,ls])


def test_name_bookmark(y):

    return p( y,
              _+y)


@optimize
def test_n_bookmark_opt(y):

    z=y

    return p( y,
              z+1)


f=len

@optimize
def test_binop_opt(ls):

    y=1
    return p( ls,
              f+y)


@optimize
def test_no_pypeval_tuple_opt(ls):

    return p( ls,
              (f,_)+(f,_))


@optimize
def test_namebookmark_list_opt(ls):

    x=1

    return p( ls,
              _+[x])


'''
def test_no_return(ls):

    (f,_)+(f,_)
'''

if __name__=='__main__':

    print('*'*30)
    print('INDEX ARG')

    ls=[1,2,3,4]
    lsls=[[0,3,4],[1,2,3]]
    dct={'a':1,'b':2}
    a=np.array(lsls)

    class CallMe:

        def method(self):

            return 'hi'

        def method_with_arg(self,x):

            return f'***method with arg {x}***'

    ob=CallMe()

    print(f'{ls} is ls')
    print(f'{dct} is dct')
    print(f'{ob} is ob')

    print(f'{test_namebookmark_list_opt(ls)} is test_namebookmark_list_opt')
    '''
    print(f'{test_no_pypeval_tuple_opt(ls)} is test_no_pypeval_tuple_opt')
    print(f'{test_no_return(ls)} is test_no_return(ls)') 

    print(f'{test_binop_opt(ls)} is test_binop_opt')

    print(f'{test_name_bookmark(1)} is test_name_bookmark')
    print(f'{test_name_bookmark_opt(1)} is test_name_bookmark')

    print(f'{test_reduce_opt(ls)} is test_reduce_opt(ls)')
    print(f'{test_reduce_startval_opt(ls)} is test_reduce_startval_opt(ls)')

    print(f'{test_lambda(1)} is test_lambda(1)')
    print(f'{test_lambda_opt(1)} is test_lambda_opt(1)')

    print(f'{test_xedni_2_arg(lsls)} is test_index_2_arg')
    print(f'{test_xedni_2_arg_opt(lsls)} is test_index_2_arg_opt')

    print(f'{test_xedni_arg(ls)} is test_xedni_arg')

    print(f'{test_index_arg(ls)} is test_index_arg')
    print(f'{test_index_arg_opt(ls)} is test_index_arg')

    print(f'{test_bracket_dct(dct)} is test_bracket_index')
    print(f'{test_bracket_dct_opt(dct)} is test_bracket_index_opt')

    print(f'{test_dot_dct(dct)} is test_dot_index')
    print(f'{test_dot_dct_opt(dct)} is test_dot_index_opt')

    print(f'{test_obj_method(ob)} is test_obj_method(ob)') 
    print(f'{test_obj_method_opt(ob)} is test_obj_method_opt(ob)') 

    print(f'{test_obj_method_in_lambda(ob)} is test_obj_method_in_lambda(ob)') 
    print(f'{test_obj_method_in_lambda_opt(ob)} is test_obj_method_in_lambda_opt(ob)') 
    '''

    
