from controller.utils.ocrTool import ocrTool
from controller.utils.screenCap import screenCap
from utils.taskScheduler import scheduled
from utils.interface.winController import *


screenCap = screenCap()
ocrTool = ocrTool()

img = screenCap()

print(ocrTool(img))