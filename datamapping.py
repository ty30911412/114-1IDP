import pandas as pd
import os
import re
import glob

# =================設定區=================
# 資料夾路徑 (請確保您的 CSV 檔案都放在這個資料夾內)
SOURCE_FOLDER = '/Users/xian/R project/114-1IDP' 
# 輸出的檔案名稱
OUTPUT_FILENAME = '114_IDP_Master_Merged.csv'
# =======================================

def extract_metadata_from_filename(filename):
    """
    從檔名解析學校與角色資訊
    例如: "114-1IDP/三民國小新進.csv" -> School: 三民國小, Role: 新進
    """
    basename = os.path.basename(filename)
    name_without_ext = os.path.splitext(basename)[0]
    
    # 簡單的規則：假設檔名通常是 "學校名稱+角色.csv" 或 "學校名稱+年份+角色.csv"
    # 這裡做一個簡單的關鍵字提取，您可以根據實際檔名規則調整
    school = "Unknown"
    role = "一般教師"
    
    if "三民國小" in name_without_ext: school = "三民國小"
    elif "三民國中" in name_without_ext: school = "三民國中"
    elif "仙草" in name_without_ext: school = "仙草實小"
    elif "樟湖" in name_without_ext: school = "樟湖生態國中小"
    elif "坪林" in name_without_ext: school = "坪林實中"
    elif "老梅" in name_without_ext: school = "老梅實小"
    elif "拯民" in name_without_ext: school = "拯民國小"
    elif "峨眉" in name_without_ext: school = "峨眉國中"
    
    # 提取角色/年資標籤
    if "新進" in name_without_ext: role = "新進教師"
    elif "熟手" in name_without_ext: role = "熟手教師"
    elif "行政" in name_without_ext: role = "行政人員"
    elif "領導人" in name_without_ext: role = "教師領導人"
    elif "3年以上" in name_without_ext: role = "資深教師(3y+)"
    elif "1~3年" in name_without_ext: role = "初任教師(1-3y)"
    
    return school, role

def clean_column_name(col_name):
    """
    關鍵函數：清洗欄位名稱以實現跨校對齊
    邏輯：移除 [分類]、移除 1.1 / A1 等編號，只保留題幹文字
    """
    # 1. 移除中括號分類，如 [步驟 ①：教學力自評] 或 [核心價值]
    # 非貪婪匹配，移除開頭的 [xxx]
    name = re.sub(r'^\[.*?\]\s*', '', col_name)
    
    # 2. 移除樟湖/標準版的編號前綴
    # 範例匹配: "1.1 ", "2.3 ", "A1 - ", "C13 - "
    # 邏輯: 開頭是 數字/字母 + 點或無點 + 數字 + 空格或橫線
    name = re.sub(r'^[A-Za-z0-9]+\.?[0-9]*\s*[-]?\s*', '', name)
    
    # 3. 移除額外的空白
    return name.strip()

def main():
    # 檢查資料夾是否存在
    if not os.path.exists(SOURCE_FOLDER):
        print(f"錯誤: 找不到資料夾 '{SOURCE_FOLDER}'，請確認路徑。")
        return

    # 搜尋所有 CSV 檔案
    csv_files = glob.glob(os.path.join(SOURCE_FOLDER, "*.csv"))
    
    if not csv_files:
        print(f"在 '{SOURCE_FOLDER}' 中找不到任何 CSV 檔案。")
        return

    print(f"找到 {len(csv_files)} 個 CSV 檔案，開始處理...")
    
    all_dfs = []
    
    for file_path in csv_files:
        try:
            # 讀取 CSV (嘗試 utf-8，若失敗則嘗試 big5/cp950，這是中文csv常見問題)
            try:
                df = pd.read_csv(file_path, encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, encoding='cp950')
            
            # 提取並新增 Metadata 欄位
            school, role = extract_metadata_from_filename(file_path)
            
            # 為了避免欄位順序混亂，我們把 Metadata 放在最前面
            df.insert(0, 'Source_File', os.path.basename(file_path))
            df.insert(1, 'Role_Tag', role)
            df.insert(2, 'School_Name', school)
            
            # 欄位名稱清洗 (對齊關鍵)
            original_cols = df.columns.tolist()
            new_cols = {}
            for c in original_cols:
                # 保留我們剛加的 Metadata 欄位，不清洗
                if c in ['School_Name', 'Role_Tag', 'Source_File', '教師姓名', '教師信箱', '學校', '職位', '科目', '提交時間']:
                    new_cols[c] = c
                else:
                    new_cols[c] = clean_column_name(c)
            
            df.rename(columns=new_cols, inplace=True)
            
            all_dfs.append(df)
            print(f"成功讀取: {os.path.basename(file_path)} (學校: {school}, 角色: {role})")
            
        except Exception as e:
            print(f"讀取失敗: {file_path}, 原因: {e}")

    # 合併所有 DataFrames
    if all_dfs:
        # 使用 outer join 保留所有欄位，自動對齊相同名稱的欄位
        master_df = pd.concat(all_dfs, axis=0, ignore_index=True, sort=False)
        
        # 儲存結果
        master_df.to_csv(OUTPUT_FILENAME, index=False, encoding='utf-8-sig')
        print("-" * 30)
        print(f"合併完成！")
        print(f"總資料筆數: {len(master_df)}")
        print(f"總欄位數: {len(master_df.columns)}")
        print(f"檔案已輸出至: {OUTPUT_FILENAME}")
        
        # 簡單檢查：列出幾個合併後的關鍵欄位，確認是否有對齊
        print("\n[檢查] 合併後的部分教學力指標欄位 (前10個):")
        feature_cols = [c for c in master_df.columns if c not in ['School_Name', 'Role_Tag', 'Source_File', '教師姓名']]
        for col in feature_cols[:10]:
            print(f" - {col}")
            
    else:
        print("沒有成功處理任何資料。")

if __name__ == "__main__":
    main()