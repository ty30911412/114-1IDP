import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
#python3 -m streamlit run dashboard.py
# 設定頁面標題與佈局
st.set_page_config(page_title="114學年度 教師IDP教學力分析儀表板", layout="wide")

# ================= 資料讀取區 =================
@st.cache_data
def load_data():
    data = {}
    # 檔案路徑對應 (請確保這些檔案在同一目錄下)
    files = {
        "kist_overall": "1_KIST_Overall_Stats_v2.csv",
        "kist_school": "2_KIST_School_Comparison_v2.csv",
        "kist_role": "3_KIST_Role_Comparison_v2.csv",
        "zhanghu_overall": "Zhanghu_Overall_Stats.csv"
    }
    
    for key, filename in files.items():
        if os.path.exists(filename):
            # 讀取時將第一欄設為 Index 並命名為 '指標'
            df = pd.read_csv(filename, index_col=0)
            df.index.name = '指標'
            data[key] = df
        else:
            st.error(f"找不到檔案: {filename}，請確認檔案是否在同一目錄下。")
            return None
    return data

data = load_data()

if data:
    st.title("114-1 教師IDP教學力分析儀表板")
    st.markdown("---")

    # 側邊欄導航
    st.sidebar.header("分析維度選擇")
    analysis_mode = st.sidebar.radio(
        "請選擇要查看的分析視角：",
        ("KIST 標準分析", "樟湖指標分析")
    )

    # ================= 頁面 1: KIST 標準體系分析 =================
    if analysis_mode == "KIST 標準分析":
        st.header("KIST 標準分析")
        
        # 1. 總體表現概況
        st.subheader("1. 總體表現")
        df_overall = data['kist_overall']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 高分指標 (Top 5)")
            top5 = df_overall.sort_values(by='平均數', ascending=False).head(5)
            fig_top = px.bar(top5, x='平均數', y=top5.index, orientation='h', 
                             text_auto='.2f', title="平均分數最高的指標",
                             color='平均數', color_continuous_scale='Greens')
            fig_top.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_top, use_container_width=True)
            
        with col2:
            st.markdown("#### 待觀察指標 (Bottom 5)")
            bot5 = df_overall.sort_values(by='平均數', ascending=True).head(5)
            fig_bot = px.bar(bot5, x='平均數', y=bot5.index, orientation='h', 
                             text_auto='.2f', title="平均分數較低的指標",
                             color='平均數', color_continuous_scale='Reds_r')
            fig_bot.update_layout(yaxis={'categoryorder':'total descending'})
            st.plotly_chart(fig_bot, use_container_width=True)

        st.markdown("---")

        # 2. 校際比較
        st.subheader("2. 校際比較")
        df_school = data['kist_school']
        
        # 分離樣本數列與數據列
        sample_sizes = df_school.loc[['有效樣本數 (N)']]
        metrics_data = df_school.drop(['有效樣本數 (N)'], errors='ignore')
        
        # 展示樣本數
        st.info("各校有效樣本數 (N)：" + ", ".join([f"{col}: {int(val)}" for col, val in sample_sizes.iloc[0].items()]))
        
        # 熱力圖
        fig_heatmap = px.imshow(metrics_data, 
                                text_auto='.1f',
                                aspect="auto",
                                color_continuous_scale="RdYlGn",
                                title="各校教學力指標熱力圖 (數值越高越綠)")
        st.plotly_chart(fig_heatmap, use_container_width=True)

        st.markdown("---")

        # 3. 身份差異分析
        st.subheader("3. 身份/資歷差異")
        df_role = data['kist_role']
        
        # 同樣分離樣本數
        role_metrics = df_role.drop(['有效樣本數 (N)'], errors='ignore')
        
        # 讓使用者選擇要比較的身份
        roles = role_metrics.columns.tolist()
        selected_roles = st.multiselect("選擇要比較的身份：", roles, default=roles[:2])
        
        if selected_roles:
            # 雷達圖比較 (如果指標太多，雷達圖會很亂，改用分組長條圖)
            # 為了可讀性，我們只選取差異最大的前 10 個指標來畫圖
            
            # 計算選定角色的差異 (變異數)
            role_metrics['variance'] = role_metrics[selected_roles].var(axis=1)
            top_diff_metrics = role_metrics.sort_values('variance', ascending=False).head(10).index
            
            df_plot = role_metrics.loc[top_diff_metrics, selected_roles].reset_index().melt(id_vars='指標', var_name='身份', value_name='分數')
            
            fig_group = px.bar(df_plot, x='指標', y='分數', color='身份', barmode='group',
                               title="不同身份在關鍵指標上的差異 (差異最大的前10項)", text_auto='.1f')
            st.plotly_chart(fig_group, use_container_width=True)
            
            with st.expander("查看完整數據表"):
                st.dataframe(role_metrics[selected_roles].style.highlight_max(axis=1, color='lightgreen'))

    # ================= 頁面 2: 樟湖特色體系分析 =================
    elif analysis_mode == "樟湖指標分析":
        st.header("樟湖指標分析")
        
        df_zh = data['zhanghu_overall']
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.metric("分析教師人數", int(df_zh.iloc[0]['有效樣本數']))
            st.markdown("### 指標總表")
            st.dataframe(df_zh[['平均數', '標準差']].style.background_gradient(cmap='Greens'))
            
        with col2:
            st.markdown("### 指標表現排序")
            fig_zh = px.bar(df_zh.sort_values('平均數'), x='平均數', y=df_zh.index, orientation='h',
                            text_auto='.2f', color='平均數', color_continuous_scale='Teal')
            fig_zh.update_layout(height=600)
            st.plotly_chart(fig_zh, use_container_width=True)
            
        st.info("註：樟湖體系採用獨立的校本指標（如：生態哲學、人文關懷），因此獨立呈現分析結果。")

else:
    st.warning("請確認 CSV 檔案已放置於正確路徑。")