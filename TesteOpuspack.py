import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import serial
import threading
from serial.tools import list_ports

class SerialApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Serial Port Teste Opuspack")

        # Estilo personalizado
        style = ttk.Style()
        style.theme_use('clam')

        # Configurações de cores e fontes
        bg_color = "#f5f5f5"
        fg_color = "#000000"
        accent_color = "#2979ff"
        button_bg_color = "#ffffff"
        connected_button_color = "#4caf50"  # Verde
        disconnected_button_color = "#f44336"  # Vermelho
        button_active_color = "#cccccc"

        style.configure("TFrame", background=bg_color)
        style.configure("TLabel", background=bg_color, foreground=fg_color, font=("Helvetica", 10))
        style.configure("TButton", background=button_bg_color, foreground=fg_color, font=("Helvetica", 10, "bold"))
        style.configure("TCheckbutton", background=bg_color, foreground=fg_color, font=("Helvetica", 10))
        style.configure("TCombobox", font=("Helvetica", 10))
        style.configure("TEntry", font=("Helvetica", 10))

        style.map("TButton",
                  background=[("active", button_active_color), ("pressed", connected_button_color)],
                  foreground=[("active", fg_color), ("!active", fg_color)])

        self.ser = None  # Variável para manter a conexão serial aberta

        # Configurar a GUI com ttk
        self.main_frame = ttk.Frame(root, padding="10 10 10 10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.port_label = ttk.Label(self.main_frame, text="Porta Serial:")
        self.port_label.grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)

        self.port_combo = ttk.Combobox(self.main_frame)
        self.port_combo.grid(row=0, column=1, pady=5, padx=5)

        # Preencher a combobox com as portas disponíveis
        self.update_ports()

        self.baud_label = ttk.Label(self.main_frame, text="Baud Rate:")
        self.baud_label.grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)

        self.baud_entry = ttk.Entry(self.main_frame)
        self.baud_entry.grid(row=1, column=1, pady=5, padx=5)
        self.baud_entry.insert(0, "9600")

        self.connect_button = ttk.Button(self.main_frame, text="Conectar", command=self.toggle_connection)
        self.connect_button.grid(row=2, column=0, columnspan=2, pady=5, padx=5)

        self.devices_frame = ttk.LabelFrame(self.main_frame, text="Dispositivos", padding="10 10 10 10")
        self.devices_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))

        style.configure("TLabelframe.Label", background=bg_color, foreground=accent_color, font=("Helvetica", 12, "bold"))
        style.configure("TLabelframe", background=bg_color)

        self.device_vars = []

        for i in range(8):
            device_var = []
            device_frame = ttk.Frame(self.devices_frame)
            device_frame.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=5)

            device_label = ttk.Label(device_frame, text=f"Device {i + 1}")
            device_label.grid(row=0, column=0, sticky=tk.W, padx=5)

            for j in range(10):
                var = tk.IntVar()
                chk = ttk.Checkbutton(device_frame, text=f"S{j + 1}", variable=var)
                chk.grid(row=0, column=j + 1, padx=2)
                device_var.append(var)

            self.device_vars.append(device_var)

            send_button = ttk.Button(device_frame, text="Enviar", command=lambda i=i: self.send_data(i))
            send_button.grid(row=0, column=11, padx=5)

        self.control_frame = ttk.LabelFrame(self.main_frame, text="Controles", padding="10 10 10 10")
        self.control_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))

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

    def toggle_connection(self):
        if self.ser and self.ser.is_open:
            self.close_serial_connection()
        else:
            self.open_serial_connection()

    def open_serial_connection(self):
        port = self.port_combo.get()
        baud = int(self.baud_entry.get())

        try:
            self.ser = serial.Serial(port, baud, timeout=1)
            self.connect_button.config(text="Desconectar")
            messagebox.showinfo("Sucesso", f"Conectado à porta: {port}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir a conexão serial: {e}")

    def close_serial_connection(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.connect_button.config(text="Conectar")
            messagebox.showinfo("Sucesso", "Conexão serial fechada.")

    def send_serial_data(self, message):
        try:
            if self.ser and self.ser.is_open:
                self.ser.write(message.encode('utf-8'))
            else:
                messagebox.showerror("Erro", "Conexão serial não está aberta.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao enviar dados: {e}")

    def send_data(self, device_index):
        message = f"D{device_index + 1}"
        for var in self.device_vars[device_index]:
            message += '1' if var.get() == 1 else '0'
        threading.Thread(target=self.send_serial_data, args=(message,)).start()

    def send_control_command(self, command):
        threading.Thread(target=self.send_serial_data, args=(command,)).start()

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

    def on_closing(self):
        self.close_serial_connection()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SerialApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
