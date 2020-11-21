import cv2 as cv
import time


class AnalyzeFrame:
    def __init__(self):
        self.faceProto = "data/modelNweight/modelNweight/opencv_face_detector.pbtxt"
        self.faceModel = "data/modelNweight/modelNweight/opencv_face_detector_uint8.pb"

        self.ageProto = "data/modelNweight/modelNweight/age_deploy.prototxt"
        self.ageModel = "data/modelNweight/modelNweight/age_net.caffemodel"

        self.genderProto = "data/modelNweight/modelNweight/gender_deploy.prototxt"
        self.genderModel = "data/modelNweight/modelNweight/gender_net.caffemodel"

        self.MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
        self.ageList = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
        self.genderList = ['Male', 'Female']

        # Load network
        self.ageNet = cv.dnn.readNet(self.ageModel, self.ageProto)
        self.genderNet = cv.dnn.readNet(self.genderModel, self.genderProto)
        self.faceNet = cv.dnn.readNet(self.faceModel, self.faceProto)

        self.padding = 20

    @staticmethod
    def getFaceBox(net, frame, conf_threshold=0.7):
        frameOpencvDnn = frame.copy()
        frameHeight = frameOpencvDnn.shape[0]
        frameWidth = frameOpencvDnn.shape[1]
        blob = cv.dnn.blobFromImage(frameOpencvDnn, 1.0, (300, 300), [104, 117, 123], True, False)

        net.setInput(blob)
        detections = net.forward()
        bboxes = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > conf_threshold:
                x1 = int(detections[0, 0, i, 3] * frameWidth)
                y1 = int(detections[0, 0, i, 4] * frameHeight)
                x2 = int(detections[0, 0, i, 5] * frameWidth)
                y2 = int(detections[0, 0, i, 6] * frameHeight)
                bboxes.append([x1, y1, x2, y2])
                cv.rectangle(frameOpencvDnn, (x1, y1), (x2, y2), (0, 255, 0), int(round(frameHeight/150)), 8)
        return frameOpencvDnn, bboxes

    def age_gender_detector(self, frame):
        # Read frame
        t = time.time()
        frameFace, bboxes = self.getFaceBox(self.faceNet, frame)
        for bbox in bboxes:
            # print(bbox)
            face = frame[max(0,bbox[1]-self.padding):min(bbox[3]+self.padding,frame.shape[0]-1),max(0,bbox[0]-self.padding):min(bbox[2]+self.padding, frame.shape[1]-1)]

            blob = cv.dnn.blobFromImage(face, 1.0, (227, 227), self.MODEL_MEAN_VALUES, swapRB=False)
            self.genderNet.setInput(blob)
            genderPreds = self.genderNet.forward()
            gender = self.genderList[genderPreds[0].argmax()]
            self.ageNet.setInput(blob)
            agePreds = self.ageNet.forward()
            age = self.ageList[agePreds[0].argmax()]

            label = "{},{}".format(gender, age)
            cv.putText(frameFace, label, (bbox[0], bbox[1]-10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2, cv.LINE_AA)
        return frameFace


# AnalyzeFrame().age_gender_detector(frame)
