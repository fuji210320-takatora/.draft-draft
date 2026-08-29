import streamlit as st
import random
import pandas as pd
import re
import requests
from bs4 import BeautifulSoup

# =====================================================================
# 1. ページ全体の基本設定 ＆ 文字サイズ・見出しサイズ調整CSS
# =====================================================================
st.set_page_config(page_title="ドラフト×ドラフト", layout="wide")

st.markdown("""
<style>
    /* アプリ全体の基本の文字サイズを変更 */
    html, body, [class*="css"] {
        font-size: 15px; 
    }
    
    /* 表（dataframe）の中の文字サイズを変更 */
    div[data-testid="stDataFrame"] div[role="grid"] {
        font-size: 15px;
    }
    
    /* 見出しの文字サイズ変更 */
    h1 {
        font-size: 26px !important;
    }
    h2 {
        font-size: 22px !important;
    }
    h3 {
        font-size: 18px !important;
    }
</style>
""", unsafe_allow_html=True)

TEAMS_LIST = [
    "読売ジャイアンツ", "阪神タイガース", "中日ドラゴンズ",
    "横浜DeNAベイスターズ", "広島東洋カープ", "東京ヤクルトスワローズ",
    "オリックス・バファローズ", "千葉ロッテマリーンズ",
    "福岡ソフトバンクホークス", "東北楽天ゴールデンイーグルス",
    "埼玉西武ライオンズ", "北海道日本ハムファイターズ",
    "大阪近鉄バファローズ", "オリックス・ブルーウェーブ"
]

def get_team_code_and_name(team_name, year):
    """年度に応じたURLコードと正式な球団名を取得する関数"""
    # 楽天は2005年参入（2004年ドラフトから参加）なので、2004年未満は存在しない
    if team_name == "東北楽天ゴールデンイーグルス" and year < 2004:
        return None, None

    # 近鉄は2001〜2003年限定
    if team_name == "大阪近鉄バファローズ":
        if 2001 <= year <= 2003:
            return "bu", "大阪近鉄バファローズ"
        else:
            return None, None

    # オリックス・ブルーウェーブは2003年以前
    if team_name == "オリックス・ブルーウェーブ":
        if year <= 2003:
            return "bw", "オリックス・ブルーウェーブ"
        else:
            return None, None

    # オリックス・バファローズ（2004年合併、2005年〜、2004年はBs統合）
    if team_name == "オリックス・バファローズ":
        if year <= 2003:
            return None, None
        elif year == 2004:
            return "bs", "オリックス・バファローズ"
        elif 2005 <= year <= 2018:
            return "bs", "オリックス・バファローズ"
        else:
            return "b", "オリックス・バファローズ"

    # 横浜DeNAベイスターズ
    if team_name == "横浜DeNAベイスターズ":
        return ("yb", "横浜ベイスターズ") if year <= 2011 else ("db", "横浜DeNAベイスターズ")

    # ソフトバンク（2004年はダイエー）
    if team_name == "福岡ソフトバンクホークス" and year == 2004:
        return ("h", "福岡ダイエーホークス")

    # 西武（2007年以前は西武ライオンズ）
    if team_name == "埼玉西武ライオンズ" and year <= 2007:
        return ("l", "西武ライオンズ")

    # ヤクルト（2005年以前はヤクルトスワローズ）
    if team_name == "東京ヤクルトスワローズ" and year <= 2005:
        return ("s", "ヤクルトスワローズ")

    # 日本ハム（2003年以前は日本ハムファイターズ、コードはfのまま）
    if team_name == "北海道日本ハムファイターズ":
        actual_name = "日本ハムファイターズ" if year <= 2003 else "北海道日本ハムファイターズ"
        return "f", actual_name

    codes = {
        "読売ジャイアンツ": "g", "阪神タイガース": "t", "中日ドラゴンズ": "d",
        "広島東洋カープ": "c", "千葉ロッテマリーンズ": "m",
        "福岡ソフトバンクホークス": "h", "東北楽天ゴールデンイーグルス": "e",
        "埼玉西武ライオンズ": "l", "北海道日本ハムファイターズ": "f",
    }
    return codes.get(team_name, "t"), team_name

