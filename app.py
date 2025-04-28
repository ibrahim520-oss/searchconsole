#ライブラリー

import streamlit as st  
import pandas as pd
import datetime
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

#ウェブアプリのタイトル
st.title("Google Search Console データ分析")

#サイドバーにアップロードとドメイン
st.sidebar.header("Google search console設定")
uploaded_file = st.sidebar.file_uploader("サービスアカウントのJSONファイルをアップロードしてください", type="json")
SITE_URL = st.sidebar.text_input("ドメインを入力してください", "例：https://example.com/")  # デフォルト値を設定
end_date = st.sidebar.date_input("終了日を選択", datetime.date.today())
start_date = st.sidebar.date_input("開始日を選択", end_date - datetime.timedelta(days=90))

#セッションステートでデータ保持
if 'df' not in st.session_state:
    st.session_state.df = None

df = pd.DataFrame(columns=['query', 'page', 'clicks', 'impressions', 'ctr', 'position'])  # 初期化
if uploaded_file and SITE_URL:
    if st.sidebar.button("分析開始"):
        try:
            # JSONファイルの読み込み
            json_data = json.load(uploaded_file)
            credentials = service_account.Credentials.from_service_account_info(json_data,scopes=['https://www.googleapis.com/auth/webmasters.readonly'])
            service = build('webmasters', 'v3', credentials=credentials)

            request = {
                'startDate': start_date.strftime('%Y-%m-%d'),
                'endDate': end_date.strftime('%Y-%m-%d'),
                'dimensions': ['query', 'page'],
                'rowLimit': 25000,
                "startRow": 0
            }
            
            response = service.searchanalytics().query(siteUrl=SITE_URL, body=request).execute()

            rows = response.get('rows', [])
            data = []
            for row in rows:
                query = row['keys'][0]
                page = row['keys'][1]
                clicks = row['clicks']
                impressions = row['impressions']
                ctr = row['ctr']
                position = row['position']
                data.append([query, page, clicks, impressions, ctr, position])
                
            df = pd.DataFrame(data, columns=['query', 'page', 'clicks', 'impressions', 'ctr', 'position'])

            #セッションステートにデータを格納
            st.session_state.df = df
            
        except Exception as e:
            st.error(f"エラーが発生しました: {str(e)}")


if 'df' in locals() and not df.empty:
    st.write(df)
else:
    st.warning("データがありません。")

#データが存在する場合は全データ表示とフィルタリング表示
if st.session_state.df is not None:
    df = st.session_state.df

    #全件表示
    st.header("全データ表示")
    st.write(df)

    #数字のインプットでフィルタリング条件を指定
    st.header("フィルタリング条件指定")  

    #impressionsの条件
    st.subheader("Impressionsの条件")
    col1, col2 = st.columns(2)
    with col1:
        min_impressions = st.number_input(
            "impressinos 以上", 
            min_value=int(df["impressions"].min()),
            max_value=int(df["impressions"].max()),
            value=int(df["impressions"].min())
        )
    with col2:
        max_impressions =st.number_input("impressinos 以下", 
            min_value=int(df["impressions"].min()),
            max_value=int(df["impressions"].max()),
            value=int(df["impressions"].max())
        )

        # clicksの条件
    st.subheader("Clicksの条件")
    col3, col4 = st.columns(2) 
    with col3:
        min_clicks = st.number_input(
            "clicks 以上", 
            min_value=int(df["clicks"].min()),
            max_value=int(df["clicks"].max()),
            value=int(df["clicks"].min())
        )
    with col4:
        max_clicks = st.number_input("clicks 以下", 
            min_value=int(df["clicks"].min()),
            max_value=int(df["clicks"].max()),
            value=int(df["clicks"].max())
        )
    #ctrの条件
    st.subheader("CTRの条件")
    col5, col6 = st.columns(2)
    with col5:
        min_ctr = st.number_input(
            "ctr 以上", 
            min_value=float(df["ctr"].min()),
            max_value=float(df["ctr"].max()),
            value=float(df["ctr"].min()),
            step=0.01
        )
    with col6:
        max_ctr = st.number_input("ctr 以下", 
            min_value=float(df["ctr"].min()),
            max_value=float(df["ctr"].max()),
            value=float(df["ctr"].max()),
            step=0.01
        )
    #positionの条件
    st.subheader("Positionの条件")  
    col7, col8 = st.columns(2) 
    with col7:
        min_position = st.number_input(
            "position 以上", 
            min_value=float(df["position"].min()),
            max_value=float(df["position"].max()),
            value=float(df["position"].min())
        )
    with col8:  
        max_position = st.number_input("position 以下", 
            min_value=float(df["position"].min()),
            max_value=float(df["position"].max()),
            value=float(df["position"].max())
        )
    #フィルタリング条件の適応
    filtered_df = df[
        (df["impressions"] >= min_impressions) 
        & (df["impressions"] <= max_impressions) 
        & (df["clicks"] >= min_clicks) 
        & (df["clicks"] <= max_clicks) 
        & (df["ctr"] >= min_ctr) 
        & (df["ctr"] <= max_ctr) 
        & (df["position"] >= min_position) 
        & (df["position"] <= max_position)
    ]

    st.header("フィルタリングされたデータ")
    st.write(filtered_df)
