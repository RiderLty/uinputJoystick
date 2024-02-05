from interface import winController , WIN_KEY as KEY

if __name__ == "__main__":
    print("test...")
    print(winController)
    for k in KEY:
        print(k.value)
    wc = winController()
    # wc.click(KEY.KEY_A)
    
    wc.mouseWheel(10)