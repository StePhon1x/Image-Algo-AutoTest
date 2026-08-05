# test_processor.py
import pytest
import os
import time
import pandas as pd
from processor_test_utils import project_root, generate_test_cases, run_benchmark

# ===================== Fixture 全局资源 =====================
@pytest.fixture(scope="session")
def exe_binary():
    # 提供C++程序路径，session级别只初始化一次
    exe_path = os.path.join(project_root, "build", "bin", "processor.exe")
    assert os.path.exists(exe_path), f"可执行文件不存在：{exe_path}"
    return exe_path

@pytest.fixture(scope="session")
def report_store():
    # 根报告目录：项目根目录/test_reports/run_时间戳
    ts = time.strftime("%Y%m%d_%H%M%S")
    run_root = os.path.join(project_root, "test_reports", f"run_{ts}")
    os.makedirs(run_root, exist_ok=True)
    return run_root

@pytest.fixture(scope="session")
def test_image_dir(report_store):
    # 测试原图放在 run_root/inputs 下，共用同一个时间戳文件夹
    img_dir = os.path.join(report_store, "inputs")
    generate_test_cases(str(img_dir))
    return str(img_dir)

@pytest.fixture(scope="session", autouse=True)
def collect_all_results(report_store):
    # 自动收集所有用例结果，测试结束导出CSV
    results = []
    yield results  # 测试执行阶段，用例往list追加数据
    # 所有用例跑完后导出报告
    csv_path = os.path.join(report_store, "test_report.csv")
    df = pd.DataFrame(results)
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"\n===== 测试报告已生成：{csv_path} =====")

# ===================== 测试参数配置 =====================
ALL_ALGOS = ["gray", "blur"]
TEST_IMAGES = [
    "black.jpg",
    "white.jpg",
    "huge.jpg",
    "odd_width.jpg",
    "corrupt_test.jpg"
]

# ===================== 核心测试用例 =====================
@pytest.mark.parametrize("algo", ALL_ALGOS)
@pytest.mark.parametrize("img_name", TEST_IMAGES)
def test_image_process(
    algo,
    img_name,
    exe_binary,
    test_image_dir,
    report_store,
    collect_all_results
):
    # 组装输入输出路径
    input_path = os.path.join(test_image_dir, img_name)
    output_path = os.path.join(report_store, f"output_{algo}_{img_name}")

    # 执行C++程序，获取运行结果
    res = run_benchmark(exe_binary, input_path, output_path, algo)
    collect_all_results.append(res)  # 存入全局结果列表用于导出CSV

    # ========== 自定义业务断言（按需修改） ==========
    # 1. 正常图片不应该超时
    assert res["status"] != "TIMEOUT", f"[{img_name}-{algo}] 执行超时！日志：{res['stderr']}"

    # 2. 黑白标准图应当正常执行成功
    normal_img = ("black.jpg", "white.jpg")
    if img_name in normal_img:
        assert res["status"] == "SUCCESS", \
            f"标准图执行失败 status={res['status']}, code={res['exit_code']}, stderr={res['stderr']}"

    # 3. huge大图、奇数宽图允许逻辑错误，但不能段错误崩溃
    if img_name in ("huge.jpg", "odd_width.jpg"):
        assert "CRASH" not in res["status"], \
            f"边界图发生段错误崩溃！{res['stderr']}"

    # 4. 损坏图片允许报错/崩溃，不做强制成功断言