import streamlit as str_module
import random
import pandas as pd
import requests
from bs4 import BeautifulSoup

# =====================================================================
# 1. ページ全体の基本設定 ＆ スタイル調整
# =====================================================================
str_module.set_page_config(page_title="ドラフト×ドラフト", layout="wide")

str_module.markdown("""
<style>
    /* フォントサイズ調整 */
    html, body, [class*="css"] {
        font-size: 15px; 
    }
    
    h1 { font-size: 26px !important; }
    h2 { font-size: 22px !important; }
    h3 { font-size: 18px !important; }

    /* スマホ表示時、年度選択のチェックボックス群を3列グリッドに折り返す */
    @media (max-width: 768px) {
        div[data-testid="stHorizontalBlock"]:has(div[data-testid="stCheckbox"]) {
            display: grid !important;
            grid-template-columns: repeat(3, 1fr) !important;
            gap: 4px !important;
            margin-bottom: 0px !important;
        }
        div[data-testid="stHorizontalBlock"]:has(div[data-testid="stCheckbox"]) > div[data-testid="column"] {
            width: auto !important;
            flex: none !important;
            padding: 0px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

TEAMS_LIST = [
    "読売ジャイアンツ", "阪神タイガース", "中日ドラゴンズ",
    "東京ヤクルトスワローズ", "広島東洋カープ",
    "横浜DeNAベイスターズ", "埼玉西武ライオンズ",
    "福岡ソフトバンクホークス", "北海道日本ハムファイターズ",
    "千葉ロッテマリーンズ", "オリックス・バファローズ",
    "大阪近鉄バファローズ", "東北楽天ゴールデンイーグルス"
]

all_years = list(range(1965, 2026))

# =====================================================================
# 2. 補助関数（チーム名・表記関連）
# =====================================================================
def get_draft_tokyo_team_names(team_name, year):
    if "巨人" in team_name or "読売" in team_name:
        return ["読売", "巨人", "読売ジャイアンツ"]
    elif "阪神" in team_name:
        return ["阪神", "阪神タイガース"]
    elif "中日" in team_name:
        return ["中日", "中日ドラゴンズ"]
    elif "ヤクルト" in team_name or "サンケイ" in team_name or "アトムズ" in team_name:
        if year == 1965:
            return ["サンケイ", "サンケイスワローズ"]
        elif 1966 <= year <= 1968:
            return ["サンケイ", "サンケイアトムズ"]
        elif year == 1969:
            return ["アトムズ"]
        elif 1970 <= year <= 1973:
            return ["ヤクルト", "ヤクルトアトムズ"]
        elif 1974 <= year <= 2005:
            return ["ヤクルト", "ヤクルトスワローズ"]
        elif 2006 <= year <= 2025:
            return ["ヤクルト", "東京ヤクルトスワローズ"]
    elif "広島" in team_name:
        if 1965 <= year <= 1967:
            return ["広島", "広島カープ"]
        else:
            return ["広島", "広島東洋カープ"]
    elif "DeNA" in team_name or "横浜" in team_name or "大洋" in team_name:
        if 1965 <= year <= 1978:
            return ["大洋", "大洋ホエールズ"]
        elif 1979 <= year <= 1991:
            return ["大洋", "横浜大洋ホエールズ"]
        elif 1992 <= year <= 2011:
            return ["横浜", "横浜ベイスターズ"]
        else:
            return ["DeNA", "横浜DeNAベイスターズ"]
    elif "西武" in team_name or "西鉄" in team_name or "太平洋" in team_name or "クラウン" in team_name:
        if 1965 <= year <= 1971:
            return ["西鉄", "西鉄ライオンズ"]
        elif 1972 <= year <= 1976:
            return ["太平洋", "太平洋クラブライオンズ"]
        elif 1977 <= year <= 1978:
            return ["クラウン", "クラウンライターライオンズ"]
        elif 1979 <= year <= 2007:
            return ["西武", "西武ライオンズ"]
        else:
            return ["西武", "埼玉西武ライオンズ"]
    elif "ソフトバンク" in team_name or "ダイエー" in team_name or "南海" in team_name:
        if 1965 <= year <= 1987:
            return ["南海", "南海ホークス"]
        elif 1988 <= year <= 2003:
            return ["ダイエー", "福岡ダイエーホークス"]
        else:
            return ["ソフトバンク", "福岡ソフトバンクホークス"]
    elif "日本ハム" in team_name or "日ハム" in team_name or "東映" in team_name:
        if 1965 <= year <= 1972:
            return ["東映", "東映フライヤーズ"]
        elif 1973 <= year <= 2002:
            return ["日本ハム", "日本ハムファイターズ"]
        else:
            return ["日本ハム", "北海道日本ハムファイターズ"]
    elif "ロッテ" in team_name or ("東京" in team_name and year <= 1968):
        if 1965 <= year <= 1968:
            return ["東京", "東京オリオンズ"]
        elif 1969 <= year <= 1990:
            return ["ロッテ", "ロッテオリオンズ"]
        else:
            return ["ロッテ", "千葉ロッテマリーンズ"]
    elif "近鉄" in team_name:
        if 1965 <= year <= 1998:
            return ["近鉄", "近鉄バファローズ"]
        elif 1999 <= year <= 2003:
            return ["近鉄", "大阪近鉄バファローズ"]
        else:
            return None
    elif "オリックス" in team_name or "阪急" in team_name:
        if 1965 <= year <= 1987:
            return ["阪急", "阪急ブレーブス"]
        elif 1988 <= year <= 2003:
            return ["オリックス", "オリックス・ブレーブス"]
        else:
            return ["オリックス", "オリックスバファローズ"]
    elif "楽天" in team_name:
        if year < 2004:
            return None
        return ["楽天", "東北楽天ゴールデンイーグルス"]

    return [team_name]

def get_short_team_name(team_name, year):
    if "阪神" in team_name: return "阪神"
    if "巨人" in team_name or "読売" in team_name: return "読売"
    if "中日" in team_name: return "中日"
    if "ヤクルト" in team_name or "サンケイ" in team_name or "アトムズ" in team_name:
        if year == 1965: return "サンケイ"
        elif 1966 <= year <= 1968: return "サンケイ"
        elif year == 1969: return "アトムズ"
        elif 1970 <= year <= 1973: return "ヤクルト"
        elif 1974 <= year <= 2005: return "ヤクルト"
        else: return "ヤクルト"
    if "広島" in team_name:
        if 1965 <= year <= 1967: return "広島"
        else: return "広島"
    if "DeNA" in team_name or "横浜" in team_name or "大洋" in team_name:
        if 1965 <= year <= 1978: return "大洋"
        elif 1979 <= year <= 1991: return "大洋"
        elif 1992 <= year <= 2011: return "横浜"
        else: return "DeNA"
    if "西武" in team_name or "西鉄" in team_name or "太平洋" in team_name or "クラウン" in team_name:
        if 1965 <= year <= 1971: return "西鉄"
        elif 1972 <= year <= 1976: return "太平洋"
        elif 1977 <= year <= 1978: return "クラウン"
        else: return "西武"
    if "ソフトバンク" in team_name or "ダイエー" in team_name or "南海" in team_name:
        if 1965 <= year <= 1987: return "南海"
        elif 1988 <= year <= 2003: return "ダイエー"
        else: return "ソフトバンク"
    if "日本ハム" in team_name or "日ハム" in team_name or "東映" in team_name:
        if 1965 <= year <= 1972: return "東映"
        elif 1973 <= year <= 2002: return "日本ハム"
        else: return "日本ハム"
    if "ロッテ" in team_name or "東京" in team_name:
        if 1965 <= year <= 1968: return "東京"
        else: return "ロッテ"
    if "近鉄" in team_name: return "近鉄"
    if "楽天" in team_name: return "楽天"
    if "オリックス" in team_name or "阪急" in team_name:
        if 1965 <= year <= 1987: return "阪急"
        elif 1988 <= year <= 2003: return "オリックス"
        else: return "オリックス"
    return team_name

def get_position_short_name(pos):
    mapping = {
        "投手": "投", "捕手": "捕", "一塁手": "一", "二塁手": "二",
        "三塁手": "三", "遊撃手": "遊", "左翼手": "左", "中堅手": "中",
        "右翼手": "右", "指名打者": "指"
    }
    return mapping.get(pos, pos)

def get_position_border_color(pos):
    if pos == "捕手":
        return "#0284c7" # 青系
    elif pos in ["一塁手", "二塁手", "三塁手", "遊撃手"]:
        return "#ca8a04" # 黄・オレンジ系
    elif pos in ["左翼手", "中堅手", "右翼手"]:
        return "#16a34a" # 緑系
    return "#cccccc"

# =====================================================================
# 3. draft.tokyo スクレイピング関数
# =====================================================================
@str_module.cache_data(ttl=3600, show_spinner=False)
def fetch_draft_tokyo_data(team_name, year):
    target_names = get_draft_tokyo_team_names(team_name, year)
    if not target_names:
        return []

    url = f"https://draft.tokyo/draft/{year}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = response.apparent_encoding
        if response.status_code != 200:
            return []
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        target_table = None
        for h3 in soup.find_all("h3"):
            h3_text = h3.get_text(strip=True)
            if any(name in h3_text for name in target_names):
                next_table = h3.find_next("table")
                if next_table:
                    target_table = next_table
                    break

        if not target_table:
            return []

        players = []
        rows = target_table.find_all("tr")
        
        for row in rows:
            cols = [col.get_text(strip=True) for col in row.find_all(["th", "td"])]
            if not cols or "順位" in cols[0] or "選手名" in cols or "守備" in cols:
                continue
                
            if len(cols) >= 2:
                rank = cols[0]
                if 1998 <= year <= 2009:
                    pos = cols[1] if len(cols) > 1 else "---"
                    name = cols[2] if len(cols) > 2 else "---"
                else:
                    name = cols[1]
                    pos = cols[2] if len(cols) > 2 else "---"
                
                status = "入団"
                row_full_text = row.get_text()
                if "拒否" in name or "拒否" in row_full_text:
                    status = "入団拒否"
                elif "×" in name or "外れ" in name or "交渉権なし" in name:
                    status = "その他"
                elif "ドラフト外" in row_full_text or "ドラフト外" in name:
                    status = "ドラフト外"

                cat = "育成" if "育成" in rank else "支配下"
                
                player_entry = {
                    "rank_str": rank, "name": name,
                    "pos": pos if pos in ["投手", "捕手", "内野手", "外野手"] else "---",
                    "status": status, "category": cat
                }
                if player_entry not in players:
                    players.append(player_entry)
                    
        return players
    except Exception:
        return []

# =====================================================================
# 4. セッションステートの初期化 ＆ 同期ロジック
# =====================================================================
if "game_started" not in str_module.session_state:
    str_module.session_state.game_started = False
if "my_team" not in str_module.session_state:
    str_module.session_state.my_team = {"batters": [], "pitchers": []}
if "current_lottery" not in str_module.session_state:
    str_module.session_state.current_lottery = None
if "draft_count" not in str_module.session_state:
    str_module.session_state.draft_count = 0
if "skip_count" not in str_module.session_state:
    str_module.session_state.skip_count = 0
if "used_lotteries" not in str_module.session_state:
    str_module.session_state.used_lotteries = set()

for y in all_years:
    if f"setup_year_{y}" not in str_module.session_state:
        str_module.session_state[f"setup_year_{y}"] = True

def generate_year_text():
    active_y = [y for y in all_years if str_module.session_state.get(f"setup_year_{y}", True)]
    if not active_y:
        return ""
    if len(active_y) == len(all_years):
        return f"{min(all_years)}〜{max(all_years)}"
    
    active_y = sorted(active_y)
    ranges = []
    range_start = active_y[0]
    range_end = active_y[0]
    
    for y in active_y[1:]:
        if y == range_end + 1:
            range_end = y
        else:
            ranges.append((range_start, range_end))
            range_start = y
            range_end = y
    ranges.append((range_start, range_end))
    
    parts = []
    for start, end in ranges:
        if start == end:
            parts.append(str(start))
        else:
            parts.append(f"{start}〜{end}")
    return ", ".join(parts)

if "pending_year_text" not in str_module.session_state:
    str_module.session_state.pending_year_text = generate_year_text()

if "year_text_input" not in str_module.session_state:
    str_module.session_state.year_text_input = str_module.session_state.pending_year_text
else:
    str_module.session_state.year_text_input = str_module.session_state.pending_year_text

def update_checkboxes_from_text():
    val = str_module.session_state.get("year_text_input", "")
    parsed_years = set()
    parts = val.replace("～", "~").replace("-", "~").replace("〜", "~").split(",")
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if "~" in part:
            try:
                sub_parts = part.split("~")
                if len(sub_parts) == 2:
                    s, e = int(sub_parts[0].strip()), int(sub_parts[1].strip())
                    for y in range(min(s, e), max(s, e) + 1):
                        if 1965 <= y <= 2025:
                            parsed_years.add(y)
            except:
                pass
        else:
            try:
                y = int(part)
                if 1965 <= y <= 2025:
                    parsed_years.add(y)
            except:
                pass
    
    for y in all_years:
        str_module.session_state[f"setup_year_{y}"] = (y in parsed_years)
    str_module.session_state.pending_year_text = generate_year_text()

# =====================================================================
# 5. スタート前画面
# =====================================================================
if not str_module.session_state.game_started:
    str_module.title("⚙️ 設定画面")
    str_module.markdown("ゲームを始める前に、チームの必要人数、スキップ上限、対象年度を設定してください。")
    
    str_module.markdown("---")
    str_module.markdown("### 🏟️ チーム編成の人数設定")
    c_p1, c_p2, c_p3 = str_module.columns(3)
    with c_p1:
        num_starting = str_module.number_input("先発投手枠", min_value=1, max_value=10, value=1)
    with c_p2:
        num_relief = str_module.number_input("中継ぎ投手枠", min_value=0, max_value=10, value=1)
    with c_p3:
        num_closer = str_module.number_input("抑え投手枠", min_value=0, max_value=5, value=1)

    str_module.markdown("---")
    str_module.markdown("### ⚾ 野手人数設定")
    num_starting_batters = 9
    num_sub_batters = str_module.number_input("控え野手の追加人数", min_value=0, max_value=20, value=0)

    total_batters = num_starting_batters + num_sub_batters
    total_required_drafts = num_starting + num_relief + num_closer + total_batters
    str_module.success(f"💡 設定されたチームの総人数（必要指名数）: **{total_required_drafts} 人**")

    str_module.markdown("---")
    str_module.markdown("### 🔄 スキップ回数制限 ＆ 抽選設定")
    skip_limit_option = str_module.selectbox("スキップ上限回数を選択", options=["無制限"] + [str(i) for i in range(21)], index=4)
    max_skips_val = float("inf") if skip_limit_option == "無制限" else int(skip_limit_option)

    no_duplicate_lottery = str_module.checkbox("一度引いたドラフト（球団×年）の組み合わせを重複させない", value=True)

    str_module.markdown("---")
    str_module.markdown("### 📅 対象年度の設定 (1965〜2025)")

    str_module.text_input(
        "対象年度を直接入力 (例: `2010〜2020` または `1965, 1970, 2010〜2015`)",
        key="year_text_input",
        on_change=update_checkboxes_from_text
    )

    q_col1, q_col2, q_col3, q_col4 = str_module.columns(4)
    
    if q_col1.button("2000年以降", use_container_width=True):
        for y in all_years:
            str_module.session_state[f"setup_year_{y}"] = (2000 <= y <= 2025)
        str_module.session_state.pending_year_text = generate_year_text()
        str_module.rerun()

    if q_col2.button("1990年以降", use_container_width=True):
        for y in all_years:
            str_module.session_state[f"setup_year_{y}"] = (1990 <= y <= 2025)
        str_module.session_state.pending_year_text = generate_year_text()
        str_module.rerun()

    if q_col3.button("すべて選択", use_container_width=True):
        for y in all_years:
            str_module.session_state[f"setup_year_{y}"] = True
        str_module.session_state.pending_year_text = generate_year_text()
        str_module.rerun()
        
    if q_col4.button("すべてクリア", use_container_width=True):
        for y in all_years:
            str_module.session_state[f"setup_year_{y}"] = False
        str_module.session_state.pending_year_text = generate_year_text()
        str_module.rerun()

    str_module.markdown("")
    num_cols = 6
    rows = [all_years[i:i + num_cols] for i in range(0, len(all_years), num_cols)]
    
    def on_checkbox_change():
        str_module.session_state.pending_year_text = generate_year_text()

    for row_years in rows:
        cols_grid = str_module.columns(num_cols)
        for i, y in enumerate(row_years):
            with cols_grid[i]:
                str_module.checkbox(f"{y}", value=str_module.session_state.get(f"setup_year_{y}", True), key=f"setup_year_{y}", on_change=on_checkbox_change)

    active_temp_years = [y for y in all_years if str_module.session_state.get(f"setup_year_{y}", True)]
    
    str_module.markdown("---")

    total_possible_combinations = 0
    for y in active_temp_years:
        for t in TEAMS_LIST:
            if get_draft_tokyo_team_names(t, y) is not None:
                total_possible_combinations += 1

    max_possible_trials = total_required_drafts if max_skips_val == float("inf") else (total_required_drafts + max_skips_val)

    str_module.info(f"📊 選択された年度の利用可能な総組み合わせ数: **約 {total_possible_combinations} 回** (選択年数: {len(active_temp_years)}年)")

    can_start = True
    if len(active_temp_years) == 0:
        str_module.error("⚠️ エラー: 対象年度が1つも選択されていません。")
        can_start = False
    elif no_duplicate_lottery and max_possible_trials > total_possible_combinations:
        str_module.error(f"⚠️ エラー: 必要人数＋スキップ上限の合計が、選択された年度の最大組み合わせ数を超えています！")
        can_start = False

    if str_module.button("🚀 この設定でゲームスタート！", type="primary", use_container_width=True, disabled=not can_start):
        str_module.session_state.selected_years = active_temp_years
        str_module.session_state.max_skips = max_skips_val
        str_module.session_state.no_duplicate_lottery = no_duplicate_lottery
        str_module.session_state.config_num_starting = num_starting
        str_module.session_state.config_num_relief = num_relief
        str_module.session_state.config_num_closer = num_closer
        str_module.session_state.config_num_batters = total_batters
        str_module.session_state.max_drafts = total_required_drafts
        
        str_module.session_state.game_started = True
        str_module.session_state.draft_count = 0
        str_module.session_state.skip_count = 0
        str_module.session_state.my_team = {"batters": [], "pitchers": []}
        str_module.session_state.current_lottery = None
        str_module.session_state.used_lotteries = set()
        str_module.rerun()

# =====================================================================
# 6. メインゲーム画面
# =====================================================================
else:
    max_skips = str_module.session_state.max_skips
    selected_years = str_module.session_state.selected_years
    max_drafts = str_module.session_state.max_drafts
    no_duplicate_lottery = str_module.session_state.no_duplicate_lottery

    num_starting = str_module.session_state.config_num_starting
    num_relief = str_module.session_state.config_num_relief
    num_closer = str_module.session_state.config_num_closer
    num_batters = str_module.session_state.config_num_batters

    all_defensive_positions = ["捕手", "一塁手", "二塁手", "三塁手", "遊撃手", "左翼手", "中堅手", "右翼手", "指名打者"]

    str_module.sidebar.title("📋 メニュー")
    if str_module.sidebar.button("⚙️ 設定を変更してやり直す", use_container_width=True):
        str_module.session_state.game_started = False
        str_module.rerun()

    str_module.title("⚾ ドラフト×ドラフト")
    str_module.markdown(f"選択中年度: <code>{min(selected_years)} 〜 {max(selected_years)} ({len(selected_years)}年間)</code>", unsafe_allow_html=True)

    col_sub, col_main = str_module.columns([1, 1.2])

    with col_sub:
        str_module.subheader("🏟️ チーム編成ボード")

        # 野手陣セクション
        str_module.markdown(f"**【野手陣 ({len(str_module.session_state.my_team['batters'])} / {num_batters}人)】**")
        
        batter_template_roles = [str(i) for i in range(1, 10)]
        bench_count = max(0, num_batters - 9)
        for i in range(1, bench_count + 1):
            if bench_count == 1:
                batter_template_roles.append("控")
            else:
                batter_template_roles.append(f"控{i}")

        existing_batters_dict = {b["打順/役割"]: b for b in str_module.session_state.my_team["batters"]}
        
        for target_role in batter_template_roles:
            if target_role in existing_batters_dict:
                b = existing_batters_dict[target_role]
                pos_short = get_position_short_name(b["守備位置"]) if b["守備位置"] != "---" else "-"
                str_module.markdown(
                    f"- <code>{target_role}</code> : **{b['選手名']}** "
                    f"(`{pos_short}`) <span style='color:gray; font-size:12px;'>({b['出自']})</span>",
                    unsafe_allow_html=True
                )
            else:
                str_module.markdown(
                    f"- <code>{target_role}</code> : <span style='color:gray;'>未選択 (---)</span>",
                    unsafe_allow_html=True
                )

        str_module.markdown("---")

        # 投手陣セクション
        total_pitcher_slots = num_starting + num_relief + num_closer
        str_module.markdown(f"**【投手陣 ({len(str_module.session_state.my_team['pitchers'])} / {total_pitcher_slots}人)】**")
        
        pitcher_template_roles = []
        for i in range(1, num_starting + 1): 
            pitcher_template_roles.append("先" if num_starting == 1 else f"先{i}")
        for i in range(1, num_relief + 1): 
            pitcher_template_roles.append("継" if num_relief == 1 else f"継{i}")
        for i in range(1, num_closer + 1): 
            pitcher_template_roles.append("抑" if num_closer == 1 else f"抑{i}")

        pitchers_by_role = {"先発": [], "中継ぎ": [], "抑え": []}
        for p in str_module.session_state.my_team["pitchers"]:
            if p["起用法"] in pitchers_by_role:
                pitchers_by_role[p["起用法"]].append(p)

        s_idx, r_idx, c_idx = 0, 0, 0
        for target_role in pitcher_template_roles:
            assigned_player = None
            if target_role.startswith("先") and s_idx < len(pitchers_by_role["先発"]):
                assigned_player = pitchers_by_role["先発"][s_idx]; s_idx += 1
            elif target_role.startswith("継") and r_idx < len(pitchers_by_role["中継ぎ"]):
                assigned_player = pitchers_by_role["中継ぎ"][r_idx]; r_idx += 1
            elif target_role.startswith("抑") and c_idx < len(pitchers_by_role["抑え"]):
                assigned_player = pitchers_by_role["抑え"][c_idx]; c_idx += 1

            if assigned_player:
                str_module.markdown(
                    f"- <code>{target_role}</code> : **{assigned_player['選手名']}** "
                    f"(`投`) <span style='color:gray; font-size:12px;'>({assigned_player['出自']})</span>",
                    unsafe_allow_html=True
                )
            else:
                str_module.markdown(
                    f"- <code>{target_role}</code> : <span style='color:gray;'>未選択 (---)</span>",
                    unsafe_allow_html=True
                )

    with col_main:
        str_module.progress(str_module.session_state.draft_count / max_drafts)
        str_module.write(f"**指名完了数: {str_module.session_state.draft_count} / {max_drafts} 回**")

        if max_skips != float("inf"):
            remaining_skips = max(0, max_skips - str_module.session_state.skip_count)
            str_module.write(f"スキップ残回数: **{remaining_skips} / {max_skips} 回**")
        else:
            str_module.write(f"スキップ残回数: **無制限 (現在 {str_module.session_state.skip_count} 回使用)**")

        all_possible_pool = []
        for y in selected_years:
            for t in TEAMS_LIST:
                if get_draft_tokyo_team_names(t, y) is not None:
                    all_possible_pool.append((t, y))

        if no_duplicate_lottery:
            active_pool = [item for item in all_possible_pool if item not in str_module.session_state.used_lotteries]
        else:
            active_pool = all_possible_pool

        if str_module.session_state.draft_count >= max_drafts:
            str_module.success("🎉 すべてのドラフト指名が完了しました！お疲れ様でした！")
            if str_module.button("もう一度最初から設定し直す", use_container_width=True):
                str_module.session_state.game_started = False
                str_module.rerun()
        elif no_duplicate_lottery and not active_pool:
            str_module.warning("⚠️ 選択された年度内のすべての球団ドラフトをすでに引き切りました！")
        else:
            c1, c2 = str_module.columns(2)
            with c1:
                is_lottery_disabled = (str_module.session_state.current_lottery is not None)
                if str_module.button("🎲 抽選する（球団 ＆ 年）", type="primary", disabled=is_lottery_disabled, use_container_width=True):
                    chosen_team, chosen_year = random.choice(active_pool)
                    names = get_draft_tokyo_team_names(chosen_team, chosen_year)
                    actual_team_name = names[0] if names else chosen_team
                    
                    fetched_players = fetch_draft_tokyo_data(chosen_team, chosen_year)
                    
                    str_module.session_state.current_lottery = {
                        "team": chosen_team,
                        "actual_team_name": actual_team_name,
                        "year": chosen_year,
                        "players": fetched_players
                    }
                    if no_duplicate_lottery:
                        str_module.session_state.used_lotteries.add((chosen_team, chosen_year))
                    str_module.rerun()
            with c2:
                is_skip_disabled = (str_module.session_state.current_lottery is None) or (str_module.session_state.skip_count >= max_skips) or (no_duplicate_lottery and len(active_pool) == 0)
                skip_button_label = "🔄 スキップ（引き直す）"
                if str_module.session_state.skip_count >= max_skips:
                    skip_button_label = "🚫 スキップ上限に達しました"

                if str_module.button(skip_button_label, disabled=is_skip_disabled, use_container_width=True):
                    if str_module.session_state.skip_count < max_skips and (not no_duplicate_lottery or active_pool):
                        if no_duplicate_lottery and str_module.session_state.current_lottery:
                            current_t = str_module.session_state.current_lottery["team"]
                            current_y = str_module.session_state.current_lottery["year"]
                            str_module.session_state.used_lotteries.add((current_t, current_y))

                        updated_active_pool = [item for item in all_possible_pool if item not in str_module.session_state.used_lotteries] if no_duplicate_lottery else all_possible_pool
                        
                        if not no_duplicate_lottery or updated_active_pool:
                            str_module.session_state.skip_count += 1
                            chosen_team, chosen_year = random.choice(updated_active_pool)
                            names = get_draft_tokyo_team_names(chosen_team, chosen_year)
                            actual_team_name = names[0] if names else chosen_team
                            
                            fetched_players = fetch_draft_tokyo_data(chosen_team, chosen_year)
                                
                            str_module.session_state.current_lottery = {
                                "team": chosen_team,
                                "actual_team_name": actual_team_name,
                                "year": chosen_year,
                                "players": fetched_players
                            }
                            if no_duplicate_lottery:
                                str_module.session_state.used_lotteries.add((chosen_team, chosen_year))
                            str_module.rerun()

        if str_module.session_state.current_lottery:
            lottery = str_module.session_state.current_lottery
            
            str_module.info(f"✨ 抽選結果： **{lottery['year']}年** の **{lottery['actual_team_name']}** が選ばれました！")
            
            if not lottery["players"]:
                str_module.warning("⚠️ この年のデータが取得できませんでした。別のボタンで引き直してください。")
            else:
                str_module.subheader("📋 指名候補選手一覧")
                display_players = [
                    {
                        "順位": p["rank_str"], 
                        "選手名": p["name"], 
                        "守備": p["pos"], 
                        "区分": p["status"]
                    } for p in lottery["players"]
                ]
                players_df = pd.DataFrame(display_players)
                
                def highlight_special_status(row):
                    status = lottery["players"][row.name]["status"]
                    if status != "入団":
                        return ['color: #888888; background-color: #f1f5f9'] * len(row)
                    return [''] * len(row)

                styled_df = players_df.style.apply(highlight_special_status, axis=1)
                str_module.dataframe(styled_df, use_container_width=True, hide_index=True, height=min(400, 38 + len(players_df) * 35))
                
                str_module.subheader("✍️ 選手を指名して役割を決定する")
                role_type = str_module.radio("選手タイプを選択してください", ["野手", "投手"], horizontal=True, key="role_type_radio")
                
                current_batters_count = len(str_module.session_state.my_team["batters"])
                current_starting_count = sum(1 for p in str_module.session_state.my_team["pitchers"] if p["起用法"] == "先発")
                current_relief_count = sum(1 for p in str_module.session_state.my_team["pitchers"] if p["起用法"] == "中継ぎ")
                current_closer_count = sum(1 for p in str_module.session_state.my_team["pitchers"] if p["起用法"] == "抑え")
                
                player_options = {f"[{p['category']}] {p['rank_str']}: {p['name']} ({p['pos']} / {p['status']})": p for p in lottery["players"]}
                selected_key = str_module.selectbox("指名する選手を選択", options=list(player_options.keys()))
                
                assigned_bat_role = ""
                assigned_pos = "-"
                assigned_pitcher_role = ""
                
                if role_type == "野手":
                    if current_batters_count >= num_batters:
                        str_module.warning("⚠️ 野手枠はすでに満員です！")
                    
                    available_batter_roles = []
                    for i in range(1, 10):
                        role_name = str(i)
                        if not any(b["打順/役割"] == role_name for b in str_module.session_state.my_team["batters"]):
                            available_batter_roles.append(role_name)
                    
                    bench_max = max(0, num_batters - 9)
                    for i in range(1, bench_max + 1):
                        role_name = f"控{'①②③④⑤⑥⑦⑧⑨⑩'[i-1] if i <= 10 else i}"
                        if not any(b["打順/役割"] == role_name for b in str_module.session_state.my_team["batters"]):
                            available_batter_roles.append(role_name)
                            
                    assigned_bat_role = str_module.selectbox("打順・役割を選択", options=available_batter_roles if available_batter_roles else ["満員"])
                    
                    if "控" in assigned_bat_role:
                        assigned_pos = "---"
                    else:
                        used_positions = [b["守備位置"] for b in str_module.session_state.my_team["batters"] if b["守備位置"] != "---"]
                        available_positions = [pos for pos in all_defensive_positions if pos not in used_positions]
                        assigned_pos = str_module.selectbox("守備ポジションを選択", options=available_positions if available_positions else ["すべてのポジションが埋まっています"])
                else:
                    available_pitcher_types = []
                    if current_starting_count < num_starting: available_pitcher_types.append("先発")
                    if current_relief_count < num_relief: available_pitcher_types.append("中継ぎ")
                    if current_closer_count < num_closer: available_pitcher_types.append("抑え")
                    assigned_pitcher_role = str_module.selectbox("投手起用法を選択", options=available_pitcher_types if available_pitcher_types else ["満員"])
                
                if str_module.button("この選手を決定して登録！", type="primary", use_container_width=True):
                    chosen_player = player_options[selected_key]
                    if role_type == "野手" and (current_batters_count >= num_batters or assigned_bat_role == "満員" or (not "控" in assigned_bat_role and assigned_pos == "すべてのポジションが埋まっています")):
                        str_module.error("野手枠が上限に達しているか、選べる打順・ポジションがありません。")
                    elif role_type == "投手" and assigned_pitcher_role == "満員":
                        str_module.error("選べる投手起用法枠がありません。")
                    else:
                        short_team_name = get_short_team_name(lottery['actual_team_name'], lottery['year'])
                        y_str = str(lottery['year'])[-2:]
                        origin_text = f"'{y_str} {short_team_name}・{chosen_player['rank_str']}"
                        
                        if role_type == "野手":
                            str_module.session_state.my_team["batters"].append({"打順/役割": assigned_bat_role, "守備位置": assigned_pos, "選手名": chosen_player["name"], "出自": origin_text})
                        else:
                            str_module.session_state.my_team["pitchers"].append({"起用法": assigned_pitcher_role, "選手名": chosen_player["name"], "出自": origin_text})
                        
                        str_module.session_state.draft_count += 1
                        str_module.session_state.current_lottery = None
                        str_module.success(f"{chosen_player['name']} 選手を指名しました！")
                        str_module.rerun()
