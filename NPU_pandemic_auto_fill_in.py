import sys
import requests
import json

# 网页url
yqtb_url = "http://yqtb.nwpu.edu.cn"
uis_login_url = "https://uis.nwpu.edu.cn/cas/login?service=http%3A%2F%2Fyqtb.nwpu.edu.cn%2F%2Fsso%2Flogin.jsp%3FtargetUrl%3Dbase64aHR0cDovL3lxdGIubndwdS5lZHUuY24vL3d4L3hnL3l6LW1vYmlsZS9pbmRleC5qc3A%3D"
yqtb_fillin_url = "http://yqtb.nwpu.edu.cn/wx/ry/ry_util.jsp"
yqtb_referer_url = "http://yqtb.nwpu.edu.cn/wx/ry/jrsb.jsp"

# 疫情填报的会话ID
yqtb_cookie = ""
# 指示是否成功
flag = True
# 指示是否成功发送填报数据并获取返回值
filled = False
# 服务器返回的状态信息
state = "1"
# 服务器返回的错误信息
error = ""

# 用户信息，通过参数读取
name = sys.argv[1]
studentId = sys.argv[2]
password = sys.argv[3]
webhook = sys.argv[4]

# 打印学生信息
print("西北工业大学 疫情自动填报Python脚本")
print("【免责声明】本脚本专为懒人准备，不代表校方观点。若出现填报失败、填报错误、被后台识别等，开发者不负任何责任。使用此脚本则表示你已阅读并同意以上免责声明。")
print("你的姓名：" + name)
print("你的学号：" + studentId)
print("你的密码：" + "***")

try:
    # 创建会话
    session = requests.Session()
    # 请求疫情填报页面
    response1 = session.get(yqtb_url)
    yqtb_cookie = session.cookies["JSESSIONID"] # 疫情填报的会话id
    uis_cookie = response1.cookies["SESSION"] # 登录翱翔门户的会话id
    print("会话ID：" + yqtb_cookie)
    # 登录翱翔门户post的数据
    loginData = {
        "username" : studentId,
        "password" : password,
        "currentMenu" : 1,
        "execution" : "e1s1",
        "_eventId" : "submit",
        "geolocation" : "",
        "submit" : "稍等片刻……"
    }
    # 登录翱翔门户所用的cookie
    loginHeader = {
        "Cookie" : "SESSION=" + uis_cookie
    }
    # 请求登录
    response2 = session.post(uis_login_url, data = loginData, headers = loginHeader)

    # 提交填报信息post的数据（神TM知道这些是啥）
    fillinData = {
        "sfczbcqca" : "",
        "czbcqcasjd" : "",
        "sfczbcfhyy" : "",
        "czbcfhyysjd" : "",
        "actionType" : "addRbxx",
        "userLoginId" : studentId,
        "userName" : name,
        "szcsbm" : 1,
        "szcsmc" : "在学校",
        "sfjt" : 0,
        "sfjtsm" : "",
        "sfjcry" : 0,
        "sfjcrysm" : "",
        "sfjcqz" : 0,
        "sfyzz" : 0,
        "sfqz" : 0,
        "ycqksm" : "",
        "glqk" : 0,
        "glksrq" : "",
        "gljsrq" : "",
        "tbly" : "sso",
        "glyy" : "",
        "qtqksm" : "",
        "sfjcqzsm" : "",
        "sfjkqk" : 0,
        "jkqksm" : "",
        "sfmtbg" : "",
        "userType" : 2,
        "qrlxzt" : ""
    }
    # 填报所需要的header
    fillinHeader = {
        "Host" : "yqtb.nwpu.edu.cn",
        "Proxy-Connection" : "keep-alive",
        "Accept" : "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With" : "XMLHttpRequest",
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
        "Content-Type" : "application/x-www-form-urlencoded",
        "Origin" : yqtb_url,
        "Referer" : yqtb_referer_url,
        "Accept-Encoding" : "gzip, deflate",
        "Accept-Language" : "zh-CN,zh;q=0.9,en;q=0.8",
        "Cookie" : "JSESSIONID=" + yqtb_cookie
    }
    # 提交填报信息
    response3 = session.post(yqtb_fillin_url, data = fillinData, headers = fillinHeader)
    message = response3.text.strip().replace("\n", "").replace("\r", "").replace("－", "-") # 草（请赏析草字的妙处，6分）
    dict = json.loads(message)
    filled = True
    state = dict["state"]
    if state != "1":
        flag = False
        error = dict["err-msg"]
except:
    flag = False # 设置状态为失败

# 打印信息
if flag:
    print("填报成功")
else:
    print("填报失败")
    if filled:
        print("错误码：" + str(state))
        print("错误信息：" + error)

# 发送钉钉通知
if len(webhook) != 0:
    message = "【疫情自动填报】"
    if flag:
        message += "填报成功"
    elif filled:
        message += "填报失败\n错误码：" + str(state) + "\n错误信息：" + error
    else:
        message += "填报失败"
    if filled and len(yqtb_cookie) != 0:
        message += "\n会话ID：" + yqtb_cookie
    # 要发送的数据
    data = {
        "msgtype" : "text",
        "text" : {
            "content" : message
        },
        "at" : {
            "isAtAll" : not flag
        }
    }
    response = requests.post(webhook, data = json.dumps(data), headers = {"Content-Type": "application/json"})