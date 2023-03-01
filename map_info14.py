import streamlit as st                      # streamlit
from streamlit_folium import st_folium    # streamlitでfoliumを使う
import folium                               # folium
import pandas as pd                         # CSVをデータフレームとして読み込む
import requests
import urllib
from urllib.parse import urlencode

# 表示するデータを読み込み2
df_final = pd.read_csv('realestate_info_finalimage.csv')

# ページ設定
st.set_page_config(
    page_title="streamlit-foliumテスト",
    page_icon="🗾",
    layout="wide"
)

# 1. 画面の表示
# サイドバー
st.sidebar.title('MAP表示条件')
xmax = st.sidebar.number_input('物件表示数 ：', 0, 1000, 100)
ymax = st.sidebar.number_input('test ：', 0, 1000, 200)

st.sidebar.title('比較条件')
zmax = st.sidebar.number_input('test1 ：', 0, 1000, 200)
amax = st.sidebar.number_input('test2 ：', 0, 1000, 200)
bmax = st.sidebar.number_input('test3 ：', 0, 1000, 200)

# メイン画面 検索
st.title('賃貸検索')
st.markdown("---")
st.subheader('検索条件')
extra_configs_0 = st.expander("検索条件1")  # Extra Configs
with extra_configs_0:
    se1 = st.number_input('家賃[万円]以下 ：', 0, 500, 30)
    se2 = st.number_input('面積[m^2]以上 ：', 0, 500, 50)

extra_configs_1 = st.expander("検索条件2")  # Extra Configs
with extra_configs_1:
    se3 = st.multiselect(
        '間取り', ['ワンルーム', '1K', '1DK', '1LDK', '2DK', '2LDK'], ['2LDK'])
    se4 = st.multiselect('区', ['品川', '渋谷', '江戸川', '港'], ['品川', '江戸川'])
    #se5 = st.multiselect('市町', ['南品川', '東五反田', '南大井', '東品川'], ['南品川'])

# 住所追加
extra_configs_2 = st.expander("周辺施設")  # Extra Configs
with extra_configs_2:
    se6 = st.multiselect('検索施設', ['コンビニ', 'スーパー', '病院', '公園'], ['コンビニ'])


# フィルタリング
df_final0 = df_final
joken1 = (df_final0["家賃"] > 0) & (df_final0["家賃"] < se1)
df_final0 = df_final0[joken1]
joken2 = (df_final0["面積"] > se2) & (df_final0["面積"] < 300)
df_final0 = df_final0[joken2]
joken3 = df_final0["間取り"].isin(se3)
df_final0 = df_final0[joken3]
joken4 = df_final0["区"].isin(se4)
df_final0 = df_final0[joken4]

st.subheader('(フィルター後のデータ確認用)')
# フィルター後の地図データを作成する
# 表示するデータを読み込み1

df_final0 = df_final0.drop_duplicates(subset=['名称', '階数'])

se90 = st.write(df_final0)
se91 = st.write(df_final0.shape)

if df_final0.shape[0] > 50:
    df = df_final0[:50]
else:
    df = df_final0

def Map_info(x):
    makeUrl = "https://msearch.gsi.go.jp/address-search/AddressSearch?q="
    s_quote = urllib.parse.quote(x['アドレス'])
    response = requests.get(makeUrl + s_quote)
    try:
        map_info_d = response.json()[0]["geometry"]["coordinates"]
        #map_info_d = pd.DataFrame(map_info)
        return map_info_d[0], map_info_d[1]
    except Exception as e:
        print(e)
        return 0, 0


df[['経度', '緯度']] = df.apply(lambda x: Map_info(x),axis=1, result_type='expand')

se90 = st.write(df)
se91 = st.write(df.shape)

# 地図の中心の緯度/経度、タイル、初期のズームサイズを指定します。
m = folium.Map(
    # 地図の中心位置の指定
    location=[35.623516, 139.706985],
    # タイル、アトリビュートの指定
    tiles='https://cyberjapandata.gsi.go.jp/xyz/pale/{z}/{x}/{y}.png',
    attr='都道府県庁所在地、人口、面積(2016年)',
    # ズームを指定
    zoom_start=10
)

