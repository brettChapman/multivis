import sys
from string import Template
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import json

class edgeBundle:
    """Class for edgeBundle to produce a hierarchical edge bundle.

        Parameters
        ----------
        edges : Pandas dataframe containing edges generated from Edge.

        Methods
        -------
        set_params : Set parameters - diameter, inner radius offset, group separation, link fade opacity, mouse over flag, font size, background colour, foreground colour, filter offset
                        , colour scale (value to colour edges by: 'Score' or 'Pvalue') and CMAP colour palette for edges.
        run : Generates and outputs the hierarchical edge bundle.
    """

    def __init__(self, edges):

        self.__edges = self.__checkData(edges);

        self.set_params()

    def set_params(self, diameter=960, innerRadiusOffset=120, groupSeparation=1, linkFadeOpacity=0.05, mouseOver=True, fontSize=10, backgroundColor='white', foregroundColor='black', filterOffSet=-60, color_scale='Score', edge_cmap="brg"):

        diameter, innerRadiusOffset, groupSeparation, linkFadeOpacity, mouseOver, fontSize, backgroundColor, foregroundColor, filterOffSet, color_scale, edge_cmap = self.__paramCheck(diameter, innerRadiusOffset, groupSeparation, linkFadeOpacity, mouseOver, fontSize, backgroundColor, foregroundColor, filterOffSet, color_scale, edge_cmap)

        self.__diameter = diameter;
        self.__innerRadiusOffset = innerRadiusOffset;
        self.__groupSeparation = groupSeparation;
        self.__linkFadeOpacity = linkFadeOpacity;
        self.__mouseOver = mouseOver;
        self.__fontSize = fontSize;
        self.__backgroundColor = backgroundColor;
        self.__foregroundColor = foregroundColor;
        self.__filterOffSet = filterOffSet;
        self.__color_scale = color_scale;
        self.__edge_cmap = edge_cmap;

    def run(self):

        edges = self.__edges
        diameter = self.__diameter
        innerRadiusOffset = self.__innerRadiusOffset
        groupSeparation = self.__groupSeparation
        linkFadeOpacity = self.__linkFadeOpacity
        mouseOver = self.__mouseOver
        fontSize = self.__fontSize
        backgroundColor = self.__backgroundColor
        foregroundColor = self.__foregroundColor
        filterOffSet = self.__filterOffSet
        color_scale = self.__color_scale
        edge_cmap = self.__edge_cmap

        edgeCmap = plt.cm.get_cmap(edge_cmap)  # Sets the color palette for the edges

        if "Pvalue" in edges.columns:
            edges = self.__edge_color(edges, color_scale, edgeCmap)
        elif "Score" in edges.columns:
            edges = self.__edge_color(edges, 'Score', edgeCmap)
        else:
            print("Error: Edges dataframe does not contain \"Pvalue\" or \"Score\".")
            sys.exit()

        if mouseOver:
            mouse = "true";
        else:
            mouse = "false";

        bundleJson = self.__df_to_Json(edges);

        css_text_template_bundle = Template(self.__getCSSbundle());
        js_text_template_bundle = Template(self.__getJSbundle())
        html_template_bundle = Template(self.__getHTMLbundle());

        js_text = js_text_template_bundle.substitute({'flareData': bundleJson
                                                         , 'diameter': diameter
                                                         , 'innerRadiusOffset': innerRadiusOffset
                                                         , 'groupSeparation': groupSeparation
                                                         , 'linkFadeOpacity': linkFadeOpacity
                                                         , 'mouseOver': mouse
                                                         , 'backgroundColor': backgroundColor})

        css_text = css_text_template_bundle.substitute({'fontSize': str(fontSize) + 'px'
                                                           , 'backgroundColor': backgroundColor
                                                           , 'foregroundColor': foregroundColor
                                                           , 'radioOffSet': str(filterOffSet) + 'px'
                                                           , 'filterSliderOffSet': str(filterOffSet - 40) + 'px'
                                                           , 'tensionSliderOffSet': str(filterOffSet - 70) + 'px'
                                                           , 'saveButtonOffSet': str(filterOffSet - 90) + 'px'})

        html = html_template_bundle.substitute({'css_text': css_text, 'js_text': js_text})

        return html

    def __checkData(self, df):

        if not isinstance(df, pd.DataFrame):
            print("Error: A dataframe was not entered. Please check your data.")
            sys.exit()

        return df

    def __paramCheck(self, diameter, innerRadiusOffset, groupSeparation, linkFadeOpacity, mouseOver, fontSize, backgroundColor, foregroundColor, filterOffSet, color_scale, edge_cmap):

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

        if not type(mouseOver) == bool:
            print("Error: Mouse over is not valid. Choose either \"True\" or \"False\".")
            sys.exit()

        if not isinstance(fontSize, float):
            if not isinstance(fontSize, int):
                print("Error: Font size is not valid. Choose a float or integer value.")
                sys.exit()

        if not matplotlib.colors.is_color_like(backgroundColor):
            print("Error: Background colour is not valid. Choose a valid colour value.")
            sys.exit()

        if not matplotlib.colors.is_color_like(foregroundColor):
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

        return diameter, innerRadiusOffset, groupSeparation, linkFadeOpacity, mouseOver, fontSize, backgroundColor, foregroundColor, filterOffSet, color_scale, edge_cmap

    def __getCSSbundle(self):

        css_text = '''
        .node {
            font: "Helvetica Neue", Helvetica, Arial, sans-serif;
            font-size: $fontSize;
        }
        
        body {background-color: $backgroundColor;}

        .node:hover {
            stroke-opacity: 1.0;
            font-weight: bold;
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
            font-weight: bold;
        }
               
        .node:hover,
        .link--source,
        .link--target {
            stroke-opacity: 1.0;
        }
       
        .node--source {
            stroke-opacity: 1.0;
            stroke-width: 2px;
            font-weight: bold;
        }
    
        .node--target {
            stroke-opacity: 1.0;
            stroke-width: 2px;
            font-weight: bold;
        }
       
        .node--both {
            stroke-opacity: 1.0;
            stroke-width: 2px;
            font-weight: bold;
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
            color: $foregroundColor;
        }
       
        #scoreSelect {
            position: absolute;
            bottom: $radioOffSet;
            left: 160px;
            color: $foregroundColor;
        }
     
        #abs_score, #p_score, #n_score, #pvalue {
            position: absolute;
            bottom: $filterSliderOffSet;
            left: 0px;
            color: $foregroundColor;
        }
        
        #absScoreSlider, #posScoreSlider, #negScoreSlider, #pvalueSlider {
            position: absolute;
            bottom: -115px;     
            left: 85px;
        }
        
        #tension {
            position: absolute;
            bottom: $tensionSliderOffSet;
            left: 0px;
            color: $foregroundColor;
        }
        
        #tensionSlider {
            position: absolute;
            bottom: -115px;            
            left: 85px;
        }
      
        #abs_scoreValue, #p_scoreValue, #n_scoreValue, #pvalueValue, #tensionValue {
            position: absolute;
            bottom: 0px;
            left: 315px;
            color: $foregroundColor;
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
        
        #save {
            position: absolute;
            bottom: $saveButtonOffSet;
            left: 0px;
            color: $foregroundColor;     
        }   
                
        h3, text {
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
        
        var flareData = $flareData
        
        var pvalues = [];
        var p_scores = [];
        var n_scores = [];
        var abs_scores = [];
        
        var diameter = $diameter,
            radius = diameter / 2,
            innerRadius = radius - $innerRadiusOffset;
        
        var cluster = d3.cluster()
		            .separation(function(a, b) { return (a.parent == b.parent ? 1 : $groupSeparation ) })
                    .size([360, innerRadius]);
        
        var canvas = d3.select("#wrapper")
		                .append("svg")
		                .attr("id", "edgeBundle")
    	                .attr("width", diameter)
    	                .attr("height", diameter)
                        .append("g")
    	                .attr("transform", "translate(" + radius + "," + radius + ")")
                        .append("g");
        
        var node = canvas.selectAll(".node");
        var link = canvas.selectAll(".link");
        
        d3.select("#save")
                .on('click', function(){
		        
                    var options = {
                            canvg: window.canvg,
                            backgroundColor: '$backgroundColor',
                            height: diameter+100,
                            width: diameter+100,
                            left: -50,
                            scale: 5/window.devicePixelRatio,
                            encoderOptions: 1,
                            ignoreMouse : true,
                            ignoreAnimation : true,
                    }
		    
                    saveSvgAsPng(d3.select('svg#edgeBundle').node(), "edgeBundle.png", options);
                })
                
        var linkLine = updateBundle(flareData);    //Initial generation of bundle to populate arrays
                                
        var currValues = {'abs_score': 0               
                        , 'p_score': 0                
                        , 'n_score': 0                
                        , 'pvalue': 1                
                        , 'tension': 0.85};
        
        var abs_scaleLinksLinear = d3.scaleLinear()
            .domain(d3.extent(abs_scores))
            .range([1,1000])
            .clamp(true);
        
        d3.select('#abs_scoreValue').text(d3.min(abs_scores).toPrecision(5));
        
        var sliderWidth = 225;
        var sliderOffSet = 45;
        
        var abs_scoreSlider = d3.sliderHorizontal()
    	    					.min(abs_scaleLinksLinear(d3.min(abs_scores)))
    							.max(abs_scaleLinksLinear(d3.max(abs_scores)))
                                .default(abs_scaleLinksLinear(d3.min(abs_scores)))
                                .ticks(0)
                                .handle(d3.symbol().type(d3.symbolCircle).size(150)())
    							.step(0.0001)                        
                                .fill('#2196f3')
    							.width(sliderWidth - sliderOffSet)
    							.displayValue(false)
    							.on('onchange', value => {
      							    				
                                    var absScoreValue = abs_scaleLinksLinear.invert(value);
                                        
                    				var tension = currValues.tension;
                					currValues['abs_score'] = absScoreValue;
                						
                					d3.select('#abs_scoreValue').text(absScoreValue.toPrecision(5));
                						
                					var FlareData = filterData(absScoreValue, 'score_abs');
      											
                					var linkLine = updateBundle(FlareData);
      
                					var line = linkLine.line;
                					var link = linkLine.link;
      
                					line.curve(d3.curveBundle.beta(tension));
                    				link.attr('d', d => line(d.source.path(d.target)));          
          						});
        
        d3.select('#absScoreSlider')
                .append('svg')
                .attr('width', sliderWidth)    
                .append('g')    
                .attr('transform', 'translate(30,30)')
                .call(abs_scoreSlider);
        
        if (p_scores.length != 0) {
        
            var pos_scaleLinksLinear = d3.scaleLinear()
                .domain(d3.extent(p_scores))
                .range([1,1000])
                .clamp(true);
        
            d3.select('#p_scoreValue').text(d3.min(p_scores).toPrecision(5));
        
            var pos_scoreSlider = d3.sliderHorizontal()
								    .min(pos_scaleLinksLinear(d3.min(p_scores)))
    							    .max(pos_scaleLinksLinear(d3.max(p_scores)))
                                    .default(pos_scaleLinksLinear(d3.min(p_scores)))
                                    .ticks(0)
                                    .handle(d3.symbol().type(d3.symbolCircle).size(150)())
    							    .step(0.0001)                        
                                    .fill('#2196f3')
    							    .width(sliderWidth - sliderOffSet)
    							    .displayValue(false)
    							    .on('onchange', value => {
      											            
                    				    var p_scoreValue = pos_scaleLinksLinear.invert(value);
                						
                					    var tension = currValues.tension;
                					    currValues['p_score'] = p_scoreValue;
    												
                					    d3.select('#p_scoreValue').text(p_scoreValue.toPrecision(5));
          									
                					    var FlareData = filterData(p_scoreValue, 'score_pos');
														      							
                					    var linkLine = updateBundle(FlareData);
														      							
                					    var line = linkLine.line;
                					    var link = linkLine.link;
      											
                					    line.curve(d3.curveBundle.beta(tension));
                					    link.attr("d", d => line(d.source.path(d.target)));        
          						    });
        
            d3.select('#posScoreSlider')
                    .append('svg')
                    .attr('width', sliderWidth)
                    .append('g')    
                    .attr('transform', 'translate(30,30)')
                    .call(pos_scoreSlider);
        } else {
        
            d3.select('#p_scoreValue').text('none');
        
        }
        
        if (n_scores.length != 0) {
                
            var neg_scaleLinksLinear = d3.scaleLinear()
                .domain(d3.extent(n_scores))
                .range([1,1000])
                .clamp(true);
            
            d3.select('#n_scoreValue').text(d3.max(n_scores).toPrecision(5));
            
            var neg_scoreSlider = d3.sliderHorizontal()
			    					.min(neg_scaleLinksLinear(d3.min(n_scores)))
    			    				.max(neg_scaleLinksLinear(d3.max(n_scores)))
                                    .default(neg_scaleLinksLinear(d3.max(n_scores)))
                                    .ticks(0)
                                    .handle(d3.symbol().type(d3.symbolCircle).size(150)())
    					    		.step(0.0001)                        
                                    .fill('#2196f3')
    					    		.width(sliderWidth - sliderOffSet)
    							    .displayValue(false)
    							    .on('onchange', value => {
      											                						
                					    var n_scoreValue = neg_scaleLinksLinear.invert(value);
                						
                					    var tension = currValues.tension;
                					    currValues['n_score'] = n_scoreValue;
                						
                					    d3.select('#n_scoreValue').text(n_scoreValue.toPrecision(5));
                						
                					    var FlareData = filterData(n_scoreValue, 'score_neg');
														      							
                					    var linkLine = updateBundle(FlareData);
      											
                					    var line = linkLine.line;
                					    var link = linkLine.link;
      											
                					    line.curve(d3.curveBundle.beta(tension));
                					    link.attr("d", d => line(d.source.path(d.target)));          
          						    });
        
            d3.select('#negScoreSlider')
                    .append('svg')
                    .attr('width', sliderWidth)
                    .append('g')    
                    .attr('transform', 'translate(30,30)')
                    .call(neg_scoreSlider);
        
        } else {
            
            d3.select('#n_scoreValue').text('none');
            
        }
        
        if (pvalues.length != 0) {
        
            if (d3.min(pvalues) != 0.0) {
            
                var pvalue_scaleLinksLog = d3.scaleLog()
                        .domain(d3.extent(pvalues))          	    
                        .range([1,1000])
                        .clamp(true);
                        
            } else {
                        
                var pvalue_scaleLinksLog = d3.scaleSymlog()
                    .domain(d3.extent(pvalues))
                    .range([1,1000])
                    .clamp(true);
            }
        
            d3.select('#pvalueValue').text(d3.max(pvalues).toPrecision(5));
            
            var pvalueSlider = d3.sliderHorizontal()
                                .min(pvalue_scaleLinksLog(d3.min(pvalues)))
    						    .max(pvalue_scaleLinksLog(d3.max(pvalues)))
                                .default(pvalue_scaleLinksLog(d3.max(pvalues)))
                                .ticks(0)
                                .handle(d3.symbol().type(d3.symbolCircle).size(150)())
    						    .step(0.0001)                        
                                .fill('#2196f3')
    						    .width(sliderWidth - sliderOffSet)
    						    .displayValue(false)
    					        .on('onchange', value => {
      							
                                    var pvalueValue = pvalue_scaleLinksLog.invert(value);
                    				
                    			    var tension = currValues.tension;
                				    currValues['pvalue'] = pvalueValue;
                						
                				    d3.select('#pvalueValue').text(pvalueValue.toPrecision(5));
          									
                				    var FlareData = filterData(pvalueValue, 'pvalue');
      										
                				    var linkLine = updateBundle(FlareData);
      											
                				    var line = linkLine.line;
                				    var link = linkLine.link;
      							    
                				    line.curve(d3.curveBundle.beta(tension));
                				    link.attr("d", d => line(d.source.path(d.target)));                            
          					    });
        
            d3.select('#pvalueSlider')
                    .append('svg')
                    .attr('width', sliderWidth)
                    .append('g')    
                    .attr('transform', 'translate(30,30)')
                    .call(pvalueSlider);
        } else {
            
            d3.select('#pvalueValue').text('none');
         
        }
        
        var tension_scaleLinear = d3.scaleLinear()
			.domain([0,1])
            .range([0,20])
            .clamp(true);
        
        d3.select('#tensionValue').text(currValues.tension);
        
        var tensionSlider = d3.sliderHorizontal()
							.min(tension_scaleLinear(0.0))
    						.max(tension_scaleLinear(1.0))
                            .default(tension_scaleLinear(0.85))
                            .ticks(0)
                            .handle(d3.symbol().type(d3.symbolCircle).size(150)())
    						.step(0.01)                        
                            .fill('#2196f3')
    						.width(sliderWidth - sliderOffSet)
    						.displayValue(false)
    						.on('onchange', value => {
      											            
                    		    var tension =  tension_scaleLinear.invert(value);
                				currValues['tension'] = tension;
      											
                				d3.select('#tensionValue').text(tension.toPrecision(2));
          
               					var form = document.getElementById("filterType")
                				var form_val;
      											
                				for(var i=0; i<form.length; i++) {
                    				if(form[i].checked) {
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
                              	        var p_scoreValue = currValues.p_score;
                        				var FlareData = filterData(p_scoreValue, 'score_pos');
                    				} else if (score_form_val == "NegScoreRadio") {
                              	        var n_scoreValue = currValues.n_score;
                        				var FlareData = filterData(n_scoreValue, 'score_neg');
                    				} else if (score_form_val == "AbsScoreRadio") {
                              	        var abs_scoreValue = currValues.abs_score;
                        				var FlareData = filterData(abs_scoreValue, 'score_abs');
                    				}
                				} else if (form_val == "pvalueRadio") {
                            	    var pvalueValue = currValues.pvalue;
                    				var FlareData = filterData(pvalueValue, 'pvalue');
								}
                
                				var linkLine = updateBundle(FlareData);
                                
                				var line = linkLine.line;
                				var link = linkLine.link;
                                
                				line.curve(d3.curveBundle.beta(tension));
                				link.attr("d", d => line(d.source.path(d.target)));     
          					});
                                
        d3.select('#tensionSlider')
                .append('svg')
                .attr('width', sliderWidth)
                .append('g')    
                .attr('transform', 'translate(30,30)')
                .call(tensionSlider);
        
        function changeFilter() {
            
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
                    
                    //Filter out all links prior to updating with the score threshold
                    var FlareData = filterData(1, 'score_pos');
    		        var linkLine = updateBundle(FlareData);
    		        
    		        var FlareData = filterData(currValues.p_score, 'score_pos');        
    		        var linkLine = updateBundle(FlareData);
                } else if (form_val_score == "NegScoreRadio") {
                    d3.select('#p_scoreHide').style("display", 'none');
                    d3.select('#n_scoreHide').style("display", 'block');
                    d3.select('#abs_scoreHide').style("display", 'none');
                    
                    var FlareData = filterData(-1, 'score_neg');    
    		        var linkLine = updateBundle(FlareData);
    		        
  			        var FlareData = filterData(currValues.n_score, 'score_neg');  
  			        var linkLine = updateBundle(FlareData);       
                } else if (form_val_score == "AbsScoreRadio") {
                    d3.select('#p_scoreHide').style("display", 'none');
                    d3.select('#n_scoreHide').style("display", 'none');
                    d3.select('#abs_scoreHide').style("display", 'block');
                    
                    //Filter out all links prior to updating with the score threshold
                    var FlareData = filterData(1, 'score_abs');
    		        var linkLine = updateBundle(FlareData);
                    
    		        var FlareData = filterData(currValues.abs_score, 'score_abs');
    		        var linkLine = updateBundle(FlareData);
                }
   	        } else if (form_val == "pvalueRadio") {
       	        d3.select('#abs_scoreHide').style("display", 'none');
                d3.select('#p_scoreHide').style("display", 'none');
                d3.select('#n_scoreHide').style("display", 'none');
                d3.select('#scoreSelect').style("display", 'none');
                d3.select('#pvalueHide').style("display", 'block');
                
    		    //Filter out all links prior to updating with the pvalue threshold
                var FlareData = filterData(-1, 'pvalue');
    		    var linkLine = updateBundle(FlareData);
                
    		    var FlareData = filterData(currValues.pvalue, 'pvalue');
                var linkLine = updateBundle(FlareData);
            }
      
            var tension = currValues.tension;
            
            var line = linkLine.line;
            var link = linkLine.link;
            
            line.curve(d3.curveBundle.beta(tension));
            link.attr("d", d => line(d.source.path(d.target)));
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
                
   	            //Filter out all links prior to updating with the score threshold
                var FlareData = filterData(1, 'score_pos');
                var linkLine = updateBundle(FlareData);
                
                var FlareData = filterData(currValues.p_score, 'score_pos');        
                var linkLine = updateBundle(FlareData);      
                
            } else if (form_val == "NegScoreRadio") {
                d3.select('#p_scoreHide').style("display", 'none');
                d3.select('#n_scoreHide').style("display", 'block');
                d3.select('#abs_scoreHide').style("display", 'none');
                
                //Filter out all links prior to updating with the score threshold
                var FlareData = filterData(-1, 'score_neg');    
                var linkLine = updateBundle(FlareData);
                
  	            var FlareData = filterData(currValues.n_score, 'score_neg');  
  	            var linkLine = updateBundle(FlareData);        
            } else if (form_val == "AbsScoreRadio") {
                d3.select('#p_scoreHide').style("display", 'none');
                d3.select('#n_scoreHide').style("display", 'none');
                d3.select('#abs_scoreHide').style("display", 'block');
                
                //Filter out all links prior to updating with the score threshold
                var FlareData = filterData(1, 'score_abs');
                var linkLine = updateBundle(FlareData);
                
                var FlareData = filterData(currValues.abs_score, 'score_abs');
                var linkLine = updateBundle(FlareData);
            }
            
            var tension = currValues.tension;
                  
            var line = linkLine.line;
            var link = linkLine.link;
                  
            line.curve(d3.curveBundle.beta(tension));
            link.attr("d", d => line(d.source.path(d.target)));
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
            
	        var line = d3.radialLine()
    	        .curve(d3.curveBundle.beta(0.85))
    	        .radius(function(d) { return d.y; })
    	        .angle(function(d) { return d.x / 180 * Math.PI; });
            
            var root = d3.hierarchy(packageHierarchy(data), (d) => d.children);
            
            cluster(root)
            
            var nodes = root.descendants();
              
            node = node.data(nodes.filter(function(n) { return !n.children; }));
            
            node.exit().remove();
            
            if ("$mouseOver" == "true") {
            
                var newNode = node.enter().append("text")
                      	            .attr("class", "node")
    				    			.attr("dy", ".31em")
    					    		.attr("transform", function(d) { return "rotate(" + (d.x - 90) + ")translate(" + (d.y + 8) + ",0)" + (d.x < 180 ? "" : "rotate(180)"); })
    						    	.style("text-anchor", function(d) { return d.x < 180 ? "start" : "end"; })
      							    .text(function(d) { return d.data.name; })
      							    .style("fill", function(d) { return d.node_color; })
    							    .on("mouseover", mouseovered)
    							    .on("mouseout", mouseouted);
    	    } else {
    	    
    	        var newNode = node.enter().append("text")
                      	            .attr("class", "node")
    				    			.attr("dy", ".31em")
    					    		.attr("transform", function(d) { return "rotate(" + (d.x - 90) + ")translate(" + (d.y + 8) + ",0)" + (d.x < 180 ? "" : "rotate(180)"); })
    						    	.style("text-anchor", function(d) { return d.x < 180 ? "start" : "end"; })
      							    .text(function(d) { return d.data.name; })
      							    .style("fill", function(d) { return d.node_color; })
    							    .on("click", mouseovered)
    							    .on("dblclick", mouseouted);
    	    }
    							
            
            node = node.merge(newNode);
            
            var links = packageImports(root.descendants());
            
            links = links.map(d=> ({ ...d
  									, link_color: d.source.data.imports[d.target.data.id]["link_color"]
                                    , link_score: d.source.data.imports[d.target.data.id]["link_score"]
                                    , link_pvalue : d.source.data.imports[d.target.data.id]["link_pvalue"]}));
            
            links.forEach(function(d) { abs_scores.push(Math.abs(d.link_score))
  										, pvalues.push(d.link_pvalue);
                      				
                                        if (d.link_score >= 0) {
                                    
                        					p_scores.push(d.link_score);
                                     
                        			    } else {
                                
   	                        			    n_scores.push(d.link_score);
                                  
                        			    }
            	        });
            
            link = link.data(links);
            
            link.exit().remove();
              
            var newLink = link.enter().append("path")
    	      				.attr("class", "link")
            				.attr('d', d => line(d.source.path(d.target)))
            				.style("stroke", function(d) { return d.link_color; });
            
            link = link.merge(newLink);
            
            var linkLine = {"line": line, "link": link}            
            
	        function mouseovered(d) {
	        
	            //d3.select(this).style('font-weight', 'bold');
	        	            
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
                //node.style('font-weight', 'normal');
	        }
            
	        function packageHierarchy(classes) {
  		        var map = {};
                
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
    		        map[d.data.id] = d;
  		        });
                
  		        nodes.forEach(function(d) {
      		        if (d.data.imports) Object.keys(d.data.imports).forEach(function(i) {    
      				    imports.push({source: map[d.data.id], target: map[i]});
    			    });
  		        });
                
  		        return imports;
	        }
            
            return linkLine;
        }
        
        function filterData(threshold, filtType) {
            
            const data = flareData.map(a => ({...a}));
                        
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
                        
            		    if (Math.abs(link_score) >= threshold) {
                            newLinks[key] = {"link_score": link_score
                                            , "link_pvalue": link_pvalue
                                            , "link_color": link_color};
                        }
                            
                    } else if (filtType == 'score_neg') {
                        
                        if (link_score <= threshold) {
                            newLinks[key] = {"link_score": link_score
            	                            , "link_pvalue": link_pvalue
                                            , "link_color": link_color};
                        }
                        
                    } else if (filtType == 'score_pos') {
                        if (link_score >= threshold) {
                            newLinks[key] = {"link_score": link_score
                                           , "link_pvalue": link_pvalue
                                           , "link_color": link_color};
                        }
                                            
                    } else if (filtType == 'pvalue') {
                        if (link_pvalue <= threshold) {
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
                
                <button id='save'>Save</button>
            </div>
            
            <script src="https://d3js.org/d3.v5.min.js"></script>
            <script src="https://unpkg.com/d3-simple-slider"></script>
            <script src="https://github.com/canvg/canvg/blob/master/src/canvg.js"></script>
            <script src="https://exupero.org/saveSvgAsPng/src/saveSvgAsPng.js"></script>
    
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