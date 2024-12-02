import sys
import zipfile
import os
import shutil  # Для копирования файлов
import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime

class ShellEmulator:
    def __init__(self, master, virtual_fs_path):
        self.master = master
        self.base_virtual_fs_path = virtual_fs_path  # Базовая директория виртуальной файловой системы
        self.current_directory = virtual_fs_path  # Текущая рабочая директория
        self.master.title(r"Avatark's Terminal")

        self.log_area = scrolledtext.ScrolledText(master, wrap=tk.WORD)
        self.log_area.pack(fill=tk.BOTH, expand=True)

        # Поле для ввода команд
        self.command_entry = tk.Entry(master, width=50)
        self.command_entry.pack(side=tk.LEFT, padx=5, pady=5)

        # Кнопка для отправки команды
        self.submit_button = tk.Button(master, text="Ввод", command=self.submit_command)
        self.submit_button.pack(side=tk.LEFT, padx=5, pady=5)

    def execute_command(self, command):
        command = command.strip()
        self.log_area.insert(tk.END, f"> {command}\n")

        if command == "exit":
            self.master.destroy()  # Закрытие всего окна приложения
        elif command.startswith("ls"):
            self.handle_ls(command)
        elif command.startswith("cd"):
            self.change_directory(command)
        elif command == "date":
            self.show_date()
        elif command.startswith("cp"):
            self.copy_file(command)
        elif command == "pwd":
            self.show_current_directory()
        else:
            self.log_area.insert(tk.END, f"Command not found: {command}\n")

    def change_directory(self, command):
        parts = command.split()
        if len(parts) < 2:
            self.log_area.insert(tk.END, "Usage: cd <directory>\n")
            return

        new_directory = parts[1]
        new_path = os.path.join(self.current_directory, new_directory)

        if os.path.isdir(new_path):
            self.current_directory = new_path
            self.log_area.insert(tk.END, f"Changed directory to: {self.current_directory}\n")
        else:
            self.log_area.insert(tk.END, f"Directory not found: {new_directory}\n")

    def handle_ls(self, command):
        parts = command.split()
        directory = self.current_directory

        if len(parts) > 1:
            if parts[1] == "-l":
                if len(parts) > 2:
                    directory = os.path.join(self.base_virtual_fs_path, parts[2])
                self.list_files_long(directory)
            else:
                directory = os.path.join(self.base_virtual_fs_path, parts[1])
                self.list_files(directory)
        else:
            self.list_files(directory)

    def list_files(self, directory):
        try:
            files = os.listdir(directory)
            self.log_area.insert(tk.END, f"Files in {directory}:\n")
            for file in files:
                self.log_area.insert(tk.END, f"{file}\n")
        except FileNotFoundError:
            self.log_area.insert(tk.END, f"Directory not found: {directory}\n")
        except PermissionError:
            self.log_area.insert(tk.END, f"Permission denied: {directory}\n")
        except Exception as e:
            self.log_area.insert(tk.END, f"Error listing files: {e}\n")

    def list_files_long(self, directory):
        try:
            files = os.listdir(directory)
            self.log_area.insert(tk.END, f"Detailed files in {directory}:\n")
            for file in files:
                full_path = os.path.join(directory, file)
                file_info = os.stat(full_path)
                file_size = file_info.st_size
                self.log_area.insert(tk.END, f"{file}\tSize: {file_size} bytes\n")
        except FileNotFoundError:
            self.log_area.insert(tk.END, f"Directory not found: {directory}\n")
        except PermissionError:
            self.log_area.insert(tk.END, f"Permission denied: {directory}\n")
        except Exception as e:
            self.log_area.insert(tk.END, f"Error listing files: {e}\n")

    def show_date(self):
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_area.insert(tk.END, f"Current date and time: {current_date}\n")

    def copy_file(self, command):
        parts = command.split()
        if len(parts) != 3:
            self.log_area.insert(tk.END, "Usage: cp <source> <destination>\n")
            return

        source = parts[1]
        destination = parts[2]
        source_path = os.path.join(self.current_directory, source)
        destination_path = os.path.join(self.current_directory, destination)

        try:
            shutil.copy(source_path, destination_path)
            self.log_area.insert(tk.END, f"Copied {source} to {destination}\n")
        except FileNotFoundError:
            self.log_area.insert(tk.END, f"File not found: {source}\n")
        except PermissionError:
            self.log_area.insert(tk.END, f"Permission denied: {source}\n")
        except Exception as e:
            self.log_area.insert(tk.END, f"Error copying file: {e}\n")

    def show_current_directory(self):
        self.log_area.insert(tk.END, f"Current directory: {self.current_directory}\n")

    def submit_command(self):
        command = self.command_entry.get()
        self.execute_command(command)
        self.command_entry.delete(0, tk.END)  # Очистка поля ввода

    def run_startup_script(self, script_path):
        if not os.path.isfile(script_path):
            self.log_area.insert(tk.END, f"Startup script not found: {script_path}\n")
            return

        with open(script_path, 'r') as script_file:
            commands = script_file.readlines()
            for cmd in commands:
                self.execute_command(cmd.strip())

def extract_zip(zip_path, extract_to):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
    except FileNotFoundError:
        print(f"ZIP file not found: {zip_path}")

def main(zip_path, startup_script):
    extract_dir = "file_system"  # Директория для извлечения
    os.makedirs(extract_dir, exist_ok=True)
    extract_zip(zip_path, extract_dir)

    root = tk.Tk()
    emulator = ShellEmulator(root, extract_dir)  # Передаем путь к виртуальной файловой системе
    emulator.run_startup_script(os.path.join(extract_dir, startup_script))
    root.mainloop()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python emulator.py <path_to_zip> <startup_script>")
        sys.exit(1)

    zip_file_path = sys.argv[1]
    startup_script_name = sys.argv[2]
    main(zip_file_path, startup_script_name)