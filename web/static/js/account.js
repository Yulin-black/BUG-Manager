var url = "http://127.0.0.1:8000"
// 提交注册数据
function ClickSubmit(num) {
    var urlList=[
        '/register/',
        '/login_email/',
    ]
    console.log(urlList[num])

    $('.error-msg').empty();   //每次点击请空 提示 span 中的内容
    $.ajax({
        url : url+urlList[num],
        type : "POST",
        // $('#regFrom').serialize()  可以获取id对应表单中所有的数据包括 token
        data : $('#regFrom').serialize(),
        dataType : "JSON",
        success:function (res) {
            if (res.status){
                location.href = res.data;
            }else{
                //错误信息
                $.each(res.error, function (key,value){
                    console.log(key, value[0]);
                    $('#id_' + key).next().text("*"+value[0]);
                })
            }
        }
    });
}

// 获取验证码
function getCode(num) {

    var postType = [
        'register',
        'login',
        'retpasswd',
    ]
    // 获取邮箱
    // var email = document.getElementById("id_email").value;
    var email = $('#id_email').val();
    $('.error-msg').empty();   //每次点击请空 提示 span 中的内容
    // console.log(email);
    // 使用AJAX发送邮箱地址到服务器
    $.ajax({
        // 反向成功url = 'http://127.0.0.1:8000/send_email_info/'
        url : url+"/send_email_info/",
        type : "GET",
        data : {"email" : email, "tpl":postType[num]},
        dataType:"JSON",
        success:function (res) {
            // ajax 发送成功后，自动执行的函数
            // res 为后端返回的值
            if (res.status){
                sendEmailRemind();
            }else{
                //错误信息
                $.each(res.error, function (key,value){
                    console.log(key, value[0]);
                    $('#id_' + key).next().text("*"+value[0]);
                })
            }

        }
    });
}

// 重新发送 的倒计时
function sendEmailRemind() {
    var $sendEmail = $("#sendEmail");
    $sendEmail.prop('disabled',true);
    var time = 6;
    var remid = setInterval(function () {
        $sendEmail.val(time+"后重新发送");
        time = time - 1 ;
        if (time < 0){
            clearInterval(remid);   // 取消定时器
            $sendEmail.val("点击获取验证码").prop("disabled", false)
        }
    },1000)
}


