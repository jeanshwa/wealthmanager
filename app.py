import streamlit as st
import plotly.graph_objects as go
import numpy as np
import json, os, copy
from datetime import datetime

# ================================================================
# CONFIG
# ================================================================
st.set_page_config(page_title="Wealth Manager", page_icon="💰", layout="wide")
DATA_FILE = "wealth_data.json"
CURRENCIES = ["AUD", "USD", "CNY", "HKD"]
CUR_SYMBOLS = {"AUD": "A$", "USD": "US$", "CNY": "¥", "HKD": "HK$"}
CUR_FLAGS = {"AUD": "🇦🇺", "USD": "🇺🇸", "CNY": "🇨🇳", "HKD": "🇭🇰"}
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
    # Navigation
    "nav_dashboard": {"zh": "📊 总览", "en": "📊 Dashboard"},
    "nav_assets": {"zh": "🏠 资产管理", "en": "🏠 Assets"},
    "nav_cashflow": {"zh": "💰 现金流", "en": "💰 Cash Flow"},
    "nav_retirement": {"zh": "🎯 退休规划", "en": "🎯 Retirement"},
    "nav_super": {"zh": "📈 Super Fund 优化", "en": "📈 Super Fund"},
    "nav_monte": {"zh": "🎲 蒙特卡洛", "en": "🎲 Monte Carlo"},
    "nav_currency": {"zh": "💱 汇率分析", "en": "💱 Currency"},
    "nav_settings": {"zh": "⚙️ 设置", "en": "⚙️ Settings"},
    # Dashboard
    "net_worth": {"zh": "净资产总额", "en": "Net Worth"},
    "annual_cashflow": {"zh": "年净现金流", "en": "Annual Cash Flow"},
    "retirement_gap": {"zh": "退休缺口", "en": "Retirement Gap"},
    "retire_age": {"zh": "预计可退休年龄", "en": "Est. Retirement Age"},
    "asset_allocation": {"zh": "资产配置", "en": "Asset Allocation"},
    "net_worth_proj": {"zh": "净值增长趋势", "en": "Net Worth Projection"},
    "alerts": {"zh": "⚠️ 关键提醒", "en": "⚠️ Key Alerts"},
    # Assets
    "properties": {"zh": "🏠 房产", "en": "🏠 Properties"},
    "super_fund": {"zh": "📈 Super Fund", "en": "📈 Super Fund"},
    "cash_other": {"zh": "💵 现金 & 其他", "en": "💵 Cash & Other"},
    "name": {"zh": "名称", "en": "Name"},
    "market_value": {"zh": "当前市值", "en": "Market Value"},
    "mortgage": {"zh": "未偿贷款", "en": "Outstanding Mortgage"},
    "monthly_repay": {"zh": "每月还款", "en": "Monthly Repayment"},
    "add_property": {"zh": "＋ 添加房产", "en": "＋ Add Property"},
    "add_asset": {"zh": "＋ 添加资产", "en": "＋ Add Asset"},
    "remove": {"zh": "删除", "en": "Remove"},
    "total_assets": {"zh": "总资产", "en": "Total Assets"},
    "total_liabilities": {"zh": "总负债", "en": "Total Liabilities"},
    "display_cur": {"zh": "显示货币", "en": "Display Currency"},
    "auto_saved": {"zh": "💾 所有修改自动保存 · 刷新不丢失", "en": "💾 All changes auto-saved"},
    # Cash Flow
    "income": {"zh": "收入", "en": "Income"},
    "expenses": {"zh": "支出", "en": "Expenses"},
    "gross_income": {"zh": "税前收入 (合计)", "en": "Gross Income (Total)"},
    "after_tax": {"zh": "税后收入", "en": "After-tax Income"},
    "total_expenses": {"zh": "年支出", "en": "Annual Expenses"},
    "net_surplus": {"zh": "年净余", "en": "Annual Surplus"},
    "savings_rate": {"zh": "储蓄率", "en": "Savings Rate"},
    "waterfall": {"zh": "现金流瀑布图", "en": "Cash Flow Waterfall"},
    "amount_annual": {"zh": "年金额", "en": "Annual Amount"},
    # Retirement
    "current_age": {"zh": "当前年龄", "en": "Current Age"},
    "target_retire_age": {"zh": "目标退休年龄", "en": "Target Retirement Age"},
    "life_expectancy": {"zh": "预期寿命", "en": "Life Expectancy"},
    "months_au": {"zh": "澳洲居住 (月/年)", "en": "Months in Australia"},
    "months_cn": {"zh": "中国居住 (月/年)", "en": "Months in China"},
    "au_cost": {"zh": "澳洲期间年开支", "en": "Australia Annual Cost"},
    "cn_cost": {"zh": "中国期间年开支", "en": "China Annual Cost"},
    "biz_class_trips": {"zh": "商务舱往返/年", "en": "Business Class Trips/yr"},
    "ticket_price": {"zh": "人均往返票价", "en": "Ticket Price (per person RT)"},
    "health_ins": {"zh": "国际医疗险/年", "en": "Int'l Health Insurance/yr"},
    "real_return": {"zh": "预期实际回报率 %", "en": "Expected Real Return %"},
    "annual_contrib": {"zh": "年供款 (到退休)", "en": "Annual Contribution"},
    "projection": {"zh": "退休本金 Projection", "en": "Retirement Projection"},
    "sensitivity": {"zh": "敏感度分析", "en": "Sensitivity Analysis"},
    "scenario": {"zh": "情景", "en": "Scenario"},
    "capital_at_retire": {"zh": "退休时本金", "en": "Capital at Retirement"},
    "lasts_until": {"zh": "能撑到", "en": "Lasts Until"},
    "status": {"zh": "状态", "en": "Status"},
    "suggestion": {"zh": "💡 建议", "en": "💡 Suggestions"},
    "total_annual_expense": {"zh": "退休年开支合计", "en": "Total Retirement Expense"},
    "capital_needed_4pct": {"zh": "需要本金 (4%法则)", "en": "Capital Needed (4% Rule)"},
    # Super Fund
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
    "optimal_cc": {"zh": "今年最优供款", "en": "Optimal CC This Year"},
    "tax_saved": {"zh": "省税效果", "en": "Tax Saved"},
    "ncc": {"zh": "NCC (税后供款) 空间", "en": "NCC (After-tax) Room"},
    "ncc_annual": {"zh": "NCC 年限额", "en": "NCC Annual Cap"},
    "bring_forward": {"zh": "Bring-forward (3年)", "en": "Bring-forward (3yr)"},
    "eligible": {"zh": "是否可用", "en": "Eligible"},
    "div293": {"zh": "⚠️ Division 293 提醒", "en": "⚠️ Division 293 Alert"},
    # Monte Carlo
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
    "mc_conclusion": {"zh": "🎲 模拟结论", "en": "🎲 Simulation Conclusion"},
    # Currency
    "fx_rates": {"zh": "汇率设置 (每1 AUD兑)", "en": "FX Rates (per 1 AUD)"},
    "fx_sensitivity": {"zh": "汇率敏感度分析", "en": "FX Sensitivity Analysis"},
    "fx_scenario": {"zh": "情景分析", "en": "Scenario Analysis"},
    "fx_strategy": {"zh": "💱 货币策略提示", "en": "💱 Currency Strategy"},
    "current": {"zh": "当前", "en": "Current"},
    "aud_strong": {"zh": "AUD走强", "en": "AUD Strengthens"},
    "aud_weak": {"zh": "AUD走弱", "en": "AUD Weakens"},
    "aud_very_weak": {"zh": "极端弱AUD", "en": "Extreme Weak AUD"},
    "us_etf_aud": {"zh": "美股(AUD)", "en": "US ETF (AUD)"},
    "cn_cost_aud": {"zh": "中国年开支(AUD)", "en": "China Cost (AUD)"},
    "net_impact": {"zh": "净影响", "en": "Net Impact"},
    # Settings
    "language": {"zh": "界面语言", "en": "Language"},
    "display_currency_setting": {"zh": "汇总显示货币", "en": "Display Currency"},
    "data_mgmt": {"zh": "💾 数据管理", "en": "💾 Data Management"},
    "auto_save_on": {"zh": "✅ 自动保存已开启", "en": "✅ Auto-save Enabled"},
    "export_data": {"zh": "📥 导出备份", "en": "📥 Export Backup"},
    "import_data": {"zh": "📂 导入数据", "en": "📂 Import Data"},
    "reset_data": {"zh": "🗑️ 重置所有数据", "en": "🗑️ Reset All Data"},
    "about": {"zh": "关于", "en": "About"},
}

