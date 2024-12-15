import numpy as np
from sympy import symbols, Eq, solve, Symbol, pretty_print, sympify
import pandas as pd
import time
import win32com.client
import pythoncom
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import xlwings as xw
import sys
import logging
import yaml
from pathlib import Path
from sympy.parsing.sympy_parser import parse_expr
import re


def setup_logging(config_path="config.yaml"):
    """设置日志配置"""
    # 默认配置
    default_config = {
        "logging": {
            "console_level": "DEBUG",
            "file_level": "INFO",
            "log_file": "storage_calculator.log",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        }
    }

    # 尝试读取配置文件
    config = default_config
    if Path(config_path).exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
        except Exception as e:
            print(f"读取配置文件失败，使用默认配置: {e}", file=sys.stderr)

    # 创建logger
    logger = logging.getLogger("StorageCalculator")
    logger.setLevel(logging.DEBUG)

    # 日志格式
    formatter = logging.Formatter(config["logging"]["format"])

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, config["logging"]["console_level"]))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件处理器
    file_handler = logging.FileHandler(config["logging"]["log_file"], encoding="utf-8")
    file_handler.setLevel(getattr(logging, config["logging"]["file_level"]))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


# 创建全局logger
logger = setup_logging()


class FormulaWatcher(FileSystemEventHandler):
    def __init__(self, calculator):
        self.calculator = calculator
        self.last_modified = 0
        self.retry_count = 3  # 添加重试次数
        self.retry_delay = 0.5  # 重试延迟（秒）

    def on_modified(self, event):
        if event.src_path.endswith("formulas.yaml"):
            current_time = time.time()
            if current_time - self.last_modified < 1:
                return
            self.last_modified = current_time
            logger.info("检测到配置文件更改，准备重新加载")

            # 添加重试机制
            for attempt in range(self.retry_count):
                try:
                    # 确保文件写入完成
                    time.sleep(self.retry_delay)

                    # 验证文件是否可读且不为空
                    if not os.path.exists(event.src_path):
                        logger.warning(
                            f"配置文件不存在，等待重试 ({attempt + 1}/{self.retry_count})"
                        )
                        continue

                    file_size = os.path.getsize(event.src_path)
                    if file_size == 0:
                        logger.warning(
                            f"配置文件为空，等待重试 ({attempt + 1}/{self.retry_count})"
                        )
                        continue

                    # 尝试读取文件
                    with open(event.src_path, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        if not content:
                            logger.warning(
                                f"配置文件内容为空，等待重试 ({attempt + 1}/{self.retry_count})"
                            )
                            continue

                    # 重新加载配置
                    self.calculator.load_config()

                    # 触发Excel重新计算
                    if hasattr(self.calculator, "_trigger_recalculation"):
                        self.calculator._trigger_recalculation()

                    logger.info("配置重新加载成功")
                    break

                except Exception as e:
                    logger.warning(f"第 {attempt + 1} 次重试失败: {str(e)}")
                    if attempt == self.retry_count - 1:
                        logger.error(
                            f"重新加载配置失败，已达到最大重试次数", exc_info=True
                        )


class UnitConverter:
    """单位转换工具类"""

    # 定义单位换算基数
    BINARY_BASE = 1024  # 二进制单位(Ki, Mi, Gi, Ti, Pi)
    DECIMAL_BASE = 1000  # 十进制单位(K, M, G, T, P)

    # 单位定义
    BINARY_UNITS = [
        (1024**4, "TiB"),
        (1024**3, "GiB"),
        (1024**2, "MiB"),
        (1024**1, "KiB"),
        (1, "B"),
    ]

    DECIMAL_UNITS = [
        (1000**4, "TB"),
        (1000**3, "GB"),
        (1000**2, "MB"),
        (1000**1, "KB"),
        (1, "B"),
    ]

    @classmethod
    def auto_format(cls, value, use_binary=True, precision=2):
        """自动选择合适的单位进行格式化"""
        if value is None:
            return None

        if value == 0:
            return f"0 {'B' if use_binary else 'B'}"

        # 选择单位系统
        units = cls.BINARY_UNITS if use_binary else cls.DECIMAL_UNITS

        # 取绝对值用于比较
        abs_value = abs(value)

        # 找到合适的单位
        for factor, unit in units:
            if abs_value >= factor:
                converted = value / factor
                # 如果转换后的值接近整数，则不显示小数位
                if abs(round(converted) - converted) < 0.01:
                    return f"{int(round(converted))} {unit}"
                return f"{converted:.{precision}f} {unit}"

        return f"{value} {'B' if use_binary else 'B'}"

    @classmethod
    def parse_value(cls, value):
        """解析带单位的值，返回字节数"""
        if value is None:
            return None

        if isinstance(value, (int, float)):
            return float(value)

        value = str(value).strip().upper()
        if not value:
            return None

        # 尝试匹配数字和单位
        match = re.match(r"^([-+]?\d*\.?\d+)\s*([A-Z]*)(?:I?B)?$", value)
        if not match:
            return None

        number, prefix = match.groups()
        number = float(number)

        # 处理无单位情况
        if not prefix:
            return number

        # 构建单位映射
        binary_map = {unit: factor for factor, unit in cls.BINARY_UNITS}
        decimal_map = {unit: factor for factor, unit in cls.DECIMAL_UNITS}

        # 检查是否是二进制单位（以i结尾）
        if "I" in prefix:
            unit = prefix.replace("I", "") + "iB"
            if unit in binary_map:
                return number * binary_map[unit]
        else:
            unit = prefix + "B"
            if unit in decimal_map:
                return number * decimal_map[unit]

        return number

    @classmethod
    def format_value(cls, value, target_unit=None, use_binary=True):
        """格式化数值为指定单位或自动选择单位"""
        if value is None:
            return None

        if target_unit and target_unit.upper() == "%":
            return f"{value * 100:.2f}%"

        # 如果没有指定目标单位，使用自动格式化
        if not target_unit:
            return cls.auto_format(value, use_binary)

        # 处理指定单位的情况
        base = cls.BINARY_BASE if use_binary else cls.DECIMAL_BASE
        units = cls.BINARY_UNITS if use_binary else cls.DECIMAL_UNITS

        # 构建单位映射
        unit_map = {unit: factor for factor, unit in units}

        if target_unit not in unit_map:
            return str(value)

        # 计算转换后的值
        converted = value / unit_map[target_unit]

        # 如果接近整数则返回整数
        if abs(round(converted) - converted) < 0.01:
            return f"{int(round(converted))} {target_unit}"
        return f"{converted:.2f} {target_unit}"


class StorageCalculator:
    def __init__(self, excel_mode=False, formula_file="formulas.yaml"):
        logger.debug("初始化StorageCalculator")
        self.excel_mode = excel_mode
        self.formula_file = formula_file
        self._calculated_values = {}  # 存储计算结果
        self._last_config = None  # 存储上一次的配置用于比较
        self.unit_converter = UnitConverter()

        # 加载配置并初始化
        self.load_config()

        # 设置配置文件监听
        if self.excel_mode:
            self.setup_formula_watcher()

    def _config_has_changed(self, new_config):
        """检查配置是否发生实质性变化"""
        # 处理空配置的情况
        if new_config is None:
            logger.error("新配置为空")
            return False
        if self._last_config is None:
            return True

        try:
            # 检查各个部分的变化
            sections = ["global", "variables", "formulas", "excel"]
            for section in sections:
                if (section in new_config) != (section in self._last_config):
                    logger.debug(f"配置节{section}存在性发生变化")
                    return True
                if (
                    section in new_config
                    and new_config[section] != self._last_config[section]
                ):
                    logger.debug(f"配置节{section}内容发生变化")
                    return True

            return False
        except Exception as e:
            logger.error(f"配置比较出错: {str(e)}")
            return False

    def load_config(self):
        """加载配置文件"""
        try:
            with open(self.formula_file, "r", encoding="utf-8") as f:
                new_config = yaml.safe_load(f)

            # 检查配置是否有效
            if not new_config:
                logger.error("配置文件为空或格式无效")
                return

            # 检查必要的配置节是否存在
            required_sections = ["global", "variables", "formulas"]
            missing_sections = [
                section for section in required_sections if section not in new_config
            ]
            if missing_sections:
                logger.error(f"配置文件缺少必要的节: {', '.join(missing_sections)}")
                return

            # 检查配置是否发生变化
            if not self._config_has_changed(new_config):
                logger.debug("配置未发生变化，跳过重新加载")
                return

            self.config = new_config
            self._last_config = new_config.copy()

            # 加载默认值
            self.load_defaults()
            logger.info("已重新加载默认值配置")

            # 加载变量定义
            self.load_variables()
            logger.info("已重新加载变量定义")

            # 加载公式
            self.load_formulas()
            logger.info("已重新加载公式定义")

            logger.debug("配置加载完成")

        except yaml.YAMLError as e:
            logger.error(f"YAML格式错误: {str(e)}")
        except Exception as e:
            logger.error(f"加载配置文件出错: {str(e)}")

    def _trigger_recalculation(self):
        """触发Excel重新计算"""
        try:
            if hasattr(self, "_current_sheet"):
                logger.info("配置已更新，触发重新计算")
                self._do_calculation(self._current_sheet)
        except Exception as e:
            logger.error(f"触发重新计算失败: {str(e)}", exc_info=True)

    def _do_calculation(self, sheet):
        """保存当前sheet引用并执行计算"""
        self._current_sheet = sheet
        return _do_calculation(sheet)

    def setup_formula_watcher(self):
        """设置公式文件监听"""
        try:
            self.formula_watcher = FormulaWatcher(self)
            self.formula_observer = Observer()
            self.formula_observer.schedule(
                self.formula_watcher,
                path=os.path.dirname(os.path.abspath(self.formula_file)),
                recursive=False,
            )
            self.formula_observer.start()
            logger.debug("公式文件监听已启动")
        except Exception as e:
            logger.error(f"设置公式文件监听失败: {str(e)}")

    def load_defaults(self):
        """加载默认值"""
        defaults = self.config.get("global", {}).get("defaults", {})
        for var, value in defaults.items():
            setattr(self, var, value)
            self._calculated_values[var] = value
        logger.debug(f"已加载默认值: {defaults}")

    def load_variables(self):
        """加载变量定义"""
        self.variables = {}
        for var_name, var_info in self.config.get("variables", {}).items():
            self.variables[var_name] = {
                "description": var_info.get("description", ""),
                "unit": var_info.get("unit", ""),
                "excel_column": var_info.get("excel_column", var_name),
                "can_be_input": var_info.get("can_be_input", False),
            }
        logger.debug(f"已加载变量定义: {list(self.variables.keys())}")

    def load_formulas(self):
        """加载公式定义"""
        self.formulas = {}
        self.excel_columns = {}

        for name, formula_data in self.config.get("formulas", {}).items():
            try:
                # 修改表达式格式以适应sympy解析
                expr_str = formula_data["expression"]
                # 移除等号左边的变量定义，只保留等式右边
                expr_str = expr_str.split("=")[1].strip()

                # 解析公式表达式
                expr = parse_expr(expr_str)

                # 存储公式信息
                self.formulas[name] = {
                    "equation": Eq(Symbol(formula_data["output_variable"]), expr),
                    "description": formula_data["description"],
                    "variables": formula_data["variables"],
                    "output_variable": formula_data["output_variable"],
                    "excel_column": formula_data["excel_column"],
                    "unit": formula_data.get("unit", ""),
                }

                # 注册Excel列映射
                self.excel_columns[formula_data["excel_column"]] = name

                logger.debug(f"已加载公式 {name}: {formula_data['description']}")

            except Exception as e:
                logger.error(f"解析公式 {name} 时出错: {str(e)}")

    def calculate_with_formula(self, formula_name):
        """使用预定义公式进行计算"""
        if formula_name not in self.formulas:
            raise ValueError(f"未找到公式: {formula_name}")

        formula_data = self.formulas[formula_name]
        formula = formula_data["equation"]

        # 收集变量值
        kwargs = {}
        for var in formula_data["variables"]:
            if var in self._calculated_values:
                kwargs[var] = self._calculated_values[var]
            else:
                raise ValueError(f"缺少变量 {var} 的值")

        # 打印原始公式
        logger.debug(f"使用公式: {pretty_print(formula, use_unicode=True)}")

        # 创建代入步骤的字符串表示
        substitution_expr = []
        for var, value in kwargs.items():
            substitution_expr.append(f"{var} = {value}")
        logger.debug(f"代入步骤:\n" + "\n".join(substitution_expr))

        # 创建代入后但未计算的表达式字符串
        display_formula = str(formula)
        for var, value in kwargs.items():
            display_formula = display_formula.replace(var, str(value))
        logger.debug(f"代入后的表达式: {display_formula}")

        # 计算结果：从方程右边提取表达式并计算
        right_side = formula.rhs  # 获取等号右边的表达式
        result = float(right_side.subs(kwargs))  # 对右的表达式进行计算

        # 存储计算结果
        output_var = formula_data["output_variable"]
        self._calculated_values[output_var] = result

        return result

    def update_from_excel_row(self, row_data):
        """从Excel行数据更新配置，支持单位解析"""
        # 清除之前的计算结果，但保留默认值
        self._calculated_values = {
            k: v
            for k, v in self._calculated_values.items()
            if k in self.config["global"]["defaults"]
        }

        # 更新输入值
        for var_name, var_info in self.variables.items():
            if var_info["can_be_input"]:
                excel_col = var_info["excel_column"]
                if excel_col in row_data and row_data[excel_col] is not None:
                    # 解析带单位的值
                    parsed_value = UnitConverter.parse_value(row_data[excel_col])
                    if parsed_value is not None:
                        self._calculated_values[var_name] = parsed_value

    def get_excel_columns(self):
        """获取Excel列配置"""
        return self.config.get("excel", {})

    def __del__(self):
        """清理资源"""
        if hasattr(self, "formula_observer"):
            self.formula_observer.stop()
            self.formula_observer.join()

    def calculate_all_formulas(self, row_data):
        """一次性计算所有公式，支持局部求解，尊重已填写的值"""
        try:
            # 收集所有已知变量（纯数值，无单位）
            known_values = {}
            # 从默认值获取
            known_values.update(self._calculated_values)

            # 从Excel行数据获取（包括输出列的已填写值）
            for var_name, var_info in self.variables.items():
                if var_info["can_be_input"]:
                    excel_col = var_info["excel_column"]
                    if excel_col in row_data and row_data[excel_col] is not None:
                        # 解析带单位的值，转换为基本单位（字节）但不添加单位后缀
                        parsed_value = UnitConverter.parse_value(row_data[excel_col])
                        if parsed_value is not None:
                            known_values[var_name] = float(parsed_value)  # 确保是纯数值

            # 收集已填写的输出值
            for name, formula_data in self.formulas.items():
                output_col = formula_data["excel_column"]
                if output_col in row_data and row_data[output_col] is not None:
                    # 解析已填写的输出值，转换为基本单位
                    parsed_value = UnitConverter.parse_value(row_data[output_col])
                    if parsed_value is not None:
                        known_values[formula_data["output_variable"]] = float(
                            parsed_value
                        )

            # 存储所有方程和它们的变量依赖
            equation_deps = {}
            for name, formula_data in self.formulas.items():
                output_var = formula_data["output_variable"]
                # 只为未知的输出变量创建方程
                if output_var not in known_values:
                    eq = formula_data["equation"]
                    vars_needed = set(formula_data["variables"])
                    equation_deps[name] = {
                        "equation": eq,
                        "variables": vars_needed,
                        "output": output_var,
                        "solved": False,
                    }

            # 存储结果（纯数值）
            results = {}
            made_progress = True

            # 持续尝试求解直到无法取得更多进展
            while made_progress:
                made_progress = False

                # 遍历每个未解决的方程
                for name, eq_data in equation_deps.items():
                    if eq_data["solved"]:
                        continue

                    # 检查是否所有需要的变量都已知
                    missing_vars = eq_data["variables"] - set(known_values.keys())

                    if not missing_vars:  # 如果所有变量都已知
                        try:
                            # 尝试求解单个方程
                            eq = eq_data["equation"]
                            sub_eq = eq

                            eq_str = str(sub_eq)
                            for var, value in known_values.items():
                                eq_str = eq_str.replace(var, str(value))
                            logger.debug(f"求解方程: {eq_str}")

                            # 替换已知值
                            for var, value in known_values.items():
                                sub_eq = sub_eq.subs(var, value)

                            # 求解
                            solution = solve(sub_eq)

                            if solution:
                                # 获取结果
                                if isinstance(solution, dict):
                                    value = solution[Symbol(eq_data["output"])]
                                else:
                                    value = solution[0]  # 取第一个解

                                # 存储结果
                                float_value = float(value)
                                results[eq_data["output"]] = float_value
                                known_values[eq_data["output"]] = float_value
                                eq_data["solved"] = True
                                made_progress = True

                                logger.debug(
                                    f"已解出变量 {eq_data['output']} = {float_value}"
                                )

                        except Exception as e:
                            logger.warning(f"求解方程 {name} 失败: {str(e)}")
                            continue

            # 报告未能求解的方程
            unsolved = [
                name for name, data in equation_deps.items() if not data["solved"]
            ]
            if unsolved:
                logger.warning(f"以下方程无法求解: {unsolved}")
                logger.debug(f"已知变量: {list(known_values.keys())}")

            # 只在最终输出时格式化单位
            formatted_results = {}
            for name, formula_data in self.formulas.items():
                output_var = formula_data["output_variable"]
                if output_var in results:
                    raw_value = float(results[output_var])  # 确保是纯数值
                    # 只在返回结果时添加单位
                    formatted_value = self._format_output_value(raw_value, formula_data)
                    formatted_results[output_var] = formatted_value

                    # 保存纯数值用于后续计算
                    self._calculated_values[output_var] = raw_value

            return formatted_results

        except Exception as e:
            logger.error(f"方程组求解失败: {str(e)}", exc_info=True)
            return None

    def _format_output_value(self, value, formula_data):
        """根据公式配置格式化输出值"""
        if value is None:
            return None

        unit = formula_data.get("unit", "")
        if not unit:
            return value

        # 确定是否使用二进制单位
        use_binary = unit.upper().endswith("IB")

        # 只在最终显示时添加单位
        return UnitConverter.format_value(float(value), unit, use_binary)


class ExcelHandler(FileSystemEventHandler):
    def __init__(self, excel_path):
        self.excel_path = os.path.abspath(excel_path)
        self.calculator = StorageCalculator(excel_mode=True)
        self.last_modified = 0
        self.app = None
        self.wb = None
        self._thread_id = None
        self.setup_excel_connection()

    def _ensure_excel_thread(self):
        """确保Excel操作在正确的线程中执行"""
        import threading

        current_thread = threading.current_thread().ident
        if self._thread_id is None:
            self._thread_id = current_thread
        elif self._thread_id != current_thread:
            raise RuntimeError("Excel操作必须在创建它的线程中执行")

    def cleanup(self):
        """清理资源"""
        try:
            self._ensure_excel_thread()
            if hasattr(self, "wb") and self.wb:
                try:
                    self.wb.save()
                except:
                    pass
                self.wb = None

            if hasattr(self, "app") and self.app:
                try:
                    self.app.quit()
                except:
                    pass
                self.app = None

        except Exception as e:
            print(f"清理资源时出错: {str(e)}")

    def setup_excel_connection(self):
        """建立Excel连接"""
        try:
            self._ensure_excel_thread()
            if self.app is None:
                # 使用xlwings的api
                self.app = xw.App(visible=True, add_book=False)
                print("Excel连接已建立")

            # 尝试获取已打开的工作簿
            try:
                self.wb = xw.books[os.path.basename(self.excel_path)]
            except:
                # 如果工作簿未打开，则打开它
                self.wb = self.app.books.open(self.excel_path)

        except Exception as e:
            print(f"Excel接失败: {str(e)}")
            print(f"详细错误: {repr(e)}")
            import traceback

            print(f"错误堆栈: \n{traceback.format_exc()}")
            self.cleanup()
            raise

    def process_excel(self):
        """处理Excel文件并更新计算结果"""
        if not os.path.exists(self.excel_path):
            logger.error(f"Excel文件不存在: {self.excel_path}")
            return

        try:
            self._ensure_excel_thread()

            # 获取Excel配置
            excel_config = self.calculator.get_excel_columns()
            sheet_name = excel_config.get("sheet_name", "sheet1")
            start_row = excel_config.get("start_row", 2)
            header_row = excel_config.get("header_row", 1)

            # 获取工作表
            sheet = self.wb.sheets[sheet_name]

            # 获取标题行
            headers = sheet.range(f"{header_row}:{header_row}").value

            # 获取数据范围
            used_range = sheet.used_range
            row_count = used_range.last_cell.row

            for row in range(start_row, row_count + 1):
                # 收集行数据，包括已填写的输出列
                row_data = {}
                needs_calculation = False

                for col, header in enumerate(headers, 1):
                    if header:
                        value = sheet.range((row, col)).value
                        row_data[header] = value
                        # 检查是否有需要计算的列（值为空的输出列）
                        if value is None and header in self.calculator.excel_columns:
                            needs_calculation = True

                # 只在有需要计算的列时进行计算
                if needs_calculation:
                    # 一次性计算所有公式
                    results = self.calculator.calculate_all_formulas(row_data)

                    if results:
                        # 只更新空的单元格
                        for formula_data in self.calculator.formulas.values():
                            output_var = formula_data["output_variable"]
                            if output_var in results:
                                output_col = formula_data["excel_column"]
                                if output_col in headers:
                                    col_index = headers.index(output_col) + 1
                                    current_value = sheet.range((row, col_index)).value
                                    # 只在单元格为空时更新
                                    if current_value is None:
                                        sheet.range((row, col_index)).value = results[
                                            output_var
                                        ]
                                        logger.info(
                                            f"已更新 {output_col}: {results[output_var]}"
                                        )

            # 保存更改
            self.wb.save()
            logger.info("Excel已更新")

        except Exception as e:
            logger.error("处理Excel时出错", exc_info=True)

    def on_modified(self, event):
        if event.src_path == self.excel_path:
            # 防止重复触发
            current_time = time.time()
            if current_time - self.last_modified < 1:
                return
            self.last_modified = current_time

            # 使用主线程处理Excel操作
            try:
                # 将Excel操作放入主线程的队列中
                import queue
                import threading

                if hasattr(self, "_main_thread_queue"):
                    self._main_thread_queue.put(self.process_excel)
                else:
                    # 如果在主线程中，直接执行
                    if threading.current_thread().ident == self._thread_id:
                        self.process_excel()
                    else:
                        print("无法在非主线程执行Excel操作")
            except Exception as e:
                print(f"文件修改处理时出错:")
                print(f"错误类型: {type(e).__name__}")
                print(f"错误信息: {str(e)}")
                print(f"详细错误: {repr(e)}")
                import traceback

                print(f"错误堆栈: \n{traceback.format_exc()}")

    def __del__(self):
        """析构函数"""
        self.cleanup()


def watch_excel(excel_path):
    """启动Excel文件监听"""
    excel_path = os.path.abspath(excel_path)

    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"Excel文件不存在: {excel_path}")

    directory = os.path.dirname(excel_path)

    # 创建一个队列用于主线程处理Excel操作
    import queue

    main_thread_queue = queue.Queue()

    # 在主线程中创建Excel处理器
    event_handler = ExcelHandler(excel_path)
    event_handler._main_thread_queue = main_thread_queue

    observer = Observer()
    observer.schedule(event_handler, directory, recursive=False)
    observer.start()

    print(f"开始监听Excel文件: {excel_path}")
    print("提示: 您可以保持Excel文件打开并编辑，程序会自动检测更改并更新计算结果")
    print("按Ctrl+C退出监听")

    try:
        while True:
            # 在主线程中处理Excel操作
            try:
                # 非阻塞方式获取任
                func = main_thread_queue.get_nowait()
                func()
            except queue.Empty:
                pass
            time.sleep(0.1)  # 短暂休眠以减少CPU使用
    except KeyboardInterrupt:
        print("\n正在停止监听...")
        observer.stop()
        event_handler.cleanup()
    observer.join()


