import streamlit as st
import plotly.graph_objects as go
import numpy as np
import json, os, copy, subprocess
from datetime import datetime

# ================================================================
# CONFIG
# ================================================================
st.set_page_config(page_title="Wealth", page_icon="💰", layout="wide")

# Global CSS for consistent fonts and bigger sidebar menu
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
/* Apply Inter globally */
html, body, [class*="css"], [data-testid="stAppViewContainer"],
[data-testid="stSidebar"], input, button, select, textarea {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}
/* Sidebar radio buttons - bigger, more spacing */
div[data-testid="stSidebar"] div[role="radiogroup"] label {
    font-size: 16px !important;
    padding: 8px 12px !important;
    margin-bottom: 2px !important;
    border-radius: 8px !important;
    cursor: pointer !important;
}
div[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background-color: rgba(255, 255, 255, 0.05) !important;
}
/* Consistent caption font */
.stCaption, small {
    font-size: 13px !important;
}
/* Metric values */
div[data-testid="stMetricValue"] {
    font-size: 22px !important;
}
div[data-testid="stMetricLabel"] {
    font-size: 13px !important;
}
</style>
""", unsafe_allow_html=True)
DATA_FILE = "wealth_data.json"
CURRENCIES = ["AUD", "USD", "CNY", "HKD"]
CUR_SYMBOLS = {"AUD": "A$", "USD": "US$", "CNY": "¥", "HKD": "HK$"}
CUR_FLAGS = {"AUD": "🇦🇺", "USD": "🇺🇸", "CNY": "🇨🇳", "HKD": "🇭🇰"}
OWNERS = ["self", "spouse", "joint"]
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#c9d1d9", size=12), margin=dict(l=40, r=20, t=40, b=40),
    xaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.1)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.1)"),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
)

# ================================================================
# TRANSLATIONS
# ================================================================
TR = {
    "nav_dashboard": {"zh": "📊 总览", "en": "📊 Dashboard"},
    "nav_assets": {"zh": "🏠 资产管理", "en": "🏠 Assets"},
    "nav_cashflow": {"zh": "💰 现金流", "en": "💰 Cash Flow"},
    "nav_retirement": {"zh": "🎯 退休规划", "en": "🎯 Retirement"},
    "nav_super": {"zh": "📈 Super Fund 优化", "en": "📈 Super Fund"},
    "nav_monte": {"zh": "🎲 蒙特卡洛", "en": "🎲 Monte Carlo"},
    "nav_settings": {"zh": "⚙️ 设置", "en": "⚙️ Settings"},
    "net_worth": {"zh": "净资产总额", "en": "Net Worth"},
    "annual_cashflow": {"zh": "年净现金流", "en": "Annual Cash Flow"},
    "retirement_gap": {"zh": "退休缺口", "en": "Retirement Gap"},
    "retirement_gap_help": {
        "zh": "退休时本金 − 需要本金 (4%法则)。正数代表充足，负数代表缺口",
        "en": "Capital at Retirement − Capital Needed (4% Rule). Positive means on track, negative means a shortfall"},
    "retire_age": {"zh": "预计可退休年龄", "en": "Est. Retirement Age"},
    "asset_allocation": {"zh": "资产配置", "en": "Asset Allocation"},
    "net_worth_proj": {"zh": "净值增长趋势", "en": "Net Worth Projection"},
    "alerts": {"zh": "⚠️ 关键提醒", "en": "⚠️ Key Alerts"},
    "properties": {"zh": "🏠 房产", "en": "🏠 Properties"},
    "super_fund": {"zh": "📈 Super Fund", "en": "📈 Super Fund"},
    "cash_other": {"zh": "💵 现金 & 其他", "en": "💵 Cash & Other"},
    "name": {"zh": "名称", "en": "Name"},
    "market_value": {"zh": "当前市值", "en": "Market Value"},
    "mortgage": {"zh": "未偿贷款", "en": "Outstanding Mortgage"},
    "interest_rate": {"zh": "年利率 %", "en": "Interest Rate %"},
    "loan_years": {"zh": "剩余年限", "en": "Remaining Years"},
    "monthly_repay": {"zh": "每月还款 (自动)", "en": "Monthly Repay (auto)"},
    "appreciation_rate": {"zh": "年增值/贬值 %", "en": "Annual Appreciation/Depreciation %"},
    "in_10_years": {"zh": "10年后预估", "en": "In 10 years"},
    "annual_return": {"zh": "年回报率 %", "en": "Annual Return %"},
    "taxable_income": {"zh": "应税", "en": "Taxable"},
    "home_loan_repayment": {"zh": "🏠 房贷还款", "en": "🏠 Home Loan Repayment"},
    "owner": {"zh": "归属", "en": "Owner"},
    "owner_self": {"zh": "本人", "en": "Self"},
    "owner_spouse": {"zh": "配偶", "en": "Spouse"},
    "owner_joint": {"zh": "共同", "en": "Joint"},
    "income_breakdown": {"zh": "收入来源明细", "en": "Income Breakdown"},
    "income_by_person": {"zh": "个人收入与税务", "en": "Income & Tax by Person"},
    "salary_income": {"zh": "工资收入", "en": "Salary Income"},
    "savings_income": {"zh": "储蓄/利息收入", "en": "Savings Interest Income"},
    "tax_payable": {"zh": "应缴税额", "en": "Tax Payable"},
    "after_tax_income": {"zh": "税后收入", "en": "After-tax Income"},
    "household_available": {"zh": "家庭可支配收入 (税后)", "en": "Household Available (After Tax)"},
    "add_property": {"zh": "＋ 添加房产", "en": "＋ Add Property"},
    "add_asset": {"zh": "＋ 添加资产", "en": "＋ Add Asset"},
    "remove": {"zh": "删除", "en": "Remove"},
    "total_assets": {"zh": "总资产", "en": "Total Assets"},
    "total_liabilities": {"zh": "总负债", "en": "Total Liabilities"},
    "display_cur": {"zh": "显示货币", "en": "Display Currency"},
    "auto_saved": {"zh": "💾 所有修改自动保存 · 刷新不丢失", "en": "💾 All changes auto-saved"},
    "income": {"zh": "收入", "en": "Income"},
    "expenses": {"zh": "支出", "en": "Expenses"},
    "gross_income": {"zh": "税前收入 (合计)", "en": "Gross Income (Total)"},
    "after_tax": {"zh": "税后收入", "en": "After-tax Income"},
    "total_expenses": {"zh": "年支出", "en": "Annual Expenses"},
    "net_surplus": {"zh": "年净余", "en": "Annual Surplus"},
    "savings_rate": {"zh": "储蓄率", "en": "Savings Rate"},
    "waterfall": {"zh": "现金流瀑布图", "en": "Cash Flow Waterfall"},
    "amount_annual": {"zh": "年金额 (税前)", "en": "Annual (Gross)"},
    "current_age": {"zh": "当前年龄", "en": "Current Age"},
    "target_retire_age": {"zh": "目标退休年龄", "en": "Target Retirement Age"},
    "life_expectancy": {"zh": "预期寿命", "en": "Life Expectancy"},
    "months_au": {"zh": "澳洲居住 (月/年)", "en": "Months in Australia"},
    "months_cn": {"zh": "中国居住 (月/年)", "en": "Months in China"},
    "au_cost": {"zh": "澳洲月开支", "en": "Australia Monthly Cost"},
    "cn_cost": {"zh": "中国月开支", "en": "China Monthly Cost"},
    "biz_class_trips": {"zh": "商务舱往返/年", "en": "Business Class Trips/yr"},
    "ticket_price": {"zh": "人均往返票价", "en": "Ticket Price (per person RT)"},
    "health_ins": {"zh": "国际医疗险/年", "en": "Int'l Health Insurance/yr"},
    "real_return": {"zh": "预期实际回报率 %", "en": "Expected Real Return %"},
    "annual_contrib": {"zh": "年供款 (到退休)", "en": "Annual Contribution"},
    "projection": {"zh": "退休本金 Projection", "en": "Retirement Projection"},
    "sensitivity": {"zh": "敏感度分析", "en": "Sensitivity Analysis"},
    "scenario": {"zh": "情景", "en": "Scenario"},
    "capital_at_retire": {"zh": "退休时本金", "en": "Capital at Retirement"},
    "capital_at_retire_help": {
        "zh": "Super Fund + 其他资产为起点，按实际回报率逐年复利增长，并每年加上年度供款，直到目标退休年龄",
        "en": "Super Fund + other assets as the starting capital, compounded yearly at your real return rate plus annual contributions, until your target retirement age"},
    "lasts_until": {"zh": "能撑到", "en": "Lasts Until"},
    "status": {"zh": "状态", "en": "Status"},
    "total_annual_expense": {"zh": "退休年开支合计", "en": "Total Retirement Expense"},
    "total_annual_expense_help": {
        "zh": "计算方式：澳洲月生活费 × 澳洲月数 + 中国月生活费 × 中国月数（换算成AUD）+ 商务舱机票单价 × 2 × 次数 + 年度医疗保险",
        "en": "AU monthly cost × AU months + CN monthly cost × CN months (converted to AUD) + business-class ticket price × 2 × trips + health insurance"},
    "capital_needed_4pct": {"zh": "需要本金 (4%法则)", "en": "Capital Needed (4% Rule)"},
    "capital_needed_4pct_help": {
        "zh": "退休年开支合计 × 25，即假设每年安全提取本金的4%用于生活开支",
        "en": "Total Retirement Expense × 25 — assumes a 4% annual safe withdrawal rate"},
    "passive_income": {"zh": "被动收入/年", "en": "Passive Income/yr"},
    "sf_current": {"zh": "当前 Super Fund 状况", "en": "Current Super Fund Status"},
    "sf_total": {"zh": "Super Fund 总值", "en": "Super Fund Total"},
    "sf_concentration": {"zh": "最大持仓占比", "en": "Top Holding %"},
    "sf_liquid": {"zh": "流动资产", "en": "Liquid Assets"},
    "concessional": {"zh": "Concessional 供款优化", "en": "Concessional Contribution"},
    "member": {"zh": "成员", "en": "Member"},
    "super_balance": {"zh": "Super 余额", "en": "Super Balance"},
    "sg_received": {"zh": "已收 SG/年", "en": "SG Received/yr"},
    "personal_income": {"zh": "个人收入", "en": "Personal Income"},
    "cc_cap": {"zh": "Concessional 上限", "en": "CC Cap"},
    "cc_used": {"zh": "已用 (SG)", "en": "Used (SG)"},
    "cc_room": {"zh": "可供空间", "en": "Available Room"},
    "carry_forward": {"zh": "Carry-forward 可补", "en": "Carry-forward"},
    "optimal_cc": {"zh": "今年最多可供 (含结转)", "en": "Max CC This Year (incl. carry-fwd)"},
    "planned_self_contrib": {"zh": "本年计划自行供款", "en": "Planned Self-Contribution This Year"},
    "remaining_room": {"zh": "剩余空间", "en": "Remaining Room"},
    "tax_saved": {"zh": "省税效果", "en": "Tax Saved"},
    "ncc": {"zh": "NCC (税后供款) 空间", "en": "NCC (After-tax) Room"},
    "ncc_annual": {"zh": "NCC 年限额", "en": "NCC Annual Cap"},
    "bring_forward": {"zh": "Bring-forward 可结转额", "en": "Bring-forward Cap"},
    "bring_forward_years": {"zh": "结转年数", "en": "Bring-forward Period"},
    "no_bring_fwd": {"zh": "无结转", "en": "no bring-fwd"},
    "eligible": {"zh": "是否可用", "en": "Eligible"},
    "planned_annual_contrib": {"zh": "预计每年平均自行供款 (至退休)", "en": "Planned Avg. Annual Self-Contribution (to retirement)"},
    "super_at_retire_projection": {"zh": "退休时 Super 预估余额", "en": "Projected Super at Retirement"},
    "super_projection_help": {"zh": "以当前余额为起点，每年计入 SG（按当前工资×12%）+ 计划自行供款，并按退休页设置的实际回报率复利，直到目标退休年龄", "en": "Starting from current balance, each year adds SG (current salary × 12%) + planned self-contribution, compounded at the real return rate from the Retirement page, until your target retirement age"},
    "mc_params": {"zh": "模拟参数", "en": "Simulation Parameters"},
    "initial_capital": {"zh": "退休本金", "en": "Initial Capital"},
    "annual_withdrawal": {"zh": "年提取", "en": "Annual Withdrawal"},
    "sim_years": {"zh": "模拟年数", "en": "Simulation Years"},
    "nominal_return": {"zh": "预期回报 (名义) %", "en": "Nominal Return %"},
    "volatility": {"zh": "波动率 (标准差) %", "en": "Volatility (Std Dev) %"},
    "inflation": {"zh": "通胀率 %", "en": "Inflation %"},
    "num_sims": {"zh": "模拟次数", "en": "Simulations"},
    "run_sim": {"zh": "▶ 运行模拟", "en": "▶ Run Simulation"},
    "success_rate": {"zh": "成功率（撑满期限）", "en": "Success Rate"},
    "median_end": {"zh": "中位终值 (P50)", "en": "Median End Value (P50)"},
    "p10_end": {"zh": "最差 10% (P10)", "en": "Worst 10% (P10)"},
    "fan_chart": {"zh": "本金路径扇形图", "en": "Balance Fan Chart"},
    "stress_test": {"zh": "Sequence Risk 崩盘压力测试", "en": "Sequence Risk Stress Test"},
    "crash_year": {"zh": "崩盘年份", "en": "Crash Year"},
    "crash_size": {"zh": "崩盘幅度", "en": "Crash Size"},
    "recovery": {"zh": "恢复期", "en": "Recovery"},
    "fx_rates": {"zh": "汇率设置 (每1 AUD兑)", "en": "FX Rates (per 1 AUD)"},
    "fx_scenario": {"zh": "情景分析", "en": "Scenario Analysis"},
    "current": {"zh": "当前", "en": "Current"},
    "aud_strong": {"zh": "AUD走强", "en": "AUD Strengthens"},
    "aud_weak": {"zh": "AUD走弱", "en": "AUD Weakens"},
    "aud_very_weak": {"zh": "极端弱AUD", "en": "Extreme Weak AUD"},
    "us_etf_aud": {"zh": "美股(AUD)", "en": "US ETF (AUD)"},
    "cn_cost_aud": {"zh": "中国年开支(AUD)", "en": "China Cost (AUD)"},
    "net_impact": {"zh": "净影响", "en": "Net Impact"},
    "language": {"zh": "界面语言", "en": "Language"},
    "display_currency_setting": {"zh": "汇总显示货币", "en": "Display Currency"},
    "data_mgmt": {"zh": "💾 数据管理", "en": "💾 Data Management"},
    "auto_save_on": {"zh": "✅ 自动保存已开启", "en": "✅ Auto-save Enabled"},
    "export_data": {"zh": "📥 导出备份", "en": "📥 Export Backup"},
    "import_data": {"zh": "📂 导入数据", "en": "📂 Import Data"},
    "reset_data": {"zh": "🗑️ 重置所有数据", "en": "🗑️ Reset All Data"},
    "about": {"zh": "关于", "en": "About"},
    "biz_section": {"zh": "🏢 Business", "en": "🏢 Business"},
    "biz_gross": {"zh": "年营业额 (含GST)", "en": "Annual Gross Revenue (incl GST)"},
    "gst_rate": {"zh": "GST税率 %", "en": "GST Rate %"},
    "after_gst": {"zh": "扣除GST后", "en": "After GST"},
    "total_salaries": {"zh": "已发工资总额", "en": "Total Salaries Paid"},
    "biz_expense_budget": {"zh": "可用于经营支出", "en": "Available for Business Expenses"},
    "personal_salary": {"zh": "💡 以下为从公司支取的个人工资/drawings，税务按此计算", "en": "💡 Below are personal salaries/drawings from the business — tax is calculated on these"},
    "currency_label": {"zh": "货币", "en": "Currency"},
    "return_pct": {"zh": "回报%", "en": "Return%"},
    "add_income": {"zh": "＋ 添加收入", "en": "＋ Add Income"},
    "add_expense": {"zh": "＋ 添加支出", "en": "＋ Add Expense"},
    "add_super_item": {"zh": "＋ 添加 Super Fund 项目", "en": "＋ Add Super Fund Item"},
    "new_property": {"zh": "新房产", "en": "New Property"},
    "new_item": {"zh": "新项目", "en": "New Item"},
    "new_asset": {"zh": "新资产", "en": "New Asset"},
    "new_income": {"zh": "新收入", "en": "New Income"},
    "new_expense": {"zh": "新支出", "en": "New Expense"},
    "auto_link": {"zh": "🔗自动", "en": "🔗Auto"},
    "monthly": {"zh": "月", "en": "Mo."},
    "equity": {"zh": "净值", "en": "Equity"},
    "sf_total_label": {"zh": "Super Fund 总值", "en": "Super Fund Total"},
    "fx_label": {"zh": "汇率", "en": "FX Rates"},
    "current_super_total": {"zh": "当前 Super Fund 总值 (AUD)", "en": "Current Super Fund Total (AUD)"},
    "surplus_ok": {"zh": "✅ 超额", "en": "✅ Surplus"},
    "shortfall": {"zh": "⚠️ 不足", "en": "⚠️ Shortfall"},
    "need_more_contrib": {"zh": "需增加供款", "en": "Increase contributions"},
    "lifestyle_settings": {"zh": "🏠 生活方式设置", "en": "🏠 Lifestyle Settings"},
    "accumulation": {"zh": "累积阶段", "en": "Accumulation"},
    "drawdown": {"zh": "提取阶段", "en": "Drawdown"},
    "age": {"zh": "年龄", "en": "Age"},
    "capital": {"zh": "本金", "en": "Capital"},
    "years_after_retire": {"zh": "退休后年数", "en": "Years After Retirement"},
    "conservative": {"zh": "保守 2.5%", "en": "Conservative 2.5%"},
    "baseline": {"zh": "基准 3.5%", "en": "Baseline 3.5%"},
    "optimistic": {"zh": "乐观 4.5%", "en": "Optimistic 4.5%"},
    "age_suffix": {"zh": "岁", "en": ""},
    "no_crash": {"zh": "无崩盘", "en": "No Crash"},
    "crash_yr1": {"zh": "退休第1年崩盘", "en": "Crash Year 1"},
    "crash_yr5": {"zh": "退休第5年崩盘", "en": "Crash Year 5"},
    "crash_yr10": {"zh": "退休第10年崩盘", "en": "Crash Year 10"},
    "crash_bucket": {"zh": "第1年崩盘+现金桶", "en": "Crash Y1 + Cash Bucket"},
    "fetch_fx": {"zh": "🔄 获取实时汇率", "en": "🔄 Fetch Live Rates"},
    "fx_updated": {"zh": "✅ 汇率已更新（Yahoo Finance）", "en": "✅ Rates updated (Yahoo Finance)"},
    "fx_error": {"zh": "❌ 获取失败，请手动输入", "en": "❌ Fetch failed, enter manually"},
    "fx_hedge_tip": {"zh": "💱 天然对冲：AUD贬→美股更值钱(+)，但中国开支更贵(−)。净敞口偏「喜欢弱AUD」。无需额外FX对冲。", "en": "💱 Natural hedge: weak AUD boosts US ETF value but increases China costs. Net exposure favours weak AUD. No extra FX hedge needed."},
    "baseline_label": {"zh": "基准", "en": "Baseline"},
    "tax_label": {"zh": "税", "en": "Tax"},
    "enter_data_first": {"zh": "请先在「资产管理」页录入数据", "en": "Enter data in Assets page first"},
    "sf_concentration_warn": {"zh": "Super Fund {pct:.0f}% 集中在 {name} — 流动性风险高", "en": "Super Fund {pct:.0f}% concentrated in {name} — liquidity risk"},
    "retire_ok": {"zh": "退休目标可达 ✅", "en": "Retirement target achievable ✅"},
    "retire_gap_warn": {"zh": "退休缺口 {gap}，需增加供款或调整退休计划", "en": "Retirement gap {gap}, increase contributions or adjust plan"},
    "passive_retire_note": {"zh": "被动收入 {p}/年 → 实际净提取 {w}/年（提取率 {r}%）", "en": "Passive income {p}/yr → net withdrawal {w}/yr (rate {r}%)"},
    "passive_auto_note": {"zh": "/年（自动计入退休规划）", "en": "/yr (auto-included in retirement plan)"},
    "suggest_ok": {"zh": "💡 基准情景下目标可达。商务舱预算 (~{cost}/年) 是天然安全阀。", "en": "💡 Target achievable at baseline. Business class budget (~{cost}/yr) is a natural safety valve."},
    "suggest_gap": {"zh": "💡 需额外每年供款约 {extra} 或推迟退休 2–3 年。", "en": "💡 Need additional ~{extra}/yr contribution or delay retirement 2-3 years."},
    "div293_over": {"zh": "⚠️ {name}: 收入+CC=${th:,.0f} 超$250k → Division 293 额外15%。但总税率30%仍远低于边际税率。", "en": "⚠️ {name}: Income+CC=${th:,.0f} over $250k → Division 293 extra 15%. But 30% total still well below marginal rate."},
    "div293_room": {"zh": "ℹ️ {name}: 距 Division 293 阈值还有 ${room:,.0f} 空间。", "en": "ℹ️ {name}: ${room:,.0f} room before Division 293 threshold."},
    "mc_ok": {"zh": "🎲 {sr:.0f}% 成功率。建议保留 2 年现金桶 ({bucket}) 应对 sequence risk。", "en": "🎲 {sr:.0f}% success rate. Keep 2yr cash bucket ({bucket}) for sequence risk."},
    "mc_warn": {"zh": "🎲 {sr:.0f}% 成功率，略有风险。可降低提取或增加本金 10-15%。", "en": "🎲 {sr:.0f}% success rate, some risk. Reduce withdrawal or increase capital 10-15%."},
    "mc_bad": {"zh": "🎲 {sr:.0f}% 成功率偏低。建议降提取/增本金/推迟退休。", "en": "🎲 {sr:.0f}% success rate is low. Reduce withdrawal / increase capital / delay retirement."},
    "git_push_ok": {"zh": "✅ 推送成功！Streamlit Cloud 将自动重新部署。", "en": "✅ Push successful! Streamlit Cloud will auto-redeploy."},
    "git_push_fail": {"zh": "推送失败", "en": "Push failed"},
    "git_no_git": {"zh": "未找到 git 命令。请确保已安装 Git 并在项目目录中运行。", "en": "Git not found. Ensure Git is installed and run from the project directory."},
    "import_ok": {"zh": "✅ 导入成功！", "en": "✅ Import successful!"},
    "import_fail": {"zh": "导入失败", "en": "Import failed"},
    "persistence_note": {"zh": "🖥️ 本地：自动写入 wealth_data.json\n\n☁️ Cloud：自动存入浏览器 localStorage，刷新不丢失", "en": "🖥️ Local: auto-saves to wealth_data.json\n\n☁️ Cloud: auto-saves to browser localStorage, persists on refresh"},
    "git_caption": {"zh": "将代码推送到 Git 仓库（wealth_data.json 不会被推送，数据安全）", "en": "Push code to Git repo (wealth_data.json is gitignored, data stays safe)"},
    "about_text": {"zh": "Wealth v1.0 · 仅供个人财务规划参考，不构成理财或税务建议。\n\nBuilt with Streamlit + Plotly · 数据存储在本地。澳洲税率/Super 规则基于 2026-27 财年。", "en": "Wealth v1.0 · For personal planning only, not financial advice.\n\nBuilt with Streamlit + Plotly · Data stored locally. AU tax/super rules based on FY2026-27."},
    "not_financial_advice": {"zh": "仅供参考，不构成理财建议", "en": "Not financial advice"},
    "au_cost_aud": {"zh": "澳洲月开支 (AUD)", "en": "Australia Monthly Cost (AUD)"},
    "cn_cost_aud": {"zh": "中国月开支 (CNY)", "en": "China Monthly Cost (CNY)"},
    "ticket_aud": {"zh": "人均往返票价 (AUD)", "en": "Ticket Price per person RT (AUD)"},
    "health_ins_aud": {"zh": "国际医疗险/年 (AUD)", "en": "Int\'l Health Insurance/yr (AUD)"},
    "contrib_aud": {"zh": "年供款 (AUD)", "en": "Annual Contribution (AUD)"},
    "super_bal_aud": {"zh": "Super 余额 (AUD)", "en": "Super Balance (AUD)"},
    "sg_aud": {"zh": "已收 SG/年 (AUD)", "en": "SG Received/yr (AUD)"},
    "income_aud": {"zh": "个人收入 (AUD)", "en": "Personal Income (AUD)"},
    "error_label": {"zh": "错误", "en": "Error"},
    "git_update": {"zh": "🚀 一键推送到 Git", "en": "🚀 Push to Git"},
    "login_title": {"zh": "💰 个人资产管理", "en": "💰 Wealth"},
    "login_prompt": {"zh": "请输入密码", "en": "Enter Password"},
    "login_btn": {"zh": "登录", "en": "Login"},
    "login_error": {"zh": "密码错误", "en": "Wrong password"},
    "logout": {"zh": "退出登录", "en": "Logout"},
}

def t(key):
    lang = st.session_state.get("lang", "en")
    return TR.get(key, {}).get(lang, key)

# ================================================================
# UI HELPERS
# ================================================================
def money_input(label, value, key, container=None, placeholder=None, max_value=None):
    """Reliable number input using Streamlit's native widget"""
    ctx = container or st
    vis = "collapsed" if not label else "visible"
    result = ctx.number_input(label or "val", value=min(int(value), max_value) if max_value is not None else int(value),
        step=10000, min_value=0, max_value=max_value, key=key,
        format="%d", label_visibility=vis, placeholder=placeholder)
    return result

