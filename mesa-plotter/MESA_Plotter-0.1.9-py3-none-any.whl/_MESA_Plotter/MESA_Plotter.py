import matplotlib.colors as col
import numpy as np
import os
import json
import subprocess

def check_sshfs(path):
    if os.path.exists(os.path.join(path,"1","log_Teff.txt")):
        return

    command = f"sshfs endurance:/mnt/data/MESA_Plotter {path}"
    subprocess.check_call(command.split())

    if not os.path.exists(os.path.join(path,"1","log_Teff.txt")):
        raise IOError(f"Issue with sshfs, can't mount tracks to {path}")


def folder(mass):
    masses = np.linspace(np.log10(0.5),np.log10(10), 40)
    masses = 10**masses
    delta = np.inf
    out = 0
    for i in range(len(masses)):
        if abs(mass-masses[i]) < delta:
            delta = abs(mass-masses[i])
            out = i+1
    return out

def color_mag(path):
    bc_v = np.genfromtxt(path + f'/bc_V.txt')
    log_L = np.genfromtxt(path + f'/log_L.txt')
    mag_v = np.genfromtxt(path + f'/abs_mag_V.txt')
    mag_b = np.genfromtxt(path + f'/abs_mag_B.txt')
    return (mag_b - mag_v, 4.8 - 2.5 * log_L - bc_v, r'$(B - V)_0$', r'$M_v$')

def color_mag_r_b(path):
    bc_v = np.genfromtxt(path + f'/bc_V.txt')
    log_L = np.genfromtxt(path + f'/log_L.txt')
    mag_r = np.genfromtxt(path + f'/abs_mag_R.txt')
    mag_b = np.genfromtxt(path + f'/abs_mag_B.txt')
    return (mag_r - mag_b, 4.8 - 2.5 * log_L - bc_v, r'$(R - B)_0$', r'$M_v$')

def color_mag_b_r(path):
    bc_v = np.genfromtxt(path + f'/bc_V.txt')
    log_L = np.genfromtxt(path + f'/log_L.txt')
    mag_r = np.genfromtxt(path + f'/abs_mag_R.txt')
    mag_b = np.genfromtxt(path + f'/abs_mag_B.txt')
    return (mag_b - mag_r, 4.8 - 2.5 * log_L - bc_v, r'$(B - R)_0$', r'$M_v$')

def get_path():
    conf_file = os.path.join("~", ".MESAPlotter", "MESAPlotter.json")
    if os.path.exists(conf_file):
        with open(conf_file, 'r')as f:
            data_dict = json.load(f)
        return data_dict['sshfs_path']
    else:
        path = input("Please enter the full path for the MESA tracks:\n")
        while not os.path.exists(path):
            path = input("Path doesn't exist. Please enter the full path for the MESA tracks:\n")

        os.makedirs(os.path.join("~", ".MESAPlotter"))
        data_dict = {'sshfs_path': path}
        with open(conf_file, 'w') as f:
            json.dump(data_dict, f)
        return path


def plot_diagram(x_name, y_name, ax, fig, z_name = ' ', mass_min = 0.5, mass_max = 6.0, color_log = False, isochrones = []):
    masses = np.linspace(np.log10(0.5),np.log10(10), 40)
    masses = 10**masses
    path = get_path()
    start = folder(mass_min)
    end = folder(mass_max)
    labels= {'log_Teff': r'log$(T_\mathrm{eff})$', 'log_L': r'log$(L/L_\odot)$', 'log_g': r'log$(g)$', 'pp': 'log energy production by PP chain', 'cno': 'log energy production by CNO cycle',
             'star_age': 'age in years', }
    built_ins ={'color_mag': color_mag, 'color_mag_r_b': color_mag_r_b, 'color_mag_b_r': color_mag_b_r}

    x_sign = 1
    y_sign = 1
    if x_name in ['log_Teff']:
        x_sign = -1
    if y_name in ['log_g','color_mag', 'color_mag_r_b']:
        y_sign = -1

    if isochrones != []:
        steps= []
        for i in range(start, end+1):
            age = np.genfromtxt(path + f'/{i}/star_age.txt')
            stepslist = []
            for isos in range(len(isochrones)):
                isostep = -1
                for k in range(len(age)):
                    if age[k]>float(isochrones[isos])*10**6:
                        isostep = k
                        break
                stepslist.append(isostep)
            steps.append(stepslist)
    if z_name != ' ':
        all_x = []
        all_y = []
        all_z = []

    if isochrones != []:
        iso_data = {f'iso{isochrones[0]}': []}
        for k in range(1, len(isochrones)):
            iso_data[f'iso{isochrones[k]}'] = []

    for i in range(start, end+1):
        if x_name == 'built_in':
            x_value, y_value, xlabel, ylabel= built_ins[y_name](path + f'/{i}')
        else:
            x_value = np.genfromtxt(path + f'/{i}/{x_name}.txt')
            y_value = np.genfromtxt(path + f'/{i}/{y_name}.txt')

        if isochrones != []:
            for k in range(len(isochrones)):
                if steps[i-1][k] != -1:
                    iso_data[f'iso{isochrones[k]}'].append(x_value[steps[i-1][k]])
                    iso_data[f'iso{isochrones[k]}'].append(y_value[steps[i-1][k]])

        if z_name != ' ':
            z_value = np.genfromtxt(path + f'/{i}/{z_name}.txt')
            for k in range(len(z_value)):
                all_z.append(z_value[k])
                all_x.append(x_value[k])
                all_y.append(y_value[k])
        else:
            ax.plot(x_value, y_value, 'k-')
            pass

    if z_name != ' ':
        if color_log:
            scat = ax.scatter(all_x, all_y, c=all_z, s=10, cmap='jet', zorder=1, alpha=0.7, norm=col.LogNorm())
        else:
            scat = ax.scatter(all_x, all_y, c=all_z, s=10, cmap='jet', zorder=1, alpha=0.7)
        cbar = fig.colorbar(scat, ax=ax)
        try:
            cbar.set_label(labels[z_name])
        except:
            cbar.set_label(z_name)
    if isochrones != []:
        for k in range(len(isochrones)):
            ax.plot(iso_data[f'iso{isochrones[k]}'][::2], iso_data[f'iso{isochrones[k]}'][1::2], 'k--',lw = 1.5,  alpha = 0.7)
            ax.text(iso_data[f'iso{isochrones[k]}'][0]+x_sign*0.01*np.std(ax.set_xlim()), iso_data[f'iso{isochrones[k]}'][1], f'{isochrones[k]} Myr', fontsize = 'xx-small')

    else:
        pass
    if x_name in ['log_Teff']:
        ax.invert_xaxis()
    if y_name in ['log_g','color_mag', 'color_mag_r_b', 'color_mag_b_r']:
        ax.invert_yaxis()
    if y_name in ['color_mag_r_b']:
        ax.invert_xaxis()

    if x_name == 'built_in':
        ax.set_xlabel(xlabel)
    else:
        try:
            ax.set_xlabel(labels[x_name])
        except:
            ax.set_xlabel(x_name)
    if x_name == 'built_in':
        ax.set_ylabel(ylabel)
    else:
        try:
            ax.set_ylabel(labels[y_name])
        except:
            ax.set_ylabel(y_name)