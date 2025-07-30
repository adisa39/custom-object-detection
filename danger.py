import cv2
import numpy as np

def getcam(cam):
    """
    Let user click to define a polygon zone on a live frame.
    Left-click to add points.
    Press Enter to finish and save.
    Press ESC to cancel.
    Returns list of points, or None.
    """
    cap = cv2.VideoCapture(cam)
    ret, frame = cap.read()
    h = frame.shape[0]
    w = frame.shape[1]
    frame = cv2.resize(frame, (w, h), interpolation=cv2.INTER_CUBIC)
    cap.release()
    if not ret:
        print('Failed to capture frame from', cam)
        return None

    pts = []
    drawing_img = frame.copy()
    win = "Draw Zone (press Enter to finish, ESC to cancel)"
    cv2.namedWindow(win)

    def mouse_cb(event, x, y, flags, param):
        nonlocal drawing_img
        if event == cv2.EVENT_LBUTTONDOWN:
            pts.append((x, y))
        # draw live polyline
        if len(pts) >= 1:
            img = frame.copy()
            cv2.polylines(img, [np.array(pts, np.int32)], False, (0, 0, 255), 2)
            cv2.imshow(win, img)

    cv2.setMouseCallback(win, mouse_cb)
    cv2.imshow(win, drawing_img)

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == 13:  # Enter → finish
            print("Polygon completed:", pts)
            break
        if key == 27:  # ESC → cancel
            print("Polygon drawing canceled.")
            pts = None
            break

    cv2.destroyWindow(win)
    return pts
