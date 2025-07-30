import mimetypes
#import imp
from flask import Flask, render_template, redirect, request, Response
from detector import detector, toggle_alarm, alarm_on
import cv2
import webbrowser
import numpy as np
import json
import supervision as sv
from ast import literal_eval


app = Flask("__name__")

@app.route('/')
def gohome():
    return render_template('index.html')


@app.route('/setting', methods=['GET', 'POST'])
def getSet():
    cam = request.form['cam']
    zone_name = request.form['x']
    sd = request.form['sound']
    objects = request.form.getlist('Objects')
    draw_zone = request.form.get('draw_zone', '')

    if draw_zone == 'on':
        cam_idx = int(cam) if cam.isdigit() else cam
        from danger import getcam
        polygon = getcam(cam_idx)
        if polygon:
            # Save polygon file
            with open(zone_name, 'w') as f:
                json.dump(polygon, f)
            print('Zone saved:', polygon)

    settings = {
        "camera": cam,
        "zone_name": zone_name,
        "sound_state": sd,
        "objects": objects
    }
    with open('setting.json', 'w') as file:
        json.dump(settings, file, indent=4)
    print('Settings saved successfully!')
    return redirect('/')

@app.route('/live')
def show_live():
    # Read settings from a JSON file
    try:
        with open('setting.json', 'r') as file:
            settings = json.load(file)

        # Convert 'objects' field to a list of integers
        settings['objects'] = [int(obj) for obj in settings['objects']]

        # print(settings['objects'])
        # print('Camera =', settings['camera'],'Danger Zone =',  settings['zone_name'],'Play sound =',  settings['sound_state'])

        # Read the danger zone coordinate from zone_name 
        fl = open(settings['zone_name'], 'r')
        p = fl.read()
        fl.close()
        zone_cord = p.split('\n')
        
    except Exception as err:
        return Response('<h2>No Camera is Configured or Danger zone is not specified.<br/> To create danger zone, run the danger.py app</h2>' + err)
    
    # return redirect('/')
    return Response(show2(settings['camera'], zone_cord, settings['sound_state'], settings['objects']), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/report')
def rep():
    dt =[]
    ca=[]
    ur=[]
    fl = open('reports.txt', 'r+')
    ms = fl.read()
    fl.close()
    alms = ms.split('\n')
    for m in alms:
        if len(m)>1:
            a1,a2,a3 = m.split(',')
            dt.append(a1)
            ur.append(a2)
            ca.append(a3)
            
    l = len(dt)
    return render_template('rep.html', l=l, dt=dt, ca=ca, ur=ur)

@app.route('/reportdrone')
def rep1():
    dt =[]
    ps=[]
    ca=[]
    ur=[]
    bk=[]
    cw=[]
    fl = open('dronereport.txt', 'r+')
    ms = fl.read()
    fl.close()
    alms = ms.split('\n')
    for m in alms:
        if len(m)>1:
            a1,a2,a3,a4,a5,a6 = m.split(',')
            dt.append(a1)
            ur.append(a2)
            ca.append(a3)
            ps.append(a4)
            bk.append(a6)
            cw.append(a5)
    
    l = len(dt)
    return render_template('repdrone.html', l=l, dt=dt, ps=ps, ca=ca, ur=ur,bk=bk,cw=cw)


@app.route('/monitor')
def monr():
    if alarm_on:
        #detector.ALARM = False
        def generate():
            with open('sound/street.wav', 'rb') as fwav:
                data = fwav.read(1024)
                while data:
                    yield data
                    data = fwav.read(1024)
        return Response(generate(), mimetype='audio/x-wav')
    else:
        return 'No Alarm'
    #return render_template('mon.html', r=r)


@app.route('/monroute')
def sr():
    global ALARM    
    toggle_alarm()
    return redirect('/')


# @app.route('/zone')
# def draw_zone():
#     cap = cv2.VideoCapture(0)
    
#     while cap.isOpened():
#         success, frame = cap.read()
#         if success:
#             if cv2.waitKey(1) == 13:
#                 print('Saving the line drawn...')
#                 fl = open('house', 'w')
#                 fl.writelines(str(l)+'\n' for l in points)
#                 fl.close()
#                 print('Lines saved!')

#             frame_for_web = cv2.imencode('.jpg',frame)[1].tobytes()
#             #return Response('Goopd')
#             # yield(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame_for_web + b'\r\n')
#         return Response(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame_for_web + b'\r\n', mimetype='multipart/x-mixed-replace; boundary=frame')
            

#         # if cv2.waitKey(1) == 27: break
#     # vid.release()
#     # cv2.destroyAllWindows()
            
#     # return Response(frame_for_web, mimetype='multipart/x-mixed-replace; boundary=frame')
    


def show2(cm, p0, sd, obj):
    import cv2, numpy as np, supervision as sv
    from ast import literal_eval

    # Parse polygon vertices from input
    pts = [literal_eval(pt) for pt in p0[:4]]
    print(str(pts[0]))
    polygon = np.array(pts[0], dtype=int)  # shape (4, 2)
    if cm == '0': cm = int(0)

    # cm = "../video/slow_traffic.mp4"
    # Load video
    cap = cv2.VideoCapture(cm)
    # video_info = sv.VideoInfo.from_video_path(video_path=cm)

    # Create polygon zone with center-anchor triggering
    detect_zone = sv.PolygonZone(polygon=polygon,
                                 triggering_anchors=(sv.Position.CENTER,))

    # Annotator to draw zone and display count
    zone_annotator = sv.PolygonZoneAnnotator(
        zone=detect_zone,
        color=sv.Color.RED,
        text_scale=0.5,
        text_thickness=1,
        thickness=2,
        text_color=sv.Color.BLACK
    )

    # Frame loop
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        # Run detection → apply tracking → mask filtering in detector()
        annotated = detector(frame, detect_zone, sd, obj)

        # Draw the polygon zone lines
        annotated = sv.draw_polygon(scene=annotated, polygon=polygon, color=sv.Color.RED, thickness=1)

        # Annotate count inside the zone
        annotated = zone_annotator.annotate(scene=annotated)

        # Yield frame to web stream
        h, w = annotated.shape[:2]
        frame_resized = cv2.resize(annotated, (w, h), interpolation=cv2.INTER_CUBIC)
        jpg = cv2.imencode('.jpg', frame_resized)[1].tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' +
               jpg + b'\r\n')

    # cap.release()
        # except Exception as err:
            # print(err)
    # cap.release()
    # cap = cv2.VideoCapture(cm)
     

if __name__ == '__main__':
    # webbrowser.open('http://localhost:3005', new=0, autoraise=True)
    app.run(debug=True, host='0.0.0.0', port=3005)
    