def _log_error(message, error=None, include_traceback=True):
    """统一的错误日志处理"""
    logger.error(f"错误: {message}")

    if error:
        logger.error(f"错误类型: {type(error).__name__}")
        logger.error(f"错误信息: {str(error)}")
        logger.error(f"详细错误: {repr(error)}")

    if include_traceback and error:
        import traceback

        logger.error(f"错误堆栈:\n{traceback.format_exc()}")


def calc_excel_cli(excel_path):
    """CLI命令行调用的计算函数"""
    app = None
    try:
        app = xw.App(visible=True, add_book=False)
        app.screen_updating = True
        wb = app.books.open(excel_path)
        success = _do_calculation(wb.sheets.active)
        return 0 if success else 1
    except Exception as e:
        _log_error("CLI执行出错", e)
        return 1
    finally:
        if app:
            app.quit()


def calc_excel():
    """供Excel VBA调用的计算函数"""
    app = None
    try:
        # 获取当前活动的Excel应用程序实例
        app = xw.apps.active
        if app is None:
            app = xw.App()

        # 设置Excel应用程序选项
        app.screen_updating = True
        app.display_alerts = False
        app.calculation = "automatic"

        # 获取活动工作簿
        wb = xw.books.active
        success = _do_calculation(wb.sheets.active)

        # 确保更新显示
        app.calculate()
        app.screen_updating = True

        return success
    except Exception as e:
        _log_error("VBA调用计算出错", e)
        return False
    finally:
        # 如果是我们创建的新实例，则关闭它
        if app and not xw.apps:
            app.quit()


