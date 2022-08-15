from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QFrame, QMessageBox
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import sys
import time
import csv
import os

class UiForm(object):
    def setupUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setObjectName("Form")
        Form.resize(454, 177)
        Form.setWindowTitle(_translate("Form", "UniFi Login"))

        self.thread = {}
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(170, 120, 93, 28))
        self.pushButton.setObjectName("pushButton")

        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(20, 5, 51, 61))
        self.label.setObjectName("label")

        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(20, 55, 51, 61))
        self.label_2.setObjectName("label")

        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setGeometry(QtCore.QRect(100, 70, 293, 28))
        self.label_3.setObjectName("label")

        self.lineEdit = QtWidgets.QLineEdit(Form)
        self.lineEdit.setGeometry(QtCore.QRect(80, 20, 351, 30))
        self.lineEdit.setObjectName("lineEdit")

        self.lineEdit_2 = QtWidgets.QLineEdit(Form)
        self.lineEdit_2.setGeometry(QtCore.QRect(80, 70, 351, 30))
        self.lineEdit_2.setObjectName("lineEdit")

        self.labeledit()
        self.lineedit_init()
        self.check_input_func()
        self.buttonedit()
        QtCore.QMetaObject.connectSlotsByName(Form)

    def buttonedit(self):
        _translate = QtCore.QCoreApplication.translate
        self.pushButton.setText(_translate("Form", "登入"))
        self.pushButton.clicked.connect(self.buttonclick)

    def labeledit(self):
        _translate = QtCore.QCoreApplication.translate
        self.label.setText(_translate("Form", "帳號："))
        self.label_2.setText(_translate("Form", "密碼："))
        self.label_3.setText(_translate("Form", "程式運行中，請勿關閉此視窗"))

    def lineedit_init(self):
        self.lineEdit.setPlaceholderText('請輸入Email')
        self.lineEdit_2.setPlaceholderText('請輸入密碼')
        self.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit.textChanged.connect(self.check_input_func)
        self.lineEdit_2.textChanged.connect(self.check_input_func)

    def check_input_func(self):
        if self.lineEdit.text() and self.lineEdit_2.text():
            self.pushButton.setEnabled(True)
        else:
            self.pushButton.setEnabled(False)


    def message_box(self, result):
        if result:
            QMessageBox.information(self, 'Information', 'Log in Successfully!')
        else:
            QMessageBox.critical(self, 'Wrong', 'Wrong Username or Password!')

    def buttonclick(self):
        email = self.lineEdit.text()
        password = self.lineEdit_2.text()
        self.thread[1] = ThreadClass(email=email, password=password)
        self.thread[1].start()
        self.pushButton.setEnabled(False)


class ThreadClass(QtCore.QThread):
    any_signal = QtCore.pyqtSignal(int)

    def __init__(self, email, password, parent=None):
        super(ThreadClass, self).__init__(parent)
        self.email = email
        self.password = password

    def run(self):
        Email = self.email
        Password = self.password

        Url = "https://unifi.ui.com"
        DeviceUrl = f"{Url}/device/E063DA8A50B5000000000474FE440000000004A664EE000000005E1FCB67:26626280/protect/devices/"

        # chrome setting
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # 啟動Headless 無頭
        chrome_options.add_argument('--disable-gpu')  # 關閉GPU 避免某些系統或是網頁出錯

        driver = webdriver.Chrome('./chromedriver', options=chrome_options)
        try:
            driver.get(Url)
        except:
            _translate = QtCore.QCoreApplication.translate
            mainFrame.label.close()
            mainFrame.label_2.close()
            mainFrame.lineEdit.close()
            mainFrame.lineEdit_2.close()
            mainFrame.pushButton.close()
            mainFrame.label_3.setText(_translate("Form", "未連接上網路，關閉後再試一次"))
            mainFrame.label_3.show()
            time.sleep(60)

        # login unifi
        driver.find_element(By.NAME, "username").send_keys(Email)
        driver.find_element(By.NAME, "password").send_keys(Password)
        driver.find_element(By.NAME, "password").submit()

        driver.implicitly_wait(5)

        # getdata in this page
        def GetData(device_id):
            global humidity, temperature, location
            try:
                humidity = driver.find_elements(By.CSS_SELECTOR,
                                                value="span[class='SensorReadingsState__ChipText-sc-1ygwv1j-2 cFlQgU']")[
                    2].text
                temperature = driver.find_elements(By.CSS_SELECTOR,
                                                value="span[class='SensorReadingsState__ChipText-sc-1ygwv1j-2 cFlQgU']")[
                    3].text
                location = driver.find_element(By.CSS_SELECTOR,
                                            value="span[class='text-base__bIyDk3C7 text-size-caption__bIyDk3C7 "
                                                    "text-light-header__bIyDk3C7 truncate__bIyDk3C7 text-weight-normal__bIyDk3C7 "
                                                    "primaryHeading__bIyDk3C7 undefined']").text
                print(humidity)
            except:
                print(f"deviceID: {device_id} isn't exist !")

            now = datetime.now()
            date = now.date()
            filename = f"{os.getcwd()}/{str(date)}.csv"
            if not os.path.isfile(filename):
                with open(filename, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['時間', '地點', '濕度', '溫度'])

            with open(filename, 'a+', newline='') as csvfile:
                writer = csv.writer(csvfile)
                time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                writer.writerow([time, location, humidity, temperature])

        try:
            driver.find_element(By.ID, "unifi-portal-styles")
            print("Login success")
            # mainFrame.message_box(result=True)
            #切換為成功
            mainFrame.label.close()
            mainFrame.label_2.close()
            mainFrame.lineEdit.close()
            mainFrame.lineEdit_2.close()
            mainFrame.pushButton.close()
            mainFrame.label_3.show()


            while True:
                try:
                    if os.path.isfile("deviceID.txt"):
                        with open("deviceID.txt", "r") as ID_file:
                            Id = ID_file.readlines()
                            for device_id in Id:
                                driver.get(f"{DeviceUrl}{str(device_id)}")
                                time.sleep(5)
                                GetData(device_id)
                    else:
                        with open('deviceID.txt', 'w') as timeinterval_file:
                            device_id = "62d4e63300ab8c03e700193f"
                            timeinterval_file.write(device_id)

                    # time interval
                    if os.path.isfile("time(min).txt"):
                        with open('time(min).txt', 'r') as timeinterval_file:
                            timeinterval = timeinterval_file.read()
                        time.sleep(int(timeinterval) * 60 - 11)

                    else:
                        with open('time(min).txt', 'w') as timeinterval_file:
                            timeinterval = "1"
                            timeinterval_file.write(timeinterval)
                        time.sleep(int(timeinterval) * 60 - 11)
                except:
                    driver.delete_all_cookies()
                    driver.get(Url)
                    driver.find_element(By.NAME, "username").send_keys(Email)
                    driver.find_element(By.NAME, "password").send_keys(Password)
                    driver.find_element(By.NAME, "password").submit()
                    time.sleep(10)
        except:
            print("Login Fail")
            # mainFrame.message_box(result=True)
            mainFrame.pushButton.setEnabled(True)

        self.any_signal.emit(0)


class MainFrame(QFrame, UiForm):
    def __init__(self, parent=None):
        super(MainFrame, self).__init__(parent) # 調用父類把子類對象轉為父類對象
        # 調用介面
        self.setupUi(self)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainFrame = MainFrame()
    mainFrame.show()
    os.system('taskkill /im chromedriver.exe /F')
    os.system('taskkill /im chrome.exe /F')
    sys.exit(app.exec_())
#
