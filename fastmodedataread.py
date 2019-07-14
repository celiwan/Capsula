import time, serial
import numpy as np
ser = serial.Serial('/dev/ttyACM0',115200,bytesize=serial.EIGHTBITS)
dataList=[]
i=1
tper=60
j=0
for k in range(0,tper,1):
    i=1
    while i==1:
        data=ser.read(40000)
        ser.flushInput()
        j+=40000
        if len(data)>=40000:
            i = 0
            k+=1
            print(k)
            dataList = np.append(dataList,(list(data)))
            data = 0
    
dataList = list(map(float,dataList))
dataListFloat = [i*0.00322581 for i in dataList]
timeData = np.arange(0.0, j*100e-6,100e-6)
finalData = np.column_stack((timeData,dataListFloat))
np.save('datatest.npy',finalData)
ser.close()

