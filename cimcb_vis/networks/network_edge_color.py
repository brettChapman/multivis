import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
#from metaboplots.utils import range_scale

def get_colors(x, cmap):

    norm = matplotlib.colors.Normalize(vmin=x.min(), vmax=x.max())
    #norm = matplotlib.colors.Normalize(vmin=-1.0, vmax=1.0)

    #norm = plt.Normalize()
    return cmap(norm(x))

def network_edge_color(df_edges, link_type, edgeCmap):

    colorsHEX = []

    signs = df_edges['Sign'].values
    
    if "Pval" in df_edges.columns:
        df_edges_color = df_edges[['start_index', 'start_color', 'start', 'start_block', 'end_index', 'end_color', 'end', 'end_block', 'Rho', 'Pval']]
    else:
        df_edges_color = df_edges[['start_index', 'start_color', 'start', 'start_block', 'end_index', 'end_color', 'end', 'end_block', 'Rho']]

    if link_type == "Rho":

        for i in range(edgeCmap.N):
            colorsHEX.append(matplotlib.colors.rgb2hex(edgeCmap(i)[:3]))

        signColors = []
        for sign in signs:
            if sign > 0:
                signColors.append(colorsHEX[-1])
            else:
                signColors.append(colorsHEX[0])

        df_edges_color = df_edges_color.assign(color=pd.Series(signColors, index=df_edges_color.index))
    elif link_type == "Pval":

        if "Pval" in df_edges_color.columns:
                colorsRGB = get_colors(df_edges_color['Pval'].values, edgeCmap)[:, :3]
        else:
            print("Pval in not a column in this dataset. Now choosing Rho as a color scale.")
            colorsRGB = get_colors(df_edges_color['Rho'].values, edgeCmap)[:, :3]

            for rgb in colorsRGB:
                colorsHEX.append(matplotlib.colors.rgb2hex(rgb))

            df_edges_color = df_edges_color.assign(color=pd.Series(colorsHEX, index=df_edges_color.index))

    return df_edges_color