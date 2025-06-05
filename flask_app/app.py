import os

from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

pintu_dir = os.path.join(os.path.dirname(__file__), "..")


@app.route("/v1")
def home():
    return render_template("v1.html", title="主页", message="欢迎！")


@app.route("/v2")
def v2():
    return render_template("v2.html", title="主页", message="欢迎！")


@app.route("/zi")
def zi():
    return render_template("v2.html", title="主页", message="欢迎！")


@app.route("/shici")
def shici():
    return render_template("shici.html", title="主页", message="欢迎！")


@app.route("/hanzi_pic/<path:filename>")
def hanzi_pic(filename):
    return send_from_directory(pintu_dir + "/data/hanzi_pic/", filename)


@app.route("/hanzi_splited/<path:filename>")
def hanzi_splited(filename):
    return send_from_directory(pintu_dir + "/data/hanzi_splited/", filename)


@app.route("/shici_pic/<path:filename>")
def shici_pic(filename):
    return send_from_directory(pintu_dir + "/data/shici_pics/", filename)


@app.route("/shici_splited/<path:filename>")
def shici_splited(filename):
    return send_from_directory(pintu_dir + "/data/shici_splited/", filename)


@app.route("/shici_bg/<filename>")
def shici_bg(filename):
    return send_from_directory(pintu_dir + "/data/shici_bg/", filename)


@app.route("/hanzi_video/<filename>")
def hanzi_video(filename):
    return send_from_directory(pintu_dir + "/data/hanzi_video/", filename)


@app.route("/icons/<filename>")
def icon(filename):
    return send_from_directory(pintu_dir + "/data/icons/", filename)


@app.route("/data/<filename>")
def data(filename):
    return send_from_directory(pintu_dir + "/data/", filename)


if __name__ == "__main__":
    app.run(debug=True, port=8000, host="0.0.0.0")
