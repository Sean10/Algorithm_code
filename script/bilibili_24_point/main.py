from Spiders.bilibili_live_barrage import main
from Spiders.capture import Pic
import time

if __name__ == '__main__':
    # main()
    pic = Pic()
    for i in range(20):
        pic.capture_pic(i)
        time.sleep(1)