# 数独求解器

这是一个功能强大的数独求解器，能够从图像中识别数独问题并解决它们。该项目结合了图像处理、光学字符识别（OCR）和高级数独解题算法。

## 功能

* [ ] 从图像中识别数独问题
    * 目前实测不太行, 解析不出正确问题
* [ ] 使用多种数独解题技巧，包括：
  - 基本逻辑推理
  - XY-Wing技巧
  - 回溯算法
- 可视化数独问题和解决方案

## 安装

2. 安装所需的Python库：
   ```
   pip install opencv-python pytesseract numpy
   ```

3. 安装Tesseract OCR（如果尚未安装）。请参考[Tesseract文档](https://github.com/tesseract-ocr/tesseract)进行安装。

## 使用方法

1. 将数独图像放在`image`文件夹中。

2. 在`calc.py`文件中，更新`image_path`变量以指向您的数独图像：
   ```python
   image_path = "image/your_sudoku_image.png"
   ```

3. 运行程序：
   ```
   python calc.py
   ```

4. 程序将显示从图像中识别的数独问题，然后显示解决方案。

## 项目结构

- `calc.py`: 主程序文件，包含数独求解算法和主要逻辑。
- `image_processor.py`: 处理图像识别和数字提取的模块。
- `tests/`: 包含测试文件。
- `image/`: 存放数独图像的文件夹。

## 算法说明

本求解器使用多种技巧来解决数独问题：

1. 简单逻辑：填充唯一候选数。
2. 高级技巧：实现了XY-Wing技巧。
3. 回溯法：当逻辑推理无法完全解决问题时使用。

## Changelog
* 支持从图像识别数独问题并求解 (2024.03.15)
* 实现XY-Wing高级解题技巧 (2024.03.10)
* 支持基本DFS求解数独 (2019.10.20)
