from flask import Flask, jsonify, request, send_file
import os
from io import BytesIO
import PIL.Image
import numpy as np

import matplotlib as mpl
mpl.use('Agg')

import matplotlib.pyplot as plt
from skimage.filters import threshold_otsu, threshold_li
from skimage.filters import roberts, sobel, prewitt
from skimage.filters import gaussian, median
from skimage.morphology import disk
from skimage.morphology import erosion, dilation, opening, closing
from skimage.morphology import medial_axis, skeletonize


APP_PORT = 5005
APP_HOST = "0.0.0.0"
IMG_FOLDER = 'imgs/'


class State:

    def __init__(self):
        self.files = [f for f in os.listdir(IMG_FOLDER) if (f.endswith(".png")
                     or f.endswith(".jpg") or f.endswith(".jpeg"))]
        self.pid = 1
        self._img = None
        self._option_value = None
        self.img = self.files[0]
        self.clear_choice()
        self.clear_option()

    @property
    def img(self):
        return self._img

    @img.setter
    def img(self, x):
        self._img = x
        self.pil = PIL.Image.open(os.path.join(IMG_FOLDER, self.img))
        self.grayscale_pil = self.pil.convert('L')
        self.hist = self.grayscale_pil.histogram()
        h, w = self.pil.size
        self.size_ratio = w / h

    def jsonify(self):
        return jsonify({"pid": self.pid,
                        "img": self.img,
                        "files": self.files,
                        "choices": self.choices,
                        "choice": self.choice,
                        "inputVisible": self.input_visible,
                        "optionValue": self.option_value})

    def clear_choice(self):
        self.choice = self.choices[0]

    def clear_option(self):
        self.option_value = None

    @property
    def option_value(self):
        return self._option_value

    @option_value.setter
    def option_value(self, x):
        '''
        Input handler. If illegal, return `pid`-specific option value. 
        '''
        illegal = True
        if self.pid == 1:
            try:
                v = int(x)
                if 0 <= v <= 255:
                    self._option_value = v
                    illegal = False
            except:
                pass
            if illegal:
                self._option_value = 67
                illegal = False
        if self.pid == 2:
            try:
                v = float(x)
                if self.choice == "NR:med":
                    v = max(1, int(v))
                else:
                    v = max(0.1, v)
                self._option_value = v
                illegal = False
            except:
                pass
            if illegal:
                self._option_value = 3
                illegal = False
        if self.pid == 3:
            try:
                v = int(x)
                self._option_value = max(1, v)
                illegal = False
            except:
                pass
            if illegal:
                self._option_value = 3
                illegal = False
        if illegal:
            self._option_value = None

    @property
    def choices(self):
        '''
        The option choices for each `pid`.
        '''
        if self.pid == 1:
            return ["ostu", "entropy", "manual"]
        if self.pid == 2:
            return ["ED:Rob", "ED:Prew", "ED:Sob", "NR:gaus", "NR:med"]
        if self.pid == 3:
            return ["dilation", 'erosion', 'opening', 'closing']
        if self.pid == 4:
            return ["distance/ostu", 'skeleton/ostu']
        return []

    @property
    def input_visible(self):
        '''
        The visiability on the page for input option value.
        '''
        if self.pid == 1 and (self.choice == "manual"):
            return True
        if self.pid == 2 and (self.choice in ["NR:gaus", "NR:med"]):
            return True
        if self.pid == 3:
            return True
        return False

    def get_result(self):
        '''
        The resulting image for each project (Picture 4 on the page). 
        '''
        arr = np.array(self.grayscale_pil)
        if self.pid == 1:
            if self.choice == 'ostu':
                self.option_value = threshold_otsu(arr)
            elif self.choice == 'entropy':
                self.option_value = threshold_li(arr)
            else:
                pass
            result_arr = (arr > self.option_value)*255
        elif self.pid == 2:
            if self.choice == 'ED:Rob':
                result_arr = (1-roberts(arr))*255.
            elif self.choice == 'ED:Prew':
                result_arr = (1-prewitt(arr))*255.
            elif self.choice == 'ED:Sob':
                result_arr = (1-sobel(arr))*255.
            elif self.choice == 'NR:gaus':
                result_arr = gaussian(arr, sigma=self.option_value)*255.
            elif self.choice == 'NR:med':
                result_arr = median(arr, disk(self.option_value))
            else:
                pass
        elif self.pid == 3:
            fn_dict = {"dilation": dilation, "erosion": erosion, "opening": opening,"closing": closing}
            fn = fn_dict[self.choice]
            result_arr = fn(arr, disk(self.option_value))
        elif self.pid == 4:
            thresh = threshold_otsu(arr)
            binary_arr = arr > thresh
            if self.choice == "distance/ostu":
                skel, distance = medial_axis(binary_arr, return_distance=True)
                max_distance = np.max(distance)
                min_distance = np.min(distance)
                result_arr = (distance-min_distance)/(max_distance-min_distance)*255.
            if self.choice == 'skeleton/ostu':
                skel = skeletonize(binary_arr)
                result_arr = skel*255.
        else:
            result_arr = arr
            
        result_pil = PIL.Image.fromarray((result_arr).astype(np.uint8))
        return serve_pil(result_pil)


def serve_pil(pil):
    img_io = BytesIO()
    pil.save(img_io, "png")
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')


def serve_histrogram(hist, ratio):
    fig, ax = plt.subplots(figsize=(10, 10*ratio))
    ax.bar(range(256), height=hist, width=1)
    # ax.axis("off")
    img_io = BytesIO()
    fig.savefig(img_io, format='png')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')


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
            state.clear_choice()
            state.clear_option()
        if "img" in request.json:   
            state.img = request.json['img']
        if "choice" in request.json:
            state.choice = request.json['choice']
        if "optionValue" in request.json:
            state.option_value = request.json['optionValue']
    return state.jsonify()


@app.route("/pic/<int:picture_id>")
def return_pic(picture_id):
    if picture_id == 1:
        return serve_pil(state.pil)
    if picture_id == 2:
        return serve_pil(state.grayscale_pil)
    if picture_id == 3:
        return serve_histrogram(state.hist, state.size_ratio)
    return state.get_result()


@app.route("/project_pic")
def return_project_pic():
    return app.send_static_file('Project_%s.jpg' % state.pid)

if __name__ == "__main__":
    print("Run the webapp at http://<any address for your local host>:%s/" % APP_PORT)

    # IMPORTANT: `threaded=False` to ensure correct behavior
    app.run(port=APP_PORT, threaded=False, host=APP_HOST, debug=True)