def calc_monthly_repayment(principal, annual_rate_pct):
    """Simple monthly interest = principal * annual_rate / 12"""
    if principal <= 0 or annual_rate_pct <= 0:
        return 0
    return principal * annual_rate_pct / 100 / 12

def fmt_cur(amount, cur=None):
    if cur is None:
        cur = st.session_state.data.get("display_currency", "AUD")
    sym = CUR_SYMBOLS.get(cur, "$")
    if abs(amount) >= 1_000_000:
        return f"{sym}{amount/1_000_000:,.2f}M"
    return f"{sym}{amount:,.0f}"

def fmt_md(amount, cur=None):
    """Currency format safe for markdown (escapes $ for LaTeX)"""
    return fmt_cur(amount, cur).replace("$", r"\$")

def esc(text):
    """Escape $ signs for markdown/caption rendering"""
    return str(text).replace("$", r"\$")

# ================================================================
# DEFAULT DATA
# ================================================================
def get_default_data():
    return {
        "lang": "en", "display_currency": "AUD",
        "fx_rates": {"USD": 0.645, "CNY": 4.72, "HKD": 5.04},
        "properties": [
            {"name": "自住房 — Sydney", "value": 0, "currency": "AUD", "mortgage": 0, "interest_rate": 6.0, "loan_years": 25, "monthly_repay": 0, "appreciation_rate": 0.0},
            {"name": "自有住房 — 中国", "value": 0, "currency": "CNY", "mortgage": 0, "interest_rate": 3.5, "loan_years": 20, "monthly_repay": 0, "appreciation_rate": 0.0},
        ],
        "super_fund": [
            {"name": "Office (商业物业)", "value": 0, "currency": "AUD"},
            {"name": "ETF (美股)", "value": 0, "currency": "USD"},
            {"name": "现金", "value": 0, "currency": "AUD"},
        ],
        "other_assets": [
            {"name": "澳洲银行存款", "value": 0, "currency": "AUD", "annual_return": 4.0, "taxable_income": False, "owner": "joint"},
            {"name": "中国银行存款", "value": 0, "currency": "CNY", "annual_return": 2.0, "taxable_income": False, "owner": "joint"},
            {"name": "香港账户", "value": 0, "currency": "HKD", "annual_return": 3.5, "taxable_income": False, "owner": "joint"},
            {"name": "个人 ETF (super外)", "value": 0, "currency": "USD", "annual_return": 7.0, "taxable_income": False, "owner": "joint"},
            {"name": "其他资产", "value": 0, "currency": "AUD", "annual_return": 0.0, "taxable_income": False, "owner": "joint"},
        ],
        "business": {
            "gross_revenue": 0, "gst_rate": 10.0,
        },
        "income": [
            {"name": "Salary — Self", "amount": 0, "currency": "AUD", "owner": "self"},
            {"name": "Salary — Spouse", "amount": 0, "currency": "AUD", "owner": "spouse"},
            {"name": "Office Rent (in Super Fund)", "amount": 0, "currency": "AUD", "owner": "joint"},
        ],
        "expenses": [
            {"name": "🏠 Home Loan Repayment", "annual": 0},
            {"name": "🍽️ 日常生活", "annual": 0},
            {"name": "🎓 子女教育", "annual": 0},
            {"name": "🏥 私人医保", "annual": 0},
            {"name": "🚗 交通/车", "annual": 0},
            {"name": "✈️ 旅行/机票", "annual": 0},
            {"name": "📋 保险", "annual": 0},
            {"name": "📦 其他", "annual": 0},
        ],
        "retirement": {
            "current_age": 45, "target_age": 60, "life_expectancy": 90,
            "months_au": 6, "months_cn": 6,
            "au_cost": 7700, "cn_cost": 9300,
            "biz_class_trips": 3, "ticket_price": 4200,
            "health_ins": 4000, "real_return": 3.5,
            "annual_contrib": 60000,
        },
        "super_opt": {
            "m1_name": "本人", "m2_name": "配偶",
            "m1_balance": 0, "m2_balance": 0,
            "m1_sg": 0, "m2_sg": 0,
            "m1_income": 0, "m2_income": 0,
            "m1_self_contrib": 0, "m2_self_contrib": 0,
            "m1_planned_annual_contrib": 0, "m2_planned_annual_contrib": 0,
        },
        "monte_carlo": {
            "initial_capital": 2200000, "annual_withdrawal": 88000,
            "years": 30, "nominal_return": 7.0,
            "volatility": 12.0, "inflation": 2.5, "num_sims": 5000,
        },
    }

