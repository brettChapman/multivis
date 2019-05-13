from string import Template
from .utils import df_to_Json
import json

def getCSSbundle():

    css_text = '''
    .node {
        font: "Helvetica Neue", Helvetica, Arial, sans-serif;
        font-size: $fontSize;
    }    

    .node:hover {
        stroke-opacity: 1.0;
        font-weight: 800;
    }

    .link {
        stroke-opacity: 0.4;
        fill: none;
        pointer-events: none;
    }

    .node:hover,
    .node--source,
    .node--target {
        stroke-opacity: 1.0;
        font-weight: 800;
    }
   
    .node:hover,
    .link--source,
    .link--target {
        stroke-opacity: 1.0;
    }
   
    .node--source {
        stroke-opacity: 1.0;
        stroke-width: 2px;
        font-weight: 800;
    }

    .node--target {
        stroke-opacity: 1.0;
        stroke-width: 2px;
        font-weight: 800;
    }
   
    .node--both {
        stroke-opacity: 1.0;
        stroke-width: 2px;
        font-weight: 800;
    }
   
    .link--source,
    .link--target {
        stroke-opacity: 1.0;
        stroke-width: 2px;
    }

    .link--source {
        stroke-opacity: 1.0;
        stroke-width: 2px;
    }

    .link--target {
        stroke-opacity: 1.0;
        stroke-width: 2px;
    }
   
    #wrapper {
        position: relative;
        width: 960px;
        margin: 0 auto;
        margin-left: auto;
        margin-right: auto;
    }
   
    #filterType {
        position: absolute;
        bottom: $radioOffSet;
        left: 0px; 
    }
   
    #corrCoeffSelect {
        position: absolute;
        bottom: $radioOffSet;
        left: 160px; 
    }
 
    #abs_corrCoeff, #p_corrCoeff, #n_corrCoeff {
        position: absolute;
        bottom: $filterSliderOffSet;
        left: 0px; 
    }
   
    #pvalue {
        position: absolute;
        bottom: $filterSliderOffSet;
        left: 0px; 
    }
   
    #tension {
        position: absolute;
        bottom: $tensionSliderOffSet;
        left: 0px; 
    }
  
    #abs_corrCoeffValue, #p_corrCoeffValue, #n_corrCoeffValue, #pvalueValue, #tensionValue {
        position: absolute;
        bottom: 0px;
        left: 375px;
    }
   
    #abs_corrCoeffHide {
        display: block;
    }
   
    #p_corrCoeffHide, #n_corrCoeffHide {
        display: none;
    }
   
    #corrCoeffSelect {
        display: block;
    }
   
    #pvalueHide {
        display: none;
    }
   
    .d3-slider {
        position: absolute;
        left: 105px;
        bottom: 0px;
        font-family: Verdana,Arial,sans-serif;
        font-size: 1.1em;
        border: 1px solid #aaaaaa;
        z-index: 2;
    }

    .d3-slider-horizontal {
        width: 250px;
        height: .8em;
    }  

    .d3-slider-vertical {
        width: .8em;
        height: 100px;
    }      

    .d3-slider-handle {
        position: absolute;
        width: 1.2em;
        height: 1.2em;
        border: 1px solid #d3d3d3;
        border-radius: 4px;
        background: #eee;
        background: linear-gradient(to bottom, #eee 0%, #ddd 100%);
        z-index: 3;
    }

    .d3-slider-handle:hover {
        border: 1px solid #999999;
    }

    .d3-slider-horizontal .d3-slider-handle {
        top: -.3em;
        margin-left: -.6em;
    }

    .d3-slider-axis {
        position: relative;
        z-index: 1;    
    }

    .d3-slider-axis-bottom {
        top: .8em;
    }

    .d3-slider-axis-right {
        left: .8em;
    }

    .d3-slider-axis path {
        stroke-width: 0;
        fill: none;
    }

    .d3-slider-axis line {
        fill: none;
        stroke: #aaa;
        shape-rendering: crispEdges;
    }

    .d3-slider-axis text {
        font-size: 11px;
    }

    .d3-slider-vertical .d3-slider-handle {
        left: -.25em;
        margin-left: 0;
        margin-bottom: -.6em;      
    }
    '''

    return css_text

