# 服务端

## 功能介绍

适用于安卓的虚拟键鼠与手柄

<!-- ## Quick start

从release直接下载编译好的二进制程序

[uinputJoystick](https://github.com/RiderLty)

读写uinput需要shell或者root权限

所以可以用adb shell或者su shell运行 -->

## 编译

使用环境 termux
```
pkg i golang -y
git clone https://github.com/RiderLty/uinputJoystick --depth=1
cd uinputJoystick/server
CGO_ENABLE=0 GOOS=linux go build -ldflags="-s -w"
```

## 运行
[termux如何连接本机无线调试](https://www.bilibili.com/video/BV14P411E7Bt/?spm_id_from=333.337.search-card.all.click)
```
adb push ./uinputJoystick /data/local/tmp
adb shell chmod 777  /data/local/tmp/uinputJoystick
adb shell /data/local/tmp/uinputJoystick
```
