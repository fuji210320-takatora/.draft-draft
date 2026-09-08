import streamlit as st
import random
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="ドラフト×ドラフト", layout="wide")

TEAMS_LIST = [
    "読売ジャイアンツ", "阪神タイガース", "中日ドラゴンズ",
    "東京ヤクルトスワローズ", "広島東洋カープ",
    "横浜DeNAベイスターズ", "埼玉西武ライオンズ",
    "福岡ソフトバンクホークス", "北海道日本ハムファイターズ",
    "千葉ロッテマリーンズ", "オリックス・バファローズ",
    "大阪近鉄バファローズ", "東北楽天ゴールデンイーグルス"
]

all_years = list(range(1965, 2026))

def get_draft_tokyo_team_names(team_name, year):
    if "巨人" in team_name or "読売" in team_name:
        return ["読売", "巨人", "読売ジャイアンツ"]
    elif "阪神" in team_name:
        return ["阪神", "阪神タイガース"]
    elif "中日" in team_name:
        return ["中日", "中日ドラゴンズ"]
    elif "ヤクルト" in team_name or "サンケイ" in team_name or "アトムズ" in team_name:
        if year == 1965: return ["サンケイ", "サンケイスワローズ"]
        elif 1966 <= year <= 1968: return ["サンケイ", "サンケイアトムズ"]
        elif year == 1969: return ["アトムズ"]
        elif 1970 <= year <= 1973: return ["ヤクルト", "ヤクルトアトムズ"]
        elif 1974 <= year <= 2005: return ["ヤクルト", "ヤクルトスワローズ"]
        else: return ["ヤクルト", "東京ヤクルトスワローズ"]
    elif "広島" in team_name:
        return ["広島", "広島カープ"] if 1965 <= year <= 1967 else ["広島", "広島東洋カープ"]
    elif "DeNA" in team_name or "横浜" in team_name or "大洋" in team_name:
        if 1965 <= year <= 1978: return ["大洋", "大洋ホエールズ"]
        elif 1979 <= year <= 1991: return ["大洋", "横浜大洋ホエールズ"]
        elif 1992 <= year <= 2011: return ["横浜", "横浜ベイスターズ"]
        else: return ["DeNA", "横浜DeNAベイスターズ"]
    elif "西武" in team_name or "西鉄" in team_name or "太平洋" in team_name or "クラウン" in team_name:
        if 1965 <= year <= 1971: return ["西鉄", "西鉄ライオンズ"]
        elif 1972 <= year <= 1976: return ["太平洋", "太平洋クラブライオンズ"]
        elif 1977 <= year <= 1978: return ["クラウン", "クラウンライターライオンズ"]
        elif 1979 <= year <= 2007: return ["西武", "西武ライオンズ"]
        else: return ["西武", "埼玉西武ライオンズ"]
    elif "ソフトバンク" in team_name or "ダイエー" in team_name or "南海" in team_name:
        if 1965 <= year <= 1987: return ["南海", "南海ホークス"]
        elif 1988 <= year <= 2003: return ["ダイエー", "福岡ダイエーホークス"]
        else: return ["ソフトバンク", "福岡ソフトバンクホークス"]
    elif "日本ハム" in team_name or "日ハム" in team_name or "東映" in team_name:
        if 1965 <= year <= 1972: return ["東映", "東映フライヤーズ"]
        elif 1973 <= year <= 2002: return ["日本ハム", "日本ハムファイターズ"]
        else: return ["日本ハム", "北海道日本ハムファイターズ"]
    elif "ロッテ" in team_name or ("東京" in team_name and year <= 1968):
        if 1965 <= year <= 1968: return ["東京", "東京オリオンズ"]
        elif 1969 <= year <= 1990: return ["ロッテ", "ロッテオリオンズ"]
        else: return ["ロッテ", "千葉ロッテマリーンズ"]
    elif "近鉄" in team_name:
        if 1965 <= year <= 1998: return ["近鉄", "近鉄バファローズ"]
        elif 1999 <= year <= 2003: return ["近鉄", "大阪近鉄バファローズ"]
        else: return None
    elif "オリックス" in team_name or "阪急" in team_name:
        if 1965 <= year <= 1987: return ["阪急", "阪急ブレーブス"]
        elif 1988 <= year <= 2003: return ["オリックス", "オリックス・ブレーブス"]
        else: return ["オリックス", "オリックスバファローズ"]
    elif "楽天" in team_name:
        return None if year < 2004 else ["楽天", "東北楽天ゴールデンイーグルス"]
    return [team_name]

