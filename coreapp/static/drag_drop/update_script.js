var dashboard_obj={};
var tools_obj={};
var test_tools_obj={};
let row_constructor_object={}

// raw_endpoints_coloumns_data we are getting it directly from html file
let replace_quotes  = raw_endpoints_coloumns_data.replace(/&quot;/g,'"');
let endpoints_coloumn_data = JSON.parse(replace_quotes);


//GETTING AND PARSING THE OBJECT RECIEVED FROM BACKEND
var updated_object = document.getElementById('dashboard_format_id').value;
var final_updated_object = JSON.parse(updated_object);
console.log(final_updated_object)

// BELOW CODE IS USED TO STORE RICH TEXT VALUES IN AN OBJECT
for (var key in final_updated_object) {
	if (final_updated_object.hasOwnProperty(key)) {
		test_tools_obj = final_updated_object[key].rich_text;
	}
	for (var k in final_updated_object[key].row_constructor_object) {
			
		// console.log(k + " -> " + final_updated_object[key].row_constructor_object[k].col_1);
		row_constructor_object = final_updated_object[key].row_constructor_object;
		console.log(row_constructor_object)
	}

	// for(var k in final_updated_object[key].row_constructor){
		
	// 	console.log(k + " -> " + final_updated_object[key].row_constructor_object[k].col_1);
	// }

}



let dashboard_elements = document.getElementById('final_container').children;
// console.log(dashboard_elements)

// LOOPING THROUGH ALREADY PRESENT ELEMENTS IN FINAL CONTAINER
for(var i=0;i< dashboard_elements.length;i++){
	$('.view_endpoint_text').css('pointer-events','all');


	if(dashboard_elements[i].type === "text_editor"){


		
	//START: FUNCTION EXECUTES ONLY ONCE FOR EACH ELEMENT WHERE DYNAMIC MODAL CONTENT WILL BE APPENED WITH RICHTEXT
		$(document).one('click',"#edit_view_"+dashboard_elements[i].value, function (e) {

						if (e.target !== this){

							return;
						}

						// Reading parent value edit text element
						var get_parent_element_present_value = $("#"+e.target.id).parent('li').attr('data-present');
						var get_parent_element_value = $("#"+e.target.id).parent('li').attr('data-myvar');
						var get_parent_element_id = $("#"+e.target.id).parent('li').attr('id');
						console.log(get_parent_element_value)

					if(get_parent_element_present_value==="present_endpoint"){

						var html = `<div id="DYN-${get_parent_element_id}"  title="Rich Text Editor" style="display:none;">
												<span class="ui-state-default"><span class="ui-icon ui-icon-info" style="float:left; margin:0 7px 0 0;"></span></span>
												<div style="margin-left: 23px;" class="modal_box">
												<textarea class="content" name="example" id="TEXT-${get_parent_element_id}">${get_parent_element_value}</textarea>
												<input value="generating" class="" name="example" hidden id="INPUT-${get_parent_element_id}">
												 </div>
												</div>`;

						$("TEXT-"+get_parent_element_id).html(get_parent_element_value)
						$(".modal_section").append(html);
						$('#TEXT-'+get_parent_element_id).richText();

					}
			});
//END: FUNCTION EXECUTES ONLY ONCE FOR EACH ELEMENT WHERE DYNAMIC MODAL CONTENT WILL BE APPENED WITH RICHTEXT

		$(document).on('click',"#edit_view_"+dashboard_elements[i].value,function(e){

				// Reading parent value edit text element
				var get_parent_element_present_value = $("#"+e.target.id).parent('li').attr('data-present');
				var get_parent_element_value = $("#"+e.target.id).parent('li').attr('data-myvar');
				var get_parent_element_id = $("#"+e.target.id).parent('li').attr('id');
				var get_parent_element_li_value = $("#"+e.target.id).parent('li').attr('value');
				console.log(get_parent_element_li_value)


				openModal(this,"DYN-"+get_parent_element_id,"TEXT-"+get_parent_element_id,get_parent_element_id,get_parent_element_li_value)
		})
	}

else if(dashboard_elements[i].type === "end_point"){
		$('#'+dashboard_elements[i].id).children().css('pointer-events','');
		// console.log(dashboard_elements[i].id)
		// $('#'+dashboard_elements[i].id).children().css('pointer-events','');


		//START: ONCLICK FUNCTIONALITY FOR CLOSEMARK ICON
		$('#'+dashboard_elements[i].id).children().on('click',function (e) {

				// console.log(e.target.id);

				$("#" + e.target.id).parent().removeClass('done')
				$('#'+e.target.id).parent().removeClass('remove_class')
				$('#endpoint_container').append($("#"+e.target.id).parent());


				$("#" + e.target.id).remove("i");

				//dataset.myvar IS USED TO READ CUSTOM ATTRIBUTE FROM CROSSMARK ICON
				$("#three_dots_" + e.target.dataset.myvar).remove("i");

		});
		//END: ONCLICK FUNCTIONALITY FOR CLOSEMARK ICON


	}
	else if(dashboard_elements[i].type === "row_constructor"){
		$(document).one('click',"#edit_row_constructor_"+dashboard_elements[i].value, function (e) {

						if (e.target !== this){

							return;
						}

						// Reading parent value edit text element
						var get_parent_element_present_value = $("#"+e.target.id).parent('li').attr('data-row-constructor');
						var get_parent_element_value = $("#"+e.target.id).parent('li').attr('data-row-constructor-value');
						var get_parent_column_value = $("#"+e.target.id).parent('li').attr('data-column');
						var get_parent_element_id = $("#"+e.target.id).parent('li').attr('id');
						var selected_options;
						

							
					if(get_parent_element_present_value==="present_row_constructor"){
						
						if(get_parent_column_value=="2"){
							selected_options = `<select class="change_columns_${get_parent_element_id} form-control" name="change_columns" onchange="displayColumns('change_columns_${get_parent_element_id}','')">
																<option value="">CHOOSE COLUMNS</option>
																<option value="two_columns" selected>TWO COLUMNS</option>
																<option value="three_columns">THREE COLUMNS</option>
															</select>`

						}else if(get_parent_column_value=="3"){
							selected_options = `<select class="change_columns_${get_parent_element_id} form-control" name="change_columns" onchange="displayColumns('change_columns_${get_parent_element_id}','')">
																<option value="">CHOOSE COLUMNS</option>
																<option value="two_columns" >TWO COLUMNS</option>
																<option value="three_columns" selected>THREE COLUMNS</option>
															</select>`
						}
						
						var html = `<div id="row-constructor-${get_parent_element_id}"  title="ROW CONSTRUCTOR" style="display:none;">
													<span class="ui-state-default"><span class="ui-icon ui-icon-info" style="float:left; margin:0 7px 0 0;"></span></span>
													<div class="row" style="margin-left: 23px;" class="modal_box">
														<div class="col-md-6">
															${selected_options}
															<div class="row two_columns_">
																<div class="col-md-6 ">
																		<div class="two_target_options_1_${get_parent_element_id}">

																		</div>
																		<div>

																		</div>
																</div>
																<div class="col-md-6 ">
																		<div class="two_target_options_2_${get_parent_element_id}">

																		</div>
																		<div>

																		</div>
																</div>
															</div>
															<div class="row three_columns_">
																<div class="col-md-4 ">
																	<div class="three_target_options_1_${get_parent_element_id}">

																	</div>
																	<div>

																	</div>
																</div>
																<div class="col-md-4">
																		<div class="three_target_options_2_${get_parent_element_id}">

																		</div>
																		<div>

																		</div>
																</div>
																<div class="col-md-4">
																		<div class="three_target_options_3_${get_parent_element_id}">

																		</div>
																		<div>

																		</div>
																</div>
															</div>
														</div>
													</div>
											</div>`;
						// $("TEXT-"+get_parent_element_id).html(get_parent_element_value)
						$(".modal_section_row").append(html);
						// $('#TEXT-'+get_parent_element_id).richText();

					}
			});
//END: FUNCTION EXECUTES ONLY ONCE FOR EACH ELEMENT WHERE DYNAMIC MODAL CONTENT WILL BE APPENED WITH RICHTEXT

		$(document).on('click',"#edit_row_constructor_"+dashboard_elements[i].value,function(e){
				// alert("hi")
				// Reading parent value edit text element
				var get_parent_element_present_value = $("#"+e.target.id).parent('li').attr('data-present');
				// var get_parent_element_value = $("#"+e.target.id).parent('li').attr('data-myvar');
				var get_parent_element_id = $("#"+e.target.id).parent('li').attr('id');
				var get_parent_element_li_value = $("#"+e.target.id).parent('li').attr('value');
				openRowModal(this,"row-constructor-"+get_parent_element_id,get_parent_element_id,get_parent_element_li_value,true)
		})
	}

}
//END OF LOOPING THROUGH ALREADY PRESENT ELEMENTS IN FINAL CONTAINER


