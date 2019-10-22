# vis.py
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.cluster import KMeans
from math import pi

class vis:
    def k_means_pp(features, num_clusters):
        kmeans = KMeans(n_clusters=num_clusters, random_state=0, init='k-means++', ).fit(X)
        features['cluster_labels'] = kmeans.labels_
        return features

    def create_columns(features):
        '''
        create feature column hour_minite,

        '''
        features['h_m'] = features.timestamp.apply(lambda x: datetime.fromtimestamp(x).time().strftime('%H:%M'))
        return features

    def dense_scatter(features, figsize=(15,15), dot_size = 2):
        '''
        this function is used for dense plot
        args: features -- pandas DataFrame
            figsize -- figure size to set
            dot_size -- the size for each dot
        out:
            matplotlib plot
        '''
        fig,ax= plt.subplots(figsize = figsize)

        # scatter
        ax.scatter(x=features["h_m"].values,
                   y=features["date"].values,
                   c=features["cluster_labels"].values,
                  s = 2)

        ax.xaxis.set_major_locator(ticker.MultipleLocator(60))
        ax.set_ylim((features["date"].min(), features["date"].max()))

    def radar_plot(features, figsize=(15,15)):
        '''
        this function is used for dense plot
        args: features -- pandas DataFrame
            figsize -- figure size to set
        out:
            matplotlib plot
        '''
        values = radar_mean_spl.mean_spl.values.tolist()
        values += values[:1]

        # number of variable
        categories=list(range(1,9))
        N = len(categories)

        # What will be the angle of each axis in the plot? (we divide the plot / number of variable)
        angles = [n / float(N) * 2 * pi for n in range(N)]
        angles += angles[:1]

        # Initialise the spider plot
        plt.figure(figsize = figsize)
        ax = plt.subplot(111, polar=True)

        # Draw one axe per variable + add labels labels yet
        plt.xticks(angles[:-1], categories, color='grey', size=16)

        # Draw ylabels
        ax.set_rlabel_position(0)
        plt.yticks([58,64,70], ["58","64","70"], color="grey", size=14)
        plt.ylim(56,72)
        plt.title('mean spl vs. clusters')
        # Plot data
        ax.plot(angles, values, linewidth=1, linestyle='solid')

        # Fill area
        ax.fill(angles, values, 'b', alpha=0.1)

    def polar_plot(features, day_to_plot, figsize = (15,15)):
        '''
        this function is used for polar plot
        args: features -- pandas DataFrame
            day_to_plot -- select which day to plot
            figsize -- figure size to set
        out:
            matplotlib plot
        '''
        date_feature = features[features.date == day_to_plot]
        date_feature['hour'] = date_feature.h_m.apply(lambda x: x.split(':')[0])
        # Fixing random state for reproducibility
        # np.random.seed(19680801)

        # Compute pie slices
        N = len(date_feature)
        theta, width = np.linspace(0.0, 2 * np.pi, N, endpoint=False, retstep=True)
        colors = date_feature.cluster_labels

        plt.figure(figsize = figsize)
        ax = plt.subplot(111, polar=True)
        for i in range(1,9):
            target = date_feature.apply(lambda x: x.mean_spl if x.cluster_labels == i else 0, axis = 1).values
            bars = ax.bar(
                theta, target,
                width=width-0.01,
                label = 'cluster '+str(i)
            #     bottom=50,
        #         color=i
            )
        plt.legend()

        # bars = ax.bar(
        #     theta, [3000]*24,
        #     width=width-0.03,
        #     bottom=bottom,
        #     color="#f39c12", alpha=0.2
        # )

        ax.set_theta_zero_location("N")
        ax.set_theta_direction(-1)
        ax.grid(False)
        ax.spines['polar'].set_visible(False)
        ax.set_rlim(55, 75)
        ax.set_rticks(np.arange(55,75,5))

        plt.title('spl of different clusters in time slots')
        ticks = [f"{i}:00" for i in range(0, 24, 3)]
        ax.set_xticklabels(ticks)
        _ = ax
