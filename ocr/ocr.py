import os
import subprocess
import time

workingDir, _ = os.path.split(__file__)
ocrBin = os.path.join(workingDir, "tesseract-arm64-v8a")
ocrData = os.path.join(workingDir, "image_text_searcher", "tessdata")
print(ocrData)


def ocr(path):
    start = time.time()
    command = [ocrBin, "--tessdata-dir",
               ocrData, path, "stdout", "-l", "chi_sim"]

    process = subprocess.Popen(command,  stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out,err = process.communicate()
    return out.decode("UTF-8")


res = ocr(r"/data/data/com.termux/files/home/storage/shared/Pictures/Screenshots/Screenshot_20240123-211508.jpg")
print(res)