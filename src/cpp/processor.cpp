#include <iostream>
#include <string>
#include <thread>
#include <chrono>

using namespace std;

// 模拟算法处理函数
bool processImage(string input, string output, string algo, int width, int height) {
    cout << "[INFO] 开始处理图片: " << input << endl;
    cout << "[INFO] 分辨率: " << width << "x" << height << " | 算法: " << algo << endl;

    // --- 故意埋下的“坑” 1：尺寸限制 ---
    if (width > 5000 || height > 5000) {
        cerr << "[ERROR] 错误代码 1001: 不支持超大尺寸图片处理！" << endl;
        return false;
    }

    // --- 故意埋下的“坑” 2：模拟段错误 (Segmentation Fault) ---
    if (input.find("corrupt") != string::npos) {
        cout << "[WARNING] 检测到损坏的输入文件标记..." << endl;
        int* ptr = nullptr;
        *ptr = 42; // 触发段错误，测试脚本是否能捕获崩溃
    }

    // 模拟算法耗时（高斯模糊比灰度化慢）
    int delay = (algo == "blur") ? 1000 : 200;
    this_thread::sleep_for(chrono::milliseconds(delay));

    // --- 故意埋下的“坑” 3：特定算法在特定条件下失败 ---
    if (algo == "blur" && width % 2 != 0) {
        cerr << "[ERROR] 错误代码 1002: 高斯模糊仅支持偶数宽度的图片！" << endl;
        return false;
    }

    cout << "[SUCCESS] 处理完成，已保存至: " << output << endl;
    return true;
}

int main(int argc, char* argv[]) {
    // 预期参数: ./processor [input] [output] [algo] [width] [height]
    if (argc < 6) {
        cerr << "用法: " << argv[0] << " <输入> <输出> <算法:gray/blur> <宽> <高>" << endl;
        return 1;
    }

    string input = argv[1];
    string output = argv[2];
    string algo = argv[3];
    int width = stoi(argv[4]);
    int height = stoi(argv[5]);

    if (processImage(input, output, algo, width, height)) {
        return 0; // 成功
    } else {
        return 1; // 业务逻辑失败
    }
}




