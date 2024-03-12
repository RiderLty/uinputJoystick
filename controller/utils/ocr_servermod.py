import requests

image_fp = r"C:\Users\lty\Pictures\QQ截图20231026105710.jpg"
while True:
    r = requests.post(
    'http://192.168.3.1:8501/ocr', files={'image': (image_fp, open(image_fp, 'rb'), 'image/png')},
    )
    ocr_out = r.json()['results']
    print(ocr_out)