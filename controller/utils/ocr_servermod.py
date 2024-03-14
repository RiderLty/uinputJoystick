import time
import requests

image_fp = r"P:\5.jpg"

start = time.time()
r = requests.post(
'http://192.168.3.1:8501/ocr', files={'image': (image_fp, open(image_fp, 'rb'), 'image/png')},
)
ocr_out = r.json()['results']
print(ocr_out)
print("over in ",time.time() - start)