dragula([
	document.getElementById('endpoint_container'),
	document.getElementById('final_container'),
],{
	accepts: function (el, target, source, sibling) {
		return target !== document.getElementById('endpoint_container')
	}
})
.on('drop', function(el) {
	let dashboard_elements = document.getElementById('final_container').children;
	let test = document.getElementById('final_container');
	for(var i=0;i< dashboard_elements.length;i++){
		// console.log(dashboard_elements[i]);

	}

//IF LOOP IS USED TO ADD THE BELOW CODE TO ENDPOINT ONLY
	if(el.type === "end_point"){
		//IF LOOP IS USED TO PREVENT DUPLICATES ON DROPPING TO SAME CONTAINER
		if($('#'+el.id).hasClass("remove_class") !==true){
			$('#'+el.id).addClass('done');
			// $("#"+el.id).append('<i class="fa fa-times cross_mark_icon '+el.id+'" aria-hidden="true" ></i>');
			$("#"+el.id).append('<input type="checkbox" name="remove_arranged_elements" class="checkbox_styles endpoint_checkbox" />');
			$("#"+el.id).append('<i class="fas fa-bars endpoints_tool drag-header-more dots_'+el.id+'" aria-hidden="true" id="three_dots"></i>');
			//
			// $("#"+el.id).append('<i class="fa fa-ellipsis-v drag-header-more dots_'+el.id+'" aria-hidden="true" id="three_dots"></i>');
	}


	}


	$('.view_endpoint_text').css('pointer-events','all');
	document.getElementById('submit_button').disabled=false;
	// $("i").remove('.'+el.id);
	// // $("#"+el.id).append('<img src="/static/images/cross-mark.png" class='+el.id+' id="test">');

	$('.'+el.id).css('pointer-events','');





	$(document).on("click", '.'+el.id, function(chosen) {
		if(dashboard_elements.length ===0){
			document.getElementById('submit_button').disabled=true;
		}
	//
		$("i").remove( '.dots_'+el.id);
		$("i").remove('.'+el.id);

		$('#'+el.id).removeClass('remove_class');
		$('#endpoint_container').append($("#"+el.id));
		$('#'+el.id).removeClass('done')


	})


	// remove 'is-moving' class from element after dragging has stopped
	el.classList.remove('is-moving');
	// add the 'is-moved' class for 600ms then remove it
	window.setTimeout(function() {
		el.classList.add('is-moved');
		window.setTimeout(function() {
			el.classList.remove('is-moved');
		}, 600);
	}, 100);


});




// START: FUNCTION TO ADD DYNAMIC ID'S TO COPIED ELEMENTS