# ================================================================
# PERSISTENCE
# ================================================================
def save_data():
    d = st.session_state.data
    try:
        # Backup
        if os.path.exists(DATA_FILE):
            import shutil
            shutil.copy2(DATA_FILE, DATA_FILE + ".bak")
    except Exception:
        pass  # Backup failure is non-fatal
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
        st.session_state._last_saved = datetime.now().astimezone().strftime("%H:%M:%S %Z")
        st.session_state._save_error = None
    except Exception as e:
        st.session_state._save_error = str(e)
    try:
        from streamlit_js_eval import streamlit_js_eval
        js = json.dumps(d, ensure_ascii=False)
        _ = streamlit_js_eval(js_expressions=f"localStorage.setItem('wealth_data', JSON.stringify({js}))",
            key=f"save_{datetime.now().timestamp()}")
    except Exception:
        pass
    # Auto-commit data to git
    has_real_data = any([
        any(p.get("value", 0) > 0 for p in d.get("properties", [])),
        any(s.get("value", 0) > 0 for s in d.get("super_fund", [])),
        any(o.get("value", 0) > 0 for o in d.get("other_assets", [])),
        any(i.get("amount", 0) > 0 for i in d.get("income", [])),
    ])
    if has_real_data:
        _auto_git_save()

def _auto_git_save():
    """Quietly commit wealth_data.json to git if repo exists. Runs at most once per session."""
    if st.session_state.get("_git_saved"):
        return
    try:
        if os.path.exists(".git") and os.path.exists(DATA_FILE):
            subprocess.run(["git", "add", DATA_FILE], capture_output=True, timeout=10)
            subprocess.run(["git", "commit", "-m", "auto-save data"], capture_output=True, timeout=10)
            subprocess.run(["git", "push"], capture_output=True, timeout=30)
            st.session_state._git_saved = True
    except Exception:
        pass

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return None

def load_from_localstorage():
    try:
        from streamlit_js_eval import streamlit_js_eval
        raw = streamlit_js_eval(js_expressions="localStorage.getItem('wealth_data')", key="load_ls")
        if raw:
            return json.loads(raw)
    except Exception:
        pass
    return None

@st.cache_data(ttl=14400, show_spinner=False)  # Cache 4 hours
def _try_fetch_fx():
    """Try to fetch live FX rates. Returns dict or None."""
    # Try Yahoo Finance (one by one to avoid rate limits)
    try:
        import yfinance as yf
        tickers = {"USD": "AUDUSD=X", "CNY": "AUDCNY=X", "HKD": "AUDHKD=X"}
        result = {}
        for cur, ticker in tickers.items():
            try:
                import time
                time.sleep(1.5)
                data = yf.download(ticker, period="5d", progress=False, auto_adjust=False)
                if not data.empty:
                    result[cur] = data["Close"].dropna().iloc[-1].item()
            except Exception:
                pass
        if len(result) == 3:
            return {k: round(v, 6) for k, v in result.items()}
    except Exception:
        pass
    # Fallback: free API
    try:
        import urllib.request, json as _json
        with urllib.request.urlopen("https://open.er-api.com/v6/latest/AUD", timeout=10) as resp:
            data = _json.loads(resp.read())
            if data.get("result") == "success":
                r = data["rates"]
                return {"USD": round(r["USD"], 6), "CNY": round(r["CNY"], 4), "HKD": round(r["HKD"], 4)}
    except Exception:
        pass
    return None

def fetch_live_fx():
    """Fetch fresh FX rates. On failure, return last good rates from saved data."""
    live = _try_fetch_fx()
    if live:
        return live
    # Fallback: load last saved rates from JSON file
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            saved_fx = saved.get("fx_rates", {})
            if saved_fx.get("USD") and saved_fx.get("CNY") and saved_fx.get("HKD"):
                return saved_fx
    except Exception:
        pass
    # Last resort: hardcoded defaults
    return {"USD": 0.645, "CNY": 4.72, "HKD": 5.04}

