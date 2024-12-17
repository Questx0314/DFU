import tkinter as tk
import serial
import serial.tools.list_ports
import time

class SerialDebugger:
    def __init__(self, master):
        self.master = master
        self.master.title("串口调试器")

        # 串口选择区域
        self.create_serial_selection_ui()

        # 数据发送区域
        self.create_data_send_ui()

        # 接收数据区域
        self.received_text = tk.Text(master, height=15, width=60)
        self.received_text.pack()

        # 串口对象
        self.serial_connection = None

        # 定时更新接收数据
        self.update_receive()

    def create_serial_selection_ui(self):
        """创建串口选择UI"""
        self.port_label = tk.Label(self.master, text="选择串口:")
        self.port_label.pack()

        self.port_list = self.get_serial_ports()
        self.selected_port = tk.StringVar(value=self.port_list[0] if self.port_list else "")
        self.port_menu = tk.OptionMenu(self.master, self.selected_port, *self.port_list)
        self.port_menu.pack()

        self.refresh_button = tk.Button(self.master, text="刷新串口", command=self.refresh_ports)
        self.refresh_button.pack()

    def create_data_send_ui(self):
        """创建数据发送UI"""
        self.send_text = tk.Entry(self.master)
        self.send_text.pack()

        self.send_button = tk.Button(self.master, text="发送", command=self.send_data_from_textbox)
        self.send_button.pack()

        self.jump_button = tk.Button(self.master, text="跳转到 Bootloader", command=self.jump_to_bootloader)
        self.jump_button.pack()

    def get_serial_ports(self):
        """获取可用串口列表"""
        return [port.device for port in serial.tools.list_ports.comports()]

    def refresh_ports(self):
        """刷新串口列表"""
        self.port_list = self.get_serial_ports()
        self.update_port_menu()

    def update_port_menu(self):
        """更新串口下拉菜单"""
        self.port_menu['menu'].delete(0, 'end')
        for port in self.port_list:
            self.port_menu['menu'].add_command(label=port, command=lambda p=port: self.selected_port.set(p))
        message = "串口列表已更新。\n" if self.port_list else "未检测到可用串口。\n"
        self.log_message(message)

    def send_data(self, data):
        """发送字符串数据到串口"""
        try:
            self.open_serial()
            self.serial_connection.write(data.encode())
            self.log_message(f"发送: {data}")
        except Exception as e:
            self.log_message(f"发送失败: {e}")

    def send_data_from_textbox(self):
        """从文本框获取数据并发送"""
        data = self.send_text.get()
        if data:
            self.send_data(data)
            self.send_text.delete(0, tk.END)

    def jump_to_bootloader(self):
        """发送跳转命令到 Bootloader 并重连"""
        try:
            self.open_serial()
            self.serial_connection.write(b"jump")
            self.log_message("发送: jump 命令，准备跳转到 Bootloader...")

            # 重置串口，等待设备重启
            self.serial_connection.reset_input_buffer()
            self.serial_connection.reset_output_buffer()
            self.serial_connection.flush()  # 清理串口缓冲区
            self.serial_connection.close()
            self.serial_connection = None
            self.received_text.insert(tk.END, "串口已关闭，等待设备重启...\n")
            # 延长时间，等待设备重启
            self.master.after(1000, self.reconnect_serial)  # 延长等待时间
        except Exception as e:
            self.log_message(f"跳转失败: {e}")

    def reconnect_serial(self):
        """尝试重新连接串口并检查 Bootloader 响应"""
        try:
            # 重新打开串口
            self.send_data("Hello World")

        except serial.SerialException as e:
            self.received_text.insert(tk.END, f"串口无法打开: {e}\n")
        except Exception as e:
            self.received_text.insert(tk.END, f"重连失败: {e}\n")

    def open_serial(self):
        """打开串口连接"""
        if self.serial_connection is None or not self.serial_connection.is_open:
            self.serial_connection = serial.Serial(self.selected_port.get(), 9600, timeout=1)
            self.log_message(f"串口 {self.selected_port.get()} 已打开")

    def close_serial(self):
        """关闭串口连接"""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            self.serial_connection = None
            self.log_message("串口已关闭")

    def receive_data(self):
        """接收串口数据"""
        try:
            if self.serial_connection and self.serial_connection.in_waiting:
                data = self.serial_connection.read(self.serial_connection.in_waiting).decode()
                self.log_message(f"接收: {data}")
        except Exception as e:
            self.log_message(f"接收失败: {e}")

    def update_receive(self):
        """定时更新接收数据"""
        self.receive_data()
        self.master.after(100, self.update_receive)

    def log_message(self, message):
        """在文本区域显示消息"""
        self.received_text.insert(tk.END, f"{message}\n")
        self.received_text.see(tk.END)  # 滚动到最新消息

if __name__ == "__main__":
    root = tk.Tk()
    app = SerialDebugger(root)
    root.mainloop()
