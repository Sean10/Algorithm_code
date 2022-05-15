

from selenium import webdriver


class Pic:
    def __init__(self):
        self.brower = webdriver.Chrome()
        self.brower.set_window_size(800, 600)
        self.brower.get("https://live.bilibili.com/23058701")


    def capture_pic(self, name):
        ret = self.brower.save_screenshot(f"/data/{name}.png")
        if ret:
            print(f"succeed to save {name}.png")
        else:
            print(f"fail to save {name}.png")

    def quit(self):
        self.brower.quit()
