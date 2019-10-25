''' Functions to convert string case

History:
10-30-2013 - 1.0.0 - Stephen Funkhouser
    Created
'''
__version__ = '1.0.0'


def nearly_equal(a, b, sig_fig=5):
    ''' determine if a & b are nearly equal to one another.

    @param sig_fig values must be equal through this value.

    examples:
        sig_fig==4 : (10.00000 == 10.00001) == True
        sig_fig==4 : (10.0000  == 10.0001) == False

    Probably not perfectly implemented, but reasonable start

    Look at http://floating-point-gui.de/errors/comparison/
        public static boolean nearlyEqual(float a, float b, float epsilon) {
            final float absA = Math.abs(a);
            final float absB = Math.abs(b);
            final float diff = Math.abs(a - b);

            if (a == b) { // shortcut, handles infinities
                return true;
            } else if (a == 0 || b == 0 || diff < Float.MIN_NORMAL) {
                // a or b is zero or both are extremely close to it
                // relative error is less meaningful here
                return diff < (epsilon * Float.MIN_NORMAL);
            } else { // use relative error
                return diff / (absA + absB) < epsilon;
            }
        }
    '''
    return (a == b or
            int(a * 10 ** sig_fig) == int(b * 10 ** sig_fig)
            )
