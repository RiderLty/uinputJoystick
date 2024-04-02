# # #OCR

# import asyncio
# from os.path import join as path_join
# import time

# from fastapi import FastAPI, UploadFile
# from fastapi.responses import FileResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.middleware.gzip import GZipMiddleware

# from uvicorn import Config, Server
# from utils.imgTools import pil2np
# from paddleocr import PaddleOCR
# import cv2
# from PIL import Image

# p_ocr = PaddleOCR(use_angle_cls=True,  use_gpu = True , show_log=False,)
# app = FastAPI()
# app.add_middleware(GZipMiddleware, minimum_size=1000)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# @app.get("/")
# def index():
#     return FileResponse(path_join("controller/html", "ocr_index.html"))


# @app.post("/ocr")
# async def ocr(image: UploadFile):
#     try:
#         image = image.file
#         image = pil2np(Image.open(image).convert('RGB'))
#         start = time.time()
#         result = p_ocr.ocr(image, cls=True)
#         end = time.time()
#         cnocrResults = []
#         allText = ""
#         for idx in range(len(result)):
#             res = result[idx]
#             for line in res:
#                 [position , (text , score) ] = line
#                 # print(text,score , position)
#                 cnocrResults.append({
#                     "position":position,
#                     "score":score,
#                     "text":text,
#                 })
#                 allText += f"[{text}]"
#         print(f"OCR in {end-start :.4f}s\n{allText}\n" )
#         return cnocrResults
#     except Exception as e:
#         print(e)
#         return '[]'


# app.mount("/", StaticFiles(directory="controller/html"), name="static")

# def getServer(port):
#     serverConfig = Config(
#         app=app,
#         # host="::",
#         host="0.0.0.0",
#         port=port,
#         log_level="info",
#         ws_max_size=1024*1024*1024*1024,
#     )
#     return Server(serverConfig)

# mainEventLoop = asyncio.get_event_loop()
# serverInstance = getServer(8501)
# mainEventLoop.run_until_complete(serverInstance.serve())

# # result = p_ocr.ocr(url2ImgNp("http://192.168.3.155:4443/screen"), cls=True)




# #OCR

import asyncio
import logging
from os.path import join as path_join
import time

from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from uvicorn import Config, Server
from utils.imgTools import pil2np
from paddleocr import PaddleOCR
from PIL import Image
import coloredlogs

p_ocr = PaddleOCR(use_angle_cls=True,  use_gpu = True , show_log=False,)
app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def index():
    return FileResponse(path_join("controller/html", "ocr_index.html"))


@app.post("/ocr")
async def ocr(image: UploadFile):
    try:
        image = image.file
        image = pil2np(Image.open(image).convert('RGB'))
        start = time.time()
        result = p_ocr.ocr(image, cls=True)
        end = time.time()
        cnocrResults = []
        allText = ""
        for idx in range(len(result)):
            res = result[idx]
            for line in res:
                [position , (text , score) ] = line
                # print(text,score , position)
                cnocrResults.append({
                    "position":position,
                    "score":score,
                    "text":text,
                })
                allText += f"[{text}]"
        # print(f"OCR in {end-start :.4f}s\n{allText}\n" )
        return cnocrResults
    except Exception as e:
        print(e)
        return '[]'


app.mount("/", StaticFiles(directory="controller/html"), name="static")

def getServer(port):
    serverConfig = Config(
        app=app,
        # host="::",
        host="0.0.0.0",
        port=port,
        log_level="info",
        ws_max_size=1024*1024*1024*1024,
    )
    return Server(serverConfig)

mainEventLoop = asyncio.get_event_loop()
serverInstance = getServer(8501)
LOGGER_NAMES = ("uvicorn", "uvicorn.access",)
for logger_name in LOGGER_NAMES:
    logging_logger = logging.getLogger(logger_name)
    fmt = f"🌏%(asctime)s .%(levelname)s %(message)s"  # 📨
    coloredlogs.install(
        level=logging.WARN, logger=logging_logger, milliseconds=False, datefmt='%m-%d %H:%M:%S', fmt=fmt
    )
    
mainEventLoop.run_until_complete(serverInstance.serve())

# result = p_ocr.ocr(url2ImgNp("http://192.168.3.155:4443/screen"), cls=True)


