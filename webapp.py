from flask import Flask, jsonify, request, send_file
import os
from io import BytesIO
import PIL.Image
import numpy as np


APP_PORT = 5005
APP_HOST = "0.0.0.0"
IMG_FOLDER = 'imgs/'


class State:

    def __init__(self):
        self.files = os.listdir(IMG_FOLDER)
        self.pid = 1
        self._img = None
        self.img = self.files[0]

    @property
    def img(self):
        return self._img

    @img.setter
    def img(self, x):
        self._img = x
        self.pil = PIL.Image.open(os.path.join(IMG_FOLDER, self.img))
        self.grayscale_pil = self.pil.convert('LA')
        self.arr = np.array(self.grayscale_pil)

    def jsonify(self):
        return jsonify({"pid": self.pid,
                        "img": self.img,
                        "files": self.files})

    def get_results(self):
        if self.pid:
            pass
        return serve_pil(self.pil)
        thresh = 67
        if picture == 2:
            arr = np.array(self.pil)
            pil = PIL.Image.fromarray(((arr>67)*255).astype(np.uint8))
            return serve_pil(pil)
        return serve_pil(self.pil)


def serve_pil(pil):
    img_io = BytesIO()
    pil.save(img_io, "png")
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')


def serve_histrogram(arr):
    return 


state = State()
app = Flask(__name__)


@app.route("/")
def index():
    return app.send_static_file('board.html')


@app.route("/state", methods=['GET', 'POST'])
def get_state():
    if request.method == "POST":
        if "pid" in request.json:   
            state.pid = request.json['pid']
        if "img" in request.json:   
            state.img = request.json['img']
    return state.jsonify()


@app.route("/pic/<int:picture_id>")
def return_pic(picture_id):
    if picture_id == 1:
        return serve_pil(state.pil)
    if picture_id == 2:
        return serve_pil(state.grayscale_pil)
    return state.get_results()


@app.route("/project_pic")
def return_project_pic():
    return app.send_static_file('Project_%s.jpg' % state.pid)

if __name__ == "__main__":
    print("Run the webapp at http://<any address for your local host>:%s/" % APP_PORT)

    # IMPORTANT: `threaded=False` to ensure correct behavior
    app.run(port=APP_PORT, threaded=False, host=APP_HOST, debug=True)