def t(key):
    lang = st.session_state.get("lang", "zh")
    entry = TR.get(key, {})
    return entry.get(lang, key)

# ================================================================
# DEFAULT DATA
# ================================================================
def get_default_data():
    return {
        "lang": "zh",
        "display_currency": "AUD",
        "fx_rates": {"USD": 0.645, "CNY": 4.72, "HKD": 5.04},
        "properties": [
            {"name": "自住房 — Sydney", "value": 0, "currency": "AUD", "mortgage": 0, "monthly_repay": 0},
            {"name": "自有住房 — 中国", "value": 0, "currency": "CNY", "mortgage": 0, "monthly_repay": 0},
        ],
        "super_fund": [
            {"name": "Office (商业物业)", "value": 0, "currency": "AUD"},
            {"name": "ETF (美股)", "value": 0, "currency": "USD"},
            {"name": "现金", "value": 0, "currency": "AUD"},
        ],
        "other_assets": [
            {"name": "澳洲银行存款", "value": 0, "currency": "AUD"},
            {"name": "中国银行存款", "value": 0, "currency": "CNY"},
            {"name": "香港账户", "value": 0, "currency": "HKD"},
            {"name": "个人 ETF (super外)", "value": 0, "currency": "USD"},
            {"name": "其他资产", "value": 0, "currency": "AUD"},
        ],
        "income": [
            {"name": "Practice 收入 (本人)", "amount": 0, "currency": "AUD"},
            {"name": "配偶工资", "amount": 0, "currency": "AUD"},
            {"name": "Office 租金 (Super Fund内)", "amount": 0, "currency": "AUD"},
        ],
        "expenses": [
            {"name": "🏠 房贷还款", "annual": 0},
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
            "au_cost": 46000, "cn_cost": 12000,
            "biz_class_trips": 3, "ticket_price": 4200,
            "health_ins": 4000, "real_return": 3.5,
            "annual_contrib": 60000, "current_super": 870000,
        },
        "super_opt": {
            "m1_name": "本人", "m2_name": "配偶",
            "m1_balance": 0, "m2_balance": 0,
            "m1_sg": 0, "m2_sg": 0,
            "m1_income": 0, "m2_income": 0,
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
    # Save to local JSON file
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
    # Save to browser localStorage for Cloud persistence
    try:
        from streamlit_js_eval import streamlit_js_eval
        js = json.dumps(d, ensure_ascii=False)
        streamlit_js_eval(js_expressions=f"localStorage.setItem('wealth_data', JSON.stringify({js}))", key=f"save_{datetime.now().timestamp()}")
    except Exception:
        pass

def load_data():
    # Try JSON file first
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
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

def init_data():
    if "data" not in st.session_state:
        loaded = load_data()
        if loaded is None:
            loaded = load_from_localstorage()
        if loaded is None:
            loaded = get_default_data()
        # Merge with defaults to handle new fields
        default = get_default_data()
        for k, v in default.items():
            if k not in loaded:
                loaded[k] = v
        st.session_state.data = loaded
    if "lang" not in st.session_state:
        st.session_state.lang = st.session_state.data.get("lang", "zh")
    # Auto-fetch live FX on first load
    if not st.session_state.get("_fx_auto_fetched"):
        live = fetch_live_fx()
        if live:
            st.session_state.data["fx_rates"].update(live)
        st.session_state._fx_auto_fetched = True

# ================================================================
# CURRENCY HELPERS
# ================================================================
def to_aud(amount, from_cur, fx):
    if from_cur == "AUD":
        return amount
    rate = fx.get(from_cur, 1)
    return amount / rate if rate else amount

def from_aud(amount, to_cur, fx):
    if to_cur == "AUD":
        return amount
    rate = fx.get(to_cur, 1)
    return amount * rate

def to_display(amount, from_cur, display_cur, fx):
    aud = to_aud(amount, from_cur, fx)
    return from_aud(aud, display_cur, fx)

def fmt_cur(amount, cur=None):
    if cur is None:
        cur = st.session_state.data.get("display_currency", "AUD")
    sym = CUR_SYMBOLS.get(cur, "$")
    if abs(amount) >= 1_000_000:
        return f"{sym}{amount/1_000_000:,.2f}M"
    return f"{sym}{amount:,.0f}"

# ================================================================
# FINANCIAL CALCULATIONS
# ================================================================
AU_TAX_BRACKETS_2526 = [
    (18200, 0), (45000, 0.16), (135000, 0.30), (190000, 0.37), (float("inf"), 0.45)
]

def au_income_tax(income):
    tax = 0
    prev = 0
    for threshold, rate in AU_TAX_BRACKETS_2526:
        taxable = min(income, threshold) - prev
        if taxable > 0:
            tax += taxable * rate
        prev = threshold
        if income <= threshold:
            break
    tax += income * 0.02  # Medicare levy
    return tax

def calc_net_worth(d):
    fx = d["fx_rates"]
    dc = d["display_currency"]
    total_assets = 0
    total_liabilities = 0
    breakdown = {}
    # Properties
    prop_val = sum(to_display(p["value"], p["currency"], dc, fx) for p in d["properties"])
    prop_mort = sum(to_display(p["mortgage"], p["currency"], dc, fx) for p in d["properties"])
    total_assets += prop_val
    total_liabilities += prop_mort
    breakdown["properties"] = prop_val - prop_mort
    # Super Fund
    sf_val = sum(to_display(s["value"], s["currency"], dc, fx) for s in d["super_fund"])
    total_assets += sf_val
    breakdown["super_fund"] = sf_val
    # Other
    other_val = sum(to_display(o["value"], o["currency"], dc, fx) for o in d["other_assets"])
    total_assets += other_val
    breakdown["other"] = other_val
    return total_assets, total_liabilities, total_assets - total_liabilities, breakdown

def calc_cashflow(d):
    fx = d["fx_rates"]
    gross = sum(to_aud(i["amount"], i["currency"], fx) for i in d["income"])
    # Simplified: treat first income as self, second as spouse
    incomes = d["income"]
    tax = 0
    for inc in incomes:
        aud_amt = to_aud(inc["amount"], inc["currency"], fx)
        if aud_amt > 0:
            tax += au_income_tax(aud_amt)
    after_tax = gross - tax
    total_exp = sum(e["annual"] for e in d["expenses"])
    surplus = after_tax - total_exp
    return gross, tax, after_tax, total_exp, surplus

def project_retirement(d):
    r = d["retirement"]
    years_to = r["target_age"] - r["current_age"]
    years_in = r["life_expectancy"] - r["target_age"]
    ret_return = r["real_return"] / 100
    # Annual retirement expense
    annual_exp = r["au_cost"] + r["cn_cost"] + r["biz_class_trips"] * r["ticket_price"] * 2 + r["health_ins"]
    # Accumulation
    bal = r["current_super"]
    acc = [bal]
    for _ in range(years_to):
        bal = bal * (1 + ret_return) + r["annual_contrib"]
        acc.append(bal)
    capital_at_retire = bal
    # Drawdown
    draw = [bal]
    deplete_age = None
    for y in range(years_in):
        bal = bal * (1 + ret_return) - annual_exp
        if bal <= 0 and deplete_age is None:
            deplete_age = r["target_age"] + y + 1
        bal = max(bal, 0)
        draw.append(bal)
    if deplete_age is None:
        deplete_age = r["life_expectancy"] + 10  # Beyond expectancy
    return acc, draw, capital_at_retire, annual_exp, deplete_age

def run_monte_carlo(params):
    np.random.seed(42)
    ic = params["initial_capital"]
    aw = params["annual_withdrawal"]
    yrs = params["years"]
    nr = params["nominal_return"] / 100
    vol = params["volatility"] / 100
    inf = params["inflation"] / 100
    n = params["num_sims"]
    real_r = (1 + nr) / (1 + inf) - 1
    returns = np.random.normal(real_r, vol, (n, yrs))
    balances = np.zeros((n, yrs + 1))
    balances[:, 0] = ic
    for y in range(yrs):
        balances[:, y + 1] = np.maximum(balances[:, y] * (1 + returns[:, y]) - aw, 0)
    success = np.mean(balances[:, -1] > 0)
    p10 = np.percentile(balances, 10, axis=0)
    p25 = np.percentile(balances, 25, axis=0)
    p50 = np.percentile(balances, 50, axis=0)
    p75 = np.percentile(balances, 75, axis=0)
    p90 = np.percentile(balances, 90, axis=0)
    return {"success": success, "p10": p10, "p25": p25, "p50": p50, "p75": p75, "p90": p90, "balances": balances}

def stress_test_sequence(params, crash_year, crash_pct=-0.35, recovery_years=3, cash_bucket=0):
    ic = params["initial_capital"] - cash_bucket
    aw = params["annual_withdrawal"]
    yrs = params["years"]
    real_r = ((1 + params["nominal_return"]/100) / (1 + params["inflation"]/100)) - 1
    bal = ic
    cash = cash_bucket
    for y in range(yrs):
        if y == crash_year:
            r = crash_pct
        elif crash_year < y <= crash_year + recovery_years:
            r = real_r * 1.3  # Recovery bounce
        else:
            r = real_r
        # Use cash bucket in crash years
        if y >= crash_year and y < crash_year + 2 and cash > 0:
            withdrawal = min(aw, cash)
            cash -= withdrawal
            remaining = aw - withdrawal
            bal = bal * (1 + r) - remaining
        else:
            bal = bal * (1 + r) - aw
        if bal <= 0:
            return params["initial_capital"], y + params.get("start_age", 60)
    return bal, params.get("start_age", 60) + yrs

# ================================================================
# PAGES
# ================================================================

def page_dashboard():
    d = st.session_state.data
    total_a, total_l, nw, breakdown = calc_net_worth(d)
    gross, tax, after_tax, total_exp, surplus = calc_cashflow(d)
    acc, draw, cap_retire, annual_exp_ret, deplete_age = project_retirement(d)
    dc = d["display_currency"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(t("net_worth"), fmt_cur(nw, dc))
    savings_pct = f"{surplus/after_tax*100:.0f}%" if after_tax > 0 else "—"
    c2.metric(t("annual_cashflow"), fmt_cur(surplus, dc), savings_pct)
    needed = annual_exp_ret * 25
    gap = cap_retire - needed
    c3.metric(t("retirement_gap"), fmt_cur(gap, dc), "✅" if gap >= 0 else "⚠️")
    c4.metric(t("retire_age"), f"{d['retirement']['target_age']}", "✅" if gap >= 0 else "需增加供款")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader(t("asset_allocation"))
        labels = [t("properties"), t("super_fund"), t("cash_other")]
        values = [max(breakdown.get("properties", 0), 0), max(breakdown.get("super_fund", 0), 0), max(breakdown.get("other", 0), 0)]
        if sum(values) > 0:
            fig = go.Figure(go.Pie(labels=labels, values=values, hole=0.55,
                marker=dict(colors=["#4da6ff", "#a371f7", "#d29922"]),
                textinfo="label+percent", textfont=dict(size=12)))
            fig.update_layout(**PLOTLY_LAYOUT, height=320, showlegend=False)
            fig.add_annotation(text=fmt_cur(nw, dc), x=0.5, y=0.5, font=dict(size=18, color="#e6edf3"), showarrow=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("请先在「资产管理」页录入数据" if st.session_state.lang == "zh" else "Please enter data in Assets page")

    with col2:
        st.subheader(t("net_worth_proj"))
        r = d["retirement"]
        ages_acc = list(range(r["current_age"], r["target_age"] + 1))
        ages_draw = list(range(r["target_age"], r["life_expectancy"] + 1))
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ages_acc, y=acc, mode="lines", name="累积" if st.session_state.lang == "zh" else "Accumulation",
            line=dict(color="#3fb950", width=2), fill="tozeroy", fillcolor="rgba(63,185,80,0.1)"))
        fig.add_trace(go.Scatter(x=ages_draw, y=draw, mode="lines", name="提取" if st.session_state.lang == "zh" else "Drawdown",
            line=dict(color="#f85149", width=2), fill="tozeroy", fillcolor="rgba(248,81,73,0.1)"))
        fig.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.3)")
        fig.update_layout(**PLOTLY_LAYOUT, height=320, xaxis_title="年龄" if st.session_state.lang == "zh" else "Age",
            yaxis_title=dc)
        st.plotly_chart(fig, use_container_width=True)

    # Alerts
    st.subheader(t("alerts"))
    sf_total = sum(to_aud(s["value"], s["currency"], d["fx_rates"]) for s in d["super_fund"])
    if sf_total > 0:
        max_item = max(d["super_fund"], key=lambda s: to_aud(s["value"], s["currency"], d["fx_rates"]))
        max_pct = to_aud(max_item["value"], max_item["currency"], d["fx_rates"]) / sf_total * 100
        if max_pct > 70:
            st.warning(f"Super Fund {max_pct:.0f}% 集中在 {max_item['name']} — 流动性风险高" if st.session_state.lang == "zh"
                else f"Super Fund {max_pct:.0f}% concentrated in {max_item['name']} — liquidity risk")
    if gap < 0:
        st.error(f"退休缺口 {fmt_cur(abs(gap), dc)}，需增加供款或调整退休计划" if st.session_state.lang == "zh"
            else f"Retirement gap {fmt_cur(abs(gap), dc)}, increase contributions or adjust plan")
    elif gap >= 0:
        st.success("退休目标可达 ✅" if st.session_state.lang == "zh" else "Retirement target achievable ✅")


def page_assets():
    d = st.session_state.data
    fx = d["fx_rates"]
    dc = d["display_currency"]

    # Properties
    st.subheader(t("properties"))
    props_to_remove = []
    for i, p in enumerate(d["properties"]):
        with st.expander(f"{p['name']}", expanded=True):
            c1, c2 = st.columns([3, 1])
            p["name"] = c1.text_input(t("name"), p["name"], key=f"pn_{i}")
            p["currency"] = c2.selectbox(f"{CUR_FLAGS.get(p['currency'],'')} " + ("货币" if st.session_state.lang == "zh" else "Currency"),
                CURRENCIES, index=CURRENCIES.index(p["currency"]), key=f"pc_{i}")
            c1, c2, c3 = st.columns(3)
            p["value"] = c1.number_input(t("market_value"), value=p["value"], step=10000, key=f"pv_{i}")
            p["mortgage"] = c2.number_input(t("mortgage"), value=p["mortgage"], step=10000, key=f"pm_{i}")
            p["monthly_repay"] = c3.number_input(t("monthly_repay"), value=p["monthly_repay"], step=100, key=f"pr_{i}")
            equity = p["value"] - p["mortgage"]
            st.caption(f"净值: {CUR_SYMBOLS[p['currency']]}{equity:,.0f} {p['currency']} → {fmt_cur(to_display(equity, p['currency'], dc, fx), dc)} {dc}")
            if st.button(t("remove"), key=f"prm_{i}"):
                props_to_remove.append(i)
    for i in sorted(props_to_remove, reverse=True):
        d["properties"].pop(i)
        st.rerun()
    if st.button(t("add_property")):
        d["properties"].append({"name": "新房产", "value": 0, "currency": "AUD", "mortgage": 0, "monthly_repay": 0})
        st.rerun()

    # Super Fund
    st.subheader(t("super_fund"))
    for i, s in enumerate(d["super_fund"]):
        c1, c2, c3 = st.columns([3, 2, 1])
        s["name"] = c1.text_input(t("name"), s["name"], key=f"sn_{i}")
        s["value"] = c2.number_input(t("market_value"), value=s["value"], step=5000, key=f"sv_{i}")
        s["currency"] = c3.selectbox(f"{CUR_FLAGS.get(s['currency'],'')}",
            CURRENCIES, index=CURRENCIES.index(s["currency"]), key=f"sc_{i}")
    sf_aud = sum(to_aud(s["value"], s["currency"], fx) for s in d["super_fund"])
    sf_disp = from_aud(sf_aud, dc, fx) if dc != "AUD" else sf_aud
    st.caption(f"Super Fund 总值: {fmt_cur(sf_disp, dc)}")
    if st.button("＋ 添加 Super Fund 项目"):
        d["super_fund"].append({"name": "新项目", "value": 0, "currency": "AUD"})
        st.rerun()

    # Other assets
    st.subheader(t("cash_other"))
    others_to_remove = []
    for i, o in enumerate(d["other_assets"]):
        c1, c2, c3, c4 = st.columns([3, 2, 1, 1])
        o["name"] = c1.text_input(t("name"), o["name"], key=f"on_{i}")
        o["value"] = c2.number_input(t("market_value"), value=o["value"], step=5000, key=f"ov_{i}")
        o["currency"] = c3.selectbox(f"{CUR_FLAGS.get(o['currency'],'')}",
            CURRENCIES, index=CURRENCIES.index(o["currency"]), key=f"oc_{i}")
        if c4.button("✕", key=f"orm_{i}"):
            others_to_remove.append(i)
    for i in sorted(others_to_remove, reverse=True):
        d["other_assets"].pop(i)
        st.rerun()
    if st.button(t("add_asset")):
        d["other_assets"].append({"name": "新资产", "value": 0, "currency": "AUD"})
        st.rerun()

    # Summary
    st.divider()
    total_a, total_l, nw, _ = calc_net_worth(d)
    # Display currency selector
    c1, c2 = st.columns([3, 1])
    with c2:
        new_dc = st.selectbox(t("display_cur"), CURRENCIES,
            index=CURRENCIES.index(dc), key="asset_dc",
            format_func=lambda x: f"{CUR_FLAGS[x]} {x}")
        if new_dc != dc:
            d["display_currency"] = new_dc
            st.rerun()
    with c1:
        fx_str = " · ".join([f"AUD/{k} {v}" for k, v in fx.items()])
        st.caption(f"汇率: {fx_str}")
        st.markdown(f"### {t('total_assets')} {fmt_cur(total_a, dc)} − {t('total_liabilities')} {fmt_cur(total_l, dc)} = **{fmt_cur(nw, dc)}**")
    st.success(t("auto_saved"))


def page_cashflow():
    d = st.session_state.data
    dc = d["display_currency"]
    fx = d["fx_rates"]

    # Income
    st.subheader(t("income"))
    inc_to_remove = []
    for i, inc in enumerate(d["income"]):
        c1, c2, c3, c4 = st.columns([3, 2, 1, 0.5])
        inc["name"] = c1.text_input(t("name"), inc["name"], key=f"in_{i}")
        inc["amount"] = c2.number_input(t("amount_annual"), value=inc["amount"], step=5000, key=f"ia_{i}")
        inc["currency"] = c3.selectbox(f"{CUR_FLAGS.get(inc['currency'],'')}",
            CURRENCIES, index=CURRENCIES.index(inc["currency"]), key=f"ic_{i}")
        if c4.button("✕", key=f"irm_{i}"):
            inc_to_remove.append(i)
    for i in sorted(inc_to_remove, reverse=True):
        d["income"].pop(i)
        st.rerun()
    if st.button("＋ 添加收入"):
        d["income"].append({"name": "新收入", "amount": 0, "currency": "AUD"})
        st.rerun()

    # Expenses
    st.subheader(t("expenses"))
    exp_to_remove = []
    for i, exp in enumerate(d["expenses"]):
        c1, c2, c3, c4 = st.columns([3, 2, 1, 0.5])
        exp["name"] = c1.text_input(t("name"), exp["name"], key=f"en_{i}")
        exp["annual"] = c2.number_input(t("amount_annual"), value=exp["annual"], step=1000, key=f"ea_{i}")
        c3.caption(f"月均 {CUR_SYMBOLS.get(dc, '$')}{exp['annual']/12:,.0f}")
        if c4.button("✕", key=f"erm_{i}"):
            exp_to_remove.append(i)
    for i in sorted(exp_to_remove, reverse=True):
        d["expenses"].pop(i)
        st.rerun()
    if st.button("＋ 添加支出"):
        d["expenses"].append({"name": "新支出", "annual": 0})
        st.rerun()

    # Summary
    st.divider()
    gross, tax, after_tax, total_exp, surplus = calc_cashflow(d)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(t("gross_income"), fmt_cur(gross, "AUD"))
    c2.metric(t("after_tax"), fmt_cur(after_tax, "AUD"), f"税 {fmt_cur(tax, 'AUD')}")
    c3.metric(t("total_expenses"), fmt_cur(total_exp, "AUD"))
    sr = f"{surplus/after_tax*100:.0f}%" if after_tax > 0 else "—"
    c4.metric(t("net_surplus"), fmt_cur(surplus, "AUD"), f"{t('savings_rate')} {sr}")

    # Waterfall chart
    st.subheader(t("waterfall"))
    labels = [t("gross_income"), "税/Tax"]
    values = [gross, -tax]
    for e in d["expenses"]:
        if e["annual"] > 0:
            labels.append(e["name"])
            values.append(-e["annual"])
    labels.append(t("net_surplus"))
    values.append(surplus)
    measures = ["relative"] * len(labels)
    measures[-1] = "total"
    measures[0] = "absolute"
    fig = go.Figure(go.Waterfall(
        x=labels, y=values, measure=measures,
        connector=dict(line=dict(color="rgba(255,255,255,0.1)")),
        increasing=dict(marker=dict(color="#3fb950")),
        decreasing=dict(marker=dict(color="#f85149")),
        totals=dict(marker=dict(color="#4da6ff")),
        textposition="outside", textfont=dict(size=10),
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def page_retirement():
    d = st.session_state.data
    r = d["retirement"]
    dc = d["display_currency"]

    c1, c2, c3, c4 = st.columns(4)
    r["current_age"] = c1.number_input(t("current_age"), value=r["current_age"], min_value=18, max_value=80, key="r_ca")
    r["target_age"] = c2.number_input(t("target_retire_age"), value=r["target_age"], min_value=40, max_value=80, key="r_ta")
    r["life_expectancy"] = c3.number_input(t("life_expectancy"), value=r["life_expectancy"], min_value=70, max_value=110, key="r_le")
    r["real_return"] = c4.number_input(t("real_return"), value=r["real_return"], step=0.5, format="%.1f", key="r_rr")

    st.subheader("🏠 " + ("生活方式设置" if st.session_state.lang == "zh" else "Lifestyle Settings"))
    c1, c2 = st.columns(2)
    with c1:
        r["months_au"] = st.number_input(t("months_au"), value=r["months_au"], min_value=0, max_value=12, key="r_mau")
        r["au_cost"] = st.number_input(t("au_cost"), value=r["au_cost"], step=1000, key="r_auc")
        r["biz_class_trips"] = st.number_input(t("biz_class_trips"), value=r["biz_class_trips"], min_value=0, max_value=12, key="r_bct")
    with c2:
        r["months_cn"] = st.number_input(t("months_cn"), value=r["months_cn"], min_value=0, max_value=12, key="r_mcn")
        r["cn_cost"] = st.number_input(t("cn_cost"), value=r["cn_cost"], step=1000, key="r_cnc")
        r["ticket_price"] = st.number_input(t("ticket_price"), value=r["ticket_price"], step=100, key="r_tp")

    c1, c2, c3 = st.columns(3)
    r["health_ins"] = c1.number_input(t("health_ins"), value=r["health_ins"], step=500, key="r_hi")
    r["annual_contrib"] = c2.number_input(t("annual_contrib"), value=r["annual_contrib"], step=5000, key="r_ac")
    r["current_super"] = c3.number_input("当前 Super Fund 总值" if st.session_state.lang == "zh" else "Current Super Fund Total",
        value=r["current_super"], step=10000, key="r_cs")

    # Calculate
    acc, draw, cap_retire, annual_exp, deplete_age = project_retirement(d)
    needed = annual_exp * 25

    # Metrics
    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(t("total_annual_expense"), fmt_cur(annual_exp, dc))
    c2.metric(t("capital_needed_4pct"), fmt_cur(needed, dc))
    c3.metric(t("capital_at_retire"), fmt_cur(cap_retire, dc))
    gap = cap_retire - needed
    c4.metric(t("retirement_gap"), fmt_cur(gap, dc), "✅ 超额" if gap >= 0 else "⚠️ 不足")

    # Projection chart
    st.subheader(t("projection"))
    ages_acc = list(range(r["current_age"], r["target_age"] + 1))
    ages_draw = list(range(r["target_age"], r["life_expectancy"] + 1))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ages_acc, y=acc, mode="lines+markers", name="累积阶段",
        line=dict(color="#3fb950", width=2.5), marker=dict(size=3)))
    fig.add_trace(go.Scatter(x=ages_draw, y=draw, mode="lines+markers", name="提取阶段",
        line=dict(color="#f85149", width=2.5), marker=dict(size=3)))
    fig.add_hline(y=needed, line_dash="dot", line_color="#4da6ff", annotation_text="4% 法则线")
    fig.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.3)")
    fig.update_layout(**PLOTLY_LAYOUT, height=400,
        xaxis_title="年龄", yaxis_title=f"本金 ({dc})")
    st.plotly_chart(fig, use_container_width=True)

    # Sensitivity
    st.subheader(t("sensitivity"))
    scenarios = []
    for label, ret in [("保守 2.5%", 2.5), ("基准 3.5%", 3.5), ("乐观 4.5%", 4.5)]:
        old_rr = r["real_return"]
        r["real_return"] = ret
        a, dr, cr, ae, da = project_retirement(d)
        r["real_return"] = old_rr
        lasts = f"{da}岁" if da <= r["life_expectancy"] else f">{r['life_expectancy']}岁"
        status = "✅" if da > r["life_expectancy"] else ("⚠️" if da > r["life_expectancy"] - 5 else "❌")
        scenarios.append({"情景": label, "退休时本金": fmt_cur(cr, dc), "能撑到": lasts, "状态": status})
    # Delayed retirement
    r_copy = copy.deepcopy(r)
    r_copy["target_age"] = r["target_age"] + 2
    d_copy = copy.deepcopy(d)
    d_copy["retirement"] = r_copy
    a2, dr2, cr2, ae2, da2 = project_retirement(d_copy)
    lasts2 = f"{da2}岁" if da2 <= r_copy["life_expectancy"] else f">{r_copy['life_expectancy']}岁"
    scenarios.append({"情景": f"推迟到{r['target_age']+2}岁退休", "退休时本金": fmt_cur(cr2, dc), "能撑到": lasts2, "状态": "✅" if da2 > r["life_expectancy"] else "⚠️"})
    st.dataframe(scenarios, use_container_width=True, hide_index=True)

    # Suggestion
    if gap >= 0:
        st.success(f"💡 基准情景下目标可达。商务舱预算 (~{fmt_cur(r['biz_class_trips']*r['ticket_price']*2, dc)}/年) 是天然安全阀，压力场景下可降级释放弹性。")
    else:
        extra = abs(gap) / max(r["target_age"] - r["current_age"], 1)
        st.warning(f"💡 需额外每年供款约 {fmt_cur(extra, dc)} 才能达到 4% 法则线，或推迟退休 2–3 年。")


