import time
import os
import sys
import logging
import re
import importlib
from pathlib import Path

class TimingStats:
    """用于记录和统计时间的工具类"""
    def __init__(self):
        self.stats = {}
        self._start_times = {}
        self.import_times = []  # 专门用于存储导入时间

    def start(self, name):
        """开始计时"""
        self._start_times[name] = time.time()

    def end(self, name):
        """结束计时并记录"""
        if name in self._start_times:
            duration = time.time() - self._start_times[name]
            if name not in self.stats:
                self.stats[name] = []
            self.stats[name].append(duration)
            del self._start_times[name]
            return duration
        return 0

    def add_import_time(self, module_name, duration):
        """添加导入时间记录"""
        self.import_times.append((module_name, duration))

    def get_stats(self):
        """获取统计信息"""
        result = {}

        # 处理常规统计
        for name, times in self.stats.items():
            if times:  # 确保有数据
                result[name] = {
                    'count': len(times),
                    'total': sum(times),
                    'avg': sum(times) / len(times),
                    'min': min(times),
                    'max': max(times)
                }

        # 处理导入时间统计
        if self.import_times:
            total_import_time = sum(t[1] for t in self.import_times)
            result['imports'] = {
                'count': len(self.import_times),
                'total': total_import_time,
                'avg': total_import_time / len(self.import_times),
                'min': min(t[1] for t in self.import_times),
                'max': max(t[1] for t in self.import_times),
                'details': {name: time for name, time in self.import_times}
            }

        return result

    def print_stats(self):
        """打印统计信息"""
        stats = self.get_stats()
        print("\n性能统计信息:")

        # 先打印导入时间详情
        if 'imports' in stats:
            print("模块导入时间:")
            for module, time in stats['imports']['details'].items():
                print(f"  {module}: {time:.3f}秒")
            print(f"  总导入时间: {stats['imports']['total']:.3f}秒")
            print(f"  平均导入时间: {stats['imports']['avg']:.3f}秒")
            print()

        # 打印其他统计信息
        for name, data in stats.items():
            if name != 'imports':  # 导入时间已经单独处理
                print(f"{name}:")
                print(f"  总次数: {data['count']}")
                print(f"  总时间: {data['total']:.3f}秒")
                print(f"  平均时间: {data['avg']:.3f}秒")
                print(f"  最短时间: {data['min']:.3f}秒")
                print(f"  最长时间: {data['max']:.3f}秒")
                print()

# 创建全局计时器
timing = TimingStats()

# 记录模块导入时间
def time_import(module_name):
    start_time = time.time()
    module = importlib.import_module(module_name)
    duration = time.time() - start_time
    timing.add_import_time(module_name, duration)
    return module

# 记录主要依赖库的导入时间
timing.start('total_imports')

# 导入基础库
watchdog_events = time_import('watchdog.events')
watchdog_observers = time_import('watchdog.observers')
FileSystemEventHandler = watchdog_events.FileSystemEventHandler
Observer = watchdog_observers.Observer

# 导入计算相关库
np = time_import('numpy')
sympy_module = time_import('sympy')
symbols = sympy_module.symbols
Eq = sympy_module.Eq
solve = sympy_module.solve
Symbol = sympy_module.Symbol
pretty_print = sympy_module.pretty_print
sympify = sympy_module.sympify
parse_expr = time_import('sympy.parsing.sympy_parser').parse_expr

# 导入数据处理库
# pd = time_import('pandas')
yaml = time_import('yaml')
xw = time_import('xlwings')

timing.end('total_imports')

def setup_logging(config_path='config.yaml'):
    """设置日志配置"""
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # 默认配置
    default_config = {
        'logging': {
            'console_level': 'DEBUG',
            'file_level': 'INFO',
            'log_file': os.path.join(script_dir, 'storage_calculator.log'),  # 使用绝对路径
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    }

    # 将配置文件路径转换为绝对路径
    config_path = os.path.join(script_dir, config_path)

    # 尝试读取配置文件
    config = default_config
    if Path(config_path).exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                # 确保日志文件路径是绝对路径
                if 'logging' in config and 'log_file' in config['logging']:
                    if not os.path.isabs(config['logging']['log_file']):
                        config['logging']['log_file'] = os.path.join(
                            script_dir,
                            config['logging']['log_file']
                        )
        except Exception as e:
            print(f"读取配置文件失败，使用默认配置: {e}", file=sys.stderr)

    # 创建logger
    logger = logging.getLogger('StorageCalculator')
    logger.setLevel(logging.DEBUG)

    # 确保日志目录存在
    log_file = config['logging']['log_file']
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # 日志格式
    formatter = logging.Formatter(config['logging']['format'])

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, config['logging']['console_level']))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(getattr(logging, config['logging']['file_level']))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 记录初始化信息
    logger.debug(f"日志配置已初始化")
    logger.debug(f"脚本目录: {script_dir}")
    logger.debug(f"日志文件: {log_file}")
    logger.debug(f"配置文件: {config_path}")

    return logger

