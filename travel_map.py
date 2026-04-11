"""
帽帽屁屁旅行打卡系统 v2.3
- 海滩森林清新多巴胺配色
- Tooltip 景区标签自动换行
- 去掉对钩，用色块标识已打卡状态
"""

import streamlit as st
import json
import os
import urllib.parse

# ===================== 数据配置 =====================
PROVINCES = {
    "北京": "北京", "天津": "天津", "河北": "河北", "山西": "山西", "内蒙古": "内蒙古",
    "辽宁": "辽宁", "吉林": "吉林", "黑龙江": "黑龙江", "上海": "上海", "江苏": "江苏",
    "浙江": "浙江", "安徽": "安徽", "福建": "福建", "江西": "江西", "山东": "山东",
    "河南": "河南", "湖北": "湖北", "湖南": "湖南", "广东": "广东", "广西": "广西",
    "海南": "海南", "重庆": "重庆", "四川": "四川", "贵州": "贵州", "云南": "云南",
    "西藏": "西藏", "陕西": "陕西", "甘肃": "甘肃", "青海": "青海", "宁夏": "宁夏",
    "新疆": "新疆", "台湾": "台湾", "香港": "香港", "澳门": "澳门"
}

# GeoJSON省份名称映射（GeoJSON名称 -> 标准名称）
GEOJSON_NAME_MAP = {
    "北京市": "北京", "天津市": "天津", "河北省": "河北", "山西省": "山西",
    "内蒙古自治区": "内蒙古", "辽宁省": "辽宁", "吉林省": "吉林",
    "黑龙江省": "黑龙江", "上海市": "上海", "江苏省": "江苏", "浙江省": "浙江",
    "安徽省": "安徽", "福建省": "福建", "江西省": "江西", "山东省": "山东",
    "河南省": "河南", "湖北省": "湖北", "湖南省": "湖南", "广东省": "广东",
    "广西壮族自治区": "广西", "海南省": "海南", "重庆市": "重庆", "四川省": "四川",
    "贵州省": "贵州", "云南省": "云南", "西藏自治区": "西藏", "陕西省": "陕西",
    "甘肃省": "甘肃", "青海省": "青海", "宁夏回族自治区": "宁夏", "新疆维吾尔自治区": "新疆",
    "台湾省": "台湾", "香港特别行政区": "香港", "澳门特别行政区": "澳门"
}