select_columns_num = ['緯度', '経度']
pre_df = df[select_columns_num]

for column in pre_df:
    pre_df[column] = pd.to_numeric(pre_df[column], errors='coerce')
df[select_columns_num] = pre_df

# 読み込んだデータ(緯度・経度、ポップアップ用文字、アイコンを表示)
for i, row in df.iterrows():
    # ポップアップの作成(都道府県名＋都道府県庁所在地＋人口＋面積)
    pop = f"{row['カテゴリー']} <br>・家賃…{row['家賃']} <br>・面積…{row['面積']}<br>・築数…{row['築年数']}<br>・階数…{row['階数']}"
    folium.Marker(
        # 緯度と経度を指定
        location=[row['緯度'], row['経度']],
        # ツールチップの指定(都道府県名)
        tooltip=row['名称'],
        # ポップアップの指定
        popup=folium.Popup(pop, max_width=300),
        # アイコンの指定(アイコン、色)
        icon=folium.Icon(icon="home", icon_color="white", color="red")
    ).add_to(m)

# --------------------------------------------------------------------------------------------------------------------

# パラメータリスト
api_key = 'AIzaSyAdFUui2C-RKcw48ApjPQJtBR_AAxIoWg4'
radius = 500  # 半径500m
keyword = "コンビニ"
language = 'ja'

if 'count1' not in st.session_state:
    lat2, lng2 = 35.623516, 139.706985  # m_data13, m_data14
else:
    lat2, lng2 = 35.623516, 139.706985 #st.session_state.count1, st.session_state.count2

# エンドポイントURL
# places_endpoint = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
# # パラメータ
# params = {
#     "key": api_key,
#     "location": f"{lat2},{lng2}",
#     "radius": radius,
#     "keyword": keyword,
#     "language": language,
# }

# # URLエンコード, リクエストURL生成
# params_encoded = urlencode(params)
# places_url = f"{places_endpoint}?{params_encoded}"

# # 結果取得
# r = requests.get(places_url)
# data = r.json()

# # APIレスポンスを取得
# places = r.json()["results"]
# df_cb = pd.DataFrame(columns=['名称', '住所', '緯度', '経度'])

# # 各コンビニの位置情報を表示
# for place in places:
#     temp = pd.DataFrame(data=[[place["name"], place["vicinity"], round(place["geometry"]["location"]["lat"], 7), round(
#         place["geometry"]["location"]["lng"], 7)]], columns=df_cb.columns)
#     df_cb = pd.concat([df_cb, temp])
#     print("名称:", place["name"])

# df_cb = df_cb.reset_index()
# home = (lat2, lng2)

#for i, row in df_cb.iterrows():
#    # ポップアップの作成(都道府県名＋都道府県庁所在地＋人口＋面積)
#    pop = f"・名称…{row['名称']} <br>・距離[m]…"
#    folium.Marker(
#        # 緯度と経度を指定
#        location=[row['緯度'], row['経度']],
#        # ツールチップの指定(都道府県名)
#        tooltip=row['名称'],
#        # ポップアップの指定
#        popup=folium.Popup(pop, max_width=300),
#        # アイコンの指定(アイコン、色)
#        icon=folium.Icon(icon="bell", icon_color="white", color="blue")
#    ).add_to(m)


# メイン画面 MAP表示 ＆ 詳細情報
st.markdown("---")
map_col, info_col = st.columns([2, 1], gap="medium")

map_col.subheader("物件地図")
with map_col:
    map = st_folium(m, width=1000, height=600)
    m_data = map["last_object_clicked_tooltip"]
    m_data1 = df[df["名称"] == m_data]["アドレス"].values
    m_data2 = df[df["名称"] == m_data]["家賃"].values
    m_data3 = df[df["名称"] == m_data]["間取り"].values
    m_data4 = df[df["名称"] == m_data]["面積"].values
    m_data5 = df[df["名称"] == m_data]["築年数"].values
    m_data6 = df[df["名称"] == m_data]["階数"].values
    m_data7 = df[df["名称"] == m_data]["構造"].values
    m_data8 = df[df["名称"] == m_data]["敷金"].values
    m_data9 = df[df["名称"] == m_data]["礼金"].values
    m_data10 = df[df["名称"] == m_data]["管理費"].values
    m_data11 = df[df["名称"] == m_data]["カテゴリー"].values
    m_data12 = df[df["名称"] == m_data]["オススメ度"].values
    m_data13 = df[df["名称"] == m_data]["経度"].values
    m_data14 = df[df["名称"] == m_data]["緯度"].values

