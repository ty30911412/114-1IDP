import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm
import os

# ================= 設定區 =================
# 輸入檔案 (來自上一步分流的結果)
FILE_ZHANGHU = 'Analysis_Zhanghu_Teachers.csv'
FILE_KIST = 'Analysis_KIST_Standard.csv'

# 指定您的字體檔案路徑
FONT_PATH = '/Users/xian/R project/114-1IDP/jf-openhuninn-2.1.ttf'
# =========================================

def set_chinese_font():
    """
    直接載入使用者指定的字體檔案，解決中文亂碼問題
    """
    # 檢查字體檔案是否存在
    if os.path.exists(FONT_PATH):
        # 加入字體管理器
        fm.fontManager.addfont(FONT_PATH)
        
        # 取得字體名稱
        font_prop = fm.FontProperties(fname=FONT_PATH)
        font_name = font_prop.get_name()
        
        # 設定全域字體
        plt.rcParams['font.sans-serif'] = [font_name]
        plt.rcParams['axes.unicode_minus'] = False # 讓負號正常顯示
        
        print(f"✅ 已成功載入字體: {font_name} (來自 {FONT_PATH})")
        return font_prop
    else:
        print(f"⚠️ 警告: 找不到字體檔案 '{FONT_PATH}'")
        print("將嘗試使用系統預設字體，可能會出現亂碼。")
        plt.rcParams['axes.unicode_minus'] = False
        return None

def draw_beautiful_heatmap(data_df, index_col, title, output_filename):
    """
    核心繪圖函數：繪製美觀、不擁擠的熱力圖
    """
    # 1. 資料準備
    metric_cols = data_df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    
    if not metric_cols or index_col not in data_df.columns:
        print(f"跳過繪製 {title}：資料不足或索引欄位不存在。")
        return

    # 依指定欄位分群計算平均值
    plot_data = data_df.set_index(index_col)[metric_cols]
    if plot_data.index.duplicated().any():
         plot_data = plot_data.groupby(level=0).mean()
         
    # 2. 動態計算畫布大小
    n_rows, n_cols = plot_data.shape
    # 樟湖的指標較多，我們可以把寬度係數調大一點
    figsize_w = max(12, 6 + n_cols * 0.8) 
    figsize_h = max(8, 4 + n_rows * 0.6)
    
    plt.figure(figsize=(figsize_w, figsize_h))

    # 3. 設定配色
    cmap = sns.diverging_palette(15, 145, as_cmap=True, sep=2, s=85, l=60, center='light')

    # 4. 繪製熱力圖
    ax = sns.heatmap(plot_data, 
                     cmap=cmap, 
                     annot=True,       
                     fmt='.1f',        
                     linewidths=1.5,   
                     linecolor='white',
                     cbar_kws={'label': '平均分數 (1-5)', 'shrink': 0.8}, 
                     vmin=1.0, vmax=5.0,
                     center=3.0        
                    )

    # 5. 調整標籤與標題 (確保字體大小適中)
    # X軸標籤旋轉 45 度並靠右對齊
    plt.xticks(rotation=45, ha='right', fontsize=12, fontweight='medium')
    plt.yticks(fontsize=12)
    
    plt.title(title, fontsize=20, pad=30, fontweight='bold')
    plt.xlabel('', fontsize=12) 
    plt.ylabel(index_col, fontsize=14, fontweight='bold')
    
    # 調整佈局
    plt.tight_layout()
    
    # 儲存圖片
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"✅ 優化圖表已輸出: {output_filename}")
    plt.close() 

def main():
    # 設定字體
    set_chinese_font()
    
    # 設定 Seaborn 風格 (需在字體設定後)
    sns.set_theme(style="whitegrid", font=plt.rcParams['font.sans-serif'][0])

    print("開始繪製優化版熱力圖...")

    # 1. 繪製 KIST 標準體系
    try:
        df_kist = pd.read_csv(FILE_KIST)
        print(f"\n讀取 KIST 資料成功 (n={len(df_kist)})")
        draw_beautiful_heatmap(
            data_df=df_kist,
            index_col='School_Name', 
            title='KIST 標準體系 - 各校教學力平均表現',
            output_filename='Beautiful_Heatmap_KIST.png'
        )
    except FileNotFoundError:
        print(f"找不到 {FILE_KIST}，請先執行分流腳本。")

    # 2. 繪製 樟湖體系
    try:
        df_zh = pd.read_csv(FILE_ZHANGHU)
        print(f"\n讀取 樟湖 資料成功 (n={len(df_zh)})")
        
        # 匿名化處理 (可選)
        # df_zh['教師姓名'] = df_zh['教師姓名'].astype(str).str[0] + "老師"

        draw_beautiful_heatmap(
            data_df=df_zh,
            index_col='教師姓名', 
            title='樟湖實驗中學 - 教師教學力指標表現',
            output_filename='Beautiful_Heatmap_Zhanghu.png'
        )
    except FileNotFoundError:
        print(f"找不到 {FILE_ZHANGHU}，請先執行分流腳本。")

if __name__ == "__main__":
    main()