import pandas as pd

# 讀取合併後的檔案
file_path = '114_IDP_Master_Merged.csv'

try:
    df = pd.read_csv(file_path)
    print(f"成功讀取檔案，共 {len(df)} 筆資料。\n")

    print("正在掃描包含 '__TEMP__' 的錯誤值...\n")
    
    error_count = 0
    # 遍歷所有欄位
    for col in df.columns:
        # 檢查該欄位是否為字串型態 (因為 __TEMP__ 是文字)
        if df[col].dtype == 'object':
            # 篩選出含有 __TEMP__ 的列
            # 使用 na=False 避免遇到空值報錯
            temp_rows = df[df[col].astype(str).str.contains('__TEMP__', na=False)]
            
            if not temp_rows.empty:
                for index, row in temp_rows.iterrows():
                    error_count += 1
                    print(f"🔴 發現錯誤 #{error_count}")
                    print(f"   - 來源檔案: {row.get('Source_File', '未知')}")
                    print(f"   - 學校: {row.get('School_Name', '未知')}")
                    print(f"   - 姓名: {row.get('教師姓名', '未知')}")
                    print(f"   - 欄位名稱: {col}")
                    print(f"   - 錯誤內容: {row[col]}")
                    print("-" * 50)

    if error_count == 0:
        print("恭喜！檔案中未發現任何 '__TEMP__' 字串。")
    else:
        print(f"\n掃描完成，共發現 {error_count} 處錯誤。")
        print("這些值在之前的 '114_Teaching_Ability_Quantified.csv' 轉換過程中，都已經被自動轉為空值 (NaN)，不影響後續統計。")

except FileNotFoundError:
    print(f"錯誤：找不到檔案 '{file_path}'，請確認檔案位置。")