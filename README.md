<img src="cimcb_logo.png" alt="drawing" width="400"/>

# cimcb_vis
cimcb_vis package containing the necessary tools for the visualisation of different Omics data.

## Installation

### Dependencies
cimcb_vis requires:
- Python (>=3.5)
- NumPy (>=1.12)
- SciPy
- scikit-learn
- Pandas
- matplotlib
- seaborn
- networks
- cimcb

### User installation
The recommend way to install cimcb_vis and dependencies is to using ``conda``:
```console
conda install -c brettChapman cimcb_vis
```
or ``pip``:
```console
pip install cimcb_vis
```
Alternatively, to install directly from github:
```console
pip install https://github.com/brettChapman/cimcb_vis/archive/master.zip
```

### API
For further detail on the usage refer to the docstring.

#### cimcb_vis
- [clustermap](https://github.com/brettChapman/cimcb_vis/blob/master/cimcb_vis/clustermap.py#L14-L36): HCA with dendrograms.
- [corrAnalysis](https://github.com/brettChapman/cimcb_vis/blob/master/cimcb_vis/corrAnalysis.py#L8-L29): Correlation analysis with Spearman or Pearson.
- [network](https://github.com/brettChapman//cimcb_vis/blob/master/cimcb_vis/network.py#L8-L9): Generates network structures prior to visualisations.
- [edgeBundle](https://github.com/brettChapman/cimcb_vis/blob/master/cimcb_vis/edgeBundle.py#L8-L29): Hierarchical edge bundle plot.
- [graphviz_plotNetwork](https://github.com/brettChapman/cimcb_vis/blob/master/cimcb_vis/graphviz_plotNetwork.py#L8-L9): Static spring plot using pygraphviz.
- [interactiveNetwork](https://github.com/brettChapman/cimcb_vis/blob/master/cimcb_vis/interactiveNetwork.py#L8-L9): Interactive spring plot.

#### cimcb_vis.networks
- [network_edges](https://github.com/brettChapman/cimcb_vis/blob/master/cimcb_vis/networks/network_edges.py#L8-L18): Generates a dataframe of all network edges.
- [network_edge_color](https://github.com/brettChapman/cimcb_vis/blob/master/cimcb_vis/networks/network_edge_color.py#L6-L16): Assigns a colour based on correlation coefficient or p-value to each of the edges in the dataframe.

#### cimcb_vis.utils
- [df_to_Json](https://github.com/brettChapman/cimcb_vis/blob/master/cimcb_vis/utils/df_to_Json.py#L5-L23): Generates a Json data structure from an edges dataframe.
- [mergeBlocks](https://github.com/brettChapman/cimcb_vis/blob/master/cimcb_vis/utils/mergeBlocks.py#L6-L28): Merges multiply Omics blocks into a single peak table and data table.
- [range_scale](https://github.com/brettChapman/cimcb_vis/blob/master/cimcb_vis/utils/range_scale.py#L7-L22): Scales a range of values between a sets of user chosen values.
- [spatialClustering](https://github.com/brettChapman/cimcb_vis/blob/master/cimcb_vis/utils/spatialClustering.py#L7-L29): Spatially clusters a matrix based on a user chosen distance metric clustering method.

### License
cimcb_vis is licensed under the ___ license.

### Authors
- Brett Chapman
- https://scholar.google.com.au/citations?user=A_wYNAQAAAAJ&hl=en

### Correspondence
Dr. Brett Chapman, Post-doctoral Research Fellow at the Centre for Integrative Metabolomics & Computational Biology at Edith Cowan University.
E-mail: brett.chapman@ecu.edu.au

### Citation
If you would cite cimcb_vis in a scientific publication, you can use the following: ___