def page_super():
    d = st.session_state.data
    so = d["super_opt"]

    st.subheader(t("sf_current"))
    sf_total = sum(to_aud(s["value"], s["currency"], d["fx_rates"]) for s in d["super_fund"])
    c1, c2, c3 = st.columns(3)
    c1.metric(t("sf_total"), fmt_cur(sf_total, "AUD"))
    if sf_total > 0:
        max_item = max(d["super_fund"], key=lambda s: to_aud(s["value"], s["currency"], d["fx_rates"]))
        max_pct = to_aud(max_item["value"], max_item["currency"], d["fx_rates"]) / sf_total * 100
        c2.metric(t("sf_concentration"), f"{max_pct:.0f}% ({max_item['name']})")
        liquid = sf_total - to_aud(max_item["value"], max_item["currency"], d["fx_rates"]) if max_pct > 50 else sf_total
        c3.metric(t("sf_liquid"), fmt_cur(liquid, "AUD"))

    st.subheader(t("concessional"))
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**{so['m1_name']}**")
        so["m1_balance"] = st.number_input(t("super_balance"), value=so["m1_balance"], step=10000, key="so_m1b")
        so["m1_sg"] = st.number_input(t("sg_received"), value=so["m1_sg"], step=1000, key="so_m1sg")
        so["m1_income"] = st.number_input(t("personal_income"), value=so["m1_income"], step=5000, key="so_m1i")
    with c2:
        st.markdown(f"**{so['m2_name']}**")
        so["m2_balance"] = st.number_input(t("super_balance"), value=so["m2_balance"], step=10000, key="so_m2b")
        so["m2_sg"] = st.number_input(t("sg_received"), value=so["m2_sg"], step=1000, key="so_m2sg")
        so["m2_income"] = st.number_input(t("personal_income"), value=so["m2_income"], step=5000, key="so_m2i")

    CC_CAP = 30000
    NCC_CAP = 120000
    NCC_BF = 360000

    st.divider()
    results = []
    for name, bal, sg, inc in [
        (so["m1_name"], so["m1_balance"], so["m1_sg"], so["m1_income"]),
        (so["m2_name"], so["m2_balance"], so["m2_sg"], so["m2_income"]),
    ]:
        room = max(CC_CAP - sg, 0)
        can_cf = bal < 500000
        cf_est = min(5 * CC_CAP - sg, 5 * CC_CAP) if can_cf else 0  # Simplified estimate
        optimal = room + (cf_est if can_cf else 0)
        marginal_rate = 0.45 if inc > 190000 else (0.37 if inc > 135000 else (0.30 if inc > 45000 else 0.16))
        tax_saving = optimal * (marginal_rate + 0.02 - 0.15)  # Marginal + Medicare - super tax
        div293 = inc + min(optimal, CC_CAP) > 250000
        results.append({
            t("member"): name,
            t("cc_cap"): f"${CC_CAP:,}",
            t("cc_used"): f"${sg:,.0f}",
            t("cc_room"): f"${room:,.0f}",
            t("carry_forward"): f"✅ ~${cf_est:,.0f}" if can_cf else "❌ >$500k",
            t("optimal_cc"): f"${optimal:,.0f}",
            t("tax_saved"): f"${tax_saving:,.0f}",
        })
    st.dataframe(results, use_container_width=True, hide_index=True)

    # NCC
    st.subheader(t("ncc"))
    ncc_results = []
    for name, bal in [(so["m1_name"], so["m1_balance"]), (so["m2_name"], so["m2_balance"])]:
        can_ncc = bal < 1900000
        ncc_results.append({
            t("member"): name,
            t("ncc_annual"): f"${NCC_CAP:,}",
            t("bring_forward"): f"${NCC_BF:,}",
            t("eligible"): "✅" if can_ncc else "❌ >$1.9M",
        })
    st.dataframe(ncc_results, use_container_width=True, hide_index=True)

    # Div 293 warning
    for name, inc, sg in [(so["m1_name"], so["m1_income"], so["m1_sg"]), (so["m2_name"], so["m2_income"], so["m2_sg"])]:
        threshold = inc + CC_CAP
        if threshold > 250000 and inc > 0:
            over = threshold - 250000
            st.warning(f"⚠️ {name}: 收入 ${inc:,.0f} + CC ${CC_CAP:,} = ${threshold:,.0f}（超 $250k 阈值 ${over:,.0f}）→ 触发 Division 293 额外 15% 税。"
                f"但总税率 30% 仍远低于边际税率。")
        elif inc > 0:
            buffer = 250000 - threshold
            st.info(f"ℹ️ {name}: 距 Division 293 阈值还有 ${buffer:,.0f} 空间。")