def getJSbundle():

    js_text = '''

    var pvalues = [];
    var corrCoeff = [];

    var diameter = $diameter,
    radius = diameter / 2,
    innerRadius = radius - $innerRadiusOffset;
    
    var cluster = d3.layout.cluster()
        .size([360, innerRadius]);

    var bundle = d3.layout.bundle();

    var canvas = d3.select("#wrapper")
			.append("svg")
    	    .attr("width", diameter)
    	    .attr("height", diameter)
            .append("g")
    	    .attr("transform", "translate(" + radius + "," + radius + ")")
            .append("g");
            
    var linkLine = updateBundle($flareData);

    d3.slider = function module() {
  	    "use strict";

  	    // Public variables width default settings
  	    var min = 0,
      	    max = 100,
      	    step = 1, 
      	    animate = true,
      	    orientation = "horizontal",
      	    axis = false,
      	    margin = 50,
      	    value,
      	    scale; 

  	    // Private variables
  	    var axisScale,
      	    dispatch = d3.dispatch("slide"),
      	    formatPercent = d3.format(".2%"),
      	    tickFormat = d3.format(".0"),
      	    sliderLength;

  	    function slider(selection) {
    		selection.each(function() {

      			// Create scale if not defined by user
      			if (!scale) {
        				scale = d3.scale.linear().domain([min, max]);
      			}  

      			// Start value
      			value = value || scale.domain()[0]; 

      			// DIV container
      			var div = d3.select(this).classed("d3-slider d3-slider-" + orientation, true);

      			var drag = d3.behavior.drag();

      			// Slider handle
      			var handle = div.append("a")
          			.classed("d3-slider-handle", true)
          			.attr("xlink:href", "#")
          			.on("click", stopPropagation)
          			.call(drag);

      			// Horizontal slider
      			if (orientation === "horizontal") {

        				div.on("click", onClickHorizontal);
        				drag.on("drag", onDragHorizontal);
        				handle.style("left", formatPercent(scale(value)));
        				sliderLength = parseInt(div.style("width"), 10);
      			} else { // Vertical

        				div.on("click", onClickVertical);
        				drag.on("drag", onDragVertical);
        				handle.style("bottom", formatPercent(scale(value)));
        				sliderLength = parseInt(div.style("height"), 10);
      			}	
      
      			if (axis) {
        			createAxis(div);
      			}

      			function createAxis(dom) {

        			// Create axis if not defined by user
        			if (typeof axis === "boolean") {

          				axis = d3.svg.axis()
              			    .ticks(Math.round(sliderLength / 100))
              				.tickFormat(tickFormat)
              				.orient((orientation === "horizontal") ? "bottom" :  "right");

        			}      

        			// Copy slider scale to move from percentages to pixels
        			axisScale = scale.copy().range([0, sliderLength]);
          			axis.scale(axisScale);

          			// Create SVG axis container
        			var svg = dom.append("svg")
            		.classed("d3-slider-axis d3-slider-axis-" + axis.orient(), true)
            		.on("click", stopPropagation);

        			var g = svg.append("g");

        			// Horizontal axis
        			if (orientation === "horizontal") {

          				svg.style("left", -margin);

          				svg.attr({ 
            				width: sliderLength + margin * 2, 
            				height: margin
          				});  

          				if (axis.orient() === "top") {
            				svg.style("top", -margin);  
            				g.attr("transform", "translate(" + margin + "," + margin + ")")
          				} else { // bottom
            				g.attr("transform", "translate(" + margin + ",0)")
          				}

        			} else { // Vertical

          				svg.style("top", -margin);

          				svg.attr({ 
            				width: margin, 
            				height: sliderLength + margin * 2
          				});      

          					if (axis.orient() === "left") {
            					svg.style("left", -margin);
            					g.attr("transform", "translate(" + margin + "," + margin + ")")  
          					} else { // right          
            					g.attr("transform", "translate(" + 0 + "," + margin + ")")      
          					}
        			}

        			g.call(axis);  
      			}

      			// Move slider handle on click/drag
      			function moveHandle(pos) {

        			var newValue = stepValue(scale.invert(pos / sliderLength));

        			if (value !== newValue) {
          				var oldPos = formatPercent(scale(stepValue(value))),
              				newPos = formatPercent(scale(stepValue(newValue))),
              				position = (orientation === "horizontal") ? "left" : "bottom";

          				dispatch.slide(d3.event.sourceEvent || d3.event, value = newValue);

          				if (animate) {
            				handle.transition()
              	  				.styleTween(position, function() { return d3.interpolate(oldPos, newPos); })
                				.duration((typeof animate === "number") ? animate : 250);
          				} else {
            				handle.style(position, newPos);          
          				}
        			}
      			}

      			// Calculate nearest step value
      			function stepValue(val) {

        			var valModStep = (val - scale.domain()[0]) % step,
            				alignValue = val - valModStep;

        			if (Math.abs(valModStep) * 2 >= step) {
          				alignValue += (valModStep > 0) ? step : -step;
        			}

        			return alignValue;

      			}

      			function onClickHorizontal() {
        			moveHandle(d3.event.offsetX || d3.event.layerX);
      			}

      			function onClickVertical() {
        			moveHandle(sliderLength - d3.event.offsetY || d3.event.layerY);
      			}

      			function onDragHorizontal() {
        			moveHandle(Math.max(0, Math.min(sliderLength, d3.event.x)));
      			}

      			function onDragVertical() {
        			moveHandle(sliderLength - Math.max(0, Math.min(sliderLength, d3.event.y)));
      			}      

      			function stopPropagation() {
        			d3.event.stopPropagation();
      			}
    		});
  	    } 

  	    // Getter/setter functions
  	    slider.min = function(_) {
    		if (!arguments.length) return min;
    		min = _;
    		return slider;
  	    } 

  	    slider.max = function(_) {
    		if (!arguments.length) return max;
    		max = _;
    		return slider;
  	    }     

  	    slider.step = function(_) {
    		if (!arguments.length) return step;
    		step = _;
    		return slider;
  	    }   

  	    slider.animate = function(_) {
    		if (!arguments.length) return animate;
    		animate = _;
    		return slider;
  	    }

  	    slider.orientation = function(_) {
    		if (!arguments.length) return orientation;
    		orientation = _;
    		return slider;
  	    }     

  	    slider.axis = function(_) {
    		if (!arguments.length) return axis;
    		axis = _;
    		return slider;
  	    }     

  	    slider.margin = function(_) {
    		if (!arguments.length) return margin;
    		margin = _;
    		return slider;
  	    }  

  	    slider.value = function(_) {
    		if (!arguments.length) return value;
    		value = _;
    		return slider;
  	    }  

  	    slider.scale = function(_) {
    		if (!arguments.length) return scale;
    		scale = _;
    		return slider;
  	    }  

  	    d3.rebind(slider, dispatch, "on");

  	    return slider;
    }

    var currValues = {'abs_corrCoeff': -1
						, 's_abs_corrCoeff': -1
						, 'p_corrCoeff': 0
                        , 's_p_corrCoeff': 0
                        , 'n_corrCoeff': -1
                        , 's_n_corrCoeff': -1
                        , 'pvalue': 1
                        , 's_pvalue': 1
                        , 'tension': 0.85};
                        
    var absScale = d3.scale.linear()
              .domain(d3.extent(corrCoeff))
              .range([0.0, 1.0])
              .clamp(true);

    d3.select('#abs_corrCoeffValue').text(absScale(d3.min(corrCoeff)).toPrecision(5));
    
    var abs_corrCoeffSlider = d3.slider().scale(d3.scale.linear().domain([d3.min(corrCoeff), d3.max(corrCoeff)]).clamp(true)).value(d3.min(corrCoeff)).min(d3.min(corrCoeff)).max(d3.max(corrCoeff)).step(1E-20).on("slide", function(evt, value) {

			var corrCoeffValue = value;            
      
            var tension = currValues.tension;
            currValues['abs_corrCoeff'] = corrCoeffValue;
            currValues['s_abs_corrCoeff'] = corrCoeffValue;
            currValues['pvalue'] = 1;

            d3.select('#abs_corrCoeffValue').text(absScale(corrCoeffValue).toPrecision(5));
      
            var FlareData = filterData(corrCoeffValue, 1, 1);
  
  		    var linkLine = updateBundle(FlareData);
  
  		    var line = linkLine.line;
  		    var link = linkLine.link;
  
  		    line.interpolate("bundle").tension(tension);//tension);
 			link.attr("d", line);
    });

    d3.select('#absCorrCoeffSlider').call(abs_corrCoeffSlider); 
 
    d3.select('#p_corrCoeffValue').text(0.0.toPrecision(5));
    
    var p_corrCoeffSlider = d3.slider().scale(d3.scale.linear().domain([0, d3.max(corrCoeff)]).clamp(true)).value(0).min(0).max(d3.max(corrCoeff)).step(1E-20).on("slide", function(evt, value) {

			var p_corrCoeffValue = value;
            var tension = currValues.tension;
            currValues['p_corrCoeff'] = p_corrCoeffValue;
            currValues['s_p_corrCoeff'] = p_corrCoeffValue;
            currValues['pvalue'] = 1;

            d3.select('#p_corrCoeffValue').text(p_corrCoeffValue.toPrecision(5));
      
            var FlareData = filterData(p_corrCoeffValue, 1, 1);
  
  		    var linkLine = updateBundle(FlareData);
  
  		    var line = linkLine.line;
  		    var link = linkLine.link;
  
  		    line.interpolate("bundle").tension(tension);
 			link.attr("d", line);
    });
 
    d3.select('#posCorrCoeffSlider').call(p_corrCoeffSlider);
    
    d3.select('#n_corrCoeffValue').text(d3.min(corrCoeff).toPrecision(5));
 
    var n_corrCoeffSlider = d3.slider().scale(d3.scale.linear().domain([d3.min(corrCoeff), 0]).clamp(true)).value(d3.min(corrCoeff)).min(d3.min(corrCoeff)).max(0).step(1E-20).on("slide", function(evt, value) {

			var n_corrCoeffValue = value;
            var tension = currValues.tension;
            currValues['n_corrCoeff'] = n_corrCoeffValue;
            currValues['s_n_corrCoeff'] = n_corrCoeffValue;
            currValues['pvalue'] = 1;
            
            d3.select('#n_corrCoeffValue').text(n_corrCoeffValue.toPrecision(5));
            
            var FlareData = filterData(n_corrCoeffValue, 0, 1);
  
  		    var linkLine = updateBundle(FlareData);
  
  		    var line = linkLine.line;
  		    var link = linkLine.link;
  
  		    line.interpolate("bundle").tension(tension);
 			link.attr("d", line);
    });

    d3.select('#negCorrCoeffSlider').call(n_corrCoeffSlider);
 
    d3.select('#pvalueValue').text(d3.max(pvalues).toPrecision(5));
        
    var pvalueSlider = d3.slider().scale(d3.scale.log().domain([Math.exp(d3.min(pvalues)), Math.exp(d3.max(pvalues))]).clamp(true)).value(Math.exp(d3.max(pvalues))).min(Math.exp(d3.min(pvalues))).max(Math.exp(d3.max(pvalues))).step(1E-20).on("slide", function(evt, value) {
                        
            var pvalueValue = Math.log(value)
            var tension = currValues.tension;
            currValues['abs_corrCoeff'] = -1
            currValues['p_corrCoeff'] = 0
            currValues['n_corrCoeff'] = -1
            currValues['pvalue'] = pvalueValue;
            currValues['s_pvalue'] = pvalueValue;
      
            d3.select('#pvalueValue').text(pvalueValue.toPrecision(5));
      
            var FlareData = filterData(-1, 1, pvalueValue);
  
  		    var linkLine = updateBundle(FlareData);
  
  		    var line = linkLine.line;
  		    var link = linkLine.link;
  
  		    line.interpolate("bundle").tension(tension);
 			link.attr("d", line);
    });
 
    d3.select('#pvalueSlider').call(pvalueSlider);
 
    d3.select('#tensionValue').text(0.85);
 
    var tensionSlider = d3.slider().scale(d3.scale.linear().domain([0,1]).clamp(true)).value(0.85).min(0.0).max(1.0).step(0.05).on("slide", function(evt, value) {
 
 			var tension = value;
            var pvalueValue = currValues.pvalue;
			var abs_corrCoeffValue = currValues.abs_corrCoeff;
            var p_corrCoeffValue = currValues.p_corrCoeff;
            var n_corrCoeffValue = currValues.n_corrCoeff;
            currValues['tension'] = tension;
  
  		    d3.select('#tensionValue').text(Math.round(tension * 1000) / 1000);
      
            var form = document.getElementById("corrCoeffSelect")
            var form_val;
  
            for(var i=0; i<form.length; i++){
  	  		    if(form[i].checked){
    		    	form_val = form[i].id;        
                }
            }
  
            if (form_val == "PosCorrCoeffRadio") {
  	  		    var FlareData = filterData(p_corrCoeffValue, 1, pvalueValue);
            } else if (form_val == "NegCorrCoeffRadio") {
  	            var FlareData = filterData(n_corrCoeffValue, 0, pvalueValue);
            } else if (form_val == "AbsCorrCoeffRadio") {
                var FlareData = filterData(abs_corrCoeffValue, 1, pvalueValue);
            }
  
            var linkLine = updateBundle(FlareData);
  
  		    var line = linkLine.line;
  		    var link = linkLine.link;
  
  		    line.interpolate("bundle").tension(tension);
 			link.attr("d", line);
    });
 
    d3.select('#tensionSlider').call(tensionSlider);
 
    function changeFilter(){

	    var form = document.getElementById("filterType")
        var form_val;
  
        for(var i=0; i<form.length; i++){
  	        if(form[i].checked){
    		    form_val = form[i].id;        
            }
        }
  
        if (form_val == "corrCoeffRadio") { 
  	        d3.select('#abs_corrCoeffHide').style("display", 'block');
            d3.select('#p_corrCoeffHide').style("display", 'none');
            d3.select('#n_corrCoeffHide').style("display", 'none');
            d3.select('#corrCoeffSelect').style("display", 'block');
  	        d3.select('#pvalueHide').style("display", 'none');
    
            var form_corrCoeff = document.getElementById("corrCoeffSelect")
            var form_val_corrCoeff;
  
            for(var i=0; i<form_corrCoeff.length; i++){
  			    if(form_corrCoeff[i].checked){
    		        form_val_corrCoeff = form_corrCoeff[i].id;        
                }
            }
  
            if (form_val_corrCoeff == "PosCorrCoeffRadio") {
  	            var FlareData = filterData(currValues.s_p_corrCoeff, 1, 1);
            } else if (form_val_corrCoeff == "NegCorrCoeffRadio") {
  	            var FlareData = filterData(currValues.s_n_corrCoeff, 0, 1);
            } else if (form_val_corrCoeff == "AbsCorrCoeffRadio") {
                var FlareData = filterData(currValues.s_abs_corrCoeff, 1, 1);
            }  

		    var linkLine = updateBundle(FlareData);
    
        } else {
  	        d3.select('#abs_corrCoeffHide').style("display", 'none');
            d3.select('#p_corrCoeffHide').style("display", 'none');
            d3.select('#n_corrCoeffHide').style("display", 'none');
            d3.select('#corrCoeffSelect').style("display", 'none');
  	        d3.select('#pvalueHide').style("display", 'block');

            var FlareData = filterData(-1, 1, currValues.s_pvalue);
		    var linkLine = updateBundle(FlareData);
        }
  
        var tension = currValues.tension;
  
        var line = linkLine.line;
 	    var link = linkLine.link;
  
        line.interpolate("bundle").tension(tension);
 	    link.attr("d", line);
    }

    function changeCorrCoeff() {
	
        var form = document.getElementById("corrCoeffSelect")
        var form_val;
  
        for(var i=0; i<form.length; i++) {
  	        if(form[i].checked){
    		    form_val = form[i].id;        
            }
        }
  
        if (form_val == "PosCorrCoeffRadio") { 
            d3.select('#p_corrCoeffHide').style("display", 'block');
            d3.select('#n_corrCoeffHide').style("display", 'none');
            d3.select('#abs_corrCoeffHide').style("display", 'none');
   
            var FlareData = filterData(currValues.s_p_corrCoeff, 1, 1);
		    var linkLine = updateBundle(FlareData);
    
        } else if (form_val == "NegCorrCoeffRadio") {
  	        d3.select('#p_corrCoeffHide').style("display", 'none');
            d3.select('#n_corrCoeffHide').style("display", 'block');
            d3.select('#abs_corrCoeffHide').style("display", 'none');
    
            var FlareData = filterData(currValues.s_n_corrCoeff, 0, 1);
		    var linkLine = updateBundle(FlareData);
    
        } else if (form_val == "AbsCorrCoeffRadio") {
  	        d3.select('#p_corrCoeffHide').style("display", 'none');
            d3.select('#n_corrCoeffHide').style("display", 'none');
            d3.select('#abs_corrCoeffHide').style("display", 'block');
    
            var FlareData = filterData(currValues.s_abs_corrCoeff, 1, 1);
		    var linkLine = updateBundle(FlareData);
        }
  
        var tension = currValues.tension;
  
        var line = linkLine.line;
 	    var link = linkLine.link;
  
        line.interpolate("bundle").tension(tension);
 	    link.attr("d", line);
    }

    var filterDim = d3.select("#filterType");
    filterDim.on("change", changeFilter);

    var selectDim = d3.select("#corrCoeffSelect");
    selectDim.on("change", changeCorrCoeff);

    function updateBundle(data) {

	    pvalues = []
        corrCoeff = []

	    var line = d3.svg.line.radial()
    	    .interpolate("bundle")
    	    .tension(.85)
    	    .radius(function(d) { return d.y; })
    	    .angle(function(d) { return d.x / 180 * Math.PI; });
  
	    var nodes = cluster.nodes(packageHierarchy(data));
        var links = packageImports(nodes);

	    var link = canvas.selectAll(".link").data(bundle(links));
        var node = canvas.selectAll(".node").data(nodes.filter(function(n) { return !n.children; }));
  
        link.enter().append("path");
    
        link.each(function(d) { d.source = d[0]
      					    , d.target = d[d.length - 1]
                            , d.link_color = d.source.imports[d.target.keyname]["link_color"]
                            , d.link_corrCoeff = d.source.imports[d.target.keyname]["link_corrCoeff"]
                            , corrCoeff.push(d.source.imports[d.target.keyname]["link_corrCoeff"])
                            , pvalues.push(d.source.imports[d.target.keyname]["link_pvalue"])
                            , d.link_pvalue = d.source.imports[d.target.keyname]["link_pvalue"];
             				})
    	    .attr("class", "link")
    	    .attr("d", line)
    	    .style("stroke", function(d) { return d.link_color; });
    
	    node.enter().append("text");
    
        node.attr("class", "node")
    	    .attr("dy", ".31em")
    	    .attr("transform", function(d) { return "rotate(" + (d.x - 90) + ")translate(" + (d.y + 8) + ",0)" + (d.x < 180 ? "" : "rotate(180)"); })
    	    .style("text-anchor", function(d) { return d.x < 180 ? "start" : "end"; })
            .text(function(d) { return d.name; })
            .style("fill", function(d) { return d.node_color; })
    	    .on("mouseover", mouseovered)
    	    .on("mouseout", mouseouted);
  
        node.exit().remove();
        link.exit().remove();
  
        var linkLine = {"line": line, "link": link}
  
        var linkedByIndex = {};
	    for (i = 0; i < nodes.length; i++) {
    	    linkedByIndex[i + "," + i] = 1;
	    };
	    links.forEach(function (d) {
    	    linkedByIndex[d.source.index + "," + d.target.index] = 1;
	    });
  
        function neighboring(a, b) {
    	    return linkedByIndex[a.index + "," + b.index];
	    }
      
	    function mouseovered(d) {
  	        node
      	        .each(function(n) { n.target = n.source = false; });

  	        link
      	        .classed("link--target", function(l) { if (l.target === d) return l.source.source = true; })
      	        .classed("link--source", function(l) { if (l.source === d) return l.target.target = true; })
    		    .filter(function(l) { return l.target === d || l.source === d; })
      	        .each(function() { this.parentNode.appendChild(this); })
        
  	        node
      	        .classed("node--both", function(n) { return n.source && n.target; })
      	        .classed("node--target", function(n) { return n.target; })
      	        .classed("node--source", function(n) { return n.source; });
        
            link.style('opacity', o => (o.source === d || o.target === d ? 1 : 0.05))
	    }

	    function mouseouted(d) {
  	        link
      	        .classed("link--target", false)
      	        .classed("link--source", false);
    
  	        node
      	        .classed("node--both", false)
      	        .classed("node--target", false)
      	        .classed("node--source", false);
        
            link.style('opacity', 1);
            node.style('opacity', 1);
	    }

	    function packageHierarchy(classes) {
  		    var map = {}    ;

  		    function find(keyname, data) {
    		    var node = map[keyname], i;
    		    if (!node) {
      		        node = map[keyname] = data || {keyname: keyname, children: []};
      		        if (keyname.length) {
        		        node.parent = find(keyname.substring(0, i = keyname.lastIndexOf("#")));
        		        node.parent.children.push(node);
        		        node.key = keyname.substring(i + 1);
      		        }
    		    }
   			    return node;
  		    }

  		    classes.forEach(function(d) {
    		    find(d.keyname, d);
  		    });

  		    return map[""];
	    }

	    function packageImports(nodes) {
  		    var map = {}, imports = [];

  		    nodes.forEach(function(d) {
    		    map[d.keyname] = d;
  		    });

  		    nodes.forEach(function(d) {       
                if (d.imports) Object.keys(d.imports).forEach(function(i) {    
      		        imports.push({source: map[d.keyname], target: map[i]});
    		    });
  		    });

  		    return imports;
	    }
  
        return linkLine;
    }   

    function filterData(lower_corrCoeffThresh, upper_corrCoeffThresh, pvalueThresh) {

        const data = $flareData.map(a => ({...a}));
  
	    var FlareData = []
  
        //Remove nodes from imports with weight below threshold
        for (var i = 0; i < data.length; i++) {
            var flare = data[i];
    
            var links = flare.imports;
            var newLinks = {}
    
            for (const [key, value] of Object.entries(links)) {

                var link_corrCoeff = value["link_corrCoeff"];
                var link_pvalue = value["link_pvalue"];
                var link_color = value["link_color"];
				
                if (link_corrCoeff > lower_corrCoeffThresh && link_corrCoeff < upper_corrCoeffThresh) {
        		    if (link_pvalue <= pvalueThresh) {
        				newLinks[key] = {"link_corrCoeff": link_corrCoeff
                						, "link_pvalue": link_pvalue
                                        , "link_color": link_color};
        		    }
                }
		    }
    
            flare.imports = newLinks;
    
            FlareData.push(flare)
	    }
  
        return FlareData;
    }
    '''

    return js_text

