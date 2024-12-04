# 原子磁力仪数据传输与可视化项目

## 一、项目概述
本项目旨在实现原子磁力仪数据的采集、传输、处理及可视化展示。原子磁力仪通过串口将磁场和工参数据传输给树莓派，树莓派对接收的数据进行解析、处理并打包成JSON格式，随后借助4G模块将数据上传至阿里云物联网平台。阿里云物联网平台会进一步将数据流转至IOT Studio数据可视化平台，最终通过web端和移动端进行显示，方便用户查看和分析数据。同时，可视化平台提供了一些便捷的功能，如设定数据上传频率、滤波方式，以及启动或关闭数据上传等操作。

## 二、项目架构及代码模块介绍

### （一）整体架构
- **数据采集层**：原子磁力仪负责测量磁场和相关工参数据，并通过串口将这些原始数据发送出去。
- **数据处理与传输层**：树莓派作为中间处理设备，接收原子磁力仪传来的数据，进行解析、处理和上传操作。通过与4G模块配合，将处理好的数据发送至阿里云物联网平台。
- **数据流转与可视化层**：阿里云物联网平台接收树莓派上传的数据，并按照设定规则将数据流转至IOT Studio数据可视化平台。该可视化平台对流转过来的数据进行处理和展示，提供给用户在web端和移动端查看数据的界面，且支持相关参数设置和数据上传控制功能。

### （二）代码模块介绍

#### 1. `Config.py`
- **功能概述**：此文件主要用于管理项目的各种配置参数，为其他模块提供必要的配置信息。
- **主要类及属性**：
    - `ConfigManager`类：
        - 初始化一系列与项目配置相关的属性，包括设备连接相关属性（如`product_key`、`device_name`、`device_secret`、`client_id`等），用于在阿里云物联网平台等环境中标识产品、设备以及进行认证等操作。
        - 定义了多个用于与阿里云物联网平台进行消息交互的主题（如`post_thing_topic`、`post_reply_thing_topic`、`set_thing_topic`、`set_reply_thing_topic`等），明确了数据发布、回复以及设置等操作的消息通道。
        - 还设置了其他一些与项目运行相关的常量，如`host`、`port`、`serial_port`、`baudrate`、`rb87_ggr`、`filter_types`、`output_json_path`、`tls_crt`、`keep_alive`等，分别涉及到网络连接、串口通信、数据处理等方面的配置。
    - `VariableManager`类：
        - 负责对项目中的变量进行管理，包括变量的初始化（通过`initialize_variables`方法），设置了一些默认的变量值（如`Switch`、`WorkMode`、`FilterType`等）以及对应的转换表（如`switch_table`、`work_mode_table`、`filter_type_functions`等）。
        - 提供了检查变量是否存在（`is_variable_present`方法）、获取变量值（`get_variable_value`方法）、设置变量值（`get_variable_value`方法）以及获取变量的转换值（`get_converted_value`方法）等功能。