def page_monte_carlo():
    d = st.session_state.data
    mc = d["monte_carlo"]

    st.subheader(t("mc_params"))
    c1, c2, c3 = st.columns(3)
    mc["initial_capital"] = c1.number_input(t("initial_capital"), value=mc["initial_capital"], step=50000, key="mc_ic")
    mc["annual_withdrawal"] = c2.number_input(t("annual_withdrawal"), value=mc["annual_withdrawal"], step=5000, key="mc_aw")
    mc["years"] = c3.number_input(t("sim_years"), value=mc["years"], min_value=10, max_value=50, key="mc_yr")
    c1, c2, c3 = st.columns(3)
    mc["nominal_return"] = c1.number_input(t("nominal_return"), value=mc["nominal_return"], step=0.5, format="%.1f", key="mc_nr")
    mc["volatility"] = c2.number_input(t("volatility"), value=mc["volatility"], step=1.0, format="%.1f", key="mc_vol")
    mc["inflation"] = c3.number_input(t("inflation"), value=mc["inflation"], step=0.5, format="%.1f", key="mc_inf")
    mc["num_sims"] = st.slider(t("num_sims"), min_value=1000, max_value=20000, value=mc["num_sims"], step=1000, key="mc_ns")

    if st.button(t("run_sim"), type="primary"):
        with st.spinner("运行模拟中..." if st.session_state.lang == "zh" else "Running simulation..."):
            result = run_monte_carlo(mc)
            st.session_state.mc_result = result

    if "mc_result" in st.session_state:
        result = st.session_state.mc_result
        c1, c2, c3 = st.columns(3)
        sr = result["success"]
        c1.metric(t("success_rate"), f"{sr*100:.1f}%", "✅" if sr > 0.9 else ("⚠️" if sr > 0.8 else "❌"))
        c2.metric(t("median_end"), fmt_cur(result["p50"][-1], "AUD"))
        c3.metric(t("p10_end"), fmt_cur(result["p10"][-1], "AUD"))

        # Fan chart
        st.subheader(t("fan_chart"))
        years = list(range(mc["years"] + 1))
        fig = go.Figure()
        # P10-P90 band
        fig.add_trace(go.Scatter(x=years, y=result["p90"].tolist(), mode="lines", line=dict(width=0),
            showlegend=False, hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=years, y=result["p10"].tolist(), mode="lines", line=dict(width=0),
            fill="tonexty", fillcolor="rgba(163,113,247,0.15)", name="P10–P90"))
        # P25-P75 band
        fig.add_trace(go.Scatter(x=years, y=result["p75"].tolist(), mode="lines", line=dict(width=0),
            showlegend=False, hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=years, y=result["p25"].tolist(), mode="lines", line=dict(width=0),
            fill="tonexty", fillcolor="rgba(77,166,255,0.2)", name="P25–P75"))
        # Median
        fig.add_trace(go.Scatter(x=years, y=result["p50"].tolist(), mode="lines",
            line=dict(color="#4da6ff", width=2.5), name="P50 (中位)"))
        fig.add_hline(y=0, line_dash="dash", line_color="rgba(248,81,73,0.5)")
        fig.update_layout(**PLOTLY_LAYOUT, height=400,
            xaxis_title="退休后年数" if st.session_state.lang == "zh" else "Years After Retirement",
            yaxis_title="AUD")
        st.plotly_chart(fig, use_container_width=True)

        # Stress test
        st.subheader(t("stress_test"))
        start_age = d["retirement"].get("target_age", 60)
        mc_with_age = {**mc, "start_age": start_age}
        stress_rows = []
        for label, cy, cash in [
            ("无崩盘 (基准)", None, 0),
            ("退休第1年崩盘", 0, 0),
            ("退休第5年崩盘", 4, 0),
            ("退休第10年崩盘", 9, 0),
            (f"第1年崩盘+现金桶(${mc['annual_withdrawal']*2:,.0f})", 0, mc["annual_withdrawal"] * 2),
        ]:
            if cy is None:
                real_r = ((1+mc["nominal_return"]/100)/(1+mc["inflation"]/100))-1
                bal = mc["initial_capital"]
                for y in range(mc["years"]):
                    bal = bal * (1+real_r) - mc["annual_withdrawal"]
                    if bal <= 0:
                        stress_rows.append({t("scenario"): label, t("crash_year"): "—", t("crash_size"): "—",
                            t("recovery"): "—", t("lasts_until"): f"{start_age+y+1}岁", t("status"): "⚠️"})
                        break
                else:
                    stress_rows.append({t("scenario"): label, t("crash_year"): "—", t("crash_size"): "—",
                        t("recovery"): "—", t("lasts_until"): f">{start_age+mc['years']}岁", t("status"): "✅"})
            else:
                end_bal, end_age = stress_test_sequence(mc_with_age, cy, cash_bucket=cash)
                age_str = f"{end_age}岁" if end_bal <= 0 else f">{start_age+mc['years']}岁"
                status = "✅" if end_bal > 0 else ("⚠️" if end_age > start_age + mc["years"] - 5 else "❌")
                crash_label = f"{start_age+cy}岁" if st.session_state.lang == "zh" else f"Age {start_age+cy}"
                stress_rows.append({t("scenario"): label, t("crash_year"): crash_label,
                    t("crash_size"): "-35%", t("recovery"): "3年", t("lasts_until"): age_str, t("status"): status})
        st.dataframe(stress_rows, use_container_width=True, hide_index=True)

        # Conclusion
        if sr >= 0.9:
            st.success(f"🎲 {sr*100:.0f}% 成功率，目标可达。建议保留 2 年开支现金桶 ({fmt_cur(mc['annual_withdrawal']*2, 'AUD')}) 应对 sequence risk。")
        elif sr >= 0.8:
            st.warning(f"🎲 {sr*100:.0f}% 成功率，略有风险。可降低提取额或增加初始本金 10-15% 以提升至 90%+。")
        else:
            st.error(f"🎲 {sr*100:.0f}% 成功率偏低。建议：①降提取 ②增本金 ③推迟退休。")


