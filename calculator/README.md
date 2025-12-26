# 存储系统配置计算器

## 项目概述

这是一个专门用于存储系统配置计算的工具，支持通过YAML配置文件定义计算公式，并提供多种运行模式。主要用于解决以下场景：

- 存储系统容量规划和计算
- 性能指标预估和验证
- 配置参数动态调整和实时计算
- 支持复杂公式依赖链的自动求解

### 核心特性

- 支持YAML配置的公式定义系统
- 支持Excel交互式计算
- 支持实时文件监听和自动计算
- 支持单位自动转换和格式化
- 支持复杂公式依赖链自动求解
- 支持多种运行模式（命令行/Excel集成）

## 系统架构

### 配置文件结构

配置文件采用YAML格式，支持模块化配置：

```yaml
formulas/
├── capacity.yaml    # 容量相关计算
├── throughput.yaml  # 吞吐量相关计算
├── metadata.yaml    # 元数据相关配置
├── global.yaml     # 全局默认值配置
└── ec.yaml        # EC编码相关配置
```

### 配置文件格式说明

每个YAML文件包含以下主要部分：

```yaml
global:
  defaults:
    variable_name: default_value

variables:
  variable_name:
    description: "变量描述"
    unit: "单位"
    excel_column: "Excel列名"
    can_be_input: true/false

formulas:
  formula_name:
    expression: "计算公式表达式"
    excel_column: "输出列名"
    unit: "输出单位"
```

## 使用方式

### 1. 命令行直接计算模式

```bash
python storage_calculator.py
```

### 2. Excel一次性计算模式

```bash
python storage_calculator.py --excel "数据表.xlsm"
```

### 3. Excel实时监听模式

```bash
python storage_calculator.py --watch "数据表.xlsm"
```

### 4. Excel VBA集成模式

在Excel中通过VBA调用计算功能：

```vba
Sub CalculateStorageMetrics()
    ' VBA代码见storage_calculator.py中的示例
End Sub
```

## 配置指南

### 1. 变量定义

```yaml
variables:
  nvme_capacity:
    description: "单个NVMe容量"
    unit: "TB"
    excel_column: "NVMe容量"
    can_be_input: true
```

### 2. 公式定义

```yaml
formulas:
  total_nvme_capacity:
    expression: "total_nvme_capacity = nvme_capacity * nvme_count"
    excel_column: "NVMe总容量"
    unit: "TB"
```

### 3. 默认值配置

```yaml
global:
  defaults:
    nvme_capacity: "7.68 TB"
    hdd_capacity: "20 TB"
```

## 单位支持

系统支持以下单位类型：

- 容量单位：B, KB/KiB, MB/MiB, GB/GiB, TB/TiB, PB/PiB
- 速率单位：B/s, MB/s, MiB/s, GB/s, GiB/s
- 百分比：%
- 计数单位：个

## 注意事项

### Mac系统特别说明

1. 运行时需要授予终端/IDE自动化权限
2. 对于Cursor等IDE，可能需要修改plist添加权限声明：
```xml
<key>NSAppleEventsUsageDescription</key>
<string>This app requires Apple Events access to automate system functions.</string>
```
3. **测试时的临时目录权限问题**：
   - macOS 的 TCC (Transparency, Consent, and Control) 机制会追踪每个具体路径的授权状态
   - `tempfile.mkdtemp()` 每次创建的随机临时目录（如 `/var/folders/...`）都需要单独授权
   - 解决方案：测试使用项目目录下的固定 `test_temp/` 目录
   - 首次运行测试时会弹出权限对话框，点击"好"授权后即可正常使用

### 文件监听限制

Mac系统中，fseventsd不允许多个watchdog observer监听同一目录，建议将Excel文件和formula.yaml配置放在不同目录。

## 开发扩展

### 添加新公式

1. 在appropriate的YAML文件中定义新变量
2. 添加公式定义
3. 设置默认值（可选）
4. 配置Excel映射（如需要）

