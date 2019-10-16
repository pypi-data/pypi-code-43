from pype import pype as p,_
from pype.vals import PypeVal as v
from pype.vals import NameBookmark

if __name__=='__main__':

    print('*'*30)
    print('v(_)+v(v(NameBookmark("a")))')
    print(v(_)+v(v(v(NameBookmark("a")))))
    print(p(1,v(_)+v(v(NameBookmark("a")))))

    '''
    print('*'*30)
    print('v(_)+v(v(1))')
    print(v(_)+v(v(1)))
    print(p(1,v(_)+v(v(1))))

    print('*'*30)
    print('v(_)+1')
    print(v(_)+1)
    print(p(1,v(_)+1))

    print('*'*30)
    print('v(_)+v(1)')
    print(v(_)+v(1))
    print(p(1,v(_)+v(1)))

    print('*'*30)
    print('v(_)+v(v(1))')
    print(v(_)+v(v(1)))
    print(p(1,v(_)+v(v(1))))

    print('*'*30)
    print('_+v(1)+v(1)')
    print(p(1,_+v(1)+v(1)))
    '''
