import cv2
import datetime

url = "rtsp://pei:5g-mobix@10.0.19.201:554"

def connectToCam():
    cap = cv2.VideoCapture(url, cv2.CAP_ANY)
    now = datetime.datetime.now()
    return cap, now

cap, startDate = connectToCam()

while True:
    ret,frame = cap.read()
    if not(ret):
        cap, startDate = connectToCam()
        continue
    else:
        camtime = cap.get(cv2.CAP_PROP_POS_MSEC)
        print(startDate + datetime.timedelta(milliseconds=camtime))


    cv2.imshow("Current frame", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows() 