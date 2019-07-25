import sys
import numpy as np
import networkx as nx
import matplotlib
from string import Template
from ast import literal_eval
from networkx.drawing.nx_agraph import pygraphviz_layout
import json

from .utils import *

class forceNetwork:

    def __init__(self, g):

        self.__g = self.__checkData(g)

        self.set_params()
        self.__set_node_params()
        self.__set_link_params()

    def __checkData(self, g):

        if not isinstance(g, nx.classes.graph.Graph):
            print("Error: A networkx graph was not entered. Please check your data.")
            sys.exit()

        return g

    def set_params(self, node_params={}, link_params={}, backgroundColor='white', foregroundColor='black', canvas_size=(1060,900), layout='spring', chargeStrength=-120):

        if node_params:
            self.__set_node_params(**node_params)

        if link_params:
            self.__set_link_params(**link_params)

        backgroundColor, foregroundColor, canvas_size, layout, chargeStrength = self.__paramCheck(backgroundColor, foregroundColor, canvas_size, layout, chargeStrength)

        self.__backgroundColor = backgroundColor;
        self.__foregroundColor = foregroundColor;
        self.__canvas_size = canvas_size;
        self.__layout = layout;
        self.__chargeStrength = chargeStrength;

    def __set_node_params(self, node_text_size=15, fix_nodes=False, displayLabel=False, node_size_scale={}):

        node_text_size, fix_nodes, displayLabel, node_size_scale = self.__node_paramCheck(node_text_size, fix_nodes, displayLabel, node_size_scale)

        self.__node_text_size = node_text_size;
        self.__fix_nodes = fix_nodes;
        self.__displayLabel = displayLabel;
        self.__node_size_scale = node_size_scale;

    def __set_link_params(self, link_type='Score', link_width=0.5, link_score_color={}):

        link_type, link_width, link_score_color = self.__link_paramCheck(link_type, link_width, link_score_color)

        self.__link_type = link_type;
        self.__link_width = link_width;
        #self.__restrict_link_distance = restrict_link_distance;
        self.__link_score_color = link_score_color;

    def __paramCheck(self, backgroundColor, foregroundColor, canvas_size, layout, chargeStrength):

        if not matplotlib.colors.is_color_like(backgroundColor):
            print("Error: Background colour is not valid. Choose a valid colour value.")
            sys.exit()

        if not matplotlib.colors.is_color_like(foregroundColor):
            print("Error: Slider text colour is not valid. Choose a valid colour value.")
            sys.exit()

        if not isinstance(canvas_size, tuple):
            print("Error: Canvas size is not valid. Choose a tuple of length 2.")
            sys.exit()
        else:
            for length in canvas_size:
                if not isinstance(length, float):
                    if not isinstance(length, int):
                        print("Error: Canvas size values not valid. Choose a float or integer value.")
                        sys.exit()

        if layout not in ["spring", "neato", "dot", "fdp", "sfdp", "twopi", "circo"]:
            print("Error: Layout program not valid. Choose either \"spring\", or graphviz layout \"neato\", \"dot\", \"fdp\", \"sfdp\", \"twopi\" or \"circo\".")
            sys.exit()

        if not isinstance(chargeStrength, float):
            if not isinstance(chargeStrength, int):
                print("Error: Charge strength is not valid. Choose a float or integer value.")
                sys.exit()

        return backgroundColor, foregroundColor, canvas_size, layout, chargeStrength

    def __node_paramCheck(self, node_text_size, fix_nodes, displayLabel, node_size_scale):

        g = self.__g
        col_list = list(g.nodes[list(g.nodes.keys())[0]].keys())

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

        if node_size_scale:
            if not isinstance(node_size_scale, dict):
                print("Error: Node size scale is not a valid data type. Choose a dictionary.")
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
                            print("Error: Node size scale column {} contains invalid values. Choose a node size scale column containing float or integer values.".format(column))
                            sys.exit()

                        for key in node_size_scale[column].keys():

                            if key not in ['scale', 'range']:
                                print("Error: Node size scale column {} dictionary keys are not valid. Use \"scale\" and \"range\".".format(column))
                                sys.exit()

                        if node_size_scale[column]['scale'].lower() not in ["linear", "reverse_linear", "log", "reverse_log", "square", "reverse_square", "area", "reverse_area", "volume", "reverse_volume"]:
                            print("Error: Node size scale column {} dictionary scale value not valid. Choose either \"linear\", \"reverse_linear\", \"log\", \"reverse_log\", \"square\", \"reverse_square\", \"area\", \"reverse_area\", \"volume\", \"reverse_volume\".".format(column))
                            sys.exit()

                        if not isinstance(node_size_scale[column]['range'], list):
                            print("Error: Node size scale column {} dictionary range data type is not valid. Use a list of length 2.".format(column))
                            sys.exit()
                        else:
                            for size in node_size_scale[column]['range']:
                                if not isinstance(size, float):
                                    if not isinstance(size, int):
                                        print("Error: Node size scale column {} dictionary range value is not valid. Choose a float or integer value.")
                                        sys.exit()
        else:
            node_size_scale = dict({}) #Default to an empty dict

        return node_text_size, fix_nodes, displayLabel, node_size_scale

    def __link_paramCheck(self, link_type, link_width, link_score_color):

        g = self.__g

        min_weight = min(list(nx.get_edge_attributes(g, 'weight').values()))

        if link_type not in ["Pvalue", "Score"]:
            print("Error: Link type not valid. Choose either \"Pvalue\" or \"Score\".")
            sys.exit()
        else:
            if link_type == "Pvalue":
                if min_weight < 0:
                    print("Error: Link type invalid with edge values. Negative values present. Choose \"Score\" link type or change the edge values to p-values instead of scores.")
                    sys.exit()

        if not isinstance(link_width, float):
            if not isinstance(link_width, int):
                print("Error: Link width is not valid. Choose a float or integer value.")
                sys.exit()

        #if not type(restrict_link_distance) == bool:
        #    print("Error: Restrict maximum link distance is not valid. Choose either \"True\" or \"False\".")
        #    sys.exit()

        if link_score_color:
            if not isinstance(link_score_color, dict):
                print("Error: Link score color is not a valid data type. Choose a dictionary.")
                sys.exit()

            for key in link_score_color.keys():
                if key not in ['positive', 'negative']:
                    print("Error: Link score colour keys not valid. Use \"positive\" and \"negative\".")
                    sys.exit()
                else:

                    colorValue = link_score_color[key]

                    if "#" in str(colorValue):
                        if not matplotlib.colors.is_color_like(colorValue):
                            print("Error: The colour value for the {} link color is not valid. Choose a valid colour as a HTML/CSS name, hex code, or (R,G,B) tuple.".format(key))
                            sys.exit()
                    else:
                        try:
                            rgb_color = literal_eval(str(colorValue))
                            cValue = '#{:02x}{:02x}{:02x}'.format(rgb_color[0], rgb_color[1], rgb_color[2])
                        except ValueError:
                            cValue = colorValue

                        if not matplotlib.colors.is_color_like(cValue):
                            print("Error: The colour value for the {} link color is not valid. Choose a valid colour as a HTML/CSS name, hex code, or (R,G,B) tuple.".format(key))
                            sys.exit()

                        colorValue = cValue;

                    link_score_color[key] = colorValue;
        else:
            link_score_color = dict({'positive': 'red', 'negative': 'black'}) #Default to red and black

        return link_type, link_width, link_score_color

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
            graph_data['links'].append({
                "source": source,
                "target": target,
                "weight": G.edges[source, target]['weight']})
                #"length": G.edges[source, target]['len']})

        return graph_data

    def __getCSSnetwork(self):

        css_text = '''
        
        body {background-color: $backgroundColor;}
        
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
        
        select.nodeSizeDropDown {
            position: relative;
        }
        
        select.nodeColorDropDown {
            position: relative;
            left: 0px;
            top: 10px;
        }
        
        button.save {
            position: relative;
            left: 0px;
            top: 15px;            
        }
        
        text {
                    
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

    def __getJSnetwork(self):

        js_text = '''
        
        var groups = []  
                
        var params = JSON.parse(JSON.stringify($paramDict));
            
        var networkData = $networkData
    
        var width = params.width, height = params.height;
       
        var svg = d3.select("body").append("svg")
            .attr("width", width)
            .attr("height", height);
    
        svg.call(d3.zoom().on('zoom', zoomed))
            .on("dblclick.zoom", null);
    
        var simulation = d3.forceSimulation()
            .force("link", d3.forceLink().id(d => d.id))            
            .force("center", d3.forceCenter(width / 2, height / 2));        
    
        var container = svg.append('g');
    
        var search = d3.select("body").append('form').attr('onsubmit', 'return false;');
    
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
        
        if (params.link_type == "Score") {
            graph.links.forEach( function(d) {
                if (d.weight > 0) {
                    d.Color = params.link_score_color['positive'];
                } else {
                    d.Color = params.link_score_color['negative'];
                }
            });
        } else if (params.link_type == "Pvalue") {
            graph.links.forEach(function(d) {
                d.Color = "$foregroundColor";
            });
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
        
            graph.nodes.forEach( function (d) { d.Size = 10; });
        
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
                 
                graph.nodes.forEach( function (d) { if (isNaN(d[centrality])) { d.Size = linearScale(initScale(parseFloat(0))); } else { d.Size = linearScale(initScale(parseFloat(d[centrality]))); }});
              
            } else if (scaleType == "reverse_linear") {
                
                reversed_linear_values = []
                 
                scaledValues.forEach( function (d) { reversed_linear_values.push(parseFloat(1/d)); });
                 
                reversedLinearScale = d3.scaleLinear()
                    .domain(d3.extent(reversed_linear_values))
                    .range(range);
                
                graph.nodes.forEach( function (d) { if (isNaN(d[centrality])) { d.Size = reversedLinearScale(1 / initScale(parseFloat(0))); } else { d.Size = reversedLinearScale(1 / initScale(parseFloat(d[centrality]))); }});
                 
            } else if (scaleType == "log") {
               
                logScale = d3.scaleLog()
                    .domain(d3.extent(scaledValues))
                    .range(range);  	        
                         
                graph.nodes.forEach( function (d) { if (isNaN(d[centrality])) { d.Size = logScale(initScale(parseFloat(0))); } else { d.Size = logScale(initScale(parseFloat(d[centrality]))); }});
              
            } else if (scaleType == "reverse_log") {
                
                reversed_log_values = []
                 
                scaledValues.forEach( function (d) { reversed_log_values.push(parseFloat(1/d)); });
                 
                reversedLogScale = d3.scaleLog()
                    .domain(d3.extent(reversed_log_values))
                    .range(range);
                 
                graph.nodes.forEach( function (d) { if (isNaN(d[centrality])) { d.Size = reversedLogScale(1 / initScale(parseFloat(0))); } else { d.Size = reversedLogScale(1 / initScale(parseFloat(d[centrality]))); }});
                 
            } else if (scaleType == "square") {
               
                squareScale = d3.scalePow()
                    .domain(d3.extent(scaledValues))
                    .exponent(2)
                    .range(range);
                
                graph.nodes.forEach( function (d) { if (isNaN(d[centrality])) { d.Size = squareScale(initScale(parseFloat(0))); } else { d.Size = squareScale(initScale(parseFloat(d[centrality]))); }});
              
            } else if (scaleType == "reverse_square") {
               
                reversed_squared_values = []
                 
                scaledValues.forEach( function (d) { reversed_squared_values.push(parseFloat(1/d)); });
                 
                reversedSquareScale = d3.scalePow()
                    .domain(d3.extent(reversed_squared_values))
                    .exponent(2)
                    .range(range);
                
                graph.nodes.forEach( function (d) { if (isNaN(d[centrality])) { d.Size = reversedSquareScale(1 / initScale(parseFloat(0))); } else { d.Size = reversedSquareScale(1 / initScale(parseFloat(d[centrality]))); }});
              
            } else if (scaleType == "area") {
                
                area_values = []
                 
                scaledValues.forEach( function (d) { area_values.push(parseFloat(Math.PI * (d * d))); });
                 
                areaScale = d3.scaleLinear()
                    .domain(d3.extent(area_values))
                    .range(range);
                 
                graph.nodes.forEach( function (d) { if (isNaN(d[centrality])) { d.Size = areaScale(Math.PI * (initScale(parseFloat(0)) * initScale(parseFloat(0)))); } else { d.Size = areaScale(Math.PI * (initScale(parseFloat(d[centrality])) * initScale(parseFloat(d[centrality])))); }});
                 
            } else if (scaleType == "reverse_area") {
                
                reversed_area_values = []
                 
                scaledValues.forEach( function (d) { reversed_area_values.push(parseFloat(Math.PI * (parseFloat(1/d) * parseFloat(1/d)))); });
                 
                reversedAreaScale = d3.scaleLinear()
                    .domain(d3.extent(reversed_area_values))
                    .range(range);
                 
                graph.nodes.forEach( function (d) { if (isNaN(d[centrality])) { d.Size = reversedAreaScale(Math.PI * (1 / initScale(parseFloat(0))) * (1 / initScale(parseFloat(0)))); } else { d.Size = reversedAreaScale(Math.PI * (1 / initScale(parseFloat(d[centrality]))) * (1 / initScale(parseFloat(d[centrality])))); }});
                 
            } else if (scaleType == "volume") {
                
                volume_values = []
                 
                scaledValues.forEach( function (d) { volume_values.push(parseFloat(4 / 3 * (Math.PI * (d * d * d)))); });
                 
                volumeScale = d3.scaleLinear()
                    .domain(d3.extent(volume_values))
                    .range(range);
                 
                graph.nodes.forEach( function (d) { if (isNaN(d[centrality])) { d.Size = volumeScale(4 / 3 * (Math.PI * (initScale(parseFloat(0)) * initScale(parseFloat(0)) * initScale(parseFloat(0))))); } else { d.Size = volumeScale(4 / 3 * (Math.PI * (initScale(parseFloat(d[centrality])) * initScale(parseFloat(d[centrality])) * initScale(parseFloat(d[centrality]))))); }});
              
            } else if (scaleType == "reverse_volume") {
             
                reversed_volume_values = []             
                
                scaledValues.forEach( function (d) { reversed_volume_values.push(parseFloat(4 / 3 * (Math.PI * (parseFloat(1/d) * parseFloat(1/d) * parseFloat(1/d))))); });
                 
                reversedVolumeScale = d3.scaleLinear()
                    .domain(d3.extent(reversed_volume_values))
                    .range(range);
                
                graph.nodes.forEach( function (d) { if (isNaN(d[centrality])) { d.Size = reversedVolumeScale(4 / 3 * (Math.PI * ((1 / initScale(parseFloat(0))) * (1 / initScale(parseFloat(0))) * (1 / initScale(parseFloat(0)))))); } else { d.Size = reversedVolumeScale(4 / 3 * (Math.PI * ((1 / initScale(parseFloat(d[centrality]))) * (1 / initScale(parseFloat(d[centrality]))) * (1 / initScale(parseFloat(d[centrality])))))); }});
                   
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
        
        //if (params.restrict_link_distance == "true") {
        //    simulation            
        //        .force("charge", d3.forceManyBody().strength(params.chargeStrength).distanceMax(function (d) { return d.length; }))
        //        .force("collide", d3.forceCollide().radius( function (d) { return d.Size; }));
             
        //} else {
            
        //}
        
        simulation
            .force("charge", d3.forceManyBody().strength(params.chargeStrength).distanceMax(500))
            .force("collide", d3.forceCollide().radius( function (d) { return d.Size; }));
    
        graph.nodes.forEach(function(d) { d.x = d.x_position; d.y = d.y_position; if (typeof d.Group !== 'undefined') { groups.push(d.Group); } else if (typeof d.Color !== 'undefined') { groups.push(d.Color); } else { groups.push(1); } });
        
        var groups = Array.from(new Set(groups)) 
       
        update();
    
        function update() {
    
            node = node.data(graph.nodes, d => d.id);
    
            node.exit().remove();
        
            var newNode = node.enter().append("circle")
                    .attr('r', function(d, i) { return d.Size; })      		    
                    .attr("fill", function(d) { return d.Color; })  //d.Color; })
                    .attr('class', 'node')
                    .on('mouseover.tooltip', function(d) {
                            tooltip.transition()
                                .duration(300)
                                .style("opacity", .8);
              
                            if (typeof d.Group !== 'undefined') {
            
                                        tooltip.html("Name:" + d.Label + "<br/>group:" + d.Group)
                                                .style("left", (d3.event.pageX) + "px")
                                                .style("top", (d3.event.pageY + 10) + "px");
                  
                            } else {
            
                                        tooltip.html("Name:" + d.Label)
                                                .style("left", (d3.event.pageX) + "px")
                                                .style("top", (d3.event.pageY + 10) + "px");
                            }
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
              
                            if (typeof d.Group !== 'undefined') {
            
                                    tooltip.html("Name:" + d.Label + "<br/>group:" + d.Group)
                                            .style("left", (d3.event.pageX) + "px")
                                            .style("top", (d3.event.pageY + 10) + "px");
                  
                            } else {
            
                                    tooltip.html("Name:" + d.Label)
                                            .style("left", (d3.event.pageX) + "px")
                                            .style("top", (d3.event.pageY + 10) + "px");
                        }
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
    
            link = link.data(graph.links);
    
            link.exit().remove();
                    
            var newLink = link.enter().append("line")
                        .attr("class", "link")
                        .attr("stroke-width", params.link_width)
                        .style("stroke", function(d) { return d.Color; })
                        .on('mouseover.tooltip', function(d) {
                                tooltip.transition()
                                        .duration(300)
                                        .style("opacity", .8);
                                tooltip.html("Source: "+ d.source.Label + 
                                            "<br/>Target: " + d.target.Label +
                                            "<br/>" + params.link_type + ": "  + d.weight.toPrecision(3))
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
                //.distance(function(d) { return d.length; });
                    
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
             
        var slider = d3.select('body')
                            .append('p')
                            .style('color', '$foregroundColor')
                            .text(params.link_type + ' threshold: ');
    
        var sliderInitValue = '';
        var sliderMin = '';
        var sliderMax = '';
        var sliderValue = '';
        
        if (params.link_type == "Score") {
            sliderInitValue =  d3.min(graph.links, function(d) {return d.weight; }).toPrecision(5)
            sliderMin = scaleLinksLinear(d3.min(graph.links, function(d) {return d.weight; }))
            sliderMax = scaleLinksLinear(d3.max(graph.links, function(d) {return d.weight; }))
            sliderValue = scaleLinksLinear(d3.min(graph.links, function(d) {return d.weight; }))
        } else if (params.link_type == "Pvalue") {
            sliderInitValue =  d3.max(graph.links, function(d) {return d.weight; }).toPrecision(5)
            sliderMin = scaleLinksLog(Math.log(d3.min(graph.links, function(d) {return d.weight; })))
            sliderMax = scaleLinksLog(Math.log(d3.max(graph.links, function(d) {return d.weight; })))
            sliderValue = scaleLinksLog(Math.log(d3.max(graph.links, function(d) {return d.weight; })))
        }
    
        slider.append('label')
                .attr('for', 'threshold')
                .text(sliderInitValue);
        slider.append('input')
                .attr('type', 'range')
                .attr('min', sliderMin)
                .attr('max', sliderMax)
                .attr('value', sliderValue)
                .attr('id', 'threshold')
                .style('display', 'block')
                .on('input', function () {
                    
                    if (params.link_type == "Score") {
                        var threshold = scaleLinksLinear.invert(this.value);
                    } else if (params.link_type == "Pvalue")  {
                        var threshold = Math.exp(scaleLinksLog.invert(this.value));
                    }
                    
                    d3.select('label').text(threshold.toPrecision(5));
    
                    //Filter links
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
        
        if (Object.keys(params.node_size_scale).length != 0) {
        
            var nodeSizeDropdown = d3.select('body').append('div')                
                .append('select')
                .attr("class","nodeSizeDropdown")
                .on('change', function() { 
                    var centrality = this.value;
                
                    updateNodeSize(centrality)
                    
                    node.attr('r', function(d) { return d.Size; } );  
                
                    simulation.force("collide", d3.forceCollide().radius( function (d) { return d.Size; }));
                    simulation.alphaTarget(0.1).restart();
                });
                                
            nodeSizeDropdown.selectAll('option')
                .data(Object.keys(params.node_size_scale))
                .enter().append('option')		
                .text(function(d) { return d; });
        } else {
        
            var nodeSizeDropdown = d3.select('body').append('div')
                .append('select')
                .attr("class","nodeSizeDropdown");
            
            nodeSizeDropdown.selectAll('option')
                .data(['none'])
                .enter().append('option')		
                .text(function(d) { return d; });        
        }
        
        var nodeColorDropdown = d3.select('body').append('div')
            .append('select')
            .attr("class","nodeColorDropdown")
            .on('change', function() { 
                var colorScheme = this.value;
                            
                if (colorScheme == 'default') {
                    node.attr("fill", function(d) { return d.Color; })
                } else {
                    var color_palette = d3.scaleOrdinal().domain(groups)
                                                    .range(d3[colorScheme]);
                                   
                    node.attr("fill", function(d) { if (typeof d.Group !== 'undefined') { return color_palette(d.Group); } else if (typeof d.Color !== 'undefined') { return color_palette(d.Color); } else { return color_palette(1); } });
                }
    
                simulation.alphaTarget(0.1).restart();
            });
    
        nodeColorDropdown.selectAll('option')
            .data(['default','schemeCategory10','schemeAccent','schemeDark2','schemePaired','schemePastel1','schemePastel2','schemeSet1','schemeSet2','schemeSet3'])
            .enter().append('option')		
            .text(function(d) { return d; });
        
        d3.select('body').append('div')
            .append('button')
            .attr("class","save")
            .text("Save")
            .on('click', function(){
		        
                var options = {
                    canvg: window.canvg,
                    backgroundColor: "$backgroundColor",
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
                    .duration(5000)
                    .style('opacity', '1');
            d3.selectAll('.link').transition().duration(5000).style('stroke-opacity', '0.6');
        } 
        '''

        return js_text

    def __getHTMLnetwork(self):

        html = '''
        <body>
        
            <style> $css_text </style>
            
            <script src="https://d3js.org/d3.v5.min.js"></script>
            <script src="https://unpkg.com/d3-simple-slider"></script>
            <script src="https://github.com/canvg/canvg/blob/master/src/canvg.js"></script>
            <script src="https://exupero.org/saveSvgAsPng/src/saveSvgAsPng.js"></script>
             
            <script> $js_text </script>
                
        </body>
        '''

        return html

    def run(self):

        g = self.__g
        layout = self.__layout
        link_type = self.__link_type
        link_score_color = self.__link_score_color
        link_width = self.__link_width
        chargeStrength = self.__chargeStrength
        backgroundColor = self.__backgroundColor
        foregroundColor = self.__foregroundColor
        canvas_size = self.__canvas_size
        node_text_size = self.__node_text_size
        node_size_scale = self.__node_size_scale
        fix_nodes = self.__fix_nodes
        displayLabel = self.__displayLabel

        if fix_nodes:
            fixed = "true";
        else:
            fixed = "false";

        #if restrict_link_distance:
        #    max_link = "true";
        #else:
        #    max_link = "false";

        if link_type == 'Pvalue':
            operator = '<';
        else:
            operator = '>';

        if displayLabel:
            dispLabel = "true";
        else:
            dispLabel = "false";

        paramDict = dict({"width": canvas_size[0], "height": canvas_size[1], "link_type": link_type
                    , "link_score_color": link_score_color, "link_width": link_width, "node_text_size": node_text_size
                    , "displayLabel": dispLabel, "node_size_scale": node_size_scale, "chargeStrength": chargeStrength, "fix_nodes": fixed})

        if layout == "spring":
            pos = nx.spring_layout(g)
        else:
            pos = pygraphviz_layout(g, prog=layout)

        for idx, node in enumerate(g.nodes()):
            g.node[node]['x_position'] = pos[node][0]
            g.node[node]['y_position'] = pos[node][1]

        data = json.dumps(self.__generateJson(g), cls=self.__graphEncoder)

        css_text_template_network = Template(self.__getCSSnetwork());
        js_text_template_network = Template(self.__getJSnetwork());
        html_template_network = Template(self.__getHTMLnetwork());

        css_text_network = css_text_template_network.substitute({'backgroundColor': backgroundColor, 'foregroundColor': foregroundColor})

        js_text_network = js_text_template_network.substitute({'networkData': json.dumps(data)
                                                                  , 'backgroundColor': backgroundColor
                                                                  , 'foregroundColor': foregroundColor
                                                                  , 'operator': operator
                                                                  , 'paramDict': paramDict})

        html = html_template_network.substitute({'css_text': css_text_network, 'js_text': js_text_network})

        return html