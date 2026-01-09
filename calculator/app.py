"""
存储容量计算器 - Streamlit Web 前端
支持数据持久化、列名编辑、自动公式识别
"""
import streamlit as st
import pandas as pd
import io
import os
import time
import threading
from datetime import datetime
from pathlib import Path
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from calculator_core import StorageCalculator, UnitConverter

# 数据文件路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, "calc_data.xlsx")
BACKUP_DIR = os.path.join(SCRIPT_DIR, "backups")
FORMULA_DIR = os.path.join(SCRIPT_DIR, "formulas")


class FormulaWatcher(FileSystemEventHandler):
    """配置文件监听器"""

    def __init__(self, formula_dir):
        self.formula_dir = os.path.abspath(formula_dir)
        self.last_modified = {}  # 改为字典，分别记录每个文件的修改时间

    def on_modified(self, event):
        """检测到文件修改时触发"""
        # 只监听 yaml 文件的修改
        if not event.src_path.endswith('.yaml'):
            return

        if os.path.dirname(event.src_path) != self.formula_dir:
            return

        current_time = time.time()
        file_path = event.src_path

        # 防抖：1秒内同一文件只触发一次
        if file_path in self.last_modified:
            if current_time - self.last_modified[file_path] < 1:
                return

        self.last_modified[file_path] = current_time

        # 清除缓存，触发重新加载
        st.cache_resource.clear()
        # 设置重载标记
        if 'config_reload_trigger' not in st.session_state:
            st.session_state.config_reload_trigger = 0
        st.session_state.config_reload_trigger += 1


def start_formula_watcher():
    """启动配置文件监听器"""
    try:
        # 如果已存在，则跳过
        if 'formula_observer' in st.session_state:
            return

        event_handler = FormulaWatcher(FORMULA_DIR)
        observer = Observer()
        observer.schedule(event_handler, FORMULA_DIR, recursive=False)
        observer.start()
        st.session_state.formula_observer = observer
        st.session_state.formula_watcher = event_handler
    except Exception as e:
        # 如果监听器已存在，静默忽略
        if "already scheduled" not in str(e):
            st.error(f"启动配置文件监听失败: {str(e)}")