def get_short_team_name(team_name, year):
    """球団名の略称を取得する関数"""
    if team_name == "大阪近鉄バファローズ":
        return "近鉄"
    if team_name == "オリックス・ブルーウェーブ":
        return "オリックス"
    if team_name == "北海道日本ハムファイターズ" and year <= 2003:
        return "日本ハム"

    if team_name == "横浜DeNAベイスターズ":
        return "横浜" if year <= 2011 else "DeNA"
    if team_name == "福岡ソフトバンクホークス" and year == 2004:
        return "ダイエー"
    if team_name == "埼玉西武ライオンズ" and year <= 2007:
        return "西武"
    if team_name == "東京ヤクルトスワローズ" and year <= 2005:
        return "ヤクルト"

    short_names = {
        "読売ジャイアンツ": "巨人",
        "阪神タイガース": "阪神",
        "中日ドラゴンズ": "中日",
        "横浜DeNAベイスターズ": "DeNA",
        "広島東洋カープ": "広島",
        "東京ヤクルトスワローズ": "ヤクルト",
        "オリックス・バファローズ": "オリックス",
        "千葉ロッテマリーンズ": "ロッテ",
        "福岡ソフトバンクホークス": "ソフトバンク",
        "東北楽天ゴールデンイーグルス": "楽天",
        "埼玉西武ライオンズ": "西武",
        "北海道日本ハムファイターズ": "日本ハム",
    }
    return short_names.get(team_name, team_name)

# =====================================================================
# 2. テキスト全体から順位・名前・年齢・ポジションを正確に分解する関数
# =====================================================================
def parse_player_data(cols, row_text, current_category):
    rank_text = ""
    name = ""
    age = ""
    pos = "---"
    
    for col_val in cols:
        if any(kw in col_val for kw in ["位", "巡", "枠", "自由", "選択権なし", "希望"]):
            rank_text = col_val
            break
            
    if not rank_text:
        if current_category == "希望入団枠":
            rank_text = "希望入団枠"
        elif "希望入団枠" in row_text:
            rank_text = "希望入団枠"
        if current_category == "自由獲得選手":
            rank_text = "自由獲得選手"
        elif "自由獲得選手" in row_text:
            rank_text = "自由獲得選手"

    if "選択権なし" in row_text:
        return rank_text if rank_text else "選択権なし", "（選択権なし）", "", "---"

    full_target_text = "".join(cols)
    
    age_match = re.search(r'[（\(](\d+)[）\)]', full_target_text)
    if age_match:
        age = f"（{age_match.group(1)}）"

    pos_match = re.search(r'(投手|捕手|内野手|外野手|投\s*手|捕\s*手|内野\s*手|外野\s*手)', full_target_text)
    if pos_match:
        raw_p = pos_match.group(1).replace(" ", "")
        pos = raw_p

    clean_text = full_target_text
    if rank_text and rank_text != "不明":
        clean_text = clean_text.replace(rank_text, "")
    
    if age_match:
        clean_text = clean_text.split(age_match.group(0))[0]
    if pos_match:
        clean_text = clean_text.split(pos_match.group(0))[0]
        
    name = clean_text.strip()
    
    return rank_text, name if name else "（不明）", age, pos

