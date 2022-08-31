import urllib.request
import urllib.parse
import base64
import os
import time
import requests
import picamera
import smbus
import schedule
import time

# Untuk kirim data sensornya pak
# POST http://mlj.belajarobot.com/sensor/***

# * id lumbung
# Content-Type : multipart/form-data

# moist
# lumen
# humid
# temp
# image -> tidak perlu encode base64

url_post  = 'http://mlj.belajarobot.com/sensor/1'
headers = {
  'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Mobile Safari/537.36'
}

hostname = "8.8.8.8"


def realtime():
    readLux()
    readSHT()
    takePicture()
    name_img = 'picture.png'
    img = open(name_img, 'rb')
    data = {
        'lumen': int(lux),
        'temp': int(cTemp),
        'humid': int(humidity),
        'moist': 0,
    }
    files = {'image': (name_img,img,'images/png')}

    try:
        res = requests.post(url_post, data=data, files=files, headers=headers)
        print(res.text)
    
    except Exception as error:
        print(error)


def takePicture():
    try:
        camera = picamera.PiCamera()
        time.sleep(0.5)
        camera.resolution = (320, 240)
        camera.rotation = 180
        camera.start_preview()
        time.sleep(0.5)
        camera.capture('picture.png')
        camera.stop_preview()
        camera.close()
    except:
        print("Camera Error")


def readLux():
    global lux
    try:
        bus = smbus.SMBus(1)
        bus.write_byte_data(0x39, 0x00 | 0x80, 0x03)
        bus.write_byte_data(0x39, 0x01 | 0x80, 0x02)
        time.sleep(0.5)
        data = bus.read_i2c_block_data(0x39, 0x0C | 0x80, 2)
        lux = data[1] * 256 + data[0]

        # print("Lux Meter: {} Lumen".format(lux))

    except Exception as error:
        print("Lux data error")


def readSHT():
    global cTemp, fTemp, humidity
    try:
        # Get I2C bus
        bus = smbus.SMBus(1)
        bus.write_i2c_block_data(0x44, 0x2C, [0x06])  # Address 0x44
        time.sleep(0.5)
        data = bus.read_i2c_block_data(0x44, 0x00, 6)

        # Convert the data
        temp = data[0] * 256 + data[1]
        cTemp = -45 + (175 * temp / 65535.0)
        fTemp = -49 + (315 * temp / 65535.0)
        humidity = 100 * (data[3] * 256 + data[4]) / 65535.0

        # print("Temperature in Celsius is : %.2f C" % cTemp)
        # print("Temperature in Fahrenheit is : %.2f F" % fTemp)
        # print("Relative Humidity is : %.2f %%RH" % humidity)

    except:
        print("SHT error")


def mainloop():
    schedule.run_pending()
    time.sleep(1)


# Inisialisasi
schedule.every(3).minutes.do(realtime)

while True:
    response = os.system("ping -c3 " + hostname)
    if response == 0:
        mainloop()
    else:
        print("Device not connected to Internet")