SCENIC_BY_PROVINCE = {
   "北京": ["故宫博物院","天坛公园","颐和园","八达岭—慕田峪长城旅游区","明十三陵景区","恭王府景区","北京奥林匹克公园","圆明园遗址公园","北京（通州）大运河文化旅游景区"],
"天津": ["盘山风景名胜区","天津古文化街旅游区（津门故里）"],
"河北": ["承德避暑山庄及周围寺庙","白洋淀景区","山海关景区","野三坡景区","西柏坡景区","清东陵景区","娲皇宫景区","广府古城景区","白石山景区","清西陵景区","金山岭长城景区","南湖·开滦旅游景区","衡水湖旅游景区"],
"山西": ["云冈石窟","五台山风景名胜区","皇城相府生态文化旅游区","绵山风景区","平遥古城景区","雁门关景区","洪洞大槐树寻根祭祖园","太行山大峡谷八泉峡景区","云丘山景区","黄河壶口瀑布旅游区","晋祠天龙山景区","乔家大院景区"],
"内蒙古": ["响沙湾旅游景区","成吉思汗陵旅游区","中俄边境旅游区","阿尔山-柴河旅游景区","阿斯哈图石林景区","胡杨林旅游区","呼伦贝尔大草原·莫尔格勒河景区","老牛湾黄河大峡谷旅游区"],
"辽宁": ["沈阳植物园","老虎滩海洋公园—老虎滩极地馆","金石滩景区","千山景区","本溪水洞景区","五女山景区","红海滩风景廊道景区"],
"吉林": ["长白山景区","伪满皇宫博物院","净月潭景区","长影世纪城景区","六鼎山文化旅游区","世界雕塑公园景区","高句丽文物古迹旅游景区","大安嫩江湾旅游区","前郭查干湖景区"],
"黑龙江": ["太阳岛景区","五大连池景区","镜泊湖景区","林海奇石景区","北极村旅游景区","虎头旅游景区","扎龙生态旅游区"],
"上海": ["东方明珠广播电视塔","上海野生动物园","上海科技馆","中国共产党一大·二大·四大纪念馆景区","西沙明珠湖景区"],
"江苏": ["钟山风景名胜区-中山陵园风景区","苏州园林（拙政园-留园-虎丘）","周庄古镇景区","中央电视台无锡影视基地三国水浒城景区","灵山大佛景区","夫子庙-秦淮河风光带","鼋头渚旅游风景区","瘦西湖风景区","环球恐龙城休闲旅游区","同里古镇景区","金山·焦山·北固山风景区","濠河风景区","溱湖旅游景区","金鸡湖旅游区","太湖旅游区","沙家浜-虞山尚湖旅游区","天目湖景区","茅山景区","周恩来故里景区","中华麋鹿园景区","云龙湖景区","花果山景区","春秋淹城旅游区","惠山古镇景区","洪泽湖湿地景区","连岛景区"],
"浙江": ["杭州西湖风景区","雁荡山风景区","普陀山风景区","千岛湖风景区","溪口-滕头旅游景区","横店影视城景区","南湖旅游区","西溪湿地旅游区","根宫佛国文化旅游区","南浔古镇景区","天台山景区","神仙居景区","西塘古镇旅游景区","乌镇古镇旅游区","天一阁·月湖景区","江郎山·廿八都旅游区","鲁迅故里·沈园景区","缙云仙都景区","台州府城文化旅游区","刘伯温故里景区","云和梯田景区","双龙风景旅游区"],
"安徽": ["黄山风景区","九华山风景区","天柱山风景区","皖南古村落-西递宏村","天堂寨旅游景区","龙川景区","八里河风景区","古徽州文化旅游区","三河古镇景区","方特旅游区","万佛湖风景区","长江采石矶文化生态旅游区","琅琊山景区"],
"福建": ["鼓浪屿风景名胜区","武夷山风景名胜区","泰宁风景旅游区","福建土楼（永定·南靖）旅游景区","宁德市（白水洋·鸳鸯溪）旅游景区","清源山风景名胜区","太姥山旅游区","三坊七巷景区","古田旅游区","湄洲岛妈祖文化旅游区","冠豸山景区","厦门园林植物园景区"],
"江西": ["庐山风景名胜区","井冈山风景旅游区","三清山风景区","龙虎山风景名胜区","江湾景区","古窑民俗博览区","共和国摇篮景区","明月山旅游区","大觉山景区","龟峰景区","滕王阁旅游区","萍乡武功山景区","庐山西海景区","三百山景区","篁岭景区"],
"山东": ["泰山景区","蓬莱阁旅游区","明故城三孔旅游区","崂山景区","刘公岛景区","南山景区","台儿庄古城景区","天下第一泉景区","沂蒙山旅游区","青州古城景区","威海华夏城景区","黄河口生态旅游区","萤火虫水洞·地下大峡谷旅游区","微山湖旅游区","奥帆海洋文化旅游区","周村古商城景区"],
"河南": ["嵩山少林景区","龙门石窟景区","云台山-神农山-青天河风景区","殷墟景区","河南白云山景区","清明上河园景区","尧山-中原大佛景区","老君山-鸡冠洞旅游区","龙潭大峡谷景区","西峡恐龙遗迹园-伏牛山-老界岭旅游区","嵖岈山旅游景区","红旗渠-太行大峡谷旅游景区","芒砀山汉文化旅游景区","八里沟景区","鸡公山景区","太昊伏羲陵文化旅游区","宝泉旅游区"],
"湖北": ["黄鹤楼公园","三峡大坝-屈原故里文化旅游区","三峡人家风景区","武当山风景区","神农溪纤夫文化旅游区","神农架生态旅游区","清江画廊景区","中国武汉-东湖生态旅游风景区","木兰文化生态旅游区","恩施大峡谷景区","三国赤壁古战场景区","古隆中景区","腾龙洞景区","三峡大瀑布景区","明显陵文化旅游景区","麻城龟峰山景区"],
"湖南": ["武陵源-天门山旅游区","衡山旅游区","韶山旅游区","岳阳楼-君山岛景区","岳麓山-橘子洲旅游区","花明楼景区","东江湖旅游区","崀山景区","炎帝陵景区","桃花源旅游区","矮寨·十八洞·德夯大峡谷景区","凤凰古城旅游区"],
"广东": ["长隆旅游度假区","华侨城旅游度假区","白云山景区","雁南飞茶田景区","观澜湖休闲旅游区","连州地下河旅游景区","丹霞山景区","西樵山景区","罗浮山景区","长鹿旅游休博园","海陵岛大角湾海上丝路旅游区","孙中山故里旅游区","惠州西湖旅游景区","星湖旅游景区","开平碉楼文化旅游区","万绿湖风景区"],
"广西": ["漓江风景区","乐满地度假世界","独秀峰·靖江王城景区","青秀山风景名胜旅游区","两江四湖·象山景区","德天跨国瀑布景区","百色起义纪念园景区","涠洲岛南湾鳄鱼山景区","黄姚古镇景区","程阳八寨景区","花山岩画景区"],
"海南": ["南山文化旅游区","南山大小洞天旅游区","呀诺达雨林文化旅游区","分界洲岛旅游区","槟榔谷黎苗文化旅游区","蜈支洲岛旅游区","天涯海角游览区"],
"重庆": ["大足石刻景区","小三峡-小小三峡旅游区","武隆喀斯特旅游区","酉阳桃花源旅游景区","万盛黑山谷-龙鳞石海风景区","南川金佛山景区","江津四面山景区","云阳龙缸景区","彭水阿依河景区","黔江濯水景区","奉节白帝城·瞿塘峡景区","涪陵武陵山大裂谷景区"],
"四川": ["青城山-都江堰旅游景区","峨眉山景区","九寨沟景区","乐山大佛景区","黄龙风景名胜区","羌城旅游区","汶川特别旅游区","阆中古城旅游景区","邓小平故里旅游区","剑门蜀道剑门关旅游景区","朱德故里景区","海螺沟景区","碧峰峡旅游景区","光雾山旅游景区","稻城亚丁旅游景区","安仁古镇景区","四姑娘山景区","成都天台山景区"],
"贵州": ["黄果树瀑布景区","龙宫景区","百里杜鹃景区","荔波樟江景区","青岩古镇景区","梵净山旅游区","镇远古城旅游景区","赤水丹霞旅游区","织金洞景区","万峰林景区"],
"云南": ["石林风景区","玉龙雪山景区","崇圣寺三塔文化旅游区","中国科学院西双版纳热带植物园","香格里拉普达措景区","世博园景区","腾冲火山热海旅游区","普者黑旅游景区","元阳哈尼梯田景区","丽江古城景区"],
"西藏": ["布达拉宫景区","大昭寺景区","扎什伦布寺景区","巴松措景区","冈仁波齐-玛旁雍措景区"],
"陕西": ["秦始皇兵马俑博物馆","华清宫景区","黄帝陵景区","大雁塔-大唐芙蓉园景区","华山景区","法门寺佛文化景区","金丝峡景区","太白山旅游景区","城墙·碑林历史文化景区","延安革命纪念地景区","镇北台长城景区","韩城司马迁祠景区","大明宫旅游景区","乾陵景区"],
"甘肃": ["嘉峪关文物景区","崆峒山风景名胜区","麦积山景区","鸣沙山月牙泉景区","七彩丹霞景区","炳灵寺世界文化遗产旅游区","官鹅沟景区","冶力关旅游区"],
"青海": ["青海湖景区","塔尔寺景区","互助土族故土园景区","阿咪东索景区"],
"宁夏": ["沙湖旅游景区","沙坡头旅游景区","镇北堡西部影城景区","水洞沟旅游区","青铜峡黄河大峡谷旅游区","六盘山红军长征旅游区"],
"新疆": ["天山天池风景名胜区","葡萄沟风景区","喀纳斯景区","那拉提旅游风景区","坎儿井民俗园景区","博斯腾湖景区","泽普金湖杨景区","巴音布鲁克景区","帕米尔旅游区","世界魔鬼城景区","赛里木湖景区","江布拉克景区","天山托木尔景区","和田白沙湖景区","刀郎部落景区","喀拉峻景区","白沙湖景区","塔克拉玛干·三五九旅文化旅游区"]
}

