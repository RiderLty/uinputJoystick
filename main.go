package main

import (
	"bytes"
	"encoding/binary"
	"io/ioutil"
	"net"
	"net/http"
	"os"
	"os/exec"
	"syscall"
	"unsafe"

	"github.com/kenshaw/evdev"
	"github.com/lunixbochs/struc"
)

func toUInputName(name []byte) [uinputMaxNameSize]byte {
	var fixedSizeName [uinputMaxNameSize]byte
	copy(fixedSizeName[:], name)
	return fixedSizeName
}

func uInputDevToBytes(uiDev UinputUserDev) []byte {
	var buf bytes.Buffer
	_ = struc.PackWithOptions(&buf, &uiDev, &struc.Options{Order: binary.LittleEndian})
	return buf.Bytes()
}

func createDevice(f *os.File) (err error) {
	return ioctl(f.Fd(), UIDEVCREATE(), uintptr(0))
}

func sendEvents(fd *os.File, events []*evdev.Event) {
	sizeofEvent := int(unsafe.Sizeof(evdev.Event{}))
	if fd == nil {
		logger.Warnf("fd is nil,pass %v", events)
		return
	}

	buf := make([]byte, sizeofEvent*len(events))
	for i, event := range events {
		copy(buf[i*sizeofEvent:], (*(*[1<<27 - 1]byte)(unsafe.Pointer(event)))[:sizeofEvent])
	}
	n, err := fd.Write(buf)
	if err != nil {
		logger.Errorf("write %v bytes error:%v", n, err)
	}
}

const (
	DOWN int32 = 1
	UP   int32 = 0
)

var global_close_signal = make(chan bool)

type event_pack struct {
	//表示一个动作 由一系列event组成
	dev_name string
	events   []*evdev.Event
}

func screenCap() {

	handleScreenPNG := func(w http.ResponseWriter, r *http.Request) {
		// start := time.Now()
		c := exec.Command("bash", "-c", "screencap -p")
		stdout, err := c.StdoutPipe()
		if err != nil {
			logger.Error(err)
			return
		}
		if err := c.Start(); err != nil {
			logger.Error(err)
			return
		}
		imageBytes, err := ioutil.ReadAll(stdout)
		if err != nil {
			logger.Error(err)
			return
		}
		if err := c.Wait(); err != nil {
			logger.Error(err)
			return
		}
		// elapsed := time.Since(start) // 计算经过的时间
		// fmt.Println("Code execution time:", elapsed)
		w.Header().Set("Content-Type", "image/png")
		w.Write(imageBytes)
	}
	http.HandleFunc("/screen.png", handleScreenPNG)
	logger.Info("截图服务器 http://0.0.0.0:8888/screen.png")
	http.ListenAndServe(":8888", nil)

}

