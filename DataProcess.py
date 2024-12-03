#DataProcess.py
from Init import config_manager


def process_line(line):
    """解析一行数据并计算磁场值"""
    try:
        parts = line.split("\t")
        if len(parts) != 5:
            raise ValueError("数据格式错误")

        # 提取数据并计算磁场
        mag1_fre = float(parts[0])
        mag2_fre = float(parts[1])  # 修正此处错误的变量名
        voltage1 = float(parts[2])
        voltage2 = float(parts[3])
        serial_number = int(parts[4])

        mag1 = mag1_fre / config_manager.rb87_ggr
        mag2 = mag2_fre / config_manager.rb87_ggr

        return {
            "Mag1": mag1,
            "Mag2": mag2,
            "Voltage1": voltage1,
            "Voltage2": voltage2,
            "SerialNumber": serial_number
        }
    except ValueError as e:
        print(f"解析数据失败: {e}, 数据行: {line}")
    return None


def process_period_data(data, func):
    """
    对一个时间段的数据列表进行统计处理。

    参数:
        data (list): 包含多个 JSON 数据的列表，每个元素是字典，键为 'Mag1', 'Mag2', 'Voltage1', 'Voltage2', 'SerialNumber'。
        func (callable): 一个函数，可以是 max, min, statistics.mean 或其他函数。

    返回:
        dict: 包含处理结果的 JSON 数据。
    """
    if not data:
        print("数据列表为空，无法处理")
        return {}

    try:
        result = {}

        # 按键提取数据并应用 func
        for key in ["Mag1", "Mag2", "Voltage1", "Voltage2"]:
            values = [entry[key] for entry in data]
            result[key] = func(values)

        # 特殊处理 SerialNumber，返回最后一个值
        result["SerialNumber"] = data[-1]["SerialNumber"]

        return result

    except Exception as e:
        print(f"处理数据时出现错误: {e}")
        return {}