# =====================================================================
# 3. DOM順走査関数
# =====================================================================
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_npb_draft_data(team_name, year):
    t_code, actual_team_name = get_team_code_and_name(team_name, year)
    if not t_code:
        return []

    url = f"https://draft.npb.jp/draft/{year}/draftlist_{t_code}.html"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    players = []
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = response.apparent_encoding
        
        if response.status_code != 200:
            return []
            
        soup = BeautifulSoup(response.text, "html.parser")
        current_category = None
        
        content_area = soup.find("div", id="content") or soup.body
        if not content_area:
            content_area = soup
            
        elements = content_area.find_all(["h2", "h3", "h4", "div", "tr"])
        
        for el in elements:
            el_text = el.get_text(strip=True)
            if not el_text:
                continue
                
            if el.name in ["h2", "h3", "h4"] or "選択会議" in el_text:
                if "育成選手選択会議" in el_text or "育成" in el_text:
                    current_category = "育成選手"
                elif "新人選手選択会議" in el_text and "育成" not in el_text:
                    current_category = "支配下選手"
                elif "高校生" in el_text:
                    current_category = "高校生"
                elif "大学生・社会人" in el_text or "大学生" in el_text or "社会人" in el_text:
                    current_category = "大学生・社会人ほか"
                elif "自由獲得" in el_text or "希望入団枠" in el_text:
                    current_category = "希望入団枠" if "希望" in el_text else "自由獲得選手"
                continue

            if el.name == "tr":
                row_text = el_text
                
                if "育成" in row_text:
                    current_category = "育成選手"
                elif "自由獲得枠" in row_text:
                    current_category = "自由獲得選手"
                elif "希望入団枠" in row_text:
                    current_category = "希望入団枠"
                elif "高校生" in row_text:
                    current_category = "高校生"
                elif "大学生" in row_text or "社会人" in row_text:
                    current_category = "大学生・社会人ほか"

                is_header_or_note = False
                if "選手名" in row_text or "選択選手" in row_text or row_text.startswith("※"):
                    is_header_or_note = True

                cols = [c.get_text(strip=True) for c in el.find_all(["th", "td"]) if c.get_text(strip=True)]
                
                if len(cols) >= 1 and not is_header_or_note:
                    rank_text, name, age, pos = parse_player_data(cols, row_text, current_category)
                    
                    if name and "選手名" not in name:
                        cat = "育成" if (current_category == "育成選手" or "育成" in rank_text) else "支配下"
                        
                        if current_category in ["高校生", "大学生・社会人ほか"]:
                            display_rank = f"[{current_category}] {rank_text}" if current_category not in rank_text else rank_text
                        else:
                            display_rank = rank_text
                        
                        player_entry = {
                            "rank_str": display_rank,
                            "name": name,
                            "pos": pos,
                            "category": cat
                        }
                        if player_entry not in players:
                            players.append(player_entry)
                            
        if not players:
            players = [
                {"rank_str": "1位", "name": f"{actual_team_name}テスト選手1", "pos": "投手", "category": "支配下"},
                {"rank_str": "育成1位", "name": f"{actual_team_name}テスト育成1", "pos": "捕手", "category": "育成"},
            ]
            
        return players

    except Exception as e:
        return []

# =====================================================================
# 4. セッションステートの初期化
# =====================================================================
if "game_started" not in st.session_state:
    st.session_state.game_started = False

if "my_team" not in st.session_state:
    st.session_state.my_team = {"batters": [], "pitchers": []}

if "current_lottery" not in st.session_state:
    st.session_state.current_lottery = None

if "draft_count" not in st.session_state:
    st.session_state.draft_count = 0

if "skip_count" not in st.session_state:
    st.session_state.skip_count = 0

# 対象年度を2001年まで拡張
all_years = list(range(2025, 2000, -1))

