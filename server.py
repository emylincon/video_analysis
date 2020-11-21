from flask import Flask, render_template, session, url_for, request, jsonify, Response
import cv2
import time
from analysis.ageGender import AnalyzeFrame

app = Flask(__name__)
cap = cv2.VideoCapture(0)


@app.route('/')
def home():
    return render_template('index.html')


def gen():
    """Video streaming generator function."""

    # Read until video is completed
    while (cap.isOpened()):
        # Capture frame-by-frame
        ret, img = cap.read()
        if ret == True:
            img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
            frame = cv2.imencode('.jpg', img)[1].tobytes()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.1)
        else:
            break


def gen1():
    """Video streaming generator function."""

    # Read until video is completed
    while (cap.isOpened()):
        # Capture frame-by-frame
        ret, img = cap.read()
        if ret == True:
            img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
            img = AnalyzeFrame().age_gender_detector(img)
            frame = cv2.imencode('.jpg', img)[1].tobytes()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.1)
        else:
            break


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_analysis')
def video_analytics():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen1(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True)