def init_data():
    if "data" not in st.session_state:
        loaded = load_data()
        if loaded is None:
            loaded = load_from_localstorage()
        if loaded is None:
            loaded = get_default_data()
        default = get_default_data()
        for k, v in default.items():
            if k not in loaded:
                loaded[k] = v
        # Ensure new fields exist in nested items
        for p in loaded.get("properties", []):
            p.setdefault("interest_rate", 6.0)
            p.setdefault("loan_years", 25)
            p.setdefault("appreciation_rate", 0.0)
        for o in loaded.get("other_assets", []):
            o.setdefault("annual_return", 0.0)
            o.setdefault("taxable_income", False)
            o.setdefault("owner", "joint")
        for i in loaded.get("income", []):
            i.setdefault("owner", "joint")
        so = loaded.get("super_opt", {})
        so.setdefault("m1_self_contrib", 0); so.setdefault("m2_self_contrib", 0)
        so.setdefault("m1_planned_annual_contrib", 0); so.setdefault("m2_planned_annual_contrib", 0)
        st.session_state.data = loaded
    if "lang" not in st.session_state:
        st.session_state.lang = st.session_state.data.get("lang", "en")
    if not st.session_state.get("_fx_auto_fetched"):
        live = fetch_live_fx()
        if live:
            st.session_state.data["fx_rates"].update(live)
        st.session_state._fx_auto_fetched = True

# ================================================================
# CURRENCY HELPERS
# ================================================================
def to_aud(amount, from_cur, fx):
    if from_cur == "AUD": return amount
    rate = fx.get(from_cur, 1)
    return amount / rate if rate else amount

def from_aud(amount, to_cur, fx):
    if to_cur == "AUD": return amount
    return amount * fx.get(to_cur, 1)

def to_display(amount, from_cur, display_cur, fx):
    return from_aud(to_aud(amount, from_cur, fx), display_cur, fx)

# ================================================================
# FINANCIAL CALCULATIONS
# ================================================================
AU_TAX_BRACKETS = [(18200, 0), (45000, 0.16), (135000, 0.30), (190000, 0.37), (float("inf"), 0.45)]
# 2025-26 Medicare levy low-income thresholds (single, no dependants) — below LOWER: no levy;
# LOWER-UPPER: levy phases in at 10c per $1 over LOWER; above UPPER: full 2%.
MEDICARE_LOWER, MEDICARE_UPPER = 28011, 35013

def medicare_levy(income):
    if income <= MEDICARE_LOWER:
        return 0
    full = income * 0.02
    if income <= MEDICARE_UPPER:
        return min(full, (income - MEDICARE_LOWER) * 0.10)
    return full

def lito(income):
    """Low Income Tax Offset — reduces tax payable (not refundable below $0)."""
    if income <= 37500:
        offset = 700
    elif income <= 45000:
        offset = 700 - 0.05 * (income - 37500)
    elif income <= 66667:
        offset = 325 - 0.015 * (income - 45000)
    else:
        offset = 0
    return max(offset, 0)

def au_income_tax(income):
    tax, prev = 0, 0
    for threshold, rate in AU_TAX_BRACKETS:
        taxable = min(income, threshold) - prev
        if taxable > 0: tax += taxable * rate
        prev = threshold
        if income <= threshold: break
    tax = max(tax - lito(income), 0)
    return tax + medicare_levy(income)

def calc_net_worth(d):
    fx, dc = d["fx_rates"], d["display_currency"]
    total_a, total_l, breakdown = 0, 0, {}
    pv = sum(to_display(p["value"], p["currency"], dc, fx) for p in d["properties"])
    pm = sum(to_display(p["mortgage"], p["currency"], dc, fx) for p in d["properties"])
    total_a += pv; total_l += pm; breakdown["properties"] = pv - pm
    sf = sum(to_display(s["value"], s["currency"], dc, fx) for s in d["super_fund"])
    total_a += sf; breakdown["super_fund"] = sf
    ov = sum(to_display(o["value"], o["currency"], dc, fx) for o in d["other_assets"])
    total_a += ov; breakdown["other"] = ov
    return total_a, total_l, total_a - total_l, breakdown

def calc_passive_income(d):
    """Annual passive income from other_assets based on annual_return %"""
    fx = d["fx_rates"]
    total = 0
    for o in d["other_assets"]:
        ret = o.get("annual_return", 0) / 100
        total += to_aud(o["value"] * ret, o["currency"], fx)
    return total

def calc_cashflow(d):
    fx = d["fx_rates"]
    income_breakdown = []
    # Each taxpayer (self/spouse) is assessed on their own combined taxable income, once,
    # through the progressive brackets — not per income source. "Joint" items split 50/50.
    owner_income = {"self": {"salary": 0.0, "interest": 0.0}, "spouse": {"salary": 0.0, "interest": 0.0}}
    def attribute(owner, amt, kind):
        if owner == "joint":
            owner_income["self"][kind] += amt / 2
            owner_income["spouse"][kind] += amt / 2
        elif owner in owner_income:
            owner_income[owner][kind] += amt
    # Personal salaries
    personal_gross = 0
    for i in d["income"]:
        amt = to_aud(i["amount"], i["currency"], fx)
        personal_gross += amt
        if amt > 0:
            income_breakdown.append({"name": i["name"], "amount": amt})
        attribute(i.get("owner", "joint"), amt, "salary")
    # Interest/income from cash & other accounts flagged as taxable income (e.g. bank savings interest)
    taxable_interest = 0
    for o in d["other_assets"]:
        if not o.get("taxable_income"):
            continue
        amt = to_aud(o["value"], o["currency"], fx) * o.get("annual_return", 0) / 100
        taxable_interest += amt
        if amt > 0:
            income_breakdown.append({"name": o["name"], "amount": amt})
        attribute(o.get("owner", "joint"), amt, "interest")
    personal_gross += taxable_interest
    owner_summary = []
    tax = 0
    personal_after_tax = 0
    for owner in ("self", "spouse"):
        salary = owner_income[owner]["salary"]
        interest = owner_income[owner]["interest"]
        gross = salary + interest
        t_owed = au_income_tax(max(gross, 0))
        tax += t_owed
        personal_after_tax += gross - t_owed
        owner_summary.append({"owner": owner, "salary": salary, "interest": interest,
            "gross": gross, "tax": t_owed, "after_tax": gross - t_owed})
    # Business budget (after GST, minus salaries and super already paid)
    biz = d.get("business", {})
    biz_gross = biz.get("gross_revenue", 0)
    gst = biz_gross * biz.get("gst_rate", 10.0) / 100
    # Super payable by business (12% on all salaries, FY2026-27) — excludes account interest, not salary
    SG_RATE = 0.12
    salaries_gross = sum(to_aud(i["amount"], i["currency"], fx) for i in d["income"])
    super_payable = salaries_gross * SG_RATE
    biz_budget = biz_gross - gst - salaries_gross - super_payable
    # Total available = personal after tax + business budget
    total_available = personal_after_tax + max(biz_budget, 0)
    total_exp = sum(e["annual"] for e in d["expenses"])
    surplus = total_available - total_exp
    return personal_gross, tax, personal_after_tax, total_exp, surplus, max(biz_budget, 0), income_breakdown, owner_summary

def project_retirement(d):
    r = d["retirement"]
    fx = d["fx_rates"]
    years_to = r["target_age"] - r["current_age"]
    years_in = r["life_expectancy"] - r["target_age"]
    ret_return = r["real_return"] / 100
    annual_exp = r["au_cost"] * r["months_au"] + to_aud(r["cn_cost"] * r["months_cn"], "CNY", fx) + r["biz_class_trips"] * r["ticket_price"] * 2 + r["health_ins"]
    passive = calc_passive_income(d)
    # Total investable = super (live from Assets) + other assets (in AUD)
    super_total = sum(to_aud(s["value"], s["currency"], fx) for s in d["super_fund"])
    other_total = sum(to_aud(o["value"], o["currency"], fx) for o in d["other_assets"])
    total_capital = super_total + other_total
    # Accumulation
    bal = total_capital
    acc = [bal]
    for _ in range(years_to):
        bal = bal * (1 + ret_return) + r["annual_contrib"]
        acc.append(bal)
    capital_at_retire = bal
    # Drawdown (passive income offsets expenses)
    net_withdrawal = max(annual_exp - passive, 0)
    draw = [bal]
    deplete_age = None
    for y in range(years_in):
        bal = bal * (1 + ret_return) - net_withdrawal
        if bal <= 0 and deplete_age is None:
            deplete_age = r["target_age"] + y + 1
        bal = max(bal, 0)
        draw.append(bal)
    if deplete_age is None:
        deplete_age = r["life_expectancy"] + 10
    return acc, draw, capital_at_retire, annual_exp, deplete_age, passive

def project_net_worth(d):
    """Total net worth trajectory (properties + super + other assets) for the dashboard chart —
    unlike project_retirement's investable-capital view, this includes property equity, each
    growing/shrinking at its own appreciation rate (mortgage held flat, since no amortization
    schedule is modeled)."""
    r = d["retirement"]
    fx = d["fx_rates"]
    years_to = r["target_age"] - r["current_age"]
    years_in = r["life_expectancy"] - r["target_age"]
    ret_return = r["real_return"] / 100

    prop_bases = [(to_aud(p["value"], p["currency"], fx), to_aud(p["mortgage"], p["currency"], fx),
        p.get("appreciation_rate", 0.0) / 100) for p in d["properties"]]

    def properties_equity(years_elapsed):
        return sum(val * (1 + rate) ** years_elapsed - mort for val, mort, rate in prop_bases)

    super_total = sum(to_aud(s["value"], s["currency"], fx) for s in d["super_fund"])
    other_total = sum(to_aud(o["value"], o["currency"], fx) for o in d["other_assets"])
    invest_bal = super_total + other_total
    annual_exp = r["au_cost"] * r["months_au"] + to_aud(r["cn_cost"] * r["months_cn"], "CNY", fx) + r["biz_class_trips"] * r["ticket_price"] * 2 + r["health_ins"]
    passive = calc_passive_income(d)
    net_withdrawal = max(annual_exp - passive, 0)

    ages = [r["current_age"]]
    totals = [invest_bal + properties_equity(0)]
    for y in range(1, years_to + 1):
        invest_bal = invest_bal * (1 + ret_return) + r["annual_contrib"]
        ages.append(r["current_age"] + y)
        totals.append(invest_bal + properties_equity(y))
    for y in range(1, years_in + 1):
        invest_bal = max(invest_bal * (1 + ret_return) - net_withdrawal, 0)
        ages.append(r["target_age"] + y)
        totals.append(invest_bal + properties_equity(years_to + y))
    return ages, totals, years_to

def ncc_bring_forward_tier(tsb):
    """2026-27 NCC bring-forward tiers (general transfer balance cap $2.1M).
    Returns (bring_forward_cap, bring_forward_years)."""
    if tsb < 1_840_000:
        return 390000, 3
    elif tsb < 1_970_000:
        return 260000, 2
    elif tsb < 2_100_000:
        return 130000, 0
    else:
        return 0, 0

def project_super_balance(balance, salary, planned_annual_contrib, real_return_pct, years):
    """Project a super balance forward: each year adds SG (12% of current salary) plus a
    planned self-contribution, compounded at the given real return rate."""
    bal = balance
    ret = real_return_pct / 100
    sg = salary * 0.12
    for _ in range(years):
        bal = bal * (1 + ret) + sg + planned_annual_contrib
    return bal

