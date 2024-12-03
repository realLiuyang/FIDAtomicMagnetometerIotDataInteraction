#Init.py
from Config import ConfigManager, VariableManager
from IOT import IoTClientManager
from Raspi import RaspiInfo
from Serial import MagnetometerReader

# 配置管理器实例化
config_manager = ConfigManager()

# 变量管理器实例化
sys_vars = VariableManager()

# 设备客户端管理器实例化
device = IoTClientManager(config_manager, sys_vars)

# 磁力计读取器实例化
serial = MagnetometerReader(config_manager)

# 树莓派信息实例化
raspi = RaspiInfo()

# 简单日志输出，确认系统已初始化
print("系统初始化完成")
