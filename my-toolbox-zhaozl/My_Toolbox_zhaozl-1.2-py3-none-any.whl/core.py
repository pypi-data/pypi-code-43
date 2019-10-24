import numpy as np
import matplotlib.pyplot as plt
np.set_printoptions(threshold=np.inf, linewidth=np.inf)
"""
This toolbox contents some basic methods can be used during developing progress.
【Methods】
1.  Print_Tool.Integrated_Print
2.  Plot_Tool.Multi_Plot

"""


class Print_Tool:
    @staticmethod
    def Integrated_Print(name, value):
        import numpy as np
        """
        By inputing [name] and [value] of a vars like ['name', value], to print the basic info of this Var.

        【example】:
            Print_Tool.Integrated_Print('name', value)

        *   value can be string or scaler data or the mixed of them.
        """
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
    def Multi_Plot(**kwargs):
        import matplotlib.pyplot as plt
        import numpy as np
        """
        By inputing [name] and [value] of vars like [measured, predicted_1, predicted_2, predicted_3],
        to plot the lines of input vars and the error distribution lines between them.

        【example】:
            Plot_Tool.Multi_Plot(value0=a, value1=b, value2=c, value3=d, bins=500, names=['a', 'b', 'c', 'd'])

        *   a, b, c, d should be columns-like
        """
        def Error_Limit(a1, b1, error):
            x_offset = 0.01
            fontsize = 8
            # ===== 作均值线 ===== #
            mu1 = np.mean(error)
            sigma = np.std(error)
            plt.plot([mu1, mu1], [0, 1], 'r-.')
            plt.annotate(' mu=%2.4f;\n sigma=%2.4f' % (mu1, sigma), (mu1 + x_offset, 0.05), fontsize=fontsize)
            # ===== 作左方差线 ===== #
            locCache_x = b1[np.where(b1 <= mu1 - sigma)[-1][-1]]
            locCache_y = a1[np.where(b1 <= mu1 - sigma)[-1][-1]]
            plt.plot([locCache_x, locCache_x], [0.5, 0], color='black', linestyle=':')
            plt.annotate(' sigma=%2.4f;\n P=%2.4f' % (locCache_x, locCache_y), (locCache_x + x_offset, 0.5), fontsize=fontsize)
            try:
                locCache_x = b1[np.where(b1 <= mu1 - 2 * sigma)[-1][-1]]
                locCache_y = a1[np.where(b1 <= mu1 - 2 * sigma)[-1][-1]]
                plt.plot([locCache_x, locCache_x], [0.25, 0], color='black', linestyle=':')
                plt.annotate(' sigma=%2.4f;\n P=%2.4f' % (locCache_x, locCache_y), (locCache_x + x_offset, 0.25), fontsize=fontsize)
                locCache_x = b1[np.where(b1<=mu1-3*sigma)[-1][-1]]
                locCache_y = a1[np.where(b1<=mu1-3*sigma)[-1][-1]]
                plt.plot([locCache_x, locCache_x], [0.125, 0], color='black', linestyle=':')
                plt.annotate(' sigma=%2.4f;\n P=%2.4f' % (locCache_x, locCache_y), (locCache_x+x_offset, 0.125), fontsize=fontsize)
            except:
                pass
            # ===== 作右方差线 ===== #
            locCache_x = b1[np.where(b1 >= mu1 + sigma)[0][0]]
            locCache_y = a1[np.where(b1 >= mu1 + sigma)[0][0]]
            plt.plot([locCache_x, locCache_x], [0.5, 1], color='black', linestyle=':')
            plt.annotate(' sigma=%2.4f;\n P=%2.4f' % (locCache_x, locCache_y), (locCache_x + x_offset, 0.5), fontsize=fontsize)
            try:
                locCache_x = b1[np.where(b1 >= mu1 + 2 * sigma)[0][0]]
                locCache_y = a1[np.where(b1 >= mu1 + 2 * sigma)[0][0]]
                plt.plot([locCache_x, locCache_x], [0.75, 1], color='black', linestyle=':')
                plt.annotate(' sigma=%2.4f;\n P=%2.4f' % (locCache_x, locCache_y), (locCache_x + x_offset, 0.75),
                             fontsize=fontsize)
                plt.subplots_adjust(left=0.03, bottom=0.03, right=0.97, top=0.97, wspace=0.12, hspace=0.3)
                locCache_x = b1[np.where(b1>=mu1+3*sigma)[0][0]]
                locCache_y = a1[np.where(b1>=mu1+3*sigma)[0][0]]
                plt.plot([locCache_x, locCache_x], [0.95, 1], color='black', linestyle=':')
                plt.annotate(' sigma=%2.4f;\n P=%2.4f' % (locCache_x, locCache_y), (locCache_x+x_offset, 1), fontsize=fontsize)
            except:
                pass
            plt.subplots_adjust(left=0.03, bottom=0.03, right=0.97, top=0.97, wspace=0.12, hspace=0.1)


        def plot4Vars(value0, value1, value2, value3, names, bins):
            error1, error2, error3 = np.subtract(value0, value1), np.subtract(value0, value2), np.subtract(value0, value3)
            plt.subplot(311)
            plt.plot(value0, 'k-', linewidth=2)
            plt.plot(value1, 'r:', linewidth=1, alpha=0.8)
            plt.plot(value2, 'm:', linewidth=1, alpha=0.8)
            plt.plot(value3, 'g:', linewidth=1, alpha=0.8)
            plt.legend(names)
            plt.subplot(334)
            plt.hist(error1, label=names[0] + '-' + names[1], bins=bins, color='r')
            plt.legend()
            plt.subplot(335)
            plt.hist(error2, label=names[0] + '-' + names[2], bins=bins, color='m')
            plt.legend()
            plt.subplot(336)
            plt.hist(error3, label=names[0] + '-' + names[3], bins=bins, color='g')
            plt.legend()

            plt.subplot(337)
            a1, b1, _ = plt.hist(error1, bins, cumulative=True, histtype='step', normed=True, color='r')
            Error_Limit(a1, b1, error1)
            plt.legend([names[0] + '-' + names[1]])
            plt.subplot(338)
            a1, b1, _ = plt.hist(error2, bins, cumulative=True, histtype='step', normed=True, color='m')
            Error_Limit(a1, b1, error2)
            plt.legend([names[0] + '-' + names[2]])
            plt.subplot(339)
            a1, b1, _ = plt.hist(error3, bins, cumulative=True, histtype='step', normed=True, color='g')
            Error_Limit(a1, b1, error3)
            plt.legend([names[0] + '-' + names[3]])

            plt.show()

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
            if len(kwargs) == 6:
                varNames = ['value0', 'value1', 'value2', 'value3']
                value0, value1, value2, value3 = [np.reshape(kwargs[var], (-1, 1)) for var in varNames]
                plot4Vars(value0, value1, value2, value3, names, bins)
            elif len(kwargs) == 5:
                varNames = ['value0', 'value1', 'value2']
                value0, value1, value2 = [np.reshape(kwargs[var], (-1, 1)) for var in varNames]
                plot3Vars(value0, value1, value2, names, bins)
            elif len(kwargs) == 4:
                varNames = ['value0', 'value1']
                value0, value1 = [np.reshape(kwargs[var], (-1, 1)) for var in varNames]
                plot2Vars(value0, value1, names, bins)
        else:
            bins = kwargs['bins']
            names = ['value0', 'value1', 'value2', 'value3']
            if len(kwargs) == 5:
                varNames = names
                value0, value1, value2, value3 = [np.reshape(kwargs[var], (-1, 1)) for var in varNames]
                plot4Vars(value0, value1, value2, value3, names, bins)
            elif len(kwargs) == 4:
                varNames = names[0:3]
                value0, value1, value2 = [np.reshape(kwargs[var], (-1, 1)) for var in varNames]
                plot3Vars(value0, value1, value2, names, bins)
            elif len(kwargs) == 3:
                varNames = names[0:2]
                value0, value1 = [np.reshape(kwargs[var], (-1, 1)) for var in varNames]
                plot2Vars(value0, value1, names, bins)