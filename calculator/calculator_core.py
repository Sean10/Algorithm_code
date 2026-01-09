"""
存储计算器核心模块 - 纯计算逻辑，无平台依赖
"""
import time
import os
import logging
import re
from pathlib import Path

import yaml
import numpy as np
from sympy import symbols, Eq, solve, Symbol, pretty_print, sympify
from sympy.parsing.sympy_parser import parse_expr

# 设置日志
def setup_logging(name='StorageCalculator', level=logging.INFO):
    """设置日志配置"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(handler)
    return logger

# 默认使用 INFO 级别，确保能看到详细的计算过程日志
logger = setup_logging(level=logging.INFO)


class UnitConverter:
    """单位转换工具类"""

    BINARY_BASE = 1024
    DECIMAL_BASE = 1000

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

    SPECIAL_UNITS = {
        '%': {'base': 0.01, 'format': lambda x: f"{x*100:.2f}%"},
        '个': {'base': 1, 'format': lambda x: f"{x:.0f}个"},
    }

    @classmethod
    def _parse_unit_prefix(cls, unit):
        """解析单位前缀"""
        unit = unit.strip().lower()
        if unit.endswith('/s'):
            base_unit = unit[:-2]
            suffix = '/s'
        else:
            base_unit = unit
            suffix = ''

        if '/' in base_unit:
            return unit, 1, False

        # 二进制单位 (1024倍数)
        binary_units = {
            'kib': 1024**1, 'mib': 1024**2,
            'gib': 1024**3, 'tib': 1024**4,
            'pib': 1024**5
        }
        if base_unit in binary_units:
            formatted = f"{base_unit[0].upper()}{base_unit[1]}B{suffix}"
            return formatted, binary_units[base_unit], True

        # 十进制单位 (1000倍数) - 支持简写如 K, M, G, T, P
        decimal_units = {
            'k': 1000**1, 'kb': 1000**1,
            'm': 1000**2, 'mb': 1000**2,
            'g': 1000**3, 'gb': 1000**3,
            't': 1000**4, 'tb': 1000**4,
            'p': 1000**5, 'pb': 1000**5
        }
        if base_unit in decimal_units:
            # 统一格式化为带B的形式
            unit_letter = base_unit[0].upper()
            formatted = f"{unit_letter}B{suffix}"
            return formatted, decimal_units[base_unit], False

        if base_unit in ['b', 'bytes']:
            return f"B{suffix}", 1, True

        return None, 1, False

    @classmethod
    def parse_value(cls, value):
        """解析带单位的值"""
        try:
            if isinstance(value, str) and 'e' in value.lower():
                match = re.match(r'^([\d\.e+-]+)\s*([a-z%]*)$', value, re.I)
                if match:
                    number_part, unit_part = match.groups()
                    return float(number_part) * cls._parse_unit_prefix(unit_part)[1]

            if isinstance(value, str) and '%' in value:
                return float(value.replace('%', '')) * 0.01

            if value is None:
                return None

            if isinstance(value, (int, float)):
                return float(value)

            value_str = str(value).strip()
            if not value_str:
                return None

            match = re.match(r'^([-+]?\d*\.?\d+)\s*(.*)$', value_str)
            if not match:
                return float(value_str) if value_str.replace('.','',1).isdigit() else None

            number, unit = match.groups()
            number = float(number)
            unit = unit.strip()

            if not unit:
                return number

            unit_info, factor, is_binary = cls._parse_unit_prefix(unit)
            if unit_info is None:
                return number

            if unit_info in cls.SPECIAL_UNITS:
                return number * cls.SPECIAL_UNITS[unit_info]['base']

            return number * factor

        except (ValueError, TypeError):
            return None
        except Exception as e:
            logger.error(f"解析错误: {value} -> {str(e)}")
            return None

    @classmethod
    def format_value(cls, value, target_unit=None, use_binary=True):
        """格式化数值，将数值转换为人类可读的单位显示
        
        Args:
            value: 数值（对于容量类单位，假设是字节数；对于特殊单位如%，是原始比例值）
            target_unit: 目标单位（如 TB, TiB, GB, MiB/s 等）
            use_binary: 自动选择单位时是否使用二进制单位
        """
        if value is None:
            return None

        try:
            value = float(value)
        except (ValueError, TypeError):
            return str(value)

        # 优先处理用户明确指定的单位
        if target_unit:
            # 检查是否是特殊单位
            if target_unit in cls.SPECIAL_UNITS:
                return cls.SPECIAL_UNITS[target_unit]['format'](value)

            # 尝试解析标准单位
            unit_info, factor, is_binary = cls._parse_unit_prefix(target_unit)

            # 如果无法识别单位，直接附加原单位
            if unit_info is None:
                return f"{value:.2f} {target_unit}"
            
            # 标准单位转换（从字节转换到目标单位）
            converted_value = value / factor
            return f"{converted_value:.2f} {unit_info}"

        # 没有指定目标单位时，自动选择合适的单位
        units = cls.BINARY_UNITS if use_binary else cls.DECIMAL_UNITS

        abs_value = abs(value)
        for factor, unit in units:
            if abs_value >= factor:
                converted_value = value / factor
                return f"{converted_value:.2f} {unit}"

        return f"{value:.2f}"


class StorageCalculator:
    """存储计算器核心类"""
    
    def __init__(self, formula_dir='formulas'):
        """初始化计算器
        
        Args:
            formula_dir: 配置目录路径（相对于脚本目录或绝对路径）
        """
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 处理formula_dir路径
        if os.path.isabs(formula_dir):
            self.formula_dir = formula_dir
        else:
            self.formula_dir = os.path.join(self.script_dir, formula_dir)
        
        logger.debug(f"配置目录路径: {self.formula_dir}")

        self._calculated_values = {}
        self._last_config = None
        self.unit_converter = UnitConverter()

        self.variables = {}
        self.formulas = {}
        self.config = {}
        self.display_columns = {}

        self.load_config()

    def _config_has_changed(self, new_config):
        """检查配置是否发生变化"""
        if new_config is None:
            return False
        if self._last_config is None:
            return True

        try:
            sections = ['global', 'variables', 'formulas']
            for section in sections:
                if (section in new_config) != (section in self._last_config):
                    return True
                if section in new_config and new_config[section] != self._last_config[section]:
                    return True
            return False
        except Exception:
            return False

    def load_config(self):
        """加载配置文件"""
        try:
            if not os.path.exists(self.formula_dir):
                logger.error(f"配置目录不存在: {self.formula_dir}")
                return False

            merged_config = {
                'global': {},
                'variables': {},
                'formulas': {},
            }

            yaml_files = [f for f in os.listdir(self.formula_dir) if f.endswith('.yaml')]
            if not yaml_files:
                logger.error("配置目录下没有找到yaml文件")
                return False

            yaml_files.sort()

            for yaml_file in yaml_files:
                file_path = os.path.join(self.formula_dir, yaml_file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                        if not config:
                            continue

                        for section in ['global', 'variables', 'formulas']:
                            if section in config:
                                merged_config[section].update(config[section])

                    logger.debug(f"已加载配置文件: {yaml_file}")

                except yaml.YAMLError as e:
                    logger.error(f"YAML格式错误 {yaml_file}: {str(e)}")
                    continue

            if not any(merged_config.values()):
                logger.error("没有找到有效的配置")
                return False

            if not self._config_has_changed(merged_config):
                return True

            self.config = merged_config
            self._last_config = merged_config.copy()

            self.load_defaults()
            self.load_variables()
            self.load_formulas()

            logger.info("配置加载完成")
            return True

        except Exception as e:
            logger.error(f"加载配置文件出错: {str(e)}")
            return False

    def load_defaults(self):
        """加载默认值"""
        defaults = self.config.get('global', {}).get('defaults', {})
        for var, value in defaults.items():
            parsed_value = self.unit_converter.parse_value(value)
            if parsed_value is not None:
                self._calculated_values[var] = parsed_value
            else:
                self._calculated_values[var] = value

    def load_variables(self):
        """加载变量定义"""
        self.variables = {}
        for var_name, var_info in self.config.get('variables', {}).items():
            self.variables[var_name] = {
                'description': var_info.get('description', ''),
                'unit': var_info.get('unit', ''),
                'display_name': var_info.get('excel_column', var_name),
                'can_be_input': var_info.get('can_be_input', False)
            }

    def load_formulas(self):
        """加载公式定义"""
        self.formulas = {}
        self.display_columns = {}

        for name, formula_data in self.config.get('formulas', {}).items():
            if 'expression' not in formula_data:
                logger.error(f"公式 {name} 缺少expression，跳过")
                continue
            try:
                expr_str = formula_data['expression']
                expr_str = expr_str.split('=')[1].strip()
                expr = parse_expr(expr_str)
                variables = [str(symbol) for symbol in expr.free_symbols]

                display_name = formula_data.get('excel_column', name)
                
                self.formulas[name] = {
                    'equation': Eq(Symbol(name), expr),
                    'variables': set(variables),
                    'display_name': display_name,
                    'unit': formula_data.get('unit', ''),
                    'expression': formula_data['expression']
                }

                self.display_columns[display_name] = name

                logger.debug(f"已加载公式 {name}, 变量: {variables}")

            except Exception as e:
                logger.error(f"解析公式 {name} 时出错: {str(e)}")

    def get_input_variables(self):
        """获取所有可输入的变量"""
        return {
            name: info for name, info in self.variables.items()
            if info.get('can_be_input', False)
        }

    def get_output_formulas(self):
        """获取所有输出公式"""
        return self.formulas

    def get_defaults(self):
        """获取默认值"""
        return self.config.get('global', {}).get('defaults', {})

    def calculate(self, input_data):
        """执行计算
        
        Args:
            input_data: 输入数据字典，键可以是变量名或显示名
            
        Returns:
            计算结果字典
        """
        if not input_data:
            return None

        try:
            # 【关键修复】清除之前行的计算结果，只保留全局默认值
            config_defaults = self.config.get('global', {}).get('defaults', {})
            preserved_defaults = {}
            for var_name in config_defaults:
                if var_name in self._calculated_values:
                    preserved_defaults[var_name] = self._calculated_values[var_name]
            self._calculated_values = preserved_defaults.copy()

            known_values = {}

            # 处理输入数据
            for var_name, var_info in self.variables.items():
                if var_info['can_be_input']:
                    display_name = var_info['display_name']
                    
                    # 尝试通过变量名或显示名获取值（检查空值）
                    value = None
                    if var_name in input_data and input_data[var_name] not in (None, '', 'nan'):
                        value = input_data[var_name]
                    elif display_name in input_data and input_data[display_name] not in (None, '', 'nan'):
                        value = input_data[display_name]

                    if value is not None:
                        parsed_value = self.unit_converter.parse_value(value)
                        if parsed_value is not None:
                            known_values[var_name] = float(parsed_value)

            # 使用默认值填充
            for var_name in self.variables:
                if var_name not in known_values and var_name in self._calculated_values:
                    known_values[var_name] = self._calculated_values[var_name]

            if not known_values:
                return None

            # 迭代求解
            equation_deps = {}
            for name, formula_data in self.formulas.items():
                if name not in known_values:
                    equation_deps[name] = {
                        'equation': formula_data['equation'],
                        'variables': set(formula_data['variables']),
                        'solved': False
                    }

            results = known_values.copy()

            while True:
                made_progress = False
                for name, eq_data in equation_deps.items():
                    if eq_data['solved']:
                        continue

                    if all(var in results for var in eq_data['variables']):
                        try:
                            eq = eq_data['equation']
                            subs_dict = {Symbol(var): results[var] for var in eq_data['variables']}
                            solution = solve(eq.subs(subs_dict))
                            if solution:
                                results[name] = float(solution[0])
                                eq_data['solved'] = True
                                made_progress = True
                        except Exception as e:
                            logger.warning(f"求解方程 {name} 失败: {str(e)}")

                if not made_progress:
                    break

            self._calculated_values.update(results)
            return results

        except Exception as e:
            logger.error(f"计算过程出错: {str(e)}")
            return None

    def format_result(self, name, value):
        """格式化单个结果值"""
        if name in self.formulas:
            unit = self.formulas[name].get('unit', '')
            if unit:
                use_binary = 'i' in unit.lower()
                return self.unit_converter.format_value(value, unit, use_binary)
        return f"{value:.4f}" if isinstance(value, float) else str(value)

    def format_results(self, results):
        """格式化所有结果"""
        if not results:
            return {}
        
        formatted = {}
        for name, value in results.items():
            formatted[name] = self.format_result(name, value)
        return formatted

    def get_column_to_variable_map(self):
        """获取列名到变量名的映射"""
        column_map = {}
        
        # 从变量定义中获取映射
        for var_name, var_info in self.variables.items():
            display_name = var_info.get('display_name', var_name)
            column_map[display_name] = var_name
            column_map[var_name] = var_name  # 也支持直接用变量名
        
        # 从公式定义中获取映射
        for name, formula_data in self.formulas.items():
            display_name = formula_data.get('display_name', name)
            column_map[display_name] = name
            column_map[name] = name
        
        return column_map

    def get_variable_to_column_map(self):
        """获取变量名到列名的映射"""
        var_map = {}
        
        for var_name, var_info in self.variables.items():
            var_map[var_name] = var_info.get('display_name', var_name)
        
        for name, formula_data in self.formulas.items():
            var_map[name] = formula_data.get('display_name', name)
        
        return var_map

    def calculate_with_columns(self, row_data, column_map=None, row_index=None):
        """根据列名进行计算，自动识别公式

        Args:
            row_data: 行数据字典，键为列名（显示名）
            column_map: 列名到变量名的映射，如果为None则自动生成
            row_index: data_editor中的行索引（用于日志记录）

        Returns:
            计算结果字典，键为变量名
        """
        if not row_data:
            return None

        if column_map is None:
            column_map = self.get_column_to_variable_map()

        try:
            row_info = f" (data_editor 第 {row_index} 行)" if row_index is not None else ""
            logger.info("=" * 80)
            logger.info(f"开始新的计算过程{row_info}")
            logger.info("=" * 80)

            # 【关键修复】清除之前行的计算结果，只保留全局默认值
            # 获取配置中定义的默认值
            config_defaults = self.config.get('global', {}).get('defaults', {})
            # 只保留默认值，清除上一行的计算结果
            preserved_defaults = {}
            for var_name in config_defaults:
                if var_name in self._calculated_values:
                    preserved_defaults[var_name] = self._calculated_values[var_name]
            # 重置 _calculated_values 为仅包含默认值
            self._calculated_values = preserved_defaults.copy()
            logger.debug(f"已重置计算状态，保留的默认值: {list(preserved_defaults.keys())}")

            known_values = {}

            # 只处理输入变量，不处理输出公式列
            logger.info(f"\n【步骤1: 读取输入数据{row_info}】")
            for var_name, var_info in self.variables.items():
                if var_info.get('can_be_input', False):
                    # 获取该变量的显示名
                    display_name = var_info.get('display_name', var_name)

                    # 尝试从row_data中获取值（显示名优先，然后是变量名）
                    value = None
                    if display_name in row_data and row_data[display_name] not in (None, '', 'nan'):
                        value = row_data[display_name]
                    elif var_name in row_data and row_data[var_name] not in (None, '', 'nan'):
                        value = row_data[var_name]

                    if value is not None and not (isinstance(value, str) and not value.strip()):
                        parsed_value = self.unit_converter.parse_value(value)
                        if parsed_value is not None:
                            known_values[var_name] = float(parsed_value)
                            logger.info(f"  从输入列读取{row_info}: {var_name} = {parsed_value} (原始值: {value})")

            # 使用默认值填充
            logger.info("\n【步骤2: 应用默认值】")
            for var_name in self.variables:
                if var_name not in known_values and var_name in self._calculated_values:
                    known_values[var_name] = self._calculated_values[var_name]
                    logger.info(f"  使用默认值: {var_name} = {self._calculated_values[var_name]}")

            if not known_values:
                logger.warning("没有有效的已知值，跳过计算")
                return None

            logger.info(f"\n【已知值汇总】")
            for var, val in known_values.items():
                logger.info(f"  {var} = {val}")

            # 迭代求解（与原calculate方法相同）
            logger.info("\n【步骤3: 构建方程依赖关系】")
            equation_deps = {}
            for name, formula_data in self.formulas.items():
                if name not in known_values:
                    equation_deps[name] = {
                        'equation': formula_data['equation'],
                        'variables': set(formula_data['variables']),
                        'solved': False
                    }
                    logger.info(f"  方程 {name} 依赖变量: {formula_data['variables']}")

            results = known_values.copy()

            logger.info("\n【步骤4: 迭代求解方程】")
            iteration = 0
            while True:
                iteration += 1
                logger.info(f"\n  --- 第 {iteration} 轮迭代 ---")
                made_progress = False

                for name, eq_data in equation_deps.items():
                    if eq_data['solved']:
                        continue

                    if all(var in results for var in eq_data['variables']):
                        try:
                            eq = eq_data['equation']
                            logger.info(f"\n  求解方程: {name}")
                            logger.info(f"    原始方程: {eq}")

                            # 打印代入步骤
                            logger.info(f"    代入步骤:")
                            subs_dict = {Symbol(var): results[var] for var in eq_data['variables']}
                            for var, val in subs_dict.items():
                                logger.info(f"      {var} = {val}")

                            # 打印代入后的表达式
                            substituted_eq = eq.subs(subs_dict)
                            logger.info(f"    代入后的方程: {substituted_eq}")

                            # 求解
                            solution = solve(substituted_eq)
                            if solution:
                                float_value = float(solution[0])
                                results[name] = float_value
                                eq_data['solved'] = True
                                made_progress = True
                                logger.info(f"    ✓ 求解成功: {name} = {float_value}")
                            else:
                                logger.warning(f"    ✗ 无解: {name}")
                        except Exception as e:
                            logger.warning(f"    ✗ 求解方程 {name} 失败: {str(e)}")
                    else:
                        missing_vars = [var for var in eq_data['variables'] if var not in results]
                        logger.debug(f"  方程 {name} 缺少变量: {missing_vars}，暂时跳过")

                if not made_progress:
                    logger.info(f"\n  第 {iteration} 轮迭代无进展，终止求解")
                    break

            # 报告未能求解的方程
            unsolved = [name for name, data in equation_deps.items() if not data['solved']]
            if unsolved:
                logger.warning(f"\n【警告】以下方程无法求解: {unsolved}")

            logger.info("\n【步骤5: 计算结果汇总】")
            for name in self.formulas.keys():
                if name in results:
                    logger.info(f"  {name} = {results[name]}")

            logger.info("\n" + "=" * 80)
            logger.info("计算过程结束")
            logger.info("=" * 80 + "\n")

            self._calculated_values.update(results)
            return results

        except Exception as e:
            logger.error(f"计算过程出错: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    def get_all_known_columns(self):
        """获取所有已知的列名（变量和公式的显示名）"""
        columns = set()
        
        for var_name, var_info in self.variables.items():
            columns.add(var_info.get('display_name', var_name))
        
        for name, formula_data in self.formulas.items():
            columns.add(formula_data.get('display_name', name))
        
        return list(columns)

    def identify_column_type(self, column_name):
        """识别列名的类型
        
        Returns:
            tuple: (type, var_name) 
            type: 'input' | 'output' | 'unknown'
            var_name: 对应的变量名或None
        """
        # 检查是否是输入变量
        for var_name, var_info in self.variables.items():
            display_name = var_info.get('display_name', var_name)
            if column_name == display_name or column_name == var_name:
                if var_info.get('can_be_input', False):
                    return ('input', var_name)
        
        # 检查是否是输出公式
        for name, formula_data in self.formulas.items():
            display_name = formula_data.get('display_name', name)
            if column_name == display_name or column_name == name:
                return ('output', name)
        
        return ('unknown', None)