_.extend(dragula, {
	clone_id: dashboard_elements.length,
	count:1,
	setCloneId: function(el) {
		el.setAttribute('id', "BR"+this.clone_id++);
		el.setAttribute('value', this.clone_id);
		$(el).addClass('done');
		$(el).append('<input type="checkbox" class="checkbox_styles formatting_tools" />');
		$(el).append('<i class="fas fa-bars drag-header-more" title="Sorting Tool" aria-hidden="true" id="close-'+this.clone_id+'"></i>');
		if(el.type==="text_editor"){
			$(el).append('<a href="#" title="Click to edit" class="view_endpoint_text" id="edit_view_'+el.value+'" style="pointer-events: all;right: 29%;bottom: 43%;"  ><i class="fa fa-pencil-square-o" ></i> Edit</a>')
			$(el).append(`<div class="tooltip_dashboard" style="pointer-events:all">
											<i class="fa fa-eye search_icon_update" aria-hidden="true" ></i>
											<span class="tooltiptext_dashboard display_text" id="display_text_${el.value}" style="bottom: -7px;left: 46px;">It's Blank</span>
										</div>`
									)
		}else if(el.type==="row_constructor") {
			$(el).append('<a href="#" title="Click to edit" class="view_endpoint_text" id="view_row_constructor_'+el.value+'"  style="pointer-events: all;right: 29%;bottom: 43%;"  ><i class="fa fa-pencil-square-o" ></i> Edit</a>')
			// $(el).append(`<div class="tooltip_dashboard" style="pointer-events:all">
			// 								<i class="fa fa-eye search_icon" aria-hidden="true" ></i>
			// 								<span class="tooltiptext_dashboard display_text" id="display_text_${el.value}">It's Blank</span>
			// 							</div>
			//
			// 							`
			// 						)
		}
		// $(el).append('<i class="fa fa-ellipsis-v drag-header-more dots_'+this.clone_id+'" aria-hidden="true" id="three_dots"></i>');
		el.setAttribute('value', this.clone_id);
		// $(el).append('<p>wefoienfonweof</p>');
		$(el).addClass('style_tools');
		// $("#"+el.id).addClass('done');
	}
});

// END: FUNCTION TO ADD DYNAMIC ID'S TO COPIED ELEMENTS



dragula([document.getElementById('format_container'), document.getElementById('final_container')],

	 {
	  copy: function (el, source) {
	    return source === document.getElementById('final_container')
	  },
		copySortSource: true,
	  accepts: function (el, target) {

			return target !== document.getElementById('format_container')
	  }
	}).on('cloned', function(clone, original, type) {


	if (type == 'copy') {

		dragula.setCloneId(clone);

		if(clone.type === "text_editor"){

							//START: FUNCTION EXECUTES ONLY ONCE FOR EACH ELEMENT WHERE DYNAMIC MODAL CONTENT WILL BE APPENED WITH RICHTEXT
								$(document).one('click','#edit_view_'+clone.value, function (e) {

									if (e.target !== this){
										return;
									} else if (e.target === this) {
												// executes only once
												var html = `<div id="DYN-${clone.id}"  title="Rich Text Editor" style="display:none;">
																		<span class="ui-state-default"><span class="ui-icon ui-icon-info" style="float:left; margin:0 7px 0 0;"></span></span>
																		<div style="margin-left: 23px;" class="modal_box">
																		<input class="content" name="example" id="TEXT-${clone.id}">
																		<input value="generating" class="" name="example" hidden id="INPUT-${clone.id}">
																		 </div>
																		</div>`;
													$(".modal_section").append(html);
													$('#TEXT-'+clone.id).richText();
									}
									});
						//END: FUNCTION EXECUTES ONLY ONCE FOR EACH ELEMENT WHERE DYNAMIC MODAL CONTENT WILL BE APPENED WITH RICHTEXT


							$(document).on('click','#edit_view_'+clone.value,function(e){
									console.log(clone.id)
										if (e.target !== this){
											return;
										}
										// console.log("gegrerg"+clone.id)
										openModal(this,"DYN-"+clone.id,"TEXT-"+clone.id,clone.id,clone.value);
							});


			}

			//START: row constructor functionlity
			else if(clone.type === "row_constructor"){

				//START: FUNCTION EXECUTES ONLY ONCE FOR EACH ELEMENT WHERE DYNAMIC MODAL CONTENT WILL BE APPENED WITH RICHTEXT
					$(document).one('click','#view_row_constructor_'+clone.value, function (e) {

									if (e.target !== this){
										return;
									}
								//
								// // executes only once
								var html = `<div id="row-constructor-${clone.id}"  title="ROW CONSTRUCTOR" style="display:none;">
														<span class="ui-state-default"><span class="ui-icon ui-icon-info" style="float:left; margin:0 7px 0 0;"></span></span>
														<div class="row" style="margin-left: 23px;" class="modal_box">
															<div class="col-md-6">
																<select class="change_columns_${clone.id} form-control" name="change_columns" onchange="displayColumns('change_columns_${clone.id}','${clone.id}')">
																	<option value="">CHOOSE COLUMNS</option>
																	<option value="two_columns">TWO COLUMNS</option>
																	<option value="three_columns">THREE COLUMNS</option>
																</select>
																<div class="row two_columns_${clone.id}">
																	<div class="col-md-6 ">
																			<div class="two_target_options_1_${clone.id}">

																			</div>
																			<div>

																			</div>
																	</div>
																	<div class="col-md-6 ">
																			<div class="two_target_options_2_${clone.id}">

																			</div>
																			<div>

																			</div>
																	</div>
																</div>
																<div class="row three_columns_${clone.id}">
																	<div class="col-md-4 ">
																		<div class="three_target_options_1_${clone.id}">

																		</div>
																		<div>

																		</div>
																	</div>
																	<div class="col-md-4">
																			<div class="three_target_options_2_${clone.id}">

																			</div>
																			<div>

																			</div>
																	</div>
																	<div class="col-md-4">
																			<div class="three_target_options_3_${clone.id}">

																			</div>
																			<div>

																			</div>
																	</div>
																</div>
															</div>
														</div>
												</div>`;


										$(".modal_section_row").append(html);
										// $('#TEXT-'+clone.id).richText();
					});
					//END: FUNCTION EXECUTES ONLY ONCE FOR EACH ELEMENT WHERE DYNAMIC MODAL CONTENT WILL BE APPENED WITH RICHTEXT


					//ONCLICK OF RICHTEXT MODAL WILL OPEN
					$(document).on('click','#view_row_constructor_'+clone.value,function(e){

						//START: BELOW CODE WILL PREVENT OPENING OF MODAL ONCLICK OF CROSSMARK ICON
						if (e.target !== this){
							return;
						}
						//END: BELOW CODE WILL PREVENT OPENING OF MODAL ONCLICK OF CROSSMARK ICON
						openRowModal(this,"row-constructor-"+clone.id,clone.id);
					})

			}
			//END: row constructor functionlity

		// $('.hello').on('click',function(){
		// 	alert("hi");
		// })

		$(".cross_mark_icon_style_tools").on('click', function(e) {
			 // Do something
			 // e.stopPropagation();
			 $(this).parent('li').remove();
		});
	}
})


