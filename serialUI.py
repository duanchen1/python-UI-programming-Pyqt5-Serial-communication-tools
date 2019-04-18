# -*- coding: utf-8 -*-

"""
Module implementing MainWindow.
"""

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QTimer
from Ui_serialwindow import *
from time import sleep
import serial
import serial.tools.list_ports


class MainWindow(QMainWindow, Ui_MainWindow):
    """
    Class documentation goes here.
    """

    def __init__(self, parent=None):
        """
        Constructor

        @param parent reference to the parent widget
        @type QWidget
        """
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        # 串口初始化
        self.myserial = serial.Serial()
        self.send_num = 0
        self.receive_num = 0

        # 显示发送与接收的字符数量
        bardis = '发送：' + '{:d}'.format(self.send_num) + '  接收:' + '{:d}'.format(self.receive_num)
        self.bar.setText(bardis)

        self.refresh()

        # 波特率
        self.bandrate.addItem('115200')
        self.bandrate.addItem('57600')
        self.bandrate.addItem('56000')
        self.bandrate.addItem('38400')
        self.bandrate.addItem('19200')
        self.bandrate.addItem('14400')
        self.bandrate.addItem('9600')
        self.bandrate.addItem('4800')
        self.bandrate.addItem('2400')
        self.bandrate.addItem('1200')

        # 数据位
        shujuwei = list(serial.Serial.BYTESIZES)
        shujuwei.reverse()
        for i in shujuwei:
            self.databit.addItem(str(i))

        # 停止位
        for i in serial.Serial.STOPBITS:
            self.stopbit.addItem(str(i))

        # 校验位
        for i in serial.Serial.PARITIES:
            self.crcbit.addItem(i)

        self.openserial.setCheckable(True)

        # 实例化一个定时器
        self.timer = QTimer(self)

        self.timer_send = QTimer(self)
        # 定时器调用读取串口接收数据
        self.timer.timeout.connect(self.recv)

        # 定时发送
        self.timer_send.timeout.connect(self.on_send_clicked)

    @pyqtSlot(str)
    def on_serialnum_currentIndexChanged(self, p0):
        """
        Slot documentation goes here.

        @param p0 DESCRIPTION
        @type str
        """
        # TODO: not implemented yet
        # raise NotImplementedError
        self.myserial.port = p0

    @pyqtSlot(str)
    def on_bandrate_currentIndexChanged(self, p0):
        """
        Slot documentation goes here.

        @param p0 DESCRIPTION
        @type str
        """
        # TODO: not implemented yet
        self.myserial.baudrate = int(p0)

    @pyqtSlot(str)
    def on_databit_currentIndexChanged(self, p0):
        """
        Slot documentation goes here.

        @param p0 DESCRIPTION
        @type str
        """
        if (int(p0) - self.myserial.stopbits < 3.5):
            self.databit.setCurrentIndex(3)
            QMessageBox.critical(self, '串口设置错误', '请检查数据位与停止位参数，数据位已复位')
        else:
            self.myserial.bytesize = int(p0)

    @pyqtSlot(str)
    def on_stopbit_currentIndexChanged(self, p0):
        """
        Slot documentation goes here.

        @param p0 DESCRIPTION
        @type str
        """
        if (self.myserial.bytesize - float(p0) < 3.5):
            self.stopbit.setCurrentIndex(0)
            QMessageBox.critical(self, '串口设置错误', '请检查数据位与停止位参数,停止位已复位')
        else:
            self.myserial.stopbits = self.myserial.stopbits = float(p0)

    @pyqtSlot(str)
    def on_crcbit_currentIndexChanged(self, p0):
        """
        Slot documentation goes here.

        @param p0 DESCRIPTION
        @type str
        """
        pass

    @pyqtSlot()
    def on_openserial_clicked(self):
        """
        Slot documentation goes here.
        """
        self.myserial.port = self.serialnum.currentText()
        self.myserial.baudrate = int(self.bandrate.currentText())
        self.myserial.bytesize = int(self.databit.currentText())
        self.myserial.parity = self.crcbit.currentText()
        self.myserial.stopbits = float(self.stopbit.currentText())
        if not self.myserial.isOpen():
            try:
                # 输入参数'COM13',115200
                #self.myserial = serial.Serial(self.serialnum.currentText(), int(self.bandrate.currentText()),timeout=0.2)
                self.myserial.open()
                print(self.myserial)
            except:
                QMessageBox.critical(self, 'pycom', '没有可用的串口或当前串口被占用')
                self.openserial.setChecked(False)
                return None
            # 字符间隔超时时间设置
            if self.myserial.isOpen():
                self.myserial.interCharTimeout = 0.001
                # 1ms的测试周期
                self.timer.start(2)
                self.openserial.setText("关闭串口")

        else:
            # 关闭定时器，停止读取接收数据
            self.timer_send.stop()
            self.timer.stop()

            try:
                # 关闭串口
                self.myserial.close()
            except:
                QMessageBox.critical(self, 'pycom', '关闭串口失败')
                return None

            self.myserial = serial.Serial()
            self.timer_sendbox.setChecked(False)
            self.openserial.setChecked(False)
            self.openserial.setText("打开串口")
            print('close!')

    @pyqtSlot()
    def on_flushserial_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        if self.myserial.isOpen():
            QMessageBox.critical(self, 'pycom', '请关闭串口再点击刷新')
        else:
            self.refresh()

    @pyqtSlot()
    def on_clear_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.recedisplay.clear()
        self.send_num = 0
        self.receive_num = 0
        bardis = '发送：' + '{:d}'.format(self.send_num) + '  接收:' + '{:d}'.format(self.receive_num)
        self.bar.setText(bardis)

    @pyqtSlot()
    def on_timer_sendbox_clicked(self):
        """
        Slot documentation goes here.
        """
        if(self.timer_sendbox.checkState()):
            time = self.timer_send_interval.text()
            try:
                time_val = int(time)
            except ValueError:
                self.timer_sendbox.setChecked(False)
                QMessageBox.critical(self,"时间间隔错误","请输入正确的时间间隔")
                return None
            if time_val == 0:
                self.timer_sendbox.setChecked(False)
                QMessageBox.critical(self, "时间间隔错误", "时间间隔必须大于零")
                return None
            self.timer_send.start(time_val)
        else:
            self.timer_send.stop()


        pass

    @pyqtSlot()
    def on_send_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        if self.myserial.isOpen():
            input_s = self.sendbuffer.text()
            if input_s != "":
                # 发送字符
                if self.newline.checkState():
                    # 发送新行
                    input_s = input_s + '\r\n'
                input_s = input_s.encode('UTF-8')

                # 发送数据
                try:
                    num = self.myserial.write(input_s)
                except:
                    self.timer_send.stop()
                    self.timer.stop()

                    # 串口拔出错误，关闭定时器
                    self.myserial.close()
                    self.myserial = serial.Serial()

                    # 设置为打开按钮状态
                    self.openserial.setChecked(False)
                    self.openserial.setText("打开串口")
                    print('serial error send!')
                    return None

                self.send_num = self.send_num + num
                bardis = '发送：' + '{:d}'.format(self.send_num) + '  接收:' + '{:d}'.format(self.receive_num)
                self.bar.setText(bardis)
                # print('send!')
            else:
                print('none data input!')

        else:
            # 停止发送定时器
            self.timer_send.stop()
            QMessageBox.critical(self, 'pycom', '请打开串口')

    @pyqtSlot()
    def on_newline_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        pass

    @pyqtSlot()
    def on_recedisplay_textChanged(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.recedisplay.moveCursor(self.recedisplay.textCursor().End)

    def refresh(self):
        # 查询可用的串口
        plist = list(serial.tools.list_ports.comports())

        if len(plist) <= 0:
            print("No used com!");
            self.bar.setText('没有可用的串口')


        else:
            # 把所有的可用的串口输出到comboBox中去
            self.serialnum.clear()

            for i in range(0, len(plist)):
                plist_0 = list(plist[i])
                self.serialnum.addItem(str(plist_0[0]))

    def recv(self):
        try:
            num = self.myserial.inWaiting()
        except:
            self.timer_send.stop()
            self.timer.stop()
            # 串口拔出错误，关闭定时器
            self.myserial.close()
            self.myserial = serial.Serial()

            # 设置为打开按钮状态
            self.openserial.setChecked(False)
            self.openserial.setText("打开串口")
            return None
        if (num > 0):
            # 有时间会出现少读到一个字符的情况，所以循环读直到没有异常，一般中文字符会出错，英文字符没问题
            bufferdata = self.myserial.read(num)
            while(True):
                try:
                    data = bufferdata.decode('UTF-8')
                    break
                except:
                    sleep(0.05)
                    num = self.myserial.inWaiting()
                    bufferdata = bufferdata+self.myserial.read(num)
                    print(bufferdata)

            # 调试打印输出数据
            # print(data)
            num = len(bufferdata)
            # 十六进制显示

            # 把字符串显示到窗口中去
            self.recedisplay.insertPlainText(data)


            # 统计接收字符的数量
            self.receive_num = self.receive_num + num
            bardis = '发送：' + '{:d}'.format(self.send_num) + '  接收:' + '{:d}'.format(self.receive_num)
            self.bar.setText(bardis)

        else:
            # 此时回车后面没有收到换行，就把回车发出去
            pass


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())