def run_monte_carlo(params):
    np.random.seed(42)
    ic, aw, yrs = params["initial_capital"], params["annual_withdrawal"], params["years"]
    real_r = (1 + params["nominal_return"]/100) / (1 + params["inflation"]/100) - 1
    vol = params["volatility"] / 100
    n = params["num_sims"]
    returns = np.random.normal(real_r, vol, (n, yrs))
    bal = np.zeros((n, yrs + 1)); bal[:, 0] = ic
    for y in range(yrs):
        bal[:, y+1] = np.maximum(bal[:, y] * (1 + returns[:, y]) - aw, 0)
    return {
        "success": np.mean(bal[:, -1] > 0),
        "p10": np.percentile(bal, 10, axis=0), "p25": np.percentile(bal, 25, axis=0),
        "p50": np.percentile(bal, 50, axis=0), "p75": np.percentile(bal, 75, axis=0),
        "p90": np.percentile(bal, 90, axis=0),
    }

def stress_test_sequence(params, crash_year, crash_pct=-0.35, recovery_years=3, cash_bucket=0):
    ic = params["initial_capital"] - cash_bucket
    aw, yrs = params["annual_withdrawal"], params["years"]
    real_r = ((1+params["nominal_return"]/100)/(1+params["inflation"]/100))-1
    bal, cash = ic, cash_bucket
    sa = params.get("start_age", 60)
    for y in range(yrs):
        r = crash_pct if y == crash_year else (real_r * 1.3 if crash_year < y <= crash_year + recovery_years else real_r)
        if y >= crash_year and y < crash_year + 2 and cash > 0:
            w = min(aw, cash); cash -= w; bal = bal * (1 + r) - (aw - w)
        else:
            bal = bal * (1 + r) - aw
        if bal <= 0: return 0, sa + y + 1
    return bal, sa + yrs

# ================================================================
# LOGIN
# ================================================================
def check_password():
    if st.session_state.get("authenticated"):
        return True
    st.markdown("<div style='max-width:400px;margin:120px auto;text-align:center'>", unsafe_allow_html=True)
    st.title(t("login_title"))
    pw = st.text_input(t("login_prompt"), type="password", key="login_pw")
    if st.button(t("login_btn"), type="primary", width='stretch'):
        try:
            correct = st.secrets["password"]
        except Exception:
            correct = "hello1234"
        if pw == correct:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error(t("login_error"))
    st.markdown("</div>", unsafe_allow_html=True)
    return False

# ================================================================
# PAGES
# ================================================================
def page_dashboard():
    d = st.session_state.data
    total_a, total_l, nw, breakdown = calc_net_worth(d)
    gross, tax, after_tax, total_exp, surplus, biz_budget, income_breakdown, owner_summary = calc_cashflow(d)
    _, _, cap_retire, annual_exp_ret, deplete_age, passive = project_retirement(d)
    dc = d["display_currency"]
    fx = d["fx_rates"]

    # Net worth in all currencies
    nw_aud = to_aud(nw, dc, fx) if dc != "AUD" else nw
    st.subheader(t("net_worth"))
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("AUD", fmt_cur(nw_aud, "AUD"))
    c2.metric("USD", fmt_cur(nw_aud * fx.get("USD", 0.645), "USD"))
    c3.metric("CNY", fmt_cur(nw_aud * fx.get("CNY", 4.72), "CNY"))
    c4.metric("HKD", fmt_cur(nw_aud * fx.get("HKD", 5.04), "HKD"))

    needed = annual_exp_ret * 25
    gap = cap_retire - needed
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(t("annual_cashflow"), fmt_cur(surplus, "AUD"))
    c2.metric(t("retirement_gap"), fmt_cur(gap, "AUD"), "✅" if gap >= 0 else "⚠️")
    c3.metric(t("retire_age"), f"{d['retirement']['target_age']}", "✅" if gap >= 0 else t("need_more_contrib"))
    c4.metric(t("passive_income"), fmt_cur(passive, "AUD") if passive > 0 else "—")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader(t("asset_allocation"))
        labels = [t("properties"), t("super_fund"), t("cash_other")]
        values = [max(breakdown.get(k, 0), 0) for k in ["properties", "super_fund", "other"]]
        if sum(values) > 0:
            fig = go.Figure(go.Pie(labels=labels, values=values, hole=0.55,
                marker=dict(colors=["#4da6ff", "#a371f7", "#d29922"]),
                textinfo="label+percent", textfont=dict(size=12)))
            fig.update_layout(**PLOTLY_LAYOUT, height=320, showlegend=False)
            fig.add_annotation(text=fmt_cur(nw, dc), x=0.5, y=0.5, font=dict(size=18, color="#e6edf3"), showarrow=False)
            st.plotly_chart(fig, width='stretch')
        else:
            st.info(t("enter_data_first"))
    with col2:
        st.subheader(t("net_worth_proj"))
        r = d["retirement"]
        ages, totals, years_to = project_net_worth(d)
        split = years_to + 1
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ages[:split], y=totals[:split], mode="lines",
            name=t("accumulation"), line=dict(color="#3fb950", width=2), fill="tozeroy", fillcolor="rgba(63,185,80,0.1)"))
        fig.add_trace(go.Scatter(x=ages[split-1:], y=totals[split-1:], mode="lines",
            name=t("drawdown"), line=dict(color="#f85149", width=2), fill="tozeroy", fillcolor="rgba(248,81,73,0.1)"))
        fig.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.3)")
        fig.update_layout(**PLOTLY_LAYOUT, height=320, xaxis_title=t("age"), yaxis_title=dc)
        st.plotly_chart(fig, width='stretch')
    # Alerts
    st.subheader(t("alerts"))
    sf_total = sum(to_aud(s["value"], s["currency"], d["fx_rates"]) for s in d["super_fund"])
    if sf_total > 0:
        mx = max(d["super_fund"], key=lambda s: to_aud(s["value"], s["currency"], d["fx_rates"]))
        pct = to_aud(mx["value"], mx["currency"], d["fx_rates"]) / sf_total * 100
        if pct > 70:
            st.warning(t("sf_concentration_warn").format(pct=pct, name=mx["name"]))
    if gap < 0:
        st.error(t("retire_gap_warn").format(gap=fmt_md(abs(gap), dc)))
    else:
        st.success(t("retire_ok"))


def page_assets():
    d = st.session_state.data
    fx, dc = d["fx_rates"], d["display_currency"]

    # ── Properties ──
    st.subheader(t("properties"))
    props_rm = []
    for i, p in enumerate(d["properties"]):
        # Row 1: Currency, Name, Value, Delete
        c1, c2, c3, c4 = st.columns([1, 3, 2, 0.4])
        p["currency"] = c1.selectbox("ccy", CURRENCIES, index=CURRENCIES.index(p["currency"]),
            key=f"pc_{i}", format_func=lambda x: f"{CUR_FLAGS[x]}", label_visibility="collapsed")
        p["name"] = c2.text_input("name", p["name"], key=f"pn_{i}", label_visibility="collapsed")
        p["value"] = money_input("", p["value"], f"pv_{i}", container=c3)
        if c4.button("✕", key=f"prm_{i}"):
            props_rm.append(i)
        # Row 2: Mortgage details
        c1, c2, c3, c4 = st.columns([1, 2, 1, 2])
        c1.markdown(f"<div style='display:flex;align-items:center;height:56px;font-size:13px;color:#8b949e'>{t('mortgage')}</div>", unsafe_allow_html=True)
        p["mortgage"] = money_input("", p["mortgage"], f"pm_{i}", container=c2)
        p["interest_rate"] = c3.number_input("Rate%", value=p.get("interest_rate", 6.0),
            step=0.1, format="%.2f", key=f"pir_{i}", label_visibility="collapsed")
        auto_repay = calc_monthly_repayment(p["mortgage"], p["interest_rate"])
        p["monthly_repay"] = auto_repay
        sym = CUR_SYMBOLS[p['currency']]
        c4.markdown(f"<div style='display:flex;align-items:center;height:56px;font-size:13px;color:#8b949e'>{sym}{auto_repay:,.0f}/mo · {t('equity')}: {sym}{p['value']-p['mortgage']:,.0f}</div>", unsafe_allow_html=True)
        # Row 3: Appreciation / depreciation rate (can be negative)
        c1, c2, c3 = st.columns([1, 2, 3])
        c1.markdown(f"<div style='display:flex;align-items:center;height:56px;font-size:13px;color:#8b949e'>{t('appreciation_rate')}</div>", unsafe_allow_html=True)
        p["appreciation_rate"] = c2.number_input("Rate%", value=p.get("appreciation_rate", 0.0),
            step=0.5, format="%.1f", key=f"par_{i}", label_visibility="collapsed")
        proj_10y = p["value"] * (1 + p["appreciation_rate"] / 100) ** 10
        c3.markdown(f"<div style='display:flex;align-items:center;height:56px;font-size:13px;color:#8b949e'>{t('in_10_years')}: {sym}{proj_10y:,.0f}</div>", unsafe_allow_html=True)
        st.divider()
    for i in sorted(props_rm, reverse=True):
        d["properties"].pop(i); st.rerun()
    if st.button(t("add_property")):
        d["properties"].append({"name": t("new_property"), "value": 0, "currency": "AUD",
            "mortgage": 0, "interest_rate": 6.0, "loan_years": 25, "monthly_repay": 0, "appreciation_rate": 0.0}); st.rerun()

    # ── Super Fund ──
    st.subheader(t("super_fund"))
    sf_rm = []
    for i, s in enumerate(d["super_fund"]):
        c1, c2, c3, c4 = st.columns([1, 3, 2, 0.4])
        s["currency"] = c1.selectbox("ccy", CURRENCIES, index=CURRENCIES.index(s["currency"]),
            key=f"sc_{i}", format_func=lambda x: f"{CUR_FLAGS[x]}", label_visibility="collapsed")
        s["name"] = c2.text_input("name", s["name"], key=f"sn_{i}", label_visibility="collapsed")
        s["value"] = money_input("", s["value"], f"sv_{i}", container=c3)
        if c4.button("✕", key=f"srm_{i}"):
            sf_rm.append(i)
    for i in sorted(sf_rm, reverse=True):
        d["super_fund"].pop(i); st.rerun()
    sf_aud = sum(to_aud(s["value"], s["currency"], fx) for s in d["super_fund"])
    c1, c2 = st.columns(2)
    if c1.button(t("add_super_item")):
        d["super_fund"].append({"name": t("new_item"), "value": 0, "currency": "AUD"}); st.rerun()
    c2.caption(f"{t('sf_total_label')}: {fmt_md(to_display(sf_aud, 'AUD', dc, fx), dc)}")

    # ── Cash & Other ──
    st.subheader(t("cash_other"))
    others_rm = []
    for i, o in enumerate(d["other_assets"]):
        c1, c2, c3, c4, c5, c6, c7 = st.columns([1, 2.5, 1.8, 0.8, 1, 1.1, 0.4])
        o["currency"] = c1.selectbox("ccy", CURRENCIES, index=CURRENCIES.index(o["currency"]),
            key=f"oc_{i}", format_func=lambda x: f"{CUR_FLAGS[x]}", label_visibility="collapsed")
        o["name"] = c2.text_input("name", o["name"], key=f"on_{i}", label_visibility="collapsed")
        o["value"] = money_input("", o["value"], f"ov_{i}", container=c3)
        o["annual_return"] = c4.number_input("Ret%", value=o.get("annual_return", 0.0),
            step=0.25, format="%.2f", key=f"oar_{i}", label_visibility="collapsed")
        o["taxable_income"] = c5.checkbox(t("taxable_income"), value=o.get("taxable_income", False),
            key=f"oti_{i}")
        o["owner"] = c6.selectbox(t("owner"), OWNERS, index=OWNERS.index(o.get("owner", "joint")),
            key=f"oo_{i}", format_func=lambda x: t(f"owner_{x}"), label_visibility="collapsed")
        if c7.button("✕", key=f"orm_{i}"):
            others_rm.append(i)
    for i in sorted(others_rm, reverse=True):
        d["other_assets"].pop(i); st.rerun()
    passive = calc_passive_income(d)
    c1, c2 = st.columns(2)
    if c1.button(t("add_asset")):
        d["other_assets"].append({"name": t("new_asset"), "value": 0, "currency": "AUD", "annual_return": 0.0, "taxable_income": False, "owner": "joint"}); st.rerun()
    if passive > 0:
        c2.caption(f"📈 {t('passive_income')}: {fmt_md(passive, 'AUD')}/yr")

    # ── Summary ──
    st.divider()
    total_a, total_l, nw, _ = calc_net_worth(d)
    c1, c2 = st.columns([4, 1])
    with c1:
        fx_str = " · ".join([f"AUD/{k} {v:.4f}" for k, v in fx.items()])
        st.caption(f"{t('fx_label')}: {fx_str}")
        st.markdown(f"**{fmt_md(total_a, dc)}** − {fmt_md(total_l, dc)} = **{fmt_md(nw, dc)}**")
    with c2:
        new_dc = st.selectbox(t("display_cur"), CURRENCIES, index=CURRENCIES.index(dc), key="asset_dc",
            format_func=lambda x: f"{CUR_FLAGS[x]}", label_visibility="collapsed")
        if new_dc != dc: d["display_currency"] = new_dc; st.rerun()


