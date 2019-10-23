'''
This toolbox contens some basic developing methods,
including:
integrated printing method;
'''
import numpy as np
import matplotlib.pyplot as plt
np.set_printoptions(threshold=np.inf, linewidth=np.inf)


class Print_Tool:
    '''
    By inputing [name] and [value] of a Var, to output the basic info.
    '''
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

class Plot_Tool:
    @staticmethod
    def Integrated_Plot(**kwargs):
        '''
        By inputing [name] and [value] of 2/3 vars [value0, value1, (value2)], to plot the lines of 2/3 vars and the error between them.\n
        \t\t a, b, c should be columns-like\n
        \t\t example:\n
        \t\t Plot_Tool.Integrated(value0=a, value1=b, value2=c, bins=500, names=['a', 'b', 'c'])\n
        '''
        def plot3Vars(value0, value1, value2, names, bins):
            error1, error2 = np.subtract(value0, value1), np.subtract(value0, value2)
            plt.subplot(411)
            plt.plot(value0, label=names[0])
            plt.legend()
            plt.subplot(412)
            plt.plot(value1, label=names[1])
            plt.legend()
            plt.subplot(413)
            plt.plot(value2, label=names[2])
            plt.legend()
            plt.subplot(427)
            plt.hist(error1, label=names[0] + '-' + names[1], bins=bins)
            plt.legend()
            plt.subplot(428)
            plt.hist(error2, label=names[0] + '-' + names[2], bins=bins)
            plt.legend()
            plt.show()

        def plot2Vars(value0, value1, names, bins):
            error1 = np.subtract(value0, value1)
            plt.subplot(311)
            plt.plot(value0, label=names[0])
            plt.legend()
            plt.subplot(312)
            plt.plot(value1, label=names[1])
            plt.legend()
            plt.subplot(313)
            plt.hist(error1, label=names[0] + '-' + names[1], bins=bins)
            plt.legend()
            plt.show()

        if 'names' in kwargs:
            names = kwargs['names']
            bins = kwargs['bins']
            if len(kwargs) == 5:
                varNames = ['value0', 'value1', 'value2']
                value0, value1, value2 = [np.reshape(kwargs[var], (-1, 1)) for var in varNames]
                plot3Vars(value0, value1, value2, names, bins)
            elif len(kwargs) == 4:
                varNames = ['value0', 'value1']
                value0, value1 = [np.reshape(kwargs[var], (-1, 1)) for var in varNames]
                plot2Vars(value0, value1, names, bins)
        else:
            bins = kwargs['bins']
            names = ['value0', 'value1', 'value2']
            if len(kwargs) == 4:
                varNames = ['value0', 'value1', 'value2']
                value0, value1, value2 = [np.reshape(kwargs[var], (-1, 1)) for var in varNames]
                plot3Vars(value0, value1, value2, names, bins)
            elif len(kwargs) == 3:
                varNames = ['value0', 'value1']
                value0, value1 = [np.reshape(kwargs[var], (-1, 1)) for var in varNames]
                plot2Vars(value0, value1, names, bins)
