import os
import sys
import numpy as np
import networkx as nx
import matplotlib
from string import Template
from ast import literal_eval
import json

class springNetwork:
    """Class for springNetwork to produce an interactive Spring-embedded Network (SEN) plot.

        Initial_Parameters
        ----------
        g : NetworkX graph.

        Methods
        -------
        set_params : Set parameters -
            node_size_scale: dictionary(Peak Table column name as index: dictionary('scale': ("linear", "reverse_linear", "log", "reverse_log", "square", "reverse_square", "area", "reverse_area", "volume", "reverse_volume")
                                                                                    'range': a number array of length 2 - minimum size to maximum size)) (default: sizes all nodes to 10 with no dropdown menu)
            html_file: Name to save the HTML file as (default: 'springNetwork.html')
            backgroundColor: Set the background colour of the plot (default: 'white')
            foregroundColor: Set the foreground colour of the plot (default: 'black')
            chargeStrength: The charge strength of the spring-embedded network (force between springs) (default: -120)
            node_text_size: The text size for each node (default: 15)
            fix_nodes: Setting to 'True' will fix nodes in place when manually moved (default: False)
            displayLabel: Setting to 'True' will set the node labels to the 'Label' column, otherwise it will set the labels to the 'Name' column from the Peak Table (default: False)
            node_data: Peak Table column names to include in the mouse over information (default: 'Name' and 'Label')
            link_type: The link type used in building the network (default: 'score')
            link_width: The width of the links (default: 0.5)
            pos_score_color: Colour value for positive similarity scores. Can be HTML/CSS name, hex code, and (R,G,B) tuples (default: 'red')
            neg_score_color: Colour value for negative similarity scores. Can be HTML/CSS name, hex code, and (R,G,B) tuples (default: 'black')

        run: : Generates the JavaScript embedded HTML code and writes to a HTML file
    """

    def __init__(self, g):

        self.__g = self.__checkData(g)

        self.set_params()

    def set_params(self, node_size_scale={}, html_file='springNetwork.html', backgroundColor='white', foregroundColor='black', chargeStrength=-120, node_text_size=15, fix_nodes=False, displayLabel=False, node_data=['Name', 'Label'], link_type='score', link_width=0.5, pos_score_color='red', neg_score_color='black'):

        node_size_scale, html_file, backgroundColor, foregroundColor, chargeStrength, node_text_size, fix_nodes, displayLabel, node_data, link_type, link_width, pos_score_color, neg_score_color = self.__paramCheck(node_size_scale, html_file, backgroundColor, foregroundColor, chargeStrength, node_text_size, fix_nodes, displayLabel, node_data, link_type, link_width, pos_score_color, neg_score_color)

        self.__node_size_scale = node_size_scale;
        self.__html_file = html_file;
        self.__backgroundColor = backgroundColor;
        self.__foregroundColor = foregroundColor;
        self.__chargeStrength = chargeStrength;
        self.__node_text_size = node_text_size;
        self.__fix_nodes = fix_nodes;
        self.__displayLabel = displayLabel;
        self.__node_data = node_data;
        self.__link_type = link_type;
        self.__link_width = link_width;
        self.__pos_score_color = pos_score_color;
        self.__neg_score_color = neg_score_color;

    def run(self):

        g = self.__g
        link_type = self.__link_type.lower()
        link_width = self.__link_width
        chargeStrength = self.__chargeStrength
        html_file = self.__html_file
        backgroundColor = self.__backgroundColor
        foregroundColor = self.__foregroundColor
        node_text_size = self.__node_text_size
        node_size_scale = self.__node_size_scale
        fix_nodes = self.__fix_nodes
        displayLabel = self.__displayLabel
        node_data = self.__node_data

        if fix_nodes:
            fixed = "true";
        else:
            fixed = "false";

        if link_type.lower() == 'pvalue':
            operator = '<=';
        else:
            operator = '>=';

        if displayLabel:
            dispLabel = "true";
        else:
            dispLabel = "false";

        paramDict = dict({"link_type": link_type, "link_width": link_width, "node_text_size": node_text_size,
                          "displayLabel": dispLabel, "node_data": node_data, "node_size_scale": node_size_scale, "chargeStrength": chargeStrength, "fix_nodes": fixed})

        data = json.dumps(self.__generateJson(g), cls=self.__graphEncoder)

        css_text_template_network = Template(self.__getCSS());
        js_text_template_network = Template(self.__getJS());
        html_template_network = Template(self.__getHTML());

        css_text_network = css_text_template_network.substitute({'backgroundColor': backgroundColor, 'foregroundColor': foregroundColor})

        js_text_network = js_text_template_network.substitute({'networkData': json.dumps(data)
                                                                  , 'backgroundColor': backgroundColor
                                                                  , 'foregroundColor': foregroundColor
                                                                  , 'operator': operator
                                                                  , 'paramDict': paramDict})

        html = html_template_network.substitute({'css_text': css_text_network, 'js_text': js_text_network})

        with open(html_file, 'w') as f:
            f.write(html)
            f.close()

    def __checkData(self, g):

        if not isinstance(g, nx.classes.graph.Graph):
            print("Error: A NetworkX graph was not entered. Please check your data.")
            sys.exit()

        return g

    def __paramCheck(self, node_size_scale, html_file, backgroundColor, foregroundColor, chargeStrength, node_text_size, fix_nodes, displayLabel, node_data, link_type, link_width, pos_score_color, neg_score_color):

        g = self.__g
        col_list = list(g.nodes[list(g.nodes.keys())[0]].keys())[:-1]

        if node_size_scale:
            if not isinstance(node_size_scale, dict):
                print("Error: Node size scale is not a valid data type. Provide a dictionary.")
                sys.exit()

            for column in node_size_scale.keys():
                if column not in col_list:
                    print("Error: Node size scale columns not valid. Choose one of {}.".format(', '.join(col_list)))
                    sys.exit()
                else:
                    for idx, node in enumerate(g.nodes()):
                        try:
                            float(g.node[node][column])
                        except ValueError:
                            print(
                            "Error: Node size scale column {} contains invalid values. Choose a node size scale column containing float or integer values.".format(column))
                            sys.exit()

                        for key in node_size_scale[column].keys():

                            if key not in ['scale', 'range']:
                                print(
                                "Error: Node size scale column {} dictionary keys are not valid. Use \"scale\" and \"range\".".format(column))
                                sys.exit()

                        if node_size_scale[column]['scale'].lower() not in ["linear", "reverse_linear", "log", "reverse_log", "square", "reverse_square", "area", "reverse_area", "volume", "reverse_volume"]:
                            print("Error: Node size scale column {} dictionary scale value not valid. Choose either \"linear\", \"reverse_linear\", \"log\", \"reverse_log\", \"square\", \"reverse_square\", \"area\", \"reverse_area\", \"volume\", \"reverse_volume\".".format(column))
                            sys.exit()

                        if not isinstance(node_size_scale[column]['range'], list):
                            print(
                            "Error: Node size scale column {} dictionary range data type is not valid. Use a list of length 2.".format(
                                column))
                            sys.exit()
                        else:
                            for size in node_size_scale[column]['range']:
                                if not isinstance(size, float):
                                    if not isinstance(size, int):
                                        print(
                                        "Error: Node size scale column {} dictionary range value is not valid. Choose a float or integer value.")
                                        sys.exit()
        else:
            node_size_scale = dict({})  # Default to an empty dict

        if not isinstance(html_file, str):
            print("Error: Html file is not valid. Choose a string value.")
            sys.exit()
        else:
            html_end = html_file.split(".")[-1]

            if html_end != "html":
                print("Error: Html file extension is not 'html'. Please use '.html' extension.")
                sys.exit()

        backgroundColor = self.__colorCheck(backgroundColor, "background")

        foregroundColor = self.__colorCheck(foregroundColor, "foreground")

        if not isinstance(chargeStrength, float):
            if not isinstance(chargeStrength, int):
                print("Error: Charge strength is not valid. Choose a float or integer value.")
                sys.exit()

        if not isinstance(node_text_size, float):
            if not isinstance(node_text_size, int):
                print("Error: Node text size is not valid. Choose a float or integer value.")
                sys.exit()

        if not type(fix_nodes) == bool:
            print("Error: Fix nodes is not valid. Choose either \"True\" or \"False\".")
            sys.exit()

        if not type(displayLabel) == bool:
            print("Error: Display label is not valid. Choose either \"True\" or \"False\".")
            sys.exit()

        if not isinstance(node_data, list):
                print("Error: Node data is not valid. Use a list.")
                sys.exit()
        else:
            for node_item in node_data:
                if node_item not in col_list:
                    print("Error: Node data item not valid. Choose one of {}.".format(', '.join(col_list)))
                    sys.exit()

            if "Name" not in node_data:
                print("Error: Column \"Name\" should be node data. Please correct")
                sys.exit()

            if "Label" not in node_data:
                print("Error: Column \"Label\" should be node data. Please correct")
                sys.exit()

        min_weight = min(list(nx.get_edge_attributes(g, 'weight').values()))

        if link_type.lower() not in ["pvalue", "score"]:
            print("Error: Link type not valid. Choose either \"Pvalue\" or \"Score\".")
            sys.exit()
        else:
            if link_type.lower() == "pvalue":
                if min_weight < 0:
                    print("Error: Link type invalid with edge values. Negative values present. Choose \"Score\" link type or change the edge values to p-values instead of scores.")
                    sys.exit()

        if not isinstance(link_width, float):
            if not isinstance(link_width, int):
                print("Error: Link width is not valid. Choose a float or integer value.")
                sys.exit()

        pos_score_color = self.__colorCheck(pos_score_color, "positive score")

        neg_score_color = self.__colorCheck(neg_score_color, "negative score")

        return node_size_scale, html_file, backgroundColor, foregroundColor, chargeStrength, node_text_size, fix_nodes, displayLabel, node_data, link_type, link_width, pos_score_color, neg_score_color

    def __colorCheck(self, colorValue, type):

        if "#" in str(colorValue):
            if not matplotlib.colors.is_color_like(colorValue):
                print("Error: The colour value for the {} color is not valid. Choose a valid colour as a HTML/CSS name, hex code, or (R,G,B) tuple.".format(type))
                sys.exit()
        else:
            try:
                rgb_color = literal_eval(str(colorValue))
                cValue = '#{:02x}{:02x}{:02x}'.format(rgb_color[0], rgb_color[1], rgb_color[2])
            except ValueError:
                cValue = colorValue

            if not matplotlib.colors.is_color_like(cValue):
                print("Error: The colour value for the {} color is not valid. Choose a valid colour as a HTML/CSS name, hex code, or (R,G,B) tuple.".format(type))
                sys.exit()

            colorValue = cValue;

        return colorValue;

    class __graphEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            else:
                return super(graphEncoder, self).default(obj)

    def __generateJson(self, G):

        graph_data = {'nodes': [], 'links': []}

        key_list = list(G.nodes[list(G.nodes.keys())[0]].keys())

        #iterate over all attributes and add to dictionary before appending to graph
        for node in G.nodes():

            d = {'id': node}

            for key in key_list:
                d[key] = G.nodes[node][key]

            graph_data['nodes'].append(d)

        for (source, target) in G.edges():

            weight = G.edges[source, target]['weight']

            if weight > 0:
                color = self.__pos_score_color;
            else:
                color = self.__neg_score_color;

            graph_data['links'].append({
                "source": source,
                "target": target,
                "weight": weight,
                "color": color})

        return graph_data

    def __getCSS(self):

        css_text = '''
        
        body {
            background-color: $backgroundColor;            
        }
        
        .links line {
            stroke-opacity: 0.6;
        }
    
        .nodes circle {
            stroke: #fff;
            stroke-width: 1.5px;
            opacity: 1.0;
        }
        
        .text {
            stroke: #fff;
            stroke-width: 1.5px;
            opacity: 1.0;
        }
    
        div.tooltip {
            position: absolute;
            background-color: white;
            max-width; 200px;
            height: auto;
            padding: 1px;
            border-style: solid;
            border-radius: 4px;
            border-width: 1px;
            box-shadow: 3px 3px 10px rgba(0, 0, 0, .5);
            pointer-events: none;
        }
        
        #nodeSizeDropdown {
            position: relative;
            top: 25px;
            
        }
        
        #nodeColorDropdown {
            position: relative;
            top: 30px;
        }
        
        #sliderText {
            position: absolute;
            top: 18px;
            left: 0px;
            color: 'black';
        }
        
        #slider {
            position: absolute;
            top: 20px;
            left: 125px;
        }
        
        #sliderValue {
            position: absolute;
            top: 38px;
            left: 350px;
            color: 'black';
        }
        
        #save {
            position: relative;
            top: 35px;
            left: 0px;                 
        }  
        
        #wrapper {
            position: relative;
            height: 100%;                        
            margin: 0 auto;
            margin-top: auto;
            margin-bottom: auto;
            margin-left: auto;
            margin-right: auto;
        }
        
        #sliderValue, text {
                    
            font-family: sans-serif;
                -webkit-touch-callout: none; /* iOS Safari */
                -webkit-user-select: none; /* Safari */
                -khtml-user-select: none; /* Konqueror HTML */
                -moz-user-select: none; /* Firefox */
                -ms-user-select: none; /* Internet Explorer/Edge */
                user-select: none; /* Non-prefixed version, currently supported by Chrome and Opera */
        }
        
        '''

        return css_text

    def __getJS(self):

        js_text = '''
                
        var params = JSON.parse(JSON.stringify($paramDict));
            
        var networkData = $networkData
        
        var canvas = document.getElementById("wrapper");
        var springNetwork = d3.select(canvas).append("svg").attr("id", "springNetwork");
        
        function redraw(){
        
            d3.select('#wrapper').select("#search").selectAll("*").remove();            
            d3.select('#wrapper').select("#nodeSizeDropdown").selectAll("*").remove();
            d3.select('#wrapper').select("#nodeColorDropdown").selectAll("*").remove();
            d3.select('#wrapper').select("#save").selectAll("*").remove();
                        
            var colorBy = [];
                    
            var width = canvas.clientWidth;
            var height = canvas.clientHeight;
             
            springNetwork.selectAll("*").remove();
            
            var svg = d3.select("svg#springNetwork")
                                .attr("width", width)
                                .attr("height", height);
                                
            svg.call(d3.zoom().on('zoom', zoomed))
                .on("dblclick.zoom", null);
        
            var simulation = d3.forceSimulation()
                .force("link", d3.forceLink().id(d => d.id))            
                .force("center", d3.forceCenter(width / 2, height / 2));        
        
            var container = svg.append('g');
        
            var search = d3.select("#search").attr('onsubmit', 'return false;');
        
            var box = search.append('input')
                .attr('type', 'text')
                .attr('id', 'searchTerm')
                .attr('placeholder', 'Type to search...');
        
            var button = search.append('input')
                .attr('type', 'button')
                .attr('value', 'Search')
                .on('click', function () { searchNodes(); });
        
            var toggle = 0;
        
            var tooltip = d3.select("body")
                .append("div")
                .attr("class", "tooltip")
                .style("opacity", 0);
        
            var graph = JSON.parse(networkData);
            
            if (params.link_type == "score") {            
                var link_type_text = "Score";
            } else if (params.link_type == "pvalue") {
                var link_type_text = "Pvalue";
            }
            
            var graphRec = JSON.parse(JSON.stringify(graph));
            
            var link = container.append("g")
                .attr("class", "links")
                .selectAll("line");
            
            var node = container.append("g")
                .attr("class", "nodes")
                .selectAll("circle");
            
            var label = container.selectAll(".text");
        
            var linkedByIndex = {};
        
            graphRec.links.forEach( function(d) {
                linkedByIndex[d.source + ',' + d.target] = 1;
                linkedByIndex[d.target + ',' + d.source] = 1;
            });
            
            if (Object.keys(params.node_size_scale).length === 0) {
            
                graph.nodes.forEach( function (d) { d.size = 10; });
            
            } else {
                
                updateNodeSize(Object.keys(params.node_size_scale)[0])
            }
            
            function updateNodeSize(centrality) {
                    
                var scaleType = params.node_size_scale[centrality].scale
                var range = params.node_size_scale[centrality].range
                
                var centrality_values = []        
                graph.nodes.forEach( function (d) { if (isNaN(d[centrality])) { centrality_values.push(parseFloat(0)); } else { centrality_values.push(parseFloat(d[centrality])); }});
                
                initScale = d3.scaleLinear()
                    .domain(d3.extent(centrality_values))
                    .range([1,10]);
                        
                scaledValues = []
                centrality_values.forEach( function (d) { scaledValues.push(initScale(parseFloat(d))); });
                                   
                if (scaleType == "linear") {
                    
                    linearScale = d3.scaleLinear()
                         .domain(d3.extent(scaledValues))
                         .range(range);
                     
                    graph.nodes.forEach( function (d) { if (isNaN(d[centrality])) { d.size = linearScale(initScale(parseFloat(0))); } else { d.size = linearScale(initScale(parseFloat(d[centrality]))); }});
                  
                } else if (scaleType == "reverse_linear") {
                    
                    reversed_linear_values = []
                     
                    scaledValues.forEach( function (d) { reversed_linear_values.push(parseFloat(1/d)); });
                     
                    reversedLinearScale = d3.scaleLinear()
                        .domain(d3.extent(reversed_linear_values))
                        .range(range);
                    
                    graph.nodes.forEach( function (d) { if (isNaN(d[centrality])) { d.size = reversedLinearScale(1 / initScale(parseFloat(0))); } else { d.size = reversedLinearScale(1 / initScale(parseFloat(d[centrality]))); }});
                     
                } else if (scaleType == "log") {
                   
                    logScale = d3.scaleLog()
                        .domain(d3.extent(scaledValues))
                        .range(range);  	        
                             
                    graph.nodes.forEach( function (d) { if (isNaN(d[centrality])) { d.size = logScale(initScale(parseFloat(0))); } else { d.size = logScale(initScale(parseFloat(d[centrality]))); }});
                  
                } else if (scaleType == "reverse_log") {
                    
                    reversed_log_values = []
                     
                    scaledValues.forEach( function (d) { reversed_log_values.push(parseFloat(1/d)); });
                     
                    reversedLogScale = d3.scaleLog()
                        .domain(d3.extent(reversed_log_values))
                        .range(range);
                     
                    graph.nodes.forEach( function (d) { if (isNaN(d[centrality])) { d.size = reversedLogScale(1 / initScale(parseFloat(0))); } else { d.size = reversedLogScale(1 / initScale(parseFloat(d[centrality]))); }});
                     
                } else if (scaleType == "square") {
                   
                    squareScale = d3.scalePow()
                        .domain(d3.extent(scaledValues))
                        .exponent(2)
                        .range(range);
                    
                    graph.nodes.forEach( function (d) { if (isNaN(d[centrality])) { d.size = squareScale(initScale(parseFloat(0))); } else { d.size = squareScale(initScale(parseFloat(d[centrality]))); }});
                  
                } else if (scaleType == "reverse_square") {
                   
                    reversed_squared_values = []
                     
                    scaledValues.forEach( function (d) { reversed_squared_values.push(parseFloat(1/d)); });
                     
                    reversedSquareScale = d3.scalePow()
                        .domain(d3.extent(reversed_squared_values))
                        .exponent(2)
                        .range(range);
                    
                    graph.nodes.forEach( function (d) { if (isNaN(d[centrality])) { d.size = reversedSquareScale(1 / initScale(parseFloat(0))); } else { d.size = reversedSquareScale(1 / initScale(parseFloat(d[centrality]))); }});
                  
                } else if (scaleType == "area") {
                    
                    area_values = []
                     
                    scaledValues.forEach( function (d) { area_values.push(parseFloat(Math.PI * (d * d))); });
                     
                    areaScale = d3.scaleLinear()
                        .domain(d3.extent(area_values))
                        .range(range);
                     
                    graph.nodes.forEach( function (d) { if (isNaN(d[centrality])) { d.size = areaScale(Math.PI * (initScale(parseFloat(0)) * initScale(parseFloat(0)))); } else { d.size = areaScale(Math.PI * (initScale(parseFloat(d[centrality])) * initScale(parseFloat(d[centrality])))); }});
                     
                } else if (scaleType == "reverse_area") {
                    
                    reversed_area_values = []
                     
                    scaledValues.forEach( function (d) { reversed_area_values.push(parseFloat(Math.PI * (parseFloat(1/d) * parseFloat(1/d)))); });
                     
                    reversedAreaScale = d3.scaleLinear()
                        .domain(d3.extent(reversed_area_values))
                        .range(range);
                     
                    graph.nodes.forEach( function (d) { if (isNaN(d[centrality])) { d.size = reversedAreaScale(Math.PI * (1 / initScale(parseFloat(0))) * (1 / initScale(parseFloat(0)))); } else { d.size = reversedAreaScale(Math.PI * (1 / initScale(parseFloat(d[centrality]))) * (1 / initScale(parseFloat(d[centrality])))); }});
                     
                } else if (scaleType == "volume") {
                    
                    volume_values = []
                     
                    scaledValues.forEach( function (d) { volume_values.push(parseFloat(4 / 3 * (Math.PI * (d * d * d)))); });
                     
                    volumeScale = d3.scaleLinear()
                        .domain(d3.extent(volume_values))
                        .range(range);
                     
                    graph.nodes.forEach( function (d) { if (isNaN(d[centrality])) { d.size = volumeScale(4 / 3 * (Math.PI * (initScale(parseFloat(0)) * initScale(parseFloat(0)) * initScale(parseFloat(0))))); } else { d.size = volumeScale(4 / 3 * (Math.PI * (initScale(parseFloat(d[centrality])) * initScale(parseFloat(d[centrality])) * initScale(parseFloat(d[centrality]))))); }});
                  
                } else if (scaleType == "reverse_volume") {
                 
                    reversed_volume_values = []             
                    
                    scaledValues.forEach( function (d) { reversed_volume_values.push(parseFloat(4 / 3 * (Math.PI * (parseFloat(1/d) * parseFloat(1/d) * parseFloat(1/d))))); });
                     
                    reversedVolumeScale = d3.scaleLinear()
                        .domain(d3.extent(reversed_volume_values))
                        .range(range);
                    
                    graph.nodes.forEach( function (d) { if (isNaN(d[centrality])) { d.size = reversedVolumeScale(4 / 3 * (Math.PI * ((1 / initScale(parseFloat(0))) * (1 / initScale(parseFloat(0))) * (1 / initScale(parseFloat(0)))))); } else { d.size = reversedVolumeScale(4 / 3 * (Math.PI * ((1 / initScale(parseFloat(d[centrality]))) * (1 / initScale(parseFloat(d[centrality]))) * (1 / initScale(parseFloat(d[centrality])))))); }});
                       
                }    
            }
                
            var scaleLinksLinear = d3.scaleLinear()
                .domain([d3.min(graph.links, function(d) {return d.weight; }),d3.max(graph.links, function(d) {return d.weight; })])
                .range([1,1000])
                .clamp(true);
                
            var scaleLinksLog = d3.scaleLog()
                .domain([Math.log(d3.min(graph.links, function(d) {return d.weight; })),Math.log(d3.max(graph.links, function(d) {return d.weight; }))])          	    
                .range([1,1000])
                .clamp(true);       
            
            simulation
                .force("charge", d3.forceManyBody().strength(params.chargeStrength).distanceMax(500))            
                .force("collide", d3.forceCollide().radius( function (d) { return d.size; }));
        
            graph.nodes.forEach(function(d) { if (typeof d.color !== 'undefined') { colorBy.push(d.color); } else { colorBy.push(1); } });
            
            var colorBy = Array.from(new Set(colorBy)) 
           
            update();
        
            function update() {
                
                node = node.data(graph.nodes, d => d.id);
        
                node.exit().remove();
            
                var newNode = node.enter().append("circle")
                        .attr('r', function(d, i) { return d.size; })      		    
                        .attr("fill", function(d) { return d.color; })
                        .attr('class', 'node')
                        .on('mouseover.tooltip', function(d) {
                                tooltip.transition()
                                    .duration(300)
                                    .style("opacity", .8);
                                
                                peak_data = params.node_data;
                                                                
                                if (Number.isNaN(Number(d[peak_data[0]]))) {                                
                                    var init_value = d[peak_data[0]]                                    
                                } else if (typeof Number(d[peak_data[0]]) == 'number') { 
                                    var init_value = Number(d[peak_data[0]]).toFixed(3)
                                }
                                
                                html_line = peak_data[0] + ": " + init_value;
                                
                                peak_data.forEach(function(p) { 
                                
                                    if (p !== peak_data[0]) {
                                        if (Number.isNaN(Number(d[p]))) {
                                            var data_value = d[p];
                                        } else if (typeof Number(d[p]) == 'number') {
                                            var data_value = Number(d[p]).toFixed(3);
                                        }
                                        
                                        html_line = html_line + "<br/>" + p + ": " + data_value;
                                                                                                        
                                    }
                                });
                                
                                tooltip.html(html_line)
                                        .style("left", (d3.event.pageX) + "px")
                                        .style("top", (d3.event.pageY + 10) + "px");                  
                        })      		    
                        .on('dblclick', releaseNode)
                        .on('click', fade(0.1))
                        .on("mouseout.tooltip", function() {
                                tooltip.transition()
                                    .duration(100)
                                    .style("opacity", 0);
                        })  				
                        .on("mousemove", function() {
                                tooltip.style("left", (d3.event.pageX) + "px")
                                    .style("top", (d3.event.pageY + 10) + "px");
                        })
                        .call(d3.drag()
                            .on("start", dragstarted)
                            .on("drag", dragged)
                            .on("end", dragended));
                                            
                node = node.merge(newNode);
            
                label = label.data(graph.nodes, d => d.id);
            
                label.exit().remove();
               
                var newLabel = label.enter().append("text")
                        .text(function (d) { if (params.displayLabel == "true") { return d.Label; } else { return d.Name; } })
                        .style("text-anchor", "middle")
                            .style("fill", "$foregroundColor")
                            .style("font-family", "Helvetica")
                            .style("font-size", params.node_text_size)
                        .attr('class', 'node')
                        .on('mouseover.tooltip', function(d) {
                                tooltip.transition()
                                        .duration(300)
                                        .style("opacity", .8);
                                
                                peak_data = params.node_data;
                                
                                if (Number.isNaN(Number(d[peak_data[0]]))) {                                
                                    var init_value = d[peak_data[0]]                                    
                                } else if (typeof Number(d[peak_data[0]]) == 'number') { 
                                    var init_value = Number(d[peak_data[0]]).toFixed(3)
                                }
                                
                                html_line = peak_data[0] + ": " + init_value;
                                
                                peak_data.forEach(function(p) { 
                                
                                    if (p !== peak_data[0]) {
                                        if (Number.isNaN(Number(d[p]))) {
                                            var data_value = d[p];
                                        } else if (typeof Number(d[p]) == 'number') {
                                            var data_value = Number(d[p]).toFixed(3);
                                        }
                                        
                                        html_line = html_line + "<br/>" + p + ": " + data_value;
                                                                                                        
                                    }
                                });
                                                
                                tooltip.html(html_line)
                                        .style("left", (d3.event.pageX) + "px")
                                        .style("top", (d3.event.pageY + 10) + "px");
                        })
                        .on('dblclick', releaseNode)
                        .on('click', fade(0.1))      		    
                        .on("mouseout.tooltip", function() {
                                tooltip.transition()
                                    .duration(100)
                                    .style("opacity", 0);
                        })  			
                        .on("mousemove", function() {
                                tooltip.style("left", (d3.event.pageX) + "px")
                                    .style("top", (d3.event.pageY + 10) + "px");
                        })
                        .call(d3.drag()
                            .on("start", dragstarted)
                            .on("drag", dragged)
                            .on("end", dragended));
            
                label = label.merge(newLabel);
        
                //Add no links
                link = link.data([]);
        
                //Remove all old links, leaving no links
                link.exit().remove();
                
                //Add new links
                link = link.data(graph.links);
        
                //Remove all old links, leaving only the new links
                link.exit().remove();
                        
                var newLink = link.enter().append("line")
                            .attr("class", "link")
                            .attr("stroke-width", params.link_width)
                            .style("stroke", function(d) { return d.color; })
                            .on('mouseover.tooltip', function(d) {
                                    tooltip.transition()
                                            .duration(300)
                                            .style("opacity", .8);
                                    
                                    if (params.displayLabel == "true") {                                                
                                        var source = d.source.Label;
                                        var target = d.target.Label;
                                    } else { 
                                        var source = d.source.Name;
                                        var target = d.target.Name;
                                    }
                                           
                                    tooltip.html("Source: "+ source + 
                                                "<br/>Target: " + target +
                                                "<br/>" + link_type_text + ": "  + d.weight.toPrecision(3))                                                
                                                    .style("left", (d3.event.pageX) + "px")
                                                    .style("top", (d3.event.pageY + 10) + "px");
                            })
                            .on("mouseout.tooltip", function() {
                                    tooltip.transition()
                                            .duration(100)
                                            .style("opacity", 0);
                            })
                            .on("mousemove", function() {
                                    tooltip.style("left", (d3.event.pageX) + "px")
                                            .style("top", (d3.event.pageY + 10) + "px");
                            });
            
                link = link.merge(newLink);
                
                simulation
                    .nodes(graph.nodes)
                    .on("tick", ticked);
                           
                simulation.force("link")
                    .links(graph.links);
                
                simulation.alphaTarget(0.1).restart();
            }
            
            function ticked() {
                link
                    .attr("x1", function(d) { return d.source.x; })
                    .attr("y1", function(d) { return d.source.y; })
                    .attr("x2", function(d) { return d.target.x; })
                    .attr("y2", function(d) { return d.target.y; });    
                
                node       
                    .attr("cx", function(d) { return d.x = Math.max(d3.select(this).attr("r"), Math.min(width - d3.select(this).attr("r"), d.x)); })
                    .attr("cy", function(d) { return d.y = Math.max(d3.select(this).attr("r"), Math.min(height - d3.select(this).attr("r"), d.y)); });    
                          
                label.attr("x", function(d){ return d.x; })
                     .attr("y", function (d) {return d.y + 5; });            
                
            }
            
            var sliderInitValue = '';
            var sliderMin = '';
            var sliderMax = '';
            var sliderValue = '';
            
            if (params.link_type == "score") {
                sliderInitValue =  d3.min(graph.links, function(d) {return d.weight; }).toPrecision(5)
                sliderMin = scaleLinksLinear(d3.min(graph.links, function(d) {return d.weight; }))
                sliderMax = scaleLinksLinear(d3.max(graph.links, function(d) {return d.weight; }))
                sliderValue = scaleLinksLinear(d3.min(graph.links, function(d) {return d.weight; }))
            } else if (params.link_type == "pvalue") {
                sliderInitValue =  d3.max(graph.links, function(d) {return d.weight; }).toPrecision(5)
                sliderMin = scaleLinksLog(Math.log(d3.min(graph.links, function(d) {return d.weight; })))
                sliderMax = scaleLinksLog(Math.log(d3.max(graph.links, function(d) {return d.weight; })))
                sliderValue = scaleLinksLog(Math.log(d3.max(graph.links, function(d) {return d.weight; })))
            }
            
            d3.select('#sliderText').text(link_type_text + ' threshold: ');
            
            d3.select('#sliderValue').text(sliderInitValue);
        
            var sliderWidth = 225;
            var sliderOffSet = 45;
        
            var Slider = d3.sliderHorizontal()
    	    					    .min(sliderMin)
    							    .max(sliderMax)
                                    .default(sliderInitValue)
                                    .ticks(0)
                                    .handle(d3.symbol().type(d3.symbolCircle).size(150)())
    							    .step(0.0001)                        
                                    .fill('#2196f3')
    							    .width(sliderWidth - sliderOffSet)
    							    .displayValue(false)
    							    .on('onchange', value => {
      							    	
      							    	if (params.link_type == "score") {
                                            var threshold = scaleLinksLinear.invert(value);
                                        } else if (params.link_type == "pvalue")  {
                                            var threshold = Math.exp(scaleLinksLog.invert(value));
                                        }
                                        
                					    d3.select('#sliderValue').text(threshold.toPrecision(5));
                						                						
                                        graph.links.splice(0, graph.links.length);
                                        graphRec.links.forEach( function (d) { if (d.weight $operator threshold) { graph.links.push(d); }});
                                        
                                        //Update link dictionary
                                        linkedByIndex = {} 
                                        graphRec.links.forEach( function (d) {
                                            if (d.weight $operator threshold) {
                                                                  
                                                var source = JSON.stringify(d.source.id);
                                                var target = JSON.stringify(d.target.id);
                                                   
                                                if (typeof source == 'undefined') {
                                                    source = JSON.stringify(d.source);
                                                }
                                                
                                                if (typeof target == 'undefined') {
                                                    target = JSON.stringify(d.target);
                                                }
                                                                                        
                                                linkedByIndex[source + ',' + target] = 1;
                                                linkedByIndex[target + ',' + source] = 1;	  						         
                                            }
                                        });         
                
                                        update(); 
          						    });
        
            d3.select('#slider').selectAll("*").remove();
        
            d3.select('#slider')
                    .append('svg')
                    .attr('width', sliderWidth)    
                    .append('g')    
                    .attr('transform', 'translate(30,30)')
                    .call(Slider);
            
            if (Object.keys(params.node_size_scale).length != 0) {
            
                var nodeSizeDropdown = d3.select('#nodeSizeDropdown')   
                    .append('select')
                    .attr("class","nodeSizeDropdown")
                    .on('change', function() { 
                        var centrality = this.value;
                    
                        updateNodeSize(centrality)
                        
                        node.attr('r', function(d) { return d.size; } );  
                    
                        simulation.force("collide", d3.forceCollide().radius( function (d) { return d.size; }));
                        simulation.alphaTarget(0.1).restart();
                    });
                                    
                nodeSizeDropdown.selectAll('option')
                    .data(Object.keys(params.node_size_scale))
                    .enter().append('option')		
                    .text(function(d) { return d; });
            } else {
            
                var nodeSizeDropdown = d3.select('#nodeSizeDropdown')
                    .append('select')
                    .attr("class","nodeSizeDropdown");
                
                nodeSizeDropdown.selectAll('option')
                    .data(['none'])
                    .enter().append('option')		
                    .text(function(d) { return d; });        
            }
            
            var colorDropDownValues = ['default','schemeCategory10','schemeAccent','schemeDark2','schemePaired','schemePastel1','schemePastel2','schemeSet1','schemeSet2','schemeSet3'];
            var schemeLenCount = [];
            
            //Get lengths of all color schemes used
            colorDropDownValues.forEach( function(value) { if (value !== 'default') { schemeLenCount.push(d3[value].length); }});
                        
            var nodeColorDropdown = d3.select('#nodeColorDropdown')
                .append('select')
                .attr("class","nodeColorDropdown")
                .on('change', function() { 
                    var colorScheme = this.value;
                    
                    if (colorScheme == 'default') {
                        node.attr("fill", function(d) { return d.color; })
                    } else {
                    
                        //Slice color schemes to the minimum length across all color schemes for consistancy when switching color schemes
                        colorSchemeSliced = d3[colorScheme].slice(0, d3.min(schemeLenCount));
                    
                        var color_palette = d3.scaleOrdinal()
                                                   .domain(colorBy)
                                                   .range(colorSchemeSliced);                                                        
                                       
                        node.attr("fill", function(d) { if (typeof d.color !== 'undefined') { return color_palette(d.color); } else { return color_palette(1); } });                        
                    }
        
                    simulation.alphaTarget(0.1).restart();
                });
        
            nodeColorDropdown.selectAll('option')
                .data(colorDropDownValues)
                .enter().append('option')		
                .text(function(d) { return d; });
            
            d3.select("#save")
                    .on('click', function(){
                    
                        var options = {
                                canvg: window.canvg,
                                backgroundColor: '$backgroundColor',
                                height: height+100,
                                width: width+100,
                                left: -50,
                                scale: 5/window.devicePixelRatio,
                                encoderOptions: 1,
                                ignoreMouse : true,
                                ignoreAnimation : true,
                        }
		    
                        saveSvgAsPng(d3.select('svg').node(), "networkPlot.png", options);
                    })
        
            function dragstarted(d) {
            
                if (!d3.event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            }
        
            function dragged(d) {
                d.fx = d3.event.x;
                d.fy = d3.event.y;
            }
        
            function dragended(d) {
                if (!d3.event.active) simulation.alphaTarget(0);
                
                if (params.fix_nodes == "true") {
                    d.fx = d3.event.x;
                    d.fy = d3.event.y;
                } else {
                    d.fx = null;
                    d.fy = null;
                }
            }
                
            function releaseNode(d) {        
                d.fx = null;
                d.fy = null;
            }
                
            function zoomed() {
                container.attr("transform", "translate(" + d3.event.transform.x + ", " + d3.event.transform.y + ") scale(" + d3.event.transform.k + ")");
            }
        
            function neighboring(a, b) {
                return linkedByIndex[a.id + ',' + b.id] || linkedByIndex[b.id + ',' + a.id] || a.id === b.id;
            }          
        
            function fade(opacity) {
                return d => {
            
                    if (toggle == 0) {
            
                        node.style('stroke-opacity', function (o) {
                            const nodeOpacity = neighboring(d, o) ? 1 : opacity;
                            this.setAttribute('fill-opacity', nodeOpacity);
                            return nodeOpacity;
                        });
                  
                        label.style('stroke-opacity', function (o) {
                            const labelOpacity = neighboring(d, o) ? 1 : opacity;
                            this.setAttribute('fill-opacity', labelOpacity);
                            return labelOpacity;
                        });
        
                        link.style('stroke-opacity', o => (o.source === d || o.target === d ? 1 : opacity));
                            
                        toggle = 1;
                    } else {
                     
                        node.style('stroke-opacity', function (o) {
                            const nodeOpacity = 1;
                            this.setAttribute('fill-opacity', nodeOpacity);
                            return nodeOpacity;
                        });
                  
                        label.style('stroke-opacity', function (o) {
                            const labelOpacity = 1;
                            this.setAttribute('fill-opacity', labelOpacity);
                            return labelOpacity;
                        });          
        
                        link.style('stroke-opacity', 0.6);
               
                        toggle = 0;
                    }
                };
            }         
            
            function searchNodes() {
                var term = document.getElementById('searchTerm').value;
                var selected = container.selectAll('.node').filter(function (d, i) {
                    return d.Label.toLowerCase().search(term.toLowerCase()) == -1;
                });
                selected.style('opacity', '0');
                var link = container.selectAll('.link');
                link.style('stroke-opacity', '0');
                d3.selectAll('.node').transition()
                        .duration(1000)
                        .style('opacity', '1');
                d3.selectAll('.link').transition().duration(5000).style('stroke-opacity', '0.6');
            }
        }
        
        redraw();
        
        window.addEventListener("resize", redraw); 
        '''

        return js_text

    def __getHTML(self):

        html = '''
        <body>
        
            <style> $css_text </style>
            
            <div id="wrapper">
            
                <form id="search"></form>
            
                <h3 id="sliderText"></h3>
                <div id="slider"></div>
                <h3><span style="white-space: nowrap;" id="sliderValue"></span></h3>
            
                <div id="nodeSizeDropdown"></div>
                
                <div id="nodeColorDropdown"></div>
            
                <button id='save'>Save</button>
            
            
            </div>
            
            <script src="https://d3js.org/d3.v5.min.js"></script>
            <script src="https://unpkg.com/d3-simple-slider"></script>
            <script src="https://github.com/canvg/canvg/blob/master/src/canvg.js"></script>
            <script src="https://exupero.org/saveSvgAsPng/src/saveSvgAsPng.js"></script>
             
            <script> $js_text </script>
                
        </body>
        '''

        return html