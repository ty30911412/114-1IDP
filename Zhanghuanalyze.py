import pandas as pd
import os

# ================= 設定區 =================
# 來源檔案優先順序
FILE_ZHANGHU_SPLIT = 'Analysis_Zhanghu_Teachers.csv'
FILE_QUANTIFIED = '_Teaching_Ability_Quantified.csv'

# 輸出檔名
OUTPUT_FILE = 'Zhanghu_Overall_Stats.csv'
# =========================================

def main():
    df = None
    
    # 1. 智慧讀取資料
    if os.path.exists(FILE_ZHANGHU_SPLIT):
        print(f"正在讀取分流檔 {FILE_ZHANGHU_SPLIT}...")
        df = pd.read_csv(FILE_ZHANGHU_SPLIT)
    elif os.path.exists(FILE_QUANTIFIED):
        print(f"找不到分流檔，正在從總表 {FILE_QUANTIFIED} 提取樟湖資料...")
        df_all = pd.read_csv(FILE_QUANTIFIED)
        
        # 篩選邏輯：學校包含'樟湖' 且 角色不是'行政人員'
        df = df_all[
            (df_all['School_Name'].str.contains('樟湖', na=False)) & 
            (df_all['Role_Tag'] != '行政人員')
        ].copy()
        
        # 關鍵步驟：刪除所有「完全空白」的欄位 (這樣會自動移除 KIST 的標準指標)
        df.dropna(axis=1, how='all', inplace=True)
    else:
        print("錯誤：找不到任何可用的數據檔案。")
        return

    # 2. 確認樣本數
    print(f"分析樣本數: {len(df)} 位樟湖教師")

    # 3. 識別數值型指標欄位
    meta_cols = ['School_Name', 'Role_Tag', '教師姓名', '職位', '科目', 'Source_File']
    # 篩選出數值型欄位
    numeric_cols = [c for c in df.columns if c not in meta_cols and pd.api.types.is_numeric_dtype(df[c])]
    
    print(f"共識別出 {len(numeric_cols)} 個樟湖專屬指標。")

    if len(numeric_cols) == 0:
        print("警告：找不到任何數值指標，請檢查來源檔案是否正確。")
        return

    # 4. 執行描述性統計 (Descriptive Stats)
    print("\n正在計算統計數據...")
    
    # describe() 函數一次算出 count, mean, std, min, max 等
    stats = df[numeric_cols].describe().T[['count', 'mean', 'std', 'min', 'max']]
    
    # 重新命名欄位，使其更直觀
    stats.columns = ['有效樣本數', '平均數', '標準差', '最小值', '最大值']
    
    # 依照平均分數由高到低排序
    stats = stats.sort_values(by='平均數', ascending=False)
    
    # 5. 輸出結果
    stats.to_csv(OUTPUT_FILE, encoding='utf-8-sig')
    
    print("-" * 30)
    print(f"分析完成！報表已輸出至: {OUTPUT_FILE}")
    print("-" * 30)
    print("【前 5 名強項指標】")
    print(stats.head(5)[['平均數', '標準差']])
    print("\n【後 5 名待加強指標】")
    print(stats.tail(5)[['平均數', '標準差']])

if __name__ == "__main__":
    main()