import streamlit as st
import datetime
import streamlit.components.v1 as components
import json

# ================= 📦 联赛专属修正模块库 =================
MODULES = {
    "英超": "⑤ 英超专属修正：高密度赛程疲劳系数(12-1月/欧战周后跑动↓15%，末段失球率↑) + VAR介入倾向(点球/红牌复核率↑，临场让球盘需预留0.25波动空间) + 定位球预期进球权重(xG Set-Piece占比常超25%，修正定位球强队胜率+3-5%) + 主场优势衰减校正(近年平局率微升，主胜隐含概率需-2%)",
    "西甲": "⑤ 西甲专属修正：战术犯规/控球节奏修正(控球>60%球队末段体能分配更谨慎，平局概率+3%) + 裁判尺度松紧(技术流联赛出牌偏少，但关键战尺度收紧，影响大小球) + 高温/雨战对传控渗透率衰减(气温>28℃或大雨时，技术流球队xG预期下调0.15-0.2)",
    "意甲": "⑤ 意甲专属修正：防守体系权重(三中卫/五后卫体系对边路传中封堵率↑，修正客队预期进球-0.2) + 冬歇期后状态波动(1月重启后前3场跑动距离与战术执行力需额外验证，平局权重+4%) + 低比分倾向(联赛均值进球<2.6，大小球盘口需防1-0/0-0，客胜概率下调2-3%)",
    "德甲": "⑤ 德甲专属修正：高位逼抢转换效率(PPDA<8球队反击xG↑，但体能消耗大，60分钟后易崩盘，主胜概率+4%但需防逆转) + 冬季低温/积雪对长传精度影响(气温<0℃时，技术流球队失误率↑，xG下调0.1) + 球迷氛围加成(主场胜率溢价约+5-8%，需在赔率隐含概率中剔除)",
    "法甲": "⑤ 法甲专属修正：实力断层战意校正(非欧战区球队遇豪门常摆大巴，xGA修正↑，客胜概率需压降) + 青年军/老将体能负荷(21岁以下首发>4人时，末段防守专注度↓，大球概率+5%) + 跨区旅行距离衰减(客场飞行>1.5h需降权跑动效率，客胜-3%)",
    "杯赛": "⑤ 杯赛专属修正：轮换深度权重(主力休战比例>30%时，替补xG/xGA需重估，让球盘虚高需退0.25) + 淘汰赛规则映射(加时/点球概率计入平局修正，90分钟内保守倾向↑，平局+6-8%) + 冷门爆发系数(低级别球队战意溢价+10-15%，主/中立场需区分)",
    "日职联": "⑤ 日职专属修正：高温高湿衰减(6-9月气温>30℃+湿度>80%时，跑动距离↓12%，末段失球率↑，大球概率需压降) + 裁判严尺(出牌率联赛前列，影响让球盘稳定性，平局+3%) + 多线作战轮换(天皇杯/亚冠交叉期轮换率>40%，阵容深度权重翻倍)",
    "韩K联": "⑤ 韩K专属修正：极端气候修正(冬战<5℃/夏战>32℃对技术流影响显著，进球预期±0.15) + 军籍球员体能/状态波动(服役期归队球员需单独验证出场时长，缺阵时防守权重-5%) + 季后赛/保级战意放大(分组后战意权重翻倍，平局防冷+4%)",
    "瑞典超": "⑤ 瑞典超专属修正：人工草皮适应性(超60%球队主场为人工草，客队技术流需降权xG 0.15-0.2) + 跨纬度旅行/气候突变(南北跨度大，客场温差>10℃时状态波动↑，客胜-4%) + 阵容深度有限(伤缺1-2核心即导致xG/xGA断崖式下跌，伤停验证权重翻倍)"
}

