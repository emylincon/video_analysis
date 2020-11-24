from flask import Flask, render_template, session, url_for, request, jsonify, Response
import cv2
import time
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
from flask_marshmallow import Marshmallow
import os
from analysis.ageGender import AnalyzeFrame
from datetime import datetime as dt

app = Flask(__name__)
cap = cv2.VideoCapture(0)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.db')
db = SQLAlchemy(app)
ma = Marshmallow(app)
display = {'gender': [0] * 2, 'age': [0] * 8}
faces = 0


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
        fields = ('id', 'datetime', 'male', 'female', 'infant', 'baby', 'child', 'teen', 'young', 'adult', 'middle', 'senior')


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
    def __init__(self):
        self.start = time.time()
        self.compare = {}

    def add(self, data):
        data = tuple(data)
        if data != (0,)*10:
            if data in self.compare:
                self.compare[data] += 1
            else:
                self.compare[data] = 0
            if (time.time() - self.start) > 60:
                add_data(*max(self.compare, key=self.compare.get))
                self.start = time.time()
                self.compare = {}


data_input = DataInput()


@app.route('/')
def home():
    return render_template('dashboard.html')


def gen():
    """Video streaming generator function."""

    # Read until video is completed
    while (cap.isOpened()):
        # Capture frame-by-frame
        ret, img = cap.read()
        if ret == True:
            img = cv2.resize(img, (0, 0), fx=1, fy=0.6)
            frame = cv2.imencode('.jpg', img)[1].tobytes()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.1)
        else:
            break


def gen1():
    global display, faces
    """Video streaming generator function."""

    # Read until video is completed
    while (cap.isOpened()):
        # Capture frame-by-frame
        ret, img = cap.read()
        if ret == True:
            img = cv2.resize(img, (0, 0), fx=1, fy=0.6)
            img, display, faces = AnalyzeFrame().age_gender_detector(img)
            # add_data(*display['gender']+display['age'])
            data_input.add(display['gender']+display['age'])
            frame = cv2.imencode('.jpg', img)[1].tobytes()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.1)
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


if __name__ == '__main__':
    app.run(debug=True)
