import subprocess
import time

def free_port(port: int = 8000):
    try:
        res = subprocess.run(["netstat", "-ano"], capture_output=True, text=True)
        target = f":{port}"
        killed = False
        for line in res.stdout.splitlines():
            if target in line and "LISTENING" in line:
                parts = line.strip().split()
                if parts:
                    pid = parts[-1]
                    try:
                        subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
                        killed = True
                    except Exception:
                        pass
        if killed:
            time.sleep(1.0)
    except Exception:
        pass

if __name__ == "__main__":
    free_port(8000)
