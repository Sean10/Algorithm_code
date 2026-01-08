"""
存储容量计算器 - Streamlit Web 前端
"""
import streamlit as st
import pandas as pd
import io
import os
from calculator_core import StorageCalculator, UnitConverter

# 页面配置
st.set_page_config(
    page_title="存储容量计算器",
    page_icon="💾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    /* 主题色调 - 深蓝科技风 */
    :root {
        --primary-color: #0066cc;
        --secondary-color: #00a8e8;
        --bg-dark: #1a1a2e;
        --bg-card: #16213e;
        --text-light: #e8e8e8;
    }
    
    /* 标题样式 */
    .main-title {
        font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }
    
    .sub-title {
        font-family: 'SF Pro Text', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #888;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    
    /* 卡片样式 */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* 侧边栏样式 */
    .css-1d391kg {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    
    /* 按钮样式 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* 指标卡片 */
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
    }
    
    /* 公式展示区 */
    .formula-box {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
        font-family: 'JetBrains Mono', monospace;
    }
    
    /* 分隔线 */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_calculator():
    """获取计算器实例（缓存）"""
    return StorageCalculator()


def reload_calculator():
    """重新加载计算器"""
    st.cache_resource.clear()
    return get_calculator()


def render_sidebar(calculator):
    """渲染侧边栏配置面板"""
    st.sidebar.markdown("## ⚙️ 全局配置")
    
    # 默认值配置
    st.sidebar.markdown("### 默认参数")
    defaults = calculator.get_defaults()
    modified_defaults = {}
    
    for var_name, default_value in defaults.items():
        var_info = calculator.variables.get(var_name, {})
        unit = var_info.get('unit', '')
        display_name = var_info.get('display_name', var_name)
        
        help_text = f"变量: {var_name}"
        if unit:
            help_text += f", 单位: {unit}"
        help_text += "\n支持: 3.84, 3.84TB, 960G 等格式"
        
        # 创建文本输入框，支持带单位输入
        new_value = st.sidebar.text_input(
            f"{display_name}",
            value=str(default_value) if default_value else "",
            help=help_text,
            key=f"default_{var_name}"
        )
        
        # 解析输入值（支持带单位）
        if new_value:
            parsed = UnitConverter.parse_value(new_value)
            modified_defaults[var_name] = parsed if parsed is not None else 0
        else:
            modified_defaults[var_name] = 0
    
    st.sidebar.markdown("---")
    
    # 公式信息
    with st.sidebar.expander("📐 公式列表", expanded=False):
        for name, formula_data in calculator.get_output_formulas().items():
            st.markdown(f"**{formula_data['display_name']}**")
            st.code(formula_data['expression'], language=None)
            if formula_data.get('unit'):
                st.caption(f"单位: {formula_data['unit']}")
            st.markdown("---")
    
    # 操作按钮
    st.sidebar.markdown("### 操作")
    if st.sidebar.button("🔄 重新加载配置", use_container_width=True):
        reload_calculator()
        st.rerun()
    
    return modified_defaults


def create_input_dataframe(calculator, modified_defaults):
    """创建输入数据框"""
    input_vars = calculator.get_input_variables()
    output_formulas = calculator.get_output_formulas()
    
    # 构建列配置
    columns = []
    column_config = {}
    
    # 添加输入变量列 - 使用 TextColumn 支持带单位输入（如 3.84TB, 960G）
    for var_name, var_info in input_vars.items():
        display_name = var_info['display_name']
        columns.append(display_name)
        
        unit = var_info.get('unit', '')
        help_text = f"变量: {var_name}"
        if unit:
            help_text += f"\n单位: {unit}"
        help_text += "\n支持输入: 3.84, 3.84TB, 960G, 0.9 等格式"
        
        column_config[display_name] = st.column_config.TextColumn(
            display_name,
            help=help_text,
            default=""
        )
    
    # 添加输出公式列
    for name, formula_data in output_formulas.items():
        display_name = formula_data['display_name']
        if display_name not in columns:
            columns.append(display_name)
            column_config[display_name] = st.column_config.TextColumn(
                display_name,
                help=f"公式: {formula_data['expression']}",
                disabled=True
            )
    
    return columns, column_config


def calculate_row(calculator, row_data, modified_defaults):
    """计算单行数据"""
    # 合并默认值和行数据
    input_data = modified_defaults.copy()
    for key, value in row_data.items():
        if pd.notna(value) and value != '':
            input_data[key] = value
    
    results = calculator.calculate(input_data)
    return results


def main():
    """主函数"""
    # 获取计算器
    calculator = get_calculator()
    
    # 标题
    st.markdown('<h1 class="main-title">存储容量计算器</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">基于公式配置的存储参数计算工具</p>', unsafe_allow_html=True)
    
    # 渲染侧边栏并获取修改后的默认值
    modified_defaults = render_sidebar(calculator)
    
    # 主内容区
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 📊 数据表格")
        st.caption("编辑输入参数，系统将自动计算结果。支持输入带单位的值，如: `3.84TB`, `960GB`, `3.2TiB`, `0.9` 等")
    
    with col2:
        auto_calc = st.checkbox("自动计算", value=True, help="编辑后自动触发计算")
    
    # 创建数据框配置
    columns, column_config = create_input_dataframe(calculator, modified_defaults)
    
    # 初始化或获取session state中的数据
    if 'df' not in st.session_state:
        # 创建初始数据框，包含一行默认数据（字符串格式，支持带单位）
        initial_data = {}
        input_vars = calculator.get_input_variables()
        for var_name, var_info in input_vars.items():
            display_name = var_info['display_name']
            default_val = modified_defaults.get(var_name, 0)
            # 转为字符串，保留小数
            initial_data[display_name] = [str(default_val) if default_val else '']
        
        # 添加输出列（空值）
        for name, formula_data in calculator.get_output_formulas().items():
            display_name = formula_data['display_name']
            if display_name not in initial_data:
                initial_data[display_name] = ['']
        
        st.session_state.df = pd.DataFrame(initial_data)
    
    # 可编辑数据表格
    edited_df = st.data_editor(
        st.session_state.df,
        column_config=column_config,
        num_rows="dynamic",
        use_container_width=True,
        key="data_editor"
    )
    
    # 计算按钮
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        calc_button = st.button("🔢 计算", type="primary", use_container_width=True)
    
    with col2:
        clear_button = st.button("🗑️ 清空结果", use_container_width=True)
    
    # 处理清空
    if clear_button:
        output_formulas = calculator.get_output_formulas()
        for name, formula_data in output_formulas.items():
            display_name = formula_data['display_name']
            if display_name in edited_df.columns:
                edited_df[display_name] = ''
        st.session_state.df = edited_df
        st.rerun()
    
    # 执行计算
    if calc_button or auto_calc:
        input_vars = calculator.get_input_variables()
        output_formulas = calculator.get_output_formulas()
        
        # 逐行计算
        result_df = edited_df.copy()
        
        for idx, row in edited_df.iterrows():
            row_data = row.to_dict()
            results = calculate_row(calculator, row_data, modified_defaults)
            
            if results:
                # 更新结果列
                for name, formula_data in output_formulas.items():
                    display_name = formula_data['display_name']
                    if name in results:
                        formatted = calculator.format_result(name, results[name])
                        result_df.at[idx, display_name] = formatted
        
        st.session_state.df = result_df
        
        # 只在点击按钮时rerun，自动计算时不rerun避免循环
        if calc_button:
            st.rerun()
    
    st.markdown("---")
    
    # 数据导入导出区域
    st.markdown("### 📁 数据导入/导出")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 导入数据")
        uploaded_file = st.file_uploader(
            "选择CSV或Excel文件",
            type=['csv', 'xlsx', 'xls'],
            help="上传包含输入参数的文件"
        )
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    import_df = pd.read_csv(uploaded_file)
                else:
                    import_df = pd.read_excel(uploaded_file)
                
                # 确保所有必要的列都存在
                for col in columns:
                    if col not in import_df.columns:
                        import_df[col] = ''
                
                st.session_state.df = import_df[columns]
                st.success(f"成功导入 {len(import_df)} 行数据")
                st.rerun()
            except Exception as e:
                st.error(f"导入失败: {str(e)}")
    
    with col2:
        st.markdown("#### 导出数据")
        
        export_format = st.radio(
            "选择导出格式",
            ["CSV", "Excel"],
            horizontal=True
        )
        
        if st.button("📥 导出数据", use_container_width=True):
            try:
                if export_format == "CSV":
                    csv_data = st.session_state.df.to_csv(index=False)
                    st.download_button(
                        label="下载 CSV 文件",
                        data=csv_data,
                        file_name="storage_calculation_results.csv",
                        mime="text/csv"
                    )
                else:
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        st.session_state.df.to_excel(writer, index=False, sheet_name='计算结果')
                    
                    st.download_button(
                        label="下载 Excel 文件",
                        data=buffer.getvalue(),
                        file_name="storage_calculation_results.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            except Exception as e:
                st.error(f"导出失败: {str(e)}")
    
    st.markdown("---")
    
    # 计算结果可视化
    if len(st.session_state.df) > 0:
        st.markdown("### 📈 结果可视化")
        
        output_formulas = calculator.get_output_formulas()
        numeric_columns = []
        
        # 找出可以可视化的数值列
        for name, formula_data in output_formulas.items():
            display_name = formula_data['display_name']
            if display_name in st.session_state.df.columns:
                try:
                    # 尝试提取数值
                    col_data = st.session_state.df[display_name].apply(
                        lambda x: float(str(x).split()[0]) if pd.notna(x) and str(x).strip() else None
                    )
                    if col_data.notna().any():
                        numeric_columns.append((display_name, col_data))
                except:
                    pass
        
        if numeric_columns:
            # 选择要可视化的列
            selected_cols = st.multiselect(
                "选择要可视化的指标",
                [col[0] for col in numeric_columns],
                default=[numeric_columns[0][0]] if numeric_columns else []
            )
            
            if selected_cols:
                chart_data = pd.DataFrame()
                for col_name, col_data in numeric_columns:
                    if col_name in selected_cols:
                        chart_data[col_name] = col_data
                
                chart_data['行号'] = range(1, len(chart_data) + 1)
                chart_data = chart_data.set_index('行号')
                
                st.bar_chart(chart_data)
        else:
            st.info("暂无可视化数据，请先执行计算")
    
    # 页脚
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #888; font-size: 0.8rem;">'
        '存储容量计算器 v1.0 | 基于 Streamlit 构建'
        '</p>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()

