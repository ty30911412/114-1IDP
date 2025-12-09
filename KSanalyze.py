import pandas as pd
import os

# ================= 設定區 =================
# 來源檔案
FILE_QUANTIFIED = '/Users/xian/R project/114-1IDP/Analysis_KIST_Standard.csv'

# 輸出檔名
OUT_OVERALL = '1_KIST_Overall_Stats_v2.csv'
OUT_SCHOOL = '2_KIST_School_Comparison_v2.csv'
OUT_ROLE = '3_KIST_Role_Comparison_v2.csv'
# =========================================

def generate_stats_report(df, group_col, value_cols):
    """
    產生包含平均數與樣本數的統計報表
    """
    # 1. 計算各組的樣本數 (N)
    # 使用 '教師姓名' 來計數，如果沒有姓名欄位則計算列數
    if '教師姓名' in df.columns:
        counts = df.groupby(group_col)['教師姓名'].count()
    else:
        counts = df.groupby(group_col).size()
        
    # 2. 計算各組在各指標的平均數 (Mean)
    means = df.groupby(group_col)[value_cols].mean().T
    
    # 3. 將樣本數合併進去 (作為第一列)
    # 為了讓 N 顯示在最上面，我們先建立一個 DataFrame
    counts_df = pd.DataFrame(counts).T
    counts_df.index = ['有效樣本數 (N)']
    
    # 合併 (樣本數 row + 平均數 rows)
    final_report = pd.concat([counts_df, means])
    
    return final_report

def main():
    # 1. 讀取資料
    if not os.path.exists(FILE_QUANTIFIED):
        print(f"錯誤：找不到檔案 '{FILE_QUANTIFIED}'")
        return

    print(f"正在讀取 {FILE_QUANTIFIED} ...")
    df_all = pd.read_csv(FILE_QUANTIFIED)
    
    # 2. 資料過濾：只保留 KIST 標準體系 (排除樟湖)
    df = df_all[~df_all['School_Name'].str.contains('樟湖', na=False)].copy()
    print(f"KIST 體系原始樣本數: {len(df)}")

    # 3. 身份類別合併 (Data Transformation)
    # 將 '熟手教師' 和 '資深教師(3y+)' 合併為 '熟手/資深教師'
    # 注意：這裡使用 replace 來進行模糊匹配或精確替換
    target_roles = ['熟手教師', '資深教師(3y+)']
    new_role_name = '熟手/資深教師'
    
    # 檢查原始資料中有哪些相關標籤
    current_roles = df['Role_Tag'].unique()
    print(f"原始身份標籤: {current_roles}")
    
    # 執行合併
    df['Role_Tag'] = df['Role_Tag'].replace(target_roles, new_role_name)
    
    # 再次確認
    print(f"合併後身份標籤: {df['Role_Tag'].unique()}")

    # 4. 識別數值型指標欄位
    meta_cols = ['School_Name', 'Role_Tag', '教師姓名', '職位', '科目', 'Source_File']
    numeric_cols = [c for c in df.columns if c not in meta_cols and pd.api.types.is_numeric_dtype(df[c])]
    print(f"識別出 {len(numeric_cols)} 個教學力指標。")

    # ==========================================
    # 分析一：總體診斷 (Descriptive Stats)
    # ==========================================
    print("\n[1/3] 計算總體診斷...")
    overall_stats = df[numeric_cols].describe().T[['count', 'mean', 'std', 'min', 'max']]
    overall_stats.columns = ['有效樣本數', '平均數', '標準差', '最小值', '最大值']
    overall_stats = overall_stats.sort_values(by='平均數', ascending=False)
    overall_stats.to_csv(OUT_OVERALL, encoding='utf-8-sig')
    print(f"-> 已輸出: {OUT_OVERALL}")

    # ==========================================
    # 分析二：校際比較 (School Comparison)
    # ==========================================
    print("\n[2/3] 計算校際比較 (含樣本數)...")
    if 'School_Name' in df.columns:
        school_report = generate_stats_report(df, 'School_Name', numeric_cols)
        school_report.to_csv(OUT_SCHOOL, encoding='utf-8-sig')
        print(f"-> 已輸出: {OUT_SCHOOL}")
        
        # 顯示各校樣本數供確認
        print("   各校樣本分佈:")
        print(school_report.loc['有效樣本數 (N)'])

    # ==========================================
    # 分析三：身份比較 (Role Comparison)
    # ==========================================
    print("\n[3/3] 計算身份比較 (含樣本數)...")
    if 'Role_Tag' in df.columns:
        role_report = generate_stats_report(df, 'Role_Tag', numeric_cols)
        role_report.to_csv(OUT_ROLE, encoding='utf-8-sig')
        print(f"-> 已輸出: {OUT_ROLE}")
        
        # 顯示各身份樣本數供確認
        print("   各身份樣本分佈:")
        print(role_report.loc['有效樣本數 (N)'])

    print("\n" + "="*30)
    print("所有分析完成！")

if __name__ == "__main__":
    main()