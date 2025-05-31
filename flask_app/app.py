import os
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

pintu_dir = os.path.join(os.path.dirname(__file__), '..')

@app.route('/')
def home():
    return render_template('index.html', title="主页", message="欢迎！")

@app.route('/hanzi_pic/<path:filename>')
def serve_file(filename):
    return send_from_directory(pintu_dir + '/data/hanzi_pic/', filename)


if __name__ == '__main__':
    app.run(debug=True, port=8000, host='0.0.0.0')
 
