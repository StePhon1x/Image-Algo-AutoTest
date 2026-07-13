# Image-Algo-AutoTest
轻量级图像处理算法自动化回归测试系统。
通过 Python 驱动 C++ 底层算法，自动执行多维度的功能测试、异常捕获与性能回归监控，大幅减少人工校验的工作量。
## 项目背景
C++ 图像处理算法在迭代过程中，长期面临以下几个痛点：
- **人工校验效率低**：每次修改算法逻辑后，需要手动构造图片、执行程序、比对结果
- **崩溃难以捕获**：空指针引用等段错误在命令行下往往一闪而过，容易被忽略
- **性能退化难追踪**：算法耗时随版本变化，缺少自动化记录和回溯手段
本项目以"非侵入式"的测试框架架构，在不修改 C++ 源代码的前提下，系统性地解决上述问题。
## 核心特性
- **非侵入式自动化驱动** — 基于 Python `subprocess` 实现 C++ 被测程序与测试框架的解耦
- **多维测试矩阵** — 覆盖常规图像处理、超大分辨率（触发错误代码 1001）、奇数宽度限制（触发错误代码 1002）、损坏文件导致的段错误（SegFault）等场景
- **性能回归监控** — 微秒级计时，自动记录每种场景的算法耗时
- **结构化测试报告** — 自动聚合测试输入、期望结果、异常流和耗时，输出 `test_report.csv`
- **时间戳隔离** — 每次运行生成独立的时间戳目录，历史记录互不干扰
## 技术栈
| 组件 | 技术 |
|------|------|
| 被测算法 | C++11, CMake |
| 测试驱动 | Python 3.x |
| 核心依赖 | Pillow, NumPy, Pandas |
| 数据生成 | PIL / NumPy 合成图像 |
## 快速开始
### 1. 编译 C++ 组件
```bash
cd src/cpp
mkdir build && cd build
cmake ..
cmake --build .
```
编译后，可执行文件 `processor.exe` 位于 `build/bin/` 目录。
### 2. 安装 Python 依赖
```bash
pip install -r requirements.txt
```
### 3. 运行测试
```bash
python src/python/test_runner.py
```
测试结果将生成在 `run_YYYYMMDD_HHMMSS/` 目录下，包含：
- `test_inputs/` — 本次测试自动生成的测试图片
- `test_report.csv` — 结构化测试报告
## 测试场景说明
处理器 `processor.exe` 内置了三类典型的"埋点错误"，用于验证测试框架的捕获能力：
| 场景 | 触发条件 | 预期捕获 |
|------|----------|----------|
| ERROR 1001 | 图片宽度或高度 > 5000 | 逻辑错误，返回码非零 |
| ERROR 1002 | blur 算法 + 奇数图片宽度 | 逻辑错误，返回码非零 |
| 段错误 | 文件名包含 "corrupt" | 进程崩溃，被标记为 CRASH |
| 正常处理 | 常规尺寸 + 合法参数 | 返回成功 |
## 项目结构
```
Image-Algo-AutoTest/
├── .gitignore
├── LICENSE
├── requirements.txt
├── readme.md           
├── src/
│   ├── cpp/               # C++ 被测算法
│   │   ├── CMakeLists.txt
│   │   └── processor.cpp
│   └── python/            # Python 测试框架
│       └── test_runner.py
├── build/
│   └── bin/
│       └── processor.exe
└── run_*/                 # 自动生成，已配置 gitignore
```
## License
MIT