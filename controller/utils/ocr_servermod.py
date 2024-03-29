import time
import requests

image_fp = r"D:\Pictures\Screenshots\warframe\SC (9).png"

start = time.time()
r = requests.post(
    'http://192.168.3.128:8501/ocr', files={'image': (image_fp, open(image_fp, 'rb'), 'image/png')},
)
ocr_out = r.json()
print(ocr_out)
print("over in ", time.time() - start)
