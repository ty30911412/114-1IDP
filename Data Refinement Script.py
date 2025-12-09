import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm
import re
import os

# ================= 設定區 (User Config) =================
INPUT_FILE = '114_IDP_Master_Merged.csv'
OUTPUT_STATS_FILE = '114_IDP_Demographics_Report_v2.xlsx' # 輸出檔名更新
OUTPUT_HEATMAP_FILE = '114_IDP_SchoolLevel_Heatmap_v2.png'
FONT_PATH = '/Users/xian/R project/114-1IDP/jf-openhuninn-2.1.ttf'

# 【修改點 1】: 角色標準化邏輯 - 簡化版
# 策略：暫時不區分年資，統一歸類為「一般教師」，僅保留行政職的分野
ROLE_MAPPING = {
    # 教學類 - 全部歸一
    '新進教師': '一般教師 (待年資核對)',
    '初任教師(1-3y)': '一般教師 (待年資核對)',
    '熟手教師': '一般教師 (待年資核對)',
    '資深教師(3y+)': '一般教師 (待年資核對)',
    '一般教師': '一般教師 (待年資核對)', 
    
    # 行政/領導類 (建議仍分開，因為問卷維度可能不同，若要全合併可改為 '一般教師')
    '行政人員': '行政/領導',
    '教師領導人': '行政/領導',
    '主任': '行政/領導',
    '校長': '行政/領導'
}

# 學校層級定義
SCHOOL_LEVEL_MAP = {
    '三民國小': '1.國小',
    '仙草實小': '1.國小',
    '老梅實小': '1.國小',
    '拯民國小': '1.國小',
    '樟湖生態國中小': '2.國中小',
    '三民國中': '3.國中',
    '坪林實中': '3.國中',
    '峨眉國中': '3.國中'
}
# ======================================================

def set_chinese_font():
    if os.path.exists(FONT_PATH):
        fm.fontManager.addfont(FONT_PATH)
        font_name = fm.FontProperties(fname=FONT_PATH).get_name()
        plt.rcParams['font.sans-serif'] = [font_name]
        plt.rcParams['axes.unicode_minus'] = False
        print(f"✅ 字體載入成功: {font_name}")
    else:
        print(f"⚠️ 警告: 找不到字體 {FONT_PATH}")

