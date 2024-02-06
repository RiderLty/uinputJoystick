from PIL import Image
from cnocr import CnOcr

def ocrTool():
    cnocrInstance = CnOcr()
    def inner(img:Image):
        out = cnocrInstance.ocr(img)
        allText = "|".join([x["text"] for x in out]).strip()
        return (allText, out)
    return inner