#if m_data is not None:
    #st.session_state.count1 = m_data13
    #st.session_state.count2 = m_data14

info_col.subheader("物件詳細")
if m_data is not None:
    # st.write(m_data)
    info_col.text(f"物件名：{m_data}")
    info_col.text(f"住所　：{m_data1[0]}")
    info_col.text(f'家賃　：{m_data2[0]}')
    info_col.text(f'間取り：{m_data3[0]}')
    info_col.text(f'面積　：{m_data4[0]}')
    info_col.text(f'築年数：{m_data5[0]}')
    info_col.text(f'階数　：{m_data6[0]}')
    info_col.text(f'構造　：{m_data7[0]}')
    info_col.text(f'敷金　：{m_data8[0]}')
    info_col.text(f'礼金　：{m_data9[0]}')
    info_col.text(f'管理費：{m_data10[0]}')
    info_col.text(f'オススメ度：{m_data12[0]}')
    info_col.text(f'カテゴリー：{m_data11[0]}')

    #map2 = st_folium(m, width=1000, height=600)

# # 関数化
# def Map_distance(x):
#     home_dis = (x["緯度"], x["経度"])
#     dis = geodesic(home, home_dis)
#     return dis

# df_cb['距離'] = df_cb.apply(Map_distance, axis=1)

# ----------------------------------------------------------------------------
st.markdown("---")
df_recc = df_final0.sort_values(by="オススメ度", ascending=False)
df_recc = df_recc.reset_index()

st.header('物件比較')
a_col, b_col, c_col, d_col = st.columns([1, 1, 1, 1], gap="medium")
a_col.subheader("現在物件")
b_col.subheader("物件A")
c_col.subheader("物件B")
d_col.subheader("物件C")

if m_data is not None:
    a_col.text(f"物件名：{m_data}")
    a_col.text(f'家賃　：{m_data2[0]}')
    a_col.text(f'間取り：{m_data3[0]}')
    a_col.text(f'面積　：{m_data4[0]}')
    a_col.text(f'築年数：{m_data5[0]}')
    a_col.text(f'おススメ度：{m_data12[0]}')

    if df_recc.shape[0] > 5:
        b_col.text(f'物件名：{df_recc["名称"][0]}')
        b_col.text(f'家賃　：{df_recc["家賃"][0]}')
        b_col.text(f'間取り：{df_recc["間取り"][0]}')
        b_col.text(f'面積　：{df_recc["面積"][0]}')
        b_col.text(f'築年数：{df_recc["築年数"][0]}')
        b_col.text(f'おススメ度：{df_recc["オススメ度"][0]}')

        c_col.text(f'物件名：{df_recc["名称"][1]}')
        c_col.text(f'家賃　：{df_recc["家賃"][1]}')
        c_col.text(f'間取り：{df_recc["間取り"][1]}')
        c_col.text(f'面積　：{df_recc["面積"][0]}')
        c_col.text(f'築年数：{df_recc["築年数"][1]}')
        c_col.text(f'おススメ度：{df_recc["オススメ度"][1]}')

        d_col.text(f'物件名：{df_recc["名称"][2]}')
        d_col.text(f'家賃　：{df_recc["家賃"][2]}')
        d_col.text(f'面積　：{df_recc["面積"][0]}')
        d_col.text(f'間取り：{df_recc["間取り"][2]}')
        d_col.text(f'築年数：{df_recc["築年数"][2]}')
        d_col.text(f'おススメ度：{df_recc["オススメ度"][2]}')

st.subheader('(フィルター後のデータ確認用)')
se90 = st.write(df_recc)

#st_data = st_folium(m, width=1200, height=800)