def getHTMLbundle():

    html_text = '''
    
    <body>

        <style> $css_text </style>

        <div id="wrapper">
            <form id="filterType">
                <input type='radio' id="corrCoeffRadio" name="mode" checked/>Corr. coeff
                <input type='radio' id="pvalueRadio" name="mode"/>Pvalue
            </form>
  
            <form id="corrCoeffSelect">
                <input type='radio' id="PosCorrCoeffRadio" name="mode"/>Positive
                <input type='radio' id="NegCorrCoeffRadio" name="mode"/>Negative
                <input type='radio' id="AbsCorrCoeffRadio" name="mode" checked/>Absolute
            </form>
  
            <div id="abs_corrCoeffHide">
                <h3 id="abs_corrCoeff">Corr. coeff: <div id="absCorrCoeffSlider"></div><span id="abs_corrCoeffValue">0</span></h3>
            </div> 

            <div id="p_corrCoeffHide">
                <h3 id="p_corrCoeff"> Corr. coeff: <div id="posCorrCoeffSlider"></div><span id="p_corrCoeffValue"></span></h3>
            </div>

            <div id="n_corrCoeffHide">
                <h3 id="n_corrCoeff"> Corr. coeff: <div id="negCorrCoeffSlider"></div><span id="n_corrCoeffValue"></span></h3>
            </div>
  
            <div id="pvalueHide">
                <h3 id="pvalue"> Pvalue: <div id="pvalueSlider"></div><span id="pvalueValue"></span></h3>
            </div>

            <h3 id="tension">Tension: <div id="tensionSlider"></div><span id="tensionValue"></span></h3>
        </div>
  
        <script src="https://d3js.org/d3.v3.min.js"></script>

        <script> $js_text </script>

    </body>
    
    '''

    return html_text

def edgeBundle(df_edges, diameter, innerRadiusOffset, fontSize, filterOffSet):

    bundleJson = df_to_Json(df_edges);

    #with open('test.json', 'w') as file:

    #    file.write(json.dumps(bundleJson))


    css_text_template_bundle = Template(getCSSbundle());
    js_text_template_bundle = Template(getJSbundle())
    html_template_bundle = Template(getHTMLbundle());

    js_text = js_text_template_bundle.substitute({'flareData': json.dumps(bundleJson)
                                                     , 'diameter': diameter
                                                     , 'innerRadiusOffset': innerRadiusOffset})

    css_text = css_text_template_bundle.substitute({'fontSize': str(fontSize) + 'px'
                                                       , 'radioOffSet': str(filterOffSet) + 'px'
                                                       , 'filterSliderOffSet': str(filterOffSet - 30) + 'px'
                                                       , 'tensionSliderOffSet': str(filterOffSet - 60) + 'px'})

    html = html_template_bundle.substitute({'css_text': css_text, 'js_text': js_text})

    return html