@st.cache_data(ttl=3600, show_spinner=False)
def _fetch_fx_cached():
    """Fetch live FX rates, cached for 1 hour"""
    try:
        import yfinance as yf
        tickers = {"USD": "AUDUSD=X", "CNY": "AUDCNY=X", "HKD": "AUDHKD=X"}
        result = {}
        data = yf.download(list(tickers.values()), period="1d", progress=False)
        for cur, ticker in tickers.items():
            try:
                price = float(data["Close"][ticker].dropna().iloc[-1])
                result[cur] = round(price, 6)
            except Exception:
                pass
        return result if result else None
    except Exception:
        return None


def fetch_live_fx():
    """Fetch live exchange rates from Yahoo Finance"""
    return _fetch_fx_cached()


def page_currency():
    d = st.session_state.data
    fx = d["fx_rates"]

    st.subheader(t("fx_rates"))

    # Fetch live rates button
    c_btn, c_status = st.columns([1, 3])
    with c_btn:
        if st.button("🔄 " + ("获取实时汇率" if st.session_state.lang == "zh" else "Fetch Live Rates"), type="primary"):
            live = fetch_live_fx()
            if live:
                fx["USD"] = live["USD"]
                fx["CNY"] = live["CNY"]
                fx["HKD"] = live["HKD"]
                st.session_state._fx_updated = True
                st.rerun()
            else:
                st.session_state._fx_error = True
    with c_status:
        if st.session_state.get("_fx_updated"):
            st.success("✅ " + ("汇率已更新（来源: Yahoo Finance 实时数据）" if st.session_state.lang == "zh" else "Rates updated (source: Yahoo Finance)"))
            del st.session_state._fx_updated
        if st.session_state.get("_fx_error"):
            st.error("❌ " + ("获取失败，请检查网络或手动输入" if st.session_state.lang == "zh" else "Fetch failed, check network or enter manually"))
            del st.session_state._fx_error
    c1, c2, c3 = st.columns(3)
    fx["USD"] = c1.number_input("AUD/USD", value=fx["USD"], step=0.005, format="%.4f", key="fx_usd")
    fx["CNY"] = c2.number_input("AUD/CNY", value=fx["CNY"], step=0.01, format="%.2f", key="fx_cny")
    fx["HKD"] = c3.number_input("AUD/HKD", value=fx["HKD"], step=0.01, format="%.2f", key="fx_hkd")

    # Get US ETF value
    us_etf_usd = sum(s["value"] for s in d["super_fund"] if s["currency"] == "USD")
    us_etf_usd += sum(o["value"] for o in d["other_assets"] if o["currency"] == "USD")
    us_etf_aud = us_etf_usd / fx["USD"] if fx["USD"] > 0 else 0

    # China cost
    cn_cost = d["retirement"].get("cn_cost", 12000)

    c1, c2, c3 = st.columns(3)
    c1.metric("AUD/USD", f"{fx['USD']:.4f}")
    c2.metric("AUD/CNY", f"{fx['CNY']:.2f}")
    c3.metric(t("us_etf_aud"), fmt_cur(us_etf_aud, "AUD"), f"US${us_etf_usd:,.0f}")

    # Scenario analysis
    st.subheader(t("fx_scenario"))
    scenarios_fx = [
        (t("current"), fx["USD"], fx["CNY"]),
        (t("aud_strong"), 0.75, 5.20),
        (t("aud_weak"), 0.58, 4.20),
        (t("aud_very_weak"), 0.50, 3.60),
    ]
    rows = []
    base_etf_aud = us_etf_usd / fx["USD"] if fx["USD"] > 0 else 0
    base_cn_aud = cn_cost
    for label, usd_rate, cny_rate in scenarios_fx:
        etf_aud = us_etf_usd / usd_rate if usd_rate > 0 else 0
        # China cost in AUD: fixed CNY amount / CNY rate
        cn_cny = cn_cost * fx["CNY"]  # Convert base AUD cost to CNY at current rate
        cn_aud_new = cn_cny / cny_rate if cny_rate > 0 else 0
        etf_diff = etf_aud - base_etf_aud
        cn_diff = cn_aud_new - base_cn_aud
        rows.append({
            t("scenario"): label,
            "AUD/USD": f"{usd_rate:.3f}",
            "AUD/CNY": f"{cny_rate:.2f}",
            t("us_etf_aud"): fmt_cur(etf_aud, "AUD"),
            t("cn_cost_aud"): fmt_cur(cn_aud_new, "AUD"),
            t("net_impact"): f"{'+' if etf_diff+cn_diff >= 0 else ''}{fmt_cur(etf_diff - abs(cn_diff), 'AUD')}" if label != t("current") else "基准",
        })
    st.dataframe(rows, use_container_width=True, hide_index=True)

    # Strategy
    if us_etf_usd > 0:
        st.info("💱 " + (
            f"你有天然对冲：AUD贬 → 美股换回AUD更多（利好 +），但中国开支换算更贵（利空 −）。"
            f"净敞口偏「喜欢弱AUD」（因为美股 {fmt_cur(us_etf_usd, 'USD')} 远大于中国年开支）。"
            f"持有美元资产本身就是对澳元的分散，无需额外做 FX 对冲。"
            if st.session_state.lang == "zh" else
            f"Natural hedge: weak AUD boosts US ETF value but increases China costs. "
            f"Net exposure favours weak AUD (US assets >> China costs). No extra FX hedge needed."
        ))


