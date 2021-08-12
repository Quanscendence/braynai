var dashboard_obj={};
var tools_obj={};
var test_tools_obj={};

//GETTING AND PARSING THE OBJECT RECIEVED FROM BACKEND
var updated_object = document.getElementById('dashboard_format_id').value;
var final_updated_object = JSON.parse(updated_object);

console.log(final_updated_object)

// BELOW CODE IS USED TO STORE RICH TEXT VALUES IN AN OBJECT
for (var key in final_updated_object) {
	if (final_updated_object.hasOwnProperty(key)) {
			// console.log(key + " -> " + JSON.stringify(final_updated_object[key].rich_text));
			test_tools_obj = final_updated_object[key].rich_text;
		}

}



let dashboard_elements = document.getElementById('final_container').children;


// LOOPING THROUGH ALREADY PRESENT ELEMENTS IN FINAL CONTAINER
for(var i=0;i< dashboard_elements.length;i++){
	$('.view_endpoint_text').css('pointer-events','all');


	if(dashboard_elements[i].type === "text_editor"){


		// console.log(dashboard_elements[i])
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

		if(clone.type !== "spacer"){



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

// FINAL SUBMISSION FUNCTION
var final_updated_object = {};


function finalSubmit() {
let dashboard_elements = document.getElementById('final_container').children;

// document.getElementById('loader').style.display="block";
document.querySelector('.loading-overlay').style.display = "block"
for(var i=0;i< dashboard_elements.length;i++){

	let test = document.getElementById(dashboard_elements[i].id).type;

	final_updated_object['ele'+i]={};
	final_updated_object['ele'+i].id = dashboard_elements[i].id;
	final_updated_object['ele'+i].name = dashboard_elements[i].innerText;
	final_updated_object['ele'+i].type = dashboard_elements[i].type;
	final_updated_object['ele'+i].rich_text = test_tools_obj;
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