def page_cashflow():
    d = st.session_state.data
    dc = d["display_currency"]
    fx = d["fx_rates"]
    d.setdefault("business", {"gross_revenue": 0, "gst_rate": 10.0})
    biz = d["business"]

    # ── Business ──
    st.subheader(t("biz_section"))
    c1, c2 = st.columns(2)
    biz["gross_revenue"] = money_input(t("biz_gross"), biz["gross_revenue"], "biz_gross")
    biz["gst_rate"] = c2.number_input(t("gst_rate"), value=biz.get("gst_rate", 10.0),
        step=0.5, format="%.1f", key="biz_gst")
    # Placeholder: filled in after the Income section below commits this render's salary edits,
    # so these metrics never show a stale (previous-render) salary total.
    biz_metrics = st.empty()

    # ── Personal Income (salaries/drawings from business) ──
    st.subheader(t("income"))
    st.caption(t("personal_salary"))
    inc_rm = []
    for i, inc in enumerate(d["income"]):
        c1, c2, c3, c4, c5, c6 = st.columns([1, 2.5, 2, 1.1, 1.2, 0.5])
        inc["currency"] = c1.selectbox("ccy", CURRENCIES, index=CURRENCIES.index(inc["currency"]),
            key=f"ic_{i}", label_visibility="collapsed", format_func=lambda x: f"{CUR_FLAGS[x]}")
        inc["name"] = c2.text_input("name", inc["name"], key=f"in_{i}", label_visibility="collapsed")
        inc["amount"] = money_input("", inc["amount"], f"ia_{i}", container=c3)
        inc["owner"] = c4.selectbox(t("owner"), OWNERS, index=OWNERS.index(inc.get("owner", "joint")),
            key=f"io_{i}", format_func=lambda x: t(f"owner_{x}"), label_visibility="collapsed")
        c5.caption(esc(f"{CUR_SYMBOLS.get(inc['currency'],'A$')}{inc['amount']/12:,.0f}/mo"))
        if c6.button("✕", key=f"irm_{i}"):
            inc_rm.append(i)
    for i in sorted(inc_rm, reverse=True):
        d["income"].pop(i); st.rerun()
    if st.button(t("add_income")):
        d["income"].append({"name": t("new_income"), "amount": 0, "currency": "AUD", "owner": "joint"}); st.rerun()

    # Now that d["income"] reflects this render's edits, compute and draw the Business metrics
    # (matches the biz_budget formula in calc_cashflow: after-GST revenue minus salaries and super).
    gst_amount = biz["gross_revenue"] * biz["gst_rate"] / 100
    after_gst = biz["gross_revenue"] - gst_amount
    salaries_gross = sum(to_aud(i["amount"], i["currency"], fx) for i in d["income"])
    SG_RATE = 0.12  # 12% for FY2026-27
    super_payable = salaries_gross * SG_RATE
    biz_expenses_budget = after_gst - salaries_gross - super_payable
    with biz_metrics.container():
        bc1, bc2, bc3 = st.columns(3)
        bc1.metric(t("after_gst"), fmt_cur(after_gst, "AUD"), f"GST: {fmt_cur(gst_amount, 'AUD')}")
        bc2.metric(t("total_salaries"), fmt_cur(salaries_gross + super_payable, "AUD"),
            f"Super: {fmt_cur(super_payable, 'AUD')}" if super_payable > 0 else None)
        bc3.metric(t("biz_expense_budget"), fmt_cur(biz_expenses_budget, "AUD"))

    # Expenses
    st.subheader(t("expenses"))
    # Auto-calculate total annual mortgage from properties
    total_monthly_repay = sum(p.get("monthly_repay", 0) for p in d["properties"])
    total_annual_repay = round(total_monthly_repay * 12)
    def is_mortgage_exp(name):
        n = name.lower()
        return "房贷" in name or "mortgage" in n or "home loan" in n
    for exp in d["expenses"]:
        if is_mortgage_exp(exp["name"]):
            exp["annual"] = total_annual_repay
    exp_rm = []
    for i, exp in enumerate(d["expenses"]):
        is_mortgage = is_mortgage_exp(exp["name"])
        c1, c2, c3, c4 = st.columns([4, 3, 2, 0.6])
        if is_mortgage:
            c1.text_input(t("name"), t("home_loan_repayment"), key=f"en_{i}", disabled=True, label_visibility="collapsed")
            c2.text_input("annual", f"{total_annual_repay:,}", key=f"ea_m_{i}", disabled=True, label_visibility="collapsed")
            c3.caption(f"{t('monthly')} {esc(CUR_SYMBOLS.get(dc,'$'))}{total_monthly_repay:,.0f} · {t('auto_link')}")
        else:
            exp["name"] = c1.text_input(t("name"), exp["name"], key=f"en_{i}", label_visibility="collapsed")
            exp["annual"] = money_input("", exp["annual"], f"ea_{i}", container=c2)
            c3.caption(f"{t('monthly')} {esc(CUR_SYMBOLS.get(dc,'$'))}{exp['annual']/12:,.0f}")
            if c4.button("✕", key=f"erm_{i}"):
                exp_rm.append(i)
    for i in sorted(exp_rm, reverse=True):
        d["expenses"].pop(i); st.rerun()
    if st.button(t("add_expense")):
        d["expenses"].append({"name": t("new_expense"), "annual": 0}); st.rerun()

    # Summary
    st.divider()
    gross, tax, after_tax, total_exp, surplus, biz_budget, income_breakdown, owner_summary = calc_cashflow(d)
    total_available = after_tax + biz_budget

    st.subheader(t("income_by_person"))
    p1, p2 = st.columns(2)
    for col, o in zip((p1, p2), owner_summary):
        owner_key = o["owner"]
        with col.container(border=True):
            st.markdown(f"**{t('owner_' + owner_key)}**")
            st.caption(f"{t('salary_income')}: {fmt_md(o['salary'], 'AUD')}")
            st.caption(f"{t('savings_income')}: {fmt_md(o['interest'], 'AUD')}")
            st.caption(f"{t('gross_income')}: {fmt_md(o['gross'], 'AUD')}")
            st.caption(f"{t('tax_payable')}: {fmt_md(o['tax'], 'AUD')}")
            st.markdown(f"{t('after_tax_income')}: **{fmt_md(o['after_tax'], 'AUD')}**")

    c1, c2, c3 = st.columns(3)
    c1.metric(t("biz_expense_budget"), fmt_cur(biz_budget, "AUD"))
    c2.metric(t("total_expenses"), fmt_cur(total_exp, "AUD"))
    c3.metric(t("net_surplus"), fmt_cur(surplus, "AUD"),
        f"{t('savings_rate')} {surplus/total_available*100:.0f}%" if total_available > 0 else "—")
    if income_breakdown:
        st.caption(f"{t('income_breakdown')}: " + " · ".join(
            f"{esc(b['name'])} {fmt_md(b['amount'], 'AUD')}" for b in income_breakdown))
    # Waterfall — household expenses against after-tax income (tax already deducted per person above)
    st.subheader(t("waterfall"))
    labels, values = [t("household_available")], [total_available]
    for e in d["expenses"]:
        if e["annual"] > 0: labels.append(e["name"]); values.append(-e["annual"])
    labels.append(t("net_surplus")); values.append(surplus)
    measures = ["absolute"] + ["relative"] * (len(labels) - 2) + ["total"]
    fig = go.Figure(go.Waterfall(x=labels, y=values, measure=measures,
        connector=dict(line=dict(color="rgba(255,255,255,0.1)")),
        increasing=dict(marker=dict(color="#3fb950")),
        decreasing=dict(marker=dict(color="#f85149")),
        totals=dict(marker=dict(color="#4da6ff")),
        textposition="outside", textfont=dict(size=10)))
    fig.update_layout(**PLOTLY_LAYOUT, height=400, showlegend=False)
    st.plotly_chart(fig, width='stretch')


