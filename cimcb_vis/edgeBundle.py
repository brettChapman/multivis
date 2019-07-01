import sys
from string import Template
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import json

class edgeBundle:

    def __init__(self, edges):

        self.edges = self.__checkData(edges);

        self.set_params()

    def set_params(self, diameter=960, innerRadiusOffset=120, groupSeparation=1, linkFadeOpacity=0.05, fontSize=10, backgroundColor='white', sliderTextColor='black', filterOffSet=-60, color_scale='Score', edge_cmap="brg"):

        diameter, innerRadiusOffset, groupSeparation, linkFadeOpacity, fontSize, backgroundColor, sliderTextColor, filterOffSet, color_scale, edge_cmap = self.__paramCheck(diameter, innerRadiusOffset, groupSeparation, linkFadeOpacity, fontSize, backgroundColor, sliderTextColor, filterOffSet, color_scale, edge_cmap)

        self.diameter = diameter;
        self.innerRadiusOffset = innerRadiusOffset;
        self.groupSeparation = groupSeparation;
        self.linkFadeOpacity = linkFadeOpacity;
        self.fontSize = fontSize;
        self.backgroundColor = backgroundColor;
        self.sliderTextColor = sliderTextColor;
        self.filterOffSet = filterOffSet;
        self.color_scale = color_scale;
        self.edge_cmap = edge_cmap;

    def __checkData(self, df):

        if not isinstance(df, pd.DataFrame):
            print("Error: A dataframe was not entered. Please check your data.")
            sys.exit()

        return df

    def __paramCheck(self, diameter, innerRadiusOffset, groupSeparation, linkFadeOpacity, fontSize, backgroundColor, sliderTextColor, filterOffSet, color_scale, edge_cmap):

        if not isinstance(diameter, float):
            if not isinstance(diameter, int):
                print("Error: Diameter is not valid. Choose a float or integer value.")
                sys.exit()

        if not isinstance(innerRadiusOffset, float):
            if not isinstance(innerRadiusOffset, int):
                print("Error: Inner radius offset is not valid. Choose a float or integer value.")
                sys.exit()

        if not isinstance(groupSeparation, float):
            if not isinstance(groupSeparation, int):
                print("Error: Group separation is not valid. Choose a float or integer value.")
                sys.exit()

        if not isinstance(linkFadeOpacity, float):
            if not isinstance(linkFadeOpacity, int):
                print("Error: Link fade opacity is not valid. Choose a float or integer value.")
                sys.exit()

        if not isinstance(fontSize, float):
            if not isinstance(fontSize, int):
                print("Error: Font size is not valid. Choose a float or integer value.")
                sys.exit()

        if not matplotlib.colors.is_color_like(backgroundColor):
            print("Error: Background colour is not valid. Choose a valid colour value.")
            sys.exit()

        if not matplotlib.colors.is_color_like(sliderTextColor):
            print("Error: Slider text colour is not valid. Choose a valid colour value.")
            sys.exit()

        if not isinstance(filterOffSet, float):
            if not isinstance(filterOffSet, int):
                print("Error: Filter position offset is not valid. Choose a float or integer value.")
                sys.exit()

        if color_scale.lower() not in ["pvalue", "score"]:
            print("Error: Colour scale type not valid. Choose either \"Pvalue\" or \"Score\".")
            sys.exit()

        if not isinstance(edge_cmap, str):
            print("Error: Edge CMAP is not valid. Choose a string value.")
            sys.exit()
        else:
            cmap_list = matplotlib.cm.cmap_d.keys()

            if edge_cmap not in cmap_list:
                print("Error: Edge CMAP is not valid. Choose one of the following: {}.".format(', '.join(cmap_list)))
                sys.exit()

        return diameter, innerRadiusOffset, groupSeparation, linkFadeOpacity, fontSize, backgroundColor, sliderTextColor, filterOffSet, color_scale, edge_cmap

    def __getCSSbundle(self):

        css_text = '''
            .node {
            font: "Helvetica Neue", Helvetica, Arial, sans-serif;
            font-size: $fontSize;
        }
        
        body {background-color: $backgroundColor;}

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
            color: $sliderTextColor;
        }
       
        #scoreSelect {
            position: absolute;
            bottom: $radioOffSet;
            left: 160px;
            color: $sliderTextColor;
        }
     
        #abs_score, #p_score, #n_score {
            position: absolute;
            bottom: $filterSliderOffSet;
            left: 0px;
            color: $sliderTextColor;
        }
       
        #pvalue {
            position: absolute;
            bottom: $filterSliderOffSet;
            left: 0px;
            color: $sliderTextColor;
        }
       
        #tension {
            position: absolute;
            bottom: $tensionSliderOffSet;
            left: 0px;
            color: $sliderTextColor;
        }
      
        #abs_scoreValue, #p_scoreValue, #n_scoreValue, #pvalueValue, #tensionValue {
            position: absolute;
            bottom: 0px;
            left: 375px;
            color: $sliderTextColor;
        }
       
        #abs_scoreHide {
            display: block;
        }
       
        #p_scoreHide, #n_scoreHide {
            display: none;
        }
       
        #scoreSelect {
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

    def __getJSbundle(self):

        js_text = '''
                
        var pvalues = [];
        var p_scores = [];
        var n_scores = [];
        var abs_scores = [];
    
        var diameter = $diameter,
        radius = diameter / 2,
        innerRadius = radius - $innerRadiusOffset;
        
        var cluster = d3.layout.cluster()
            .separation(function(a, b) { return (a.parent == b.parent ? 1 : $groupSeparation ) })
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
    
        var currValues = {'abs_score': 0
                            , 's_abs_score': 0
                            , 'p_score': 0
                            , 's_p_score': 0
                            , 'n_score': 0
                            , 's_n_score': 0
                            , 'pvalue': 1
                            , 's_pvalue': 1
                            , 'tension': 0.85};
                            
        d3.select('#abs_scoreValue').text(d3.min(abs_scores).toPrecision(5));
        
        var abs_scoreSlider = d3.slider().scale(d3.scale.linear().domain([d3.min(abs_scores), d3.max(abs_scores)]).clamp(true)).value(d3.min(abs_scores)).min(d3.min(abs_scores)).max(d3.max(abs_scores)).step(1E-20).on("slide", function(evt, value) {
    
                var absScoreValue = value;
          
                var tension = currValues.tension;
                currValues['abs_score'] = absScoreValue;
                currValues['s_abs_score'] = absScoreValue;
                currValues['pvalue'] = 1;
                
                d3.select('#abs_scoreValue').text(absScoreValue.toPrecision(5));
                
                var FlareData = filterData(absScoreValue, 1, 'score_abs');
      
                var linkLine = updateBundle(FlareData);
      
                var line = linkLine.line;
                var link = linkLine.link;
      
                line.interpolate("bundle").tension(tension);
                link.attr("d", line);
        });
    
        d3.select('#absScoreSlider').call(abs_scoreSlider); 
     
        d3.select('#p_scoreValue').text(d3.min(p_scores).toPrecision(5));
        
        var p_scoreSlider = d3.slider().scale(d3.scale.linear().domain([d3.min(p_scores), d3.max(p_scores)]).clamp(true)).value(d3.min(p_scores)).min(d3.min(p_scores)).max(d3.max(p_scores)).step(1E-20).on("slide", function(evt, value) {
    
                var p_scoreValue = value;
                var tension = currValues.tension;
                currValues['p_score'] = p_scoreValue;
                currValues['s_p_score'] = p_scoreValue;
                currValues['pvalue'] = 1;
    
                d3.select('#p_scoreValue').text(p_scoreValue.toPrecision(5));
          
                var FlareData = filterData(p_scoreValue, 1, 'score_pos');
      
                var linkLine = updateBundle(FlareData);
      
                var line = linkLine.line;
                var link = linkLine.link;
      
                line.interpolate("bundle").tension(tension);
                link.attr("d", line);
        });
     
        d3.select('#posScoreSlider').call(p_scoreSlider);
        
        d3.select('#n_scoreValue').text(d3.max(n_scores).toPrecision(5));
     
        var n_scoreSlider = d3.slider().scale(d3.scale.linear().domain([d3.min(n_scores), d3.max(n_scores)]).clamp(true)).value(d3.max(n_scores)).min(d3.min(n_scores)).max(d3.max(n_scores)).step(1E-20).on("slide", function(evt, value) {
                var n_scoreValue = value;
                var tension = currValues.tension;
                currValues['n_score'] = n_scoreValue;
                currValues['s_n_score'] = n_scoreValue;
                currValues['pvalue'] = 1;
                
                d3.select('#n_scoreValue').text(n_scoreValue.toPrecision(5));
                
                var FlareData = filterData(n_scoreValue, 1, 'score_neg');
      
                var linkLine = updateBundle(FlareData);
      
                var line = linkLine.line;
                var link = linkLine.link;
      
                line.interpolate("bundle").tension(tension);
                link.attr("d", line);
        });
    
        d3.select('#negScoreSlider').call(n_scoreSlider);
     
        d3.select('#pvalueValue').text(d3.max(pvalues).toPrecision(5));
            
        var pvalueSlider = d3.slider().scale(d3.scale.log().domain([Math.log(d3.min(pvalues)), Math.log(d3.max(pvalues))]).clamp(true)).value(Math.log(d3.max(pvalues))).min(Math.log(d3.min(pvalues))).max(Math.log(d3.max(pvalues))).step(0.00001).on("slide", function(evt, value) {
    
                var pvalueValue = Math.exp(value);                       
                var tension = currValues.tension;
                currValues['abs_score'] = -1
                currValues['p_score'] = 0
                currValues['n_score'] = -1
                currValues['pvalue'] = pvalueValue;
                currValues['s_pvalue'] = pvalueValue;
                
                d3.select('#pvalueValue').text(pvalueValue.toPrecision(5));
          
                var FlareData = filterData(-1, pvalueValue, 'pvalue');
      
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
                var abs_scoreValue = currValues.abs_score;
                var p_scoreValue = currValues.p_score;
                var n_scoreValue = currValues.n_score;
                currValues['tension'] = tension;
      
                d3.select('#tensionValue').text(tension.toPrecision(2));
          
                var form = document.getElementById("filterType")
                var form_val;
      
                for(var i=0; i<form.length; i++){
                    if(form[i].checked){
                        form_val = form[i].id;        
                    }
                }
      
                if (form_val == "scoreRadio") { 
          
                    var score_form = document.getElementById("scoreSelect")
                    var score_form_val;
      
                    for(var i=0; i<score_form.length; i++){
                        if(score_form[i].checked){
                            score_form_val = score_form[i].id;        
                        }
                    }
      
                    if (score_form_val == "PosScoreRadio") {
                        var FlareData = filterData(p_scoreValue, 1, 'score_pos');
                    } else if (score_form_val == "NegScoreRadio") {
                        var FlareData = filterData(n_scoreValue, 1, 'score_neg');
                    } else if (score_form_val == "AbsScoreRadio") {
                        var FlareData = filterData(abs_scoreValue, 1, 'score_abs');
                    }
                } else if (form_val == "pvalueRadio") {
                    var FlareData = filterData(-1, pvalueValue, 'pvalue');
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
      
            if (form_val == "scoreRadio") { 
                d3.select('#abs_scoreHide').style("display", 'block');
                d3.select('#p_scoreHide').style("display", 'none');
                d3.select('#n_scoreHide').style("display", 'none');
                d3.select('#scoreSelect').style("display", 'block');
                d3.select('#pvalueHide').style("display", 'none');
        
                var form_score = document.getElementById("scoreSelect")
                var form_val_score;
      
                for(var i=0; i<form_score.length; i++){
                    if(form_score[i].checked){
                        form_val_score = form_score[i].id;        
                    }
                }
      
                if (form_val_score == "PosScoreRadio") {
                    d3.select('#p_scoreHide').style("display", 'block');
                    d3.select('#n_scoreHide').style("display", 'none');
                    d3.select('#abs_scoreHide').style("display", 'none');
                
                    var FlareData = filterData(currValues.s_p_score, 1, 'score_pos');
                } else if (form_val_score == "NegScoreRadio") {
                    d3.select('#p_scoreHide').style("display", 'none');
                    d3.select('#n_scoreHide').style("display", 'block');
                    d3.select('#abs_scoreHide').style("display", 'none');
                
                    var FlareData = filterData(currValues.s_n_score, 1, 'score_neg');
                } else if (form_val_score == "AbsScoreRadio") {
                    d3.select('#p_scoreHide').style("display", 'none');
                    d3.select('#n_scoreHide').style("display", 'none');
                    d3.select('#abs_scoreHide').style("display", 'block');
                
                    var FlareData = filterData(currValues.s_abs_score, 1, 'score_abs');
                }  
    
                var linkLine = updateBundle(FlareData);
        
            } else if (form_val == "pvalueRadio") {
                d3.select('#abs_scoreHide').style("display", 'none');
                d3.select('#p_scoreHide').style("display", 'none');
                d3.select('#n_scoreHide').style("display", 'none');
                d3.select('#scoreSelect').style("display", 'none');
                d3.select('#pvalueHide').style("display", 'block');
    
                var FlareData = filterData(-1, currValues.s_pvalue, 'pvalue');
                var linkLine = updateBundle(FlareData);
            }
      
            var tension = currValues.tension;
      
            var line = linkLine.line;
            var link = linkLine.link;
      
            line.interpolate("bundle").tension(tension);
            link.attr("d", line);
        }
    
        function changeScore() {
        
            var form = document.getElementById("scoreSelect")
            var form_val;
      
            for(var i=0; i<form.length; i++) {
                if(form[i].checked){
                    form_val = form[i].id;        
                }
            }
      
            if (form_val == "PosScoreRadio") { 
                d3.select('#p_scoreHide').style("display", 'block');
                d3.select('#n_scoreHide').style("display", 'none');
                d3.select('#abs_scoreHide').style("display", 'none');
       
                var FlareData = filterData(currValues.s_p_score, 1, 'score_pos');
                var linkLine = updateBundle(FlareData);
        
            } else if (form_val == "NegScoreRadio") {
                d3.select('#p_scoreHide').style("display", 'none');
                d3.select('#n_scoreHide').style("display", 'block');
                d3.select('#abs_scoreHide').style("display", 'none');
        
                var FlareData = filterData(currValues.s_n_score, 1, 'score_neg');
                var linkLine = updateBundle(FlareData);
        
            } else if (form_val == "AbsScoreRadio") {
                d3.select('#p_scoreHide').style("display", 'none');
                d3.select('#n_scoreHide').style("display", 'none');
                d3.select('#abs_scoreHide').style("display", 'block');
        
                var FlareData = filterData(currValues.s_abs_score, 1, 'score_abs');
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
    
        var selectDim = d3.select("#scoreSelect");
        selectDim.on("change", changeScore);
    
        function updateBundle(data) {
    
            pvalues = []
            p_scores = []
            n_scores = []
            abs_scores = []
    
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
                                , d.link_color = d.source.imports[d.target.id]["link_color"]
                                , d.link_score = d.source.imports[d.target.id]["link_score"]                               
                                , abs_scores.push(Math.abs(d.source.imports[d.target.id]["link_score"]))
                                , pvalues.push(d.source.imports[d.target.id]["link_pvalue"])              
                                , d.link_pvalue = d.source.imports[d.target.id]["link_pvalue"];
                                
                                if (d.source.imports[d.target.id]["link_score"] >= 0) {
                                    
                                    p_scores.push(d.source.imports[d.target.id]["link_score"]);
                                     
                                } else {
                                
                                    n_scores.push(d.source.imports[d.target.id]["link_score"]);
                                    
                                }  								
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
            
                link.style('opacity', o => (o.source === d || o.target === d ? 1 : $linkFadeOpacity))
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
    
                function find(id, data) {
                    var node = map[id], i;
                    if (!node) {
                        node = map[id] = data || {id: id, children: []};
                        if (id.length) {
                            node.parent = find(id.substring(0, i = id.lastIndexOf("#")));
                            node.parent.children.push(node);
                            node.key = id.substring(i + 1);
                        }
                    }
                    return node;
                }
    
                classes.forEach(function(d) {
                    find(d.id, d);
                });
    
                return map[""];
            }
    
            function packageImports(nodes) {
                var map = {}, imports = [];
    
                nodes.forEach(function(d) {
                    map[d.id] = d;
                });
    
                nodes.forEach(function(d) {       
                    if (d.imports) Object.keys(d.imports).forEach(function(i) {    
                        imports.push({source: map[d.id], target: map[i]});
                    });
                });
    
                return imports;
            }
      
            return linkLine;
        }   
    
        function filterData(scoreThresh, pvalueThresh, filtType) {
    
            const data = $flareData.map(a => ({...a}));
      
            var FlareData = []
      
            //Remove nodes from imports with weight below threshold
            for (var i = 0; i < data.length; i++) {
                var flare = data[i];
        
                var links = flare.imports;
                var newLinks = {}
        
                for (const [key, value] of Object.entries(links)) {
    
                    var link_score = value["link_score"];
                    var link_pvalue = value["link_pvalue"];
                    var link_color = value["link_color"];
                    
                    if (filtType == 'score_abs') {
                    
                        if (Math.abs(link_score) > scoreThresh) {
                                newLinks[key] = {"link_score": link_score
                                            , "link_pvalue": link_pvalue
                                            , "link_color": link_color};
                        }
                            
                    } else if (filtType == 'score_neg') {
                    
                         if (link_score < scoreThresh) {
                                newLinks[key] = {"link_score": link_score
                                        , "link_pvalue": link_pvalue
                                        , "link_color": link_color};
                        }
                        
                    } else if (filtType == 'score_pos') {
                        if (link_score > scoreThresh) {
                                newLinks[key] = {"link_score": link_score
                                        , "link_pvalue": link_pvalue
                                        , "link_color": link_color};
                        }
                        
                    } else if (filtType == 'pvalue') {
                        if (link_pvalue <= pvalueThresh) {
                            newLinks[key] = {"link_score": link_score
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

    def __getHTMLbundle(self):

        html_text = '''
        
        <body>
    
            <style> $css_text </style>
    
            <div id="wrapper">
                <form id="filterType">
                    <input type='radio' id="scoreRadio" name="mode" checked/>Corr. coeff
                    <input type='radio' id="pvalueRadio" name="mode"/>Pvalue
                </form>
      
                <form id="scoreSelect">
                    <input type='radio' id="PosScoreRadio" name="mode"/>Positive
                    <input type='radio' id="NegScoreRadio" name="mode"/>Negative
                    <input type='radio' id="AbsScoreRadio" name="mode" checked/>Absolute
                </form>
      
                <div id="abs_scoreHide">
                    <h3 id="abs_score">Corr. coeff: <div id="absScoreSlider"></div><span style="white-space: nowrap;" id="abs_scoreValue">0</span></h3>
                </div> 
    
                <div id="p_scoreHide">
                    <h3 id="p_score"> Corr. coeff: <div id="posScoreSlider"></div><span style="white-space: nowrap;" id="p_scoreValue"></span></h3>
                </div>
    
                <div id="n_scoreHide">
                    <h3 id="n_score"> Corr. coeff: <div id="negScoreSlider"></div><span style="white-space: nowrap;" id="n_scoreValue"></span></h3>
                </div>
      
                <div id="pvalueHide">
                    <h3 id="pvalue"> Pvalue: <div id="pvalueSlider"></div><span style="white-space: nowrap;" id="pvalueValue"></span></h3>
                </div>
    
                <h3 id="tension">Tension: <div id="tensionSlider"></div><span style="white-space: nowrap;" id="tensionValue"></span></h3>
            </div>
      
            <script src="https://d3js.org/d3.v3.min.js"></script>
    
            <script> $js_text </script>
    
        </body>
        
        '''

        return html_text

    def __df_to_flareJson(self, edges):
        """Convert dataframe into nested JSON as in flare files used for D3.js"""
        flare = dict()
        d = {"name": "flare", "children": []}

        for index, row in edges.iterrows():

            if len(row) > 12:
                parent_index = row[0]
                parent_name = row[1]
                parent_color = row[2]
                parent_label = row[3]
                parent_group = row[4]
                child_index = row[5]
                child_name = row[6]
                child_color = row[7]
                child_label = row[8]
                child_group = row[9]
                link_score = row[10]
                link_sign = row[11]
                link_pvalue = row[12]
                link_color = row[13]

                # Make a list of keys
                key_list = []
                for item in d['children']:
                    key_list.append(item['id'])

                # if parent index is NOT a key in flare.JSON, append it
                if not parent_index in key_list:
                    d['children'].append({"id": parent_index, "name": parent_label, "node_color": parent_color, "group": parent_group, "children": [{"id": child_index, "name": child_label, "node_color": child_color, "link_score": link_score, "link_sign": link_sign, "link_pvalue": link_pvalue, "group": child_group, "link_color": link_color}]})

                # if parent index IS a key in flare.json, add a new child to it
                else:
                    d['children'][key_list.index(parent_index)]['children'].append({"id": child_index, "name": child_label, "node_color": child_color, "link_score": link_score, "link_sign": link_sign, "link_pvalue": link_pvalue, "group": child_group, "link_color": link_color})
            else:
                parent_index = row[0]
                parent_name = row[1]
                parent_color = row[2]
                parent_label = row[3]
                child_index = row[4]
                child_name = row[5]
                child_color = row[6]
                child_label = row[7]
                link_score = row[8]
                link_sign = row[9]
                link_pvalue = row[10]
                link_color = row[11]

                # Make a list of keys
                key_list = []
                for item in d['children']:
                    key_list.append(item['id'])

                # if parent index is NOT a key in flare.JSON, append it
                if not parent_index in key_list:
                    d['children'].append({"id": parent_index, "name": parent_label, "node_color": parent_color, "children": [{"id": child_index, "name": child_label, "node_color": child_color, "link_score": link_score, "link_sign": link_sign, "link_pvalue": link_pvalue, "link_color": link_color}]})

                # if parent index IS a key in flare.json, add a new child to it
                else:
                    d['children'][key_list.index(parent_index)]['children'].append({"id": child_index, "name": child_label, "node_color": child_color, "link_score": link_score, "link_sign": link_sign, "link_pvalue": link_pvalue, "link_color": link_color})

        flare = d

        return flare

    def __df_to_Json(self, edges):

        flare = self.__df_to_flareJson(edges);

        flareString = ""

        bundleJsonArray = []
        completeChildList = []

        for key, value in flare.items():

            if isinstance(value, str):
                flareString = value
            elif isinstance(value, list):

                for idx, val in enumerate(value):

                    if "start_block" in edges.columns:
                        dParent = {"id": "", "name": "", "node_color": "", "group": "", "imports": {}}
                        parent_index = str(value[idx]['id'])
                        parentGroup = str(value[idx]['group'])

                        flareParentIndex = flareString + "#" + parentGroup + "#" + parent_index

                        dParent["group"] = parentGroup

                    else:
                        parent_index = str(value[idx]['id'])
                        dParent = {"id": "", "name": "", "node_color": "", "imports": {}}

                        flareParentIndex = flareString + "#" + parent_index

                    parentName = str(value[idx]['name'])
                    parentColor = str(value[idx]['node_color'])

                    dParent["id"] = flareParentIndex
                    dParent["name"] = parentName
                    dParent["node_color"] = parentColor

                    childList = value[idx]['children']

                    for child in childList:
                        link_score = float(child['link_score'])
                        link_sign = float(child['link_sign'])
                        link_pvalue = float(child['link_pvalue'])
                        link_color = str(child['link_color'])

                        if "start_block" in edges.columns:
                            dChild = {"id": "", "name": "", "node_color": "", "group": "", "imports": {}}
                            child_index = str(child['id'])
                            childGroup = str(child['group'])

                            flareChildIndex = flareString + "#" + childGroup + "#" + child_index

                            dChild["group"] = childGroup

                        else:
                            child_index = str(child['id'])
                            dChild = {"id": "", "name": "", "node_color": "", "imports": {}}

                            flareChildIndex = flareString + "#" + child_index


                        childName = str(child['name'])
                        childColor = str(child['node_color'])

                        dParent["imports"][flareChildIndex] = {"link_score": link_score, "link_sign": link_sign, "link_pvalue": link_pvalue, "link_color": link_color}

                        dChild["id"] = flareChildIndex
                        dChild["name"] = childName
                        dChild["node_color"] = childColor

                        dChild["imports"][flareParentIndex] = {"link_score": link_score, "link_sign": link_sign, "link_pvalue": link_pvalue, "link_color": link_color}

                        completeChildList.append(dChild)

                    bundleJsonArray.append(dParent)
        bundleJsonArray.extend(completeChildList)

        return bundleJsonArray;

    def __get_colors(self, x, cmap):
        norm = matplotlib.colors.Normalize(vmin=x.min(), vmax=x.max())
        # norm = matplotlib.colors.Normalize(vmin=-1.0, vmax=1.0)

        # norm = plt.Normalize()
        return cmap(norm(x))

    def __edge_color(self, edges, color_scale, edgeCmap):
        colorsHEX = []

        signs = edges['Sign'].values

        if "Pvalue" in edges.columns:
            if "start_block" in edges.columns:
                edges_color = edges[['start_index', 'start_name', 'start_color', 'start_label', 'start_block', 'end_index', 'end_name', 'end_color', 'end_label', 'end_block', 'Score', 'Sign', 'Pvalue']]
            else:
                edges_color = edges[['start_index', 'start_name', 'start_color', 'start_label', 'end_index', 'end_name', 'end_color', 'end_label', 'Score', 'Sign', 'Pvalue']]
        else:

            if "start_block" in edges.columns:
                edges_color = edges[['start_index', 'start_name', 'start_color', 'start_label', 'start_block', 'end_index', 'end_name', 'end_color', 'end_label', 'end_block', 'Score', 'Sign']]
            else:
                edges_color = edges[['start_index', 'start_name', 'start_color', 'start_label', 'end_index', 'end_name', 'end_color', 'end_label', 'Score', 'Sign']]

        if color_scale == "Score":

            for i in range(edgeCmap.N):
                colorsHEX.append(matplotlib.colors.rgb2hex(edgeCmap(i)[:3]))

            signColors = []
            for sign in signs:
                if sign > 0:
                    signColors.append(colorsHEX[-1])
                else:
                    signColors.append(colorsHEX[0])

            edges_color = edges_color.assign(color=pd.Series(signColors, index=edges_color.index))
        elif color_scale == "Pvalue":

            if "Pvalue" in edges_color.columns:
                colorsRGB = get_colors(edges_color['Pvalue'].values, edgeCmap)[:, :3]

                for rgb in colorsRGB:
                    colorsHEX.append(matplotlib.colors.rgb2hex(rgb))

                edges_color = edges_color.assign(color=pd.Series(colorsHEX, index=edges_color.index))

            else:
                print("Pvalue in not a column in this dataset. Now choosing Score as a color scale.")

                for i in range(edgeCmap.N):
                    colorsHEX.append(matplotlib.colors.rgb2hex(edgeCmap(i)[:3]))

                signColors = []
                for sign in signs:
                    if sign > 0:
                        signColors.append(colorsHEX[-1])
                    else:
                        signColors.append(colorsHEX[0])

                edges_color = edges_color.assign(color=pd.Series(signColors, index=edges_color.index))

        return edges_color

    def run(self):

        edges = self.edges
        diameter = self.diameter
        innerRadiusOffset = self.innerRadiusOffset
        groupSeparation = self.groupSeparation
        linkFadeOpacity = self.linkFadeOpacity
        fontSize = self.fontSize
        backgroundColor = self.backgroundColor
        sliderTextColor = self.sliderTextColor
        filterOffSet = self.filterOffSet
        color_scale = self.color_scale
        edge_cmap = self.edge_cmap

        edgeCmap = plt.cm.get_cmap(edge_cmap)  # Sets the color pallete for the edges

        if "Pvalue" in edges.columns:
            edges = self.__edge_color(edges, color_scale, edgeCmap)
        elif "Score" in edges.columns:
            edges = self.__edge_color(edges, 'Score', edgeCmap)
        else:
            print("Error: Edges dataframe does not contain \"Pvalue\" or \"Score\".")

        bundleJson = self.__df_to_Json(edges);

        #with open('test.json', 'w') as file:

        #    file.write(json.dumps(bundleJson))


        css_text_template_bundle = Template(self.__getCSSbundle());
        js_text_template_bundle = Template(self.__getJSbundle())
        html_template_bundle = Template(self.__getHTMLbundle());

        js_text = js_text_template_bundle.substitute({'flareData': json.dumps(bundleJson)
                                                         , 'diameter': diameter
                                                         , 'innerRadiusOffset': innerRadiusOffset
                                                         , 'groupSeparation': groupSeparation
                                                         , 'linkFadeOpacity': linkFadeOpacity})

        css_text = css_text_template_bundle.substitute({'fontSize': str(fontSize) + 'px'
                                                           , 'backgroundColor': backgroundColor
                                                           , 'sliderTextColor': sliderTextColor
                                                           , 'radioOffSet': str(filterOffSet) + 'px'
                                                           , 'filterSliderOffSet': str(filterOffSet - 30) + 'px'
                                                           , 'tensionSliderOffSet': str(filterOffSet - 60) + 'px'})

        html = html_template_bundle.substitute({'css_text': css_text, 'js_text': js_text})

        return html