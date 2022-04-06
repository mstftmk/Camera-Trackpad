import cv2
import numpy as np
import mediapipe as mp
import pyautogui as pyAuto

wScr, hScr = pyAuto.size() #bilgisayarın ekran boyuları.
frame = 150 #mousepad sınırlarını belirlemek için.
tipIds = [4, 8, 12, 16, 20] #parmak ucu id'leri

cap = cv2.VideoCapture(0)
width, height  = cap.get(3), cap.get(4) #Kameranın boyutları

#hand detection mediapipe ile.
mpHands = mp.solutions.hands
hands = mpHands.Hands(static_image_mode=False,
                      max_num_hands=2,
                      min_detection_confidence=0.5,
                      min_tracking_confidence=0.5)
mpDraw = mp.solutions.drawing_utils

while True:                 
    lmlist=[] #landmark list için array
    xList=[] #x konumları için array
    ylist=[] #y konumları için array

    success, img = cap.read() #videoyu okudu
    img = cv2.flip(img, 1) #videoyu ters çevirdi.
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) #griye çevirdi.
    results = hands.process(imgRGB) #handprocess yaptı
    
    #ret, thresh1 = cv2.threshold(img, 255, 0, cv2.THRESH_BINARY) #Eğer kamera arkaplanı siyah olsun istenirse, bunu yorumdan çıkarıp, img görünen yerlere thresh yazılabilir.

    cv2.rectangle(img,(frame,frame),(int(width-frame),int(height-frame)),(0,0,177),2) #mousepad sınırları çizdik.
    cv2.putText(img, "Trackpad Area", (frame, frame-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,250,250), 2, cv2.LINE_AA)
    
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            for id, lm in enumerate(handLms.landmark): #enumerate ettik. eldeki noktaları görmek için. 21 adet.
                
                h, w, c = img.shape #ekran boyutunu veriyor.
                cx, cy = int(lm.x *w), int(lm.y*h) # noktaların ekrandaki konumu.
                
                lmlist.append([id,cx,cy])
                xList.append(cx)
                ylist.append(cy)

                cv2.circle(img, (cx,cy), 3, (255,0,255), cv2.FILLED)

            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
            
    if len(lmlist)!=0:
        #parmak uçlarının hangi noktalar olduğunu gösteriyor.
        Xthumb, Ythumb = lmlist[4][1], lmlist[4][2] #baş parmak x-y.
        Xindex,Yindex = lmlist[8][1],lmlist[8][2] #işaret parmağı x-y
        Xmiddle,Ymiddle = lmlist[12][1],lmlist[12][2] # orta parmak x-y 
        xRing, yRing = lmlist[16][1],lmlist[20][2] #Yüzük parmağı x-y
        xSmall, ySmall = lmlist[20][1],lmlist[20][2] #serçe parmak x-y
        
        #sınır olarak belirttiğimiz alanda, parmak uçlarının konumunu dönüştürüyor.     
        xMOUSE = np.interp(Xindex,(frame,width-frame),(0,wScr))
        yMOUSE = np.interp(Yindex,(frame,height-frame),(0,hScr))    
            
        fingers = [] #burası, parmaklar kalkınca, 1 indirince 0 olmasını sağlıyor.
        # Baş parmak: açınca mouse click olması için.
        if lmlist[tipIds[0]][1] > lmlist[tipIds[0] - 2][1]:
            fingers.append(0) #1
        else:
            fingers.append(1) #0
        
        # Geri kalan parmaklar
        for id in range(1, 5):
            if lmlist[tipIds[id]][2] < lmlist[tipIds[id] - 2][2]:
               fingers.append(1)
            else:
                fingers.append(0)
        print(fingers)
        
        if fingers[1]==1 and (fingers[0] == 0 and fingers[2]==0): #işaret parmağı havada olunca mouse ile gezinme.
            #mouse'u belirtilen x-y konumuna götürüyor.
            pyAuto.moveTo(xMOUSE, yMOUSE)
            pyAuto.PAUSE = 0.00000001 #Bu satır ile, mouse hareketlerindeki kasılmaları gideriyoruz.
            cv2.circle(img,(Xindex,Yindex),15,(20,180,90),cv2.FILLED)
            
        if fingers[0] == 1 and (fingers[1] == 1 and fingers[2]==0): #işaret ve baş parmak havada olunca click.
            pyAuto.click()
            pyAuto.PAUSE = 0.00000001
            cv2.circle(img,(Xthumb,Ythumb),15,(12,233,240),cv2.FILLED)
            cv2.circle(img,(Xindex,Yindex),15,(12,233,240),cv2.FILLED)
            
        if (fingers[0] == 0 and fingers[3] == 0) and (fingers[1] == 1 and fingers[2]==1): #işaret ve orta parmak havada olunca sağ click.
            pyAuto.click(button='right')
            pyAuto.PAUSE = 0.00000001
            cv2.circle(img,(Xindex,Yindex),15,(255,128,0),cv2.FILLED)
            cv2.circle(img,(Xmiddle,Ymiddle),15,(255,128,0),cv2.FILLED)
        
        if 1 not in fingers: #Eli yumruk şeklinde tutunca aşağı doğru kaydırma.
            pyAuto.scroll(-5)
            cv2.circle(img,(Xindex,Yindex),15,(246,0,254),cv2.FILLED)
            cv2.circle(img,(Xthumb,Ythumb),15,(246,0,254),cv2.FILLED)
            cv2.circle(img,(Xmiddle,Ymiddle),15,(246,0,254),cv2.FILLED)
            cv2.circle(img,(xRing,yRing),15,(246,0,254),cv2.FILLED)
            cv2.circle(img,(xSmall,ySmall),15,(246,0,254),cv2.FILLED)

        if fingers[4] == 1 and fingers[0] == 0: #serçe parmak havada olunca yukarı doğru kaydırma.
            pyAuto.scroll(5)
            cv2.circle(img,(xSmall,ySmall),15,(42,112,232),cv2.FILLED)
            
    cv2.imshow('Trackpad', img)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break