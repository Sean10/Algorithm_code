import cv2
import numpy as np
import pytesseract

def preprocess_image(image_path):
    # 读取图像
    img = cv2.imread(image_path)
    # 转换为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 应用高斯模糊
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    # 应用自适应阈值
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    return thresh

def find_sudoku_grid(preprocessed_img):
    # 寻找轮廓
    contours, _ = cv2.findContours(preprocessed_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # 找到最大的轮廓（假设是数独网格）
    max_area = 0
    sudoku_contour = None
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > max_area:
            max_area = area
            sudoku_contour = contour
    
    # 获取数独网格的边界框
    x, y, w, h = cv2.boundingRect(sudoku_contour)
    return x, y, w, h

def extract_digits(preprocessed_img, x, y, w, h):
    # 提取数独网格
    sudoku_grid = preprocessed_img[y:y+h, x:x+w]
    # 计算每个单元格的大小
    cell_height = h // 9
    cell_width = w // 9
    
    # 创建9x9的数组来存储识别的数字
    sudoku_array = np.zeros((9, 9), dtype=int)
    
    for i in range(9):
        for j in range(9):
            # 提取单个单元格
            cell = sudoku_grid[i*cell_height:(i+1)*cell_height, j*cell_width:(j+1)*cell_width]
            # 使用Tesseract OCR识别数字
            digit = pytesseract.image_to_string(cell, config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789')
            # 如果识别出数字，则存储到数组中
            if digit.strip().isdigit():
                sudoku_array[i][j] = int(digit)
    
    return sudoku_array

def process_sudoku_image(image_path):
    preprocessed_img = preprocess_image(image_path)
    x, y, w, h = find_sudoku_grid(preprocessed_img)
    sudoku_array = extract_digits(preprocessed_img, x, y, w, h)
    return sudoku_array
