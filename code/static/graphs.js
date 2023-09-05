setInterval(function (){
    var svg_object = document.querySelector('object');
    var svg_document = svg_object.contentDocument;

    var water_level0 = svg_document.getElementById("water_level0")
    var water_level0_text = svg_document.getElementById("water_level_text0");
    water_level0.setAttribute("height", rw_water_level);
    water_level0.setAttribute("y", 225 - rw_water_level);
    water_level0_text.textContent = rw_water_level + 'L';

    var water_level1 = svg_document.getElementById("water_level1")
    var water_level1_text = svg_document.getElementById("water_level_text1");
    water_level1.setAttribute("height", 2 * filter_water_level);
    water_level1.setAttribute("y", 250 - 2 * filter_water_level);
    water_level1_text.textContent = filter_water_level+ 'L';

    var water_level2 = svg_document.getElementById("water_level2")
    var water_level2_text = svg_document.getElementById("water_level_text2");
    water_level2.setAttribute("height", 2 * dis_water_level);
    water_level2.setAttribute("y", 250 - 2 * dis_water_level);
    water_level2_text.textContent = dis_water_level + 'L';

    var water_level3 = svg_document.getElementById("water_level3")
    var water_level3_text = svg_document.getElementById("water_level_text3");
    water_level3.setAttribute("height", st_water_level);
    water_level3.setAttribute("y", 225 - st_water_level);
    water_level3_text.textContent = st_water_level + 'L';

}, 1000);