function openModal(ele,id,text_id,clone_id,parent_value) {

	$("#"+id).dialog({
    modal: true,
    draggable: false,
    resizable: false,
    position: ['center', 'top'],
    show: 'blind',
    hide: 'blind',
    width: 400,
    dialogClass: 'ui-dialog-osx',
    buttons: {
        "SAVE TEXT": function() {
            // $(this).dialog("close");
						// console.log(text_id);
						var str = $('#'+text_id).val();
						$("#display_text_"+parent_value).html(str)
						test_tools_obj[clone_id]={};
						test_tools_obj[clone_id].modal_id     = id;
						test_tools_obj[clone_id].value        = str;
						test_tools_obj[clone_id].parent_value = parent_value;
						console.log(test_tools_obj)
						$(this).dialog("close");
        }
    }
});
}


//START: FUNCTION TO OPEN ROW CONSTRUCTOR MODAL
function openRowModal(ele,id,dynamic_value,parent_value,update_view) {
	// console.log(dynamic_value);
	if(update_view){
		displayUpdatedColumns("change_columns_"+dynamic_value,dynamic_value)
		// DisplayFeatureOptions()
	}
	$("#"+id).dialog({
    modal: true,
    draggable: false,
    resizable: false,
    position: ['center', 'top'],
    show: 'blind',
    hide: 'blind',
    width: 400,
    dialogClass: 'ui-dialog-osx',
    buttons: {
        "SAVE TEXT": function() {
						if($('.change_columns_'+dynamic_value).val()==="two_columns"){
								row_constructor_object['row_'+id]={};
								row_constructor_object['row_'+id].col_1={};
								row_constructor_object['row_'+id].col_2={};
								// row_constructor_object.id['block'] = $('.endpoints_t1').val()
								row_constructor_object['row_'+id].columns = 2;
								row_constructor_object['row_'+id]['col_1'].block = $('.blocks_t1_'+dynamic_value).val()
								row_constructor_object['row_'+id]['col_1'].image = $('.image_link_t1_'+dynamic_value).val()
								row_constructor_object['row_'+id]['col_1'].text = $('.text_area_t1_'+dynamic_value).val()
								// row_constructor_object['row_1']['col_1'].blank = $('.text_area_t1').val()


								row_constructor_object['row_'+id]['col_2'].block = $('.blocks_t2_'+dynamic_value).val()
								row_constructor_object['row_'+id]['col_2'].image = $('.image_link_t2_'+dynamic_value).val()
								row_constructor_object['row_'+id]['col_2'].text = $('.text_area_t2_'+dynamic_value).val()
								// row_constructor_object['row_1']['col_2'].blank = $('.text_area_t2').val()
								// console.log(row_constructor_object);
						}
						else if($('.change_columns_'+dynamic_value).val()==="three_columns"){
								row_constructor_object['row_'+id]={};
								row_constructor_object['row_'+id].col_1={};
								row_constructor_object['row_'+id].col_2={};
								row_constructor_object['row_'+id].col_3={};
								// row_constructor_object.id['block'] = $('.endpoints_t1').val()
								row_constructor_object['row_'+id].columns = 3;
								row_constructor_object['row_'+id]['col_1'].block = $('.blocks_th1_'+dynamic_value).val()
								row_constructor_object['row_'+id]['col_1'].image = $('.image_link_th1_'+dynamic_value).val()
								row_constructor_object['row_'+id]['col_1'].text = $('.text_area_th1_'+dynamic_value).val()
								// row_constructor_object['row_1']['col_1'].blank = $('.text_area_t1').val()


								row_constructor_object['row_'+id]['col_2'].block = $('.blocks_th2_'+dynamic_value).val()
								row_constructor_object['row_'+id]['col_2'].image = $('.image_link_th2_'+dynamic_value).val()
								row_constructor_object['row_'+id]['col_2'].text = $('.text_area_th2_'+dynamic_value).val()
								// row_constructor_object['row_1']['col_2'].blank = $('.text_area_t1').val()

								// console.log(row_constructor_object)
								// alert($('.blocks_th3').val())
								row_constructor_object['row_'+id]['col_3'].block = $('.blocks_th3_'+dynamic_value).val()
   							    row_constructor_object['row_'+id]['col_3'].image = $('.image_link_th3_'+dynamic_value).val()
								row_constructor_object['row_'+id]['col_3'].text = $('.text_area_th3_'+dynamic_value).val()
									// row_constructor_object['row_1']['col_2'].blank = $('.text_area_t1').val()
						}
			$(this).dialog("close");
       }
    }
});
}
//END: FUNCTION TO OPEN ROW CONSTRUCTOR MODAL




// FINAL SUBMISSION FUNCTION
var final_updated_object = {};