DATA_FILE = "travel_data.json"


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"visited_provinces": [], "visited_spots": []}


def save_data():
    data = {
        "visited_provinces": st.session_state.visited,
        "visited_spots": st.session_state.visited_scenic
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ===================== 页面配置 =====================
st.set_page_config(page_title="帽帽屁屁旅行打卡", layout="wide", page_icon="✈️")

data = load_data()
if "visited" not in st.session_state:
    st.session_state.visited = data["visited_provinces"]
if "visited_scenic" not in st.session_state:
    st.session_state.visited_scenic = data["visited_spots"]

# ===================== Query Param 路由处理 =====================
query_params = st.query_params
current_page = query_params.get("page", "travel")

# 处理打卡操作
if "toggle" in query_params:
    action = query_params["toggle"]
    # 处理省份切换
    if action.startswith("p_"):
        province = action[2:]
        if province in st.session_state.visited:
            st.session_state.visited.remove(province)
        else:
            st.session_state.visited.append(province)
        save_data()
        # 清除 toggle 参数，保留 page 参数
        del query_params["toggle"]
        st.rerun()
    # 处理景区切换
    elif action.startswith("s_"):
        spot = action[2:]
        if spot in st.session_state.visited_scenic:
            st.session_state.visited_scenic.remove(spot)
        else:
            st.session_state.visited_scenic.append(spot)
        save_data()
        del query_params["toggle"]
        st.rerun()

# ===================== CSS 样式 =====================
st.markdown("""
<style>
    :root {
        --bg-cream: #F6F4F0;
        --bg-warm: #EDE8E0;
        --card-bg: #FFFFFF;
        --card-border: #D8D3CB;
        --primary-ocean: #6BA3BE;
        --primary-ocean-light: #8DBDD2;
        --accent-mint: #7DB89D;
        --accent-mint-light: #A0D0B6;
        --accent-sand: #D4B896;
        --accent-coral: #E8A090;
        --text-dark: #3D4F5F;
        --text-medium: #5A7080;
        --text-light: #8A9AA6;
        --shadow-card: 0 2px 12px rgba(61, 79, 95, 0.07);
        --radius-md: 12px;
        --radius-lg: 20px;
    }

    .stApp { background: linear-gradient(180deg, var(--bg-cream) 0%, var(--bg-warm) 100%); }

    /* 头部 */
    .header-section {
        background: linear-gradient(135deg, #FFFFFF 0%, #F5FAFC 100%);
        border-radius: var(--radius-lg);
        padding: 24px 32px;
        margin-bottom: 20px;
        box-shadow: var(--shadow-card);
        border: 1px solid var(--card-border);
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .header-section::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary-ocean), var(--accent-mint), var(--accent-sand), var(--accent-coral));
    }
    .header-title { font-size: 1.8rem; font-weight: 700; color: var(--text-dark); margin: 0 0 4px 0; }
    .header-subtitle { font-size: 0.9rem; color: var(--text-medium); margin: 0; }

    /* 统计卡片 */
    .stats-container { display: flex; gap: 16px; justify-content: center; margin-bottom: 20px; }
    .stat-card {
        background: var(--card-bg);
        border-radius: var(--radius-md);
        padding: 16px 28px;
        text-align: center;
        box-shadow: var(--shadow-card);
        border: 1px solid var(--card-border);
        min-width: 120px;
    }
    .stat-number { font-size: 1.8rem; font-weight: 700; margin: 0; }
    .stat-number.ocean { color: var(--primary-ocean); }
    .stat-number.mint { color: var(--accent-mint); }
    .stat-number.sand { color: var(--accent-sand); }
    .stat-label { font-size: 0.75rem; color: var(--text-light); margin-top: 2px; }

    /* Tab 样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: var(--card-bg);
        padding: 6px;
        border-radius: var(--radius-md);
        border: 1px solid var(--card-border);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 20px;
        font-weight: 500;
        font-size: 0.9rem;
        color: var(--text-medium);
    }
    .stTabs [aria-selected="true"] {
        background: var(--primary-ocean) !important;
        color: white !important;
    }

    /* 省份按钮 - 紧凑样式 */
    .prov-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 4px 12px;
        font-size: 0.8rem;
        height: 28px;
        line-height: 20px;
        border-radius: 14px;
        border: 1px solid var(--card-border);
        background: var(--card-bg);
        color: var(--text-medium);
        text-decoration: none;
        cursor: pointer;
        transition: all 0.2s ease;
        user-select: none;
    }
    .prov-btn:hover {
        border-color: var(--primary-ocean);
        color: var(--primary-ocean);
        background: rgba(107, 163, 190, 0.06);
    }
    .prov-visited {
        background: var(--primary-ocean) !important;
        color: white !important;
        border-color: var(--primary-ocean) !important;
        box-shadow: 0 2px 8px rgba(107, 163, 190, 0.35);
    }
    .prov-visited:hover {
        background: var(--primary-ocean-light) !important;
        border-color: var(--primary-ocean-light) !important;
        color: white !important;
    }

    /* 景区列表 */
    .scenic-item {
        background: var(--bg-cream);
        border-radius: 6px;
        padding: 8px 12px;
        margin: 4px 0;
        border-left: 3px solid var(--accent-mint);
        font-size: 0.85rem;
        color: var(--text-dark);
    }
    .scenic-item.visited {
        background: rgba(125, 184, 157, 0.12);
        border-left-color: var(--accent-mint);
    }
    .scenic-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        border: 1.5px solid var(--card-border);
        background: var(--card-bg);
        color: var(--text-light);
        text-decoration: none;
        cursor: pointer;
        transition: all 0.2s ease;
        font-size: 0.85rem;
    }
    .scenic-btn:hover {
        border-color: var(--accent-mint);
        color: var(--accent-mint);
    }
    .scenic-btn.visited {
        background: var(--accent-mint);
        border-color: var(--accent-mint);
        color: white;
        box-shadow: 0 2px 6px rgba(125, 184, 157, 0.3);
    }
    .scenic-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 2px 0;
    }

    /* 地图面板 */
    .map-panel {
        background: var(--card-bg);
        border-radius: var(--radius-lg);
        padding: 20px;
        box-shadow: var(--shadow-card);
        border: 1px solid var(--card-border);
        margin-bottom: 20px;
    }
    .map-header {
        font-size: 1.1rem;
        color: var(--text-dark);
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* 进度条 */
    .progress-container {
        margin-top: 16px;
        background: var(--bg-warm);
        border-radius: 10px;
        padding: 3px;
    }
    .progress-bar {
        height: 8px;
        border-radius: 10px;
        background: linear-gradient(90deg, var(--primary-ocean), var(--accent-mint), var(--accent-sand));
    }
    .progress-text {
        text-align: center;
        margin-top: 6px;
        font-size: 0.8rem;
        color: var(--text-medium);
    }

    /* 底部提示 */
    .footer-tip {
        background: var(--bg-warm);
        border-radius: var(--radius-md);
        padding: 12px 20px;
        margin-top: 20px;
        text-align: center;
        color: var(--text-medium);
        font-size: 0.85rem;
        border: 1px dashed var(--card-border);
    }

    /* 分组标题 */
    .region-label {
        font-size: 0.8rem;
        color: var(--text-light);
        margin: 8px 0 4px 0;
        font-weight: 500;
    }

    /* 顶部导航栏 */
    .top-nav {
        display: flex;
        gap: 6px;
        background: var(--card-bg);
        padding: 6px;
        border-radius: var(--radius-md);
        border: 1px solid var(--card-border);
        margin-bottom: 20px;
        box-shadow: var(--shadow-card);
    }
    .nav-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 10px 28px;
        border-radius: 8px;
        font-size: 0.95rem;
        font-weight: 500;
        color: var(--text-medium);
        text-decoration: none;
        cursor: pointer;
        transition: all 0.2s ease;
        border: none;
        background: transparent;
    }
    .nav-btn:hover {
        background: rgba(107, 163, 190, 0.08);
        color: var(--primary-ocean);
    }
    .nav-btn.active {
        background: var(--primary-ocean);
        color: white;
        box-shadow: 0 2px 8px rgba(107, 163, 190, 0.35);
    }
</style>
""", unsafe_allow_html=True)

# ===================== 顶部导航栏 =====================
nav_travel_class = "nav-btn active" if current_page == "travel" else "nav-btn"
nav_game_class = "nav-btn active" if current_page == "game" else "nav-btn"
st.markdown(f"""
<div class="top-nav">
    <a href="?page=travel" class="{nav_travel_class}">✈️ 旅行打卡</a>
    <a href="?page=game" class="{nav_game_class}">🎨 答题游戏</a>
</div>
""", unsafe_allow_html=True)

# ===================== 页面路由 =====================
if current_page == "game":
    # ---- 答题游戏页 ----
    game_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "game.html")
    with open(game_path, "r", encoding="utf-8") as f:
        game_html = f.read()
    st.components.v1.html(game_html, height=800, scrolling=True)

