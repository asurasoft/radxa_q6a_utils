#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Radxa Dragon Q6A CPU频率设置脚本
参考: https://docs.radxa.com/dragon/q6a/system-use/performance
"""

import os
import sys
import subprocess
from pathlib import Path


class CPUFreqManager:
    """CPU频率管理器"""
    
    # CPU策略路径
    CPUFREQ_BASE = Path("/sys/devices/system/cpu/cpufreq")
    
    # 默认策略（根据Radxa Dragon Q6A文档）
    POLICIES = ["policy0", "policy4", "policy7"]
    
    def __init__(self):
        """初始化"""
        self.check_root()
        self.check_paths()
    
    def check_root(self):
        """检查是否为root用户"""
        if os.geteuid() != 0:
            print("❌ 错误: 需要root权限!")
            print("   请使用: sudo python3 set_cpu_freq.py")
            sys.exit(1)
    
    def check_paths(self):
        """检查CPU频率路径是否存在"""
        if not self.CPUFREQ_BASE.exists():
            print(f"❌ 错误: CPU频率路径不存在: {self.CPUFREQ_BASE}")
            print("   此脚本仅适用于Radxa Dragon Q6A设备")
            sys.exit(1)
    
    def get_available_frequencies(self, policy):
        """获取指定策略的可用频率"""
        freq_file = self.CPUFREQ_BASE / policy / "scaling_available_frequencies"
        
        if not freq_file.exists():
            return []
        
        try:
            with open(freq_file, 'r') as f:
                content = f.read().strip()
                if not content:
                    return []
                # 频率以空格分隔
                frequencies = [int(freq) for freq in content.split()]
                return sorted(frequencies, reverse=True)  # 从高到低排序
        except Exception as e:
            print(f"⚠️  读取 {policy} 可用频率失败: {e}")
            return []
    
    def get_current_frequency(self, policy):
        """获取当前频率"""
        freq_file = self.CPUFREQ_BASE / policy / "scaling_cur_freq"
        
        try:
            with open(freq_file, 'r') as f:
                return int(f.read().strip())
        except Exception as e:
            print(f"⚠️  读取 {policy} 当前频率失败: {e}")
            return None
    
    def get_current_governor(self, policy):
        """获取当前调速器"""
        gov_file = self.CPUFREQ_BASE / policy / "scaling_governor"
        
        try:
            with open(gov_file, 'r') as f:
                return f.read().strip()
        except Exception as e:
            print(f"⚠️  读取 {policy} 调速器失败: {e}")
            return None
    
    def set_governor(self, policy, governor="userspace"):
        """设置调速器为userspace模式"""
        gov_file = self.CPUFREQ_BASE / policy / "scaling_governor"
        
        try:
            with open(gov_file, 'w') as f:
                f.write(governor)
            return True
        except Exception as e:
            print(f"❌ 设置 {policy} 调速器失败: {e}")
            return False
    
    def set_frequency(self, policy, frequency):
        """设置CPU频率"""
        # 首先确保调速器是userspace
        current_gov = self.get_current_governor(policy)
        if current_gov != "userspace":
            print(f"📝 设置 {policy} 调速器为 userspace...")
            if not self.set_governor(policy, "userspace"):
                return False
        
        # 检查频率是否可用
        available = self.get_available_frequencies(policy)
        if available and frequency not in available:
            print(f"⚠️  警告: {frequency} Hz 不在 {policy} 的可用频率列表中")
            print(f"   可用频率: {', '.join(map(str, available))}")
            confirm = input("   是否继续? (y/n): ").strip().lower()
            if confirm != 'y':
                return False
        
        # 设置频率
        freq_file = self.CPUFREQ_BASE / policy / "scaling_setspeed"
        
        try:
            with open(freq_file, 'w') as f:
                f.write(str(frequency))
            
            # 验证设置是否成功
            current = self.get_current_frequency(policy)
            if current == frequency:
                return True
            else:
                print(f"⚠️  设置后频率为 {current} Hz，可能与目标 {frequency} Hz 不同")
                return True
        except Exception as e:
            print(f"❌ 设置 {policy} 频率失败: {e}")
            return False
    
    def show_status(self):
        """显示所有策略的状态"""
        print("\n" + "=" * 70)
        print("CPU频率状态")
        print("=" * 70)
        
        for policy in self.POLICIES:
            policy_path = self.CPUFREQ_BASE / policy
            if not policy_path.exists():
                print(f"\n⚠️  {policy}: 不存在")
                continue
            
            governor = self.get_current_governor(policy)
            current_freq = self.get_current_frequency(policy)
            available = self.get_available_frequencies(policy)
            
            print(f"\n📊 {policy}:")
            print(f"   调速器: {governor}")
            print(f"   当前频率: {self.format_frequency(current_freq) if current_freq else 'N/A'}")
            
            if available:
                print(f"   可用频率: {', '.join([self.format_frequency(f) for f in available[:5]])}")
                if len(available) > 5:
                    print(f"              ... 共 {len(available)} 个频率")
        
        print("\n" + "=" * 70)
    
    def format_frequency(self, freq):
        """格式化频率显示"""
        if freq is None:
            return "N/A"
        
        if freq >= 1000000:
            return f"{freq/1000000:.2f} GHz ({freq} Hz)"
        else:
            return f"{freq/1000:.2f} MHz ({freq} Hz)"
    
    def set_all_policies(self, frequencies):
        """为所有策略设置频率"""
        if len(frequencies) != len(self.POLICIES):
            print(f"❌ 错误: 需要为 {len(self.POLICIES)} 个策略提供频率")
            print(f"   当前提供: {len(frequencies)} 个")
            return False
        
        success = True
        for policy, freq in zip(self.POLICIES, frequencies):
            print(f"\n📝 设置 {policy} 为 {self.format_frequency(freq)}...")
            if not self.set_frequency(policy, freq):
                success = False
        
        return success
    
    def interactive_set(self):
        """交互式设置"""
        self.show_status()
        
        print("\n选择操作:")
        print("1. 为所有策略设置频率")
        print("2. 为单个策略设置频率")
        print("3. 使用预设配置")
        print("4. 仅查看状态")
        
        choice = input("\n请选择 (1-4): ").strip()
        
        if choice == "1":
            self.set_all_interactive()
        elif choice == "2":
            self.set_single_interactive()
        elif choice == "3":
            self.set_preset()
        elif choice == "4":
            self.show_status()
        else:
            print("无效选择")
    
    def set_all_interactive(self):
        """交互式设置所有策略"""
        frequencies = []
        
        for policy in self.POLICIES:
            available = self.get_available_frequencies(policy)
            if not available:
                print(f"⚠️  {policy} 无可用频率信息")
                freq_input = input(f"请输入 {policy} 的频率 (Hz): ").strip()
            else:
                print(f"\n{policy} 可用频率:")
                for i, freq in enumerate(available[:10], 1):  # 只显示前10个
                    print(f"  {i}. {self.format_frequency(freq)}")
                
                freq_input = input(f"请输入 {policy} 的频率 (Hz) 或序号: ").strip()
                
                # 如果输入的是序号
                try:
                    idx = int(freq_input) - 1
                    if 0 <= idx < len(available):
                        freq_input = str(available[idx])
                except ValueError:
                    pass
            
            try:
                frequencies.append(int(freq_input))
            except ValueError:
                print(f"❌ 无效的频率值: {freq_input}")
                return
        
        print("\n确认设置:")
        for policy, freq in zip(self.POLICIES, frequencies):
            print(f"  {policy}: {self.format_frequency(freq)}")
        
        confirm = input("\n确认? (y/n): ").strip().lower()
        if confirm == 'y':
            self.set_all_policies(frequencies)
            print("\n✓ 设置完成!")
            self.show_status()
    
    def set_single_interactive(self):
        """交互式设置单个策略"""
        print("\n选择策略:")
        for i, policy in enumerate(self.POLICIES, 1):
            print(f"  {i}. {policy}")
        
        try:
            choice = int(input("请选择 (1-{}): ".format(len(self.POLICIES))).strip())
            if 1 <= choice <= len(self.POLICIES):
                policy = self.POLICIES[choice - 1]
            else:
                print("无效选择")
                return
        except ValueError:
            print("无效输入")
            return
        
        available = self.get_available_frequencies(policy)
        if available:
            print(f"\n{policy} 可用频率:")
            for i, freq in enumerate(available[:10], 1):
                print(f"  {i}. {self.format_frequency(freq)}")
        
        freq_input = input(f"\n请输入 {policy} 的频率 (Hz): ").strip()
        
        try:
            frequency = int(freq_input)
            if self.set_frequency(policy, frequency):
                print(f"\n✓ {policy} 设置成功!")
                self.show_status()
        except ValueError:
            print("❌ 无效的频率值")
    
    def set_preset(self):
        """使用预设配置"""
        print("\n预设配置:")
        print("1. 性能模式 (policy0: 1958400, policy4: 2400000, policy7: 2707200)")
        print("2. 平衡模式 (中等频率)")
        print("3. 省电模式 (最低频率)")
        print("4. 自定义")
        
        choice = input("请选择 (1-4): ").strip()
        
        if choice == "1":
            # 性能模式（根据Radxa文档示例）
            freqs = [1958400, 2400000, 2707200]
        elif choice == "2":
            # 平衡模式（使用中等频率）
            freqs = []
            for policy in self.POLICIES:
                available = self.get_available_frequencies(policy)
                if available:
                    # 选择中间频率
                    mid_idx = len(available) // 2
                    freqs.append(available[mid_idx])
                else:
                    print(f"⚠️  {policy} 无可用频率，使用默认值")
                    freqs.append(1500000)  # 默认值
        elif choice == "3":
            # 省电模式（最低频率）
            freqs = []
            for policy in self.POLICIES:
                available = self.get_available_frequencies(policy)
                if available:
                    freqs.append(available[-1])  # 最低频率
                else:
                    freqs.append(800000)  # 默认最低值
        elif choice == "4":
            self.set_all_interactive()
            return
        else:
            print("无效选择")
            return
        
        print("\n确认设置:")
        for policy, freq in zip(self.POLICIES, freqs):
            print(f"  {policy}: {self.format_frequency(freq)}")
        
        confirm = input("\n确认? (y/n): ").strip().lower()
        if confirm == 'y':
            self.set_all_policies(freqs)
            print("\n✓ 设置完成!")
            self.show_status()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Radxa Dragon Q6A CPU频率设置工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 查看状态
  sudo python3 set_cpu_freq.py --status
  
  # 设置所有策略频率
  sudo python3 set_cpu_freq.py --set 1958400 2400000 2707200
  
  # 设置单个策略
  sudo python3 set_cpu_freq.py --policy policy0 --freq 1958400
  
  # 交互式设置
  sudo python3 set_cpu_freq.py --interactive
  
  # 使用预设
  sudo python3 set_cpu_freq.py --preset performance
        """
    )
    
    parser.add_argument(
        '--status', '-s',
        action='store_true',
        help='显示CPU频率状态'
    )
    
    parser.add_argument(
        '--set',
        nargs=3,
        type=int,
        metavar=('FREQ0', 'FREQ4', 'FREQ7'),
        help='为所有策略设置频率 (policy0 policy4 policy7)'
    )
    
    parser.add_argument(
        '--policy', '-p',
        choices=['policy0', 'policy4', 'policy7'],
        help='指定策略'
    )
    
    parser.add_argument(
        '--freq', '-f',
        type=int,
        help='设置频率 (Hz)'
    )
    
    parser.add_argument(
        '--preset',
        choices=['performance', 'balanced', 'powersave'],
        help='使用预设配置'
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='交互式设置'
    )
    
    args = parser.parse_args()
    
    # 创建管理器
    manager = CPUFreqManager()
    
    # 执行操作
    if args.status:
        manager.show_status()
    elif args.set:
        freqs = args.set
        manager.set_all_policies(freqs)
        manager.show_status()
    elif args.policy and args.freq:
        if manager.set_frequency(args.policy, args.freq):
            print(f"✓ {args.policy} 设置成功!")
            manager.show_status()
    elif args.preset:
        if args.preset == 'performance':
            manager.set_all_policies([1958400, 2400000, 2707200])
        elif args.preset == 'balanced':
            freqs = []
            for policy in manager.POLICIES:
                available = manager.get_available_frequencies(policy)
                if available:
                    freqs.append(available[len(available) // 2])
                else:
                    freqs.append(1500000)
            manager.set_all_policies(freqs)
        elif args.preset == 'powersave':
            freqs = []
            for policy in manager.POLICIES:
                available = manager.get_available_frequencies(policy)
                if available:
                    freqs.append(available[-1])
                else:
                    freqs.append(800000)
            manager.set_all_policies(freqs)
        manager.show_status()
    elif args.interactive:
        manager.interactive_set()
    else:
        # 默认显示状态
        manager.show_status()
        print("\n💡 提示: 使用 --help 查看所有选项")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n中断。")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

