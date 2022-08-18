from PyQt5 import QtCore
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import csv
import os


def all_device_url() -> list:
    if os.path.isfile("deviceUrl.txt"):
        with open("deviceID.txt", "r") as id_file:
            id_list = id_file.readlines()
    else:
        with open('deviceUrl.txt', 'w') as device_id_file:
            device_id = "62d4e63300ab8c03e700193f"
            device_id_file.write(device_id)
            id_list = [device_id]
    return id_list


def time_interval():
    """ get time interval from txt """
    if os.path.isfile("time(min).txt"):
        with open('time(min).txt', 'r') as timeinterval_file:
            timeinterval = timeinterval_file.read()
    else:
        with open('time(min).txt', 'w') as timeinterval_file:
            timeinterval = "5"
            timeinterval_file.write(timeinterval)
    return time.sleep(int(timeinterval) * 60)


class Robot:
    def __init__(self, mainframe):
        self.mainframe = mainframe
        self._translate = QtCore.QCoreApplication.translate
        self.unifi_url = "https://unifi.ui.com"
        self.driver = None

    def set(self):
        """ chrome setting """
        chrome_options = Options()
        # chrome_options.add_argument('--headless')  # 啟動Headless 無介面
        # chrome_options.add_argument('--disable-gpu')  # 關閉GPU 避免某些系統或是網頁出錯
        self.driver = webdriver.Chrome('./chromedriver', options=chrome_options)

    def get_unifi_url(self) -> bool:
        """ go to unifi and check internet"""
        try:
            self.driver.get(self.unifi_url)
            return True
        except Exception as e:
            print(e)
            print("網路無連線")
            return False

    def login_in(self, account: str, password: str) -> bool:
        """ login to unifi """
        self.driver.find_element(By.NAME, "username").send_keys(account)
        self.driver.find_element(By.NAME, "password").send_keys(password)
        self.driver.find_element(By.NAME, "password").submit()
        self.driver.implicitly_wait(3)
        try:
            self.driver.find_element(By.ID, "unifi-portal-styles")
            return True
        except Exception as e:
            print(e)
            print("登入失敗")
            return False

    def login_result(self, status: bool):
        """ show login result """
        if status:
            print(234234)
            self.mainframe_display_status(True)
            print(777777777)

            self.mainframe.child_window.load_label.setText(self._translate("Form", "登入成功"))
        else:
            self.mainframe.child_window.load_label.setText(self._translate("Form", "登入失敗"))
            self.mainframe.pushButton.setEnabled(True)

    def start(self):
        """ start get temperature and humidity data """
        device_url_list = all_device_url()
        for device_url in device_url_list:
            self.driver.get(device_url)
            self.get_data_and_save()
            time.sleep(5)
        time_interval()

    def mainframe_display_status(self, status: bool):
        """ after internet check display """
        self.mainframe.accout_label.close()
        self.mainframe.password_label.close()
        self.mainframe.account_lineEdit.close()
        self.mainframe.password_lineEdit.close()
        self.mainframe.pushButton.close()

        if not status:
            self.mainframe.child_window.close()
            self.mainframe.status_info_label.setText(self._translate("Form", "未連接上網路，關閉後再試一次"))

        self.mainframe.status_info_label.show()

    def get_data_and_save(self):
        """ get data and save it as .csv """
        humidity = self.driver.find_elements(By.CSS_SELECTOR,
                                             value="span[class='SensorReadingsState__ChipText-sc-1ygwv1j-2 cFlQgU']")[
            2].text
        temperature = self.driver.find_elements(By.CSS_SELECTOR,
                                                value="span[class='SensorReadingsState__ChipText-sc-1ygwv1j-2 cFlQgU']"
                                                )[3].text
        location = self.driver.find_element(By.CSS_SELECTOR,
                                            value="span[class='text-base__bIyDk3C7 text-size-caption__bIyDk3C7 "
                                                  "text-light-header__bIyDk3C7 truncate__bIyDk3C7 "
                                                  "text-weight-normal__bIyDk3C7 "
                                                  "primaryHeading__bIyDk3C7 undefined']").text

        filename = f"{os.getcwd()}/{str(datetime.now().date())}.csv"
        if not os.path.isfile(filename):
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['時間', '地點', '濕度', '溫度'])

        with open(filename, 'a+', newline='') as csvfile:
            writer = csv.writer(csvfile)
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow([now, humidity, temperature, location])

    def refresh_token(self, account: str, password: str):
        """ refresh token by login again """
        self.driver.delete_all_cookies()
        self.driver.get(self.unifi_url)
        self.driver.find_element(By.NAME, "username").send_keys(account)
        self.driver.find_element(By.NAME, "password").send_keys(password)
        self.driver.find_element(By.NAME, "password").submit()
        time.sleep(10)
