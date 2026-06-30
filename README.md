# 💰 Wealth Manager — 个人资产管理

一站式个人财务规划工具，支持资产管理、现金流追踪、退休规划、Super Fund 优化、蒙特卡洛模拟和汇率分析。

## 功能

| 页面 | 功能 |
|------|------|
| 📊 总览 | 净资产汇总、资产配置饼图、净值趋势、关键提醒 |
| 🏠 资产管理 | 录入房产/Super Fund/现金，每项可选货币（AUD/USD/CNY/HKD），自动汇率换算 |
| 💰 现金流 | 收入/支出/税务计算、瀑布图、储蓄率 |
| 🎯 退休规划 | 生活方式设置（双城/商务舱）、projection 曲线、敏感度分析 |
| 📈 Super Fund 优化 | Concessional/Carry-forward/NCC 空间测算、Division 293 提醒 |
| 🎲 蒙特卡洛 | 10,000次模拟、扇形图、Sequence Risk 崩盘压力测试 |
| 💱 汇率分析 | AUD/USD/CNY/HKD 敏感度、情景对比、天然对冲分析 |
| ⚙️ 设置 | 中英文切换、显示货币、数据导入/导出/重置 |

## 本地运行

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动
streamlit run app.py

# 浏览器访问 http://localhost:8501
```

## 部署到 Streamlit Cloud

1. 将 `app.py` 和 `requirements.txt` 推送到 GitHub 仓库
2. 在 [share.streamlit.io](https://share.streamlit.io) 连接仓库
3. 选择 `app.py` 作为入口，点击 Deploy

### 数据持久化

| 环境 | 机制 | 刷新保留 | 跨设备 |
|------|------|----------|--------|
| 本地 | 自动写入 `wealth_data.json` | ✅ | 复制文件 |
| Cloud | 自动存服务器文件 + 浏览器 localStorage | ✅ | 用导出→导入 |

## 技术栈

- Python 3.10+
- Streamlit 1.30+
- Plotly 5.18+
- NumPy 1.24+

## ⚠️ 免责声明

仅供个人财务规划参考，**不构成理财、税务或法律建议**。澳洲税率/Super Fund 规则基于 2025-26 财年，请定期核实是否有变动。重大财务决策前请咨询持牌理财顾问和会计师。
