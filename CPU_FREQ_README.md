# Radxa Dragon Q6A CPU频率设置工具

这是一个用于设置Radxa Dragon Q6A设备CPU频率的Python脚本，参考了[Radxa官方文档](https://docs.radxa.com/dragon/q6a/system-use/performance)。

## 功能特性

- ✅ 支持设置所有CPU策略的频率（policy0, policy4, policy7）
- ✅ 自动切换为userspace调速器模式
- ✅ 显示当前频率和可用频率列表
- ✅ 预设配置（性能/平衡/省电模式）
- ✅ 交互式设置界面
- ✅ 命令行参数支持

## 系统要求

- Radxa Dragon Q6A设备
- Python 3.x
- Root权限（使用sudo运行）

## 快速开始

### 1. 查看当前状态

```bash
sudo python3 set_cpu_freq.py --status
```

或简写：

```bash
sudo python3 set_cpu_freq.py -s
```

### 2. 使用预设配置

```bash
# 性能模式（根据Radxa文档示例）
sudo python3 set_cpu_freq.py --preset performance

# 平衡模式
sudo python3 set_cpu_freq.py --preset balanced

# 省电模式
sudo python3 set_cpu_freq.py --preset powersave
```

### 3. 设置所有策略的频率

```bash
# 设置 policy0=1958400, policy4=2400000, policy7=2707200
sudo python3 set_cpu_freq.py --set 1958400 2400000 2707200
```

### 4. 设置单个策略

```bash
# 设置 policy0 为 1958400 Hz
sudo python3 set_cpu_freq.py --policy policy0 --freq 1958400
```

### 5. 交互式设置

```bash
sudo python3 set_cpu_freq.py --interactive
```

或简写：

```bash
sudo python3 set_cpu_freq.py -i
```

## 详细使用说明

### 命令行参数

```
--status, -s              显示CPU频率状态
--set FREQ0 FREQ4 FREQ7   为所有策略设置频率
--policy, -p POLICY       指定策略 (policy0/policy4/policy7)
--freq, -f FREQ           设置频率 (Hz)
--preset PRESET           使用预设配置 (performance/balanced/powersave)
--interactive, -i         交互式设置
--help, -h                显示帮助信息
```

### 预设配置说明

#### 性能模式 (performance)
- policy0: 1958400 Hz
- policy4: 2400000 Hz  
- policy7: 2707200 Hz

这是Radxa文档中推荐的性能配置。

#### 平衡模式 (balanced)
自动选择每个策略的中间频率，在性能和功耗之间取得平衡。

#### 省电模式 (powersave)
自动选择每个策略的最低可用频率，最大化电池续航。

### 交互式模式

交互式模式提供友好的菜单界面：

1. **为所有策略设置频率** - 逐个为每个策略选择频率
2. **为单个策略设置频率** - 只修改一个策略
3. **使用预设配置** - 快速应用预设
4. **仅查看状态** - 显示当前配置

## 工作原理

脚本按照Radxa文档的步骤操作：

1. **检查权限** - 确保以root权限运行
2. **切换调速器** - 将scaling_governor设置为`userspace`
3. **读取可用频率** - 从`scaling_available_frequencies`获取
4. **设置频率** - 写入`scaling_setspeed`文件
5. **验证设置** - 读取`scaling_cur_freq`确认

## 示例输出

### 查看状态

```
======================================================================
CPU频率状态
======================================================================

📊 policy0:
   调速器: userspace
   当前频率: 1.96 GHz (1958400 Hz)
   可用频率: 2.76 GHz (2764800 Hz), 2.59 GHz (2592000 Hz), 2.42 GHz (2419200 Hz), 2.25 GHz (2256000 Hz), 2.08 GHz (2088000 Hz)
              ... 共 15 个频率

📊 policy4:
   调速器: userspace
   当前频率: 2.40 GHz (2400000 Hz)
   可用频率: 2.76 GHz (2764800 Hz), 2.59 GHz (2592000 Hz), 2.42 GHz (2419200 Hz), 2.25 GHz (2256000 Hz), 2.08 GHz (2088000 Hz)
              ... 共 15 个频率

📊 policy7:
   调速器: userspace
   当前频率: 2.71 GHz (2707200 Hz)
   可用频率: 2.76 GHz (2764800 Hz), 2.59 GHz (2592000 Hz), 2.42 GHz (2419200 Hz), 2.25 GHz (2256000 Hz), 2.08 GHz (2088000 Hz)
              ... 共 15 个频率

======================================================================
```

## 注意事项

⚠️ **重要提示**:

1. **需要root权限** - 所有操作都需要sudo
2. **频率范围** - 确保设置的频率在可用频率列表中
3. **系统稳定性** - 过高的频率可能导致系统不稳定或过热
4. **散热措施** - 使用高性能模式时确保有足够的散热
5. **重启后失效** - 设置不会在重启后保持，需要重新设置

## 故障排除

### 错误: "需要root权限"
```bash
# 使用sudo运行
sudo python3 set_cpu_freq.py --status
```

### 错误: "CPU频率路径不存在"
- 确认设备是Radxa Dragon Q6A
- 检查内核是否支持CPU频率调节
- 确认路径 `/sys/devices/system/cpu/cpufreq` 存在

### 频率设置失败
- 检查频率是否在可用列表中
- 确认调速器已切换为userspace
- 查看系统日志: `dmesg | tail`

### 设置后频率未改变
- 某些系统可能不支持手动设置频率
- 检查是否有其他进程在控制CPU频率
- 尝试先切换到其他调速器再切回userspace

## 参考文档

- [Radxa Dragon Q6A 性能设置文档](https://docs.radxa.com/dragon/q6a/system-use/performance)
- [Linux CPU频率调节文档](https://www.kernel.org/doc/Documentation/cpu-freq/)

## 许可证

此脚本可自由使用和修改。

## 贡献

欢迎提交Issue和Pull Request来改进此工具！