# =====================================================================
# 5. スタート前画面（未開始の場合）
# =====================================================================
if not st.session_state.game_started:
    st.title("⚙️ 設定画面")
    st.markdown("ゲームを始める前に、チームの必要人数、スキップ上限、対象年度を設定してください。")
    
    st.markdown("---")
    
    # チーム編成人数の設定
    st.markdown("### 🏟️ チーム編成の人数設定")
    c_p1, c_p2, c_p3 = st.columns(3)
    with c_p1:
        num_starting = st.number_input("先発投手枠", min_value=1, max_value=6, value=1)
    with c_p2:
        num_relief = st.number_input("中継ぎ投手枠", min_value=0, max_value=7, value=1)
    with c_p3:
        num_closer = st.number_input("抑え投手枠", min_value=0, max_value=5, value=1)

    st.markdown("---")
    
    # 野手人数（左寄せ）
    st.markdown("### ⚾ 野手人数設定")
    num_starting_batters = 9
    num_sub_batters = st.number_input("控え野手の追加人数", min_value=0, max_value=20, value=0)

    total_batters = num_starting_batters + num_sub_batters
    total_required_drafts = num_starting + num_relief + num_closer + total_batters
    st.success(f"💡 設定されたチームの総人数（必要指名数）: **{total_required_drafts} 人** （投手 {num_starting + num_relief + num_closer}人 ＋ 野手スタメン9人 ＋ 控え野手 {num_sub_batters}人）")

    st.markdown("---")

    # スキップ設定（デフォルトを3回 = index=4）
    st.markdown("### 🔄 スキップ回数制限")
    skip_limit_option = st.selectbox(
        "スキップ上限回数を選択",
        options=["無制限"] + [str(i) for i in range(21)],
        index=4
    )
    if skip_limit_option == "無制限":
        max_skips_val = float("inf")
    else:
        max_skips_val = int(skip_limit_option)

    st.markdown("---")
    
    # 年度選択設定
    st.markdown("### 📅 対象年度の設定")
    col_btn1, col_btn2 = st.columns(2)

    for y in all_years:
        if f"setup_year_{y}" not in st.session_state:
            st.session_state[f"setup_year_{y}"] = True

    if col_btn1.button("すべて選択", use_container_width=True):
        for y in all_years:
            st.session_state[f"setup_year_{y}"] = True
        st.rerun()

    if col_btn2.button("すべてクリア", use_container_width=True):
        for y in all_years:
            st.session_state[f"setup_year_{y}"] = False
        st.rerun()

    st.markdown("")
    
    num_cols = 4
    rows = [all_years[i:i + num_cols] for i in range(0, len(all_years), num_cols)]
    
    for row_years in rows:
        cols_grid = st.columns(num_cols)
        for i, y in enumerate(row_years):
            with cols_grid[i]:
                st.checkbox(f"{y}年", value=st.session_state[f"setup_year_{y}"], key=f"setup_year_{y}")

    st.markdown("---")
    
    if st.button("🚀 この設定でゲームスタート！", type="primary", use_container_width=True):
        selected_years = [y for y in all_years if st.session_state[f"setup_year_{y}"]]
        
        if not selected_years:
            st.error("⚠️ 対象年度が1つも選択されていません。少なくとも1つ以上選択してください。")
        else:
            st.session_state.selected_years = selected_years
            st.session_state.max_skips = max_skips_val
            st.session_state.config_num_starting = num_starting
            st.session_state.config_num_relief = num_relief
            st.session_state.config_num_closer = num_closer
            st.session_state.config_num_batters = total_batters
            st.session_state.max_drafts = total_required_drafts
            
            st.session_state.game_started = True
            st.session_state.draft_count = 0
            st.session_state.skip_count = 0
            st.session_state.my_team = {"batters": [], "pitchers": []}
            st.session_state.current_lottery = None
            st.rerun()