### 性能优化

系统已包含性能统计功能，可通过查看日志获取详细的性能数据：
- 模块导入时间
- 计算耗时
- Excel操作耗时

## 故障排除

1. Excel连接问题
   - 检查文件路径是否正确
   - 确认Excel进程状态
   - 验证权限设置

2. 公式计算问题
   - 检查变量依赖关系
   - 验证单位换算
   - 查看详细日志输出

## 待办事项

- [ ] 支持不同放大系数的业务模型对比
- [ ] 优化公式依赖链分析
- [ ] 增强错误处理和提示
- [ ] 改进性能统计展示

## 附录

### 附录A: Excel VBA集成完整示例

以下是在Excel中通过VBA调用Python计算器的完整代码示例：

```vba
Sub CalculateStorageMetrics()
    On Error GoTo ErrorHandler

    Dim pythonCmd As String
    Dim exitCode As Integer
    Dim output As String
    Dim errorInfo As String
    Dim oExec As Object
    Dim oShell As Object
    Dim scriptPath As String

    ' 获取当前工作簿的路径
    scriptPath = ThisWorkbook.Path & "\storage_calculator.py"

    ' 构建Python命令，使用绝对路径
    pythonCmd = "python """ & scriptPath & """"

    Set oShell = CreateObject("WScript.Shell")
    Set oExec = oShell.Exec(pythonCmd)

    ' 设置超时时间（单位：毫秒）
    Dim timeout As Long
    timeout = 30000 ' 30秒

    ' 异步读取输出
    Dim startTime As Double
    startTime = Timer
    Do While oExec.Status = 0
        DoEvents
        If Timer - startTime > timeout / 1000 Then
            errorInfo = "执行超时（30秒）"
            Exit Do
        End If
    Loop

    ' 读取标准输出
    output = oExec.StdOut.ReadAll()
    ' 读取标准错误
    errorInfo = oExec.StdErr.ReadAll()

    ' 合并输出信息
    Dim fullOutput As String
    fullOutput = "标准输出：" & vbCrLf & output & vbCrLf & vbCrLf & _
                "标准错误：" & vbCrLf & errorInfo

    ' 显示结果（限制最大长度）
    Const MAX_LENGTH As Integer = 1000
    If Len(fullOutput) > MAX_LENGTH Then
        fullOutput = Left(fullOutput, MAX_LENGTH) & vbCrLf & "...（内容过长已截断）"
    End If

    If oExec.ExitCode = 0 Then
        MsgBox "计算完成！" & vbCrLf & vbCrLf & fullOutput, vbInformation, "执行结果"
    Else
        MsgBox "计算失败（错误码：" & oExec.ExitCode & "）" & vbCrLf & vbCrLf & fullOutput, vbCritical, "错误详情"
    End If

    Exit Sub

ErrorHandler:
    MsgBox "VBA运行时错误: " & Err.Description & vbCrLf & _
          "错误代码: " & Err.Number, vbCritical, "系统错误"
End Sub
```

### VBA集成说明

1. 使用步骤：
   - 在Excel中打开VBA编辑器（Alt + F11）
   - 将上述代码复制到新的模块中
   - 创建按钮并绑定该宏
   - 保存为启用宏的工作簿（.xlsm）

2. 功能特性：
   - 支持异步执行Python脚本
   - 包含超时机制（默认30秒）
   - 捕获并显示标准输出和错误信息
   - 错误处理和用户友好的提示

3. 注意事项：
   - 确保Python环境正确配置
   - 脚本路径使用相对于工作簿的路径
   - 需要启用Excel宏功能
   - Windows系统需要有执行脚本的权限

### 性能统计

使用PowerShell测量执行时间：

```powershell
Measure-Command { python3 .\storage_calculator.py --excel 数据表.xlsm }
```

目前启动耗时主要集中在导入两大库(xlwings和sympy, 约10s+), 实际计算过程约秒级。