function finalSubmit() {
let dashboard_elements = document.getElementById('final_container').children;
// console.log(row_constructor_object)
// document.getElementById('loader').style.display="block";
document.querySelector('.loading-overlay').style.display = "block"
for(var i=0;i< dashboard_elements.length;i++){

	let test = document.getElementById(dashboard_elements[i].id).type;

	final_updated_object['ele'+i]={};
	final_updated_object['ele'+i].id = dashboard_elements[i].id;
	final_updated_object['ele'+i].name = dashboard_elements[i].innerText;
	final_updated_object['ele'+i].type = dashboard_elements[i].type;
	final_updated_object['ele'+i].rich_text = test_tools_obj;
	if(final_updated_object['ele'+i].type ==="row_constructor"){
		final_updated_object['ele'+i].row_constructor_object = row_constructor_object;
	}
}

console.log(final_updated_object)
$('#dashboard_format_id').val(JSON.stringify(final_updated_object));
// alert("vale"+$('#dashboard_format_id').val())
$('#dashboard_form_id').submit();
}



// START: Code to remove arranged elements in final container

function removeEndpointListItems() {
	$("input:checked").next('.endpoints_tool').remove()
	$("input:checked").parent('.endpoints').removeClass('done')
	$("input:checked").parent('.endpoints').removeClass('remove_class')
	$('#endpoint_container').append($("input:checked").parent('.endpoints'))
	$(".endpoint_checkbox:checked").remove()
}


function removeFormatingTools() {
	$(".formatting_tools:checked").parent('.rich_text_box').remove();
	$(".formatting_tools:checked").parent('.line_spacer_box').remove()
}

function removeArrangedElements(){

	if($("input:checked").parent('li').attr('type') === "end_point"){
			removeEndpointListItems()
			if($("input:checked").parent('li').attr('type') === "text_editor") {
				$(".formatting_tools:checked").parent('.rich_text_box').remove();
			}
			// continue;
	} else if($("input:checked").parent('li').attr('type') === "text_editor") {
		removeFormatingTools()

		if($("input:checked").parent('li').attr('type') === "end_point"){
			removeEndpointListItems()
		}
	}
	else if($("input:checked").parent('li').attr('type') === "spacer") {
		removeFormatingTools();

		if($("input:checked").parent('li').attr('type') === "end_point"){
			removeEndpointListItems()
		}


	}
	// $("input:checked").parent().remove();
}
// END: Code to remove arranged elements in final container





var isShowTwoColumns=true;
var isShowThreeColumns=true;

function displayColumns(dynamic_value_option,id) {
	// alert(dynamic_value_option)
	var select_target_options;
	select_target_options = `
		<select class="selected_target_values form-control" id="endpoint_options_id_${id}" name="gerg" onchange="DisplayFeatureOptions(this,'${id}')">
			<option value=""></option>
			<option value="endpoint">Endpoint</option>
			<option value="block">Block</option>
			<option value="image">Image</option>
			<option value="text">Text</option>
			<option value="blank">Blank</option>
		</select>
	`;
	

	if($('.'+dynamic_value_option).val()==="two_columns"){

		$('.two_columns_'+id).show()
		$('.three_target_options_1_'+id).children().remove();
		$('.three_target_options_2_'+id).children().remove();
		$('.three_target_options_3_'+id).children().remove();
		// $('.three_target_options').children().remove()

		// if(isShowTwoColumns) {

			
			$('.two_target_options_1_'+id).append(select_target_options)
			// $('#target_options_children').html(select_target_options)
			// $('.two_target_options_1').children().addClass('t1')
			$('.two_target_options_1_'+id).children().addClass('t1_'+id)
			$('.two_target_options_1_'+id).next().addClass('display_features_select_option_t1_'+id)




			$('.two_target_options_2_'+id).append(select_target_options)
			$('.two_target_options_2_'+id).children().addClass('t2_'+id)
			$('.two_target_options_2_'+id).next().addClass('display_features_select_option_t2_'+id)
			// isShowTwoColumns=false;
		// }


		$('.three_columns_'+id).hide()

	} else if($('.'+dynamic_value_option).val()==="three_columns") {
		//
		$('.three_columns_'+id).show()
		// $('.two_target_options').children().remove()
		$('.two_target_options_1_'+id).children().remove();
		$('.two_target_options_2_'+id).children().remove();

		// if(isShowThreeColumns){
			$('.three_target_options_1_'+id).append(select_target_options)
			$('.three_target_options_1_'+id).children().addClass('th1_'+id)
			$('.three_target_options_1_'+id).next().addClass('display_features_select_option_th1_'+id)

			// $('.three_target_options_1').children().addClass('th1')

			$('.three_target_options_2_'+id).append(select_target_options)
			$('.three_target_options_2_'+id).children().addClass('th2_'+id)
			$('.three_target_options_2_'+id).next().addClass('display_features_select_option_th2_'+id)
			// $('.three_target_options_2').children().addClass('th2')

			$('.three_target_options_3_'+id).append(select_target_options)
			$('.three_target_options_3_'+id).children().addClass('th3_'+id)
			$('.three_target_options_3_'+id).next().addClass('display_features_select_option_th3_'+id)
			// $('.three_target_options_3').children().addClass('th3')
			isShowThreeColumns = false;
		// }


			$('.two_columns_'+id).hide()
	}

}






