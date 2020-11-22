import cv2
import random as r
cap = cv2.VideoCapture(0)
switch = 0
out = None


def control_video():
    global switch, out

    def start_recording():
        global out
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(f'output{r.randrange(1, 9999)}.avi', fourcc, 20.0, (640, 480))

    def stop_recording():
        global out
        if out:
            out.release()

    switch = switch ^ 1
    if switch == 1:
        start_recording()
    else:
        stop_recording()


class FrameProcessing:
    def __init__(self, frame):
        self.frame = frame
        self.gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

    def detect_face(self):
        path = "haarcascade_frontalface_default.xml"
        face_cascade = cv2.CascadeClassifier(path)
        faces = face_cascade.detectMultiScale(self.gray, scaleFactor=1.10, minNeighbors=5, minSize=(40, 40))
        for (x, y, w, h) in faces:
            cv2.rectangle(self.frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    def detect_eyes(self):
        path = "haarcascade_eye.xml"
        eye_cascade = cv2.CascadeClassifier(path)
        eyes = eye_cascade.detectMultiScale(self.gray, scaleFactor=1.02, minNeighbors=20, minSize=(10, 10))

        for (x, y, w, h) in eyes:
            xc = (x + x + w) / 2
            yc = (y + y + h) / 2
            radius = w / 2
            cv2.circle(self.frame, (int(xc), int(yc)), int(radius), (255, 0, 0), 2)

    def run(self):
        self.detect_face()
        self.detect_eyes()
        return self.frame




while True:
    ret, frame = cap.read()

    #frame = cv2.resize(frame, (0,0), fx=1, fy=1)
    cv2.imshow("Original", frame)
    cv2.imshow("Analytics", FrameProcessing(frame).run())

    ch = cv2.waitKey(1)
    if ch & 0xFF == ord('q'):
        print(ch)
        break
    elif ch and ch < 1000 and ch > 0:
        print(ch)
        if chr(ch) == 'r' or chr(ch) == 's':
            control_video()


cap.release()
if out:
    out.release()
cv2.destroyAllWindows()