def stop_formula_watcher():
    """停止配置文件监听器"""
    if 'formula_observer' in st.session_state:
        try:
            st.session_state.formula_observer.stop()
            st.session_state.formula_observer.join(timeout=1)
            del st.session_state.formula_observer
            if 'formula_watcher' in st.session_state:
                del st.session_state.formula_watcher
        except Exception as e:
            pass  # 静默忽略停止时的错误

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
    
    /* 列管理区域 */
    .column-tag {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        margin: 0.1rem;
        border-radius: 4px;
        font-size: 0.8rem;
    }
    .column-input {
        background: #e3f2fd;
        color: #1565c0;
    }
    .column-output {
        background: #e8f5e9;
        color: #2e7d32;
    }
    .column-unknown {
        background: #fff3e0;
        color: #ef6c00;
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


def load_data_from_file(file_path=DATA_FILE):
    """从文件加载数据"""
    if os.path.exists(file_path):
        try:
            df = pd.read_excel(file_path)
            # 将所有列转为字符串类型，便于编辑
            for col in df.columns:
                df[col] = df[col].astype(str).replace('nan', '')
            return df
        except Exception as e:
            st.error(f"加载数据文件失败: {str(e)}")
    return None


def save_data_to_file(df, file_path=DATA_FILE, create_backup=True):
    """保存数据到文件"""
    try:
        # 创建备份
        if create_backup and os.path.exists(file_path):
            if not os.path.exists(BACKUP_DIR):
                os.makedirs(BACKUP_DIR)
            backup_name = f"calc_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            backup_path = os.path.join(BACKUP_DIR, backup_name)
            # 复制当前文件作为备份
            import shutil
            shutil.copy2(file_path, backup_path)
        
        # 保存数据
        df.to_excel(file_path, index=False, sheet_name='计算数据')
        return True
    except Exception as e:
        st.error(f"保存数据失败: {str(e)}")
        return False


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
        
        new_value = st.sidebar.text_input(
            f"{display_name}",
            value=str(default_value) if default_value else "",
            help=help_text,
            key=f"default_{var_name}"
        )
        
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
    
    # 已知列名映射
    with st.sidebar.expander("📋 列名映射", expanded=False):
        column_map = calculator.get_column_to_variable_map()
        var_to_col = calculator.get_variable_to_column_map()
        
        st.markdown("**输入变量:**")
        for var_name, var_info in calculator.variables.items():
            if var_info.get('can_be_input', False):
                col_name = var_to_col.get(var_name, var_name)
                st.markdown(f"- `{col_name}` → {var_name}")
        
        st.markdown("**输出公式:**")
        for name in calculator.formulas.keys():
            col_name = var_to_col.get(name, name)
            st.markdown(f"- `{col_name}` → {name}")
    
    # 操作按钮
    st.sidebar.markdown("### 操作")
    col1, col2 = st.sidebar.columns(2)

    with col1:
        if st.button("🔄 重新加载配置", key="reload_config", use_container_width=True):
            reload_calculator()
            st.rerun()

    with col2:
        if st.button("⏸️ 停止监听", key="stop_watcher", use_container_width=True):
            stop_formula_watcher()
            st.success("已停止配置文件监听")

    return modified_defaults


def render_column_manager(calculator, current_columns):
    """渲染列管理器"""
    st.markdown("### 📝 列管理")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        st.markdown("**当前列（点击标签查看类型）:**")
        column_html = ""
        for col in current_columns:
            col_type, var_name = calculator.identify_column_type(col)
            if col_type == 'input':
                column_html += f'<span class="column-tag column-input" title="输入变量: {var_name}">{col}</span> '
            elif col_type == 'output':
                column_html += f'<span class="column-tag column-output" title="输出公式: {var_name}">{col}</span> '
            else:
                column_html += f'<span class="column-tag column-unknown" title="未识别">{col}</span> '
        st.markdown(column_html, unsafe_allow_html=True)
        st.caption("🔵输入变量 🟢输出公式 🟠未识别")
    
    with col2:
        # 添加新列
        known_columns = calculator.get_all_known_columns()
        available_columns = [c for c in known_columns if c not in current_columns]
        
        if available_columns:
            new_col = st.selectbox(
                "添加已知列",
                options=[""] + available_columns,
                key="add_known_col"
            )
            if st.button("➕ 添加列", key="btn_add_known"):
                if new_col:
                    return ('add', new_col)
        
        # 添加自定义列
        custom_col = st.text_input("或输入自定义列名", key="custom_col_name")
        if st.button("➕ 添加自定义列", key="btn_add_custom"):
            if custom_col and custom_col not in current_columns:
                return ('add', custom_col)
    
    with col3:
        # 删除列
        col_to_delete = st.selectbox(
            "选择要删除的列",
            options=[""] + list(current_columns),
            key="col_to_delete"
        )
        if st.button("🗑️ 删除列", key="btn_delete_col"):
            if col_to_delete:
                return ('delete', col_to_delete)
    
    return None


def render_column_rename(current_columns):
    """渲染列重命名功能"""
    with st.expander("✏️ 重命名列", expanded=False):
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            old_name = st.selectbox(
                "选择要重命名的列",
                options=[""] + list(current_columns),
                key="rename_old"
            )
        
        with col2:
            new_name = st.text_input("新列名", key="rename_new")
        
        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("确认重命名", key="btn_rename"):
                if old_name and new_name and new_name != old_name:
                    return (old_name, new_name)
    
    return None


def calculate_row(calculator, row_data, modified_defaults):
    """计算单行数据"""
    # 合并默认值和行数据
    input_data = modified_defaults.copy()
    for key, value in row_data.items():
        if pd.notna(value) and value != '' and value != 'nan':
            input_data[key] = value
    
    # 使用新的列名感知计算方法
    results = calculator.calculate_with_columns(input_data)
    return results


def create_default_dataframe(calculator, modified_defaults):
    """创建默认数据框"""
    input_vars = calculator.get_input_variables()
    output_formulas = calculator.get_output_formulas()
    
    initial_data = {}
    
    # 添加输入变量列
    for var_name, var_info in input_vars.items():
        display_name = var_info['display_name']
        default_val = modified_defaults.get(var_name, 0)
        initial_data[display_name] = [str(default_val) if default_val else '']
    
    # 添加输出列
    for name, formula_data in output_formulas.items():
        display_name = formula_data['display_name']
        if display_name not in initial_data:
            initial_data[display_name] = ['']
    
    return pd.DataFrame(initial_data)


def main():
    """主函数"""
    # 启动配置文件监听器（只启动一次）
    start_formula_watcher()
    
    # 检查是否有配置重载触发
    if 'config_reload_trigger' in st.session_state and st.session_state.config_reload_trigger > 0:
        if 'last_reload_trigger' not in st.session_state:
            st.session_state.last_reload_trigger = 0
        
        # 只在触发值变化时显示提示
        if st.session_state.config_reload_trigger != st.session_state.last_reload_trigger:
            st.info("✨ 检测到配置文件更新，已自动重新加载")
            st.session_state.last_reload_trigger = st.session_state.config_reload_trigger
    
    # 获取计算器实例
    calculator = get_calculator()
    
    # 标题
    st.markdown('<h1 class="main-title">存储容量计算器</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">基于公式配置的存储参数计算工具 | 支持数据持久化与列管理</p>', unsafe_allow_html=True)
    
    # 渲染侧边栏
    modified_defaults = render_sidebar(calculator)
    
    # 初始化session state
    if 'df' not in st.session_state:
        # 尝试从文件加载
        loaded_df = load_data_from_file()
        if loaded_df is not None:
            st.session_state.df = loaded_df
            st.info(f"已从 {DATA_FILE} 加载 {len(loaded_df)} 行数据")
        else:
            st.session_state.df = create_default_dataframe(calculator, modified_defaults)
    
    # 数据持久化控制
    st.markdown("### 💾 数据持久化")
    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
    
    with col1:
        if st.button("💾 保存到服务器", type="primary", width='stretch'):
            if save_data_to_file(st.session_state.df):
                st.success("数据已保存!")
    
    with col2:
        if st.button("📂 从服务器加载", width='stretch'):
            loaded_df = load_data_from_file()
            if loaded_df is not None:
                st.session_state.df = loaded_df
                st.success(f"已加载 {len(loaded_df)} 行数据")
                st.rerun()
    
    with col3:
        # 加载现有的calc.xlsx
        if st.button("📥 导入calc.xlsx", width='stretch'):
            calc_file = os.path.join(SCRIPT_DIR, "calc.xlsx")
            if os.path.exists(calc_file):
                try:
                    df = pd.read_excel(calc_file)
                    for col in df.columns:
                        df[col] = df[col].astype(str).replace('nan', '')
                    st.session_state.df = df
                    st.success(f"已导入 {len(df)} 行数据")
                    st.rerun()
                except Exception as e:
                    st.error(f"导入失败: {str(e)}")
            else:
                st.warning("calc.xlsx 文件不存在")
    
    with col4:
        st.caption(f"数据文件: {DATA_FILE}")
    
    st.markdown("---")
    
    # 列管理
    current_columns = list(st.session_state.df.columns)
    col_action = render_column_manager(calculator, current_columns)
    
    if col_action:
        action, col_name = col_action
        if action == 'add' and col_name not in st.session_state.df.columns:
            st.session_state.df[col_name] = ''
            st.success(f"已添加列: {col_name}")
            st.rerun()
        elif action == 'delete' and col_name in st.session_state.df.columns:
            st.session_state.df = st.session_state.df.drop(columns=[col_name])
            st.success(f"已删除列: {col_name}")
            st.rerun()
    
    # 列重命名
    rename_action = render_column_rename(current_columns)
    if rename_action:
        old_name, new_name = rename_action
        if old_name in st.session_state.df.columns:
            st.session_state.df = st.session_state.df.rename(columns={old_name: new_name})
            st.success(f"已将列 '{old_name}' 重命名为 '{new_name}'")
            st.rerun()
    
    st.markdown("---")
    
    # 主内容区 - 数据表格
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 📊 数据表格")
        st.caption("编辑输入参数，系统将自动计算结果。支持输入带单位的值，如: `3.84TB`, `960GB`, `3.2TiB`, `0.9` 等")
    
    with col2:
        auto_calc = st.checkbox("自动计算", value=False, help="编辑后自动触发计算（大数据量时建议关闭）")
    
    # 构建列配置
    column_config = {}
    for col in st.session_state.df.columns:
        col_type, var_name = calculator.identify_column_type(col)
        if col_type == 'input':
            var_info = calculator.variables.get(var_name, {})
            unit = var_info.get('unit', '')
            help_text = f"输入变量: {var_name}"
            if unit:
                help_text += f"\n单位: {unit}"
            column_config[col] = st.column_config.TextColumn(
                col,
                help=help_text,
                default=""
            )
        elif col_type == 'output':
            formula_data = calculator.formulas.get(var_name, {})
            expr = formula_data.get('expression', '')
            column_config[col] = st.column_config.TextColumn(
                col,
                help=f"输出公式: {expr}",
                disabled=False  # 允许编辑输出列，以便手动输入已知值
            )
        else:
            column_config[col] = st.column_config.TextColumn(
                col,
                help="自定义列",
                default=""
            )
    
    # 可编辑数据表格
    edited_df = st.data_editor(
        st.session_state.df,
        column_config=column_config,
        num_rows="dynamic",
        width='stretch',
        key="data_editor"
    )
    
    # 检测数据是否有变化（用户编辑了单元格）
    # 注意：不要在这里直接更新 session_state.df，否则会导致编辑被覆盖
    # 只在用户明确操作时（计算、保存、清空）才更新
    
    # 计算按钮
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    with col1:
        calc_button = st.button("🔢 计算", type="primary", width='stretch')

    with col2:
        clear_button = st.button("🗑️ 清空结果", width='stretch')

    with col3:
        # 同步按钮 - 用于手动同步编辑器中的数据到 session state
        sync_button = st.button("🔄 同步编辑", help="将编辑器中的修改同步到内存（编辑后建议点击此按钮再计算）", width='stretch')
    
    # 处理同步
    if sync_button:
        st.session_state.df = edited_df
        st.success("编辑已同步")
        st.rerun()
    
    # 处理清空
    if clear_button:
        # 先同步最新编辑
        result_df = edited_df.copy()
        output_formulas = calculator.get_output_formulas()
        var_to_col = calculator.get_variable_to_column_map()
        for name in output_formulas.keys():
            col_name = var_to_col.get(name, name)
            if col_name in result_df.columns:
                result_df[col_name] = ''
        st.session_state.df = result_df
        st.rerun()
    
    # 执行计算
    if calc_button or auto_calc:
        # 显示模态遮罩层阻止用户操作
        modal_placeholder = st.empty()
        modal_placeholder.markdown("""
        <div id="calc-modal" style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0, 0, 0, 0.7);
            z-index: 999999;
            display: flex;
            justify-content: center;
            align-items: center;
            backdrop-filter: blur(4px);
        ">
            <div style="
                background: white;
                padding: 40px 60px;
                border-radius: 16px;
                text-align: center;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            ">
                <div style="
                    width: 50px;
                    height: 50px;
                    border: 4px solid #f3f3f3;
                    border-top: 4px solid #667eea;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                    margin: 0 auto 20px;
                "></div>
                <h3 style="margin: 0; color: #333; font-weight: 600;">正在计算中...</h3>
                <p style="margin: 10px 0 0; color: #666; font-size: 14px;">请稍候，计算完成后将自动更新</p>
            </div>
        </div>
        <style>
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
        """, unsafe_allow_html=True)
        
        var_to_col = calculator.get_variable_to_column_map()
        # 使用编辑器中的最新数据进行计算
        result_df = edited_df.copy()
        
        for idx, row in result_df.iterrows():
            row_data = row.to_dict()
            results = calculate_row(calculator, row_data, modified_defaults)
            
            if results:
                # 更新结果列
                for var_name, value in results.items():
                    col_name = var_to_col.get(var_name, var_name)
                    if col_name in result_df.columns:
                        # 检查是否是输出公式
                        if var_name in calculator.formulas:
                            formatted = calculator.format_result(var_name, value)
                            result_df.at[idx, col_name] = formatted
        
        st.session_state.df = result_df
        
        # 清除模态遮罩
        modal_placeholder.empty()
        
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
            help="上传包含输入参数的文件，列名将自动识别"
        )
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    import_df = pd.read_csv(uploaded_file)
                else:
                    import_df = pd.read_excel(uploaded_file)
                
                # 转换为字符串
                for col in import_df.columns:
                    import_df[col] = import_df[col].astype(str).replace('nan', '')
                
                st.session_state.df = import_df
                st.success(f"成功导入 {len(import_df)} 行数据，{len(import_df.columns)} 列")
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
        
        if st.button("📥 导出数据", width='stretch'):
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
        var_to_col = calculator.get_variable_to_column_map()
        numeric_columns = []
        
        # 找出可以可视化的数值列
        for name in output_formulas.keys():
            col_name = var_to_col.get(name, name)
            if col_name in st.session_state.df.columns:
                try:
                    col_data = st.session_state.df[col_name].apply(
                        lambda x: float(str(x).split()[0]) if pd.notna(x) and str(x).strip() and str(x) != 'nan' else None
                    )
                    if col_data.notna().any():
                        numeric_columns.append((col_name, col_data))
                except:
                    pass
        
        if numeric_columns:
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
        '存储容量计算器 v2.0 | 支持数据持久化与列管理 | 基于 Streamlit 构建'
        '</p>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