// START: function to display target options such as endpoints, block,blank.etc
function DisplayFeatureOptions(ele,id) {
	// document.getElementById("target_option_children").innerHTML = "Loading";
	// document.getElementById("target_option_children").innerHTML = "";

	var cool_class = ele.className.split(" ")[2];
	// alert(cool_class)
	//matching the values with the selected target values
	if($('.'+cool_class).val()==="endpoint"){
		removeSelectedOptions()
			var endpoints_dict = {}
			let endpoint_elements = document.getElementById('endpoint_container').children;

			for(i=0;i<endpoint_elements.length;i++) {
				// endpoints_array.push(endpoint_elements[i].innerText.split('VIEW').join(""))
				var k = endpoint_elements[i].innerText.split('VIEW').join("")
				var v = endpoint_elements[i].id;
				endpoints_dict[k] = v;
			}

			var display_selected_endpoint_option = `
					<select class="endpoints_${cool_class} form-control" name="selected_endpoints_${cool_class}" >
							${Object.entries(endpoints_dict).map(([k,v],i)=>{
								return 	"<option value="+v+">" +k+ "</option>"
							})}

					</select>
				`;
				
				$('.display_features_select_option_'+cool_class).append(display_selected_endpoint_option)
				// $('#target_options_children').append(display_selected_endpoint_option)
		}
		else if($('.'+cool_class).val()==="block") {

			removeSelectedOptions()
			var display_selected_block_option = `
				<select class="blocks_${cool_class} form-control" name="selected_endpoints_${cool_class}" >
						${Object.entries(endpoints_coloumn_data).map(([k,v],i)=>{
							return 	"<option value="+k+">" +v+ "</option>"
						})}

				</select>
			`;
			
			$('.display_features_select_option_'+cool_class).append(display_selected_block_option)
			$('.blocks_'+cool_class).val(`${100},no__of_probable_cases,max`)
		}
		else if($('.'+cool_class).val()==="image"){
				removeSelectedOptions()
				var image_link = `<input type="text" class="image_link_${cool_class} form-control"  placeholder="image URL" value="" />`
				// $('.'+cool_class).parent().append(image_link)
				// $('#target_options_children').append(image_link)
				$('.display_features_select_option_'+cool_class).append(image_link)
		}
		else if($('.'+cool_class).val()==="text"){
			removeSelectedOptions()
			var selected_text_area = `
				<Textarea class="text_area_${cool_class} form-control" name="selected_text_area_${cool_class}" maxlength="140">


				</Textarea>
			`;
			// $('#target_options_children').append(selected_text_area)
			// $('.'+cool_class).parent().append(selected_text_area)
			$('.display_features_select_option_'+cool_class).append(selected_text_area)
		}
		else if($('.'+cool_class).val()==="blank"){
			removeSelectedOptions()
		}


		function removeSelectedOptions() {
			$(".endpoints_"+cool_class).remove()
			$(".blocks_"+cool_class).remove()
			$(".text_area_"+cool_class).remove()
			$(".blank_area_"+cool_class).remove()
			$(".image_link_"+cool_class).remove()
		}


}

// END: function to display target options such as endpoints, block,blank.etc




// START: Update display Feature

const DisplayUpdatedFeature = (cool_class,featured_value) => {

	
	if($('.'+cool_class).val()==="endpoint"){
		removeSelectedOptions()
			var endpoints_dict = {}
			let endpoint_elements = document.getElementById('endpoint_container').children;

			for(i=0;i<endpoint_elements.length;i++) {
				// endpoints_array.push(endpoint_elements[i].innerText.split('VIEW').join(""))
				var k = endpoint_elements[i].innerText.split('VIEW').join("")
				var v = endpoint_elements[i].id;
				endpoints_dict[k] = v;
			}

			var display_selected_endpoint_option = `
					<select class="endpoints_${cool_class} form-control" name="selected_endpoints_${cool_class}" >
							${Object.entries(endpoints_dict).map(([k,v],i)=>{
								return 	"<option value="+v+">" +k+ "</option>"
							})}

					</select>
				`;
				
				$('.display_features_select_option_'+cool_class).append(display_selected_endpoint_option)
				// $('#target_options_children').append(display_selected_endpoint_option)
		}
		else if($('.'+cool_class).val()==="block") {
			// alert("hi")
			removeSelectedOptions()
			var display_selected_block_option = `
				<select class="blocks_${cool_class} form-control" name="selected_endpoints_${cool_class}" >
						${Object.entries(endpoints_coloumn_data).map(([k,v],i)=>{
							return 	"<option value="+k+">" +v+ "</option>"
						})}

				</select>
			`;
			
			$('.display_features_select_option_'+cool_class).append(display_selected_block_option)
			var number          = Number(featured_value.split(',')[0]);
			var functions       = featured_value.split(',')[1];
			var functions_value = featured_value.split(',')[2];

			$('.blocks_'+cool_class).val(`${number},${functions},${functions_value}`)
		}
		else if($('.'+cool_class).val()==="image"){
				removeSelectedOptions()
				var image_link = `<input type="text" class="image_link_${cool_class} form-control"  placeholder="image URL" value="" />`
				// $('.'+cool_class).parent().append(image_link)
				// $('#target_options_children').append(image_link)
				$('.display_features_select_option_'+cool_class).append(image_link)
				$('.image_link_'+cool_class).val(`${featured_value}`)
		}
		else if($('.'+cool_class).val()==="text"){
			removeSelectedOptions()
			var selected_text_area = `
				<Textarea class="text_area_${cool_class} form-control" name="selected_text_area_${cool_class}" maxlength="140">


				</Textarea>
			`;
			// $('#target_options_children').append(selected_text_area)
			// $('.'+cool_class).parent().append(selected_text_area)
			$('.display_features_select_option_'+cool_class).append(selected_text_area)
			$('.text_area_'+cool_class).val(`${featured_value}`)
		}
		else if($('.'+cool_class).val()==="blank"){
			removeSelectedOptions()
		}


		function removeSelectedOptions() {
			$(".endpoints_"+cool_class).remove()
			$(".blocks_"+cool_class).remove()
			$(".text_area_"+cool_class).remove()
			$(".blank_area_"+cool_class).remove()
			$(".image_link_"+cool_class).remove()
		}
}

// END: Update display Feature




// START : Update Display Columns


var isUpdatedTwoColumns=true;
var isUpdatedThreeColumns=true;

