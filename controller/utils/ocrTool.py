# import cv2
# import requests


# class ocrTool():
#     def __init__(self, api_url="http://192.168.3.128:8501/ocr") -> None:
#         self.api_url = api_url

#     def ocr(self, npImg ):
#         try:
#             _, imgBytes = cv2.imencode('.png', npImg)
#             r = requests.post(self.api_url, files={'image': imgBytes})
#             ocr_out = r.json()
#             return ocr_out
#         except Exception as e:
#             print(e)
#             return []

from cnocr import CnOcr as ocrTool
