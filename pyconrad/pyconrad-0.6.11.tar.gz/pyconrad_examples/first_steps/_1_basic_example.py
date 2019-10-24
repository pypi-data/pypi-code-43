
# Copyright (C) 2010-2017 - Andreas Maier
# CONRAD is developed as an Open Source project under the GNU General Public License (GPL-3.0)

import pyconrad.autoinit
import edu.stanford.rsl.tutorial.phantoms

phantom2d = edu.stanford.rsl.tutorial.phantoms.MickeyMouseGrid2D(100, 100)

from edu.stanford.rsl.conrad.phantom import NumericalSheppLogan3D
phantom3d = NumericalSheppLogan3D(100, 100, 100).getNumericalSheppLoganPhantom()

# You can also group Java packages an access all classes that are contained (import * does not work)
# Access more easily using ClassGetter (# type: pyconrad.AutoCompleteConrad adds static auto-complete feature for ClassGetter.edu)
_ = pyconrad.ClassGetter(
    'edu.stanford.rsl.tutorial.phantoms',
    'edu.stanford.rsl.conrad.phantom'
)  # type: pyconrad.AutoCompleteConrad

print('This is a Java class: ' + str(_.NumericalSheppLogan3D))

# Use Java method of class MickeyMouseGrid2D
phantom2d.show()
phantom3d.show()