const displayUpdatedColumns  = (dynamic_value_option,id)=> {


	// alert(dynamic_value_option)
	var select_target_options;
	select_target_options = `
		<select class="selected_target_values form-control" id="endpoint_options_id_${id}" name="gerg" onchange="DisplayFeatureOptions(this,'${id}')">
			<option value=""></option>
			<option value="endpoint">Endpoint</option>
			<option value="block">Block</option>
			<option value="image">Image</option>
			<option value="text">Text</option>
			<option value="blank">Blank</option>
		</select>


	`;
	

	if($('.'+dynamic_value_option).val()==="two_columns"){
		var featured_value;
		$('.two_columns_'+id).show()
		// $('.three_target_options').children().remove()

		if(isUpdatedTwoColumns) {
			var final_updated_object = JSON.parse(updated_object);
			selectTwoColumnsColOne(id)	
			selectTwoColumnsColTwo(id)
		}


		$('.three_columns_'+id).hide()

	} else if($('.'+dynamic_value_option).val()==="three_columns") {
		//
		$('.three_columns_'+id).show()
		// $('.two_target_options').children().remove()

		if(isUpdatedThreeColumns){
			selectThreeColumnsColOne(id)
			selectThreeColumnsColTwo(id)
			selectThreeColumnsColThree(id)
		}


		$('.two_columns_'+id).hide()
	}

}

// END : Update Display Columns


const selectTwoColumnsColOne = (id)=>{
var final_updated_object = JSON.parse(updated_object);
var featured_value;

for (var key in final_updated_object) {
	if (final_updated_object.hasOwnProperty(key)) {
			for (var k in final_updated_object[key].row_constructor_object) {
				// if (final_updated_object[key].row_constructor_object.hasOwnProperty(k)) {
					console.log(k + " -> " + final_updated_object[key].row_constructor_object[k].col_1);
				// }

				for (var value in final_updated_object[key].row_constructor_object[k].col_1){
					
					

					if(value === "block"){
						featured_value = final_updated_object[key].row_constructor_object[k].col_1[value];
						select_target_options = `
							<select class="selected_target_values form-control" id="endpoint_options_id_${id}" name="gerg" onchange="DisplayFeatureOptions(this,'${id}')">
								<option value=""></option>
								<option value="endpoint">Endpoint</option>
								<option value="block" selected>Block</option>
								<option value="image">Image</option>
								<option value="text">Text</option>
								<option value="blank">Blank</option>
							</select>
							
						`;	
					}
					else if(value === "text"){
								featured_value = final_updated_object[key].row_constructor_object[k].col_1[value];
								featured_value = featured_value.replace('\t','');
								featured_value = featured_value.replace('\n','');
								featured_value = featured_value.replace('\n','');
								console.log(featured_value)
							select_target_options = `
								<select class="selected_target_values form-control" id="endpoint_options_id_${id}" name="gerg" onchange="DisplayFeatureOptions(this,'${id}')">
									<option value=""></option>
									<option value="endpoint">Endpoint</option>
									<option value="block" >Block</option>
									<option value="image">Image</option>
									<option value="text" selected>Text</option>
									<option value="blank">Blank</option>
								</select>
								
							`;
							// DisplayUpdatedFeature('t2_'+id,featured_value)
						}
						else if(value === "image"){
							featured_value = final_updated_object[key].row_constructor_object[k].col_1[value];
							select_target_options = `
								<select class="selected_target_values form-control" id="endpoint_options_id_${id}" name="gerg" onchange="DisplayFeatureOptions(this,'${id}')">
									<option value=""></option>
									<option value="endpoint">Endpoint</option>
									<option value="block" >Block</option>
									<option value="image" selected>Image</option>
									<option value="text">Text</option>
									<option value="blank">Blank</option>
								</select>
								
							`;
							
						}
						else if(value === "blank"){
							select_target_options = `
								<select class="selected_target_values form-control" id="endpoint_options_id_${id}" name="gerg" onchange="DisplayFeatureOptions(this,'${id}')">
									<option value=""></option>
									<option value="endpoint">Endpoint</option>
									<option value="block" >Block</option>
									<option value="image" >Image</option>
									<option value="text">Text</option>
									<option value="blank" selected>Blank</option>
								</select>
								
							`;
							
						}	
				}	
			}
		}
	}
	$('.two_target_options_1_'+id).append(select_target_options)
	$('.two_target_options_1_'+id).children().addClass('t1_'+id)
	$('.two_target_options_1_'+id).next().addClass('display_features_select_option_t1_'+id)
	DisplayUpdatedFeature('t1_'+id,featured_value)
}


