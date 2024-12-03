#Serial.py
import serial  # 串口通信库


class MagnetometerReader:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        # 初始化串口
        self.serial_port = self.config_manager.serial_port
        self.baudrate = self.config_manager.baudrate
        self.rb87_ggr = self.config_manager.rb87_ggr
        self.filer_types = self.config_manager.filter_types
        # self.data_buffer = []  # 存储当前周期内的数据
        self.serial_connection = None

        # 在初始化时调用 initialize_serial 来自动初始化串口
        self.initialize_serial()

    def initialize_serial(self):
        """初始化串口连接"""
        try:
            self.serial_connection = serial.Serial(
                port=self.serial_port,
                baudrate=self.baudrate,
                timeout=1
            )
            print(f"串口 {self.serial_port} 已打开，波特率 {self.baudrate}")
        except serial.SerialException as e:
            print(f"无法打开串口：{e}")
            exit(1)

    def read_data(self):
        """从串口读取一行数据"""
        try:
            if self.serial_connection.in_waiting > 0:
                line = self.serial_connection.readline().decode("utf-8").strip()
                return line
            return None
        except Exception as e:
            print(f"读取串口数据时出错: {e}")
            return None

    def close(self):
        """关闭串口"""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            print("串口已关闭")