# 创建全局logger
logger = setup_logging()

class FormulaWatcher(FileSystemEventHandler):
    def __init__(self, calculator):
        self.calculator = calculator
        self.last_modified = 0
        self.retry_count = 3
        self.retry_delay = 0.5
        # 改为监听整个配置目录
        self.watch_dir = os.path.abspath(calculator.formula_dir)
        logger.debug(f"监听配置目录: {self.watch_dir}")

    def on_modified(self, event):
        # 检查是否是yaml文件修改
        if event.src_path.endswith('.yaml') and os.path.dirname(event.src_path) == self.watch_dir:
            current_time = time.time()
            if current_time - self.last_modified < 1:
                return
            self.last_modified = current_time
            logger.info(f"检测到配置文件 {os.path.basename(event.src_path)} 更改，准备重新加载")

class UnitConverter:
    """单位转换工具类"""

    # 定义单位换算基数
    BINARY_BASE = 1024  # 二进制单位(Ki, Mi, Gi, Ti, Pi)
    DECIMAL_BASE = 1000  # 十进制单位(K, M, G, T, P)

    # 单位定义
    BINARY_UNITS = [
        (1024**4, 'TiB'),
        (1024**3, 'GiB'),
        (1024**2, 'MiB'),
        (1024**1, 'KiB'),
        (1, 'B')
    ]

    DECIMAL_UNITS = [
        (1000**4, 'TB'),
        (1000**3, 'GB'),
        (1000**2, 'MB'),
        (1000**1, 'KB'),
        (1, 'B')
    ]

    # 特殊单位映射（非1024/1000倍数关系的单位）
    SPECIAL_UNITS = {
        '%': {'base': 0.01, 'format': lambda x: f"{x*100:.2f}%"},
        '个': {'base': 1, 'format': lambda x: f"{x:.0f}个"},
        'MiB/s': {'base': 1, 'format': lambda x: f"{x:.2f}MiB/s"}
    }

    @classmethod
    def _parse_unit_prefix(cls, unit):
        """增强单位前缀解析能力"""
        # 统一处理单位格式
        unit = unit.strip().lower()
        if unit.endswith('/s'):  # 保留速率单位特征
            base_unit = unit[:-2]
            suffix = '/s'
        else:
            base_unit = unit
            suffix = ''

        # 扩展单位别名映射
        unit_aliases = {
            'mib': 'mebibytes',
            'mb': 'megabytes',
            'gib': 'gibibytes',
            'gb': 'gigabytes',
            'tib': 'tebibytes',
            'tb': 'terabytes'
        }

        # 处理带/的复合单位
        if '/' in base_unit:
            numerator, denominator = base_unit.split('/', 1)
            return unit, 1, False  # 暂不处理复杂单位

        # 处理二进制单位
        binary_units = {
            'kib': 1024**1, 'mib': 1024**2,
            'gib': 1024**3, 'tib': 1024**4,
            'pib': 1024**5
        }
        if base_unit in binary_units:
            return f"{base_unit}{suffix}".upper(), binary_units[base_unit], True

        # 处理十进制单位
        decimal_units = {
            'kb': 1000**1, 'mb': 1000**2,
            'gb': 1000**3, 'tb': 1000**4,
            'pb': 1000**5
        }
        if base_unit in decimal_units:
            return f"{base_unit}{suffix}".upper(), decimal_units[base_unit], False

        # 处理无前缀单位
        if base_unit in ['b', 'bytes']:
            return f"B{suffix}", 1, True

        return None, 1, False

    @classmethod
    def parse_value(cls, value):
        """增强带复杂单位的解析能力"""
        try:
            # 增强科学计数法处理
            if isinstance(value, str) and 'e' in value.lower():
                match = re.match(r'^([\d\.e+-]+)\s*([a-z%]*)$', value, re.I)
                if match:
                    number_part, unit_part = match.groups()
                    return float(number_part) * cls._parse_unit_prefix(unit_part)[1]

            # 处理特殊单位
            if isinstance(value, str) and '%' in value:
                return float(value.replace('%', '')) * 0.01

            # 其余保持原有逻辑...
            if value is None:
                return None

            try:
                # 如果是数字，直接返回
                if isinstance(value, (int, float)):
                    return float(value)

                # 转换为字符串并清理
                value_str = str(value).strip()
                if not value_str:
                    return None

                # 分离数值和单位
                import re
                match = re.match(r'^([-+]?\d*\.?\d+)\s*(.*)$', value_str)
                if not match:
                    return float(value_str) if value_str.replace('.','',1).isdigit() else None

                number, unit = match.groups()
                number = float(number)
                unit = unit.strip()

                if not unit:
                    return number

                # 获取单位信息
                unit_info, factor, is_binary = cls._parse_unit_prefix(unit)
                if unit_info is None:
                    return number

                # 特殊单位处理
                if unit_info in cls.SPECIAL_UNITS:
                    return number * cls.SPECIAL_UNITS[unit_info]['base']

                # 转换为基本单位
                logger.debug(f"解析值: {value_str} -> 数值: {number} 单位: {unit}")
                parsed = number * factor
                logger.debug(f"解析结果: {parsed} 基本单位")
                return parsed

            except (ValueError, TypeError):
                return None

        except Exception as e:
            logger.error(f"解析错误: {value} -> {str(e)}")
            return None

    @classmethod
    def format_value(cls, value, target_unit=None, use_binary=True):
        """格式化数值，自动选择合适的单位"""
        if value is None:
            return None

        try:
            value = float(value)
        except (ValueError, TypeError):
            return str(value)

        # 特殊单位处理
        if target_unit in cls.SPECIAL_UNITS:
            return cls.SPECIAL_UNITS[target_unit]['format'](value)

        # 选择单位系统
        units = cls.BINARY_UNITS if use_binary else cls.DECIMAL_UNITS
        base = cls.BINARY_BASE if use_binary else cls.DECIMAL_BASE

        # 如果指定了目标单位
        if target_unit:
            unit_info, factor, is_binary = cls._parse_unit_prefix(target_unit)
            if unit_info:
                converted_value = value / factor
                return f"{converted_value:.2f} {unit_info}"

        # 自动选择最合适的单位
        abs_value = abs(value)
        for factor, unit in units:
            if abs_value >= factor:
                converted_value = value / factor
                return f"{converted_value:.2f} {unit}"

        return f"{value:.2f} B"

