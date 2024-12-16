# main.py
import tkinter as tk
import serial
import serial.tools.list_ports

class SerialDebugger:
    def __init__(self, master):
        self.master = master
        self.master.title("串口调试器")

        self.port_label = tk.Label(master, text="选择串口:")
        self.port_label.pack()

        self.port_list = [port.device for port in serial.tools.list_ports.comports()]
        self.selected_port = tk.StringVar(value=self.port_list[0])
        self.port_menu = tk.OptionMenu(master, self.selected_port, *self.port_list)
        self.port_menu.pack()

        self.send_text = tk.Entry(master)
        self.send_text.pack()

        self.send_button = tk.Button(master, text="发送", command=self.send_data)
        self.send_button.pack()

        self.jump_button = tk.Button(master, text="跳转", command=self.jump)
        self.jump_button.pack()

        self.received_text = tk.Text(master, height=10, width=50)
        self.received_text.pack()

        self.serial_connection = None

        # 启动接收数据的定时器
        self.update_receive()

    def send_data(self):
        try:
            if self.serial_connection is None:
                self.serial_connection = serial.Serial(self.selected_port.get(), 9600)
                self.received_text.insert(tk.END, f"串口 {self.selected_port.get()} 已打开\n")

            data = self.send_text.get()
            self.serial_connection.write(data.encode())
            self.send_text.delete(0, tk.END)
            self.received_text.insert(tk.END, f"发送: {data}\n")
        except serial.SerialException as e:
            self.received_text.insert(tk.END, f"串口错误: {e}\n")
        except Exception as e:
            self.received_text.insert(tk.END, f"其他错误: {e}\n")

    def jump(self):
        try:
            if self.serial_connection is None:
                self.serial_connection = serial.Serial(self.selected_port.get(), 9600)
                self.received_text.insert(tk.END, f"串口 {self.selected_port.get()} 已打开\n")

            # 发送 "jump" 消息
            jump_message = "jump"
            self.serial_connection.write(jump_message.encode())
            self.received_text.insert(tk.END, f"发送: {jump_message}\n")
            self.serial_connection.close()  # 发送后关闭串口连接
            self.serial_connection = None  # 清空串口连接
        except serial.SerialException as e:
            self.received_text.insert(tk.END, f"串口错误: {e}\n")
        except Exception as e:
            self.received_text.insert(tk.END, f"其他错误: {e}\n")

    def receive_data(self):
        if self.serial_connection and self.serial_connection.is_open and self.serial_connection.in_waiting:
            data = self.serial_connection.read(self.serial_connection.in_waiting)
            self.received_text.insert(tk.END, f"接收: {data.decode()}\n")

    def update_receive(self):
        self.receive_data()  # 调用接收数据方法
        self.master.after(100, self.update_receive)  # 每100毫秒调用一次

if __name__ == "__main__":
    root = tk.Tk()
    app = SerialDebugger(root)
    root.mainloop()