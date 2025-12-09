import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import platform

# ================= 設定區 =================
INPUT_FILENAME = '_Teaching_Ability_Quantified.csv' # 上一步產出的量化檔案
# =========================================

def set_chinese_font():
    """設定中文字體，確保圖表顯示正常"""
    system = platform.system()
    if system == 'Windows':
        plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
    elif system == 'Darwin':  # macOS
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
    else:
        plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei']
    plt.rcParams['axes.unicode_minus'] = False

def main():
    # 1. 讀取檔案
    try:
        df = pd.read_csv(INPUT_FILENAME)
        print(f"成功讀取總表，共 {len(df)} 筆資料。")
    except FileNotFoundError:
        print(f"錯誤：找不到檔案 '{INPUT_FILENAME}'")
        return

    # 2. 定義切割邏輯
    # 樟湖體系：學校名稱包含 "樟湖"
    # KIST 標準體系：學校名稱不包含 "樟湖"
    
    # === A. 處理樟湖體系 ===
    print("\n[處理中] 正在分離樟湖體系資料...")
    df_zhanghu = df[df['School_Name'].str.contains('樟湖', na=False)].copy()
    
    # 過濾掉行政人員 (假設 Role_Tag 或 職位 欄位有標示)
    # 先確認有哪些角色
    print(f"樟湖原始人數: {len(df_zhanghu)}")
    print("樟湖角色分佈:", df_zhanghu['Role_Tag'].unique())
    
    # 執行排除: 排除 Role_Tag 為 "行政人員" 的資料
    # 注意：如果您的 Role_Tag 是從檔名來的，請確認是否為 "行政人員"
    df_zhanghu_teachers = df_zhanghu[df_zhanghu['Role_Tag'] != '行政人員'].copy()
    print(f"排除行政人員後人數: {len(df_zhanghu_teachers)}")
    
    # 清洗欄位: 刪除所有 "全為空值" 的欄位 (這樣就會自動把 KIST 的指標刪掉)
    df_zhanghu_teachers.dropna(axis=1, how='all', inplace=True)
    
    # 輸出樟湖檔案
    df_zhanghu_teachers.to_csv('Analysis_Zhanghu_Teachers.csv', index=False, encoding='utf-8-sig')
    print("-> 已輸出: Analysis_Zhanghu_Teachers.csv")

    # === B. 處理 KIST 標準體系 ===
    print("\n[處理中] 正在分離 KIST 標準體系資料...")
    df_kist = df[~df['School_Name'].str.contains('樟湖', na=False)].copy()
    print(f"KIST 體系人數: {len(df_kist)}")
    
    # 清洗欄位: 刪除所有 "全為空值" 的欄位 (這樣就會自動把樟湖的指標刪掉)
    df_kist.dropna(axis=1, how='all', inplace=True)
    
    # 輸出 KIST 檔案
    df_kist.to_csv('Analysis_KIST_Standard.csv', index=False, encoding='utf-8-sig')
    print("-> 已輸出: Analysis_KIST_Standard.csv")
    
    # 3. 產生簡單的統計摘要 (確認分流是否成功)
    
    # 找出數值欄位
    zh_metric_cols = df_zhanghu_teachers.select_dtypes(include=['float64', 'int64']).columns.tolist()
    kist_metric_cols = df_kist.select_dtypes(include=['float64', 'int64']).columns.tolist()
    
    print("\n" + "="*30)
    print("【分流分析摘要】")
    print("="*30)
    
    print(f"\n1. 樟湖體系 (n={len(df_zhanghu_teachers)})")
    print(f"   保留指標數: {len(zh_metric_cols)} 個")
    if len(zh_metric_cols) > 0:
        print("   指標範例: ", zh_metric_cols[:3])
        print("   平均表現 Top 3:")
        print(df_zhanghu_teachers[zh_metric_cols].mean().nlargest(3))
        
    print(f"\n2. KIST 標準體系 (n={len(df_kist)})")
    print(f"   保留指標數: {len(kist_metric_cols)} 個")
    if len(kist_metric_cols) > 0:
        print("   指標範例: ", kist_metric_cols[:3])
        print("   平均表現 Top 3:")
        print(df_kist[kist_metric_cols].mean().nlargest(3))

    # 4. (選用) 繪製獨立的熱力圖
    # 既然分開了，就各自畫一張圖，這樣指標名稱才不會擠在一起
    set_chinese_font()
    
    # 畫 KIST 的
    if len(kist_metric_cols) > 0:
        plt.figure(figsize=(12, 8))
        kist_school_stats = df_kist.groupby('School_Name')[kist_metric_cols].mean()
        sns.heatmap(kist_school_stats.T, cmap='RdYlGn', annot=True, fmt='.1f')
        plt.title('KIST 標準體系 - 各校教學力表現', fontsize=14)
        plt.tight_layout()
        plt.savefig('Heatmap_KIST_Standard.png', dpi=300)
        print("\n-> 圖表已輸出: Heatmap_KIST_Standard.png")

    # 畫 樟湖 的 (因為只有一間學校，我們可以改畫 "個人" 或 "平均")
    if len(zh_metric_cols) > 0:
        plt.figure(figsize=(8, 6))
        # 因為只有一間學校，我們畫全校平均的長條圖可能比較適合，或者畫個人的熱力圖
        # 這裡示範畫個人的熱力圖 (因為人少，可以看個別差異)
        df_zh_viz = df_zhanghu_teachers.set_index('教師姓名')[zh_metric_cols]
        sns.heatmap(df_zh_viz, cmap='RdYlGn', annot=True, fmt='.1f')
        plt.title('樟湖體系 - 教師個別教學力表現', fontsize=14)
        plt.tight_layout()
        plt.savefig('Heatmap_Zhanghu_Teachers.png', dpi=300)
        print("-> 圖表已輸出: Heatmap_Zhanghu_Teachers.png")

if __name__ == "__main__":
    main()