def page_retirement():
    d = st.session_state.data
    r = d["retirement"]; dc = d["display_currency"]
    c1, c2, c3, c4 = st.columns(4)
    r["current_age"] = c1.number_input(t("current_age"), value=r["current_age"], min_value=18, max_value=80, key="r_ca")
    r["target_age"] = c2.number_input(t("target_retire_age"), value=r["target_age"], min_value=40, max_value=80, key="r_ta")
    r["life_expectancy"] = c3.number_input(t("life_expectancy"), value=r["life_expectancy"], min_value=70, max_value=110, key="r_le")
    r["real_return"] = c4.number_input(t("real_return"), value=r["real_return"], step=0.5, format="%.1f", key="r_rr")
    st.subheader(t("lifestyle_settings"))
    c1, c2 = st.columns(2)
    with c1:
        r["months_au"] = st.number_input(t("months_au"), value=r["months_au"], min_value=0, max_value=12, key="r_mau")
        r["au_cost"] = money_input(t("au_cost_aud"), r["au_cost"], "r_auc")
        st.caption(esc(f"A${r['au_cost']:,} × {r['months_au']}mo = A${r['au_cost']*r['months_au']:,}/yr"))
        r["biz_class_trips"] = st.number_input(t("biz_class_trips"), value=r["biz_class_trips"], min_value=0, max_value=12, key="r_bct")
    with c2:
        r["months_cn"] = st.number_input(t("months_cn"), value=r["months_cn"], min_value=0, max_value=12, key="r_mcn")
        r["cn_cost"] = money_input(t("cn_cost_aud"), r["cn_cost"], "r_cnc")
        cn_annual_aud = to_aud(r["cn_cost"] * r["months_cn"], "CNY", d["fx_rates"])
        st.caption(esc(f"¥{r['cn_cost']:,} × {r['months_cn']}mo = A${cn_annual_aud:,.0f}/yr"))
        r["ticket_price"] = money_input(t("ticket_aud"), r["ticket_price"], "r_tp")
    c1, c2, c3 = st.columns(3)
    r["health_ins"] = money_input(t("health_ins_aud"), r["health_ins"], "r_hi", container=c1)
    r["annual_contrib"] = money_input(t("contrib_aud"), r["annual_contrib"], "r_ac", container=c2)
    # Super total is no longer entered here — it's fetched live from the Assets page's Super Fund section.
    fx = d["fx_rates"]
    super_total = sum(to_aud(s["value"], s["currency"], fx) for s in d["super_fund"])
    c3.metric(t("current_super_total"), fmt_cur(super_total, "AUD"))
    # Calculate
    acc, draw, cap_retire, annual_exp, deplete_age, passive = project_retirement(d)
    needed = annual_exp * 25
    net_withdrawal = max(annual_exp - passive, 0)
    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(t("total_annual_expense"), fmt_cur(annual_exp, dc), help=t("total_annual_expense_help"))
    c2.metric(t("capital_needed_4pct"), fmt_cur(needed, dc), help=t("capital_needed_4pct_help"))
    c3.metric(t("capital_at_retire"), fmt_cur(cap_retire, dc), help=t("capital_at_retire_help"))
    gap = cap_retire - needed
    c4.metric(t("retirement_gap"), fmt_cur(gap, dc), t("surplus_ok") if gap >= 0 else t("shortfall"),
        help=t("retirement_gap_help"))
    if passive > 0:
        if cap_retire > 0 and passive > 0:
            st.info(t("passive_retire_note").format(p=fmt_md(passive, "AUD"), w=fmt_md(net_withdrawal, "AUD"), r=f"{net_withdrawal/cap_retire*100:.1f}"))
    # Chart
    st.subheader(t("projection"))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(range(r["current_age"], r["target_age"]+1)), y=acc, mode="lines+markers",
        name=t("accumulation"), line=dict(color="#3fb950", width=2.5), marker=dict(size=3)))
    fig.add_trace(go.Scatter(x=list(range(r["target_age"], r["life_expectancy"]+1)), y=draw, mode="lines+markers",
        name=t("drawdown"), line=dict(color="#f85149", width=2.5), marker=dict(size=3)))
    fig.add_hline(y=needed, line_dash="dot", line_color="#4da6ff", annotation_text="4% Rule Line")
    fig.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.3)")
    fig.update_layout(**PLOTLY_LAYOUT, height=400, xaxis_title=t("age"), yaxis_title=f"{t('capital')} ({dc})")
    st.plotly_chart(fig, width='stretch')
    # Sensitivity
    st.subheader(t("sensitivity"))
    scenarios = []
    for label, ret in [(t("conservative"), 2.5), (t("baseline"), 3.5), (t("optimistic"), 4.5)]:
        old = r["real_return"]; r["real_return"] = ret
        _, _, cr, ae, da, _ = project_retirement(d); r["real_return"] = old
        lasts = f"{da}{t('age_suffix')}" if da <= r["life_expectancy"] else f">{r['life_expectancy']}{t('age_suffix')}"
        scenarios.append({t("scenario"): label, t("capital_at_retire"): fmt_cur(cr, dc), t("lasts_until"): lasts,
            t("status"): "✅" if da > r["life_expectancy"] else ("⚠️" if da > r["life_expectancy"]-5 else "❌")})
    st.dataframe(scenarios, width='stretch', hide_index=True)
    if gap >= 0:
        st.success(t("suggest_ok").format(cost=fmt_md(r["biz_class_trips"]*r["ticket_price"]*2, dc)))
    else:
        extra = abs(gap) / max(r["target_age"] - r["current_age"], 1)
        st.warning(t("suggest_gap").format(extra=fmt_md(extra, dc)))


def page_super():
    d = st.session_state.data; so = d["super_opt"]; fx = d["fx_rates"]
    st.subheader(t("sf_current"))
    sf_total = sum(to_aud(s["value"], s["currency"], fx) for s in d["super_fund"])
    c1, c2, c3 = st.columns(3)
    c1.metric(t("sf_total"), fmt_cur(sf_total, "AUD"))
    if sf_total > 0:
        mx = max(d["super_fund"], key=lambda s: to_aud(s["value"], s["currency"], fx))
        pct = to_aud(mx["value"], mx["currency"], fx) / sf_total * 100
        c2.metric(t("sf_concentration"), f"{pct:.0f}% ({mx['name']})")
        liquid = sf_total - to_aud(mx["value"], mx["currency"], fx) if pct > 50 else sf_total
        c3.metric(t("sf_liquid"), fmt_cur(liquid, "AUD"))

    st.subheader(t("concessional"))
    # Auto-pull income from Cash Flow
    incomes = d.get("income", [])
    m1_income = to_aud(incomes[0]["amount"], incomes[0]["currency"], fx) if len(incomes) > 0 else 0
    m2_income = to_aud(incomes[1]["amount"], incomes[1]["currency"], fx) if len(incomes) > 1 else 0
    SG_RATE = 0.12  # 12% for FY2026-27
    CC_CAP, NCC_CAP = 32500, 130000  # FY2026-27 ATO caps

    members = []
    c1, c2 = st.columns(2)
    for col, p, name, income in [(c1, "m1", so["m1_name"], m1_income), (c2, "m2", so["m2_name"], m2_income)]:
        with col:
            st.markdown(f"**{name}**")
            balance = money_input(t("super_bal_aud"), so[f"{p}_balance"], f"so_{p}b")
            so[f"{p}_balance"] = balance
            sg = round(income * SG_RATE)
            so[f"{p}_sg"] = sg
            so[f"{p}_income"] = income
            idx = 0 if p == "m1" else 1
            if len(incomes) > idx:
                st.caption(esc(f"🔗 {incomes[idx]['name']}: A${income:,.0f}"))
            st.caption(esc(f"SG: A${sg:,.0f}") + f" ({SG_RATE*100:.0f}%)")
            # Carry-forward eligibility (TSB < $500k) computed here so the self-contribution
            # input below can be capped at this member's actual max room.
            room = max(CC_CAP - sg, 0)
            can_cf = balance < 500000
            cf_est = max(min(5 * CC_CAP - sg, 5 * CC_CAP), 0) if can_cf else 0
            max_cc = room + cf_est
            self_contrib = money_input(t("planned_self_contrib"),
                so.get(f"{p}_self_contrib", 0), f"so_{p}sc", max_value=max_cc)
            so[f"{p}_self_contrib"] = self_contrib
            remaining = max_cc - self_contrib
            st.caption(f"{t('remaining_room')}: A${remaining:,.0f}" + (" ⚠️" if max_cc > 0 and self_contrib >= max_cc else ""))
            members.append({"name": name, "balance": balance, "sg": sg, "income": income,
                "room": room, "can_cf": can_cf, "cf_est": cf_est, "max_cc": max_cc, "self_contrib": self_contrib})

    st.divider()
    results = []
    for m in members:
        mr = 0.45 if m["income"] > 190000 else (0.37 if m["income"] > 135000 else (0.30 if m["income"] > 45000 else 0.16))
        tax_saving = m["self_contrib"] * (mr + 0.02 - 0.15)
        results.append({t("member"): m["name"], t("cc_cap"): f"${CC_CAP:,}", t("cc_used"): f"${m['sg']:,.0f}",
            t("cc_room"): f"${m['room']:,.0f}",
            t("carry_forward"): f"✅ ~${m['cf_est']:,.0f}" if m["can_cf"] else "❌ >$500k",
            t("optimal_cc"): f"${m['max_cc']:,.0f}",
            t("planned_self_contrib"): f"${m['self_contrib']:,.0f}",
            t("tax_saved"): f"${tax_saving:,.0f}"})
    st.dataframe(results, width='stretch', hide_index=True)

    st.subheader(t("ncc"))
    ncc_r = []
    for m in members:
        bf_cap, bf_years = ncc_bring_forward_tier(m["balance"])
        eligible = m["balance"] < 2_100_000
        bf_label = f"${bf_cap:,} ({bf_years}yr)" if bf_years > 0 else (f"${bf_cap:,} ({t('no_bring_fwd')})" if bf_cap > 0 else "$0")
        ncc_r.append({t("member"): m["name"], t("ncc_annual"): f"${NCC_CAP:,}",
            t("bring_forward"): bf_label,
            t("eligible"): "✅" if eligible else "❌ ≥$2.1M"})
    st.dataframe(ncc_r, width='stretch', hide_index=True)
    for m in members:
        th = m["income"] + CC_CAP
        if th > 250000 and m["income"] > 0:
            st.warning(t("div293_over").format(name=m["name"], th=th))
        elif m["income"] > 0:
            st.info(t("div293_room").format(name=m["name"], room=250000-th))

    # Long-term projection: planned average annual self-contribution until retirement
    st.divider()
    st.subheader(t("super_at_retire_projection"))
    r = d["retirement"]
    years_to_retire = max(r["target_age"] - r["current_age"], 0)
    c1, c2 = st.columns(2)
    current_total, projected_total = 0, 0
    for col, m, p in zip((c1, c2), members, ("m1", "m2")):
        with col:
            st.markdown(f"**{m['name']}**")
            planned = money_input(t("planned_annual_contrib"), so.get(f"{p}_planned_annual_contrib", 0), f"so_{p}pac")
            so[f"{p}_planned_annual_contrib"] = planned
            projected = project_super_balance(m["balance"], m["income"], planned, r["real_return"], years_to_retire)
            current_total += m["balance"]; projected_total += projected
            st.metric(f"{m['name']} @ {r['target_age']}{t('age_suffix')}", fmt_cur(projected, "AUD"),
                help=t("super_projection_help"))
    st.caption(f"{t('current_super_total')}: {fmt_md(current_total, 'AUD')} → {t('super_at_retire_projection')}: {fmt_md(projected_total, 'AUD')} ({years_to_retire}{t('age_suffix')})")


