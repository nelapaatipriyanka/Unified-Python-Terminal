#!/usr/bin/env python3
"""
Unified Python Terminal:
- Supports direct commands + NLP commands
- Maintains history with timestamp
- Windows & Linux compatible
- Added CPU, Memory, and Processes monitoring
- Added confirmation messages for file/folder operations
"""

import os
import subprocess
import re
from pathlib import Path
from datetime import datetime

try:
    import readline
    READLINE_AVAILABLE = True
except ImportError:
    READLINE_AVAILABLE = False

# For system monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

HISTORY_FILE = os.path.join(os.getcwd(), "terminal_history.txt")

def safe_print(*args, **kwargs):
    try:
        print(*args, **kwargs)
    except Exception as e:
        print(f"Print error: {e}")

class UnifiedTerminal:
    def __init__(self):
        self.history = []
        self.load_history()
        if READLINE_AVAILABLE:
            readline.parse_and_bind("tab: complete")
            readline.set_completer(self.completer)

        # NLP patterns
        self.nlp_patterns = {
            r'create file (\S+)': 'touch {0}',
            r'create folder (\S+)': 'mkdir {0}',
            r'delete file (\S+)': 'rm {0}',
            r'remove file (\S+)': 'rm {0}',
            r'rename file (\S+) to (\S+)': 'mv {0} {1}',
            r'move (\S+) to (\S+)': 'mv {0} {1}',
            r'copy (\S+) to (\S+)': 'cp {0} {1}',
            r'show contents of (\S+)': 'cat {0}',
            r'list directory (\S+)': 'ls {0}',
            r'go to directory (\S+)': 'cd {0}',
            r'current directory': 'pwd',
            r'clear screen': 'clear',
            r'exit': 'exit',
            r'quit': 'quit',
            r'help': 'help'
        }

    # ---------------- History ----------------
    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r') as f:
                    self.history = [line.strip() for line in f.readlines()]
            except Exception as e:
                safe_print(f"Error loading history: {e}")

    def save_history(self, command):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] {command}"
        self.history.append(entry)
        try:
            with open(HISTORY_FILE, 'a') as f:
                f.write(entry + "\n")
        except Exception as e:
            safe_print(f"Error saving history: {e}")

    # ---------------- NLP Parsing ----------------
    def parse_nlp(self, command):
        cmd = command.lower().strip()
        for pattern, template in self.nlp_patterns.items():
            match = re.match(pattern, cmd)
            if match:
                groups = match.groups()
                return template.format(*groups)
        return command

    # ---------------- Tab completion ----------------
    def completer(self, text, state):
        commands = ['ls','cd','pwd','mkdir','rmdir','rm','touch','mv','cp','cat',
                    'echo','clear','history','help','exit','quit',
                    'cpu','memory','processes']
        matches = [c for c in commands if c.startswith(text)]
        return matches[state] if state < len(matches) else None

    # ---------------- Command Execution ----------------
    def execute(self, command):
        if not command.strip():
            return
        self.save_history(command)
        command = self.parse_nlp(command)
        parts = command.strip().split()
        cmd = parts[0].lower()
        args = parts[1:]

        try:
            if cmd == 'ls':
                return self.cmd_ls(args)
            elif cmd == 'pwd':
                return self.cmd_pwd()
            elif cmd == 'cd':
                return self.cmd_cd(args)
            elif cmd == 'mkdir':
                return self.cmd_mkdir(args)
            elif cmd == 'rmdir':
                return self.cmd_rmdir(args)
            elif cmd == 'rm':
                return self.cmd_rm(args)
            elif cmd == 'touch':
                return self.cmd_touch(args)
            elif cmd == 'mv':
                return self.cmd_mv(args)
            elif cmd == 'cp':
                return self.cmd_cp(args)
            elif cmd == 'cat':
                return self.cmd_cat(args)
            elif cmd == 'echo':
                return self.cmd_echo(args)
            elif cmd == 'history':
                return self.cmd_history(args)
            elif cmd == 'clear':
                os.system('cls' if os.name=='nt' else 'clear')
                return ""
            elif cmd == 'cpu':
                return self.cmd_cpu()
            elif cmd == 'memory':
                return self.cmd_memory()
            elif cmd == 'processes':
                return self.cmd_processes()
            elif cmd in ['exit','quit']:
                return "exit"
            else:
                return self.system_command(command)
        except Exception as e:
            return f"Error: {e}"

    # ---------------- Commands ----------------
    def normalize_path(self, path):
        return os.path.abspath(os.path.expanduser(path))

    def cmd_ls(self, args):
        path = self.normalize_path(args[0]) if args else os.getcwd()
        try:
            entries = sorted(os.listdir(path))
            return "\n".join(entries) if entries else "(empty)"
        except Exception as e:
            return f"ls error: {e}"

    def cmd_pwd(self):
        return os.getcwd()

    def cmd_cd(self, args):
        if not args:
            return "cd: missing argument"
        path = self.normalize_path(args[0])
        if not os.path.exists(path):
            return f"cd: '{path}' does not exist"
        if not os.path.isdir(path):
            return f"cd: '{path}' is not a directory"
        os.chdir(path)
        return f"Changed directory to '{path}'"

    def cmd_mkdir(self, args):
        if not args:
            return "mkdir: missing argument"
        output = []
        for path in args:
            path = self.normalize_path(path)
            os.makedirs(path, exist_ok=True)
            output.append(f"Directory '{path}' created successfully")
        return "\n".join(output)

    def cmd_rmdir(self, args):
        if not args:
            return "rmdir: missing argument"
        output = []
        for path in args:
            path = self.normalize_path(path)
            if os.path.isdir(path):
                try:
                    os.rmdir(path)
                    output.append(f"Directory '{path}' removed successfully")
                except OSError:
                    output.append(f"rmdir: '{path}' not empty")
            else:
                output.append(f"rmdir: '{path}' not a directory")
        return "\n".join(output)

    def cmd_rm(self, args):
        if not args:
            return "rm: missing operand"
        output = []
        for path in args:
            path = self.normalize_path(path)
            if os.path.isfile(path):
                os.remove(path)
                output.append(f"File '{path}' removed successfully")
            elif os.path.isdir(path):
                output.append(f"rm: '{path}' is a directory (use rmdir)")
            else:
                output.append(f"rm: '{path}' not found")
        return "\n".join(output)

    def cmd_touch(self, args):
        if not args:
            return "touch: missing file operand"
        output = []
        for file in args:
            path = self.normalize_path(file)
            open(path, 'a').close()
            output.append(f"File '{path}' created successfully")
        return "\n".join(output)

    def cmd_mv(self, args):
        if len(args) < 2:
            return "mv: missing source/destination"
        src, dest = self.normalize_path(args[0]), self.normalize_path(args[1])
        os.rename(src, dest)
        return f"'{src}' renamed/moved to '{dest}' successfully"

    def cmd_cp(self, args):
        if len(args) < 2:
            return "cp: missing source/destination"
        import shutil
        src, dest = self.normalize_path(args[0]), self.normalize_path(args[1])
        if os.path.isdir(src):
            shutil.copytree(src, dest)
            return f"Directory '{src}' copied to '{dest}' successfully"
        else:
            shutil.copy2(src, dest)
            return f"File '{src}' copied to '{dest}' successfully"

    def cmd_cat(self, args):
        if not args:
            return "cat: missing file operand"
        output = []
        for file in args:
            file = self.normalize_path(file)
            if os.path.isfile(file):
                with open(file, 'r') as f:
                    output.append(f.read())
            else:
                output.append(f"cat: '{file}' not found")
        return "\n".join(output)

    def cmd_echo(self, args):
        line = " ".join(args)
        if ">" in line:
            if ">>" in line:
                parts = line.split(">>")
                file = self.normalize_path(parts[1].strip())
                with open(file, "a") as f:
                    f.write(parts[0].strip() + "\n")
                return f"Text appended to '{file}' successfully"
            else:
                parts = line.split(">")
                file = self.normalize_path(parts[1].strip())
                with open(file, "w") as f:
                    f.write(parts[0].strip() + "\n")
                return f"Text written to '{file}' successfully"
        return line

    def cmd_history(self, args):
        if args and args[0] == "-c":
            self.history = []
            open(HISTORY_FILE, 'w').close()
            return "History cleared"
        return "\n".join(self.history[-50:])

    # ---------------- System Monitoring ----------------
    def cmd_cpu(self):
        if not PSUTIL_AVAILABLE:
            return "psutil module not installed"
        usage = psutil.cpu_percent(interval=1, percpu=True)
        result = "\n".join([f"CPU {i}: {u}%" for i, u in enumerate(usage)])
        return result

    def cmd_memory(self):
        if not PSUTIL_AVAILABLE:
            return "psutil module not installed"
        mem = psutil.virtual_memory()
        return f"Total: {mem.total//1024**2} MB\nUsed: {mem.used//1024**2} MB\nFree: {mem.available//1024**2} MB\nPercentage: {mem.percent}%"

    def cmd_processes(self):
        if not PSUTIL_AVAILABLE:
            return "psutil module not installed"
        processes = []
        for p in psutil.process_iter(['pid', 'name', 'username']):
            processes.append(f"{p.info['pid']:>5} {p.info['name'][:20]:<20} {p.info['username']}")
        return "\n".join(processes[:50])  # Show top 50 processes

    # ---------------- System Commands ----------------
    def system_command(self, command):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            output = result.stdout.strip()
            if result.stderr:
                output += "\n" + result.stderr.strip()
            return output
        except Exception as e:
            return f"System command error: {e}"

    # ---------------- Main Loop ----------------
    def run(self):
        print("Unified Python Terminal (Supports NLP & Direct Commands)")
        print("Type 'exit' to quit, 'help' for command list")
        while True:
            try:
                cmd = input(f"{os.getcwd()}$ ")
                output = self.execute(cmd)
                if output == "exit":
                    break
                if output is not None and output.strip() != "":
                    print(output, flush=True)
            except KeyboardInterrupt:
                print("\nUse 'exit' or 'quit' to exit")
            except EOFError:
                print("\nGoodbye!")
                break

if __name__ == "__main__":
    terminal = UnifiedTerminal()
    terminal.run()