# ================= 🏆 球队字典 =================
TEAM_DICT = {
    "英超": ["阿森纳", "阿斯顿维拉", "伯恩茅斯", "布伦特福德", "布莱顿", "切尔西", "水晶宫", "埃弗顿", "富勒姆", "伊普斯维奇", "莱斯特城", "利物浦", "曼城", "曼联", "纽卡斯尔联", "诺丁汉森林", "南安普顿", "托特纳姆热刺", "西汉姆联", "狼队"],
    "西甲": ["阿拉维斯", "阿尔梅里亚", "巴塞罗那", "皇家贝蒂斯", "塞尔塔", "加的斯", "赫塔菲", "赫罗纳", "拉斯帕尔马斯", "马德里竞技", "马略卡", "奥萨苏纳", "皇家马德里", "塞维利亚", "瓦伦西亚", "比利亚雷亚尔", "皇家社会", "毕尔巴鄂竞技", "巴列卡诺", "格拉纳达"],
    "意甲": ["亚特兰大", "博洛尼亚", "卡利亚里", "恩波利", "佛罗伦萨", "弗罗西诺内", "热那亚", "国际米兰", "尤文图斯", "拉齐奥", "莱切", "AC米兰", "蒙扎", "那不勒斯", "罗马", "萨勒尼塔纳", "萨索洛", "都灵", "乌迪内斯", "维罗纳"],
    "德甲": ["奥格斯堡", "柏林联合", "波鸿", "多特蒙德", "法兰克福", "弗赖堡", "海登海姆", "柏林赫塔", "霍芬海姆", "科隆", "莱比锡红牛", "勒沃库森", "美因茨", "门兴格拉德巴赫", "拜仁慕尼黑", "斯图加特", "沃尔夫斯堡", "云达不莱梅"],
    "法甲": ["昂热", "布雷斯特", "克莱蒙", "勒阿弗尔", "朗斯", "里尔", "洛里昂", "里昂", "马赛", "梅斯", "摩纳哥", "蒙彼利埃", "南特", "尼斯", "巴黎圣日耳曼", "兰斯", "雷恩", "斯特拉斯堡", "图卢兹"],
    "杯赛": ["常规杯赛"],
    "日职联": ["浦和红钻", "横滨水手", "神户胜利船", "川崎前锋", "名古屋鲸八", "大阪钢巴", "广岛三箭", "FC东京", "柏太阳神", "鹿岛鹿角", "札幌冈萨多", "湘南比马", "新泻天鹅", "町田泽维亚", "福冈黄蜂", "京都不死鸟", "大阪樱花", "鸟栖沙岩"],
    "韩K联": ["蔚山HD", "浦项制铁", "全北现代", "大邱FC", "仁川联合", "济州联合", "水原FC", "光州FC", "大田韩亚市民", "江原FC", "首尔FC", "金泉尚武"],
    "瑞典超": ["马尔默", "佐加顿斯", "赫根", "北雪平", "哥德堡", "尤尔加登", "天狼星", "卡尔马", "哈马比", "布罗马波卡纳", "埃尔夫斯堡", "瓦斯特拉斯", "米亚尔比", "代格福什", "瓦尔贝里"]
}

