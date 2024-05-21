import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import serial
import time
from serial.tools import list_ports

class SerialApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Serial Port Teste Opuspack")

        # Configurar a GUI com ttk
        self.main_frame = ttk.Frame(root, padding="10 10 10 10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.port_label = ttk.Label(self.main_frame, text="Porta Serial:")
        self.port_label.grid(row=0, column=0, sticky=tk.W, pady=5)

        self.port_combo = ttk.Combobox(self.main_frame)
        self.port_combo.grid(row=0, column=1, pady=5)

        # Preencher a combobox com as portas disponíveis
        self.update_ports()

        self.baud_label = ttk.Label(self.main_frame, text="Baud Rate:")
        self.baud_label.grid(row=1, column=0, sticky=tk.W, pady=5)

        self.baud_entry = ttk.Entry(self.main_frame)
        self.baud_entry.grid(row=1, column=1, pady=5)
        self.baud_entry.insert(0, "9600")

        self.devices_frame = ttk.LabelFrame(self.main_frame, text="Dispositivos")
        self.devices_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))

        self.device_vars = []

        for i in range(8):
            device_var = []
            device_frame = ttk.Frame(self.devices_frame)
            device_frame.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=5)

            device_label = ttk.Label(device_frame, text=f"Device {i + 1}")
            device_label.grid(row=0, column=0, sticky=tk.W)

            for j in range(10):
                var = tk.IntVar()
                chk = ttk.Checkbutton(device_frame, text=f"S{j + 1}", variable=var)
                chk.grid(row=0, column=j + 1)
                device_var.append(var)

            self.device_vars.append(device_var)

            send_button = ttk.Button(device_frame, text="Enviar", command=lambda i=i: self.send_data(i))
            send_button.grid(row=0, column=11, padx=5)

        self.control_frame = ttk.LabelFrame(self.main_frame, text="Controles")
        self.control_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))

        self.up_button = ttk.Button(self.control_frame, text="▲", command=self.press_up)
        self.up_button.grid(row=0, column=0, padx=5, pady=5)

        self.stop_button = ttk.Button(self.control_frame, text="Stop", command=self.press_stop)
        self.stop_button.grid(row=1, column=0, padx=5, pady=5)

        self.down_button = ttk.Button(self.control_frame, text="▼", command=self.press_down)
        self.down_button.grid(row=2, column=0, padx=5, pady=5)

        self.solenoid1_state = False
        self.solenoid1_button = ttk.Button(self.control_frame, text="Solenoide 1", command=self.toggle_solenoid1)
        self.solenoid1_button.grid(row=3, column=0, padx=5, pady=5)

        self.solenoid2_state = False
        self.solenoid2_button = ttk.Button(self.control_frame, text="Solenoide 2", command=self.toggle_solenoid2)
        self.solenoid2_button.grid(row=3, column=1, padx=5, pady=5)

    def update_ports(self):
        ports = [port.device for port in list_ports.comports()]
        self.port_combo['values'] = ports
        if ports:
            self.port_combo.current(0)

    def send_data(self, device_index):
        port = self.port_combo.get()
        baud = int(self.baud_entry.get())

        try:
            ser = serial.Serial(port, baud, timeout=1)
            time.sleep(2)  # Aguardar a inicialização da conexão

            if ser.is_open:
                # Construir a mensagem para o dispositivo específico
                message = f"D{device_index + 1}"
                for var in self.device_vars[device_index]:
                    message += '1' if var.get() == 1 else '0'
                
                ser.write(message.encode('utf-8'))
               # messagebox.showinfo("Sucesso", f"Dados enviados: {message}")
                ser.close()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao enviar dados: {e}")

    def send_control_command(self, command):
        port = self.port_combo.get()
        baud = int(self.baud_entry.get())

        try:
            ser = serial.Serial(port, baud, timeout=1)
            time.sleep(2)  # Aguardar a inicialização da conexão

            if ser.is_open:
                ser.write(command.encode('utf-8'))
                # messagebox.showinfo("Sucesso", f"Comando enviado: {command}")
                ser.close()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao enviar comando: {e}")

    def press_up(self):
        self.send_control_command("M1")
        self.up_button.state(['pressed'])
        self.down_button.state(['!pressed'])

    def press_stop(self):
        self.send_control_command("M0")
        self.up_button.state(['!pressed'])
        self.down_button.state(['!pressed'])

    def press_down(self):
        self.send_control_command("M2")
        self.down_button.state(['pressed'])
        self.up_button.state(['!pressed'])

    def toggle_solenoid1(self):
        self.solenoid1_state = not self.solenoid1_state
        command = "S11" if self.solenoid1_state else "S10"
        self.send_control_command(command)
        self.solenoid1_button.state(['pressed'] if self.solenoid1_state else ['!pressed'])

    def toggle_solenoid2(self):
        self.solenoid2_state = not self.solenoid2_state
        command = "S21" if self.solenoid2_state else "S20"
        self.send_control_command(command)
        self.solenoid2_button.state(['pressed'] if self.solenoid2_state else ['!pressed'])

if __name__ == "__main__":
    root = tk.Tk()
    app = SerialApp(root)
    root.mainloop()
