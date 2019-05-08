import numpy as np
import networkx as nx
from string import Template
from networkx.drawing.nx_agraph import pygraphviz_layout
import json
from .utils import *

class graphEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(graphEncoder, self).default(obj)

def generateJson(G):
    
    graph_data = {'nodes': [], 'links': []}

    for node in G.nodes():
        graph_data['nodes'].append({'keyname': node
                                    , 'label': G.nodes[node]['label']
                                    , 'name': G.nodes[node]['name']
                                    , 'color': G.nodes[node]['color']
                                    , 'group': G.nodes[node]['group']
                                    , 'size': G.nodes[node]['size']
                                    , 'node_x': G.nodes[node]['node_x']
                                    , 'node_y': G.nodes[node]['node_y']
                                    })
        
    j = 0
    for edge in G.edges():
        source = np.where([node['keyname'] == edge[0] for node in graph_data['nodes']])[0][0]
        target = np.where([node['keyname'] == edge[1] for node in graph_data['nodes']])[0][0]
        graph_data['links'].append({
            "source" : source,
            "target" : target,
            "value" : list(nx.get_edge_attributes(G,'weight').values())[j],
            "length": list(nx.get_edge_attributes(G,'len').values())[j]
        })
        j += 1
    
    return graph_data

def getCSSnetwork():
    
    #Set the CSS styles
    css_text = '''
    .node {
        cursor: move;
        stroke: #fff;
        stroke-width: 1.5px;
    }
    
    .node.fixed {
        fill: #f00;
    }
    
    .link {
        stroke: #999;
        stroke-width: 0.5;
        stroke-opacity: 1.0;
    }
    
    #wrapper {
        position: relative;
        width: 960px;
        margin: 0 auto;
        margin-left: auto;
        margin-right: auto;
    }
    
    #corrCoeff, #pvalue {
        position: absolute;
        bottom: -40px;
        left: -50px; 
    }
   
    #corrCoeffValue, #pvalueValue {
        position: absolute;
        bottom: -20px;
        left: 310px;
    }
   
    .corrCoeffSlider, .pvalueSlider {
        position: absolute;
        bottom: 13px;
        left: 100px;
    }
    
    .d3-tip {
        line-height: 1;
        color:#000;
        position: absolute;
        z-index:1000;
        background-color: rgba(255, 255, 255, 0.7);
        padding:10px;
        border-style: solid;
        border-width: 5px;
        border-color: rgba(0, 0, 0, 1);
        border-radius: 5px;
        font-size:15px;
    }
    
    .cursor {
        fill: none;
        stroke: brown;
        pointer-events: none;
    }
    
    .tray {
        position: absolute;
        width: 100%;
        height: 6px;
        border: solid 1px #ccc;
        border-top-color: #aaa;
        border-radius: 4px;
        background-color: #f0f0f0;
        box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.08);
    }
    
    .handle {
        position: absolute;
        top: 3px;
    }
    
    .handle-icon {
        width: 14px;
        height: 14px;
        border: solid 1px #aaa;
        position: absolute;
        border-radius: 10px;
        background-color: #fff;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
        top: -7px;
        left: -7px;
    }
    
    #corrCoeffHide {
      display: block;
    }
   
    #pvalueHide {
      display: none;
    }
    
    text {
        -webkit-touch-callout: none; /* iOS Safari */
        -webkit-user-select: none; /* Safari */
        -khtml-user-select: none; /* Konqueror HTML */
        -moz-user-select: none; /* Firefox */
        -ms-user-select: none; /* Internet Explorer/Edge */
        user-select: none; /* Non-prefixed version, currently supported by Chrome and Opera */
    }
    '''
    
    return css_text