elif current_page == "travel":
    # ---- 旅行打卡页（原有内容）----
    st.markdown("""
<div class="header-section">
    <h1 class="header-title">✈️ 帽帽屁屁旅行打卡</h1>
    <p class="header-subtitle">记录每一段旅程，点亮属于我们的中国地图</p>
</div>
""", unsafe_allow_html=True)

    # ===================== 统计卡片 =====================
    all_spots_count = sum(len(spots) for spots in SCENIC_BY_PROVINCE.values())
    visited_provinces_count = len(st.session_state.visited)
    visited_spots_count = len(st.session_state.visited_scenic)

    st.markdown(f"""
    <div class="stats-container">
        <div class="stat-card">
            <p class="stat-number ocean">{visited_provinces_count}</p>
            <p class="stat-label">已打卡省份</p>
        </div>
        <div class="stat-card">
            <p class="stat-number mint">{visited_spots_count}</p>
            <p class="stat-label">已打卡景区</p>
        </div>
        <div class="stat-card">
            <p class="stat-number sand">{all_spots_count - visited_spots_count}</p>
            <p class="stat-label">待探索</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ===================== 地图展示（放在上面）=====================
    st.markdown("""
    <div class="map-panel">
        <div class="map-header">🗺️ 旅行足迹地图</div>
    """, unsafe_allow_html=True)

    # 构建数据
    visited_provinces = st.session_state.visited
    province_spots = {}
    for p in visited_provinces:
        spots_in_p = [s for s in SCENIC_BY_PROVINCE.get(p, []) if s in st.session_state.visited_scenic]
        province_spots[p] = spots_in_p

    # 转换数据为 JSON
    visited_json = json.dumps(visited_provinces, ensure_ascii=False)
    spots_json = json.dumps(province_spots, ensure_ascii=False)

    # GeoJSON名称映射表（用于JS匹配）
    geojson_name_map_json = json.dumps(GEOJSON_NAME_MAP, ensure_ascii=False)

    # 所有景区数据
    all_provinces_spots = {p: list(spots) for p, spots in SCENIC_BY_PROVINCE.items()}
    all_spots_json = json.dumps(all_provinces_spots, ensure_ascii=False)

    # 生成地图 HTML（所有资源内嵌，不依赖外部CDN）
    # 读取本地 GeoJSON 和 ECharts
    _geojson_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "china_geojson.json")
    _echarts_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "echarts.min.js")

    with open(_geojson_path, "r", encoding="utf-8") as _f:
        _geojson_str = _f.read()
    with open(_echarts_path, "r", encoding="utf-8") as _f:
        _echarts_js = _f.read()

    map_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ background: transparent; }}
        #map {{ width: 100%; height: 550px; }}

        .map-tooltip {{
          background: rgba(255, 253, 250, 0.98) !important;
          border: none !important;
          border-radius: 14px !important;
          box-shadow: 0 8px 28px rgba(61, 79, 95, 0.14) !important;
          padding: 0 !important;
          max-width: 280px !important;
        }}
        .tooltip-inner {{ padding: 14px 16px; font-family: 'Microsoft YaHei', sans-serif; }}
        .tooltip-title {{ font-size: 14px; font-weight: 600; color: #3D4F5F; margin-bottom: 8px; }}
        .tooltip-status {{ font-size: 11px; padding: 2px 10px; border-radius: 10px; display: inline-block; margin-bottom: 8px; }}
        .tooltip-status.visited {{ background: rgba(107, 163, 190, 0.18); color: #5A8FA8; }}
        .tooltip-status.unvisited {{ background: rgba(212, 184, 150, 0.2); color: #A08A6A; }}
        .tooltip-spots {{
          font-size: 11px; color: #5A7080; line-height: 1.5;
          max-height: 160px; overflow-y: auto;
          display: flex; flex-wrap: wrap; gap: 4px;
          align-content: flex-start;
        }}
        .spot-tag {{
          display: inline-block;
          background: rgba(125, 184, 157, 0.12);
          color: #5A9A80;
          padding: 2px 8px; border-radius: 6px;
          font-size: 10px; white-space: nowrap;
        }}
        .tooltip-footer {{ font-size: 11px; color: #8A9AA6; margin-top: 8px; padding-top: 6px; border-top: 1px dashed #D8D3CB; }}
      </style>
    </head>
    <body>
      <div id="map"></div>
      <script>{_echarts_js}</script>
      <script>
        // 数据
        var visited = {visited_json};
        var visitedSpots = {spots_json};
        var allProvincesSpots = {all_spots_json};
        var nameMap = {geojson_name_map_json};

        // GeoJSON 数据直接内嵌，无需网络请求
        var geoJson = {_geojson_str};
        echarts.registerMap('china', geoJson);

        // 初始化图表
        var chart = echarts.init(document.getElementById('map'));

        // 构建地图数据
        var mapData = [];
        geoJson.features.forEach(function(feature) {{
          var geoName = feature.properties.name;
          var stdName = nameMap[geoName] || geoName;
          var isVisited = visited.indexOf(stdName) >= 0;
          mapData.push({{
            name: geoName,
            value: isVisited ? 1 : 0,
            itemStyle: isVisited ? {{
              areaColor: '#6BA3BE',
              borderColor: '#5A92AB',
              borderWidth: 2,
              shadowBlur: 15,
              shadowColor: 'rgba(107, 163, 190, 0.45)'
            }} : {{
              areaColor: '#E4DFD8',
              borderColor: '#CCC5BC',
              borderWidth: 1
            }},
            emphasis: isVisited ? {{
              itemStyle: {{
                areaColor: '#8DBDD2',
                borderColor: '#5A92AB',
                borderWidth: 3,
                shadowBlur: 20,
                shadowColor: 'rgba(107, 163, 190, 0.5)'
              }}
            }} : {{
              itemStyle: {{
                areaColor: '#D6D0C8',
                borderColor: '#AAA49B',
                borderWidth: 2
              }}
            }}
          }});
        }});

        // 设置图表选项
        var option = {{
          backgroundColor: 'transparent',
          tooltip: {{
            trigger: 'item',
            enterable: false,
            backgroundColor: 'transparent',
            borderWidth: 0,
            padding: 0,
            formatter: function(params) {{
              var geoName = params.name;
              var stdName = nameMap[geoName] || geoName;
              var isVisited = visited.indexOf(stdName) >= 0;
              var spots = visitedSpots[stdName] || [];
              var allSpots = allProvincesSpots[stdName] || [];

              var html = '<div class="tooltip-inner">';
              html += '<div class="tooltip-title">📍 ' + stdName + '</div>';

              if (isVisited) {{
                html += '<span class="tooltip-status visited">✅ 已打卡</span>';
                if (spots.length > 0) {{
                  html += '<div class="tooltip-spots">';
                  spots.forEach(function(s) {{
                    html += '<span class="spot-tag">' + s + '</span>';
                  }});
                  html += '</div>';
                }} else {{
                  html += '<div class="tooltip-footer">省份已打卡</div>';
                }}
              }} else {{
                html += '<span class="tooltip-status unvisited">🔒 尚未探索</span>';
                if (allSpots.length > 0) {{
                  html += '<div class="tooltip-footer">共 ' + allSpots.length + ' 个5A景区等待发现</div>';
                }}
              }}

              html += '</div>';
              return '<div class="map-tooltip">' + html + '</div>';
            }}
          }},
          scaleLimit: {{
            min: 0.8,
            max: 3
          }},
          series: [{{
            name: '中国地图',
            type: 'map',
            map: 'china',
            roam: true,
            zoom: 1.0,
            center: [105, 36],
            backgroundColor: 'transparent',
            itemStyle: {{
              areaColor: '#E4DFD8',
              borderColor: '#CCC5BC',
              borderWidth: 1,
              borderRadius: 2
            }},
            emphasis: {{
              itemStyle: {{
                areaColor: '#8DBDD2',
                borderColor: '#5A92AB',
                borderWidth: 2.5,
                shadowBlur: 12,
                shadowColor: 'rgba(107, 163, 190, 0.3)'
              }},
              label: {{
                show: true,
                color: '#3D4F5F',
                fontSize: 12,
                fontWeight: 'bold'
              }}
            }},
            select: {{
              disabled: true
            }},
            label: {{
              show: false,
              color: '#FFFFFF',
              fontSize: 10,
              fontWeight: 'normal'
            }},
            data: mapData
          }}]
        }};

        chart.setOption(option);

        // 点亮动画：依次高亮已访问省份
        if (visited.length > 0) {{
          var delay = 0;
          visited.forEach(function(p, idx) {{
            setTimeout(function() {{
              for (var key in nameMap) {{
                if (nameMap[key] === p) {{
                  var geoName = key;
                  mapData.forEach(function(item) {{
                    if (item.name === geoName) {{
                      item.value = 1;
                      item.itemStyle = {{
                        areaColor: '#6BA3BE',
                        borderColor: '#5A92AB',
                        borderWidth: 2,
                        shadowBlur: 20,
                        shadowColor: 'rgba(107, 163, 190, 0.55)'
                      }};
                    }}
                  }});
                  chart.setOption({{ series: [{{ data: mapData }}] }});
                  break;
                }}
              }}
            }}, idx * 120);
            delay += 120;
          }});
        }}

        window.addEventListener('resize', function() {{ chart.resize(); }});
      </script>
    </body>
    </html>
    """

    st.components.v1.html(map_html, height=570)

    st.markdown('</div>', unsafe_allow_html=True)

    # 进度条
    total_spots = sum(len(spots) for spots in SCENIC_BY_PROVINCE.values())
    visited_spots = len(st.session_state.visited_scenic)
    progress = (visited_spots / total_spots * 100) if total_spots > 0 else 0

    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-bar" style="width: {progress}%"></div>
    </div>
    <p class="progress-text">全国5A景区打卡进度：{visited_spots}/{total_spots} ({progress:.1f}%)</p>
    </div>
    """, unsafe_allow_html=True)

    # ===================== 打卡选项（放在下面）=====================
    st.markdown("---")
    tab1, tab2 = st.tabs(["🏠 省份打卡", "🏞️ 景区打卡"])

    with tab1:
        regions = {
            "华北": ["北京", "天津", "河北", "山西", "内蒙古"],
            "东北": ["辽宁", "吉林", "黑龙江"],
            "华东": ["上海", "江苏", "浙江", "安徽", "福建", "江西", "山东"],
            "华中": ["河南", "湖北", "湖南"],
            "华南": ["广东", "广西", "海南"],
            "西南": ["重庆", "四川", "贵州", "云南", "西藏"],
            "西北": ["陕西", "甘肃", "青海", "宁夏", "新疆"],
            "港澳台": ["香港", "澳门", "台湾"]
        }

        for region_name, provinces in regions.items():
            st.markdown(f'<p class="region-label">{region_name}</p>', unsafe_allow_html=True)

            # 用 HTML 按钮渲染，支持已打卡变色
            btns_html = '<div style="display:flex;flex-wrap:wrap;gap:4px;margin-bottom:8px;">'
            for province in provinces:
                is_visited = province in st.session_state.visited
                encoded = urllib.parse.quote(province)
                if is_visited:
                    btns_html += f'<a href="?toggle=p_{encoded}" class="prov-btn prov-visited" onclick="window.parent.location=this.href;return false;">{province}</a>'
                else:
                    btns_html += f'<a href="?toggle=p_{encoded}" class="prov-btn" onclick="window.parent.location=this.href;return false;">{province}</a>'
            btns_html += '</div>'
            st.markdown(btns_html, unsafe_allow_html=True)

    with tab2:
        for province, spots in SCENIC_BY_PROVINCE.items():
            visited_in_province = [s for s in spots if s in st.session_state.visited_scenic]
            total_in_province = len(spots)
            visited_count = len(visited_in_province)

            with st.expander(f"📌 {province} ({visited_count}/{total_in_province})"):
                spots_html = '<div style="display:flex;flex-direction:column;gap:2px;">'
                for spot in spots:
                    is_visited = spot in st.session_state.visited_scenic
                    encoded = urllib.parse.quote(spot)
                    item_class = "scenic-item visited" if is_visited else "scenic-item"
                    btn_class = "scenic-btn visited" if is_visited else "scenic-btn"
                    btn_text = "✦" if is_visited else "○"
                    spots_html += f'<div class="scenic-row"><div class="{item_class}" style="flex:1;">{spot}</div><a href="?toggle=s_{encoded}" class="{btn_class}" onclick="window.parent.location=this.href;return false;" style="margin-left:8px;flex-shrink:0;">{btn_text}</a></div>'
                spots_html += '</div>'
                st.markdown(spots_html, unsafe_allow_html=True)

    # ===================== 底部提示 =====================
    st.markdown("""
    <div class="footer-tip">
        💾 打卡数据已自动保存到本地 | 🖱️ 地图支持缩放和拖拽
    </div>
    """, unsafe_allow_html=True)
