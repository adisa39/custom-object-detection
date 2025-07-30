import cv2


def ddd(cam):
    print(cam)
    if cam == '0':
        cam =0
    p = cv2.VideoCapture(cam)
    while True:
        st, m=p.read()
        print("Camera status: ", st)
        print(m)
        if cv2.waitKey(1)==27:
            break
#if __name__=='__main__':
m = input('Enter the camera url:')
ddd(m)