#### 2. `IOT.py`
- **功能概述**：实现了`IoTClientManager`类，该类作为物联网（IOT）客户端管理器，负责处理与物联网平台之间的连接、消息收发以及设备属性变更等相关操作，采用单例模式确保在整个项目中只有一个实例存在。
- **主要类及方法**：
    - `IoTClientManager`类：
        - 通过重写`__new__`方法实现单例模式，保证在整个项目运行过程中只有一个`IoTClientManager`实例被创建。
        - 在`__init__`方法中，接收`config_manager`和`sys_vars`作为参数，初始化一系列实例属性，包括`client`（MQTT客户端对象）、`auth_info`（用于存储连接参数）、`time_stamp`、`post_payload`（用于处理发布消息的负载）和`set_reply_payload`（用于处理设置回复消息的负载）等，并调用`_initialize_mqtt_client`方法完成MQTT客户端的初始化操作。
        - `_initialize_mqtt_client`方法：完成MQTT客户端的初始化，包括计算连接所需的签名（通过`auth_info.calculate_sign`方法），设置客户端的用户名和密码，配置TLS等，并建立MQTT连接（通过`_connect_to_mqtt`方法），同时订阅相关主题（通过`subscribe_topic`方法）。
        - `_on_connect`方法：处理MQTT连接成功或失败的情况，根据返回的错误代码打印相应的提示信息。
        - `_on_message`方法：处理接收到的消息，解码消息内容，判断消息主题是否为设置设备属性相关主题，如果是则调用`_process_property_change`方法处理设备属性变更。
        - `_process_property_change`方法：尝试解析接收到的消息负载为JSON格式，根据解析结果设置系统变量的值，并发布设置回复消息和发布状态消息（通过`publish_set_reply_message`和`publish_post_message`方法）。
        - `subscribe_topic`方法：用于订阅指定的主题，若未指定主题则默认订阅`config_manager.post_reply_thing_topic`，并打印出已订阅主题的提示信息。
        - `publish_post_message`方法：用于发布消息到指定的主题（`config_manager.post_thing_topic`），将传入的参数打包成符合要求的负载（通过`post_payload.package_payload`方法）后发布，并打印出已发布消息的提示信息。
        - `publish_set_reply_message`方法：用于发布确认消息到指定的主题（`config_manager.set_reply_thing_topic`），将传入的ID打包成符合要求的负载（通过`set_reply_payload.package_payload`方法）后发布，并打印出已发布确认消息的提示信息。
        - `get_client`方法：返回MQTT客户端对象，以便在其他地方进行进一步的操作。

#### 3. `Raspi.py`
- **功能概述**：主要用于获取树莓派（Raspberry Pi）的各种系统信息，如CPU温度、CPU使用率、RAM使用率等，并提供了将这些信息汇总为一个系统信息字典的功能。通过定义`RaspiInfo`类，采用单例模式确保在整个项目中只有一个实例来获取和管理这些系统信息，方便其他模块调用获取相关数据。
- **主要类及方法**：
    - `RaspiInfo`类：
        - 通过重写`__new__`方法实现单例模式，保证在整个项目运行过程中只有一个`RaspiInfo`实例用于获取树莓派的系统信息。
        - `_initialize`方法：目前主要用于打印“初始化工参成功”的提示信息，可根据项目后续需求在该方法中添加其他必要的初始化内容。
        - `get_cpu_temperature`方法：用于获取树莓派CPU的温度信息，尝试打开`/sys/class/thermal/thermal_zone0/temp`文件，读取其中的内容并转换为摄氏度后返回整数结果，若未找到该文件则打印相应错误提示信息并返回`None`。
        - `get_cpu_usage`方法：用于获取树莓派CPU的使用率，通过获取1分钟平均负载并转换为整数百分比后返回，若获取过程中出现异常则打印相应错误提示信息并返回`None`。
        - `get_ram_usage`方法：用于获取树莓派RAM的使用率，通过读取`/proc/meminfo`文件，解析其中的内容，计算出已用内存和总内存的比例并转换为整数百分比后返回，若获取过程中出现异常则打印相应错误提示信息并返回`None`。
        - `get_system_info`方法：获取系统信息，包括当前时间、CPU温度、CPU使用率、RAM使用率等，并将这些信息汇总成一个系统信息字典后返回。

#### 4. `Serial.py`
- **功能概述**：在整个项目中负责处理与串口通信相关的操作，主要围绕从串口读取数据以及对串口连接的初始化和关闭等功能。通过`MagnetometerReader`类实现了对串口的配置管理和数据读取功能，以便与外部设备（如磁力计等可能通过串口连接的设备）进行数据交互。
- **主要类及方法**：
    - `MagnetometerReader`类：
        - 在`__init__`方法中，接收`config_manager`作为参数，初始化一系列与串口相关的实例属性（如`serial_port`、`baudrate`、`rb87_ggr`、`filer_types`等）以及`serial_connection`（初始化为`None`），并调用`initialize_serial`方法自动初始化串口。
        - `initialize_serial`方法：负责初始化串口连接，根据配置参数使用`serial.Serial`函数创建串口连接对象，如果成功创建则打印出串口已打开的提示信息，若无法打开串口则打印相应错误提示信息并退出程序。
        - `read_data`方法：用于从已经初始化好的串口读取一行数据，检查串口连接对象的`in_waiting`属性，若有数据可读取则读取并处理后返回，若没有数据可读取或读取过程中出现异常则返回`None`，并打印出相应的错误提示信息。
        - `close`方法：用于关闭已经打开的串口连接，检查串口连接对象是否存在且处于打开状态，若满足条件则关闭串口并打印出串口已关闭的提示信息。

