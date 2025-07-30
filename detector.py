import cv2
import numpy as np
import supervision as sv
from ultralytics import YOLO
from threading import Thread
from playsound import playsound
import time
from datetime import datetime

# Global variable to keep track of alarm status
alarm_on = True

# Load the YOLOv8 model
model = YOLO('./v8_models/yolov8x.pt')

tracker = sv.ByteTrack()

# Initialize bounding box and label annotators
bounding_box_annotator = sv.RoundBoxAnnotator(thickness=2)
label_annotator = sv.LabelAnnotator(text_scale=1, text_thickness=1, text_position=sv.Position.TOP_CENTER)

# List to keep track of detected object IDs
track_obj_qty = None

def detector(frame, detect_zone, sound, objects):
    global track_obj_qty, alarm_on
    
    # Run YOLOv8 inference on the frame
    results = model(frame, device='cpu', classes=objects, verbose=False)
    detections = sv.Detections.from_ultralytics(results[0])

    # Filter out detections outside the zone
    mask = detect_zone.trigger(detections=detections)  
    detections = detections[mask]
    detections = tracker.update_with_detections(detections)

    # Get detected object labels
    labels = [model.model.names[class_id] for class_id in detections.class_id]
    tracker_ids = detections.tracker_id

    # Dictionary to store count of each detected object
    track_obj = detections.class_id

    # Visualize the results on the frame
    annotated_frame = frame.copy()
    annotated_frame = bounding_box_annotator.annotate(scene=annotated_frame, detections=detections)
    annotated_frame = label_annotator.annotate(scene=annotated_frame, detections=detections, labels=labels)
    
    # Count of each detected object on the frame
    detected_obj = {}
    for label in labels:
        if label in detected_obj.keys():
            detected_obj[label] += 1
        else:
            detected_obj[label] = 1
    print(detected_obj)

    # Convert detected_obj dictionary to string for displaying
    detected_obj_str = ' | '.join([f'{label}: {count}' for label, count in detected_obj.items()])

    # Check for new detections
    if len(tracker_ids) == track_obj_qty or len(tracker_ids) == 0:
        pass
    else:
        rs = Thread(target=report, args=(annotated_frame, detected_obj_str))
        rs.start()

        # Blow alarm if on
        if alarm_on and sound == 'enable':
            ts = Thread(target=sounder)
            ts.start()

    # Update detected objects list
    track_obj_qty = len(tracker_ids)  
     
    # Display the count of each detected object on the frame
    cv2.putText(annotated_frame, detected_obj_str, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
    return annotated_frame


# Function to toggle alarm status
def toggle_alarm():
    global alarm_on
    alarm_on = not alarm_on
    # print('alarm is silence')


# Function to play alarm sound
def sounder():
    global alarm_on
    while alarm_on:
        playsound('sound/classic.wav') 
        alarm_on = True


# Function to write new detection report
def report(pic, msg):
    fn = str(time.time())
    pic2 = pic.copy()
    fn = 'static/captures/' +fn.replace('.','') + '.jpg'
    cv2.imwrite(fn, pic2)
    f = open('reports.txt','a+')
    pp = str(datetime.now()) +', ' + fn +', ' +msg + '\n'
    f.write(pp)
    f.close()
    print('Report Updated!')