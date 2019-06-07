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

    key_list = list(G.nodes[0].keys())

    #need to iterate over all attributes and add to dictionary before appending

    for node in G.nodes():

        d = {'id': node}

        for key in key_list:
            d[key] = G.nodes[node][key]

        graph_data['nodes'].append(d)
        
    j = 0
    for edge in G.edges():
        source = np.where([node['id'] == edge[0] for node in graph_data['nodes']])[0][0]
        target = np.where([node['id'] == edge[1] for node in graph_data['nodes']])[0][0]
        graph_data['links'].append({
            "source" : source,
            "target" : target,
            "weight" : list(nx.get_edge_attributes(G,'weight').values())[j],
            "length": list(nx.get_edge_attributes(G,'len').values())[j]
        })
        j += 1
    
    return graph_data

def getCSSnetwork():

    css_text = '''
    
    .links line {
        stroke: #999;
        stroke-width: 0.5;
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

def getCSSnetwork2():
    
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
              
    var params = JSON.parse(JSON.stringify($paramDict));
        
    var networkData = $networkData

    var width = params.width, height = params.height;
   
    var svg = d3.select("body").append("svg")
        .attr("width", width)
        .attr("height", height);

    svg.call(d3.zoom().on('zoom', zoomed));

    var simulation = d3.forceSimulation()
        .force("link", d3.forceLink().id(d => d.id))
        .force("charge", d3.forceManyBody().strength([params.chargeStrength]))//.distanceMax([500]))
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
    var graphRec = JSON.parse(JSON.stringify(graph));

    graph.nodes.forEach(function(d) { d.x = d.node_x; d.y = d.node_y });

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
    
    document.write(d3.max(graph.nodes, function(d) {return d[centrality]; }))
    
    updateNodeSize(Object.keys(params.node_size_scale)[0])
    
    function updateNodeSize(centrality) {
    
        var scaleType = params.node_size_scale[centrality].scale
        var range = params.node_size_scale[centrality].range
    
        initScale = d3.scaleLinear()
  	        .domain([d3.min(graph.nodes, function(d) {return d[centrality]; }),d3.max(graph.nodes, function(d) {return d[centrality]; })])
  	        .range([1,10]);

        //document.write(d3.max(graph.nodes, function(d) {return d[centrality]; }))
        
        scaledValues = []
        graph.nodes.forEach( function (d) { scaledValues.push(initScale(d[centrality])); });
                           
        if (scaleType == "linear") {
            //document.write(scaleType)
            linearScale = d3.scaleLinear()
  	             .domain([d3.min(scaledValues),d3.max(scaledValues)])
  	             .range(range);
  	         
  	        graph.nodes.forEach( function (d) { d.Size = linearScale(initScale(d[centrality])); });
          
        } else if (scaleType == "reverse_linear") {
            //document.write(scaleType)
            reversed_linear_values = []
             
            scaledValues.forEach( function (d) { reversed_linear_values.push(1/d); });
             
            reversedLinearScale = d3.scaleLinear()
  	            .domain([d3.min(reversed_linear_values),d3.max(reversed_linear_values)])
  	            .range(range);
  	         
  	        graph.nodes.forEach( function (d) { d.Size = reversedLinearScale(initScale(d[centrality])); });
  	         
        } else if (scaleType == "log") {
            //document.write(scaleType)
            
            //document.write(scaledValues)
            logScale = d3.scaleLog()
  	            .domain([d3.min(scaledValues),d3.max(scaledValues)])
  	            .range(range);
  	        
  	        //document.write(d3.min(scaledValues))
  	         
  	        graph.nodes.forEach( function (d) { d.Size = logScale(initScale(d[centrality])); });
          
        } else if (scaleType == "reverse_log") {
            //document.write(scaleType)
            reversed_log_values = []
             
            scaledValues.forEach( function (d) { reversed_log_values.push(1/d); });
             
            document.write(d3.min(reversed_log_values))
             
            reversedLogScale = d3.scaleLog()
  	            .domain([d3.min(reversed_log_values),d3.max(reversed_log_values)])
  	            .range(range);
  	         
  	        graph.nodes.forEach( function (d) { d.Size = reversedLogScale(initScale(d[centrality])); });
  	         
  	    } else if (scaleType == "square") {
  	        //document.write(scaleType)       
            squareScale = d3.scalePow()
  	            .domain([d3.min(scaledValues),d3.max(scaledValues)])
  	            .exponent(2)
  	            .range(range);
  	         
  	        graph.nodes.forEach( function (d) { d.Size = squareScale(initScale(d[centrality])); });
  	      
  	    } else if (scaleType == "reverse_square") {
  	        //document.write(scaleType)
  	        reversed_squared_values = []
  	         
  	        scaledValues.forEach( function (d) { reversed_squared_values.push(1/d); });
  	         
  	        reversedSquareScale = d3.scalePow()
  	            .domain([d3.min(reversed_square_values),d3.max(reversed_square_values)])
  	            .exponent(2)
  	            .range(range);
  	         
  	        graph.nodes.forEach( function (d) { d.Size = reversedSquareScale(initScale(d[centrality])); });
  	      
  	    } else if (scaleType == "area") {
  	        //document.write(scaleType)
  	        area_values = []
  	         
  	        scaledValues.forEach( function (d) { area_values.push(Math.PI * (d * d)); });
  	         
  	        areaScale = d3.scaleLinear()
  	            .domain([d3.min(area_values),d3.max(area_values)])
  	            .range(range);
  	         
  	        graph.nodes.forEach( function (d) { d.Size = areaScale(initScale(d[centrality])); });
  	         
  	    } else if (scaleType == "reverse_area") {
  	        //document.write(scaleType)
  	        reversed_values = []
  	        reversed_area_values = []
  	         
  	        scaledValues.forEach( function (d) { reversed_values.push(1/d); });
  	        reversed_values.forEach( function (d) { reversed_area_values.push(Math.PI * (d * d)); });
  	         
  	        reversedAreaScale = d3.scaleLinear()
  	            .domain([d3.min(reversed_area_values),d3.max(reversed_area_values)])
  	            .range(range);
  	         
  	        graph.nodes.forEach( function (d) { d.Size = reversedAreaScale(initScale(d[centrality])); });
  	         
  	    } else if (scaleType == "volume") {
            //document.write(scaleType)
            volume_values = []
             
            scaledValues.forEach( function (d) { volume_values.push(4 / 3 * (Math.PI * (d * d * d))); });
             
            volumeScale = d3.scaleLinear()
  	            .domain([d3.min(volume_values),d3.max(volume_values)])
  	            .range(range);
  	         
  	        graph.nodes.forEach( function (d) { d.Size = volumeScale(initScale(d[centrality])); });
          
        } else if (scaleType == "reverse_volume") {
            //document.write(scaleType)
            reversed_values = []
            reversed_volume_values = []
             
            scaledValues.forEach( function (d) { reversed_values.push(1/d); });
            reversed_values.forEach( function (d) { reversed_volume_values.push(4 / 3 * (Math.PI * (d * d * d))); });
             
            reversedVolumeScale = d3.scaleLinear()
  	            .domain([d3.min(reversed_volume_values),d3.max(reversed_volume_values)])
  	            .range(range);
  	         
  	        graph.nodes.forEach( function (d) { d.Size = reversedVolumeScale(initScale(d[centrality])); });
  	           
        }    
    }
    
    //var initScale = scaleDict[Object.keys(params.node_size_scale)[0]][0]
    //var defaultSize = scaleDict[Object.keys(params.node_size_scale)[0]][1]
    
        
    //if (params.node_size_scale[Object.keys(params.node_size_scale)[0]].scale == "linear") {
     //   var defaultSize = d3.scaleLinear()
  	 //       .domain([d3.min(graph.nodes, function(d) {return d[Object.keys(params.node_size_scale)[0]]; }),d3.max(graph.nodes, function(d) {return d[Object.keys(params.node_size_scale)[0]]; })])
  	 //       .range(params.node_size_scale[Object.keys(params.node_size_scale)[0]].range);
    //} else if (params.node_size_scale[Object.keys(params.node_size_scale)[0]].scale == "reverse_linear") {
     //   defaultScalePrefix = String(params.node_size_scale[Object.keys(params.node_size_scale)[0]].scale) + "_"
        
     //   graph.nodes.forEach( function (d) { d[defaultScalePrefix + Object.keys(params.node_size_scale)[0]] = 1/d[Object.keys(params.node_size_scale)[0]]; });
                
      //  var defaultSize = d3.scaleLinear()
  	   //     .domain([d3.min(graph.nodes, function(d) {return d[defaultScalePrefix + Object.keys(params.node_size_scale)[0]]; }),d3.max(graph.nodes, function(d) {return d[defaultScalePrefix + Object.keys(params.node_size_scale)[0]]; })])
  	   //     .range(params.node_size_scale[Object.keys(params.node_size_scale)[0]].range);
  	//}
  	//else if
  	
  	//var defaultSize = d3.scaleLinear()
  	//    .domain([d3.min(graph.nodes, function(d) {return d[Object.keys(params.node_size_scale)[0]]; }),d3.max(graph.nodes, function(d) {return d[Object.keys(params.node_size_scale)[0]]; })])
  	//    .range(params.node_size_scale[Object.keys(params.node_size_scale)[0]]);
  	
  	//var defaultSize_log = d3.scaleLog()
  	//    .domain([Math.log(d3.min(graph.nodes, function(d) {return d[Object.keys(params.node_size_scale)[0]]; })),Math.log(d3.max(graph.nodes, function(d) {return d[Object.keys(params.node_size_scale)[0]]; }))])
  	//    .range([Math.log(params.node_size_scale[Object.keys(params.node_size_scale)[0]][0]),Math.log(params.node_size_scale[Object.keys(params.node_size_scale)[0]][1])]);  
  	    
    var scaleLinks = d3.scaleLinear()
  	    .domain([d3.min(graph.links, function(d) {return d.weight; }),d3.max(graph.links, function(d) {return d.weight; })])
        .range([1,50])
        .clamp(true);
        
    simulation.force("collide", d3.forceCollide().radius( function (d) { return d.Size; }));
    //simulation.force("collide", d3.forceCollide().radius( function (d) { return defaultSize(d[Object.keys(params.node_size_scale)[0]]); }));
    
    update();

    function update() {

        node = node.data(graph.nodes)
    
        node.exit().remove();
    
        var newNode = node.enter().append("circle")
				.attr('r', function(d, i) { return d.Size; })
      		    //.attr('r', function(d, i) { return defaultSize(d[Object.keys(params.node_size_scale)[0]]); })
      		    .attr("fill", function(d) { return d.Color; })
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
      		    .on('click', fade(0.1))
      		    //.on('mouseover', releaseNode)
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
    
        label = label.data(graph.nodes)
    
        label.exit().remove();
    
        var newLabel = label.enter().append("text")
    			.text(function (d) { return d.Name; })
        	    .style("text-anchor", "middle")
					.style("fill", "#000")
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
      		    .on('click', fade(0.1))
      		    //.on('mouseover', releaseNode)
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

        link = link.data(graph.links)

		link.exit().remove();
    
        var newLink = link.enter().append("line")
    				.attr("class", "link")
    				.on('mouseover.tooltip', function(d) {
      						tooltip.transition()
        							.duration(300)
        							.style("opacity", .8);
      						tooltip.html("Source: "+ d.source.Label + 
                        				"<br/>Target: " + d.target.Label +
                    					"<br/>Correlation coeff.:"  + d.weight.toPrecision(3))
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
     		.links(graph.links)
     		.distance(function(d) { return d.length; });
    
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
         
    var slider = d3.select('body').append('p').text(params.link_type + ' threshold: ');

    slider.append('label')
		    .attr('for', 'threshold')
		    .text(d3.min(graph.links, function(d) {return d.weight; }).toPrecision(5));
    slider.append('input')
		    .attr('type', 'range')
		    .attr('min', scaleLinks(d3.min(graph.links, function(d) {return d.weight; })))
		    .attr('max', scaleLinks(d3.max(graph.links, function(d) {return d.weight; })))
		    .attr('value', scaleLinks(d3.min(graph.links, function(d) {return d.weight; })))
		    .attr('id', 'threshold')
		    .style('display', 'block')
		    .on('input', function () { 
				var threshold = scaleLinks.invert(this.value);

				d3.select('label').text(threshold.toPrecision(5));

				graph.links.splice(0, graph.links.length);
        
                graphRec.links.forEach( function (d) { if (d.weight $operator threshold) { graph.links.push(d); }});
              
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
    
    var dropdown = d3.select('body').append('div')
		.append('select')
		.on('change', function() { 
			var centrality = this.value;
			
			updateNodeSize(centrality)
			
			//var initScale = scaleDict[centrality][0]
			//var centralitySize = scaleDict[centrality][1]
			
			//var centralitySize = d3.scaleLinear()
			//	.domain([d3.min(graph.nodes, function(d) { return d[centrality]; }), d3.max(graph.nodes, function(d) { return d[centrality]; })])
			//	.range(params.node_size_scale[centrality].range);
				
			node.attr('r', function(d) { return d.Size; } );  
			
			simulation.force("collide", d3.forceCollide().radius( function (d) { return d.Size; }));
			simulation.alphaTarget(0.1).restart();
		});

    dropdown.selectAll('option')
		.data(Object.keys(params.node_size_scale))
		.enter().append('option')		
		.text(function(d) { return d; });

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
        d.fx = null;
        d.fy = null;
        
        
        //testing below
        //d.fx = d3.event.x;
        //d.fy = d3.event.y;
        
        
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

def getJSnetwork2():

    js_text = '''
    
    var linkDict = $link_type;
    
    switchData = JSON.parse(JSON.stringify(linkDict));
   
    var networkData = $networkData
    
    graph = JSON.parse(JSON.stringify(networkData));
    graphRec = JSON.parse(JSON.stringify(graph));
       
    var width = $width, height = $height;
    
    var toggle = 0;
    
    var weights = [];
    for (var i = 0; i < graphRec.links.length; i++) {                
        weights.push(graphRec.links[i].value);
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
              .range([d3.min(weights), d3.max(weights)])
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

def getJSnetwork3():

    js_text = '''
    
    var networkData = $networkData
        
    var width = 960, height = 600;

    var svg = d3.select("body").append("svg")
            .attr("width", width)
            .attr("height", height);
    
    // Call zoom for svg container.
    svg.call(d3.zoom().on('zoom', zoomed));
    
    var simulation = d3.forceSimulation()
        .force("link", d3.forceLink())//Or to use names rather than indices: .id(function(d) { return d.id; }))
        .force("charge", d3.forceManyBody().strength([-120]))//.distanceMax([500]))
        .force("center", d3.forceCenter(width / 2, height / 2));
    
    var container = svg.append('g');
    
    // Create form for search (see function below).
    var search = d3.select("body").append('form').attr('onsubmit', 'return false;');
    
    var box = search.append('input')
        .attr('type', 'text')
        .attr('id', 'searchTerm')
        .attr('placeholder', 'Type to search...');
    
    var button = search.append('input')
        .attr('type', 'button')
        .attr('value', 'Search')
        .on('click', function () { searchNodes(); });
    
    // Toggle for ego networks on click (below).
    var toggle = 0;
    
    var tooltip = d3.select("body")
        .append("div")
        .attr("class", "tooltip")
        .style("opacity", 0);
    
    //var graph = JSON.parse(JSON.stringify(networkData));
    var graph = JSON.parse(networkData);
    var graphRec = JSON.parse(networkData);
    
    graph.nodes.forEach(function(d) { d.x = d.node_x; d.y = d.node_y });
    
    //d3.json("marvel.json", function(error, graph) {
      //if (error) throw error;
    
      // Make object of all neighboring nodes.
    var linkedByIndex = {};
    for (i = 0; i < graph.nodes.length; i++) {
        linkedByIndex[i + "," + i] = 1;
    };
    graph.links.forEach(function(d) {
            linkedByIndex[d.source + ',' + d.target] = 1;
          linkedByIndex[d.target + ',' + d.source] = 1;
    });
    
    //var linkedByIndex = {};
    //  graph.links.forEach(d => {
    //    linkedByIndex[`${d.source.index},${d.target.index}`] = 1;
    //  });
    
    // A function to test if two nodes are neighboring.
    function neighboring(a, b) {
            return linkedByIndex[a.index + ',' + b.index];
    }
    
      // Linear scale for degree centrality.
    var pvalueSize = d3.scaleLinear()
        .domain([d3.min(graph.nodes, function(d) {return d.Pvalue; }),d3.max(graph.nodes, function(d) {return d.Pvalue; })])
        .range([8,25]);
        
    var scaleLinks = d3.scaleLinear()
        .domain([d3.min(graph.links, function(d) {return d.weight; }),d3.max(graph.links, function(d) {return d.weight; })])
        //.range([d3.min(graph.links, function(d) {return d.weight; }),d3.max(graph.links, function(d) {return d.weight; })])
        .range([1,50])
        .clamp(true);
       
    var reScaleLinks = d3.scaleLinear()
        .domain([1,50])
        //.range([d3.min(graph.links, function(d) {return d.weight; }),d3.max(graph.links, function(d) {return d.weight; })])
        .range([d3.min(graph.links, function(d) {return d.weight; }),d3.max(graph.links, function(d) {return d.weight; })])
        .clamp(true);
        
      //var degreeSize = d3.scaleLinear()
      //	.domain([d3.min(graph.nodes, function(d) {return d.degree; }),d3.max(graph.nodes, function(d) {return d.degree; })])
      //	.range([8,25]);
    
      // Collision detection based on degree centrality.
    simulation.force("collide", d3.forceCollide().radius( function (d) { return pvalueSize(d.Pvalue); }));
    
    var link = container.append("g")
            .attr("class", "links")
        .selectAll("line")
        .data(graph.links, function(d) { return d.source + ", " + d.target;})
        .enter().append("line")
        .attr('class', 'link')
        .on('mouseover.tooltip', function(d) {
            tooltip.transition()
                .duration(300)
                .style("opacity", .8);
            tooltip.html("Source: "+ d.source.Label + 
                         "<br/>Target: " + d.target.Label +
                        "<br/>Correlation coeff.:"  + d.weight.toPrecision(3))
                .style("left", (d3.event.pageX) + "px")
                .style("top", (d3.event.pageY + 10) + "px");
        })
        .on("mouseout.tooltip", function() {
              tooltip.transition()
                .duration(100)
                .style("opacity", 0);
          })
        //.on('mouseout.fade', fade(1))
        //.on('click', fade(1))
          .on("mousemove", function() {
              tooltip.style("left", (d3.event.pageX) + "px")
                .style("top", (d3.event.pageY + 10) + "px");
          });
    
    var node = container.append("g")
        .attr("class", "nodes")
        .selectAll("circle")
        .data(graph.nodes)
        .enter().append("circle")
        // Calculate degree centrality within JavaScript.
        //.attr("r", function(d, i) { count = 0; graph.links.forEach(function(l) { if (l.source == i || l.target == i) { count += 1;}; }); return size(count);})
        // Use degree centrality from NetworkX in json.
        .attr('r', function(d, i) { return pvalueSize(d.Pvalue); })
          .attr("fill", function(d) { return d.Color; })
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
              
    var label = container.selectAll(".text")
                    .data(graph.nodes)
                    .enter().append("text")
                    .text(function (d) { return d.Name; })
            .style("text-anchor", "middle")
                    .style("fill", "#000")
                    .style("font-family", "Helvetica")
                    .style("font-size", 15)
            .attr('r', function(d, i) { return pvalueSize(d.Pvalue); })
            .attr("fill", function(d) { return d.Color; })
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
          .on('click', fade(0.1))
          //.on('mouseout', fade(1))
          //.on('click', function(d) {
            //  if (toggle == 0) {
              //    d3.selectAll('.link').style('opacity', function (l) {
                    //return l.target == d || l.source == d ? 1.0 : 0.1;
           //       return l.source === d || l.target === d ? 0.6 : 0.1;
               //   });
                //  d3.selectAll('.node').style('opacity', function (n) {
              
    //return neighboring(d, n) | neighboring(n, d) ? 1.0 : 0.1;
              
                        //return neighboring(d, n) ? 1.0 : 0.1;
               //   });
           //   d3.selectAll('.text').style('opacity', function (n) {
              
            //  		return neighboring(d, n) | neighboring(n, d) ? 1.0 : 0.1;
              
                        //return neighboring(d, n) ? 1.0 : 0.1;
                //  });
                //  d3.select(this).style('opacity', 1.0);
              //d3.select(d.text).style('opacity', 1.0);
    
                //  toggle = 1;
              //}
            //  else {
              //    d3.selectAll('.link').style('opacity', '0.6');
               //   d3.selectAll('.node').style('opacity', '1.0');
           //   d3.selectAll('.text').style('opacity', '1.0');
              
              //node.style("opacity", 1);
                //label.style("opacity", 1);
                //link.style("opacity", 1);
                //  toggle = 0;
             // }
         // })
          .on("mouseout.tooltip", function() {
            tooltip.transition()
                .duration(100)
                .style("opacity", 0);
            })
        //.on('mouseout.fade', fade(1))
            .on("mousemove", function() {
              tooltip.style("left", (d3.event.pageX) + "px")
                .style("top", (d3.event.pageY + 10) + "px");
            })
          .call(d3.drag()
              .on("start", dragstarted)
              .on("drag", dragged)
              .on("end", dragended));
    //node.append("title")
     //    .text(function(d) { return d.Name; });
    
    simulation
         .nodes(graph.nodes)
         .on("tick", ticked);
    
    simulation.force("link")
         .links(graph.links)
         .distance(function(d) { return d.length; });
         
         
    
    function ticked() {
            link
            .attr("x1", function(d) { return d.source.x; })
            .attr("y1", function(d) { return d.source.y; })
            .attr("x2", function(d) { return d.target.x; })
            .attr("y2", function(d) { return d.target.y; });
    
            node
            .attr("cx", function(d) { return d.x; })
            .attr("cy", function(d) { return d.y; });
          
          label.attr("x", function(d){ return d.x; })
                 .attr("y", function (d) {return d.y + 5; });   
            
    }
      
        // A slider (using only d3 and HTML5) that removes nodes below the input threshold.
    var slider = d3.select('body').append('p').text('Corr. coeff. Threshold: ');
    
    slider.append('label')
            .attr('for', 'threshold')
            .text(d3.min(graph.links, function(d) {return d.weight; }).toPrecision(5));
    slider.append('input')
            .attr('type', 'range')
            .attr('min', scaleLinks(d3.min(graph.links, function(d) {return d.weight; })))
            .attr('max', scaleLinks(d3.max(graph.links, function(d) {return d.weight; })))
            .attr('value', scaleLinks(d3.min(graph.links, function(d) {return d.weight; })))
        //.step(0.005)
            .attr('id', 'threshold')
            //.style('width', '50%')
            .style('display', 'block')
            .on('input', function () { 
                    var threshold = reScaleLinks(this.value);
    
                    d3.select('label').text(threshold.toPrecision(5));
    
                    // Find the links that are at or above the threshold.
                    var newData = [];
            linkedByIndex = {};
                    graphRec.links.forEach( function (d) {
                        if (d.weight >= threshold) {
                        newData.push(d); 
                    
                    linkedByIndex[d.source + ',' + d.target] = 1;
                                linkedByIndex[d.target + ',' + d.source] = 1;
              };
                    });
            
            //for (i = 0; i < graph.nodes.length; i++) {
                //		linkedByIndex[i + "," + i] = 1;
                //};
            
            
            //for (var i = 0; i < graphRec.links.length; i++) {
            //		if (graphRec.links[i].value > threshold) {
                        //  add this link
            //   			linkedByIndex[graphRec.links[i].source + "," + graphRec.links[i].target] = 1;
            //		}
                //}
    
                    // Data join with only those new links.
                    link = link.data(newData, function(d) {return d.source + ', ' + d.target;});
                    link.exit().remove();
                    var linkEnter = link.enter().append('line').attr('class', 'link');
                    link = linkEnter.merge(link);
            
            link
                .on('mouseover.tooltip', function(d) {
                        tooltip.transition()
                            .duration(300)
                            .style("opacity", .8);
                        tooltip.html("Source: "+ d.source.Label + 
                         "<br/>Target: " + d.target.Label +
                        "<br/>Correlation coeff.:"  + d.weight.toPrecision(3))
                            .style("left", (d3.event.pageX) + "px")
                            .style("top", (d3.event.pageY + 10) + "px");
                    })
                    .on("mouseout.tooltip", function() {
                        tooltip.transition()
                        .duration(100)
                        .style("opacity", 0);
                    })
                    //.on('mouseout.fade', fade(1))
                    //.on('click', fade(1))
                    .on("mousemove", function() {
                        tooltip.style("left", (d3.event.pageX) + "px")
                        .style("top", (d3.event.pageY + 10) + "px");
                    });
    
                    node = node.data(graph.nodes);
    
                    // Restart simulation with new link data.
                    simulation
                        .nodes(graph.nodes).on('tick', ticked)
                        .force("link").links(newData);
    
                    simulation.alphaTarget(0.1).restart();
    
                });
    
    // A dropdown menu with three different centrality measures, calculated in NetworkX.
    // Accounts for node collision.
    var dropdown = d3.select('body').append('div')
            .append('select')
            .on('change', function() { 
                var centrality = this.value;
                var centralitySize = d3.scaleLinear()
                    .domain([d3.min(graph.nodes, function(d) { return d[centrality]; }), d3.max(graph.nodes, function(d) { return d[centrality]; })])
                    .range([8,25]);
                node.attr('r', function(d) { return centralitySize(d[centrality]); } );  
                // Recalculate collision detection based on selected centrality.
                simulation.force("collide", d3.forceCollide().radius( function (d) { return centralitySize(d[centrality]); }));
                simulation.alphaTarget(0.1).restart();
            });
    
    dropdown.selectAll('option')
            .data(['Pvalue', 'Score', 'VIP1', 'QC_RSD'])
            .enter().append('option')
            //.attr('value', function(d) { return d.split(' ')[0].toLowerCase(); })
            .text(function(d) { return d; });
    
    //});
    
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
      d.fx = null;
      d.fy = null;
    }
    
    // Zooming function translates the size of the svg container.
    function zoomed() {
          container.attr("transform", "translate(" + d3.event.transform.x + ", " + d3.event.transform.y + ") scale(" + d3.event.transform.k + ")");
    }
    
    function fade(opacity) {
        return d => {
        
             if (toggle == 0) {
        
                node.style('stroke-opacity', function (o) {
                 const thisOpacity = neighboring(d, o) ? 1 : opacity;
                    this.setAttribute('fill-opacity', thisOpacity);
                    return thisOpacity;
                });
              
              label.style('stroke-opacity', function (o) {
                 const thisOpacity = neighboring(d, o) ? 1 : opacity;
                    this.setAttribute('fill-opacity', thisOpacity);
                    return thisOpacity;
                });
    
                    link.style('stroke-opacity', o => (o.source === d || o.target === d ? 1 : opacity));
              
              toggle = 1;
           } else {
           
                node.style('stroke-opacity', function (o) {
                    const thisOpacity = 1.0;
                    this.setAttribute('fill-opacity', thisOpacity);        		
                return thisOpacity;
                });
              
              label.style('stroke-opacity', function (o) {
                 const thisOpacity = 1.0;
                    this.setAttribute('fill-opacity', thisOpacity);
                    return thisOpacity;
                });          
    
                    link.style('stroke-opacity', 1.0);
           
                  toggle = 0;      
            
           }
        };
    }
    
    // Search for nodes by making all unmatched nodes temporarily transparent.
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

def getHTMLnetwork():

    html = '''
    <body>
    
        <style> $css_text </style>
        
        <script src="https://d3js.org/d3.v4.min.js"></script>
                
        <script> $js_text </script>
            
    </body>
    '''

    return html

def getHTMLnetwork2():

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

def interactiveNetwork(g, prog, link_type, chargeStrength, canvas_size, node_text_size, node_size_scale):#, fix_position, networkx_link_type, width, height, charge, node_text_size, size_range):

    #if fix_position:
    #    fixed = "true";
    #else:
    #    fixed = "false";

    # > for filtering on Rho, < for filtering on Pval

    if link_type == 'Pval':
        operator = '<';
    else:
        operator = '>';

    paramDict = {"width": canvas_size[0], "height": canvas_size[1], "link_type": link_type, "node_text_size": node_text_size, "node_size_scale": node_size_scale, "chargeStrength": chargeStrength}

    pos = pygraphviz_layout(g, prog=prog)

    for idx, node in enumerate(g.nodes()):
        g.node[node]['node_x'] = pos[node][0]
        g.node[node]['node_y'] = pos[node][1]

    #node_size = [round(x) for x in list(map(int, range_scale(np.array(list(nx.get_node_attributes(g, 'size').values())), size_range[0], size_range[1])))]

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

    #for idx, node in enumerate(g.nodes()):
    #    g.node[node]['size'] = node_size[idx]

    #for idx, (u, v) in enumerate(g.edges()):
    #    g.edges[u, v]['length'] = edge_distance[idx]

    data = json.dumps(generateJson(g), cls=graphEncoder)

    #with open('test.json', 'w') as file:

    #    file.write(json.dumps(data))

    css_text_network = getCSSnetwork();
    js_text_template_network = Template(getJSnetwork());
    html_template_network = Template(getHTMLnetwork());

    js_text_network = js_text_template_network.substitute({'networkData': json.dumps(data)
                                                              , 'operator': operator
                                                              , 'paramDict': paramDict})

    #js_text_network = js_text_template_network.substitute({'networkData': data
    #                                                       , 'fixed': fixed
    #                                                       , 'switch': linkType
    #                                                       , 'width': width
    #                                                       , 'height': height
    #                                                       , 'charge': charge
    #                                                       , 'node_text_size': node_text_size
    #                                                       , 'threshOp': threshOp })

    html = html_template_network.substitute({'css_text': css_text_network, 'js_text': js_text_network})

    return html