def get_short_team_name(team_name, year):
    if "阪神" in team_name: return "阪神"
    if "巨人" in team_name or "読売" in team_name: return "読売"
    if "中日" in team_name: return "中日"
    if "ヤクルト" in team_name or "サンケイ" in team_name or "アトムズ" in team_name: return "ヤクルト"
    if "広島" in team_name: return "広島"
    if "DeNA" in team_name or "横浜" in team_name or "大洋" in team_name: return "DeNA" if year >= 2012 else "横浜"
    if "西武" in team_name or "西鉄" in team_name: return "西武"
    if "ソフトバンク" in team_name or "ダイエー" in team_name or "南海" in team_name: return "ソフトバンク"
    if "日本ハム" in team_name or "東映" in team_name: return "日本ハム"
    if "ロッテ" in team_name or "東京" in team_name: return "ロッテ"
    if "近鉄" in team_name: return "近鉄"
    if "楽天" in team_name: return "楽天"
    if "オリックス" in team_name or "阪急" in team_name: return "オリックス"
    return team_name

def get_position_short_name(pos):
    return {"投手": "投", "捕手": "捕", "一塁手": "一", "二塁手": "二", "三塁手": "三", "遊撃手": "遊", "左翼手": "左", "中堅手": "中", "右翼手": "右", "指名打者": "指"}.get(pos, pos)

def get_position_border_color(pos):
    if pos == "捕手": return "#0284c7"
    elif pos in ["一塁手", "二塁手", "三塁手", "遊撃手"]: return "#ca8a04"
    elif pos in ["左翼手", "中堅手", "右翼手"]: return "#16a34a"
    return "#000000"

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_draft_tokyo_data(team_name, year):
    target_names = get_draft_tokyo_team_names(team_name, year)
    if not target_names: return []
    url = f"https://draft.tokyo/draft/{year}/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = response.apparent_encoding
        if response.status_code != 200: return []
        soup = BeautifulSoup(response.text, "html.parser")
        target_table = None
        for h3 in soup.find_all("h3"):
            if any(name in h3.get_text(strip=True) for name in target_names):
                target_table = h3.find_next("table")
                break
        if not target_table: return []
        players = []
        for row in target_table.find_all("tr"):
            cols = [col.get_text(strip=True) for col in row.find_all(["th", "td"])]
            if not cols or "順位" in cols[0] or "選手名" in cols: continue
            if len(cols) >= 2:
                rank = cols[0]
                name = cols[2] if (1998 <= year <= 2009 and len(cols) > 2) else cols[1]
                pos = cols[1] if (1998 <= year <= 2009 and len(cols) > 1) else (cols[2] if len(cols) > 2 else "---")
                status = "入団"
                row_full_text = row.get_text()
                if "拒否" in name or "拒否" in row_full_text: status = "入団拒否"
                elif "×" in name or "外れ" in name: status = "その他"
                elif "ドラフト外" in row_full_text: status = "ドラフト外"
                players.append({"rank_str": rank, "name": name, "pos": pos if pos in ["投手", "捕手", "内野手", "外野手"] else "---", "status": status, "category": "育成" if "育成" in rank else "支配下"})
        return players
    except:
        return []

if "game_started" not in st.session_state: st.session_state.game_started = False
if "my_team" not in st.session_state: st.session_state.my_team = {"batters": [], "pitchers": []}
if "current_lottery" not in st.session_state: st.session_state.current_lottery = None
if "draft_count" not in st.session_state: st.session_state.draft_count = 0
if "skip_count" not in st.session_state: st.session_state.skip_count = 0
if "used_lotteries" not in st.session_state: st.session_state.used_lotteries = set()

for y in all_years:
    if f"setup_year_{y}" not in st.session_state: st.session_state[f"setup_year_{y}"] = True

