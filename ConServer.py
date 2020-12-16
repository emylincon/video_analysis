from flask import Flask, render_template, session, url_for, request, jsonify, Response
import cv2
import time
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
from flask_marshmallow import Marshmallow
import os
from analysis.ageGender import AnalyzeFrame
from analysis.advertSuggestion import Suggestion
from analysis.TimeSeries import TimeSeriesPredict
from datetime import datetime as dt

app = Flask(__name__)
# cap1 = cv2.VideoCapture('rtsp://ubnt:ubnt@10.1.2.111/s2')
# cap2 = cv2.VideoCapture('rtsp://ubnt:ubnt@10.1.2.123/s2')
cap1 = cap2 = cv2.VideoCapture(0)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.db')
db = SQLAlchemy(app)
ma = Marshmallow(app)
display = {'gender': [0] * 2, 'age': [0] * 8}
faces = 0
loop_time = 0.1
advert_suggestion = Suggestion(local=0)
predictor = TimeSeriesPredict(local=0)


# database models
class Detected(db.Model):
    id = Column(Integer, primary_key=True)
    datetime = Column(String)
    male = Column(Integer)
    female = Column(Integer)
    infant = Column(Integer)    # self.ageList = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
    baby = Column(Integer)
    child = Column(Integer)
    teen = Column(Integer)
    young = Column(Integer)
    adult = Column(Integer)
    middle = Column(Integer)
    senior = Column(Integer)


class DetectedSchema(ma.Schema):
    class Meta:
        fields = ('id', 'datetime', 'male', 'female', 'infant', 'baby', 'child', 'teen',
                  'young', 'adult', 'middle', 'senior')


detected_schema = DetectedSchema()
detected_schemas = DetectedSchema(many=True)


#@app.cli.command('db_create')
def db_create():
    db.create_all()
    print('database created!')


#@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print('database dropped!')


#@app.cli.command('db_seed')
def db_seed():
    entry = Detected(datetime="{:%d-%m-%Y %H:%M:%S}".format(dt.now()),
                     male=1,
                     female=0,
                     infant=0,
                     baby=0,
                     child=0,
                     teen=0,
                     young=0,
                     adult=1,
                     middle=0,
                     senior=0)

    db.session.add(entry)
    db.session.commit()
    print('database seeded!')


def add_data(male, female, infant, baby, child, teen, young, adult, middle, senior):
    db.session.add(Detected(datetime="{:%d-%m-%Y %H:%M:%S}".format(dt.now()),
                            male=male, female=female, infant=infant, baby=baby, child=child, teen=teen, young=young,
                            adult=adult, middle=middle, senior=senior))
    db.session.commit()


class DataInput:
    def __init__(self, seconds=20):
        self.seconds = seconds
        self.start = time.time()
        self.compare = {}
        self.times = round(60/self.seconds)
        self.vector = (0,)*10
        self.last = (0,)*10

    def set_times(self):
        self.times = round(60/self.seconds)

    def add(self, data):
        data = tuple(data)
        if data != (0,)*10:
            if data in self.compare:
                self.compare[data] += 1
            else:
                self.compare[data] = 0
            if self.times <= 0:
                add_data(*max(self.compare, key=self.compare.get))
                self.set_times()
                self.compare = {}
        elif self.times <= 0:
            if len(self.compare) > 0:
                add_data(*max(self.compare, key=self.compare.get))
            self.set_times()
            self.compare = {}
        if (time.time() - self.start) > self.seconds:
            try:
                self.vector = max(self.compare, key=self.compare.get)
            except ValueError:
                self.vector = (0,) * 10
            self.times -= 1
            self.start = time.time()


data_input = DataInput()


@app.route('/')
def home():
    return render_template('dashboard2.html')


class FrameManager:
    def __init__(self, no=5, frame_limit=10):
        self.no_of_frames = no
        self.count = 0
        self.frame_folder = 'static/frames'
        self.frame_limit = frame_limit
        self.frames = []
        self.clean_up()

    def clean_up(self):
        for file in os.listdir(self.frame_folder):
            os.remove(f'{self.frame_folder}/{file}')

    def add_count(self):
        self.count += 1
        self.limit_count()

    def limit_count(self):
        if self.count > 50000:
            self.count -= 50000

    def skip_frame(self):
        if self.count % self.no_of_frames == 0:
            return True
        return False

    def save_frame(self, frame):
        name = f'{self.frame_folder}/{round(time.time())}.jpg'
        cv2.imwrite(name, frame)
        return name

    def remove_frame(self):
        try:
            os.remove(f'{self.frames.pop(0)}')
        except FileNotFoundError:
            pass

    def add_frame(self, frame):
        self.frames.append(self.save_frame(frame))
        if len(self.frames) > self.frame_limit:
            self.remove_frame()


frame_manager1 = FrameManager()
frame_manager2 = FrameManager(no=13)


def gen():
    """Video streaming generator function."""

    # Read until video is completed
    while (cap1.isOpened()):
        # Capture frame-by-frame
        ret = cap1.grab()
        frame_manager1.add_count()
        if frame_manager1.skip_frame():
            if ret:
                ret, img = cap1.retrieve()
                img = cv2.resize(img, (0, 0), fx=1, fy=0.6)
                frame = cv2.imencode('.jpg', img)[1].tobytes()
                yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                time.sleep(loop_time)
            else:
                break


def gen1():
    global display, faces
    """Video streaming generator function."""

    # Read until video is completed
    while (cap2.isOpened()):
        # Capture frame-by-frame
        ret = cap2.grab()
        frame_manager2.add_count()
        if frame_manager2.skip_frame():
            if ret:
                ret, img = cap2.retrieve()
                img = cv2.resize(img, (0, 0), fx=1, fy=1)
                img, display, faces = AnalyzeFrame().age_gender_detector(img)
                # add_data(*display['gender']+display['age'])
                frame_manager2.add_frame(img)
                data_input.add(display['gender']+display['age'])
                frame = cv2.imencode('.jpg', img)[1].tobytes()
                yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                time.sleep(loop_time)
            else:
                break


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    try:
        return Response(gen(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    except cv2.error as e:
        print('CV2 Error: ', e)


@app.route('/video_analysis')
def video_analytics():
    """Video streaming route. Put this in the src attribute of an img tag."""
    try:
        return Response(gen1(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    except cv2.error as e:
        print('CV2 Error: ', e)


@app.route('/get_stat')
def get_stat():
    return jsonify({**display, 'faces': faces}), 200


@app.route('/get_advert')
def get_advert():
    is_predicted = 0
    vector = data_input.vector
    if vector == (0,)*10:
        is_predicted = 1
        vector = predictor.get_output(data_input.last)

    data_input.last = vector
    sex = ['male', 'female']
    age_group = ['(0, 3)', '(4, 7)', '(8, 14)', '(15, 24)', '(25, 37)', '(38, 47)', '(48, 53)', '(60, 100)']
    gender_list, age_list = vector[:2], vector[2:]
    gender_max, age_max = max(gender_list), max(age_list)
    gender, age = sex[gender_list.index(gender_max)], age_group[age_list.index(age_max)]

    advert = advert_suggestion.suggest_random(age=age, gender=gender)
    return jsonify({'advert': advert, 'is_predicted': is_predicted}), 200


@app.route('/get_frames')
def get_frames():
    frames = frame_manager2.frames
    return jsonify({'images': frames}), 200


if __name__ == '__main__':
    # app.run(debug=True, host="0.0.0.0")
    app.run(debug=True)
