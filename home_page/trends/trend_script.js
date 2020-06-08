//window.onload = function (){
//    var ul1 = document.getElementById('vtab');
//    var lis = ul1.getElementsByTagName('li');
//    var a_arr = new Array();
//
//    for(var i = 0; i < lis.length; i++){
//        a_arr[i] = lis[i].getElementsByTagName('a')[0];
//        var inside_str = a_arr[i].innerText;
//        var title = inside_str.split(':')[0];
//        var content = inside_str.split(':')[1];
//
//        var ptitle = document.createElement("p");
//        ptitle.setAttribute('style', 'font-size:15px; margin: 0; padding: 0;')
//        ptitle.innerText = title;
//        var pcontent = document.createElement("p");
//        pcontent.innerText = content;
//        a_arr[i].onmouseover = function (){
//            a_arr[0].innerHTML='';
//            a_arr[0].appendChild(ptitle);
//            a_arr[0].appendChild(pcontent);
//        }
//        a_arr[i].onmouseout = function (){
//            a_arr[0].removeChild(ptitle);
//            a_arr[0].removeChild(pcontent);
//            a_arr[0].innerText=inside_str;
//        }
//    }
//};

function change(obj){
    var inside_str = obj.innerText;
    console.log(obj);

    var title = inside_str.split(':')[0];
    var content = inside_str.split(':')[1];

    var ptitle = document.createElement("a");
    ptitle.setAttribute('style', 'font-size:15px; margin: 0; padding: 0;')
    ptitle.innerText = title;
    var pcontent = document.createElement("a");
    pcontent.setAttribute('style', 'font-size:10px; margin: 0; padding: 0;')
    pcontent.innerText = content;
    var br1 = document.createElement("br");

    obj.innerHTML = '';
    obj.appendChild(ptitle);
    obj.appendChild(br1);
    obj.appendChild(pcontent);
}

function back(obj){
    var ps = obj.getElementsByTagName('a');
    var strs = ps[0].innerText + ': ' + ps[1].innerText;
    console.log(strs);
    obj.removeChild(ps[0]);
    obj.removeChild(ps[0]);
    obj.innerHTML = strs;
}

function clicked(obj){
    var cur_color = obj.style.backgroundColor;
    if(cur_color == '#5e6568'){
        obj.setAttribute('style', 'background-color: #242525;')
    }
    else{
        obj.setAttribute('style', 'background-color: #5e6568;')
    }
}