if not st.session_state.game_started:
    st.title("⚙️ 設定画面")
    num_starting = st.number_input("先発投手枠", 1, 10, 1)
    num_relief = st.number_input("中継ぎ投手枠", 0, 10, 1)
    num_closer = st.number_input("抑え投手枠", 0, 5, 1)
    num_sub_batters = st.number_input("控え野手の追加人数", 0, 20, 0)
    total_batters = 9 + num_sub_batters
    total_required = num_starting + num_relief + num_closer + total_batters
    
    if st.button("🚀 ゲームスタート！", type="primary", use_container_width=True):
        st.session_state.selected_years = [y for y in all_years if st.session_state.get(f"setup_year_{y}", True)]
        st.session_state.max_skips = float("inf")
        st.session_state.no_duplicate_lottery = True
        st.session_state.config_num_starting = num_starting
        st.session_state.config_num_relief = num_relief
        st.session_state.config_num_closer = num_closer
        st.session_state.config_num_batters = total_batters
        st.session_state.max_drafts = total_required
        st.session_state.game_started = True
        st.rerun()
else:
    num_starting = st.session_state.config_num_starting
    num_relief = st.session_state.config_num_relief
    num_closer = st.session_state.config_num_closer
    num_batters = st.session_state.config_num_batters

    col_sub, col_main = st.columns([1, 1.2])

    with col_sub:
        board_html = f"""
        <div style="background-color: #000000; border: 1px solid #333333; border-radius: 12px; padding: 20px;">
            <h3 style="color: #ffffff; margin-top: 0; border-bottom: 2px solid #555555; padding-bottom: 8px;">🏟️ チーム編成ボード</h3>
            <div style="color: #ffffff; margin-bottom: 6px; margin-top: 10px;"><b>【野手陣 ({len(st.session_state.my_team["batters"])} / {num_batters}人)】</b></div>
        """

        batter_roles = [str(i) for i in range(1, 10)]
        for i in range(1, max(0, num_batters - 9) + 1):
            batter_roles.append(f"控{i}")

        existing_batters = {b["打順/役割"]: b for b in st.session_state.my_team["batters"]}

        for role in batter_roles:
            if role in existing_batters:
                b = existing_batters[role]
                border_col = get_position_border_color(b['守備位置'])
                pos_short = get_position_short_name(b["守備位置"]) if b["守備位置"] != "---" else "-"
                board_html += f"""
                <div style='background: #ffffff; border: 1px solid #cccccc; color: #000000; padding: 6px 10px; margin: 4px 0; border-radius: 6px; display: flex; justify-content: space-between; align-items: center;'>
                    <span>
                        <code style='color:#000000; background:#ffffff; border: 1px solid #000000; padding: 1px 4px; border-radius: 3px;'>{role}</code> 
                        <span style='border: 2px solid {border_col}; background: #ffffff; color: #000000; padding: 1px 6px; border-radius: 4px; font-weight: bold; font-size: 13px;'>{pos_short}</span> 
                        <b style='color:#000000; margin-left: 6px;'>{b['選手名']}</b>
                    </span>
                    <span style='color:#555555; font-size:13px;'>({b['出自']})</span>
                </div>
                """
            else:
                board_html += f"""
                <div style='background: #ffffff; border: 1px solid #cccccc; color: #555555; padding: 6px 10px; margin: 4px 0; border-radius: 6px; display: flex; justify-content: space-between; align-items: center;'>
                    <span>
                        <code style='color:#000000; background:#ffffff; border: 1px solid #000000; padding: 1px 4px; border-radius: 3px;'>{role}</code> 
                        <span style='border: 1px solid #000000; background: #ffffff; color: #000000; padding: 1px 6px; border-radius: 4px; font-size: 13px;'>-</span> 
                        <span style='margin-left: 6px; color: #555555;'>未選択 (---)</span>
                    </span>
                </div>
                """

        total_p_slots = num_starting + num_relief + num_closer
        board_html += f'<hr style="border-color: #333333; margin: 15px 0;"><div style="color: #ffffff; margin-bottom: 6px;"><b>【投手陣 ({len(st.session_state.my_team["pitchers"])} / {total_p_slots}人)】</b></div>'

        pitcher_roles = []
        for i in range(1, num_starting + 1): pitcher_roles.append("先" if num_starting == 1 else f"先{i}")
        for i in range(1, num_relief + 1): pitcher_roles.append("継" if num_relief == 1 else f"継{i}")
        for i in range(1, num_closer + 1): pitcher_roles.append("抑" if num_closer == 1 else f"抑{i}")

        p_by_role = {"先発": [], "中継ぎ": [], "抑え": []}
        for p in st.session_state.my_team["pitchers"]:
            if p["起用法"] in p_by_role: p_by_role[p["起用法"]].append(p)

        s_i, r_i, c_i = 0, 0, 0
        for role in pitcher_roles:
            assigned = None
            if role.startswith("先") and s_i < len(p_by_role["先発"]):
                assigned = p_by_role["先発"][s_i]; s_i += 1
            elif role.startswith("継") and r_i < len(p_by_role["中継ぎ"]):
                assigned = p_by_role["中継ぎ"][r_i]; r_i += 1
            elif role.startswith("抑") and c_i < len(p_by_role["抑え"]):
                assigned = p_by_role["抑え"][c_i]; c_i += 1

            if assigned:
                board_html += f"""
                <div style='background: #ffffff; border: 1px solid #cccccc; color: #000000; padding: 6px 10px; margin: 4px 0; border-radius: 6px; display: flex; justify-content: space-between; align-items: center;'>
                    <span>
                        <code style='color:#000000; background:#ffffff; border: 1px solid #000000; padding: 1px 4px; border-radius: 3px;'>{role}</code> 
                        <span style='border: 2px solid #000000; background: #ffffff; color: #000000; padding: 1px 6px; border-radius: 4px; font-weight: bold; font-size: 13px;'>投</span> 
                        <b style='color:#000000; margin-left: 6px;'>{assigned['選手名']}</b>
                    </span>
                    <span style='color:#555555; font-size:13px;'>({assigned['出自']})</span>
                </div>
                """
            else:
                board_html += f"""
                <div style='background: #ffffff; border: 1px solid #cccccc; color: #555555; padding: 6px 10px; margin: 4px 0; border-radius: 6px; display: flex; justify-content: space-between; align-items: center;'>
                    <span>
                        <code style='color:#000000; background:#ffffff; border: 1px solid #000000; padding: 1px 4px; border-radius: 3px;'>{role}</code> 
                        <span style='border: 1px solid #000000; background: #ffffff; color: #000000; padding: 1px 6px; border-radius: 4px; font-size: 13px;'>投</span> 
                        <span style='margin-left: 6px; color: #555555;'>未選択 (---)</span>
                    </span>
                </div>
                """
        board_html += "</div>"
        st.markdown(board_html, unsafe_allow_html=True)

    with col_main:
        if st.button("🎲 抽選する", type="primary", use_container_width=True):
            pool = [(t, y) for y in st.session_state.selected_years for t in TEAMS_LIST if get_draft_tokyo_team_names(t, y)]
            chosen_team, chosen_year = random.choice(pool)
            names = get_draft_tokyo_team_names(chosen_team, chosen_year)
            st.session_state.current_lottery = {
                "team": chosen_team, "actual_team_name": names[0] if names else chosen_team,
                "year": chosen_year, "players": fetch_draft_tokyo_data(chosen_team, chosen_year)
            }
            st.rerun()

        if st.session_state.current_lottery:
            lot = st.session_state.current_lottery
            st.info(f"✨ 抽選：{lot['year']}年 {lot['actual_team_name']}")
            opts = {f"[{p['category']}] {p['rank_str']}: {p['name']} ({p['pos']})": p for p in lot["players"]}
            sel_key = st.selectbox("選手選択", options=list(opts.keys()))
            rtype = st.radio("タイプ", ["野手", "投手"], horizontal=True)
            
            b_role = st.selectbox("打順", [str(i) for i in range(1, 10)]) if rtype == "野手" else ""
            pos = st.selectbox("ポジション", ["捕手", "一塁手", "二塁手", "三塁手", "遊撃手", "左翼手", "中堅手", "右翼手", "指名打者"]) if rtype == "野手" else "-"
            p_role = st.selectbox("投手起用法", ["先発", "中継ぎ", "抑え"]) if rtype == "投手" else ""

            if st.button("登録！", type="primary", use_container_width=True):
                p = opts[sel_key]
                origin = f"'{str(lot['year'])[-2:]} {get_short_team_name(lot['actual_team_name'], lot['year'])}・{p['rank_str']}"
                if rtype == "野手":
                    st.session_state.my_team["batters"].append({"打順/役割": b_role, "守備位置": pos, "選手名": p["name"], "出自": origin})
                else:
                    st.session_state.my_team["pitchers"].append({"起用法": p_role, "選手名": p["name"], "出自": origin})
                st.session_state.current_lottery = None
                st.rerun()