def getJSnetwork():

    js_text = '''
    
    var switchDict = $switch
    
    switchData = JSON.parse(JSON.stringify(switchDict));
   
    var networkData = $networkData
    
    graph = JSON.parse(JSON.stringify(networkData));
    graphRec = JSON.parse(JSON.stringify(graph));
       
    var width = $width, height = $height;
    
    var toggle = 0;
    
    var values = [];
    for (var i = 0; i < graphRec.links.length; i++) {                
        values.push(graphRec.links[i].value);
    }
    
    gNodes = graph.nodes
    gLinks = graph.links
    
    gNodes.forEach(function(d) { d.x = d.node_x; d.y = d.node_y; d.fixed = $fixed; });

    var force = d3.layout.force()
        .size([width, height])
        .charge($charge)
        .linkDistance(function(d) { return d.length; })
        .on("tick", tick);
        
    var drag = force.drag().on("dragstart", dragstart);
    
    var svg = d3.select("#wrapper").append("svg")
        .attr("width", width)
        .attr("height", height);
    
    var tip = d3.tip()
  	    .attr('class', 'd3-tip')
    	.offset([-10,0])
	    .html(function (d) { return  d.label + "</span>"; });
  
    svg.call(tip)
        
    force.nodes(gNodes)
            .links(gLinks)
            .start();
    
    var link = svg.selectAll(".link")
        .data(gLinks)
        .enter().append("line")
        .attr("class", "link");

    var node = svg.selectAll(".node")
        .data(gNodes)
        .enter().append("circle")
        .attr("class", "node")
        .attr("r", function (d) {return d.size;})
        .style("opacity", 1)
        .style("fill", function (d) { return d.color; })
        .call(drag)
        .on('dblclick', dblclick)
        .on('click', connectedNodes);
        
    var label = svg.selectAll(".text")
				.data(gNodes)
				.enter().append("text")
				.text(function (d) { return d.name; })
				.call(drag)
				.style("text-anchor", "middle")
				.style("fill", "#000")
				.style("font-family", "Helvetica")
				.style("font-size", $node_text_size)
				.on('dblclick', dblclick)
				.on('click', connectedNodes)
				.style("opacity", 1)
				.on('mouseover', tip.show)
                .on('mouseout', tip.hide);				
    
    function tick() {
        
        link.attr("x1", function (d) {
            return d.source.x;
        })
            .attr("y1", function (d) {
            return d.source.y;
        })
            .attr("x2", function (d) {
            return d.target.x;
        })
            .attr("y2", function (d) {
            return d.target.y;
        });   
               
        node.attr("cx", function (d) {
            return d.x;
        })
            .attr("cy", function (d) {
            return d.y;
        });
        
        label.attr("x", function(d){ return d.x; })
    		 .attr("y", function (d) {return d.y + 5; });   
        
        node.each(collide(0.5));       
        
    }
    
    var sliderWidth = 200;
    
    var CORRslider = generateSlider(sliderWidth, ".corrCoeffSlider");

    var PVALUEslider = generateSlider(sliderWidth, ".pvalueSlider");

    CORRslider.dispatch.on("sliderChange.slider", function(value) {

	    var sliderPos = CORRslider.x(value);
        var corrCoeffValue = (CORRslider.x(value) - 100) / 100;
  
        CORRslider.handle.style("left", sliderPos + "px")
  
        d3.select('#corrCoeffValue').text(Math.round(corrCoeffValue * 100) / 100);
   
        threshold(corrCoeffValue)
    });

    PVALUEslider.dispatch.on("sliderChange.slider", function(value) {

	    var sliderPos = PVALUEslider.x(value);
        var pvalueValue = PVALUEslider.y(value);

        PVALUEslider.handle.style("left", sliderPos + "px")
  
        d3.select('#pvalueValue').text(Math.round(pvalueValue * 10000) / 10000);
  
	    threshold(pvalueValue)
    });
    
    var linkedByIndex = {};
    for (i = 0; i < gNodes.length; i++) {
        linkedByIndex[i + "," + i] = 1;
    };
    gLinks.forEach(function (d) {
        linkedByIndex[d.source.index + "," + d.target.index] = 1;
    });
    
    function neighboring(a, b) {
        return linkedByIndex[a.index + "," + b.index];
    }
    
    changeFilter(switchData.switch)
        
    function changeFilter(ltype) {

        if (ltype == "rho") {
  	        d3.select('#corrCoeffHide').style("display", 'block');
  	        d3.select('#pvalueHide').style("display", 'none');
        } else if (ltype == "pval") {        
  	        d3.select('#corrCoeffHide').style("display", 'none');
  	        d3.select('#pvalueHide').style("display", 'block');
        }      
    }
    
    function connectedNodes() {
        
        if (toggle == 0) {
    
            d = d3.select(this).node().__data__;
            
            node.style("opacity", function (o) {
                return neighboring(d, o) | neighboring(o, d) ? 1 : 0.15;
            });
            
            link.style('opacity', o => (o.source === d || o.target === d ? 1 : 0.15))
            
            label.style("opacity", function (o) {
                return neighboring(d, o) | neighboring(o, d) ? 1 : 0.15;
            });
            
            toggle = 1;            
        } else {
            node.style("opacity", 1);
            label.style("opacity", 1);
            link.style("opacity", 1);
            toggle = 0;
        }
    }
        
    function collide(alpha) {
    
        var padding = 1;  // separation between circles
    
        var quadtree = d3.geom.quadtree(gNodes);
      
        return function(d) {
      
            var radius = d.size;
      
            var rb = 2*radius + padding,
                    nx1 = d.x - rb,
                    nx2 = d.x + rb,
                    ny1 = d.y - rb,
                    ny2 = d.y + rb;
            quadtree.visit(function(quad, x1, y1, x2, y2) {
                if (quad.point && (quad.point !== d)) {
                var x = d.x - quad.point.x,
                    y = d.y - quad.point.y,
                    l = Math.sqrt(x * x + y * y);
            
                if (l < rb) {
                    l = (l - rb) / l * alpha;
                    d.x -= x *= l;
                    d.y -= y *= l;
                    quad.point.x += x;
                    quad.point.y += y;
                }
            }
          
            return x1 > nx2 || x2 < nx1 || y1 > ny2 || y2 < ny1;
            });
        };
    }
    
    function threshold(thresh) {
              
        gLinks.splice(0, gLinks.length);
        
        for (var i = 0; i < graphRec.links.length; i++) {
            if (graphRec.links[i].value $threshOp thresh) {
            
                gLinks.push(graphRec.links[i]);
            }
        }
            
        linkedByIndex = {};
        for (i = 0; i < gNodes.length; i++) {
            linkedByIndex[i + "," + i] = 1;
        };
        
        // for each link
        for (var i = 0; i < graphRec.links.length; i++) {
            if (graphRec.links[i].value $threshOp thresh) {
               //  add this link
               linkedByIndex[graphRec.links[i].source.index + "," + graphRec.links[i].target.index] = 1;
            }
        }
                
        restart(); 
    }
        
    //Restart the visualisation after any node and link changes
    function restart() {
        
        link = link.data(gLinks);
        link.exit().remove();
        link.enter().insert("line", ".node").attr("class", "link");
        node = node.data(gNodes);
        node.enter().insert("circle", ".cursor").attr("class", "node").attr("r", function (d) {return d.size; }).call(drag);
        force.start();
    }
    
    //Allows dragging and fixing of nodes in place
    function dragstart(d) {
        d3.select(this).classed("fixed", d.fixed = true);
    }
    
    //Allows freeing of nodes by double clicking
    function dblclick(d) {
        d3.select(this).classed("fixed", d.fixed = false);
    }
    
    function generateSlider(sWidth, slider) {
    
        var x = d3.scale.linear()
                .domain([1, 100])
                .range([0, sWidth])
                .clamp(true);
        
        var y = d3.scale.linear()
              .domain([1, 100])
              .range([d3.min(values), d3.max(values)])
              .clamp(true);
              
        var dispatch = d3.dispatch("sliderChange");
    
        var sl = d3.select(slider)
                .style("width", sWidth + "px");
    
        var sTray = sl.append("div")
                .attr("class", "tray");
    
        var sHandle = sl.append("div")
                .attr("class", "handle");
    
        sHandle.append("div")
                .attr("class", "handle-icon");
    
        sl.call(d3.behavior.drag()
                .on("dragstart", function() {
                    dispatch.sliderChange(x.invert(d3.mouse(sTray.node())[0]));
                    d3.event.sourceEvent.preventDefault();
                })
                .on("drag", function() {
                    dispatch.sliderChange(x.invert(d3.mouse(sTray.node())[0]));
                }));
            
      return {"dispatch": dispatch, "handle": sHandle, "x": x, "y": y}
    }
    '''

    return js_text