def _do_calculation(sheet):
    """执行实际的计算逻辑"""
    try:
        logger.info("开始执行计算")
        calculator = StorageCalculator(excel_mode=True)

        # 获取Excel配置
        excel_config = calculator.get_excel_columns()
        header_row = excel_config.get("header_row", 1)
        start_row = excel_config.get("start_row", 2)

        # 获取标题行
        headers = sheet.range(f"{header_row}:{header_row}").value

        # 获取数据范围
        used_range = sheet.used_range
        row_count = used_range.last_cell.row

        # 处理每一行
        for row in range(start_row, row_count + 1):
            # 收集行数据
            row_data = {}
            for col, header in enumerate(headers, 1):
                if header:
                    value = sheet.range((row, col)).value
                    row_data[header] = value

            # 一次性计算所有公式
            results = calculator.calculate_all_formulas(row_data)

            if results:
                # 更新Excel单元格
                for formula_data in calculator.formulas.values():
                    output_var = formula_data["output_variable"]
                    if output_var in results:
                        output_col = formula_data["excel_column"]
                        if output_col in headers:
                            col_index = headers.index(output_col) + 1
                            sheet.range((row, col_index)).value = results[output_var]
                            logger.info(f"已更新 {output_col}: {results[output_var]}")

        # 保存更改
        sheet.book.save()
        logger.info("计算完成")
        return True

    except Exception as e:
        logger.error("计算过程出错", exc_info=True)
        return False


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Excel存储计算器")

    # 添加互斥参数组
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--excel", help="Excel文件路径，直接进行一次性计算")
    group.add_argument("--watch", help="Excel文件路径，监听文件变化并实时计算")

    args = parser.parse_args()

    try:
        if args.excel:
            logger.info(f"开始计算Excel文件: {args.excel}")
            exit_code = calc_excel_cli(args.excel)
            sys.exit(exit_code)
        elif args.watch:
            logger.info(f"开监听Excel文件: {args.watch}")
            try:
                watch_excel(args.watch)
                sys.exit(0)
            except FileNotFoundError as e:
                logger.error(f"文件不存在: {args.watch}", exc_info=True)
                sys.exit(1)
            except KeyboardInterrupt:
                logger.info("\n用户终止监听")
                sys.exit(0)
        else:
            # 原有的直接计算模式
            calc = StorageCalculator()
            storage = calc.calculate_total_storage()
            ec_overhead = calc.calculate_ec_overhead()
            effective = calc.calculate_effective_capacity()

            print(f"存储容量计算结果:")
            print(f"NVMe总容量: {storage['nvme_total']:.2f} TB")
            print(f"HDD总容量: {storage['hdd_total']:.2f} TB")
            print(f"EC开销率: {ec_overhead:.2f}")
            print(f"NVMe实际可用容量: {effective['effective_nvme']:.2f} TB")
            print(f"HDD实际可用容量: {effective['effective_hdd']:.2f} TB")
            logger.info("计算完成")
            sys.exit(0)
    except Exception as e:
        logger.error("程序执行出错", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    import sys

    main()
