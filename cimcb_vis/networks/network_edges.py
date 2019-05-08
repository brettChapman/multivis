import pandas as pd
import numpy as np

#Note: matrix was originally including absolute RHO: abs(RHO.values[i_idx,j_idx]). But this was screwing up the assigned colors when using RHO weight.

def network_edges(nodes, RHO, PVAL, block1, block2, filtScoreType, level, sign):

    row, col = RHO.values.shape
           
    def rho(nodes, RHO, PVAL, block1, block2, level):
               
        rho_cols = RHO.columns
        rho_rows = RHO.index
        
        e = []

        for i_idx in range(0, len(rho_rows)):

            i = rho_rows[i_idx]

            for j_idx in range(i_idx, len(rho_cols)):

                j = rho_cols[j_idx]

                if(abs(RHO.values[i_idx,j_idx]) > level):
                    block1_nodes = nodes[nodes['group'] == block1]
                    block2_nodes = nodes[nodes['group'] == block2]

                    block1_indexes = list(block1_nodes.index)
                    block2_indexes = list(block2_nodes.index)

                    start_index = block1_indexes[i_idx]
                    end_index = block2_indexes[j_idx]

                    block1_nodeColors = list(block1_nodes['sig_color'].values)
                    block2_nodeColors = list(block2_nodes['sig_color'].values)

                    start_color = block1_nodeColors[i_idx]
                    end_color = block2_nodeColors[j_idx]

                    if start_index != end_index:
                        if PVAL is None:
                            b = [start_index, start_color, i, block1, end_index, end_color, j, block2, RHO.values[i_idx,j_idx], np.sign(RHO.values[i_idx,j_idx])];
                        else:
                            b = [start_index, start_color, i, block1, end_index, end_color, j, block2, RHO.values[i_idx,j_idx], np.sign(RHO.values[i_idx,j_idx]), PVAL.values[i_idx,j_idx]];
                    
                        e.append(b)
                    
        if PVAL is None:
            df_rho = pd.DataFrame(e, columns=['start_index', 'start_color', 'start', 'start_block', 'end_index', 'end_color', 'end', 'end_block', 'Rho', 'Sign'])
        else:
            df_rho = pd.DataFrame(e, columns=['start_index', 'start_color', 'start', 'start_block', 'end_index', 'end_color', 'end', 'end_block', 'Rho', 'Sign', 'Pval'])
                               
        return df_rho
        
    def pval(nodes, RHO, PVAL, block1, block2, level):

        rho_cols = RHO.columns
        rho_rows = RHO.index
        
        e = []
        #b = []

        for i_idx in range(0, len(rho_rows)):

            i = rho_rows[i_idx]

            for j_idx in range(0, len(rho_cols)):#range(i_idx, len(rho_cols)):

                j = rho_cols[j_idx]

                block1_nodes = nodes[nodes['group'] == block1]
                block2_nodes = nodes[nodes['group'] == block2]

                block1_indexes = list(block1_nodes.index)
                block2_indexes = list(block2_nodes.index)

                start_index = block1_indexes[i_idx]
                end_index = block2_indexes[j_idx]

                block1_nodeColors = list(block1_nodes['sig_color'].values)
                block2_nodeColors = list(block2_nodes['sig_color'].values)

                start_color = block1_nodeColors[i_idx]
                end_color = block2_nodeColors[j_idx]

                if start_index != end_index:
                    if PVAL is None:
                        b = [start_index, start_color, i, block1, end_index, end_color, j, block2, RHO.values[i_idx,j_idx], np.sign(RHO.values[i_idx,j_idx])];
                        e.append(b)
                    else:
                        if(PVAL.values[i_idx,j_idx] < level):
                            b = [start_index, start_color, i, block1, end_index, end_color, j, block2, RHO.values[i_idx,j_idx], np.sign(RHO.values[i_idx,j_idx]), PVAL.values[i_idx,j_idx]];
                            e.append(b)
        
        if PVAL is None:
            df_pval = pd.DataFrame(e, columns=['start_index', 'start_color', 'start', 'start_block', 'end_index', 'end_color', 'end', 'end_block', 'Rho', 'Sign'])
        else:
            df_pval = pd.DataFrame(e, columns=['start_index', 'start_color', 'start', 'start_block', 'end_index', 'end_color', 'end', 'end_block', 'Rho', 'Sign', 'Pval'])
                            
        return df_pval
    
    options = {'Rho': rho(nodes, RHO, PVAL, block1, block2, level), 'Pval': pval(nodes, RHO, PVAL, block1, block2, level)}
    
    df_edges = pd.DataFrame()
    
    if filtScoreType in options:
        df_edges = options[filtScoreType];
    else:
        print ("Error: wrong score type specified. Valid entries are 'Rho' and 'Pval'.")
    
    if sign == "POS":
        df_edges = df_edges[df_edges['Sign'] > 0].reset_index(drop=True)
    elif sign == "NEG":
        df_edges = df_edges[df_edges['Sign'] < 0].reset_index(drop=True)
    
    return df_edges