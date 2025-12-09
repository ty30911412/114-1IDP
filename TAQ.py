import pandas as pd
import re
import os

# ================= 設定區 =================
INPUT_FILENAME = '/Users/xian/R project/114-1IDP/114_IDP_Master_Merged.csv'  # 來源檔案 (剛剛合併出來的那份)
OUTPUT_FILENAME = '/Users/xian/R project/114-1IDP/114_Teaching_Ability_Quantified.csv' # 輸出檔案
# =========================================

def extract_score(text):
    """
    將文字描述轉換為量化分數 (1-5)
    支援格式：
    1. "階段四：..." -> 4
    2. "Level 4 - ..." -> 4
    3. "4" -> 4
    4. "__TEMP__" -> None (空值)
    """
    if pd.isna(text):
        return None
    
    text_str = str(text).strip()
    
    # 排除系統預設的無效佔位符
    if "__TEMP__" in text_str:
        return None
        
    # 模式 A: 中文階段 (例如: "階段四：老師幾乎...")
    cn_num_map = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5}
    match_stage = re.search(r'階段([一二三四五])', text_str)
    if match_stage:
        return cn_num_map.get(match_stage.group(1))
    
    # 模式 B: 英文 Level 或純數字 (例如: "Level 4", "4.0", "4")
    # 邏輯：找 "Level" 後面的數字，或者字串開頭的數字
    match_level = re.search(r'(?:Level\s*|^)(\d)(\.0)?', text_str, re.IGNORECASE)
    if match_level:
        return int(match_level.group(1))
        
    return None

def main():
    # 1. 讀取合併後的檔案
    if not os.path.exists(INPUT_FILENAME):
        print(f"錯誤: 找不到檔案 '{INPUT_FILENAME}'，請確認您已執行過合併步驟。")
        return
    
    print(f"正在讀取 {INPUT_FILENAME} ...")
    try:
        df = pd.read_csv(INPUT_FILENAME)
    except Exception as e:
        print(f"讀取失敗: {e}")
        return

    # 2. 定義教學力相關的關鍵字
    # 這些關鍵字能涵蓋 KIST 標準版與樟湖版的核心指標
    teaching_keywords = [
        # --- 標準版指標 ---
        "給每一個學生機會和期待", "維護公平合理的學習狀態", "建立融合的學習氛圍", 
        "創造學習的樂趣", "打造安心無畏的空間", "校準課程體驗和學習目標", 
        "掌握課程節奏", "力求課程嚴謹", "進行差異化和個人化處遇", 
        "善用提問的力量", "引導討論和對話", "拉伸學生的思考和聲音", 
        "激發學生對學習的主動性和責任感", "拉高學生對內容的概念化理解", 
        "提供嚴謹的學習任務", "收集學習數據", "做好數據驅動的教學決定", 
        "給出有目的性的回饋", "設計差異化的課堂",
        
        # --- 樟湖版指標 (雖然合併時已部分清洗，但保留關鍵字以防萬一) ---
        "以生態哲學建立", "以正向溫暖進行溝通", "培養成長心態", 
        "保持情緒穩定", "包容差異", "主動積極", 
        "能蒐集學習數據", "培養學生主動積極性", "依照學生程度擬定教學計畫", 
        "學科核心概念", "夯實學生基礎知識能力", "培養學生多元觀點"
    ]

    # 3. 篩選欄位
    # 保留 Metadata (前幾欄通常是學校、角色、姓名)
    metadata_cols = ['School_Name', 'Role_Tag', '教師姓名', '職位', '科目']
    selected_cols = [c for c in metadata_cols if c in df.columns]
    
    # 找出所有符合教學力關鍵字的欄位
    target_cols = []
    for col in df.columns:
        if col in selected_cols: continue # 避免重複加入 metadata
        if any(keyword in col for keyword in teaching_keywords):
            target_cols.append(col)
            
    print(f"偵測到 {len(target_cols)} 個與教學力相關的指標欄位。")
    
    # 建立新的 DataFrame
    df_teaching = df[selected_cols + target_cols].copy()

    # 4. 執行量化轉換
    print("正在將文字描述轉換為量化分數 (1-5)...")
    for col in target_cols:
        df_teaching[col] = df_teaching[col].apply(extract_score)

    # 5. 儲存結果
    df_teaching.to_csv(OUTPUT_FILENAME, index=False, encoding='utf-8-sig')
    
    print("-" * 30)
    print("處理完成！")
    print(f"原始資料欄位數: {len(df.columns)}")
    print(f"清洗後欄位數: {len(df_teaching.columns)}")
    print(f"已輸出至: {OUTPUT_FILENAME}")
    print("-" * 30)
    
    # 6. 顯示簡單的統計摘要 (讓您在本機端也能看到初步結果)
    # 計算每個指標的平均分 (忽略空值)
    stats = df_teaching[target_cols].mean().sort_values(ascending=False)
    print("\n[初步分析] 各項教學指標平均分數 (全聯盟):")
    print(stats.head(10)) # 顯示前 10 高分的項目

if __name__ == "__main__":
    main()