# ================= 📜 核心提示词模板（千问3.5优化版） =================
BASE_PROMPT = """# 🎯 角色与任务
你是足球量化分析师与临场盘口解码专家。当前距比赛开球仅剩{minutes}分钟。你的任务：仅基于【赛前{time_window}分钟内更新且双源验证】的实况数据，剥离市场噪音，识别机构真实意图，推导胜平负概率与最可能比分，并输出可追溯的逻辑链与【基于 EV 模型的投注价值评估】。

# 🔒 【核心数据源铁律】（最高优先级，违反将导致推演失效）
1. 📸 图片绝对主导：本场所有盘口（亚盘/大小球）与赔率（欧赔）的初盘、临场盘、水位变化、时间戳等核心分析数据，【必须且只能】以我上传的截图内容为准进行解析与推演。
2. 🌐 检索仅限辅助：AI自行联网检索或内置知识库中的历史盘口、第三方平台数据，【严禁作为主要分析依据】，仅可作为宏观背景参考或逻辑校验辅助。
3. ⚖️ 冲突处理原则：若AI检索/记忆数据与用户截图数据存在任何差异，【无条件以截图数据为准】，并在输出首行明确标注“🔒 盘口分析已严格锁定用户截图数据源，外部信息仅作辅助参考”。

# 📥 数据时效与来源校验（必须首先执行）
- 赛事：{league} | {home} vs {away}
- 开球：{kickoff}（当前：{current} | 距开球：{minutes}分钟 | 动态分析窗口：{time_window}分钟）
1. 时间窗过滤：仅采纳【开球前{time_window}分钟内】更新的数据。超期数据标注“⚠️ 时效降级”，权重降 30%。
2. 机构特性锚定：
- 欧赔锚点：威廉希尔（保守型，反映机构底线与风控阈值）
- 亚盘/大小球锚点：皇冠（敏感型，反映临场资金真实流向）
{module}

# 📸 待解析数据源（严格以此为准）
🇬🇧 欧赔（威廉希尔）：{euro_img_info} | 文本备用：{euro_txt}
⚽ 亚盘（皇冠）：{asian_img_info} | 文本备用：{asian_txt}
🎯 大小球（皇冠）：{ou_img_info} | 文本备用：{ou_txt}

# 🧠 核心推演链路（严格按序执行）
## ① 市场信号解码（权重 40%）
- 资金意图矩阵：
• 升盘 + 降水 / 降盘 + 升水 → 机构真实倾向（资金与赔率同向）
• 升盘 + 升水 / 降盘 + 降水 → 诱盘/阻盘嫌疑（资金与赔率逆向）
- 威廉希尔欧赔换算亚盘 vs 皇冠实际亚盘偏差>0.05 → 存在套利/风控空间，标记"⚠️ 定价错位"
- 输出：明确标注【市场共识方向】、【异动类型】、【机构真实意图评估】。

## ② 基本面与战术校准（权重 40%，必须输出量化校准表）
按以下维度逐项评分并加权，禁止笼统描述。若某项实时数据缺失，采用“保守降级策略”（按联赛近10场平均基准-10%处理），严禁虚构精确数值。
【A】阵容完整性与轮换系数 (15%)
- 核心伤缺/停赛：每缺席1名主力(xG/xGA贡献>15%)，对应端战力-5%~8%
- 赛程疲劳：休息<72小时或3战10天内，跑动/冲刺数据预期-12%；跨洲飞行>800km，客场战力-4%
- 新援/磨合期：首秀或出场<3场，战术执行效率×0.85
【B】战术相性与风格克制 (15%)
- 阵型对抗：高位逼抢(PPDA<8) vs 后场出球 → 逼抢方预期xG+0.25；低位防反(5后卫) vs 传控(控球>60%) → 防反方反击xG/90 +0.15
- 定位球权重：角球/任意球转化率>12%的球队，对阵防空弱队时胜平概率+3%~5%
- 风格容错：技术流客场遇强硬对抗联赛，连续传球成功率预期-8%
【C】战意与赛程优先级 (10%)
- 明确分级：争冠/保级(战意×1.2) > 中游无欲无求(×0.8) > 杯赛轮换期(×0.6)
- 结合{module}中的联赛特定修正（如杯赛战意方差、多线作战轮换率等）进行二次校准。
【D】环境与场地变量 (动态叠加)
- 人工草/雨战/高温：直接套用{module}中对应气候/草皮衰减系数
- 裁判尺度：红黄牌高发联赛，技术流球队犯规成本↑，大球概率需下调
📊 输出要求：生成【基本面校准矩阵】，列出每项调整后的预期进球差(ΔxG_adj)与胜率修正值。计算公式：P_基本面 = 基准胜率(50%) × [1 + Σ(各维度修正系数)]。所有系数必须标注来源依据或“⚠️ 保守估算”。

## ③ 概率融合与归一化（权重 20%）
- 融合公式：P_终 = P_市场 (40%) + P_基本面 (40%) + P_临场修正 (20%)
- 强制归一化：P(主)+P(平)+P(客) ≡ 100.0%。禁止四舍五入误差累积。
# 📤 最终输出格式（严格遵循）
📊 盘口交叉验证：
- 威廉希尔欧赔：[主 X.XX/平 X.XX/客 X.XX] (无抽水换算：主 XX%/平 XX%/客 XX%)
- 皇冠亚盘：[初盘→临场] (水位变动: XX%| 意图：诱/阻/中性| 资金流向：上盘/下盘/平衡)
- 皇冠大小球：[盘口@水位] (映射总进球期望：X.X-X.X 球)
- 分歧诊断：[若有，说明机构风控意图或信息差]
⚽ 推荐比分（Top3）：
1. [X-Y] ([XX.X]%)| 逻辑：[ΔxG 锚定+BTTS 过滤 + 盘口映射]
2. [X-Y] ([XX.X]%)| 逻辑：[...]
3. [X-Y] ([XX.X]%)| 逻辑：[...]
🛡️ 风险拦截与 EV 评估：[列出可能推翻结论的临场变量，说明置信度定级依据；标注✅EV+或⚠️EV-]
"""
# ================= 🖥️ Streamlit 应用逻辑 =================
def main():
    st.set_page_config(page_title="⚽ 足球临场盘口AI推演", page_icon="📊", layout="wide")
    st.title("⚽ 足球临场盘口AI推演系统 (Qwen-3.5 优化版)")
    st.caption("📸 已升级图像输入：支持上传皇冠/威廉希尔盘口截图。AI将自动提取初临盘位移轨迹，解码资金意图，提升预测贴近度。")

    # 1. 基础信息输入
    col1, col2 = st.columns(2)
    with col1:
        league = st.selectbox("🏆 选择联赛/杯赛", list(MODULES.keys()), index=0)
        team_list = TEAM_DICT.get(league, [])
        home_options = ["-- 手动输入 --"] + team_list
        home_select = st.selectbox("🏠 选择主队", home_options, key="home_sel")
        home = st.text_input("主队名称 (若未选)", placeholder="如：阿森纳", key="home_txt") if home_select == "-- 手动输入 --" else home_select
        
    with col2:
        away_options = ["-- 手动输入 --"] + team_list
        away_select = st.selectbox("✈️ 选择客队", away_options, key="away_sel")
        away = st.text_input("客队名称 (若未选)", placeholder="如：切尔西", key="away_txt") if away_select == "-- 手动输入 --" else away_select

    # 开球时间 (兼容所有Streamlit版本)
    col_date, col_time = st.columns(2)
    with col_date:
        kickoff_date = st.date_input("📅 比赛日期", value=datetime.date.today())
    with col_time:
        kickoff_time = st.time_input("⏰ 比赛时间", value=datetime.time(20, 0))
    kickoff_dt = datetime.datetime.combine(kickoff_date, kickoff_time)

    # 2. 盘口快照输入（图像+备用文本）
    st.divider()
    st.subheader("📊 临场盘口快照")
    st.info("💡 请上传清晰截图（各机构1-2张）。AI将优先读取图片中的时间戳、初盘与临场水位变化。")
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        euro_imgs = st.file_uploader("🇬🇧 欧赔来源：威廉希尔", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="euro_up")
    with col_b:
        asian_imgs = st.file_uploader("⚽ 亚盘来源：皇冠", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="asian_up")
    with col_c:
        ou_imgs = st.file_uploader("🎯 总进球来源：皇冠", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="ou_up")

    # 图片数量限制提示
    for name, imgs in [("欧赔", euro_imgs), ("亚盘", asian_imgs), ("大小球", ou_imgs)]:
        if imgs and len(imgs) > 2:
            st.warning(f"⚠️ {name} 截图最多支持2张，超出部分将忽略。")

    # 备用手动输入
    with st.expander("📝 备用通道（若图片模糊/OCR失败，请在此补录）"):
        col_x, col_y, col_z = st.columns(3)
        with col_x: euro_txt = st.text_input("欧赔 (主/平/客)", placeholder="例: 2.10 / 3.40 / 3.20")
        with col_y: asian_txt = st.text_input("亚盘初盘 → 临场", placeholder="例: -0.5@0.89 ➡ -0.5@0.92")
        with col_z: ou_txt = st.text_input("大小球初盘 → 临场", placeholder="例: 2.5@0.85 → 2.75@0.98")

    # 3. 时间窗计算
    cn_tz = datetime.timezone(datetime.timedelta(hours=8))
    current_dt = datetime.datetime.now(cn_tz)
    kickoff_tz = kickoff_dt.replace(tzinfo=cn_tz)
    diff_minutes = int((kickoff_tz - current_dt).total_seconds() // 60)
    minutes_display = max(0, diff_minutes)
    time_window = max(60, min(120, minutes_display))
    current_time_str = current_dt.strftime("%Y-%m-%d %H:%M")

    # 4. 组装图片信息提示符
    euro_info = "未上传" if not euro_imgs else f"已上传 {len(euro_imgs)} 张威廉希尔截图 (AI请解析图中赔率与时间戳)"
    asian_info = "未上传" if not asian_imgs else f"已上传 {len(asian_imgs)} 张皇冠亚盘截图 (AI请解析让球/水位轨迹)"
    ou_info = "未上传" if not ou_imgs else f"已上传 {len(ou_imgs)} 张皇冠大小球截图 (AI请解析盘口/水位轨迹)"

    # 5. 生成最终提示词
    final_prompt = BASE_PROMPT.format(
        home=(home or "[主队]").strip(),
        away=(away or "[客队]").strip(),
        league=league,
        kickoff=kickoff_dt.strftime("%Y-%m-%d %H:%M"),
        current=current_time_str,
        minutes=minutes_display,
        time_window=time_window,
        euro_img_info=euro_info,
        asian_img_info=asian_info,
        ou_img_info=ou_info,
        euro_txt=(euro_txt or "未填").strip(),
        asian_txt=(asian_txt or "未填").strip(),
        ou_txt=(ou_txt or "未填").strip(),
        module=MODULES.get(league, "无专属修正")
    )

    # 6. 输出区
    st.divider()
    st.subheader("✅ 生成提示词 (请复制并粘贴至千问3.5对话框，同时拖入上传的截图)")
    st.code(final_prompt, language="markdown")

    if st.button("📋 一键复制完整提示词", type="primary", use_container_width=True):
        safe_prompt = json.dumps(final_prompt, ensure_ascii=False)
        components.html(
            f"""<script>
            navigator.clipboard.writeText({safe_prompt}).then(() => alert("✅ 提示词已复制！\n💡 请在AI对话框粘贴后，将刚才上传的截图一并拖入。")).catch(err => console.error("复制失败", err));
            </script>""",
            height=0, width=0
        )

if __name__ == "__main__":
    main()