def getHTMLnetwork():

    html = '''    
    <body>
    
        <style> $css_text </style>

        <div id="wrapper">
            <div id="corrCoeffHide">
                <h3 id="corrCoeff"> Corr. coeff: <div class="corrCoeffSlider"></div><p id="corrCoeffValue"></p></h3>
            </div>
  
            <div id="pvalueHide">
                <h3 id="pvalue"> Pvalue: <div class="pvalueSlider"></div><p id="pvalueValue"></p></h3>
            </div>
        </div>
    
        <script src="https://d3js.org/d3.v3.min.js"></script>
        <script src="http://labratrevenge.com/d3-tip/javascripts/d3.tip.v0.6.3.js"></script>
  
        <script> $js_text </script>
  
    </body>
    '''
    
    return html

def interactiveNetwork(g, prog, fix_position, networkx_link_type, width, height, charge, node_text_size, size_range):

    if fix_position:
        fixed = "true";
    else:
        fixed = "false";

    # > for filtering on Rho, < for filtering on Pval
    if networkx_link_type == 'Pval':
        linkType = {"switch": "pval"};
        threshOp = '<';
    else:
        linkType = {"switch": "rho"};
        threshOp = '>';

    pos = pygraphviz_layout(g, prog=prog)

    for idx, node in enumerate(g.nodes()):
        g.node[node]['node_x'] = pos[node][0]
        g.node[node]['node_y'] = pos[node][1]

    node_size = [round(x) for x in list(map(int, range_scale(np.array(list(nx.get_node_attributes(g, 'size').values())), size_range[0], size_range[1])))]

    #edge_dist = np.array(list(nx.get_edge_attributes(g, 'len').values()))

    #edge_dist = np.array(list(nx.get_edge_attributes(g, 'weight').values()))

    #if lengthScale == 'linear':
    #    edge_distance = [x for x in list(range_scale(edge_dist, length_range[0], length_range[1]))]
    #elif lengthScale == 'log':
    #    edge_dist = np.log(edge_dist)
    #    edge_distance = [x for x in list(range_scale(edge_dist, length_range[0], length_range[1]))]
    #elif lengthScale == 'square':
    #    edge_dist = np.square(edge_dist)
    #    edge_distance = [x for x in list(range_scale(edge_dist, length_range[0], length_range[1]))]

    for idx, node in enumerate(g.nodes()):
        g.node[node]['size'] = node_size[idx]

    #for idx, (u, v) in enumerate(g.edges()):
    #    g.edges[u, v]['length'] = edge_distance[idx]

    data = json.dumps(generateJson(g), cls=graphEncoder)

    with open('test.json', 'w') as file:

        file.write(json.dumps(data))

    css_text_network = getCSSnetwork();
    js_text_template_network = Template(getJSnetwork());
    html_template_network = Template(getHTMLnetwork());

    js_text_network = js_text_template_network.substitute({'networkData': data
                                                           , 'fixed': fixed
                                                           , 'switch': linkType
                                                           , 'width': width
                                                           , 'height': height
                                                           , 'charge': charge
                                                           , 'node_text_size': node_text_size
                                                           , 'threshOp': threshOp })

    html = html_template_network.substitute({'css_text': css_text_network, 'js_text': js_text_network})

    return html