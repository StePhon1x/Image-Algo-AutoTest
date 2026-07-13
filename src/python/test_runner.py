import numpy as np
from PIL import Image
import os
import subprocess
import time
import pandas as pd

# 1. 获取当前脚本完整绝对路径
script_file = os.path.abspath(__file__)
# 2. src/python 文件夹
src_python_dir = os.path.dirname(script_file)
# 3. src 文件夹
src_dir = os.path.dirname(src_python_dir)
# 4. 项目根目录
project_root = os.path.dirname(src_dir)

# 1. 数据生成（增加一个触发崩溃的文件）
def generate_test_cases(target_dir):
    os.makedirs(target_dir, exist_ok=True)

    cases = {
        "black": (1024, 1024, 0),
        "white": (1024, 1024, 255),
        "huge": (8000, 8000, 128),  # 触发 C++ 的 1001 错误
        "odd_width": (1025, 1024, 128),  # 触发 C++ 的 1002 错误 (blur 算法时)
    }
    for name, (w, h, val) in cases.items():
        img = np.full((h, w, 3), val, dtype=np.uint8)
        Image.fromarray(img).save(f"{target_dir}/{name}.jpg")

    # 特殊案例：触发段错误的文件
    Image.new("RGB", (100, 100)).save(f"{target_dir}/corrupt_test.jpg")


# 2. 增强执行引擎
def run_benchmark(exe_path, input_path, output_path, algo):
    # 使用 PIL 获取实际宽高传给 C++
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
            # 判断是逻辑错误还是崩溃
            status = "CRASH (SegFault)" if result.returncode < 0 else "ERROR (Logic)"

        return {
            "status": status,
            "exit_code": result.returncode,
            "time": f"{duration:.4f}s",
            "stderr": stderr,
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "TIMEOUT",
            "exit_code": -1,
            "time": ">5s",
            "stderr": "Process killed",
        }


# 3. 汇总运行逻辑
def main():
    # --- 生成带时间戳的任务名称 ---
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    # 拼接完整路径：脚本目录/run_时间戳
    run_dir = os.path.join(project_root, f"run_{timestamp}")
    os.makedirs(run_dir, exist_ok=True)
    # ----------------------------------

    # 测试输入图片放在时间戳文件夹内：run_xxx/test_inputs
    input_dir = os.path.join(run_dir, "test_inputs")
    # 生成测试图片到时间戳目录内
    generate_test_cases(input_dir)

    # exe路径
    exe = os.path.join(project_root, "build", "bin", "processor.exe")
    results = []

    # 测试两种算法
    for algo in ["gray", "blur"]:
        for img_file in os.listdir(input_dir):
            input_p = os.path.join(input_dir, img_file)

            # 输出路径指向run时间戳文件夹
            output_p = os.path.join(run_dir, f"output_{algo}_{img_file}")

            print(f"正在测试: {img_file} | 算法: {algo}...")
            res = run_benchmark(exe, input_p, output_p, algo)

            # 添加额外信息
            res["file"] = img_file
            res["algo"] = algo
            results.append(res)

    # 导出报告
    # --- CSV 报告存入时间戳文件夹 ---
    report_path = os.path.join(run_dir, "test_report.csv")
    df = pd.DataFrame(results)
    df.to_csv(report_path, index=False, encoding="utf-8-sig")

    print(f"\n测试完成! 所有结果已保存至目录: {run_dir}")


if __name__ == "__main__":
    main()