#### 5. `MqttParams.py`
- **功能概述**：在整个项目与阿里云IoT平台的通信过程中起着至关重要的作用，定义了三个主要的类：`Connect_Params`、`Post_Params`和`Set_Reply_Params`，分别用于处理MQTT客户端连接参数的计算、发布消息的负载打包以及设置回复消息的负载打包等操作，以满足阿里云IoT平台对消息格式和认证的要求。
- **主要类及方法**：
    - `Connect_Params`类：
        - 在`__init__`方法中，初始化`mqttClientId`、`mqttUsername`和`mqttPassword`等实例属性为 空字符串。
        - `calculate_sign`方法：根据传入的产品标识、设备名称、设备密钥、客户端ID和时间戳等参数，按照特定的算法构建`mqttClientId`和`mqttUsername`的值，并使用HMAC-SHA1进行签名，将生成的签名结果设置为`mqttPassword`的值，以满足阿里云IoT平台的认证要求。
    - `Post_Params`类：
        - 在`__init__`方法中，初始化`PostJson`为空字典。
        - `package_payload`方法：接受设备属性数据作为输入，使用随机数生成唯一的请求ID，设置`PostJson`的其他属性（如`version`、`params`、`method`等），最后将`PostJson`打包成JSON格式的字符串并返回，用于发布消息到阿里云IoT平台。
    - `Set_Reply_Params`类：
        - 在`__init__`方法中，初始化`SetReplyJson`为空字典。
        - `package_payload`方法：接受ID作为输入，设置`SetReplyJson`的各项属性（如`id`、`code`、`data`、`message`、`version`等），最后将`SetReplyJson`打包成JSON格式的字符串并返回，用于发布确认消息到阿里云IoT平台。

#### 6. `DataProcess.py`
- **功能概述**：主要负责对项目中的数据进行处理操作，包括解析单行数据以及对一个时间段内的数据列表进行统计处理等。
- **主要函数**：
    - `process_line`函数：
        - 用于解析一行数据并根据配置信息计算磁场值等相关数据。接受一行数据作为输入，按照特定格式（以制表符分隔）拆分并解析，提取各数据字段的值，通过与`Config.py`中`ConfigManager`的`rb87_ggr`参数进行计算得到磁场值等信息，最终将处理结果以字典形式返回。若数据格式错误或解析过程中出现异常，会打印错误信息并返回`None`。
    - `process_period_data`函数：
        - 对一个时间段内的多个JSON数据组成的列表进行统计处理。接受一个数据列表和一个可调用函数作为输入，针对列表中每个数据的特定键值提取数据并应用传入的函数进行统计计算，最后将处理结果以字典形式返回。若数据列表为空或处理过程中出现异常，会打印错误信息并返回`{}`.

#### 7. `Init.py`
- **功能概述**：在整个项目中扮演着初始化的关键角色，负责导入项目中各个重要模块所需的类，并完成这些类的实例化操作，从而为后续项目的运行搭建起基础框架。
- **实例化操作**：
    - 导入`Config.py`中的`ConfigManager`和`VariableManager`类、`IOT.py`中的`IoTClientManager`类、`Raspi.py`中的`RaspiInfo`类以及`Serial.py`中的`MagnetometerReader`类。
    - 分别完成这些类的实例化操作，创建了`config_manager`、`sys_vars`、`device`、`serial`、`raspi`等实例，为后续各模块协同工作提供了基础。同时，打印出“系统初始化完成”的提示信息，表明初始化工作已顺利完成。