def page_monte_carlo():
    d = st.session_state.data; mc = d["monte_carlo"]

    # Auto-pull from retirement projection
    acc, draw, cap_retire, annual_exp, deplete_age, passive = project_retirement(d)
    net_withdrawal = max(annual_exp - passive, 0)
    mc["initial_capital"] = round(cap_retire)
    mc["annual_withdrawal"] = round(net_withdrawal)
    mc["years"] = d["retirement"]["life_expectancy"] - d["retirement"]["target_age"]

    st.subheader(t("mc_params"))
    c1, c2, c3 = st.columns(3)
    c1.metric(t("initial_capital"), f"A${mc['initial_capital']:,}")
    c2.metric(t("annual_withdrawal"), f"A${mc['annual_withdrawal']:,}")
    c3.metric(t("sim_years"), f"{mc['years']}")
    st.caption("🔗 " + ("以上三项自动从退休规划页联动" if st.session_state.lang == "zh" else "Above 3 values auto-linked from Retirement page"))

    c1, c2, c3 = st.columns(3)
    mc["nominal_return"] = c1.number_input(t("nominal_return"), value=mc["nominal_return"], step=0.5, format="%.1f", key="mc_nr")
    mc["volatility"] = c2.number_input(t("volatility"), value=mc["volatility"], step=1.0, format="%.1f", key="mc_vol")
    mc["inflation"] = c3.number_input(t("inflation"), value=mc["inflation"], step=0.5, format="%.1f", key="mc_inf")
    mc["num_sims"] = st.slider(t("num_sims"), 1000, 20000, mc["num_sims"], 1000, key="mc_ns")
    if st.button(t("run_sim"), type="primary"):
        with st.spinner("⏳"):
            st.session_state.mc_result = run_monte_carlo(mc)
    if "mc_result" in st.session_state:
        result = st.session_state.mc_result
        c1, c2, c3 = st.columns(3)
        sr = result["success"]
        c1.metric(t("success_rate"), f"{sr*100:.1f}%", "✅" if sr > 0.9 else ("⚠️" if sr > 0.8 else "❌"))
        c2.metric(t("median_end"), fmt_cur(result["p50"][-1], "AUD"))
        c3.metric(t("p10_end"), fmt_cur(result["p10"][-1], "AUD"))
        st.subheader(t("fan_chart"))
        years = list(range(mc["years"] + 1))
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=years, y=result["p90"].tolist(), mode="lines", line=dict(width=0), showlegend=False))
        fig.add_trace(go.Scatter(x=years, y=result["p10"].tolist(), mode="lines", line=dict(width=0),
            fill="tonexty", fillcolor="rgba(163,113,247,0.15)", name="P10–P90"))
        fig.add_trace(go.Scatter(x=years, y=result["p75"].tolist(), mode="lines", line=dict(width=0), showlegend=False))
        fig.add_trace(go.Scatter(x=years, y=result["p25"].tolist(), mode="lines", line=dict(width=0),
            fill="tonexty", fillcolor="rgba(77,166,255,0.2)", name="P25–P75"))
        fig.add_trace(go.Scatter(x=years, y=result["p50"].tolist(), mode="lines",
            line=dict(color="#4da6ff", width=2.5), name="P50"))
        fig.add_hline(y=0, line_dash="dash", line_color="rgba(248,81,73,0.5)")
        fig.update_layout(**PLOTLY_LAYOUT, height=400, xaxis_title=t("years_after_retire"), yaxis_title="AUD")
        st.plotly_chart(fig, width='stretch')
        # Stress test
        st.subheader(t("stress_test"))
        sa = d["retirement"].get("target_age", 60)
        mca = {**mc, "start_age": sa}
        rows = []
        for label, cy, cash in [(t("no_crash"), None, 0), (t("crash_yr1"), 0, 0), (t("crash_yr5"), 4, 0),
                (t("crash_yr10"), 9, 0), (t("crash_bucket"), 0, mc["annual_withdrawal"]*2)]:
            if cy is None:
                real_r = ((1+mc["nominal_return"]/100)/(1+mc["inflation"]/100))-1
                b = mc["initial_capital"]
                age = sa + mc["years"]
                for y in range(mc["years"]):
                    b = b*(1+real_r)-mc["annual_withdrawal"]
                    if b <= 0: age = sa+y+1; break
                rows.append({t("scenario"):label,t("crash_year"):"—",t("crash_size"):"—",t("recovery"):"—",
                    t("lasts_until"):f"{'>' if b>0 else ''}{age}{t('age_suffix')}",t("status"):"✅" if b>0 else "⚠️"})
            else:
                eb, ea = stress_test_sequence(mca, cy, cash_bucket=cash)
                rows.append({t("scenario"):label,t("crash_year"):f"{sa+cy}{t('age_suffix')}",t("crash_size"):"-35%",t("recovery"):"3yr",
                    t("lasts_until"):f"{'>' if eb>0 else ''}{ea}{t('age_suffix')}",t("status"):"✅" if eb>0 else "❌"})
        st.dataframe(rows, width='stretch', hide_index=True)
        if sr >= 0.9:
            st.success(t("mc_ok").format(sr=sr*100, bucket=fmt_md(mc["annual_withdrawal"]*2,"AUD")))
        elif sr >= 0.8:
            st.warning(t("mc_warn").format(sr=sr*100))
        else:
            st.error(t("mc_bad").format(sr=sr*100))


def page_settings():
    d = st.session_state.data
    st.subheader(t("language"))
    lang_map = {"English": "en", "中文": "zh"}
    sel = st.selectbox(t("language"), list(lang_map.keys()),
        index=list(lang_map.values()).index(d["lang"]), key="set_lang")
    if lang_map[sel] != d["lang"]:
        d["lang"] = lang_map[sel]; st.session_state.lang = lang_map[sel]; st.rerun()
    st.subheader(t("display_currency_setting"))
    ndc = st.selectbox(t("display_currency_setting"), CURRENCIES, index=CURRENCIES.index(d["display_currency"]),
        key="set_dc", format_func=lambda x: f"{CUR_FLAGS[x]}")
    if ndc != d["display_currency"]: d["display_currency"] = ndc; st.rerun()

    st.divider()
    st.subheader(t("fx_rates"))
    fx = d["fx_rates"]
    cb, cs = st.columns([1, 3])
    with cb:
        if st.button(t("fetch_fx"), type="primary"):
            live = _try_fetch_fx()
            if live: fx.update(live); st.session_state._fx_ok = True; st.rerun()
            else: st.session_state._fx_err = True
    with cs:
        if st.session_state.pop("_fx_ok", None):
            st.success(t("fx_updated"))
        if st.session_state.pop("_fx_err", None):
            st.error(t("fx_error"))
    c1, c2, c3 = st.columns(3)
    fx["USD"] = c1.number_input("AUD/USD", value=fx["USD"], step=0.0001, format="%.4f", key="fx_usd")
    fx["CNY"] = c2.number_input("AUD/CNY", value=fx["CNY"], step=0.0001, format="%.4f", key="fx_cny")
    fx["HKD"] = c3.number_input("AUD/HKD", value=fx["HKD"], step=0.0001, format="%.4f", key="fx_hkd")
    us_etf_usd = sum(s["value"] for s in d["super_fund"] if s["currency"]=="USD") + \
                 sum(o["value"] for o in d["other_assets"] if o["currency"]=="USD")
    us_etf_aud = us_etf_usd / fx["USD"] if fx["USD"] > 0 else 0
    cn_cost = d["retirement"].get("cn_cost", 12000)
    c1, c2, c3 = st.columns(3)
    c1.metric("AUD/USD", f"{fx['USD']:.4f}"); c2.metric("AUD/CNY", f"{fx['CNY']:.4f}")
    c3.metric(t("us_etf_aud"), fmt_cur(us_etf_aud, "AUD"), f"US${us_etf_usd:,.0f}")
    st.subheader(t("fx_scenario"))
    base_etf = us_etf_usd / fx["USD"] if fx["USD"] > 0 else 0
    cn_cny = cn_cost * fx["CNY"]
    rows = []
    for label, ur, cr in [(t("current"),fx["USD"],fx["CNY"]),
        (t("aud_strong"),0.75,5.20),(t("aud_weak"),0.58,4.20),(t("aud_very_weak"),0.50,3.60)]:
        ea = us_etf_usd/ur if ur>0 else 0
        ca = cn_cny/cr if cr>0 else 0
        ed, cd = ea-base_etf, ca-cn_cost
        rows.append({t("scenario"):label,"AUD/USD":f"{ur:.4f}","AUD/CNY":f"{cr:.4f}",
            t("us_etf_aud"):fmt_cur(ea,"AUD"),t("cn_cost_aud"):fmt_cur(ca,"AUD"),
            t("net_impact"): t("baseline_label") if label==t("current") else f"{'+' if ed-abs(cd)>=0 else ''}{fmt_cur(ed-abs(cd),'AUD')}"})
    st.dataframe(rows, width='stretch', hide_index=True)
    if us_etf_usd > 0:
        st.info(t("fx_hedge_tip"))

    st.divider()
    st.subheader(t("data_mgmt"))
    st.success(t("auto_save_on"))
    st.caption(t("persistence_note"))
    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button(t("export_data"), json.dumps(d, ensure_ascii=False, indent=2),
            "wealth_data.json", "application/json")
    with c2:
        up = st.file_uploader(t("import_data"), type=["json"], key="imp")
        if up:
            try:
                imported = json.load(up)
                st.session_state.data = imported
                st.session_state.lang = imported.get("lang", "zh")
                # Clear money_input widget cache so new values display correctly
                for k in list(st.session_state.keys()):
                    if k.startswith(("pv_","pm_","sv_","ov_","ia_","ea_","so_","mc_","r_","_data_")):
                        del st.session_state[k]
                save_data(); st.success(t("import_ok")); st.rerun()
            except Exception as e:
                st.error(f"{t('import_fail')}: {e}")
    with c3:
        if st.button(t("reset_data")):
            st.session_state.data = get_default_data()
            st.session_state.lang = "en"
            for k in list(st.session_state.keys()):
                if k.startswith(("pv_","pm_","sv_","ov_","ia_","ea_","so_","mc_","r_","_data_")):
                    del st.session_state[k]
            save_data(); st.rerun()

    # Git push
    st.divider()
    st.subheader(t("git_update"))
    st.caption(t("git_caption"))
    commit_msg = st.text_input("Commit message", value=f"Update {datetime.now().strftime('%Y-%m-%d %H:%M')}", key="git_msg")
    if st.button(t("git_update"), type="primary", key="git_btn"):
        try:
            r1 = subprocess.run(["git", "add", "-A"], capture_output=True, text=True, timeout=30)
            r2 = subprocess.run(["git", "commit", "-m", commit_msg], capture_output=True, text=True, timeout=30)
            r3 = subprocess.run(["git", "push"], capture_output=True, text=True, timeout=60)
            if r3.returncode == 0:
                st.success(t("git_push_ok"))
            else:
                st.error(f"{t('git_push_fail')}: {r3.stderr}")
                st.code(r1.stdout + r2.stdout + r3.stdout)
        except FileNotFoundError:
            st.error(t("git_no_git"))
        except Exception as e:
            st.error(f"{t('error_label')}: {e}")

    # Logout
    st.divider()
    if st.button(t("logout")):
        st.session_state.authenticated = False; st.rerun()

    st.divider()
    st.subheader(t("about"))
    st.caption(t("about_text"))


# ================================================================
# MAIN
# ================================================================
def main():
    if not check_password():
        return
    init_data()
    d = st.session_state.data
    with st.sidebar:
        st.title(t("login_title"))
        lang_opts = ["English", "中文"]
        lang_sel = st.selectbox("🌐", lang_opts, index=0 if st.session_state.lang == "en" else 1,
            key="sb_lang", label_visibility="collapsed")
        lc = "zh" if lang_sel == "中文" else "en"
        if lc != st.session_state.lang:
            st.session_state.lang = lc; d["lang"] = lc; st.rerun()
        st.divider()
        pages = {t("nav_dashboard"):"dashboard", t("nav_assets"):"assets", t("nav_cashflow"):"cashflow",
            t("nav_retirement"):"retirement", t("nav_super"):"super", t("nav_monte"):"monte",
            t("nav_settings"):"settings"}
        sel = st.radio("Nav", list(pages.keys()), label_visibility="collapsed")
        active = pages[sel]
        st.divider()
        st.caption("⚠️ " + t("not_financial_advice"))
        st.caption(t('auto_saved'))
        if st.session_state.get("_last_saved"):
            st.caption(f"✅ {st.session_state._last_saved}")
        if st.session_state.get("_save_error"):
            st.caption(f"❌ {st.session_state._save_error}")
    {"dashboard": page_dashboard, "assets": page_assets, "cashflow": page_cashflow,
     "retirement": page_retirement, "super": page_super, "monte": page_monte_carlo,
     "settings": page_settings}[active]()
    save_data()

if __name__ == "__main__":
    main()
