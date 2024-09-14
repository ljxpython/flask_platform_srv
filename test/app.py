from flask import Flask, abort, make_response, redirect, request

app = Flask(__name__)


from flask import Flask, abort


@app.route("/")
def hello_itcast():
    # abort(404)
    return "hello itcast", 200


# 路由传递的参数默认当做string处理，这里指定int，尖括号中冒号后面的内容是动态的
@app.route("/user/<int:id>")
def hello_itcas1t(id):
    return "hello itcast %d" % id


@app.errorhandler(404)
def error(e):
    return "您请求的页面不存在了，请确认后再次访问！%s" % e


# 重定向redirect示例
@app.route("/itcase")
def hello_itcast_it():
    return redirect("http://www.itcast.cn")


@app.route("/cookie")
def set_cookie():
    resp = make_response("this is to set cookie")
    resp.set_cookie("username", "itcast")
    return resp


# 获取cookie
@app.route("/request")
def resp_cookie():
    resp = request.cookies.get("username")
    return resp


if __name__ == "__main__":
    app.run(debug=True)
