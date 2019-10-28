import locale
import matplotlib.pyplot as plt
import numpy as np

from helpers import assert_equality


def plot():
    plt.ticklabel_format(useLocale=True)

    x = np.arange(0, 8, 1)
    y = np.arange(0, 8, 1)
    x, y = np.meshgrid(x, y)
    z = x * y / 1000

    fig = plt.imshow(z)
    plt.colorbar()
    return fig


def test():
    locale.setlocale(locale.LC_NUMERIC, "de_DE.UTF-8")
    assert_equality(plot, "test_locale_de_reference.tex")
    locale.setlocale(locale.LC_NUMERIC, (None, None))
    return


if __name__ == "__main__":
    import helpers

    helpers.compare_mpl_latex(plot)
    # helpers.print_tree(plot())
