# MultiVis
The MultiVis package contains the necessary tools for visualisation of multivariate data.

## Installation

### Dependencies
multivis requires:
- Python (>=3.5)
- NumPy (>=1.12)
- Pandas
- Matplotlib
- Seaborn
- Networkx
- SciPy
- Scikit-learn
- tqdm
- xlrd

### User installation
The recommend way to install cimcb_vis and dependencies is to using ``conda``:
```console
conda install -c brett.chapman multivis
```
or ``pip``:
```console
pip install multivis
```
Alternatively, to install directly from github:
```console
pip install https://github.com/brettChapman/multivis/archive/master.zip
```

### API
For further detail on the usage refer to the docstring.

#### multivis
- [Edge](https://github.com/brettChapman/multivis/blob/master/multivis/Edge.py#L7-L429): Generates dataframe of nodes and edges.
	- [init_parameters](https://github.com/brettChapman/multivis/blob/master/multivis/Edge.py#L24-L33)
		- [peaktable] : Pandas dataframe containing peak data.
		- [scores] : Pandas dataframe containing correlation coefficients.
		- [pvalues] : Pandas dataframe containing correlation pvalues.
	- [methods](https://github.com/brettChapman/multivis/blob/master/multivis/Edge.py#L35-54)
		- [set_params] : Set parameters - filter score type, hard threshold, internal correlation flag and sign type
		- [run] : Builds the nodes and edges
		- [getNodes] : Returns a Pandas dataframe of all nodes.
		- [getEdges] : Returns a Pandas dataframe of all edges.

- [Network](https://github.com/brettChapman/multivis/blob/master/multivis/Network.py#L6-L109): Inherits from Edge and generates dataframe of nodes and edges, and a networkx graph.
	- [init_parameters](https://github.com/brettChapman/multivis/blob/master/multivis/Network.py#L25-L29)
		- [peaktable] : Pandas dataframe containing peak data.
		- [scores] : Pandas dataframe containing correlation coefficients.
		- [pvalues] : Pandas dataframe containing correlation pvalues.
	- [methods](https://github.com/brettChapman/multivis/blob/master/multivis/Network.py#L31-L51)
		- [set_params] : Set parameter - filter score type, hard threshold, internal correlation flag and sign type.
                - [run] : Builds nodes, edges and NetworkX graph.
                - [getNetworkx] : Returns a NetworkX graph.
                - [getLinkType] : Returns the link type parameter used in building the network.

- [edgeBundle](https://github.com/brettChapman/multivis/blob/master/multivis/edgeBundle.py#L9-L1304): Generates and displays a Hierarchical edge bundle plot.
	- [init_parameters](https://github.com/brettChapman/multivis/blob/master/multivis/edgeBundle.py#L23-27)
		- [edges] : Pandas dataframe containing edges generated from Edge.
	- [methods](https://github.com/brettChapman/multivis/blob/master/multivis/edgeBundle.py#L29-L99)
		- [set_params] : Set parameters - diameter: Sets the diameter of the plot
						- innerRadiusOffset: Sets the inner radius based on the offset value from the diameter
						- groupSeparation : Value to set the distance between different segmented groups
						- linkFadeOpacity: The link fade opacity when hovering over/clicking nodes
						- mouseOver: Setting to 'True' swaps from clicking to hovering over nodes to select them
						- fontSize: The font size set to each node
						- backgroundColor: Set the background colour of the plot
						- foregroundColor: Set the foreground colour of the plot
						- filterOffSet: Set the position offset for the sliders
						- color_scale: Set the values to colour the edges by. Either 'Score or 'Pvalue'
						- edge_cmap: Set the CMAP colour palette to use for colouring the edges 
		- [run] : Generates and outputs the hierarchical edge bundle.
		
- [plotNetwork](https://github.com/brettChapman/multivis/blob/master/multivis/plotNetwork.py#L12-L346): Generates and displays a static NetworkX graph given a user defined layout.
	- [init_parameters](https://github.com/brettChapman/multivis/blob/master/multivis/plotNetwork.py#L26-L32)
		- [g] : NetworkX graph.
	- [methods](https://github.com/brettChapman/multivis/blob/master/multivis/plotNetwork.py#L34-L191)
		- [set_params] : Set parameters - node_params: node parameters dictionary(
											- sizing_column: node sizing coloumn
											- sizeScale: node size scale function ("linear", "reverse_linear", "log", "reverse_log", "square", "reverse_square", "area", "reverse_area", "volume", "reverse_volume")
											- size_range: Tuple of length 2 - minimum size to maximum size
											- alpha: Node opacity value
											- nodeLabels: Setting to 'True' will label the nodes
											- fontSize: The font size set to each node
											- keepSingletons: Setting to 'True' will keep any single nodes not connected in the NetworkX graph)
 						- filter_params: filter parameters dictionary(
											- column: Column from Peak Table to filter on
											- threshold: Value to filter on
											- operator: The comparison operator to use when filtering
											- sign: The sign of the correlation to filter on ("pos", "neg" or "both")
						- imageFileName: file name to save image to
						- edgeLabels - Setting to 'True' labels all edges with the correlation value
						- saveImage - Setting to 'True' will save the image to file
						- layout = Set the NetworkX layout type ("circular", "kamada_kawai", "random", "spring", "spectral")
						- dpi : The number of Dots Per Inch (DPI) for the image
						- figSize : The figure size as a tuple (width,height)
		- [run] : Generates and displays the NetworkX graph.

- [springNetwork](https://github.com/brettChapman/multivis/blob/master/multivis/springNetwork.py): Interactive spring-embedded network which inherits data from the NetworkX graph.
	- [init_parameters](https://github.com/brettChapman/multivis/blob/master/multivis/springNetwork.py#L9-L1015)
		- [g] : NetworkX graph.
	- [methods](https://github.com/brettChapman/multivis/blob/master/multivis/springNetwork.py#L36-L101)
		- [set_params] : Set parameters - node_params: node parameters dictionary(
											- node_text_size: The text size for each node
											- fix_nodes: Setting to 'True' will fix nodes in place when manually moved
											- displayLabel: Setting to 'True' will set the node labels to the 'Label' column, otherwise it will set the labels to the 'Name' column from the Peak Table
											- node_size_scale: node size scale dictionary(
																- Peak Table columns as index: dictionary(
																					- scale: ("linear", "reverse_linear", "log", "reverse_log", "square", "reverse_square", "area", "reverse_area", "volume", "reverse_volume")
																					- range: a number array of length 2 - minimum size to maximum size))
						- link_params: link parameters dictionary(
											- link_type: The link type used in building the network
											- link_width: The width of the links
											- link_score_color: dictionary(
															- positive: Colour values. Can be HTML/CSS name, hex code, and (R,G,B) tuples
															- negative: Colour values. Can be HTML/CSS name, hex code, and (R,G,B) tuples)
											- backgroundColor: Set the background colour of the plot
											- foregroundColor: Set the foreground colour of the plot
											- canvas_size: The canvas size as a tuple (width,height)
											- chargeStrength: The charge strength of the spring-embedded network (charged directed-force)
		- [run] : Generates and returns JavaScript embedded HTML code for writing to HTML and displaying the Spring-embededded network (SEN) plot.

- [clustermap](https://github.com/brettChapman//multivis/blob/master/multivis/clustermap.py): Hierarchical Clustered Heatmap.
	- [init_parameters](https://github.com/brettChapman//multivis/blob/master/multivis/clustermap.py#L29-L39)
		- [scores] : Pandas dataframe containing similarity scores (e.g. correlation coefficients or Euclidean distance values).
		- [row_linkage] : Precomputed linkage matrix for the rows from a linkage clustered scores matrix
		- [col_linkage] : Precomputed linkage matrix for the columns from a linkage clustered scores matrix
	- [methods](https://github.com/brettChapman//multivis/blob/master/multivis/clustermap.py#L41-L331)
		- [set_params] : Set parameters - imageFileName: file name to save image to
						- saveImage: Setting to 'True' will save the image to file
						- dpi: The number of Dots Per Inch (DPI) for the image
						- figSize: The figure size as a tuple (width,height)
						- dendrogram_ratio_shift: The ratio to shift the proportion the dendrogram takes
						- fontSize: The font size for all axes
						- heatmap_params: heatmap parameters dictionary(
												- xLabels: X axis labels
												- yLabels: Y axis labels
												- heatmap_cmap: CMAP colour palette for the heatmap)
						- cluster_params: clustering parameters dictionary(
												- cluster_cmap: CMAP colour palette for each clustered axis
												- rowColorCluster: Setting to 'True' will display a colour bar for the rows
												- colColorCluster: Setting to 'True' will display a colour bar for the columns
												- row_color_threshold: The colour threshold for the row dendrogram
												- col_color_threshold: The colour threshold for the column dendrogram)
		- [run] : Generates and displays the Hierarchical Clustered Heatmap (HCH).

- [polarDendrogram](https://github.com/brettChapman/multivis/blob/master/multivis/polarDendrogram.py): Polar dendrogram
	- [init_parameters](https://github.com/brettChapman/multivis/blob/master/multivis/polarDendrogram.py#L22-L27)
		- [dn] : Dendrogram dictionary.
	- [methods](https://github.com/brettChapman/multivis/blob/master/multivis/polarDendrogram.py#L29-L144)
		- [set_params] : Set parameters - imageFileName: file name to save image to
						- saveImage: Setting to 'True' will save the image to file
						- branch_scale: Scale the distribution of branches ("linear", "log", "square")
						- gap: The gap size within the polar dendrogram
						- grid: Setting to 'True' overlays a grid over the polar dendrogram
						- style_sheet: Setting the Seaborn style-sheet (see https://python-graph-gallery.com/104-seaborn-themes/)
						- dpi: The number of Dots Per Inch (DPI) for the image
						- figSize: The figure size as a tuple (width,height)
						- text_params: text parameters dictionary(
											- fontSize: The font size for all text
											- text_colors: dictionary(Peak Table index: Peak Table 'Color' column)
											- labels: dictionary(Peak Table index: Peak Table 'Label' column))
		- [run] : Generates and displays the Polar dendrogram.

#### multivis.utils

- [loadData](https://github.com/brettChapman/multivis/blob/master/multivis/utils/loadData.py): Loads and validates the Data and Peak sheet from an excel file.
	- [parameters](https://github.com/brettChapman/multivis/blob/master/multivis/utils/loadData.py#L6)
		- [filename] : The name of the excel file (.xlsx file) e.g. 'Data.xlsx'.
		- [DataSheet] : The name of the data sheet in the file e.g. 'Data'. The data sheet must contain an 'Idx', 'SampleID', and 'Class' column.
		- [PeakSheet] : The name of the peak sheet in the file e.g. 'Pata'. The peak sheet must contain an 'Idx', 'Name', and 'Label' column.
	- [Returns]
		- DataTable: Pandas dataFrame
		- PeakTable: Pandas dataFrame

- [mergeBlocks](https://github.com/brettChapman/multivis/blob/master/multivis/utils/mergeBlocks.py): Merges multiply different Data Tables and Peak Tables into a single Peak Table and Data Table (used for multi-block/multi-omics data preparation). The 'Name' column needs to be unique across all blocks. Automatically annotates merged Peak Table with 'Block' column.
	- [parameters](https://github.com/brettChapman/multivis/blob/master/multivis/utils/mergeBlocks.py#L5)
		- [peak_blocks] : A dictionary of Pandas Peak Table dataframes from different datasets indexed by dataset type.
		- [data_blocks] : A dictionary of Pandas Data Table dataframes from different datasets indexed by dataset type.
	- [Returns]
		- [DataTable] : Merged Pandas dataFrame
		- [PeakTable] : Merged Pandas dataFrame

- [range_scale](https://github.com/brettChapman/multivis/blob/master/multivis/utils/range_scale.py): Scales a range of values between user chosen values.
	- [parameters](https://github.com/brettChapman/multivis/blob/master/multivis/utils/range_scale.py#L4)
		- [x] : A numpy array of values
		- [newMin] : The minimum value to scale the numpy array to
		- [newMax] : The maximum value to scale the number array to
	- [Returns]
		- [scaled_x] : A scaled numpy array

- [corrAnalysis](https://github.com/brettChapman/multivis/blob/master/multivis/corrAnalysis.py): Correlation analysis with Pearson, Spearman or Kendall's Tau.
	- [parameters](https://github.com/brettChapman/multivis/blob/master/multivis/corrAnalysis.py#L6)
		- [X] : A Pandas dataframe matrix of values
		- [correlationType] : The correlation type to apply. Either "Pearson", "Spearman" or "KendallTau"
	- [Returns]
		- [df_corr] : Pandas dataframe of all correlation coefficients
		- [df_pval] : Pandas dataframe of all correlation pvalues

- [cluster](https://github.com/brettChapman/multivis/blob/master/multivis/utils/spatialClustering.py): Clusters data using a linkage cluster method. If the data is correlated the correlations are first preprocessed, then clustered, otherwise a distance metric is applied to non-correlated data before clustering.
	- [parameters](https://github.com/brettChapman/multivis/blob/master/multivis/utils/spatialClustering.py#L6)
		- [X] : A Pandas dataframe matrix of values (may or may not be a matrix of correlation coefficients)
		- [transpose_non_correlated] : Setting to 'True' will transpose the matrix if it is not correlated data
		- [is_correlated] : Setting to 'True' will treat the matrix as if it contains correlation coefficients
		- distance_metric : Set the distance metric. Used if the matrix does not contain correlation coefficients.
		- linkage_method : Set the linkage method for the clustering.
	- [Returns]
		- [X] : The original matrix, transposed if transpose_non_correlated is 'True' and is_correlated is 'False'.
		- [row_linkage] : linkage matrix for the rows from a linkage clustered scores matrix
		- [col_linkage] : linkage matrix for the columns from a linkage clustered scores matrix

### License
Multivis is licensed under the MIT license.

### Authors
- Brett Chapman
- https://scholar.google.com.au/citations?user=A_wYNAQAAAAJ&hl=en

### Correspondence
Dr. Brett Chapman, Post-doctoral Research Fellow at the Centre for Integrative Metabolomics & Computational Biology at Edith Cowan University.
E-mail: brett.chapman@ecu.edu.au, brett.chapman78@gmail.com

### Citation
If you would cite multivis in a scientific publication, you can use the following: [currently pending publication submission]