func main() {

	deviceFile, err := os.OpenFile("/dev/uinput", syscall.O_WRONLY|syscall.O_NONBLOCK, 0660)
	if err != nil {
		logger.Errorf("create u_input touch_screen error:%v", err)
	} else {
		ioctl(deviceFile.Fd(), UISETEVBIT(), uintptr(evdev.EventSync))
		ioctl(deviceFile.Fd(), UISETEVBIT(), uintptr(evdev.EventKey))
		ioctl(deviceFile.Fd(), UISETEVBIT(), uintptr(evdev.EventAbsolute))
		ioctl(deviceFile.Fd(), UISETABSBIT(), uintptr(evdev.AbsoluteX))
		ioctl(deviceFile.Fd(), UISETABSBIT(), uintptr(evdev.AbsoluteY))
		ioctl(deviceFile.Fd(), UISETABSBIT(), uintptr(evdev.AbsoluteZ))
		ioctl(deviceFile.Fd(), UISETABSBIT(), uintptr(evdev.AbsoluteRZ))
		ioctl(deviceFile.Fd(), UISETABSBIT(), uintptr(evdev.AbsoluteGas))
		ioctl(deviceFile.Fd(), UISETABSBIT(), uintptr(evdev.AbsoluteBrake))
		ioctl(deviceFile.Fd(), UISETABSBIT(), uintptr(evdev.AbsoluteHat0X))
		ioctl(deviceFile.Fd(), UISETABSBIT(), uintptr(evdev.AbsoluteHat0Y))
		ioctl(deviceFile.Fd(), UISETKEYBIT(), uintptr(evdev.BtnStart))
		ioctl(deviceFile.Fd(), UISETKEYBIT(), uintptr(evdev.BtnSelect))
		ioctl(deviceFile.Fd(), UISETKEYBIT(), uintptr(evdev.BtnTL))
		ioctl(deviceFile.Fd(), UISETKEYBIT(), uintptr(evdev.BtnTR))
		ioctl(deviceFile.Fd(), UISETKEYBIT(), uintptr(evdev.BtnThumbL))
		ioctl(deviceFile.Fd(), UISETKEYBIT(), uintptr(evdev.BtnThumbR))
		ioctl(deviceFile.Fd(), UISETKEYBIT(), uintptr(evdev.BtnA))
		ioctl(deviceFile.Fd(), UISETKEYBIT(), uintptr(evdev.BtnB))
		ioctl(deviceFile.Fd(), UISETKEYBIT(), uintptr(evdev.BtnX))
		ioctl(deviceFile.Fd(), UISETKEYBIT(), uintptr(evdev.BtnY))
		ioctl(deviceFile.Fd(), UISETKEYBIT(), uintptr(evdev.BtnMode))

		var absMax [absCnt]int32
		absMax[evdev.AbsoluteX] = 65535
		absMax[evdev.AbsoluteY] = 65535
		absMax[evdev.AbsoluteZ] = 65535
		absMax[evdev.AbsoluteRZ] = 65535
		absMax[evdev.AbsoluteGas] = 1023
		absMax[evdev.AbsoluteBrake] = 1023
		absMax[evdev.AbsoluteHat0X] = 1
		absMax[evdev.AbsoluteHat0Y] = 1

		var absMin [absCnt]int32
		absMin[evdev.AbsoluteX] = 0
		absMin[evdev.AbsoluteY] = 0
		absMin[evdev.AbsoluteZ] = 0
		absMin[evdev.AbsoluteRZ] = 0
		absMin[evdev.AbsoluteGas] = 0
		absMin[evdev.AbsoluteBrake] = 0
		absMin[evdev.AbsoluteHat0X] = -1
		absMin[evdev.AbsoluteHat0Y] = -1

		uiDev := UinputUserDev{
			Name: toUInputName([]byte("Xbox Wireless Controller(uinput)")),
			ID: InputID{
				BusType: 0,
				Vendor:  randUInt16Num(0x2000),
				Product: randUInt16Num(0x2000),
				Version: randUInt16Num(0x20),
			},
			EffectsMax: 0,
			AbsMax:     absMax,
			AbsMin:     absMin,
			AbsFuzz:    [absCnt]int32{},
			AbsFlat:    [absCnt]int32{},
		}
		deviceFile.Write(uInputDevToBytes(uiDev))
		createDevice(deviceFile)
		logger.Info("已创建虚拟手柄 Xbox Wireless Controller(uinput)")
		ev_sync := evdev.Event{Type: 0, Code: 0, Value: 0}

		go screenCap()

		listen, err := net.ListenUDP("udp", &net.UDPAddr{
			IP:   net.IPv4(0, 0, 0, 0),
			Port: 8889,
		})
		if err != nil {
			logger.Errorf("udp error : %v", err)
			return
		}
		defer listen.Close()

		recv_ch := make(chan []byte)
		go func() {
			for {
				var buf [1024]byte
				n, _, err := listen.ReadFromUDP(buf[:])
				if err != nil {
					break
				}
				recv_ch <- buf[:n]
			}
		}()
		logger.Infof("已准备接收远程事件 udp:0.0.0.0:%d", 8889)
		for {
			select {
			case <-global_close_signal:
				return
			case pack := <-recv_ch:
				// logger.Debugf("%v", pack)
				event_count := int(pack[0])
				for i := 0; i < event_count; i++ {
					event := &evdev.Event{
						Type:  evdev.EventType(uint16(binary.LittleEndian.Uint16(pack[8*i+1 : 8*i+3]))),
						Code:  uint16(binary.LittleEndian.Uint16(pack[8*i+3 : 8*i+5])),
						Value: int32(binary.LittleEndian.Uint32(pack[8*i+5 : 8*i+9])),
					}
					write_events := make([]*evdev.Event, 0)
					write_events = append(write_events, event)
					write_events = append(write_events, &ev_sync)
					sendEvents(deviceFile, write_events)
				}
			}
		}
	}

}