class StorageCalculator:
    def __init__(self, excel_mode=False, formula_dir='formulas'):
        """初始化计算器

        Args:
            excel_mode (bool): 是否为Excel模式
            formula_dir (str): 配置目录名称（将自动从脚本所在目录查找）
        """
        timing.start('calculator_init')

        # 获取脚本所在目录的绝对路径
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        logger.debug(f"脚本所在目录: {self.script_dir}")

        # 修改formula_file为formula_dir
        self.formula_dir = os.path.join(self.script_dir, formula_dir)
        logger.debug(f"配置目录路径: {self.formula_dir}")

        self.excel_mode = excel_mode
        self._calculated_values = {}  # 存储计算结果
        self._last_config = None  # 存储上一次的配置用于比较
        self.unit_converter = UnitConverter()

        # 初始化配置相关属性
        self.variables = {}  # 变量定义
        self.formulas = {}   # 公式定义
        self.config = {}     # 完整配置
        self.excel_columns = {} # Excel列映射

        # 加载配置并初始化
        timing.start('load_config')
        self.load_config()
        timing.end('load_config')

        # 设置配置文件监听
        if self.excel_mode:
            timing.start('setup_formula_watcher')
            self.setup_formula_watcher()
            timing.end('setup_formula_watcher')

        timing.end('calculator_init')

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
            sections = ['global', 'variables', 'formulas', 'excel']
            for section in sections:
                if (section in new_config) != (section in self._last_config):
                    logger.debug(f"配置节{section}存在性发生变化")
                    return True
                if section in new_config and new_config[section] != self._last_config[section]:
                    logger.debug(f"配置节{section}内容发生变化")
                    return True

            return False
        except Exception as e:
            logger.error(f"配置比较出错: {str(e)}")
            return False

    def load_config(self):
        """加载配置文件"""
        try:
            # 获取formulas目录的路径
            formulas_dir = self.formula_dir
            if not os.path.exists(formulas_dir):
                logger.error(f"formulas目录不存在: {formulas_dir}")
                return

            # 初始化合并后的配置
            merged_config = {
                'global': {},
                'variables': {},
                'formulas': {},
                'excel': {}
            }

            # 遍历formulas目录下的所有yaml文件
            yaml_files = [f for f in os.listdir(formulas_dir) if f.endswith('.yaml')]
            if not yaml_files:
                logger.error("formulas目录下没有找到yaml文件")
                return

            # 按文件名排序，确保加载顺序一致
            yaml_files.sort()

            for yaml_file in yaml_files:
                file_path = os.path.join(formulas_dir, yaml_file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                        if not config:
                            logger.warning(f"配置文件为空: {yaml_file}")
                            continue

                        # 合并各个部分的配置
                        for section in ['global', 'variables', 'formulas', 'excel']:
                            if section in config:
                                if section not in merged_config:
                                    merged_config[section] = {}
                                merged_config[section].update(config[section])

                    logger.debug(f"已加载配置文件: {yaml_file}")

                except yaml.YAMLError as e:
                    logger.error(f"YAML格式错误 {yaml_file}: {str(e)}")
                    continue
                except Exception as e:
                    logger.error(f"加载配置文件出错 {yaml_file}: {str(e)}")
                    continue

            # 检查配置是否有效
            if not any(merged_config.values()):
                logger.error("没有找到有效的配置")
                return

            # 检查必要的配置节是否存在
            required_sections = ['global', 'variables', 'formulas']
            missing_sections = [section for section in required_sections if not merged_config.get(section)]
            if missing_sections:
                logger.error(f"缺少必要的配置节: {', '.join(missing_sections)}")
                return

            # 检查配置是否发生变化
            if not self._config_has_changed(merged_config):
                logger.debug("配置未发生变化，跳过重新加载")
                return

            # 更新配置
            self.config = merged_config
            self._last_config = merged_config.copy()

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

        except Exception as e:
            logger.error(f"加载配置文件出错: {str(e)}")

    def _trigger_recalculation(self):
        """触发Excel重新计算"""
        try:
            if hasattr(self, '_current_sheet'):
                logger.info("配置已更新，触发重新计算")
                self._do_calculation(self._current_sheet)
        except Exception as e:
            logger.error(f"触发重新计算失败: {str(e)}", exc_info=True)

    def _do_calculation(self, sheet):
        """执行实际的计算逻辑"""
        try:
            logger.info("开始执行计算")
            calculator = StorageCalculator(excel_mode=True)

            # 获取Excel配置
            excel_config = calculator.get_excel_columns()
            header_row = excel_config.get('header_row', 1)
            start_row = excel_config.get('start_row', 2)

            # 获取实际的sheet名称
            actual_sheet_name = sheet.name
            logger.debug(f"当前工作表名称: {actual_sheet_name}")

            # 获取标题行
            header_range = sheet.range(f'{header_row}:{header_row}')
            headers = header_range.value
            logger.debug(f"读取到的标题行: {headers}")

            # 获取数据范围
            used_range = sheet.used_range
            row_count = used_range.last_cell.row
            logger.debug(f"数据范围: 从第{start_row}行到第{row_count}行")

            # 处理每一行
            updated = False  # 跟踪是否有更新
            for row in range(start_row, row_count + 1):
                row_data = {}
                has_valid_data = False

                # 收集行数据
                for col, header in enumerate(headers, 1):
                    if header:
                        raw_value = sheet.range((row, col)).value
                        if raw_value is not None:
                            has_valid_data = True
                            row_data[header] = raw_value

                if not has_valid_data:
                    continue

                # 执行计算
                results = calculator.calculate_all_formulas(row_data)

                if results:
                    logger.debug(f"计算结果: {results}")
                    # 更新Excel
                    for name, formula_data in calculator.formulas.items():
                        if name in results:
                            output_col = formula_data['excel_column']
                            if output_col in headers:
                                col_index = headers.index(output_col) + 1

                                # 格式化输出值
                                output_unit = formula_data.get('unit', '')
                                formatted_value = calculator.unit_converter.format_value(
                                    results[name],
                                    target_unit=output_unit,
                                    use_binary='i' in output_unit.lower() if output_unit else True
                                )

                                # 更新单元格（不管是否为空）
                                current_value = sheet.range((row, col_index)).value
                                if current_value != formatted_value:
                                    try:
                                        sheet.range((row, col_index)).value = formatted_value
                                        updated = True
                                        logger.info(f"已更新单元格({row}, {col_index}) {output_col}: {formatted_value}")
                                    except Exception as e:
                                        logger.error(f"更新单元格失败: {str(e)}")

            # 只在有更新时保存
            if updated:
                try:
                    sheet.book.save()
                    logger.info("Excel已更新并保存")
                except Exception as e:
                    logger.error(f"保存Excel失败: {str(e)}")
            else:
                logger.info("没有需要更新的内容")

            return True

        except Exception as e:
            logger.error("计算过程出错", exc_info=True)
            return False

    def setup_formula_watcher(self):
        """设置公式目录监听"""
        try:
            self.formula_watcher = FormulaWatcher(self)
            self.formula_observer = Observer()
            self.formula_observer.schedule(
                self.formula_watcher,
                path=self.formula_dir,  # 修正为使用配置目录路径
                recursive=False
            )
            logger.debug(f"监听路径: {self.formula_dir}")
            self.formula_observer.start()
            logger.debug("公式目录监听已启动")
        except Exception as e:
            logger.error(f"设置公式目录监听失败: {str(e)}")

    def load_defaults(self):
        """加载默认值"""
        defaults = self.config.get('global', {}).get('defaults', {})
        for var, value in defaults.items():
            # 移除单位，转换为纯数值
            parsed_value = self.unit_converter.parse_value(value)
            if parsed_value is not None:
                self._calculated_values[var] = parsed_value
            else:
                self._calculated_values[var] = value
            logger.debug(f"已加载默认值: {var} = {value} -> {parsed_value}")

    def load_variables(self):
        """加载变量定义"""
        self.variables = {}
        for var_name, var_info in self.config.get('variables', {}).items():
            self.variables[var_name] = {
                'description': var_info.get('description', ''),
                'unit': var_info.get('unit', ''),
                'excel_column': var_info.get('excel_column', var_name),
                'can_be_input': var_info.get('can_be_input', False)
            }
        logger.debug(f"已加载变量定义: {list(self.variables.keys())}")

    def load_formulas(self):
        """加载公式定义"""
        self.formulas = {}
        self.excel_columns = {}

        for name, formula_data in self.config.get('formulas', {}).items():
            if not all(k in formula_data for k in ['expression', 'excel_column']):
                logger.error(f"公式 {name} 配置不完整，跳过加载")
                continue
            try:
                # 修改表达式格式以适应sympy解析
                expr_str = formula_data['expression']
                # 移除等号左边的变量定义，只保留等式右边
                expr_str = expr_str.split('=')[1].strip()

                # 解析公式表达式
                expr = parse_expr(expr_str)

                # 自动提取公式中的变量
                variables = [str(symbol) for symbol in expr.free_symbols]

                # 存储公式信息
                self.formulas[name] = {
                    'equation': Eq(Symbol(name), expr),  # 使用formula的key作为输出变量
                    'variables': set(variables),  # 使用自动提取的变量
                    'excel_column': formula_data['excel_column'],
                    'unit': formula_data.get('unit', '')
                }

                # 注册Excel列映射
                self.excel_columns[formula_data['excel_column']] = name

                logger.debug(f"已加载公式 {name}, 变量: {variables}")

            except Exception as e:
                logger.error(f"解析公式 {name} 时出错: {str(e)}")

    def calculate_with_formula(self, formula_name):
        """使用预定义公式进行计算"""
        if formula_name not in self.formulas:
            raise ValueError(f"未找到公式: {formula_name}")

        formula_data = self.formulas[formula_name]
        formula = formula_data['equation']

        # 收集变量值
        kwargs = {}
        for var in formula_data['variables']:
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
        self._calculated_values[formula_name] = result  # 使用formula的key作为结果key

        return result

    def update_from_excel_row(self, row_data):
        """从Excel行数据更新配置，支持单位解析"""
        # 清除之前的计算结果，但保留默认值
        self._calculated_values = {k: v for k, v in self._calculated_values.items()
                                 if k in self.config['global']['defaults']}

        # 更新输入值
        for var_name, var_info in self.variables.items():
            if var_info['can_be_input']:
                excel_col = var_info['excel_column']
                if excel_col in row_data and row_data[excel_col] is not None:
                    # 解析带单位的值（优先使用单元格中的单位）
                    parsed_value = self.unit_converter.parse_value(row_data[excel_col])
                    if parsed_value is not None:
                        self._calculated_values[var_name] = parsed_value

    def get_excel_columns(self):
        """获取Excel列配置"""
        return self.config.get('excel', {})

    def __del__(self):
        """清理资源"""
        if hasattr(self, 'formula_observer'):
            self.formula_observer.stop()
            self.formula_observer.join()

    def calculate_all_formulas(self, row_data):
        """入口添加防御性检查"""
        if not row_data:
            logger.debug("接收到空数据，跳过计算")
            return None

        try:
            # 添加调试日志
            logger.debug(f"Excel输入数据: {row_data}")

            # 收集所有已知变量（纯数值，无单位）
            known_values = {}

            # 首先从Excel行数据获取（包括输出列的已填写值）
            for var_name, var_info in self.variables.items():
                if var_info['can_be_input']:
                    excel_col = var_info['excel_column']
                    if excel_col in row_data and row_data[excel_col] is not None:
                        # 解析带单位的值，转换为基本单位
                        parsed_value = self.unit_converter.parse_value(row_data[excel_col])
                        if parsed_value is not None:
                            known_values[var_name] = float(parsed_value)  # 确保是纯数值
                            logger.debug(f"从Excel读取值: {var_name} = {parsed_value} (原始值: {row_data[excel_col]})")

            # 使用默认值填充未指定的变量
            for var_name in self.variables:
                if var_name not in known_values and var_name in self._calculated_values:
                    known_values[var_name] = self._calculated_values[var_name]
                    logger.debug(f"使用默认值: {var_name} = {self._calculated_values[var_name]}")

            logger.debug(f"最终用于计算的已知值: {known_values}")

            # 如果没有任何已知值，返回None
            if not known_values:
                logger.debug("没有有效的已知值，跳过计算")
                return None

            # 存储所有方程和它们的变量依赖
            equation_deps = {}
            for name, formula_data in self.formulas.items():
                # 只为未知的输出变量创建方程
                if name not in known_values:
                    eq = formula_data['equation']
                    vars_needed = set(formula_data['variables'])
                    equation_deps[name] = {
                        'equation': eq,
                        'variables': vars_needed,
                        'output': name,  # 使用formula的key作为输出变量
                        'solved': False
                    }

            # 存储计算结果
            results = known_values.copy()

            # 迭代求解直到无法继续
            while True:
                made_progress = False
                for name, eq_data in equation_deps.items():
                    if eq_data['solved']:
                        continue

                    # 检查是否所有需要的变量都已知
                    if all(var in results for var in eq_data['variables']):
                        try:
                            # 准备方程求解
                            eq = eq_data['equation']
                            # 替换已知变量
                            subs_dict = {Symbol(var): results[var] for var in eq_data['variables']}

                            # 求解方程
                            solution = solve(eq.subs(subs_dict))
                            if solution:
                                # 获取第一个解
                                float_value = float(solution[0])
                                # 存储结果
                                results[name] = float_value  # 使用formula的key作为结果key
                                eq_data['solved'] = True
                                made_progress = True
                                logger.debug(f"已解出变量 {name} = {float_value}")

                        except Exception as e:
                            logger.warning(f"求解方程 {name} 失败: {str(e)}")
                            continue

                if not made_progress:
                    break

            # 报告未能求解的方程
            unsolved = [name for name, data in equation_deps.items() if not data['solved']]
            if unsolved:
                logger.warning(f"以下方程无法求解: {unsolved}")

            # 更新计算结果缓存
            self._calculated_values.update(results)

            return results

        except Exception as e:
            logger.error(f"计算过程出错: {str(e)}", exc_info=True)
            return None

    def _format_output_value(self, value, formula_data):
        """根据公式配置格式化输出值"""
        if value is None:
            return None

        unit = formula_data.get('unit', '')
        if not unit:
            return value

        # 确定是否使用二进制单位
        use_binary = unit.upper().endswith('iB')
        logger.debug(f"格式化值 {value} 使用单位 {unit} (二进制单位: {use_binary})")

        try:
            # 格式化值
            formatted = self.unit_converter.format_value(float(value), unit, use_binary)
            logger.debug(f"格式化结果: {formatted}")
            return formatted
        except Exception as e:
            logger.error(f"格式化值时出错: {str(e)}")
            return value  # 返回原始值作为后备

class ExcelHandler(FileSystemEventHandler):
    def __init__(self, excel_path):
        self.excel_path = os.path.abspath(excel_path)
        self.calculator = StorageCalculator(excel_mode=True)
        self.last_modified = 0
        self.last_size = 0
        self.app = None
        self.wb = None
        self._thread_id = None
        self.processing = False
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
            if hasattr(self, 'wb') and self.wb:
                try:
                    self.wb.save()
                except:
                    pass
                self.wb = None

            if hasattr(self, 'app') and self.app:
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
            timing.start('excel_connection')
            self._ensure_excel_thread()

            if self.app is None:
                # 使用xlwings的api
                timing.start('excel_app_init')
                self.app = xw.App(visible=True, add_book=False)
                timing.end('excel_app_init')
                logger.info("Excel应用程序已启动")

            # 尝试获取已打开的工作簿
            timing.start('excel_workbook_open')
            try:
                self.wb = xw.books[os.path.basename(self.excel_path)]
                logger.info("已连接到打开的工作簿")
            except:
                # 如果工作簿未打开，则打开它
                self.wb = self.app.books.open(self.excel_path)
                logger.info("已打开新的工作簿")
            timing.end('excel_workbook_open')

            timing.end('excel_connection')
            logger.info("Excel连接已完成")

        except Exception as e:
            timing.end('excel_connection')  # 确保在异常情况下也记录时间
            logger.error(f"Excel连接失败: {str(e)}")
            logger.error(f"详细错误: {repr(e)}")
            import traceback
            logger.error(f"错误堆栈: \n{traceback.format_exc()}")
            self.cleanup()
            raise

    def on_modified(self, event):
        """处理文件修改事件"""
        if event.src_path != self.excel_path:
            return

        try:
            # 获取文件当前大小
            current_size = os.path.getsize(self.excel_path)
            current_time = time.time()

            # 防抖动：检查时间间隔和文件大小变化
            if (current_time - self.last_modified < 1 or
                current_size == self.last_size or
                self.processing):
                return

            # 更新状态
            self.last_modified = current_time
            self.last_size = current_size
            self.processing = True

            try:
                # 将Excel操作放入主线程的队列中
                if hasattr(self, '_main_thread_queue'):
                    self._main_thread_queue.put(self.process_excel)
                else:
                    # 如果在主线程中，直接执行
                    if threading.current_thread().ident == self._thread_id:
                        self.process_excel()
                    else:
                        logger.warning("无法在非主线程执行Excel操作")
            finally:
                self.processing = False

        except Exception as e:
            logger.error(f"处理文件修改事件时出错: {str(e)}", exc_info=True)
            self.processing = False

    def process_excel(self):
        """处理Excel文件并更新计算结果"""
        if not os.path.exists(self.excel_path):
            logger.error(f"Excel文件不存在: {self.excel_path}")
            return

        try:
            self._ensure_excel_thread()

            # 获取Excel配置
            excel_config = self.calculator.get_excel_columns()
            sheet_name = excel_config.get('sheet_name', 'sheet1')
            start_row = excel_config.get('start_row', 2)
            header_row = excel_config.get('header_row', 1)

            # 获取工作表
            sheet = self.wb.sheets[sheet_name]

            # 获取标题行
            headers = sheet.range(f'{header_row}:{header_row}').value

            # 获取数据范围
            used_range = sheet.used_range
            row_count = used_range.last_cell.row

            # 处理每一行
            updated = False  # 跟踪是否有更新
            for row in range(start_row, row_count + 1):
                row_data = {}
                has_valid_data = False

                # 收集行数据
                for col, header in enumerate(headers, 1):
                    if header:
                        raw_value = sheet.range((row, col)).value
                        if raw_value is not None:
                            has_valid_data = True
                            row_data[header] = raw_value

                if not has_valid_data:
                    continue

                # 执行计算
                results = self.calculator.calculate_all_formulas(row_data)

                if results:
                    logger.debug(f"计算结果: {results}")
                    # 更新Excel
                    for name, formula_data in self.calculator.formulas.items():
                        if name in results:
                            output_col = formula_data['excel_column']
                            if output_col in headers:
                                col_index = headers.index(output_col) + 1

                                # 格式化输出值
                                output_unit = formula_data.get('unit', '')
                                formatted_value = self.calculator.unit_converter.format_value(
                                    results[name],
                                    target_unit=output_unit,
                                    use_binary='i' in output_unit.lower() if output_unit else True
                                )

                                # 更新单元格（不管是否为空）
                                current_value = sheet.range((row, col_index)).value
                                if current_value != formatted_value:
                                    try:
                                        sheet.range((row, col_index)).value = formatted_value
                                        updated = True
                                        logger.info(f"已更新单元格({row}, {col_index}) {output_col}: {formatted_value}")
                                    except Exception as e:
                                        logger.error(f"更新单元格失败: {str(e)}")

            # 只在有更新时保存
            if updated:
                try:
                    self.wb.save()
                    logger.info("Excel已更新并保存")
                except Exception as e:
                    logger.error(f"保存Excel失败: {str(e)}")
            else:
                logger.info("没有需要更新的内容")

        except Exception as e:
            logger.error("处理Excel时出错", exc_info=True)
        finally:
            self.processing = False

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

    observer = None  # 显式声明为局部变量
    try:
        observer = Observer()
        logger.debug(f"监听路径: {directory}")
        observer.schedule(event_handler, directory, recursive=False)
        observer.start()

        print(f"开始监听Excel文件: {excel_path}")
        print("提示: 您可以保持Excel文件打开并编辑，程序会自动检测更改并更新计算结果")
        print("按Ctrl+C退出监听")

        # 使用带超时的阻塞队列
        while observer.is_alive():
            try:
                func = main_thread_queue.get(timeout=0.5)
                func()
            except queue.Empty:
                if not observer.is_alive():
                    break
            except KeyboardInterrupt:
                logger.info("\n接收到终止信号")
                break

    except Exception as e:
        logger.error(f"监听异常: {str(e)}", exc_info=True)
    finally:
        if observer:
            observer.stop()
            observer.join(timeout=5)
            if observer.is_alive():
                logger.warning("Observer线程未正常退出")
        event_handler.cleanup()
        logger.info("监听资源已释放")

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
        app.calculation = 'automatic'

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

def main():
    timing.start('main')
    import argparse
    parser = argparse.ArgumentParser(description='Excel存储计算器')

    # 添加互斥参数组
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--excel', help='Excel文件路径，直接进行一次性计算')
    group.add_argument('--watch', help='Excel文件路径，监听文件变化并实时计算')

    args = parser.parse_args()

    try:
        if args.excel:
            logger.info(f"开始计算Excel文件: {args.excel}")
            timing.start('excel_calculation')
            exit_code = calc_excel_cli(args.excel)
            timing.end('excel_calculation')
            timing.print_stats()  # 打印性能统计
            sys.exit(exit_code)
        elif args.watch:
            logger.info(f"开始监听Excel文件: {args.watch}")
            try:
                timing.start('excel_watch')
                watch_excel(args.watch)
                timing.end('excel_watch')
                timing.print_stats()  # 打印性能统计
                sys.exit(0)
            except FileNotFoundError as e:
                logger.error(f"文件不存在: {args.watch}", exc_info=True)
                sys.exit(1)
            except KeyboardInterrupt:
                logger.info("\n用户终止监听")
                timing.end('excel_watch')
                timing.print_stats()  # 打印性能统计
                sys.exit(0)
        else:
            # 原有的直接计算模式
            timing.start('direct_calculation')
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
            timing.end('direct_calculation')
            logger.info("计算完成")
            timing.print_stats()  # 打印性能统计
            sys.exit(0)
    except Exception as e:
        logger.error("程序执行出错", exc_info=True)
        timing.end('main')
        timing.print_stats()  # 打印性能统计
        sys.exit(1)
    finally:
        timing.end('main')

if __name__ == "__main__":
    import sys
    main()