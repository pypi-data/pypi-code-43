import numpy as np
np.set_printoptions(threshold=np.inf, linewidth=np.inf)


class Print_Tool:
    @staticmethod
    def Integrated_Print(name, value):
        print(' 【变量名  name 】', name, '\n',
              '【数  值 value 】', value, '\n',
              '【尺  寸 shape 】', np.shape(value), '\n',
              '【类  型  type 】', type(value))
        try:
            print(
                ' 【最大值  max  】', max(value), '\n',
                '【最小值  min  】', min(value), '\n',
                '【均  值  mean 】', np.mean(value), '\n',
                '【中  值 median】', np.median(value), '\n')
        except:
            pass
