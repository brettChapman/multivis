import os
import sys
import numpy as np
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
import webbrowser as wb
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
            node_size_scale: dictionary(Peak Table column name as index: dictionary('scale': ("linear", "reverse_linear", "log", "reverse_log", "square", "reverse_square", "area", "reverse_area", "volume", "reverse_volume", "ordinal")
                                                                                    , 'range': a number array of length 2 - minimum size to maximum size)) (default: sizes all nodes to 10 with no dropdown menu)
            node_color_scale: dictionary(Peak Table column name as index: dictionary('scale': ("linear", "reverse_linear", "log", "reverse_log", "square", "reverse_square", "area", "reverse_area", "volume", "reverse_volume", "ordinal")
            html_file: Name to save the HTML file as (default: 'springNetwork.html')
            backgroundColor: Set the background colour of the plot (default: 'white')
            foregroundColor: Set the foreground colour of the plot (default: 'black')
            chargeStrength: The charge strength of the spring-embedded network (force between nodes) (default: -120)
            groupByBlock: Setting to 'True' will group nodes by 'Block' if present in the data (default: False)
            groupFociStrength: Set the strength of foci for each group (default: 0.2)
            intraGroupStrength: Set the strength between each group (default: 0.01)
            groupLayoutTemplate: Set the layout template to use for grouping (default: 'treemap')
            node_text_size: The text size for each node (default: 15)
            fix_nodes: Setting to 'True' will fix nodes in place when manually moved (default: False)
            displayLabel: Setting to 'True' will set the node labels to the 'Label' column, otherwise it will set the labels to the 'Name' column from the Peak Table (default: False)
            node_data: Peak Table column names to include in the mouse over information (default: 'Name' and 'Label')
            link_type: The link type used in building the network (default: 'score')
            link_width: The width of the links (default: 0.5)
            pos_score_color: Colour value for positive scores. Can be HTML/CSS name, hex code, and (R,G,B) tuples (default: 'red')
            neg_score_color: Colour value for negative scores. Can be HTML/CSS name, hex code, and (R,G,B) tuples (default: 'black')

        build: : Generates the JavaScript embedded HTML code and writes to a HTML file and opens it in a browser.
        buildDashboard : Generates the JavaScript embedded HTML code in a dashboard format, writes to a HTML file and opens it in a browser.
    """

    def __init__(self, g):

        self.__g = self.__checkData(g)

        self.set_params()

    def set_params(self, node_size_scale={}, node_color_scale={}, html_file='springNetwork.html', backgroundColor='white', foregroundColor='black', chargeStrength=-120, groupByBlock=False, groupFociStrength=0.2, intraGroupStrength=0.01, groupLayoutTemplate='treemap', node_text_size=15, fix_nodes=False, displayLabel=False, node_data=['Name', 'Label'], link_type='score', link_width=0.5, pos_score_color='red', neg_score_color='black'):

        node_size_scale, node_color_scale, html_file, backgroundColor, foregroundColor, chargeStrength, groupByBlock, groupFociStrength, intraGroupStrength, groupLayoutTemplate, node_text_size, fix_nodes, displayLabel, node_data, link_type, link_width, pos_score_color, neg_score_color = self.__paramCheck(node_size_scale, node_color_scale, html_file, backgroundColor, foregroundColor, chargeStrength, groupByBlock, groupFociStrength, intraGroupStrength, groupLayoutTemplate, node_text_size, fix_nodes, displayLabel, node_data, link_type, link_width, pos_score_color, neg_score_color)

        self.__node_size_scale = node_size_scale;
        self.__node_color_scale = node_color_scale;
        self.__html_file = html_file;
        self.__backgroundColor = backgroundColor;
        self.__foregroundColor = foregroundColor;
        self.__chargeStrength = chargeStrength;
        self.__groupByBlock = groupByBlock;
        self.__groupFociStrength = groupFociStrength;
        self.__intraGroupStrength = intraGroupStrength;
        self.__groupLayoutTemplate = groupLayoutTemplate;
        self.__node_text_size = node_text_size;
        self.__fix_nodes = fix_nodes;
        self.__displayLabel = displayLabel;
        self.__node_data = node_data;
        self.__link_type = link_type;
        self.__link_width = link_width;
        self.__pos_score_color = pos_score_color;
        self.__neg_score_color = neg_score_color;

    def __process_params(self):

        g = self.__g
        link_type = self.__link_type.lower()
        link_width = self.__link_width
        chargeStrength = self.__chargeStrength
        groupByBlock = self.__groupByBlock
        groupFociStrength = self.__groupFociStrength
        intraGroupStrength = self.__intraGroupStrength
        groupLayoutTemplate = self.__groupLayoutTemplate
        node_text_size = self.__node_text_size
        node_size_scale = self.__node_size_scale
        node_color_scale = self.__node_color_scale
        fix_nodes = self.__fix_nodes
        displayLabel = self.__displayLabel
        node_data = self.__node_data

        if groupByBlock:
            useGroupInABox = "true"
        else:
            useGroupInABox = "false"

        if fix_nodes:
            fixed = "true";
        else:
            fixed = "false";

        if displayLabel:
            dispLabel = "true";
        else:
            dispLabel = "false";

        paramDict = dict({"link_type": link_type, "link_width": link_width, "node_text_size": node_text_size, "node_size_scale": node_size_scale,
                          "node_color_scale": node_color_scale, "displayLabel": dispLabel, "node_data": node_data, "chargeStrength": chargeStrength,
                          "useGroupInABox": useGroupInABox, "groupFociStrength": groupFociStrength, "intraGroupStrength": intraGroupStrength,
                          "groupLayoutTemplate": groupLayoutTemplate, "fix_nodes": fixed})

        data = json.dumps(self.__generateJson(g), cls=self.__graphEncoder)

        return data, paramDict

    def build(self):

        backgroundColor = self.__backgroundColor
        foregroundColor = self.__foregroundColor
        html_file = self.__html_file

        data, paramDict = self.__process_params()

        css_text_template_network = Template(self.__getCSS());
        js_text_template_network = Template(self.__getJS());
        html_template_network = Template(self.__getHTML());

        css_text_network = css_text_template_network.substitute({'backgroundColor': backgroundColor, 'foregroundColor': foregroundColor})

        #with open('test.txt', 'w') as f:
        #    f.write(json.dumps(data))
        #    f.close()

        js_text_network = js_text_template_network.substitute({'networkData': json.dumps(data)
                                                                  , 'backgroundColor': backgroundColor
                                                                  , 'foregroundColor': foregroundColor
                                                                  , 'paramDict': paramDict})

        html = html_template_network.substitute({'css_text': css_text_network, 'js_text': js_text_network})

        with open(html_file, 'w') as f:
            f.write(html)
            f.close()

        print("HTML writen to {}".format(html_file))

        wb.open_new('file://' + os.path.realpath(html_file))

    def buildDashboard(self):

        backgroundColor = self.__backgroundColor
        foregroundColor = self.__foregroundColor
        html_file = self.__html_file

        data, paramDict = self.__process_params()

        css_text_template_network = Template(self.__getCSSdashboard());
        js_text_template_network = Template(self.__getJSdashboard());
        html_template_network = Template(self.__getHTMLdashboard());

        css_text_network = css_text_template_network.substitute({'backgroundColor': backgroundColor, 'foregroundColor': foregroundColor})

        #with open('test.txt', 'w') as f:
        #    f.write(json.dumps(data))
        #    f.close()

        js_text_network = js_text_template_network.substitute({'networkData': json.dumps(data)
                                                                  , 'backgroundColor': backgroundColor
                                                                  , 'foregroundColor': foregroundColor
                                                                  , 'paramDict': paramDict})

        html = html_template_network.substitute({'css_text': css_text_network, 'js_text': js_text_network})

        html_file = html_file.split(".")[0] + "_dashboard.html"

        with open(html_file, 'w') as f:
            f.write(html)
            f.close()

        print("HTML writen to {}".format(html_file))

        wb.open('file://' + os.path.realpath(html_file))

    def __checkData(self, g):

        if not isinstance(g, nx.classes.graph.Graph):
            print("Error: A NetworkX graph was not entered. Please check your data.")
            sys.exit()

        return g

    def __paramCheck(self, node_size_scale, node_color_scale, html_file, backgroundColor, foregroundColor, chargeStrength, groupByBlock, groupFociStrength, intraGroupStrength, groupLayoutTemplate, node_text_size, fix_nodes, displayLabel, node_data, link_type, link_width, pos_score_color, neg_score_color):

        g = self.__g
        col_list = list(g.nodes[list(g.nodes.keys())[0]].keys()) + ['none']

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
                        if node_size_scale[column]['scale'] != 'ordinal':
                            try:
                                float(g.node[node][column])
                            except ValueError:
                                print("Error: Node size scale column {} contains invalid values. While scale is not ordinal, choose a column containing float or integer values.".format(column))
                                sys.exit()

                        for key in node_size_scale[column].keys():

                            if key not in ['scale', 'range']:
                                print("Error: Node size scale column {} dictionary keys are not valid. Use \"scale\" and \"range\".".format(column))
                                sys.exit()

                        if node_size_scale[column]['scale'].lower() not in ["linear", "reverse_linear", "log", "reverse_log", "square", "reverse_square", "area", "reverse_area", "volume", "reverse_volume", "ordinal"]:
                            print("Error: Node size scale column {} dictionary scale value not valid. Choose either \"linear\", \"reverse_linear\", \"log\", \"reverse_log\", \"square\", \"reverse_square\", \"area\", \"reverse_area\", \"volume\", \"reverse_volume\", \"ordinal\".".format(column))
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
            node_size_scale = dict({})  # Default to an empty dict

        if node_color_scale:
            if not isinstance(node_color_scale, dict):
                print("Error: Node color scale is not a valid data type. Provide a dictionary.")
                sys.exit()

            for column in node_color_scale.keys():
                if column not in col_list:
                    print("Error: Node color scale columns not valid. Choose one of {}.".format(', '.join(col_list)))
                    sys.exit()
                else:
                    for idx, node in enumerate(g.nodes()):
                        if node_color_scale[column]['scale'] != 'ordinal':
                            try:
                                float(g.node[node][column])
                            except ValueError:
                                print("Error: Node color scale column {} contains invalid values. While scale is not ordinal, choose a column containing float or integer values.".format(column))
                                sys.exit()

                        for key in node_color_scale[column].keys():

                            if key not in ['scale']:
                                print("Error: Node color scale column {} dictionary keys are not valid. Use \"scale\".".format(column))
                                sys.exit()

                        if node_color_scale[column]['scale'].lower() not in ["linear", "reverse_linear", "log", "reverse_log", "square", "reverse_square", "area", "reverse_area", "volume", "reverse_volume", "ordinal"]:
                            print("Error: Node color scale column {} dictionary scale value not valid. Choose either \"linear\", \"reverse_linear\", \"log\", \"reverse_log\", \"square\", \"reverse_square\", \"area\", \"reverse_area\", \"volume\", \"reverse_volume\", \"ordinal\".".format(column))
                            sys.exit()
        else:
            node_color_scale = dict({})  # Default to an empty dict

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

        if not type(groupByBlock) == bool:
            print("Error: Group by block is not valid. Choose either \"True\" or \"False\".")
            sys.exit()

        if not isinstance(groupFociStrength, float):
            if not isinstance(groupFociStrength, int):
                print("Error: Group foci strength is not valid. Choose a float or integer value.")
                sys.exit()

        if not isinstance(intraGroupStrength, float):
            if not isinstance(intraGroupStrength, int):
                print("Error: Intra group strength is not valid. Choose a float or integer value.")
                sys.exit()

        if groupLayoutTemplate.lower() not in ["treemap", "force"]:
            print("Error: Group layout template is not valid. Choose either \"treemap\" or \"force\".")
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

        return node_size_scale, node_color_scale, html_file, backgroundColor, foregroundColor, chargeStrength, groupByBlock, groupFociStrength, intraGroupStrength, groupLayoutTemplate, node_text_size, fix_nodes, displayLabel, node_data, link_type, link_width, pos_score_color, neg_score_color

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
        
        #slider {
            position: relative;
            top: 2px;
        }
        
        #nodeSizeDropdown, #nodeColorDropdown {  
            position: relative;
            margin-bottom: 10px;
            left: 0px;
            color: $foregroundColor;
        }
        
        #save {
            position: relative;
            left: 0px;
            color: $foregroundColor;
        }
        
        #springPanel {
            position: relative;            
            height: 800px;
            margin: 0 auto;
            margin-top: auto;
            margin-bottom: auto;
            margin-left: auto;
            margin-right: auto;
        }
        
        .row {
            padding-left: 15px;
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
        
        td:nth-child(odd) {
            background-color: #eee;
            font-weight: bold;
        }
               
        .slider.rzslider .rz-bar {
            background: #D3D3D3;
            height: 2px;
        }
        
        .slider.rzslider .rz-pointer {
            width: 8px;
            height: 20px;
            top: auto; /* to remove the default positioning */
            bottom: 0;
            background-color: #333;
            border-top-left-radius: 3px;
            border-top-right-radius: 3px;
        }
        
        .slider.rzslider .rz-pointer:after {
            display: none;
        }
        
        form.searchBar {
            padding-top: 4px;
        }
        
        /* Style the search field */
        form.searchBar input[type=text] {
            padding: 3px;
            font-size: 17px;
            border: 1px solid grey;
            float: left;
            top: 30px;
            width: 80%;
            height: 30px;
            background: #f1f1f1;
        }
        
        /* Style the submit button */
        form.searchBar button {
            float: left;
            width: 20%;
            height: 30px;
            padding: 3px;
            background: #2196F3;
            color: white;
            font-size: 17px;
            border: 1px solid grey;
            border-left: none; /* Prevent double borders */
            cursor: pointer;
        }
        
        form.searchBar button:hover {
            background: #0b7dda;
        }
        
        /* Clear floats */
        form.searchBar::after {
            content: "";
            clear: both;
            display: table;
        }
        '''

        return css_text

    def __getCSSdashboard(self):

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
        
        #slider {
            position: relative;
            top: 2px;
        }
        
        #nodeSizeDropdown, #nodeColorDropdown {  
            margin-bottom: 10px;
        }
        
        #save {  
            margin-bottom: -50px;
        }
        
        #springPanel {
            position: relative;
            width: 100%;
            height: 100%;
            /*height: 725px;*/
            margin: 0 auto;
            margin-top: auto;
            margin-bottom: auto;
            margin-left: auto;
            margin-right: auto;
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
        
        td:nth-child(odd) {
            background-color: #eee;
            font-weight: bold;
        }
               
        .slider.rzslider .rz-bar {
            background: #D3D3D3;
            height: 2px;
        }
        
        .slider.rzslider .rz-pointer {
            width: 8px;
            height: 20px;
            top: auto; /* to remove the default positioning */
            bottom: 0;
            background-color: #333;
            border-top-left-radius: 3px;
            border-top-right-radius: 3px;
        }
        
        .slider.rzslider .rz-pointer:after {
            display: none;
        }
        
        /* Style the search field */
        form.searchBar input[type=text] {
            padding: 3px;
            font-size: 17px;
            border: 1px solid grey;
            float: left;
            width: 80%;
            height: 30px;
            background: #f1f1f1;
        }
        
        /* Style the submit button */
        form.searchBar button {
            float: left;
            width: 20%;
            height: 30px;
            padding: 3px;
            background: #2196F3;
            color: white;
            font-size: 17px;
            border: 1px solid grey;
            border-left: none; /* Prevent double borders */
            cursor: pointer;
        }
        
        form.searchBar button:hover {
            background: #0b7dda;
        }
        
        /* Clear floats */
        form.searchBar::after {
            content: "";
            clear: both;
            display: table;
        }
        '''

        return css_text

    def __getJS(self):

        js_text = '''
        var networkData = $networkData
                
        var params = JSON.parse(JSON.stringify($paramDict));
            
        var canvas = document.getElementById("springPanel");
        var springNetwork = d3.select(canvas).append("svg").attr("id", "springNetwork");
        
        var redrawCount = 0;
        var prevRedrawCount = 0;
        
        function redraw(){
        
            if (redrawCount !== prevRedrawCount) {
                setTimeout(function(){
                    window.location.reload();
                });
                window.location.reload(); 
            }
            
            prevRedrawCount = redrawCount;

			redrawCount = redrawCount+1;
			
			var scheme_list = ['Category10','Accent','Dark2','Paired','Pastel1','Pastel2','Set1','Set2','Set3', 'Tableau10']
            var interpolate_list = ['BrBG', 'PRGn', 'PiYG', 'PuOr', 'RdBu', 'RdGy', 'RdYlBu', 'RdYlGn', 'Spectral', 'Blues', 'Greens', 'Greys', 'Oranges', 'Purples', 'Reds', 'Turbo', 'Viridis', 'Inferno', 'Magma', 'Plasma', 'Cividis', 'Warm', 'Cool', 'Cubehelix', 'BuGn', 'BuPu', 'GnBu', 'OrRd', 'PuBuGn', 'PuBu', 'PuRd', 'RdPu', 'YlGnBu', 'YlGn', 'YlOrBr', 'YlOrRd', 'Rainbow', 'Sinebow'];
            var color_options = scheme_list.concat(interpolate_list)
                        
            var colorDomain = [];
                    
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
        
            var toggle = 0;
        
            var tooltip = d3.select("body")
                .append("div")
                .attr("class", "tooltip")
                .style("opacity", 0);
        
            var graph = JSON.parse(networkData);
            
            var graphRec = JSON.parse(JSON.stringify(graph));
            
            if (params.link_type == "score") {            
                var link_type_text = "Score";
            } else if (params.link_type == "pvalue") {
                var link_type_text = "Pvalue";
            }
            
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
            
            if (Object.keys(params.node_color_scale).length === 0) {
                graph.nodes.forEach( function (d) { d.color = "#808080"; }); 
            } else {
                updateNodeColor(Object.keys(params.node_color_scale)[0], color_options[0])
            }
            
            function updateNodeSize(centrality) {
                
                var scaleType = params.node_size_scale[centrality].scale
                var range = params.node_size_scale[centrality].range
                
                var centrality_values = []
                graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { centrality_values.push(parseFloat(0)); } else { centrality_values.push(d[centrality]); }});
                
                scaledValues = []
                if (scaleType != "ordinal") {
                    centrality_values = centrality_values.map(function (x) {
                            return parseFloat(x);
                    });
                    
                    initScale = d3.scaleLinear()
                                    .domain(d3.extent(centrality_values))
                                    .range([1,10]);
                    
                    centrality_values.forEach( function (d) { scaledValues.push(initScale(parseFloat(d))); });
                } else {
                    scaledValues = centrality_values.reduce(function(a,b){if(a.indexOf(b)<0)a.push(b);return a;},[]);
                }
                                  
                if (scaleType == "linear") {
                    
                    linearScale = d3.scaleLinear()
                         .domain(d3.extent(scaledValues))
                         .range(range);
                     
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { d.size = linearScale(initScale(parseFloat(0))); } else { d.size = linearScale(initScale(parseFloat(d[centrality]))); }});
                  
                } else if (scaleType == "reverse_linear") {
                    
                    reversed_linear_values = []
                     
                    scaledValues.forEach( function (d) { reversed_linear_values.push(parseFloat(1/d)); });
                     
                    reversedLinearScale = d3.scaleLinear()
                        .domain(d3.extent(reversed_linear_values))
                        .range(range);
                    
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { d.size = reversedLinearScale(1 / initScale(parseFloat(0))); } else { d.size = reversedLinearScale(1 / initScale(parseFloat(d[centrality]))); }});
                     
                } else if (scaleType == "log") {
                   
                    logScale = d3.scaleLog()
                        .domain(d3.extent(scaledValues))
                        .range(range);  	        
                             
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { d.size = logScale(initScale(parseFloat(0))); } else { d.size = logScale(initScale(parseFloat(d[centrality]))); }});
                  
                } else if (scaleType == "reverse_log") {
                    
                    reversed_log_values = []
                     
                    scaledValues.forEach( function (d) { reversed_log_values.push(parseFloat(1/d)); });
                     
                    reversedLogScale = d3.scaleLog()
                        .domain(d3.extent(reversed_log_values))
                        .range(range);
                     
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { d.size = reversedLogScale(1 / initScale(parseFloat(0))); } else { d.size = reversedLogScale(1 / initScale(parseFloat(d[centrality]))); }});
                     
                } else if (scaleType == "square") {
                   
                    squareScale = d3.scalePow()
                        .domain(d3.extent(scaledValues))
                        .exponent(2)
                        .range(range);
                    
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { d.size = squareScale(initScale(parseFloat(0))); } else { d.size = squareScale(initScale(parseFloat(d[centrality]))); }});
                  
                } else if (scaleType == "reverse_square") {
                   
                    reversed_squared_values = []
                     
                    scaledValues.forEach( function (d) { reversed_squared_values.push(parseFloat(1/d)); });
                     
                    reversedSquareScale = d3.scalePow()
                        .domain(d3.extent(reversed_squared_values))
                        .exponent(2)
                        .range(range);
                    
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { d.size = reversedSquareScale(1 / initScale(parseFloat(0))); } else { d.size = reversedSquareScale(1 / initScale(parseFloat(d[centrality]))); }});
                  
                } else if (scaleType == "area") {
                    
                    area_values = []
                     
                    scaledValues.forEach( function (d) { area_values.push(parseFloat(Math.PI * (d * d))); });
                     
                    areaScale = d3.scaleLinear()
                        .domain(d3.extent(area_values))
                        .range(range);
                     
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { d.size = areaScale(Math.PI * (initScale(parseFloat(0)) * initScale(parseFloat(0)))); } else { d.size = areaScale(Math.PI * (initScale(parseFloat(d[centrality])) * initScale(parseFloat(d[centrality])))); }});
                     
                } else if (scaleType == "reverse_area") {
                    
                    reversed_area_values = []
                     
                    scaledValues.forEach( function (d) { reversed_area_values.push(parseFloat(Math.PI * (parseFloat(1/d) * parseFloat(1/d)))); });
                     
                    reversedAreaScale = d3.scaleLinear()
                        .domain(d3.extent(reversed_area_values))
                        .range(range);
                     
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { d.size = reversedAreaScale(Math.PI * (1 / initScale(parseFloat(0))) * (1 / initScale(parseFloat(0)))); } else { d.size = reversedAreaScale(Math.PI * (1 / initScale(parseFloat(d[centrality]))) * (1 / initScale(parseFloat(d[centrality])))); }});
                     
                } else if (scaleType == "volume") {
                    
                    volume_values = []
                     
                    scaledValues.forEach( function (d) { volume_values.push(parseFloat(4 / 3 * (Math.PI * (d * d * d)))); });
                     
                    volumeScale = d3.scaleLinear()
                        .domain(d3.extent(volume_values))
                        .range(range);
                     
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { d.size = volumeScale(4 / 3 * (Math.PI * (initScale(parseFloat(0)) * initScale(parseFloat(0)) * initScale(parseFloat(0))))); } else { d.size = volumeScale(4 / 3 * (Math.PI * (initScale(parseFloat(d[centrality])) * initScale(parseFloat(d[centrality])) * initScale(parseFloat(d[centrality]))))); }});
                  
                } else if (scaleType == "reverse_volume") {
                 
                    reversed_volume_values = []             
                    
                    scaledValues.forEach( function (d) { reversed_volume_values.push(parseFloat(4 / 3 * (Math.PI * (parseFloat(1/d) * parseFloat(1/d) * parseFloat(1/d))))); });
                     
                    reversedVolumeScale = d3.scaleLinear()
                        .domain(d3.extent(reversed_volume_values))
                        .range(range);
                    
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { d.size = reversedVolumeScale(4 / 3 * (Math.PI * ((1 / initScale(parseFloat(0))) * (1 / initScale(parseFloat(0))) * (1 / initScale(parseFloat(0)))))); } else { d.size = reversedVolumeScale(4 / 3 * (Math.PI * ((1 / initScale(parseFloat(d[centrality]))) * (1 / initScale(parseFloat(d[centrality]))) * (1 / initScale(parseFloat(d[centrality])))))); }});
                       
                } else if (scaleType == "ordinal") {
                
                    var ordinal_range = [...Array(scaledValues.length).keys()];
                    
                    initScale = d3.scaleLinear()
                                    .domain(d3.extent(ordinal_range))
                                    .range(range);
                    
                    scaled_range = []
                    ordinal_range.forEach( function (d) { scaled_range.push(initScale(d)); });
                
                    ordinalScale = d3.scaleOrdinal()
                         .domain(scaledValues)
                         .range(scaled_range);
                                        
                    graph.nodes.forEach( function (d) { d.size = ordinalScale(d[centrality]); });
                }
            }
            
            function updateNodeColor(centrality, colorOption) {
                var scaleType = params.node_color_scale[centrality].scale
                var range = [0,1]
                
                var centrality_values = []
                graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { centrality_values.push(parseFloat(0)); } else { centrality_values.push(d[centrality]); }});
                
                scaledValues = []
                if (scaleType != "ordinal") {
                    centrality_values = centrality_values.map(function (x) {
                            return parseFloat(x);
                    });
                    
                    initScale = d3.scaleLinear()
                                    .domain(d3.extent(centrality_values))
                                    .range([1,10]);
                    
                    centrality_values.forEach( function (d) { scaledValues.push(initScale(parseFloat(d))); });
                } else {
                    scaledValues = centrality_values.reduce(function(a,b){if(a.indexOf(b)<0)a.push(b);return a;},[]);
                }        
                
                colorDomain = []                
                if (scaleType == "linear") {
                    
                    linearScale = d3.scaleLinear()
                         .domain(d3.extent(scaledValues))
                         .range(range);
                     
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { d.color = linearScale(initScale(parseFloat(0))); } else { d.color = linearScale(initScale(parseFloat(d[centrality]))); }});
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { colorDomain.push(linearScale(initScale(parseFloat(0)))); } else { colorDomain.push(linearScale(initScale(parseFloat(d[centrality])))); }});
                  
                } else if (scaleType == "reverse_linear") {
                    
                    reversed_linear_values = []
                     
                    scaledValues.forEach( function (d) { reversed_linear_values.push(parseFloat(1/d)); });
                     
                    reversedLinearScale = d3.scaleLinear()
                        .domain(d3.extent(reversed_linear_values))
                        .range(range);
                    
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { d.color = reversedLinearScale(1 / initScale(parseFloat(0))); } else { d.color = reversedLinearScale(1 / initScale(parseFloat(d[centrality]))); }});
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { colorDomain.push(reversedLinearScale(1 / initScale(parseFloat(0)))); } else { colorDomain.push(reversedLinearScale(1 / initScale(parseFloat(d[centrality])))); }});
                     
                } else if (scaleType == "log") {
                   
                    logScale = d3.scaleLog()
                        .domain(d3.extent(scaledValues))
                        .range(range);  	        
                    
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { d.color = logScale(initScale(parseFloat(0))); } else { d.color = logScale(initScale(parseFloat(d[centrality]))); }});
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { colorDomain.push(logScale(initScale(parseFloat(0)))); } else { colorDomain.push(logScale(initScale(parseFloat(d[centrality])))); }});
                  
                } else if (scaleType == "reverse_log") {
                    
                    reversed_log_values = []
                     
                    scaledValues.forEach( function (d) { reversed_log_values.push(parseFloat(1/d)); });
                     
                    reversedLogScale = d3.scaleLog()
                        .domain(d3.extent(reversed_log_values))
                        .range(range);
                    
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { d.color = reversedLogScale(1 / initScale(parseFloat(0))); } else { d.color = reversedLogScale(1 / initScale(parseFloat(d[centrality]))); }});
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { colorDomain.push(reversedLogScale(1 / initScale(parseFloat(0)))); } else { colorDomain.push(reversedLogScale(1 / initScale(parseFloat(d[centrality])))); }});
                     
                } else if (scaleType == "square") {
                   
                    squareScale = d3.scalePow()
                        .domain(d3.extent(scaledValues))
                        .exponent(2)
                        .range(range);
                    
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { d.color = squareScale(initScale(parseFloat(0))); } else { d.color = squareScale(initScale(parseFloat(d[centrality]))); }});
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { colorDomain.push(squareScale(initScale(parseFloat(0)))); } else { colorDomain.push(squareScale(initScale(parseFloat(d[centrality])))); }});
                  
                } else if (scaleType == "reverse_square") {
                   
                    reversed_squared_values = []
                     
                    scaledValues.forEach( function (d) { reversed_squared_values.push(parseFloat(1/d)); });
                     
                    reversedSquareScale = d3.scalePow()
                        .domain(d3.extent(reversed_squared_values))
                        .exponent(2)
                        .range(range);
                    
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { d.color = reversedSquareScale(1 / initScale(parseFloat(0))); } else { d.color = reversedSquareScale(1 / initScale(parseFloat(d[centrality]))); }});
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { colorDomain.push(reversedSquareScale(1 / initScale(parseFloat(0)))); } else { colorDomain.push(reversedSquareScale(1 / initScale(parseFloat(d[centrality])))); }});
                  
                } else if (scaleType == "area") {
                    
                    area_values = []
                     
                    scaledValues.forEach( function (d) { area_values.push(parseFloat(Math.PI * (d * d))); });
                     
                    areaScale = d3.scaleLinear()
                        .domain(d3.extent(area_values))
                        .range(range);
                                        
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { d.color = areaScale(Math.PI * (initScale(parseFloat(0)) * initScale(parseFloat(0)))); } else { d.color = areaScale(Math.PI * (initScale(parseFloat(d[centrality])) * initScale(parseFloat(d[centrality])))); }});
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { colorDomain.push(areaScale(Math.PI * (initScale(parseFloat(0)) * initScale(parseFloat(0))))); } else { colorDomain.push(areaScale(Math.PI * (initScale(parseFloat(d[centrality])) * initScale(parseFloat(d[centrality]))))); }});
                     
                } else if (scaleType == "reverse_area") {
                    
                    reversed_area_values = []
                     
                    scaledValues.forEach( function (d) { reversed_area_values.push(parseFloat(Math.PI * (parseFloat(1/d) * parseFloat(1/d)))); });
                     
                    reversedAreaScale = d3.scaleLinear()
                        .domain(d3.extent(reversed_area_values))
                        .range(range);
                    
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { d.color = reversedAreaScale(Math.PI * (1 / initScale(parseFloat(0))) * (1 / initScale(parseFloat(0)))); } else { d.color = reversedAreaScale(Math.PI * (1 / initScale(parseFloat(d[centrality]))) * (1 / initScale(parseFloat(d[centrality])))); }});
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { colorDomain.push(reversedAreaScale(Math.PI * (1 / initScale(parseFloat(0))) * (1 / initScale(parseFloat(0))))); } else { colorDomain.push(reversedAreaScale(Math.PI * (1 / initScale(parseFloat(d[centrality]))) * (1 / initScale(parseFloat(d[centrality]))))); }});
                     
                } else if (scaleType == "volume") {
                    
                    volume_values = []
                     
                    scaledValues.forEach( function (d) { volume_values.push(parseFloat(4 / 3 * (Math.PI * (d * d * d)))); });
                     
                    volumeScale = d3.scaleLinear()
                        .domain(d3.extent(volume_values))
                        .range(range);
                    
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { d.color = volumeScale(4 / 3 * (Math.PI * (initScale(parseFloat(0)) * initScale(parseFloat(0)) * initScale(parseFloat(0))))); } else { d.color = volumeScale(4 / 3 * (Math.PI * (initScale(parseFloat(d[centrality])) * initScale(parseFloat(d[centrality])) * initScale(parseFloat(d[centrality]))))); }});
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { colorDomain.push(volumeScale(4 / 3 * (Math.PI * (initScale(parseFloat(0)) * initScale(parseFloat(0)) * initScale(parseFloat(0)))))); } else { colorDomain.push(volumeScale(4 / 3 * (Math.PI * (initScale(parseFloat(d[centrality])) * initScale(parseFloat(d[centrality])) * initScale(parseFloat(d[centrality])))))); }});
                  
                } else if (scaleType == "reverse_volume") {
                 
                    reversed_volume_values = []             
                    
                    scaledValues.forEach( function (d) { reversed_volume_values.push(parseFloat(4 / 3 * (Math.PI * (parseFloat(1/d) * parseFloat(1/d) * parseFloat(1/d))))); });
                     
                    reversedVolumeScale = d3.scaleLinear()
                        .domain(d3.extent(reversed_volume_values))
                        .range(range);
                    
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { d.color = reversedVolumeScale(4 / 3 * (Math.PI * ((1 / initScale(parseFloat(0))) * (1 / initScale(parseFloat(0))) * (1 / initScale(parseFloat(0)))))); } else { d.color = reversedVolumeScale(4 / 3 * (Math.PI * ((1 / initScale(parseFloat(d[centrality]))) * (1 / initScale(parseFloat(d[centrality]))) * (1 / initScale(parseFloat(d[centrality])))))); }});
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { colorDomain.push(reversedVolumeScale(4 / 3 * (Math.PI * ((1 / initScale(parseFloat(0))) * (1 / initScale(parseFloat(0))) * (1 / initScale(parseFloat(0))))))); } else { colorDomain.push(reversedVolumeScale(4 / 3 * (Math.PI * ((1 / initScale(parseFloat(d[centrality]))) * (1 / initScale(parseFloat(d[centrality]))) * (1 / initScale(parseFloat(d[centrality]))))))); }});
                       
                } else if (scaleType == "ordinal") {
                
                    var ordinal_range = [...Array(scaledValues.length).keys()];
                    
                    initScale = d3.scaleLinear()
                                    .domain(d3.extent(ordinal_range))
                                    .range(range);
                                                    
                    scaled_range = []
                    ordinal_range.forEach( function (d) { scaled_range.push(initScale(d)); });
                    
                    ordinalScale = d3.scaleOrdinal()
                        .domain(scaledValues)
                        .range(scaled_range);
                                        
                    graph.nodes.forEach( function (d) { d.color = ordinalScale(d[centrality]); });
                    graph.nodes.forEach( function (d) { colorDomain.push(ordinalScale(d[centrality])); });
                }
                        
                if (scheme_list.includes(colorOption)) {
                    var color_palette = d3.scaleQuantize()
                                            .domain(d3.extent(colorDomain))
                                            .range(d3["scheme" + colorOption]);
                } else if (interpolate_list.includes(colorOption)) {
                    
                    if (colorOption == 'Cubehelix') {
                        colorOption = colorOption.concat('Default')
                    }
                    
                    var color_palette = d3.scaleSequential()
                                            .interpolator(d3["interpolate" + colorOption])
                                            .domain(colorDomain);
                }                
                
                node.attr("fill", function(d) { if (typeof d[centrality] === 'undefined') { return "#808080"; } else { return color_palette(d.color); }});
            }
            
            simulation
                .force("charge", d3.forceManyBody().strength(params.chargeStrength).distanceMax(500))            
                .force("collide", d3.forceCollide().radius( function (d) { return d.size; }));
        
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
                
                //Test to see if there are multiple blocks in the data. If none then set useGroupInABox to false
                var blocks = []
                graph.nodes.forEach(function(n) { if (n.Block !== undefined) { blocks.push(n.Block) }}); 
                
                if (params.useGroupInABox == "true") {
                    var useGroupInABox = true;
                    
                    if (blocks.length == 0) {
                        useGroupInABox = false;
                    }
                } else {
                    var useGroupInABox = false;
                }
                
                if (useGroupInABox == true) {
                    var groupingForce = forceInABox()
                            .strength(params.groupFociStrength)
                            .template(params.groupLayoutTemplate)
                            .groupBy("Block")
                            .linkStrengthIntraCluster(params.intraGroupStrength)
                            .size([width, height]);
                    
                    simulation
                        .nodes(graph.nodes)
                        .on("tick", ticked)
                        .force("group", groupingForce);
                } else {
                    simulation
                        .nodes(graph.nodes)
                        .on("tick", ticked);
                }
                          
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
            
            Number.prototype.countDecimals = function () {
                if(Math.floor(this.valueOf()) === this.valueOf()) return 0;
        
                var value = 0;
                var check = this.toString().includes("e-");
                
                if (check) {
                    
    	            var value = this.toString().split("-")[1];
                     
                } else {
    	            
                    var value1 = this.toString().split(".")[1];
                    var value2 = value1.trimLeft("0");
                     
                    var value = value1.length - value2.length + 1;
                }        
                
                return value
            }
            
            var sliderMin = '';
            var sliderMax = '';
            
            var sliderScoreDecimalPlaces = 5;
            
            if (params.link_type == "score") {
                sliderMin = Number(d3.min(graph.links, function(d) {return d.weight; }).toFixed(sliderScoreDecimalPlaces))
                sliderMax = Number(d3.max(graph.links, function(d) {return d.weight; }).toFixed(sliderScoreDecimalPlaces))
                sliderStep = 0.01;
                sliderPrecision = sliderScoreDecimalPlaces;
            } else if (params.link_type == "pvalue") {
                sliderMin = Number(d3.min(graph.links, function(d) {return d.weight; }).toFixed(Number(d3.min(graph.links, function(d) {return d.weight; }).countDecimals())))
                sliderMax = Number(d3.max(graph.links, function(d) {return d.weight; }).toFixed(Number(d3.min(graph.links, function(d) {return d.weight; }).countDecimals())))
                sliderStep = Number(d3.min(graph.links, function(d) {return d.weight; }).toFixed(Number(d3.min(graph.links, function(d) {return d.weight; }).countDecimals())))
                sliderPrecision = Number(d3.min(graph.links, function(d) {return d.weight; }).countDecimals())
            }
            
            var app = angular.module('rzSliderDemo', ['rzSlider']);
            
            app.controller('MainCtrl', function ($$scope) {
                
                $$scope.node_size_options = Object.keys(params.node_size_scale);
  				$$scope.selectedNodeSizeOption = $$scope.node_size_options[0];    
                
                $$scope.updateNodeSize = function() {
                
                    var centrality = $$scope.selectedNodeSizeOption;
                    
                    if (typeof centrality != 'undefined') {
                        updateNodeSize(centrality)
                    }
                        
                    node.attr('r', function(d) { return d.size; } );  
                    
                    simulation.force("collide", d3.forceCollide().radius( function (d) { return d.size; }));
                    simulation.alphaTarget(0.1).restart();    										
  				}
  				
  				var centrality = $$scope.selectedNodeSizeOption;
  				
  				if (typeof centrality != 'undefined') {
                    updateNodeSize(centrality)                  
                }
  				
  				node.attr('r', function(d) { return d.size; } );  
                    
                simulation.force("collide", d3.forceCollide().radius( function (d) { return d.size; }));
                simulation.alphaTarget(0.1).restart();
                
                $$scope.node_coloring_options = Object.keys(params.node_color_scale);
  				$$scope.selectedNodeColorOption = $$scope.node_coloring_options[0];
  				
  				$$scope.scheme_list = scheme_list;
                   
                $$scope.interpolate_list = interpolate_list;
                    
                $$scope.color_options = color_options;
                              
                $$scope.selectedColorOption = $$scope.color_options[0]; 				
  				
                $$scope.updateNodeColor = function() {
                
                    var nodeColorOption = $$scope.selectedNodeColorOption
                
                    if (typeof nodeColorOption != 'undefined') {                        
                        var colorOption = $$scope.selectedColorOption             
                        var scaleType = params.node_color_scale[nodeColorOption].scale                    
                    
                        if (scaleType == "ordinal") {
                        
                            if (!scheme_list.includes(colorOption)) {
                                $$scope.selectedColorOption = scheme_list[0];
                                colorOption = $$scope.selectedColorOption
                            }
                        
                            $$scope.color_options = scheme_list;
                        } else {
                            $$scope.color_options = color_options;
                        }
                    
                        updateNodeColor(nodeColorOption, colorOption)
                    } else {
                        $$scope.node_coloring_options = ['None']
                        $$scope.selectedNodeColorOption = 'None'
                        $$scope.color_options = ['Grey']
                        $$scope.selectedColorOption = 'Grey'
                        
                        node.attr("fill", function(d) { return d.color; })           
                    }
                    
                    simulation.alphaTarget(0.1).restart();
                }
                
                var nodeColorOption = $$scope.selectedNodeColorOption         
                    
                if (typeof nodeColorOption != 'undefined') {
                    var colorOption = $$scope.selectedColorOption             
                    var scaleType = params.node_color_scale[nodeColorOption].scale
                    
                    if (scaleType == "ordinal") {
                    
                        if (!scheme_list.includes(colorOption)) {
                            $$scope.selectedColorOption = scheme_list[0];
                            colorOption = $$scope.selectedColorOption
                        }                    
                    
                        $$scope.color_options = scheme_list;
                    } else {
                        $$scope.color_options = color_options;
                    }
                    
                    updateNodeColor(nodeColorOption, colorOption)
                } else {
                    $$scope.node_coloring_options = ['None']
                    $$scope.selectedNodeColorOption = 'None'
                    $$scope.color_options = ['Grey']
                    $$scope.selectedColorOption = 'Grey'
                        
                    node.attr("fill", function(d) { return d.color; })           
                }
                
                simulation.alphaTarget(0.1).restart();
                                
                $$scope.savebutton = function () {
                	
                      var options = {
                                canvg: window.canvg,
                                backgroundColor: 'white',
                                height: height+100,
                                width: width+100,
                                left: -50,
                                top: -50,
                                scale: 5/window.devicePixelRatio,
                                encoderOptions: 1,
                                ignoreMouse : true,
                                ignoreAnimation : true,
                        }
		                		                
                        saveSvgAsPng(d3.select('svg#springNetwork').node(), "networkPlot.png", options);           					
        		}
        		
        		$$scope.searchNodes = function () {
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
            	         	
            	var slider_options = {
        		        showSelectionBar: true,                    
            			floor: sliderMin,
                        ceil: sliderMax,                          		
                        step: sliderStep,
            			precision: sliderPrecision,                          	
            			getSelectionBarColor: function() { return '#2AE02A'; },
            			getPointerColor: function() { return '#D3D3D3'; },
            			pointerSize: 1,
            			onChange: function () {
              
                            var minThreshold = $$scope.slider.minValue
                            var maxThreshold = $$scope.slider.maxValue
                                
                            graph.links.splice(0, graph.links.length);
                            graphRec.links.forEach( function (d) { if ((d.weight >= minThreshold) && (d.weight <= maxThreshold)) { graph.links.push(d); }});
                                
                            //Update link dictionary
                            linkedByIndex = {} 
                            graphRec.links.forEach( function (d) {
                                if ((d.weight >= minThreshold) && (d.weight <= maxThreshold)) {
                                                                  
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
            			}
        		}
            	
            	if (params.link_type == "pvalue") {
            	    slider_options['logScale'] = true;
            	}
            	
            	$$scope.slider = {
        				minValue: sliderMin,
        				maxValue: sliderMax,                     
                        options: slider_options
    			};
			});
        
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

    def __getJSdashboard(self):

        js_text = '''
        var networkData = $networkData
        
        var params = JSON.parse(JSON.stringify($paramDict));
        
        var canvas = document.getElementById("springPanel");
        var springNetwork = d3.select(canvas).append("svg").attr("id", "springNetwork");
        
        var redrawCount = 0;
        var prevRedrawCount = 0;
        
        function redraw(){
        
            if (redrawCount !== prevRedrawCount) {
                setTimeout(function(){
                    window.location.reload();
                });
                window.location.reload(); 
            }
            
            prevRedrawCount = redrawCount;

			redrawCount = redrawCount+1;
			
			var scheme_list = ['Category10','Accent','Dark2','Paired','Pastel1','Pastel2','Set1','Set2','Set3', 'Tableau10']
            var interpolate_list = ['BrBG', 'PRGn', 'PiYG', 'PuOr', 'RdBu', 'RdGy', 'RdYlBu', 'RdYlGn', 'Spectral', 'Blues', 'Greens', 'Greys', 'Oranges', 'Purples', 'Reds', 'Turbo', 'Viridis', 'Inferno', 'Magma', 'Plasma', 'Cividis', 'Warm', 'Cool', 'Cubehelix', 'BuGn', 'BuPu', 'GnBu', 'OrRd', 'PuBuGn', 'PuBu', 'PuRd', 'RdPu', 'YlGnBu', 'YlGn', 'YlOrBr', 'YlOrRd', 'Rainbow', 'Sinebow'];
            var color_options = scheme_list.concat(interpolate_list)
                        
            var colorDomain = [];
            
            var width = canvas.clientWidth;
            var height = window.innerHeight/1.22;

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

            var toggle = 0;
            
            var graph = JSON.parse(networkData);
            
            var graphRec = JSON.parse(JSON.stringify(graph));

            if (params.link_type == "score") {            
                var link_type_text = "Score";
            } else if (params.link_type == "pvalue") {
                var link_type_text = "Pvalue";
            }

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
                        
            if (Object.keys(params.node_color_scale).length === 0) {
                graph.nodes.forEach( function (d) { d.color = "#808080"; }); 
            } else {
                updateNodeColor(Object.keys(params.node_color_scale)[0], color_options[0])
            }

            function updateNodeSize(centrality) {
                
                var scaleType = params.node_size_scale[centrality].scale
                var range = params.node_size_scale[centrality].range
                
                var centrality_values = []
                graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { centrality_values.push(parseFloat(0)); } else { centrality_values.push(d[centrality]); }});
                
                scaledValues = []
                if (scaleType != "ordinal") {
                    centrality_values = centrality_values.map(function (x) {
                            return parseFloat(x);
                    });
                    
                    initScale = d3.scaleLinear()
                                    .domain(d3.extent(centrality_values))
                                    .range([1,10]);
                    
                    centrality_values.forEach( function (d) { scaledValues.push(initScale(parseFloat(d))); });
                } else {                
                    scaledValues = centrality_values.reduce(function(a,b){if(a.indexOf(b)<0)a.push(b);return a;},[]);
                }
                                  
                if (scaleType == "linear") {
                    
                    linearScale = d3.scaleLinear()
                         .domain(d3.extent(scaledValues))
                         .range(range);
                     
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { d.size = linearScale(initScale(parseFloat(0))); } else { d.size = linearScale(initScale(parseFloat(d[centrality]))); }});
                  
                } else if (scaleType == "reverse_linear") {
                    
                    reversed_linear_values = []
                     
                    scaledValues.forEach( function (d) { reversed_linear_values.push(parseFloat(1/d)); });
                     
                    reversedLinearScale = d3.scaleLinear()
                        .domain(d3.extent(reversed_linear_values))
                        .range(range);
                    
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { d.size = reversedLinearScale(1 / initScale(parseFloat(0))); } else { d.size = reversedLinearScale(1 / initScale(parseFloat(d[centrality]))); }});
                     
                } else if (scaleType == "log") {
                   
                    logScale = d3.scaleLog()
                        .domain(d3.extent(scaledValues))
                        .range(range);  	        
                             
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { d.size = logScale(initScale(parseFloat(0))); } else { d.size = logScale(initScale(parseFloat(d[centrality]))); }});
                  
                } else if (scaleType == "reverse_log") {
                    
                    reversed_log_values = []
                     
                    scaledValues.forEach( function (d) { reversed_log_values.push(parseFloat(1/d)); });
                     
                    reversedLogScale = d3.scaleLog()
                        .domain(d3.extent(reversed_log_values))
                        .range(range);
                     
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { d.size = reversedLogScale(1 / initScale(parseFloat(0))); } else { d.size = reversedLogScale(1 / initScale(parseFloat(d[centrality]))); }});
                     
                } else if (scaleType == "square") {
                   
                    squareScale = d3.scalePow()
                        .domain(d3.extent(scaledValues))
                        .exponent(2)
                        .range(range);
                    
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { d.size = squareScale(initScale(parseFloat(0))); } else { d.size = squareScale(initScale(parseFloat(d[centrality]))); }});
                  
                } else if (scaleType == "reverse_square") {
                   
                    reversed_squared_values = []
                     
                    scaledValues.forEach( function (d) { reversed_squared_values.push(parseFloat(1/d)); });
                     
                    reversedSquareScale = d3.scalePow()
                        .domain(d3.extent(reversed_squared_values))
                        .exponent(2)
                        .range(range);
                    
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { d.size = reversedSquareScale(1 / initScale(parseFloat(0))); } else { d.size = reversedSquareScale(1 / initScale(parseFloat(d[centrality]))); }});
                  
                } else if (scaleType == "area") {
                    
                    area_values = []
                     
                    scaledValues.forEach( function (d) { area_values.push(parseFloat(Math.PI * (d * d))); });
                     
                    areaScale = d3.scaleLinear()
                        .domain(d3.extent(area_values))
                        .range(range);
                     
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { d.size = areaScale(Math.PI * (initScale(parseFloat(0)) * initScale(parseFloat(0)))); } else { d.size = areaScale(Math.PI * (initScale(parseFloat(d[centrality])) * initScale(parseFloat(d[centrality])))); }});
                     
                } else if (scaleType == "reverse_area") {
                    
                    reversed_area_values = []
                     
                    scaledValues.forEach( function (d) { reversed_area_values.push(parseFloat(Math.PI * (parseFloat(1/d) * parseFloat(1/d)))); });
                     
                    reversedAreaScale = d3.scaleLinear()
                        .domain(d3.extent(reversed_area_values))
                        .range(range);
                     
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { d.size = reversedAreaScale(Math.PI * (1 / initScale(parseFloat(0))) * (1 / initScale(parseFloat(0)))); } else { d.size = reversedAreaScale(Math.PI * (1 / initScale(parseFloat(d[centrality]))) * (1 / initScale(parseFloat(d[centrality])))); }});
                     
                } else if (scaleType == "volume") {
                    
                    volume_values = []
                     
                    scaledValues.forEach( function (d) { volume_values.push(parseFloat(4 / 3 * (Math.PI * (d * d * d)))); });
                     
                    volumeScale = d3.scaleLinear()
                        .domain(d3.extent(volume_values))
                        .range(range);
                     
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { d.size = volumeScale(4 / 3 * (Math.PI * (initScale(parseFloat(0)) * initScale(parseFloat(0)) * initScale(parseFloat(0))))); } else { d.size = volumeScale(4 / 3 * (Math.PI * (initScale(parseFloat(d[centrality])) * initScale(parseFloat(d[centrality])) * initScale(parseFloat(d[centrality]))))); }});
                  
                } else if (scaleType == "reverse_volume") {
                 
                    reversed_volume_values = []             
                    
                    scaledValues.forEach( function (d) { reversed_volume_values.push(parseFloat(4 / 3 * (Math.PI * (parseFloat(1/d) * parseFloat(1/d) * parseFloat(1/d))))); });
                     
                    reversedVolumeScale = d3.scaleLinear()
                        .domain(d3.extent(reversed_volume_values))
                        .range(range);
                    
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { d.size = reversedVolumeScale(4 / 3 * (Math.PI * ((1 / initScale(parseFloat(0))) * (1 / initScale(parseFloat(0))) * (1 / initScale(parseFloat(0)))))); } else { d.size = reversedVolumeScale(4 / 3 * (Math.PI * ((1 / initScale(parseFloat(d[centrality]))) * (1 / initScale(parseFloat(d[centrality]))) * (1 / initScale(parseFloat(d[centrality])))))); }});
                       
                } else if (scaleType == "ordinal") {
                
                    var ordinal_range = [...Array(scaledValues.length).keys()];
                    
                    initScale = d3.scaleLinear()
                                    .domain(d3.extent(ordinal_range))
                                    .range(range);
                    
                    scaled_range = []
                    ordinal_range.forEach( function (d) { scaled_range.push(initScale(d)); });
                
                    ordinalScale = d3.scaleOrdinal()
                         .domain(scaledValues)
                         .range(scaled_range);                
                                        
                    graph.nodes.forEach( function (d) { d.size = ordinalScale(d[centrality]); });
                }
            }
            
            function updateNodeColor(centrality, colorOption) {
                var scaleType = params.node_color_scale[centrality].scale
                var range = [0,1]
                  
                var centrality_values = []
                graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { centrality_values.push(parseFloat(0)); } else { centrality_values.push(d[centrality]); }});
                
                scaledValues = []
                if (scaleType != "ordinal") {
                    centrality_values = centrality_values.map(function (x) {
                            return parseFloat(x);
                    });
                    
                    initScale = d3.scaleLinear()
                                    .domain(d3.extent(centrality_values))
                                    .range([1,10]);
                    
                    centrality_values.forEach( function (d) { scaledValues.push(initScale(parseFloat(d))); });
                } else {                
                    scaledValues = centrality_values.reduce(function(a,b){if(a.indexOf(b)<0)a.push(b);return a;},[]);
                }        
                
                colorDomain = []                
                if (scaleType == "linear") {
                    
                    linearScale = d3.scaleLinear()
                         .domain(d3.extent(scaledValues))
                         .range(range);
                     
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { d.color = linearScale(initScale(parseFloat(0))); } else { d.color = linearScale(initScale(parseFloat(d[centrality]))); }});
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { colorDomain.push(linearScale(initScale(parseFloat(0)))); } else { colorDomain.push(linearScale(initScale(parseFloat(d[centrality])))); }});
                  
                } else if (scaleType == "reverse_linear") {
                    
                    reversed_linear_values = []
                     
                    scaledValues.forEach( function (d) { reversed_linear_values.push(parseFloat(1/d)); });
                     
                    reversedLinearScale = d3.scaleLinear()
                        .domain(d3.extent(reversed_linear_values))
                        .range(range);
                    
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { d.color = reversedLinearScale(1 / initScale(parseFloat(0))); } else { d.color = reversedLinearScale(1 / initScale(parseFloat(d[centrality]))); }});
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { colorDomain.push(reversedLinearScale(1 / initScale(parseFloat(0)))); } else { colorDomain.push(reversedLinearScale(1 / initScale(parseFloat(d[centrality])))); }});
                     
                } else if (scaleType == "log") {
                   
                    logScale = d3.scaleLog()
                        .domain(d3.extent(scaledValues))
                        .range(range);  	        
                    
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { d.color = logScale(initScale(parseFloat(0))); } else { d.color = logScale(initScale(parseFloat(d[centrality]))); }});
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { colorDomain.push(logScale(initScale(parseFloat(0)))); } else { colorDomain.push(logScale(initScale(parseFloat(d[centrality])))); }});
                  
                } else if (scaleType == "reverse_log") {
                    
                    reversed_log_values = []
                     
                    scaledValues.forEach( function (d) { reversed_log_values.push(parseFloat(1/d)); });
                     
                    reversedLogScale = d3.scaleLog()
                        .domain(d3.extent(reversed_log_values))
                        .range(range);
                    
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { d.color = reversedLogScale(1 / initScale(parseFloat(0))); } else { d.color = reversedLogScale(1 / initScale(parseFloat(d[centrality]))); }});
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { colorDomain.push(reversedLogScale(1 / initScale(parseFloat(0)))); } else { colorDomain.push(reversedLogScale(1 / initScale(parseFloat(d[centrality])))); }});
                     
                } else if (scaleType == "square") {
                   
                    squareScale = d3.scalePow()
                        .domain(d3.extent(scaledValues))
                        .exponent(2)
                        .range(range);
                    
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { d.color = squareScale(initScale(parseFloat(0))); } else { d.color = squareScale(initScale(parseFloat(d[centrality]))); }});
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { colorDomain.push(squareScale(initScale(parseFloat(0)))); } else { colorDomain.push(squareScale(initScale(parseFloat(d[centrality])))); }});
                  
                } else if (scaleType == "reverse_square") {
                   
                    reversed_squared_values = []
                     
                    scaledValues.forEach( function (d) { reversed_squared_values.push(parseFloat(1/d)); });
                     
                    reversedSquareScale = d3.scalePow()
                        .domain(d3.extent(reversed_squared_values))
                        .exponent(2)
                        .range(range);
                    
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { d.color = reversedSquareScale(1 / initScale(parseFloat(0))); } else { d.color = reversedSquareScale(1 / initScale(parseFloat(d[centrality]))); }});
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { colorDomain.push(reversedSquareScale(1 / initScale(parseFloat(0)))); } else { colorDomain.push(reversedSquareScale(1 / initScale(parseFloat(d[centrality])))); }});
                  
                } else if (scaleType == "area") {
                    
                    area_values = []
                     
                    scaledValues.forEach( function (d) { area_values.push(parseFloat(Math.PI * (d * d))); });
                     
                    areaScale = d3.scaleLinear()
                        .domain(d3.extent(area_values))
                        .range(range);
                                        
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { d.color = areaScale(Math.PI * (initScale(parseFloat(0)) * initScale(parseFloat(0)))); } else { d.color = areaScale(Math.PI * (initScale(parseFloat(d[centrality])) * initScale(parseFloat(d[centrality])))); }});
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { colorDomain.push(areaScale(Math.PI * (initScale(parseFloat(0)) * initScale(parseFloat(0))))); } else { colorDomain.push(areaScale(Math.PI * (initScale(parseFloat(d[centrality])) * initScale(parseFloat(d[centrality]))))); }});
                     
                } else if (scaleType == "reverse_area") {
                    
                    reversed_area_values = []
                     
                    scaledValues.forEach( function (d) { reversed_area_values.push(parseFloat(Math.PI * (parseFloat(1/d) * parseFloat(1/d)))); });
                     
                    reversedAreaScale = d3.scaleLinear()
                        .domain(d3.extent(reversed_area_values))
                        .range(range);
                    
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { d.color = reversedAreaScale(Math.PI * (1 / initScale(parseFloat(0))) * (1 / initScale(parseFloat(0)))); } else { d.color = reversedAreaScale(Math.PI * (1 / initScale(parseFloat(d[centrality]))) * (1 / initScale(parseFloat(d[centrality])))); }});
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { colorDomain.push(reversedAreaScale(Math.PI * (1 / initScale(parseFloat(0))) * (1 / initScale(parseFloat(0))))); } else { colorDomain.push(reversedAreaScale(Math.PI * (1 / initScale(parseFloat(d[centrality]))) * (1 / initScale(parseFloat(d[centrality]))))); }});
                     
                } else if (scaleType == "volume") {
                    
                    volume_values = []
                     
                    scaledValues.forEach( function (d) { volume_values.push(parseFloat(4 / 3 * (Math.PI * (d * d * d)))); });
                     
                    volumeScale = d3.scaleLinear()
                        .domain(d3.extent(volume_values))
                        .range(range);
                    
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { d.color = volumeScale(4 / 3 * (Math.PI * (initScale(parseFloat(0)) * initScale(parseFloat(0)) * initScale(parseFloat(0))))); } else { d.color = volumeScale(4 / 3 * (Math.PI * (initScale(parseFloat(d[centrality])) * initScale(parseFloat(d[centrality])) * initScale(parseFloat(d[centrality]))))); }});
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { colorDomain.push(volumeScale(4 / 3 * (Math.PI * (initScale(parseFloat(0)) * initScale(parseFloat(0)) * initScale(parseFloat(0)))))); } else { colorDomain.push(volumeScale(4 / 3 * (Math.PI * (initScale(parseFloat(d[centrality])) * initScale(parseFloat(d[centrality])) * initScale(parseFloat(d[centrality])))))); }});
                  
                } else if (scaleType == "reverse_volume") {
                 
                    reversed_volume_values = []             
                    
                    scaledValues.forEach( function (d) { reversed_volume_values.push(parseFloat(4 / 3 * (Math.PI * (parseFloat(1/d) * parseFloat(1/d) * parseFloat(1/d))))); });
                     
                    reversedVolumeScale = d3.scaleLinear()
                        .domain(d3.extent(reversed_volume_values))
                        .range(range);
                    
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { d.color = reversedVolumeScale(4 / 3 * (Math.PI * ((1 / initScale(parseFloat(0))) * (1 / initScale(parseFloat(0))) * (1 / initScale(parseFloat(0)))))); } else { d.color = reversedVolumeScale(4 / 3 * (Math.PI * ((1 / initScale(parseFloat(d[centrality]))) * (1 / initScale(parseFloat(d[centrality]))) * (1 / initScale(parseFloat(d[centrality])))))); }});
                    graph.nodes.forEach( function (d) { if (typeof d[centrality] === 'undefined') { colorDomain.push(reversedVolumeScale(4 / 3 * (Math.PI * ((1 / initScale(parseFloat(0))) * (1 / initScale(parseFloat(0))) * (1 / initScale(parseFloat(0))))))); } else { colorDomain.push(reversedVolumeScale(4 / 3 * (Math.PI * ((1 / initScale(parseFloat(d[centrality]))) * (1 / initScale(parseFloat(d[centrality]))) * (1 / initScale(parseFloat(d[centrality]))))))); }});
                       
                } else if (scaleType == "ordinal") {
                
                    var ordinal_range = [...Array(scaledValues.length).keys()];
                    
                    initScale = d3.scaleLinear()
                                    .domain(d3.extent(ordinal_range))
                                    .range(range);
                                                    
                    scaled_range = []
                    ordinal_range.forEach( function (d) { scaled_range.push(initScale(d)); });
                    
                    ordinalScale = d3.scaleOrdinal()
                        .domain(scaledValues)
                        .range(scaled_range);
                                        
                    graph.nodes.forEach( function (d) { d.color = ordinalScale(d[centrality]); });
                    graph.nodes.forEach( function (d) { colorDomain.push(ordinalScale(d[centrality])); });
                }
                
                if (scheme_list.includes(colorOption)) {
                    var color_palette = d3.scaleQuantize()
                                            .domain(d3.extent(colorDomain))
                                            .range(d3["scheme" + colorOption]);
                } else if (interpolate_list.includes(colorOption)) {
                
                    if (colorOption == 'Cubehelix') {
                        colorOption = colorOption.concat('Default')
                    }
                                    
                    var color_palette = d3.scaleSequential()
                                            .interpolator(d3["interpolate" + colorOption])
                                            .domain(colorDomain);
                }                
                
                node.attr("fill", function(d) { if (typeof d[centrality] === 'undefined') { return "#808080"; } else { return color_palette(d.color); }});
            }
            
            simulation
                .force("charge", d3.forceManyBody().strength(params.chargeStrength).distanceMax(500))            
                .force("collide", d3.forceCollide().radius( function (d) { return d.size; }));

            update();

            function update() {

                node = node.data(graph.nodes, d => d.id);

                node.exit().remove();

                var newNode = node.enter().append("circle")
                        .attr('r', function(d, i) { return d.size; })      		    
                        .attr("fill", function(d) { return d.color; })
                        .attr('class', 'node')
                        .on('mouseover', function(d) {
                                
                                peak_data = params.node_data;

                                if (Number.isNaN(Number(d[peak_data[0]]))) {                                
                                    var init_value = d[peak_data[0]]                                    
                                } else if (typeof Number(d[peak_data[0]]) == 'number') { 
                                    var init_value = Number(d[peak_data[0]]).toFixed(3)
                                }
                                
                                html_line = "\\""+ peak_data[0] + "\\",\\"" + init_value + "\\"";

                                peak_data.forEach(function(p) { 

                                    if (p !== peak_data[0]) {
                                        if (Number.isNaN(Number(d[p]))) {
                                            var data_value = d[p];
                                        } else if (typeof Number(d[p]) == 'number') {
                                            var data_value = Number(d[p]).toFixed(3);
                                        }

                                        html_line = html_line + "\\n\\"" + p + "\\",\\"" + data_value + "\\"";

                                    }
                                });
                                
                                displayNodeData(html_line)
                        })      		    
                        .on('dblclick', releaseNode)
                        .on('click', fade(0.1))
                        .on("mouseout", function() {
                                d3.select('#nodedataPanel').selectAll("*").remove();                                
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
                        .on('mouseover', function(d) {
                        
                                peak_data = params.node_data;

                                if (Number.isNaN(Number(d[peak_data[0]]))) {                                
                                    var init_value = d[peak_data[0]]                                    
                                } else if (typeof Number(d[peak_data[0]]) == 'number') { 
                                    var init_value = Number(d[peak_data[0]]).toFixed(3)
                                }

                                html_line = "\\""+ peak_data[0] + "\\",\\"" + init_value + "\\"";

                                peak_data.forEach(function(p) { 

                                    if (p !== peak_data[0]) {
                                        if (Number.isNaN(Number(d[p]))) {
                                            var data_value = d[p];
                                        } else if (typeof Number(d[p]) == 'number') {
                                            var data_value = Number(d[p]).toFixed(3);
                                        }

                                        html_line = html_line + "\\n\\"" + p + "\\",\\"" + data_value + "\\"";

                                    }
                                });
                                
                                displayNodeData(html_line)                                
                        })
                        .on('dblclick', releaseNode)
                        .on('click', fade(0.1))      		    
                        .on("mouseout", function() {
                                d3.select('#nodedataPanel').selectAll("*").remove();                                
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
                            .on('mouseover', function(d) {
                                    
                                    if (params.displayLabel == "true") {                                                
                                        var source = d.source.Label;
                                        var target = d.target.Label;
                                    } else { 
                                        var source = d.source.Name;
                                        var target = d.target.Name;
                                    }
                                    
                                    html_line = "\\"Source\\",\\""+ source + "\\"\\n\\"Target\\",\\"" + target + "\\"\\n\\"" + link_type_text + "\\"," + d.weight.toPrecision(3)                 
                                    
                                    displayNodeData(html_line)                                    
                            })
                            .on("mouseout", function() {
                                    d3.select('#nodedataPanel').selectAll("*").remove();                                    
                            });                            

                link = link.merge(newLink);
                
                //Test to see if there are multiple blocks in the data. If none then set useGroupInABox to false
                var blocks = []
                graph.nodes.forEach(function(n) { if (n.Block !== undefined) { blocks.push(n.Block) }}); 
                
                if (params.useGroupInABox == "true") {
                    var useGroupInABox = true;
                    
                    if (blocks.length == 0) {
                        useGroupInABox = false;
                    }
                } else {
                    var useGroupInABox = false;
                }
                                
                if (useGroupInABox == true) {
                    var groupingForce = forceInABox()
                            .strength(params.groupFociStrength)
                            .template(params.groupLayoutTemplate)
                            .groupBy("Block")
                            .linkStrengthIntraCluster(params.intraGroupStrength)
                            .size([width, height]);
                    
                    simulation
                        .nodes(graph.nodes)
                        .on("tick", ticked)
                        .force("group", groupingForce);
                } else {
                    simulation
                        .nodes(graph.nodes)
                        .on("tick", ticked);
                }
                
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
            
            Number.prototype.countDecimals = function () {
                if(Math.floor(this.valueOf()) === this.valueOf()) return 0;
        
                var value = 0;
                var check = this.toString().includes("e-");
                
                if (check) {
                    
    	            var value = this.toString().split("-")[1];
                     
                } else {
    	            
                    var value1 = this.toString().split(".")[1];
                    var value2 = value1.trimLeft("0");
                     
                    var value = value1.length - value2.length + 1;
                }        
                
                return value
            }
                        
            var sliderMin = '';
            var sliderMax = '';
            
            var sliderScoreDecimalPlaces = 5;
            
            if (params.link_type == "score") {
                sliderMin = Number(d3.min(graph.links, function(d) {return d.weight; }).toFixed(sliderScoreDecimalPlaces))
                sliderMax = Number(d3.max(graph.links, function(d) {return d.weight; }).toFixed(sliderScoreDecimalPlaces))
                sliderStep = 0.01;
                sliderPrecision = sliderScoreDecimalPlaces;
            } else if (params.link_type == "pvalue") {                
                sliderMin = Number(d3.min(graph.links, function(d) {return d.weight; }).toFixed(Number(d3.min(graph.links, function(d) {return d.weight; }).countDecimals())))
                sliderMax = Number(d3.max(graph.links, function(d) {return d.weight; }).toFixed(Number(d3.min(graph.links, function(d) {return d.weight; }).countDecimals())))
                sliderStep = Number(d3.min(graph.links, function(d) {return d.weight; }).toFixed(Number(d3.min(graph.links, function(d) {return d.weight; }).countDecimals())))
                sliderPrecision = Number(d3.min(graph.links, function(d) {return d.weight; }).countDecimals())
            }
            
            var app = angular.module('rzSliderDemo', ['rzSlider']);
            
            app.controller('MainCtrl', function ($$scope) {
                
                $$scope.node_size_options = Object.keys(params.node_size_scale);
  				$$scope.selectedNodeSizeOption = $$scope.node_size_options[0];    
                
                $$scope.updateNodeSize = function() {
                  
                    var centrality = $$scope.selectedNodeSizeOption;
                    
                    if (typeof centrality != 'undefined') {
                        updateNodeSize(centrality)
                    }
                        
                    node.attr('r', function(d) { return d.size; } );  
                    
                    simulation.force("collide", d3.forceCollide().radius( function (d) { return d.size; }));
                    simulation.alphaTarget(0.1).restart();    										
  				}
  				
  				var centrality = $$scope.selectedNodeSizeOption;
  				
  				if (typeof centrality != 'undefined') {
                    updateNodeSize(centrality)                  
                }
  				
  				node.attr('r', function(d) { return d.size; } );  
                    
                simulation.force("collide", d3.forceCollide().radius( function (d) { return d.size; }));
                simulation.alphaTarget(0.1).restart();
                
                $$scope.node_coloring_options = Object.keys(params.node_color_scale);
  				$$scope.selectedNodeColorOption = $$scope.node_coloring_options[0];
  				
  				$$scope.scheme_list = scheme_list;
                   
                $$scope.interpolate_list = interpolate_list;
                    
                $$scope.color_options = color_options;
                              
                $$scope.selectedColorOption = $$scope.color_options[0];
                
                $$scope.updateNodeColor = function() {
                
                    var nodeColorOption = $$scope.selectedNodeColorOption
                
                    if (typeof nodeColorOption != 'undefined') {                        
                        var colorOption = $$scope.selectedColorOption             
                        var scaleType = params.node_color_scale[nodeColorOption].scale                    
                                        
                        if (scaleType == "ordinal") {
                        
                            if (!scheme_list.includes(colorOption)) {
                                $$scope.selectedColorOption = scheme_list[0];
                                colorOption = $$scope.selectedColorOption
                            }
                        
                            $$scope.color_options = scheme_list;                          
                        } else {
                            $$scope.color_options = color_options;
                        }
                    
                        updateNodeColor(nodeColorOption, colorOption)
                    } else {
                        $$scope.node_coloring_options = ['None']
                        $$scope.selectedNodeColorOption = 'None'
                        $$scope.color_options = ['Grey']
                        $$scope.selectedColorOption = 'Grey'
                        
                        node.attr("fill", function(d) { return d.color; })           
                    }
                    
                    simulation.alphaTarget(0.1).restart();
                }
                
                var nodeColorOption = $$scope.selectedNodeColorOption         
                    
                if (typeof nodeColorOption != 'undefined') {
                    var colorOption = $$scope.selectedColorOption             
                    var scaleType = params.node_color_scale[nodeColorOption].scale
                    
                    if (scaleType == "ordinal") {
                    
                        if (!scheme_list.includes(colorOption)) {
                            $$scope.selectedColorOption = scheme_list[0];
                            colorOption = $$scope.selectedColorOption
                        }
                    
                        $$scope.color_options = scheme_list;
                    } else {
                        $$scope.color_options = color_options;
                    }
                    
                    updateNodeColor(nodeColorOption, colorOption)
                } else {
                    $$scope.node_coloring_options = ['None']
                    $$scope.selectedNodeColorOption = 'None'
                    $$scope.color_options = ['Grey']
                    $$scope.selectedColorOption = 'Grey'
                        
                    node.attr("fill", function(d) { return d.color; })           
                }
                
                simulation.alphaTarget(0.1).restart();
                
                $$scope.savebutton = function () {
                	
                      var options = {
                                canvg: window.canvg,
                                backgroundColor: 'white',
                                height: height+100,
                                width: width+100,
                                left: -50,
                                top: -50,
                                scale: 5/window.devicePixelRatio,
                                encoderOptions: 1,
                                ignoreMouse : true,
                                ignoreAnimation : true,
                        }
		                		                
                        saveSvgAsPng(d3.select('svg#springNetwork').node(), "networkPlot.png", options);           					
        		}
        		
        		$$scope.searchNodes = function () {
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
            	
            	var slider_options = {
        		        showSelectionBar: true,                    
            			floor: sliderMin,
                        ceil: sliderMax,                          		
                        step: sliderStep,
            			precision: sliderPrecision,                          	
            			getSelectionBarColor: function() { return '#2AE02A'; },
            			getPointerColor: function() { return '#D3D3D3'; },
            			pointerSize: 1,
            			onChange: function () {
            			    
            			    var minThreshold = $$scope.slider.minValue
                            var maxThreshold = $$scope.slider.maxValue
                                
                            graph.links.splice(0, graph.links.length);
                            graphRec.links.forEach( function (d) { if ((d.weight >= minThreshold) && (d.weight <= maxThreshold)) { graph.links.push(d); }});
                                
                            //Update link dictionary
                            linkedByIndex = {} 
                            graphRec.links.forEach( function (d) {
                                   
                                if ((d.weight >= minThreshold) && (d.weight <= maxThreshold)) {
                                                                  
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
            			}
        		}
            	
            	if (params.link_type == "pvalue") {
            	    slider_options['logScale'] = true;
            	}
            	
            	$$scope.slider = {
        				minValue: sliderMin,
        				maxValue: sliderMax,
                        options: slider_options
    			};
			});

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
            
            function displayNodeData(datasetText) {
            
                d3.select('#nodedataPanel').selectAll("*").remove();
            
  				var rows  = d3.csvParseRows(datasetText),
      			table = d3.select('#nodedataPanel').append('table')
                						.style("border-collapse", "collapse")
                						.style("border", "2px black solid");
        				
                var tablebody = table.append("tbody");
        				
                rows = tablebody
                		.selectAll("tr")
                		.data(rows)
                		.enter()
                		.append("tr");
 
 				cells = rows.selectAll("td")            		
                		.data(function(d) { return d; })
                		.enter()
                		.append("td")
                		.text(function(d) { return d; })
                        .style("border", "1px black solid")
                        .style("font-size", "15px");
			};
        }

        redraw();

        window.addEventListener("resize", redraw); 
        '''

        return js_text

    def __getHTML(self):

        html = '''
        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <head>
	        <meta charset="utf-8">
	        <meta http-equiv="X-UA-Compatible" content="IE=edge">
	        <meta name="viewport" content="width=device-width, initial-scale=1.0">
	        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.2.1/css/bootstrap.min.css">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
            <link rel="stylesheet" type="text/css" href="https://rawgit.com/rzajac/angularjs-slider/master/dist/rzslider.css">
        </head>

        <style> $css_text </style>

        <body ng-app="rzSliderDemo">
		        <div class="row" ng-controller="MainCtrl">
			        <div class="col-4">
				        <div class="row">
                            <form class="searchBar">
                                <input id="searchTerm" type="text" placeholder="Search.." name="search">
                                <button type="submit" data-ng-click="searchNodes()"><i class="fa fa-search"></i></button>
                            </form>
                        </div>
                        
                        <rzslider id="slider" class="slider" rz-slider-model="slider.minValue" rz-slider-high="slider.maxValue" rz-slider-options="slider.options"></rzslider>
                        
                        <div id="nodeSizeDropdown" class="row">Size nodes by 
                            <select ng-options="o for o in node_size_options" data-ng-model="selectedNodeSizeOption" ng-change="updateNodeSize()"></select>
                        </div>
                       
                        <div id="nodeColorDropdown" class="row">Colour nodes by 
                            <select ng-options="o for o in node_coloring_options" data-ng-model="selectedNodeColorOption" ng-change="updateNodeColor()"></select> using
                            <select ng-options="o for o in color_options" data-ng-model="selectedColorOption" ng-change="updateNodeColor()"></select> colour palette
                        </div>
              
                        <div id="save" class="row">
                            <button class="mb-4" data-ng-click="savebutton()">Save</button>
                        </div>
					</div>		
			    </div>
			    
                <div id="springPanel"></div>
        </body>
	    
	    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>	
	    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.2.1/js/bootstrap.min.js"></script>
	    
	    <script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.4.8/angular.min.js"></script>
	    <script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.4.8/angular-animate.min.js"></script>
	    <script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.4.8/angular-aria.min.js"></script>
	    <script src="https://ajax.googleapis.com/ajax/libs/angular_material/1.0.0/angular-material.min.js"></script>        		
	    <script src="https://rawgit.com/rzajac/angularjs-slider/master/dist/rzslider.js"></script>
	    
        <script src="https://d3js.org/d3.v5.min.js"></script>
        <script src="https://unpkg.com/force-in-a-box/dist/forceInABox.js"></script>
        
        <script>
            (function(){var g=typeof exports!="undefined"&&exports||this;var b='<?xml version="1.0" standalone="no"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">';function e(h){return h&&h.lastIndexOf("http",0)==0&&h.lastIndexOf(window.location.host)==-1}function a(k,m){var h=k.querySelectorAll("image");var l=h.length;if(l==0){m()}for(var j=0;j<h.length;j++){(function(q){var o=q.getAttributeNS("http://www.w3.org/1999/xlink","href");if(o){if(e(o.value)){console.warn("Cannot render embedded images linking to external hosts: "+o.value);return}}var p=document.createElement("canvas");var i=p.getContext("2d");var n=new Image();o=o||q.getAttribute("href");n.src=o;n.onload=function(){p.width=n.width;p.height=n.height;i.drawImage(n,0,0);q.setAttributeNS("http://www.w3.org/1999/xlink","href",p.toDataURL("image/png"));l--;if(l==0){m()}};n.onerror=function(){console.log("Could not load "+o);l--;if(l==0){m()}}})(h[j])}}function f(h,k){var r="";var q=document.styleSheets;for(var o=0;o<q.length;o++){try{var u=q[o].cssRules}catch(s){console.warn("Stylesheet could not be loaded: "+q[o].href);continue}if(u!=null){for(var n=0;n<u.length;n++){var t=u[n];if(typeof(t.style)!="undefined"){var p=null;try{p=h.querySelector(t.selectorText)}catch(m){console.warn('Invalid CSS selector "'+t.selectorText+'"',m)}if(p){var l=k?k(t.selectorText):t.selectorText;r+=l+" { "+t.style.cssText+" }\\n"}else{if(t.cssText.match(/^@font-face/)){r+=t.cssText+"\\n"}}}}}}return r}function d(i,k,j){var h=(i.viewBox.baseVal&&i.viewBox.baseVal[j])||(k.getAttribute(j)!==null&&!k.getAttribute(j).match(/%$$/)&&parseInt(k.getAttribute(j)))||i.getBoundingClientRect()[j]||parseInt(k.style[j])||parseInt(window.getComputedStyle(i).getPropertyValue(j));return(typeof h==="undefined"||h===null||isNaN(parseFloat(h)))?0:h}function c(h){h=encodeURIComponent(h);h=h.replace(/%([0-9A-F]{2})/g,function(i,j){var k=String.fromCharCode("0x"+j);return k==="%"?"%25":k});return decodeURIComponent(h)}g.svgAsDataUri=function(j,i,h){i=i||{};i.scale=i.scale||1;var k="http://www.w3.org/2000/xmlns/";a(j,function(){var u=document.createElement("div");var r=j.cloneNode(true);var l,t;if(j.tagName=="svg"){l=i.width||d(j,r,"width");t=i.height||d(j,r,"height")}else{if(j.getBBox){var o=j.getBBox();l=o.x+o.width;t=o.y+o.height;r.setAttribute("transform",r.getAttribute("transform").replace(/translate\(.*?\)/,""));var p=document.createElementNS("http://www.w3.org/2000/svg","svg");p.appendChild(r);r=p}else{console.error("Attempted to render non-SVG element",j);return}}r.setAttribute("version","1.1");r.setAttributeNS(k,"xmlns","http://www.w3.org/2000/svg");r.setAttributeNS(k,"xmlns:xlink","http://www.w3.org/1999/xlink");r.setAttribute("width",l*i.scale);r.setAttribute("height",t*i.scale);r.setAttribute("viewBox",[i.left||0,i.top||0,l,t].join(" "));u.appendChild(r);var q=f(j,i.selectorRemap);var v=document.createElement("style");v.setAttribute("type","text/css");v.innerHTML="<![CDATA[\\n"+q+"\\n]]>";var n=document.createElement("defs");n.appendChild(v);r.insertBefore(n,r.firstChild);var p=b+u.innerHTML;var m="data:image/svg+xml;base64,"+window.btoa(c(p));if(h){h(m)}})};g.svgAsPngUri=function(j,i,h){g.svgAsDataUri(j,i,function(k){var l=new Image();l.onload=function(){var n=document.createElement("canvas");n.width=l.width;n.height=l.height;var o=n.getContext("2d");if(i&&i.backgroundColor){o.fillStyle=i.backgroundColor;o.fillRect(0,0,n.width,n.height)}o.drawImage(l,0,0);var m=document.createElement("a");h(n.toDataURL("image/png"))};l.src=k})};g.saveSvgAsPng=function(j,i,h){h=h||{};g.svgAsPngUri(j,h,function(l){var k=document.createElement("a");k.download=i;k.href=l;document.body.appendChild(k);k.addEventListener("click",function(m){k.parentNode.removeChild(k)});k.click()})}})();
        </script>

        <script> $js_text </script>
        '''

        return html

    def __getHTMLdashboard(self):

        html = ''' 
        <meta name="viewport" content="width=device-width, height=device-height, initial-scale=1.0">

        <style> $css_text </style>

        <head>
	        <meta charset="utf-8">
	        <meta http-equiv="X-UA-Compatible" content="IE=edge">
	        <meta name="viewport" content="width=device-width, initial-scale=1.0">	
	        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.2.1/css/bootstrap.min.css">	
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
            <link rel="stylesheet" type="text/css" href="https://rawgit.com/rzajac/angularjs-slider/master/dist/rzslider.css">
        </head>
        
        <body ng-app="rzSliderDemo">
	        <div class="container-fluid py-5">
		        <div class="row" ng-controller="MainCtrl">
			        <div class="col-lg-9 col-12">
				        <div class="row">
					        <div class="col-md-12 mb-3">
						        <div class="card summary">
							        <div class="card-header">
								        <h4>Spring-embedded network</h4>
							        </div>
							        <div class="card-body">
								        <div id="springPanel"></div>
							        </div>
						        </div>
					        </div>					
				        </div>		
			        </div>
			        <div class="col-lg-3 col-12">
				        <div class="card mb-3">
					        <div class="card-body">						
						        <div class="input-group mb-3">
							        <div class="card-body">
                                        
                                        <div class="row">
                                            <form class="searchBar">
                                                <input id="searchTerm" type="text" placeholder="Search.." name="search">
                                                <button type="submit" data-ng-click="searchNodes()"><i class="fa fa-search"></i></button>
                                            </form>
                                        </div>
                                        
                                        <div class="row">
                                            <rzslider id="slider" class="slider" rz-slider-model="slider.minValue" rz-slider-high="slider.maxValue" rz-slider-options="slider.options"></rzslider>
                                        </div>
                                        
                                        <div id="nodeSizeDropdown" class="row">Size nodes by 
                                            <select ng-options="o for o in node_size_options" data-ng-model="selectedNodeSizeOption" ng-change="updateNodeSize()"></select>
                                        </div>
                       
                                        <div id="nodeColorDropdown" class="row">Colour nodes by 
                                            <select ng-options="o for o in node_coloring_options" data-ng-model="selectedNodeColorOption" ng-change="updateNodeColor()"></select> using
                                            <select ng-options="o for o in color_options" data-ng-model="selectedColorOption" ng-change="updateNodeColor()"></select> colour palette
                                        </div>
              
                                        <div id="save" class="row">
                                            <button class="mb-4" data-ng-click="savebutton()">Save</button>
                                        </div>
					                </div>
				                </div>
					        </div>
				        </div>
				        <div class="card">
					        <div class="card-header">
						        <h4>Node Data</h4>
					        </div>
					        <div class="card-body">
						        <div id="nodedataPanel"></div>
						    </div>
					    </div>
				    </div>
			    </div>
		    </div>
	    </body>
	    
	    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>	
	    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.2.1/js/bootstrap.min.js"></script>
	    <script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.4.8/angular.min.js"></script>
	    <script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.4.8/angular-animate.min.js"></script>
	    <script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.4.8/angular-aria.min.js"></script>
	    <script src="https://ajax.googleapis.com/ajax/libs/angular_material/1.0.0/angular-material.min.js"></script>	
	    <script src="https://rawgit.com/rzajac/angularjs-slider/master/dist/rzslider.js"></script>
	    
	    <script src="https://d3js.org/d3.v5.min.js"></script>
	    <script src="https://unpkg.com/force-in-a-box/dist/forceInABox.js"></script>
	    
        <script>
            (function(){var g=typeof exports!="undefined"&&exports||this;var b='<?xml version="1.0" standalone="no"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">';function e(h){return h&&h.lastIndexOf("http",0)==0&&h.lastIndexOf(window.location.host)==-1}function a(k,m){var h=k.querySelectorAll("image");var l=h.length;if(l==0){m()}for(var j=0;j<h.length;j++){(function(q){var o=q.getAttributeNS("http://www.w3.org/1999/xlink","href");if(o){if(e(o.value)){console.warn("Cannot render embedded images linking to external hosts: "+o.value);return}}var p=document.createElement("canvas");var i=p.getContext("2d");var n=new Image();o=o||q.getAttribute("href");n.src=o;n.onload=function(){p.width=n.width;p.height=n.height;i.drawImage(n,0,0);q.setAttributeNS("http://www.w3.org/1999/xlink","href",p.toDataURL("image/png"));l--;if(l==0){m()}};n.onerror=function(){console.log("Could not load "+o);l--;if(l==0){m()}}})(h[j])}}function f(h,k){var r="";var q=document.styleSheets;for(var o=0;o<q.length;o++){try{var u=q[o].cssRules}catch(s){console.warn("Stylesheet could not be loaded: "+q[o].href);continue}if(u!=null){for(var n=0;n<u.length;n++){var t=u[n];if(typeof(t.style)!="undefined"){var p=null;try{p=h.querySelector(t.selectorText)}catch(m){console.warn('Invalid CSS selector "'+t.selectorText+'"',m)}if(p){var l=k?k(t.selectorText):t.selectorText;r+=l+" { "+t.style.cssText+" }\\n"}else{if(t.cssText.match(/^@font-face/)){r+=t.cssText+"\\n"}}}}}}return r}function d(i,k,j){var h=(i.viewBox.baseVal&&i.viewBox.baseVal[j])||(k.getAttribute(j)!==null&&!k.getAttribute(j).match(/%$$/)&&parseInt(k.getAttribute(j)))||i.getBoundingClientRect()[j]||parseInt(k.style[j])||parseInt(window.getComputedStyle(i).getPropertyValue(j));return(typeof h==="undefined"||h===null||isNaN(parseFloat(h)))?0:h}function c(h){h=encodeURIComponent(h);h=h.replace(/%([0-9A-F]{2})/g,function(i,j){var k=String.fromCharCode("0x"+j);return k==="%"?"%25":k});return decodeURIComponent(h)}g.svgAsDataUri=function(j,i,h){i=i||{};i.scale=i.scale||1;var k="http://www.w3.org/2000/xmlns/";a(j,function(){var u=document.createElement("div");var r=j.cloneNode(true);var l,t;if(j.tagName=="svg"){l=i.width||d(j,r,"width");t=i.height||d(j,r,"height")}else{if(j.getBBox){var o=j.getBBox();l=o.x+o.width;t=o.y+o.height;r.setAttribute("transform",r.getAttribute("transform").replace(/translate\(.*?\)/,""));var p=document.createElementNS("http://www.w3.org/2000/svg","svg");p.appendChild(r);r=p}else{console.error("Attempted to render non-SVG element",j);return}}r.setAttribute("version","1.1");r.setAttributeNS(k,"xmlns","http://www.w3.org/2000/svg");r.setAttributeNS(k,"xmlns:xlink","http://www.w3.org/1999/xlink");r.setAttribute("width",l*i.scale);r.setAttribute("height",t*i.scale);r.setAttribute("viewBox",[i.left||0,i.top||0,l,t].join(" "));u.appendChild(r);var q=f(j,i.selectorRemap);var v=document.createElement("style");v.setAttribute("type","text/css");v.innerHTML="<![CDATA[\\n"+q+"\\n]]>";var n=document.createElement("defs");n.appendChild(v);r.insertBefore(n,r.firstChild);var p=b+u.innerHTML;var m="data:image/svg+xml;base64,"+window.btoa(c(p));if(h){h(m)}})};g.svgAsPngUri=function(j,i,h){g.svgAsDataUri(j,i,function(k){var l=new Image();l.onload=function(){var n=document.createElement("canvas");n.width=l.width;n.height=l.height;var o=n.getContext("2d");if(i&&i.backgroundColor){o.fillStyle=i.backgroundColor;o.fillRect(0,0,n.width,n.height)}o.drawImage(l,0,0);var m=document.createElement("a");h(n.toDataURL("image/png"))};l.src=k})};g.saveSvgAsPng=function(j,i,h){h=h||{};g.svgAsPngUri(j,h,function(l){var k=document.createElement("a");k.download=i;k.href=l;document.body.appendChild(k);k.addEventListener("click",function(m){k.parentNode.removeChild(k)});k.click()})}})();
        </script>
        
        <script> $js_text </script>
        '''

        return html