const selectTwoColumnsColTwo = (id)=>{
	var final_updated_object = JSON.parse(updated_object);
	var featured_value;

	for (var key in final_updated_object) {
		if (final_updated_object.hasOwnProperty(key)) {
				
				for (var k in final_updated_object[key].row_constructor_object) {

					// if (final_updated_object[key].row_constructor_object.hasOwnProperty(k)) {
						console.log(k + " -> " + final_updated_object[key].row_constructor_object[k].col_2);
					// }

					for (var value in final_updated_object[key].row_constructor_object[k].col_2){
						// console.log(select_target_options.val())

						if(value === "block"){
							featured_value = final_updated_object[key].row_constructor_object[k].col_2[value];
							select_target_options = `
								<select class="selected_target_values form-control" id="endpoint_options_id_${id}" name="gerg" onchange="DisplayFeatureOptions(this,'${id}')">
									<option value=""></option>
									<option value="endpoint">Endpoint</option>
									<option value="block" selected>Block</option>
									<option value="image">Image</option>
									<option value="text">Text</option>
									<option value="blank">Blank</option>
								</select>
								
							`;
							
						}
						else if(value === "text"){
								featured_value = final_updated_object[key].row_constructor_object[k].col_2[value];
								featured_value = featured_value.replace('\t','');
								featured_value = featured_value.replace('\n','');
								featured_value = featured_value.replace('\n','');
								console.log(featured_value)
							select_target_options = `
								<select class="selected_target_values form-control" id="endpoint_options_id_${id}" name="gerg" onchange="DisplayFeatureOptions(this,'${id}')">
									<option value=""></option>
									<option value="endpoint">Endpoint</option>
									<option value="block" >Block</option>
									<option value="image">Image</option>
									<option value="text" selected>Text</option>
									<option value="blank">Blank</option>
								</select>
								
							`;
							// DisplayUpdatedFeature('t2_'+id,featured_value)
						}
						else if(value === "image"){
							featured_value = final_updated_object[key].row_constructor_object[k].col_2[value];
							select_target_options = `
								<select class="selected_target_values form-control" id="endpoint_options_id_${id}" name="gerg" onchange="DisplayFeatureOptions(this,'${id}')">
									<option value=""></option>
									<option value="endpoint">Endpoint</option>
									<option value="block" >Block</option>
									<option value="image" selected>Image</option>
									<option value="text">Text</option>
									<option value="blank">Blank</option>
								</select>
								
							`;
							
						}
						else if(value === "blank"){
							select_target_options = `
								<select class="selected_target_values form-control" id="endpoint_options_id_${id}" name="gerg" onchange="DisplayFeatureOptions(this,'${id}')">
									<option value=""></option>
									<option value="endpoint">Endpoint</option>
									<option value="block" >Block</option>
									<option value="image" >Image</option>
									<option value="text">Text</option>
									<option value="blank" selected>Blank</option>
								</select>
								
							`;
							
						}

					}
					
				}
			}
	}	

	$('.two_target_options_2_'+id).append(select_target_options)
	$('.two_target_options_2_'+id).children().addClass('t2_'+id)
	$('.two_target_options_2_'+id).next().addClass('display_features_select_option_t2_'+id)
	DisplayUpdatedFeature('t2_'+id,featured_value)
	isUpdatedTwoColumns=false;
}


const selectThreeColumnsColOne = (id)=>{
	updateFeatures(id,1)
}

const selectThreeColumnsColTwo = (id)=>{
	updateFeatures(id,2)
}

const selectThreeColumnsColThree = (id)=>{
	updateFeatures(id,3)
}


const updateFeatures = (id,col_value)=>{
var final_updated_object = JSON.parse(updated_object);
let select_target_options;
let const_obj;
let featured_value;

const featureSelectedValues = ()=>{
		if(col_value === 1){
			featured_value = final_updated_object[key].row_constructor_object[k].col_1[value];				
		}
		else if(col_value === 2){
			featured_value = final_updated_object[key].row_constructor_object[k].col_2[value];
		}
		else if(col_value === 3){
			featured_value = final_updated_object[key].row_constructor_object[k].col_3[value];
		}
	}

	for (var key in final_updated_object) {
		if (final_updated_object.hasOwnProperty(key)) {
				
				for (var k in final_updated_object[key].row_constructor_object) {
					if(col_value === 1){
						const_obj = final_updated_object[key].row_constructor_object[k].col_1;
					}
					else if(col_value === 2){
						const_obj = final_updated_object[key].row_constructor_object[k].col_2;
					}
					else if(col_value === 3){
						const_obj = final_updated_object[key].row_constructor_object[k].col_3;
					}

					for (var value in const_obj){

						// featured_value = final_updated_object[key].row_constructor_object[k].col_1[value];
						if(value === "block"){
							featureSelectedValues()
							select_target_options = `
								<select class="selected_target_values form-control" id="endpoint_options_id_${id}" name="gerg" onchange="DisplayFeatureOptions(this,'${id}')">
									<option value=""></option>
									<option value="endpoint">Endpoint</option>
									<option value="block" selected>Block</option>
									<option value="image">Image</option>
									<option value="text">Text</option>
									<option value="blank">Blank</option>
								</select>
								
							`;
							
						}
						else if(value === "text"){
							featureSelectedValues()
							select_target_options = `
								<select class="selected_target_values form-control" id="endpoint_options_id_${id}" name="gerg" onchange="DisplayFeatureOptions(this,'${id}')">
									<option value=""></option>
									<option value="endpoint">Endpoint</option>
									<option value="block" >Block</option>
									<option value="image">Image</option>
									<option value="text" selected>Text</option>
									<option value="blank">Blank</option>
								</select>
								
							`;
						}
						else if(value === "image"){
							featureSelectedValues()
							select_target_options = `
								<select class="selected_target_values form-control" id="endpoint_options_id_${id}" name="gerg" onchange="DisplayFeatureOptions(this,'${id}')">
									<option value=""></option>
									<option value="endpoint">Endpoint</option>
									<option value="block" >Block</option>
									<option value="image" selected>Image</option>
									<option value="text" >Text</option>
									<option value="blank">Blank</option>
								</select>
								
							`;
						}
						else if(value === "blank"){
							featureSelectedValues()
							select_target_options = `
								<select class="selected_target_values form-control" id="endpoint_options_id_${id}" name="gerg" onchange="DisplayFeatureOptions(this,'${id}')">
									<option value=""></option>
									<option value="endpoint">Endpoint</option>
									<option value="block" >Block</option>
									<option value="image">Image</option>
									<option value="text">Text</option>
									<option value="blank" selected>Blank</option>
								</select>
								
							`;
						}			
					}
					
				}
			}
	}	

	$('.three_target_options_'+col_value+'_'+id).append(select_target_options)
	$('.three_target_options_'+col_value+'_'+id).children().addClass('th'+col_value+'_'+id)
	$('.three_target_options_'+col_value+'_'+id).next().addClass('display_features_select_option_th'+col_value+'_'+id)
	
	DisplayUpdatedFeature('th'+col_value+'_'+id,featured_value)
	isUpdatedThreeColumns=false;
}