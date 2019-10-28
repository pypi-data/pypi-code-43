import matplotlib.pyplot as plt
import sys
import argparse
import MESA_Plotter._MESA_Plotter.MESA_Plotter as mp

plt.rcParams.update({'font.size': 20, 'axes.labelsize': 'large','xtick.labelsize': 'large','ytick.labelsize': 'large', 'xtick.major.size': 10,'xtick.major.width': 2,'ytick.major.size': 10,'ytick.major.width': 2,'ytick.minor.size': 5,'ytick.minor.width': 1,})


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser()

    parser.add_argument("x_axis", help="Variable to plot on x-axis. Use built_in to acces the built in plots like color magnitude diagramms.", type=str)
    parser.add_argument("y_axis", help="Variable to plot on y-axis. If x_axis==built_in, choose built in plot to generate (color_mag, color_mag_r_b)",  type=str)
    parser.add_argument("-z", "--z_axis", help="If this option is set, this variable is plotted as color code.", type=str, default= ' ')
    parser.add_argument("-fs", "--figsize",
                        help="Optional parameter to control the size of the plot.",
                        type=str, default="16,9")

    parser.add_argument("-c", "--colorLog", help="If this option is set, the color code will be log scaled", action='store_true')

    parser.add_argument("-min", "--minMass",
                        help="Defines the lowest mass of evolutionary tracks that will be plottet."
                        "Note: it takes the track which mass value is closest to this.", type=float, default=0.5)

    parser.add_argument("-max", "--maxMass",
                        help="Defines the highest mass of evolutionary tracks that will be plottet."
                        "Note: it takes the track which mass value is closest to this.", type=float, default=10.0)
    parser.add_argument("-ic", "--isochrones",
                        help="For each age in this list (age in Myrs), an isochron will be plottet", nargs='+', default=[])


    args = parser.parse_args(args)

    f_x = None if args.figsize.split(",")[0] == 'None' else float(args.figsize.split(",")[0])
    f_y = None if args.figsize.split(",")[1] == 'None' else float(args.figsize.split(",")[1])

    fig, ax = plt.subplots(1, figsize = (f_x, f_y))
    mp.plot_diagram(args.x_axis, args.y_axis, ax, fig, z_name=args.z_axis, mass_min=args.minMass, mass_max=args.maxMass, color_log=args.colorLog, isochrones =args.isochrones)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()