#### 8. `main.py`
- **功能概述**：是整个项目的主程序入口点，协调了各个模块的功能，通过循环执行一系列操作来实现数据的读取、处理和发布等核心功能，同时能够对一些异常情况进行处理，确保系统在启动、运行和关闭过程中的稳定性和安全性。
- **主要函数**：
    - `main`函数：
        - 作为主函数，首先打印出“系统启动中...”的提示信息。然后在一个无限循环中执行以下操作：
            - 每次循环开始时，创建一个空的`data_buffer`列表，用于暂存读取和解析后的数据。
            - 通过`sys_vars.get_converted_value("Switch")`检查系统开关状态，如果开关为开启状态，则执行以下操作：
                - 调用`device.publish_post_message(raspi.get_system_info())`发布树莓派的系统信息到相关平台。
                - 使用`serial.read_data()`读取串口数据，如果读取到有效数据，则对该数据进行解析（通过`DataProcess.process_line(line)`函数），如果解析成功，则将解析后的数据添加到`data_buffer`列表中。
            - 接着，通过判断`(time.time() - start_time) * 1000 >= sys_vars.get_converted_value("WorkMode")`来检查是否达到了根据工作模式设定的周期时间。如果达到周期时间，则执行以下数据处理和发布操作：
                - 调用`DataProcess.process_period_data(data_buffer, sys_vars.get_converted_value("FilterType"))`对暂存在`data_buffer`中的数据按照当前设定的滤波类型进行统计处理，得到处理后的有效数据payload。
                - 如果处理后的payload不为空，则调用`device.publish_post_message(payload)`发布处理后的数据，并清空`data_buffer`列表，重置计时器（将`start_time`重新设置为当前时间）。
            - 最后，在每次循环结束时，加入适当的延时（通过`time.sleep(1)`），避免CPU占用过高。
        - 当遇到`KeyboardInterrupt`异常时，打印出“系统关闭中...”的提示信息，表示用户手动中断了系统运行。当遇到其他异常情况时，打印出相应的错误提示信息。在程序结束时，无论何种情况，都会调用`serial.close()`关闭串口连接，并打印出“系统已安全退出”的提示信息。

## 三、使用说明
1. **硬件连接**：
    - 确保原子磁力仪与树莓派通过串口线正确连接，并且串口参数设置正确（如波特率、数据位、停止位等与原子磁力仪的设置匹配）。
    - 将4G模块与树莓派进行正确的网络连接，确保能够正常通信。
2. **代码部署**：
    - 将上述各个代码文件按照各自的功能需求部署到相应的设备或平台上。例如，`Config.py`、`IOT.py`、`Raspi.py`、`Serial.py`、`MqttParams.py`、`DataProcess.py`、`Init.py`、`main.py`等文件应部署在树莓派上（具体根据实际项目架构和需求可能会有微调）。对于阿里云物联网平台相关的配置，可通过其管理控制台或相关API进行设置（如涉及到`Config.py`中定义的一些产品密钥、设备名称等配置信息的录入等）。对于IOT Studio数据可视化平台相关的设置，需在该可视化平台的开发环境中进行操作（如根据项目展示需求选择合适的可视化组件、设置数据上传频率、滤波方式等参数）。
3. **平台配置**：
    - 在阿里云物联网平台上，根据项目需求完成数据主题、订阅关系、消息路由等配置工作，确保数据能够顺利流转到IOT Studio数据可视化平台。这可能涉及到对`Config.py`中定义的一些主题相关属性（如`post_thing_topic`、`post_reply_thing_topic`、`set_thing_topic`、`set_reply_thing_topic`等）的正确设置和使用。
    - 在IOT Studio数据可视化平台上，根据数据展示需求，选择合适的可视化组件，完成布局和配置工作。同时，利用平台提供的功能设置接口，设定好数据上传频率、滤波方式等参数。
4. **运行与监控**：
    - 启动各个设备和平台上的相关程序和服务。首先启动原子磁力仪进行数据采集，然后树莓派开始接收、解析和上传数据，接着阿里云物联网平台进行数据流转，最后IOT Studio数据可视化平台进行数据展示。在运行过程中，可以通过查看各个设备和平台的日志信息。