def extract_score(text):
    if pd.isna(text) or not isinstance(text, str):
        return np.nan
    if '階段' in text:
        if '階段五' in text: return 5.0
        if '階段四' in text: return 4.0
        if '階段三' in text: return 3.0
        if '階段二' in text: return 2.0
        if '階段一' in text: return 1.0
    match = re.search(r'Level\s*(\d)', text, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return np.nan

def process_data():
    print(f"正在讀取資料: {INPUT_FILE} ...")
    if not os.path.exists(INPUT_FILE):
        print(f"❌ 錯誤: 找不到檔案 {INPUT_FILE}")
        return None

    df = pd.read_csv(INPUT_FILE)

    # 1. 基礎標籤處理
    df['School_Name'] = df['School_Name'].fillna('Unknown')
    df['School_Level'] = df['School_Name'].map(SCHOOL_LEVEL_MAP).fillna('4.其他')
    
    # 套用簡化後的角色分類
    df['Standardized_Role'] = df['Role_Tag'].map(ROLE_MAPPING).fillna('一般教師 (待年資核對)')

    # 【修改點 2】: 產生包含「原始來源檔名」的詳細統計表
    # 這張表可以讓您追溯每個分類下的資料是來自哪個 csv 檔案
    
    # A. 學校概況 (School Summary)
    school_summary = df.groupby(['School_Level', 'School_Name']).size().reset_index(name='實際填答人數')
    school_summary['學校總人數(需手填)'] = np.nan
    school_summary['填答率(%)'] = np.nan
    
    # B. 角色與來源細節 (Detail with Source)
    # 這裡加入 'Source_File' 到 groupby，讓您清楚看到資料來源
    role_source_detail = df.groupby(
        ['School_Level', 'School_Name', 'Standardized_Role', 'Source_File']
    ).size().reset_index(name='人數')
    
    # 輸出報表
    with pd.ExcelWriter(OUTPUT_STATS_FILE) as writer:
        school_summary.to_excel(writer, sheet_name='1.學校填答概況', index=False)
        role_source_detail.to_excel(writer, sheet_name='2.角色與來源細節', index=False)
        # 順便輸出原始資料的一個子集供檢查
        check_df = df[['School_Name', 'Role_Tag', 'Standardized_Role', 'Source_File', '教師姓名']].head(50)
        check_df.to_excel(writer, sheet_name='3.前50筆資料檢查', index=False)
        
    print(f"✅ 統計報表已輸出: {OUTPUT_STATS_FILE}")
    print(f"   (請查看 '2.角色與來源細節' 分頁以確認資料來源檔案)")

    # 3. 資料數值化
    meta_cols = ['Source_File', 'Role_Tag', 'School_Name', 'School_Level', 'Standardized_Role', 
                 '教師姓名', '教師信箱', '學校', '職位', '科目', '提交時間']
    question_cols = [c for c in df.columns if c not in meta_cols]
    
    score_df = df.copy()
    for col in question_cols:
        score_df[col] = score_df[col].apply(extract_score)

    # 4. 準備熱力圖資料
    numeric_cols = score_df[question_cols].select_dtypes(include=[np.number]).columns
    
    # 這邊只取「一般教師 (待年資核對)」來畫熱力圖，避免行政職的數據干擾教學力分析
    # 如果您想看全校平均，可以把下面這行註解掉
    teacher_only_df = score_df[score_df['Standardized_Role'] == '一般教師 (待年資核對)']
    
    if teacher_only_df.empty:
        print("⚠️ 警告: 過濾後沒有教師資料，改用全體資料繪圖。")
        plot_source_df = score_df
    else:
        plot_source_df = teacher_only_df

    heatmap_data = plot_source_df.groupby(['School_Level', 'School_Name'])[numeric_cols].mean()
    school_counts = plot_source_df.groupby('School_Name').size()
    
    heatmap_data = heatmap_data.reset_index()
    heatmap_data = heatmap_data.sort_values(by=['School_Level', 'School_Name'])
    
    heatmap_data['Label'] = heatmap_data.apply(
        lambda x: f"{x['School_Name']}\n(n={school_counts.get(x['School_Name'], 0)})", axis=1
    )
    
    plot_df = heatmap_data.set_index('Label')[numeric_cols]
    plot_df = plot_df.dropna(axis=1, how='all') # 移除全空的指標

    return plot_df

def draw_heatmap(data):
    if data is None or data.empty:
        return

    set_chinese_font()
    
    # 根據資料量調整圖表大小
    plt.figure(figsize=(22, 12)) 
    
    sns.heatmap(data, 
                cmap=sns.diverging_palette(15, 145, as_cmap=True, sep=2, s=85, l=60, center='light'), 
                annot=True, 
                fmt='.1f', 
                linewidths=1, 
                linecolor='white',
                cbar_kws={'label': '平均分數 (1-5)', 'shrink': 0.6},
                vmin=1.0, vmax=5.0, center=3.0)

    plt.title('KIST 各校 [一般教師] 教學力指標表現 (依教育階段排序)', fontsize=24, pad=20, fontweight='bold')
    plt.ylabel('學校 (樣本數)', fontsize=16)
    plt.xlabel('', fontsize=16)
    plt.xticks(rotation=45, ha='right', fontsize=12)
    plt.yticks(rotation=0, fontsize=14) # 讓Y軸文字水平顯示比較好讀
    
    plt.tight_layout()
    plt.savefig(OUTPUT_HEATMAP_FILE, dpi=300)
    print(f"✅ 熱力圖已輸出: {OUTPUT_HEATMAP_FILE}")

if __name__ == "__main__":
    plot_data = process_data()
    draw_heatmap(plot_data)