# 用于实现键鼠手柄自动化的工具

虚拟了手柄，键盘，鼠标设备

可用于windows与android

win通过pywin32与vgamepad实现

android使用uinput创建，UDP操控

实现了统一的编程接口

## 使用说明(windows)

安装依赖
``` shell
pip install pywin32 vgamepad
```

运行测试

``` python
python controller/test.win.py
```

[手柄测试网站](https://hardwaretester.com/gamepad)

[键盘测试网站](https://www.bchrt.com/tools/keyboardtester/)

## 使用说明(Android)

[启动服务器](./server)

修改测试脚本IP地址

运行测试

``` python
python controller/test.android.py
```
