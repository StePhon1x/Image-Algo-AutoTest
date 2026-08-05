import numpy as np
from PIL import Image
import os
import subprocess
import time

# 1. 获取项目根路径
script_file = os.path.abspath(__file__)
src_python_dir = os.path.dirname(script_file)
src_dir = os.path.dirname(src_python_dir)
project_root = os.path.dirname(src_dir)

def generate_test_cases(target_dir):
    os.makedirs(target_dir, exist_ok=True)
    cases = {
        "black": (1024, 1024, 0),
        "white": (1024, 1024, 255),
        "huge": (8000, 8000, 128),  # C++ 1001错误
        "odd_width": (1025, 1024, 128), # C++ 1002 blur错误
    }
    for name, (w, h, val) in cases.items():
        img = np.full((h, w, 3), val, dtype=np.uint8)
        Image.fromarray(img).save(f"{target_dir}/{name}.jpg")
    # 损坏测试图
    Image.new("RGB", (100, 100)).save(f"{target_dir}/corrupt_test.jpg")

def run_benchmark(exe_path, input_path, output_path, algo):
    with Image.open(input_path) as img:
        w, h = img.size
    cmd = [exe_path, input_path, output_path, algo, str(w), str(h)]
    start = time.perf_counter()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=False,
            timeout=5,
        )
        stdout = result.stdout.decode("utf-8", errors="ignore").strip()
        stderr = result.stderr.decode("utf-8", errors="ignore").strip()
        duration = time.perf_counter() - start
        status = "SUCCESS"
        if result.returncode != 0:
            status = "CRASH (SegFault)" if result.returncode < 0 else "ERROR (Logic)"
        return {
            "status": status,
            "exit_code": result.returncode,
            "time": f"{duration:.4f}s",
            "stderr": stderr,
            "stdout": stdout,
            "file": os.path.basename(input_path),
            "algo": algo
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "TIMEOUT",
            "exit_code": -1,
            "time": ">5s",
            "stderr": "Process killed",
            "stdout": "",
            "file": os.path.basename(input_path),
            "algo": algo
        }