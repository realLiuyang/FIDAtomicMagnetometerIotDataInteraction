#main.py
import time

import DataProcess
from Init import sys_vars, device, serial, raspi


def main():
    """主函数"""
    print("系统启动中...")

    # 主循环
    try:
        start_time = time.time()  # 获取当前时间
        while True:
            data_buffer = []  # 每次循环时清空缓冲区
            if sys_vars.get_converted_value("Switch"):
                device.publish_post_message(raspi.get_system_info())  # 发布系统信息
                line = serial.read_data()  # 读取串口数据
                if line:
                    parsed_data = DataProcess.process_line(line)  # 解析数据
                    if parsed_data:
                        data_buffer.append(parsed_data)

                # 检查是否达到周期时间，处理并发布数据
                if (time.time() - start_time) * 1000 >= sys_vars.get_converted_value("WorkMode"):

                    payload = DataProcess.process_period_data(data_buffer, sys_vars.get_converted_value("FilterType"))
                    if payload:
                        device.publish_post_message(payload)
                        start_time = time.time()
                        # 清空缓冲区，重置计时器
                        data_buffer.clear()

            time.sleep(1)  # 加入适当的延时，避免CPU占用过高

    except KeyboardInterrupt:
        print("系统关闭中...")
    except Exception as e:
        print(f"运行时错误: {e}")
    finally:
        serial.close()  # 关闭串口连接
        print("系统已安全退出")


if __name__ == "__main__":
    main()
