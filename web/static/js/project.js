url = "http://127.0.0.1:8000"

function SubProject() {
    // 创建新项目
    $.ajax({
        url: url+"/project/list/",
        type: "POST",
        data: $("#addForm").serialize(),
        success: function (res) {
            if (res.status){
                location.href = location.href; //页面刷新
            }else{
                //错误信息
                $.each(res.error, function (key,value){
                    console.log(key, value[0]);
                    $('#id_' + key).next().text("* "+value[0]);
                })
            }
        }
    })
}

// function ARstar(num, pro_id) {
//     type = ["my","join","star"];
//     $.ajax({
//         url: url+"/project/star/"+type[num]+"/"+pro_id,
//         type: "GET",
//         success: function (res) {
//             if (res.status){
//                 location.reload();
//                 // location.href = location.href; //页面刷新
//             }
//         }
//     })
// }







