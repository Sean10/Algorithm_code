import pytest
from storage_calculator import UnitConverter, StorageCalculator
import sympy
import yaml
import os
import re

@pytest.fixture
def sample_config(tmp_path):
    """创建临时配置文件"""
    config_content = """
    global:
      defaults:
        base_value: 100
        throughput: 256
    variables:
      input_var:
        unit: "MB"
        excel_column: "输入列1"
        can_be_input: true
      input_with_unit:
        unit: "GB"
        excel_column: "输入列2"
        can_be_input: true
    formulas:
      test_formula:
        expression: "output = input_var * 2 + input_with_unit"
        output_variable: "output"
        excel_column: "输出列"
        unit: "TB"
    """
    config_file = tmp_path / "test_config.yaml"
    config_file.write_text(config_content)
    return str(config_file)

@pytest.fixture
def calculator(sample_config):
    """创建带测试配置的计算器实例"""
    return StorageCalculator(formula_file=sample_config)

class TestUnitConverter:
    """测试单位转换器"""

    @pytest.mark.parametrize("input_value, expected", [
        # 二进制单位测试
        ("1024KiB", 1024*1024),
        ("2MiB", 2*1024**2),
        ("1.5GiB", 1.5*1024**3),
        # 十进制单位测试
        ("1000KB", 1000*1000),
        ("3TB", 3*1000**4),
        # 科学计数法
        ("2.5e3MB", 2.5e3*1000**2),
        ("1.2E2GB", 1.2e2*1000**3),
        # 特殊单位
        ("95%", 0.95),
        ("5个", 5),
        # 无单位
        ("2048", 2048),
        # 混合写法
        ("1.5TIB", 1.5*1024**4),
        ("500mib", 500*1024**2),
    ])
    def test_parse_value(self, input_value, expected):
        assert UnitConverter.parse_value(input_value) == pytest.approx(expected, rel=1e-3)

    @pytest.mark.parametrize("invalid_input", [
        "invalid12MB",     # 无效数字格式
        "12.3.4GB",        # 错误的小数
        "500InvalidUnit",  # 无效单位
        "",                 # 空输入
        None
    ])
    def test_parse_invalid_values(self, invalid_input):
        assert UnitConverter.parse_value(invalid_input) is None

    @pytest.mark.parametrize("input_value, expected", [
        ("12.3.4GB", None),  # 错误的小数格式
        ("500InvalidUnit", None),  # 无效单位
        ("", None),  # 空输入
        ("1024KiB", 1024*1024),  # 二进制单位
        ("95%", 0.95),  # 百分比单位
        ("1.5e3GiB", 1.5e3*1024**3),  # 科学计数法+单位
    ])
    def test_edge_cases(self, input_value, expected):
        assert UnitConverter.parse_value(input_value) == pytest.approx(expected, rel=1e-3)

class TestStorageCalculator:
    """测试存储计算器核心逻辑"""

    def test_config_loading(self, calculator):
        """测试配置加载是否正确"""
        assert 'test_formula' in calculator.formulas
        assert calculator.variables['input_var']['unit'] == 'MB'

    def test_basic_calculation(self, calculator):
        """测试基本公式计算"""
        # 设置输入值（带不同单位）
        calculator._calculated_values.update({
            'input_var': UnitConverter.parse_value("100MB"),  # 100,000,000 B
            'input_with_unit': UnitConverter.parse_value("1GB")  # 1,000,000,000 B
        })

        # 执行计算
        result = calculator.calculate_with_formula('test_formula')

        # 验证结果：100,000,000*2 + 1,000,000,000 = 1,200,000,000
        assert result == pytest.approx(1.2e9)

    def test_excel_data_processing(self, calculator):
        """测试Excel数据处理逻辑"""
        # 模拟Excel行数据（带单位）
        row_data = {
            'input_var': '200MiB',  # 200*1024^2 = 209,715,200
            'input_with_unit': '0.5TB'  # 0.5*1000^4 = 5e11
        }

        # 更新计算值
        calculator.update_from_excel_row(row_data)

        # 验证解析结果
        assert calculator._calculated_values['input_var'] == pytest.approx(209715200)
        assert calculator._calculated_values['input_with_unit'] == pytest.approx(5e11)

    def test_missing_variable_handling(self, calculator):
        """测试缺失变量时的错误处理"""
        with pytest.raises(ValueError) as excinfo:
            calculator.calculate_with_formula('test_formula')

        assert "缺少变量" in str(excinfo.value)

    def test_unit_priority(self, calculator):
        """测试单元格单位优先于配置单位"""
        # 配置中的单位是GB，但单元格指定MB
        row_data = {'input_with_unit': '1000MB'}  # 应解析为1,000,000,000 B
        calculator.update_from_excel_row(row_data)

        assert calculator._calculated_values['input_with_unit'] == 1e9

    def test_formula_dependency_resolution(self, calculator):
        """测试公式依赖解析"""
        # 添加复杂公式
        calculator.formulas['complex'] = {
            'equation': sympy.Eq(sympy.Symbol('final'),
                               sympy.Symbol('a') + sympy.Symbol('b') * 2),
            'variables': {'a', 'b'},
            'output_variable': 'final'
        }

        # 设置已知变量
        calculator._calculated_values.update({'a': 10, 'b': 20})

        # 计算结果应为10 + 20*2 = 50
        assert calculator.calculate_all_formulas({})['final'] == 50

# 性能测试（可选）
class TestPerformance:
    """性能测试类"""

    @pytest.mark.benchmark
    def test_calculation_performance(self, benchmark):
        """测试计算性能"""
        calc = StorageCalculator()
        benchmark(calc.calculate_all_formulas, {
            'nvme_capacity': '10TB',
            'nvme_count': 5,
            'data_blocks': 10,
            'parity_blocks': 2
    