def page_settings():
    d = st.session_state.data

    st.subheader(t("language"))
    lang_options = {"中文": "zh", "English": "en"}
    current_label = "中文" if d["lang"] == "zh" else "English"
    new_lang_label = st.selectbox(t("language"), list(lang_options.keys()),
        index=list(lang_options.values()).index(d["lang"]), key="set_lang")
    new_lang = lang_options[new_lang_label]
    if new_lang != d["lang"]:
        d["lang"] = new_lang
        st.session_state.lang = new_lang
        st.rerun()

    st.subheader(t("display_currency_setting"))
    new_dc = st.selectbox(t("display_currency_setting"), CURRENCIES,
        index=CURRENCIES.index(d["display_currency"]), key="set_dc",
        format_func=lambda x: f"{CUR_FLAGS[x]} {x}")
    if new_dc != d["display_currency"]:
        d["display_currency"] = new_dc
        st.rerun()

    st.divider()
    st.subheader(t("data_mgmt"))
    st.success(t("auto_save_on"))
    st.caption(
        "🖥️ 本地运行：自动写入 wealth_data.json\n\n"
        "☁️ Streamlit Cloud：自动存入浏览器 localStorage，刷新不丢失。跨设备请用导出→导入"
        if st.session_state.lang == "zh" else
        "🖥️ Local: auto-saves to wealth_data.json\n\n"
        "☁️ Cloud: auto-saves to browser localStorage, persists on refresh. Use export/import across devices"
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        json_str = json.dumps(d, ensure_ascii=False, indent=2)
        st.download_button(t("export_data"), json_str, "wealth_data.json", "application/json")
    with c2:
        uploaded = st.file_uploader(t("import_data"), type=["json"], key="import_file")
        if uploaded:
            try:
                imported = json.load(uploaded)
                st.session_state.data = imported
                st.session_state.lang = imported.get("lang", "zh")
                save_data()
                st.success("导入成功！" if st.session_state.lang == "zh" else "Import successful!")
                st.rerun()
            except Exception as e:
                st.error(f"导入失败: {e}")
    with c3:
        if st.button(t("reset_data")):
            st.session_state.data = get_default_data()
            st.session_state.lang = "zh"
            save_data()
            st.rerun()

    st.divider()
    st.subheader(t("about"))
    st.caption(
        "Wealth Manager v1.0 · 仅供个人财务规划参考，不构成理财或税务建议。\n\n"
        "Built with Streamlit + Plotly · 数据存储在本地，不上传任何服务器。\n\n"
        "澳洲税率/Super 规则基于 2025-26 财年。"
        if st.session_state.lang == "zh" else
        "Wealth Manager v1.0 · For personal planning only, not financial advice.\n\n"
        "Built with Streamlit + Plotly · Data stored locally, never uploaded.\n\n"
        "AU tax/super rules based on FY2025-26."
    )


# ================================================================
# MAIN
# ================================================================
def main():
    init_data()
    d = st.session_state.data

    # Sidebar
    with st.sidebar:
        st.title("💰 Wealth Manager" if st.session_state.lang == "en" else "💰 个人资产管理")

        # Language quick-switch
        lang_opts = ["中文", "English"]
        lang_idx = 0 if st.session_state.lang == "zh" else 1
        new_lang_sel = st.selectbox("🌐", lang_opts, index=lang_idx, key="sidebar_lang", label_visibility="collapsed")
        new_lang_code = "zh" if new_lang_sel == "中文" else "en"
        if new_lang_code != st.session_state.lang:
            st.session_state.lang = new_lang_code
            d["lang"] = new_lang_code
            st.rerun()

        st.divider()
        pages = {
            t("nav_dashboard"): "dashboard",
            t("nav_assets"): "assets",
            t("nav_cashflow"): "cashflow",
            t("nav_retirement"): "retirement",
            t("nav_super"): "super",
            t("nav_monte"): "monte",
            t("nav_currency"): "currency",
            t("nav_settings"): "settings",
        }
        selection = st.radio("Navigation", list(pages.keys()), label_visibility="collapsed")
        active = pages[selection]

        st.divider()
        st.caption("⚠️ " + ("仅供参考，不构成理财建议" if st.session_state.lang == "zh" else "Not financial advice"))
        st.caption(f"💾 {t('auto_saved')}")

    # Page routing
    if active == "dashboard":
        page_dashboard()
    elif active == "assets":
        page_assets()
    elif active == "cashflow":
        page_cashflow()
    elif active == "retirement":
        page_retirement()
    elif active == "super":
        page_super()
    elif active == "monte":
        page_monte_carlo()
    elif active == "currency":
        page_currency()
    elif active == "settings":
        page_settings()

    # Auto-save on every run
    save_data()


if __name__ == "__main__":
    main()
