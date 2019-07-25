<img src="cimcb_logo.png" alt="drawing" width="400"/>

# multi-vis
multi-vis package containing the necessary tools for the visualisation of correlated data.

## Installation

### Dependencies
multi-vis requires:
- Python (>=3.5)
- NumPy (>=1.12)
- Pandas
- Matplotlib
- Seaborn
- Networkx
- SciPy
- Scikit-learn
- tqdm

### User installation
The recommend way to install cimcb_vis and dependencies is to using ``conda``:
```console
conda install -c brett.chapman cimcb_vis
```
or ``pip``:
```console
pip install cimcb_vis
```
Alternatively, to install directly from github:
```console
pip install https://github.com/brettChapman/multi-vis/archive/master.zip
```

### API
For further detail on the usage refer to the docstring.

#### multi-vis
- [Edge](https://github.com/brettChapman/multi-vis/blob/master/multi-vis/Edge.py): Generates dataframe of edges prior to visualisation.
- [Network](https://github.com/brettChapman/multi-vis/blob/master/multi-vis/Network.py) Generates dataframe of edges, with network parameters and a networkx graph prior to visualisation.
- [edgeBundle](https://github.com/brettChapman/multi-vis/blob/master/multi-vis/edgeBundle.py): Generates necessary Json structure and produces Hierarchical edge bundle plot.
- [plotNetwork](https://github.com/brettChapman/multi-vis/blob/master/multi-vis/plotNetwork.py): Static spring plot using pygraphviz and networkx.
- [forceNetwork](https://github.com/brettChapman/multi-vis/blob/master/multi-vis/forceNetwork.py): Interactive force-directed network which inherits data from the networkx graph
- [clustermap](https://github.com/brettChapman//multi-vis/blob/master/multi-vis/clustermap.py): Clustered heatmap with dendrograms.
- [polarDendrogram](https://github.com/brettChapman/multi-vis/blob/master/multi-vis/polarDendrogram.py): Polar dendrogram

#### multi-vis.utils
- [mergeBlocks](https://github.com/brettChapman/multi-vis/blob/master/multi-vis/utils/mergeBlocks.py): Merges multiply diffent blocks into a single peak table and data table.
- [range_scale](https://github.com/brettChapman/multi-vis/blob/master/multi-vis/utils/range_scale.py): Scales a range of values between user chosen values.
- [corrAnalysis](https://github.com/brettChapman/multi-vis/blob/master/multi-vis/corrAnalysis.py): Correlation analysis with Pearson, Spearman or Kendall's Tau.
- [cluster](https://github.com/brettChapman/multi-vis/blob/master/multi-vis/utils/spatialClustering.py): Clusters data using a linkage cluster method. If the data is correlated the correlations are first preprocessed, then clustered, otherwise a distance metric is applied to non-correlated data before clustering.

### License
multi-vis is licensed under the ___ license.

### Authors
- Brett Chapman
- https://scholar.google.com.au/citations?user=A_wYNAQAAAAJ&hl=en

### Correspondence
Dr. Brett Chapman, Post-doctoral Research Fellow at the Centre for Integrative Metabolomics & Computational Biology at Edith Cowan University.
E-mail: brett.chapman@ecu.edu.au

### Citation
If you would cite cimcb_vis in a scientific publication, you can use the following: ___