# =====================================================================
# 6. メインゲーム画面（スタート後の場合）
# =====================================================================
else:
    max_skips = st.session_state.max_skips
    selected_years = st.session_state.selected_years
    max_drafts = st.session_state.max_drafts

    num_starting = st.session_state.config_num_starting
    num_relief = st.session_state.config_num_relief
    num_closer = st.session_state.config_num_closer
    num_batters = st.session_state.config_num_batters

    all_defensive_positions = ["捕手", "一塁手", "二塁手", "三塁手", "遊撃手", "左翼手", "中堅手", "右翼手", "指名打者"]

    st.sidebar.title("📋 メニュー")
    if st.sidebar.button("⚙️ 設定を変更してやり直す", use_container_width=True):
        st.session_state.game_started = False
        st.rerun()

    st.title("⚾ ドラフト×ドラフト")
    st.markdown(f"選択中年度: <code>{min(selected_years)} 〜 {max(selected_years)} ({len(selected_years)}年間)</code>", unsafe_allow_html=True)

    col_sub, col_main = st.columns([1, 1.2])

    with col_sub:
        st.subheader("🏟️ チーム編成ボード")
        
        # --- 野手ボード ---
        st.markdown(f"### 【野手陣 ({len(st.session_state.my_team['batters'])} / {num_batters}人)】")
        
        batter_template_roles = [f"{i}番" for i in range(1, 10)]
        bench_count = max(0, num_batters - 9)
        for i in range(1, bench_count + 1):
            batter_template_roles.append(f"控え{i}")

        batter_display_rows = []
        existing_batters_dict = {b["打順/役割"]: b for b in st.session_state.my_team["batters"]}
        
        for target_role in batter_template_roles:
            if target_role in existing_batters_dict:
                b = existing_batters_dict[target_role]
                batter_display_rows.append({
                    "打順/役割": b["打順/役割"],
                    "守備位置": b["守備位置"],
                    "選手名": b["選手名"],
                    "出自": b["出自"]
                })
            else:
                batter_display_rows.append({
                    "打順/役割": target_role,
                    "守備位置": "---",
                    "選手名": "---",
                    "出自": "---"
                })
        
        batter_table_height = 38 + len(batter_display_rows) * 35
        st.dataframe(pd.DataFrame(batter_display_rows), use_container_width=True, hide_index=True, height=batter_table_height)

        # --- 投手ボード ---
        total_pitcher_slots = num_starting + num_relief + num_closer
        st.markdown(f"### 【投手陣 ({len(st.session_state.my_team['pitchers'])} / {total_pitcher_slots}人)】")
        
        pitcher_template_roles = []
        for i in range(1, num_starting + 1):
            pitcher_template_roles.append(f"先発{i}" if num_starting > 1 else "先発")
        for i in range(1, num_relief + 1):
            pitcher_template_roles.append(f"中継ぎ{i}" if num_relief > 1 else "中継ぎ")
        for i in range(1, num_closer + 1):
            pitcher_template_roles.append(f"抑え{i}" if num_closer > 1 else "抑え")

        pitchers_by_role = {"先発": [], "中継ぎ": [], "抑え": []}
        for p in st.session_state.my_team["pitchers"]:
            r = p["起用法"]
            if r in pitchers_by_role:
                pitchers_by_role[r].append(p)

        pitcher_display_rows = []
        s_idx, r_idx, c_idx = 0, 0, 0
        for target_role in pitcher_template_roles:
            assigned_player = None
            if "先発" in target_role and s_idx < len(pitchers_by_role["先発"]):
                assigned_player = pitchers_by_role["先発"][s_idx]
                s_idx += 1
            elif "中継ぎ" in target_role and r_idx < len(pitchers_by_role["中継ぎ"]):
                assigned_player = pitchers_by_role["中継ぎ"][r_idx]
                r_idx += 1
            elif "抑え" in target_role and c_idx < len(pitchers_by_role["抑え"]):
                assigned_player = pitchers_by_role["抑え"][c_idx]
                c_idx += 1

            if assigned_player:
                pitcher_display_rows.append({
                    "起用法": target_role,
                    "選手名": assigned_player["選手名"],
                    "出自": assigned_player["出自"]
                })
            else:
                pitcher_display_rows.append({
                    "起用法": target_role,
                    "選手名": "---",
                    "出自": "---"
                })
        
        pitcher_table_height = 38 + len(pitcher_display_rows) * 35
        st.dataframe(pd.DataFrame(pitcher_display_rows), use_container_width=True, hide_index=True, height=pitcher_table_height)

    with col_main:
        st.progress(st.session_state.draft_count / max_drafts)
        st.write(f"**指名完了数: {st.session_state.draft_count} / {max_drafts} 回**")

        if max_skips != float("inf"):
            remaining_skips = max(0, max_skips - st.session_state.skip_count)
            st.write(f"スキップ残回数: **{remaining_skips} / {max_skips} 回**")
        else:
            st.write(f"スキップ残回数: **無制限 (現在 {st.session_state.skip_count} 回使用)**")

        if st.session_state.draft_count >= max_drafts:
            st.success("🎉 すべてのドラフト指名が完了しました！お疲れ様でした！")
            if st.button("もう一度最初から設定し直す", use_container_width=True):
                st.session_state.game_started = False
                st.rerun()
        else:
            c1, c2 = st.columns(2)
            with c1:
                is_lottery_disabled = (st.session_state.current_lottery is not None)
                if st.button("🎲 抽選する（球団 ＆ 年）", type="primary", disabled=is_lottery_disabled, use_container_width=True):
                    # 抽選ループ：選ばれた年に対して、その年に実際に存在するチームが出るまで再抽選する
                    while True:
                        chosen_team = random.choice(TEAMS_LIST)
                        chosen_year = random.choice(selected_years)
                        t_code, actual_team_name = get_team_code_and_name(chosen_team, chosen_year)
                        if t_code is not None:
                            break
                    
                    fetched_players = fetch_npb_draft_data(chosen_team, chosen_year)
                    
                    st.session_state.current_lottery = {
                        "team": chosen_team,
                        "actual_team_name": actual_team_name,
                        "year": chosen_year,
                        "players": fetched_players
                    }
                    st.rerun()
            with c2:
                is_skip_disabled = (st.session_state.current_lottery is None) or (st.session_state.skip_count >= max_skips)
                
                skip_button_label = "🔄 スキップ（引き直す）"
                if st.session_state.skip_count >= max_skips:
                    skip_button_label = "🚫 スキップ上限に達しました"

                if st.button(skip_button_label, disabled=is_skip_disabled, use_container_width=True):
                    if st.session_state.skip_count < max_skips:
                        st.session_state.skip_count += 1
                        while True:
                            chosen_team = random.choice(TEAMS_LIST)
                            chosen_year = selected_years[random.randint(0, len(selected_years) - 1)]
                            t_code, actual_team_name = get_team_code_and_name(chosen_team, chosen_year)
                            if t_code is not None:
                                break
                        
                        fetched_players = fetch_npb_draft_data(chosen_team, chosen_year)
                            
                        st.session_state.current_lottery = {
                            "team": chosen_team,
                            "actual_team_name": actual_team_name,
                            "year": chosen_year,
                            "players": fetched_players
                        }
                        st.rerun()

        if st.session_state.current_lottery:
            lottery = st.session_state.current_lottery
            short_name = get_short_team_name(lottery['team'], lottery['year'])
            st.info(f"✨ 抽選結果： **{lottery['year']}** の **{short_name} ({lottery['actual_team_name']})** が選ばれました！")
            
            if not lottery["players"]:
                st.warning("⚠️ この年のデータが見つかりませんでした。別のボタンで引き直してください。")
            else:
                st.subheader("📋 指名候補選手一覧")
                display_players = []
                for p in lottery["players"]:
                    display_players.append({
                        "順位": p["rank_str"],
                        "区分": p["category"],
                        "選手名": p["name"],
                        "ポジション": p["pos"]
                    })
                players_df = pd.DataFrame(display_players)
                candidate_table_height = min(400, 38 + len(players_df) * 35)
                st.dataframe(players_df, use_container_width=True, hide_index=True, height=candidate_table_height)
                
                st.subheader("✍️ 選手を指名して役割を決定する")
                
                role_type = st.radio("選手タイプを選択してください", ["野手", "投手"], horizontal=True)
                
                current_batters_count = len(st.session_state.my_team["batters"])
                current_starting_count = sum(1 for p in st.session_state.my_team["pitchers"] if p["起用法"] == "先発")
                current_relief_count = sum(1 for p in st.session_state.my_team["pitchers"] if p["起用法"] == "中継ぎ")
                current_closer_count = sum(1 for p in st.session_state.my_team["pitchers"] if p["起用法"] == "抑え")
                
                with st.form("select_form"):
                    player_options = {}
                    for p in lottery["players"]:
                        label = f"[{p['category']}] {p['rank_str']}: {p['name']} ({p['pos']})"
                        player_options[label] = p
                        
                    selected_key = st.selectbox("指名する選手を選択", options=list(player_options.keys()))
                    
                    assigned_bat_role = ""
                    assigned_pos = "-"
                    assigned_pitcher_role = ""
                    
                    if role_type == "野手":
                        if current_batters_count >= num_batters:
                            st.warning("⚠️ 野手枠はすでに満員です！")
                        
                        available_batter_roles = []
                        for i in range(1, 10):
                            role_name = f"{i}番"
                            if not any(b["打順/役割"] == role_name for b in st.session_state.my_team["batters"]):
                                available_batter_roles.append(role_name)
                        
                        bench_count = max(0, num_batters - 9)
                        for i in range(1, bench_count + 1):
                            role_name = f"控え{i}"
                            if not any(b["打順/役割"] == role_name for b in st.session_state.my_team["batters"]):
                                available_batter_roles.append(role_name)
                                
                        assigned_bat_role = st.selectbox("打順・役割を選択", options=available_batter_roles if available_batter_roles else ["満員"])
                        
                        used_positions = [b["守備位置"] for b in st.session_state.my_team["batters"] if b["守備位置"] != "---"]
                        available_positions = [pos for pos in all_defensive_positions if pos not in used_positions]
                        
                        assigned_pos = st.selectbox(
                            "守備ポジションを選択", 
                            options=available_positions if available_positions else ["すべてのポジションが埋まっています"]
                        )
                    else:
                        available_pitcher_types = []
                        if current_starting_count < num_starting:
                            available_pitcher_types.append("先発")
                        if current_relief_count < num_relief:
                            available_pitcher_types.append("中継ぎ")
                        if current_closer_count < num_closer:
                            available_pitcher_types.append("抑え")
                            
                        if not available_pitcher_types:
                            st.warning("⚠️ すべての投手枠（先発・中継ぎ・抑え）が満員です！")
                            
                        assigned_pitcher_role = st.selectbox("投手起用法を選択", options=available_pitcher_types if available_pitcher_types else ["満員"])
                    
                    submit_btn = st.form_submit_button("この選手を決定して登録！", use_container_width=True)
                    
                    if submit_btn:
                        chosen_player = player_options[selected_key]
                        
                        if role_type == "野手" and (current_batters_count >= num_batters or assigned_bat_role == "満員" or assigned_pos == "すべてのポジションが埋まっています"):
                            st.error("野手枠が上限に達しているか、選べる打順・ポジションがありません。")
                        elif role_type == "投手" and assigned_pitcher_role == "満員":
                            st.error("選べる投手起用法枠がありません。")
                        else:
                            short_team_name = get_short_team_name(lottery['team'], lottery['year'])
                            origin_text = f"{lottery['year']} {short_team_name} ({chosen_player['rank_str']})"
                            
                            if role_type == "野手":
                                st.session_state.my_team["batters"].append({
                                    "打順/役割": assigned_bat_role,
                                    "守備位置": assigned_pos,
                                    "選手名": chosen_player["name"],
                                    "出自": origin_text
                                })
                            else:
                                st.session_state.my_team["pitchers"].append({
                                    "起用法": assigned_pitcher_role,
                                    "選手名": chosen_player["name"],
                                    "出自": origin_text
                                })
                            
                            st.session_state.draft_count += 1
                            st.session_state.current_lottery = None
                            st.success(f"{chosen_player['name']} 選手を指名しました！")
                            st.rerun()
