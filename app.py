import streamlit as st
import pandas as pd
import numpy as np
import io
import os
import re

# ページ設定
st.set_page_config(
    page_title="AutoPage Converter",
    page_icon="🔄",
    layout="wide"
)

PARTS_CATEGORY_MAP = {
    'ブロアモーター': r'補修部品\電子系\ブロアモーター',
    'ラジエーター': r'補修部品\冷却系\ラジエーター',
    'オルタネーター': r'補修部品\電装系\オルタネーター',
    'スターターモーター': r'補修部品\スターターモーター',
    'ラジエーター': r'補修部品\ラジエーター',
    'コンプレッサー': r'補修部品\コンプレッサー',
    'イグニッションコイル': r'補修部品\イグニッションコイル',
    'スパークプラグ': r'補修部品\スパークプラグ',
    'ベンツ': r'補修部品\ブレーキパッド\ベンツ',
    'BMW': r'補修部品\ブレーキパッド\BMW',
    'VW': r'補修部品\ブレーキパッド\VW',
    'ポルシェ': r'補修部品\ブレーキパッド\ポルシェ',
    'アウディ': r'補修部品\ブレーキパッド\アウディ',
    'ボルボ': r'補修部品\ブレーキパッド\ボルボ',
    'トヨタ': r'補修部品\ブレーキパッド\トヨタ',
    '日産': r'補修部品\ブレーキパッド\日産',
    'ホンダ': r'補修部品\ブレーキパッド\ホンダ',
    'スバル': r'補修部品\ブレーキパッド\スバル',
    'ダイハツ': r'補修部品\ブレーキパッド\ダイハツ',
    'スズキ': r'補修部品\ブレーキパッド\スズキ',
    '三菱': r'補修部品\ブレーキパッド\三菱',
    'マツダ': r'補修部品\ブレーキパッド\マツダ',
    'レクサス': r'補修部品\ブレーキパッド\レクサス',
    'ライト・ランプ': r'補修部品\ライト・ランプ',
    'ウォーターポンプ': r'補修部品\ウォーターポンプ',
    'オイル・添加剤': r'補修部品\オイル・添加剤',
    'カムシール': r'補修部品\エンジン系\カムシール',
    'オイルフィルター': r'補修部品\エンジン系\オイルフィルター',
    'オルタネーター': r'補修部品\エンジン系\オルタネーター',
    'カムシャフト': r'補修部品\エンジン系\カムシャフト',
    'クランクシール': r'補修部品\エンジン系\クランクシール',
    'スターターモーター': r'補修部品\エンジン系\スターターモーター',
    'タイミングベルト・ファンベルト': r'補修部品\エンジン系\タイミングベルト・ファンベルト',
    'フューエルポンプ': r'補修部品\エンジン系\フューエルポンプ',
    'フューエルフィルタ': r'補修部品\エンジン系\フューエルフィルタ',
    'スパークプラグ': r'補修部品\エンジン系\スパークプラグ',
    'イグニッションコイル': r'補修部品\エンジン系\イグニッションコイル',
    'プラグコード': r'補修部品\エンジン系\プラグコード',
    'NOxセンサー': r'補修部品\エンジン系\NOxセンサー',
    'その他エンジン系': r'補修部品\エンジン系\その他エンジン系',
    'ウォーターポンプ': r'補修部品\冷却系\ウォーターポンプ',
    'コンデンサー': r'補修部品\冷却系\コンデンサー',
    'ラジエーター': r'補修部品\冷却系\ラジエーター',
    'ラジエーターキャップ': r'補修部品\冷却系\ラジエーターキャップ',
    'ラジエーターホース': r'補修部品\冷却系\ラジエーターホース',
    '電動ファン': r'補修部品\冷却系\電動ファン',
    'インタークーラー': r'補修部品\冷却系\インタークーラー',
'オイルクーラー': r'補修部品\冷却系\オイルクーラー',
'サーモスタット': r'補修部品\冷却系\サーモスタット',
'その他冷却系': r'補修部品\冷却系\その他冷却系',
'インテークパイプ': r'補修部品\吸気系\インテークパイプ',
'インテークマニホールド': r'補修部品\吸気系\インテークマニホールド',
'エアクリーナー・エアフィルター': r'補修部品\吸気系\エアクリーナー・エアフィルター',
'エアコンプレッサー': r'補修部品\吸気系\エアコンプレッサー',
'エアコンフィルター': r'補修部品\吸気系\エアコンフィルター',
'その他吸気系': r'補修部品\吸気系\その他吸気系',
'O2センサー': r'補修部品\排気系\O2センサー',
'エキゾーストマニホールド': r'補修部品\排気系\エキゾーストマニホールド',
'タービンキット': r'補修部品\排気系\タービンキット',
'マフラー': r'補修部品\排気系\マフラー',
'エアフロメーター': r'補修部品\排気系\エアフロメーター',
'その他排気系': r'補修部品\排気系\その他排気系',
'エバポレーター': r'補修部品\電子系\エバポレーター',
'オイルプレッシャースイッチ': r'補修部品\電子系\オイルプレッシャースイッチ',
'パワーウィンドウスイッチ': r'補修部品\電子系\パワーウィンドウスイッチ',
'パワーウィンドウモーター': r'補修部品\電子系\パワーウィンドウモーター',
'ブロアモーター': r'補修部品\電子系\ブロアモーター',
'その他スイッチ・電子系': r'補修部品\電子系\その他スイッチ・電子系',
'車高調整キット': r'補修部品\サスペンション系\車高調整キット',
'エアサス': r'補修部品\サスペンション系\エアサス',
'コントロールアーム': r'補修部品\サスペンション系\コントロールアーム',
'サスペンションキット': r'補修部品\サスペンション系\サスペンションキット',
'ショックアブソーバー': r'補修部品\サスペンション系\ショックアブソーバー',
'スタビライザー': r'補修部品\サスペンション系\スタビライザー',
'スプリング': r'補修部品\サスペンション系\スプリング',
'その他サスペンション系': r'補修部品\サスペンション系\その他サスペンション系',
'クラッチ': r'補修部品\駆動系\クラッチ',
'ステアリングギヤボックス': r'補修部品\駆動系\ステアリングギヤボックス',
'ステアリングラックブーツ': r'補修部品\駆動系\ステアリングラックブーツ',
'タイロッドエンド': r'補修部品\駆動系\タイロッドエンド',
'ドライブシャフト': r'補修部品\駆動系\ドライブシャフト',
'ドライブシャフトブーツ': r'補修部品\駆動系\ドライブシャフトブーツ',
'ドライブベルト': r'補修部品\駆動系\ドライブベルト',
'プロペラシャフト': r'補修部品\駆動系\プロペラシャフト',
'ベーンポンプ': r'補修部品\駆動系\ベーンポンプ',
'ポールジョイントブーツ': r'補修部品\駆動系\ポールジョイントブーツ',
'ミッションオイルフィルター': r'補修部品\駆動系\ミッションオイルフィルター',
'その他駆動系': r'補修部品\駆動系\その他駆動系',
'ブレーキパッド': r'補修部品\ブレーキ系\ブレーキパッド',
'ブレーキローター': r'補修部品\ブレーキ系\ブレーキローター',
'ブレーキシュー': r'補修部品\ブレーキ系\ブレーキシュー',
'ブレーキキャリパー': r'補修部品\ブレーキ系\ブレーキキャリパー',
'ブレーキホース': r'補修部品\ブレーキ系\ブレーキホース',
'その他ブレーキ系': r'補修部品\ブレーキ系\その他ブレーキ系',
'ABS': r'補修部品\ブレーキ系\ABS',
'スポイラー': r'用品\外装・エアロ\スポイラー',
'ナンバープレートフレーム': r'用品\外装・エアロ\ナンバープレートフレーム',
'アンテナ': r'用品\外装・エアロ\アンテナ',
'ボンネット': r'用品\外装・エアロ\ボンネット',
'マフラーカッター': r'用品\外装・エアロ\マフラーカッター',
'エンブレム': r'用品\外装・エアロ\エンブレム',
'フェンダー': r'用品\外装・エアロ\フェンダー',
'グリル': r'用品\外装・エアロ\グリル',
'サイドステップ': r'用品\外装・エアロ\サイドステップ',
'ドアパネル': r'用品\外装・エアロ\ドアパネル',
'ドアミラー': r'用品\外装・エアロ\ドアミラー',
'バンパー': r'用品\外装・エアロ\バンパー',
'ワイパーゴム': r'用品\外装・エアロ\ワイパーゴム',
'ワイパーブレード': r'用品\外装・エアロ\ワイパーブレード',
'その他外装・エアロ': r'用品\外装・エアロ\その他外装・エアロ',
'シート': r'用品\内装\シート',
'インテリアパネル': r'用品\内装\インテリアパネル',
'シートレール': r'用品\内装\シートレール',
'ステアリング・ハンドル': r'用品\内装\ステアリング・ハンドル',
'ペダル': r'用品\内装\ペダル',
'その他内装': r'用品\内装\その他内装',
'カスタムパーツ': r'トラック用品\カスタムパーツ',
'補修': r'トラック用品\補修',
'アクセサリー　※「トラック用品\アクセサリー」': r'トラック用品\アクセサリー',
'アクセサリー　※「雑貨等\アクセサリー」': r'雑貨等\アクセサリー',
'サンシェード': r'雑貨等\アクセサリー\サンシェード',
'キーカバー': r'雑貨等\アクセサリー\キーカバー',
'芳香剤・消臭剤': r'雑貨等\アクセサリー\芳香剤・消臭剤',
'スピーカー': r'雑貨等\アクセサリー\スピーカー',
'その他　※「用品\雑貨等\その他」': r'雑貨等\アクセサリー\その他',
'工具': r'雑貨等\整備・メンテナンス\工具',
'その他整備・メンテナンス': r'雑貨等\整備・メンテナンス\その他整備・メンテナンス',
'アラーム': r'雑貨等\盗難防止・セキュリティ\アラーム',
'ロック': r'雑貨等\盗難防止・セキュリティ\ロック',
'キャンプ用品': r'雑貨等\アウトドア雑貨\キャンプ用品',
'プール': r'雑貨等\アウトドア雑貨\プール',
'楽しい雑貨': r'雑貨等\楽しい雑貨'
}


# 左サイドバーの入力UI
st.sidebar.header("楽天登録用 設定項目")
genre_id_input = st.sidebar.text_input("ジャンルID", value="")
catch_copy_input = st.sidebar.text_input("キャッチコピー", value="")
attr3_input = st.sidebar.text_input("代表カラー", value="-")
target_cat_row3 = st.sidebar.text_input("表示先カテゴリ（3行目用）", value="商品3")
target_parts_key = st.sidebar.selectbox("パーツカテゴリ（2行目用）", options=list(PARTS_CATEGORY_MAP.keys()) + ['その他（直接入力）'])
if target_parts_key == 'その他（直接入力）':
    selected_path = st.sidebar.text_input("カテゴリパスを直接入力", value="")
else:
    selected_path = PARTS_CATEGORY_MAP.get(target_parts_key, '')

# 商品画像設定アコーディオンUIの追加
with st.sidebar.expander("商品画像設定"):
    # 白背景画像の追加
    white_bg_input = st.text_input("白背景画像", value="")
    
    image_inputs = {}
    image_keys = [
        ("メイン画像", "商品画像パス1"),
        ("画像1", "商品画像パス2"),
        ("画像2", "商品画像パス3"),
        ("画像3", "商品画像パス4"),
        ("画像4", "商品画像パス5"),
        ("画像5", "商品画像パス6"),
        ("画像6", "商品画像パス7"),
        ("画像7", "商品画像パス8"),
        ("画像8", "商品画像パス9"),
        ("画像9", "商品画像パス10"),
        ("画像10", "商品画像パス11"),
    ]
    for label, header_name in image_keys:
        image_inputs[header_name] = st.text_input(label, value="")

# 画面最上部にタイトルを表示
st.title("AutoPage Converter")

# ブランドコード対応表（辞書形式）
BRAND_CODE_MAP = {
    "2328": "三菱",
    "3909": "ホンダ",
    "13208": "BMW",
    "14684": "スズキ",
    "15839": "トヨタ",
    "15840": "日産",
    "15841": "マツダ",
    "15842": "スバル",
    "15843": "ダイハツ",
    "18477": "レクサス",
    "18479": "ベンツ",
    "18480": "VW",
    "18482": "アウディ",
    "59744": "ポルシェ",
    "18496": "BMW",
    "18490": "VOLVO",
    "3148": "ジャガー",
    "34949": "三菱",
    "53377": "プール"
}

# 商品属性（値）14専用の対応表（CAR_BRAND_MAP）
CAR_BRAND_MAP = {
    "2328": "三菱",
    "3909": "ホンダ",
    "13208": "BMW",
    "14684": "スズキ",
    "15839": "トヨタ",
    "15840": "日産",
    "15841": "マツダ",
    "15842": "スバル",
    "15843": "ダイハツ",
    "18477": "レクサス",
    "18479": "メルセデス・ベンツ",
    "18480": "フォルクスワーゲン",
    "18482": "アウディ",
    "59744": "ポルシェ",
    "25434": "大野ゴム",
    "18485": "いすゞ",
    "61090": "日野自動車",
    "18517": "ミツオカ",
    "18495": "フィアット",
    "18489": "フォード",
    "18493": "アルファロメオ",
    "18494": "ルノー",
    "18491": "シボレー",
    "18503": "クライスラー",
    "18500": "ダッジ",
    "18499": "ジープ",
    "18496": "MINI",
    "18511": "サーブ",
    "5972": "オペル",
    "18515": "ランドローバー",
    "1637": "プジョー",
    "18497": "シトロエン",
    "18490": "ボルボ",
    "59744": "ポルシェ",
    "3148": "ジャガー(デイムラー)",
    "59746": "MG",
    "18501": "ローバー",
    "35910": "ヒュンダイ",
    "70329": "ISSE",
    "18516": "ベントレー",
    "34949": "三菱ふそう",
    "3170": "フェラーリ",
    "17073": "Kashimura",
    "25447": "大東プレス",
    "38074": "unknown",
    "53377": "INTEX",
    "18498": "BMWアルピナ",
    "18512": "スマート",
    "17097": "アイシン",
    "20287": "アバルト",
    "18505": "マセラティ",
    "2039": "ヤマハ",
    "14683": "カワサキ",
    "18509": "キャデラック"
}

CATEGORY_MAP = {
    'BMW': r'欧州車\BMW',
    'いすゞ': r'国産車\ISUZU',
    'アウディ': r'欧州車\AUDI',
    'アルファ ロメオ': r'欧州車\ALFA ROMEO',
    'シトロエン': r'欧州車',
    'ジャガー': r'欧州車\JAGUAR',
    'スズキ': r'国産車\SUZUKI',
    'スバル': r'国産車\SUBARU',
    'ダイハツ': r'国産車\DAIHATSU',
    'トヨタ': r'国産車\TOYOTA',
    'フォルクスワーゲン': r'欧州車\VolksWagen',
    'プジョー': r'欧州車\PEUGEOT',
    'ホンダ': r'国産車\HONDA',
    'ボルボ': r'欧州車\VOLVO',
    'ポルシェ': r'欧州車\PORSCHE',
    'マツダ': r'国産車\MAZDA',
    'ミニ': r'欧州車\BMW\MINI',
    'メルセデス・ベンツ': r'欧州車\Mercedes-Benz',
    'ランドローバー': r'欧州車\LANDROVER',
    'レクサス': r'国産車\TOYOTA',
    '三菱': r'国産車\MITSUBISHI',
    '日産': r'国産車\NISSAN',
    'スマート': r'欧州車\SMART'
}

BANNER_RULES = [
    {
        "name": "PREMIUM HAPAD",
        "must_keywords": ["PREMIUM HAPAD"],
        "or_keywords": ["パッド"],
        "excludes": [],
        "pc_banners": '<img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/imgrc0336018428.jpg" border="0">',
        "sp_banners": '<img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/imgrc0336018428.jpg" width="100%">'
    },
    {
        "name": "CAPSOL ラジエーター",
        "must_keywords": ["CAPSOL"],
        "or_keywords": ["ラジエーター"],
        "excludes": [],
        "pc_banners": '<img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/imgrc0331357316.jpg" border="0">',
        "sp_banners": '<img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/imgrc0331357316.jpg" width="100%">'
    },
    {
        "name": "CAPSOL オルタネーター",
        "must_keywords": ["CAPSOL"],
        "or_keywords": ["オルタ"],
        "excludes": [],
        "pc_banners": '<img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/imgrc0331395353.jpg" border="0">',
        "sp_banners": '<img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/imgrc0331395353.jpg" width="100%">'
    },
    {
        "name": "HAPAD ローター",
        "must_keywords": ["HAPAD"],
        "or_keywords": ["ローター"],
        "excludes": ["PREMIUM"],
        "pc_banners": '<img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/imgrc0330601774.jpg" border="0">',
        "sp_banners": '<img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/imgrc0330601774.jpg" width="100%">'
    },
    {
        "name": "HAPAD パッド",
        "must_keywords": ["HAPAD"],
        "or_keywords": ["パッド"],
        "excludes": ["PREMIUM"],
        "pc_banners": '<img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/imgrc0330575433.jpg" border="0">',
        "sp_banners": '<img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/imgrc0330575433.jpg" width="100%">'
    },
    {
        "name": "CAPSOL コンデンサー",
        "must_keywords": ["CAPSOL"],
        "or_keywords": ["コンデンサー"],
        "excludes": [],
        "pc_banners": '<img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/imgrc0332589124.jpg" border="0">',
        "sp_banners": '<img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/imgrc0332589124.jpg" width="100%">'
    },
    {
        "name": "CAPSOL ラジコン",
        "must_keywords": ["CAPSOL", "コンデンサー", "ラジエーター"],
        "or_keywords": [],
        "excludes": [],
        "pc_banners": '<img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/imgrc0331466899.jpg" border="0">',
        "sp_banners": '<img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/imgrc0331466899.jpg" width="100%">'
    },
    {
        "name": "CAPSOL スノーワイパー",
        "must_keywords": ["CAPSOL"],
        "or_keywords": ["スノーワイパー"],
        "excludes": [],
        "pc_banners": '<img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/imgrc0334050737.jpg" border="0">',
        "sp_banners": '<img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/imgrc0334050737.jpg" width="100%">'
    },
    {
        "name": "ALIC スターター",
        "must_keywords": ["ALIC"],
        "or_keywords": ["スターター"],
        "excludes": [],
        "pc_banners": '<img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/imgrc0335159669.jpg" border="0">',
        "sp_banners": '<img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/imgrc0335159669.jpg" width="100%">'
    },
    {
        "name": "CAPSOL ACコンプレッサー",
        "must_keywords": ["CAPSOL"],
        "or_keywords": ["ACコンプレッサー", "エアコンコンプレッサー"],
        "excludes": [],
        "pc_banners": '<img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/imgrc0332589124.jpg" border="0">',
        "sp_banners": '<img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/imgrc0332589124.jpg" width="100%">'
    },
    {
        "name": "CAPSOL O2センサー",
        "must_keywords": ["CAPSOL"],
        "or_keywords": ["O2センサー"],
        "excludes": [],
        "pc_banners": '<img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/imgrc0336919795.jpg" border="0">',
        "sp_banners": '<img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/imgrc0336919795.jpg" width="100%">'
    },
    {
        "name": "CAPSOL スターター",
        "must_keywords": ["CAPSOL"],
        "or_keywords": ["スターター"],
        "excludes": [],
        "pc_banners": '<img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/imgrc0338860944.jpg" border="0">',
        "sp_banners": '<img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/imgrc0338860944.jpg" width="100%">'
    },
    {
        "name": "CAPSOL NOXセンサー",
        "must_keywords": ["CAPSOL"],
        "or_keywords": ["NOXセンサー"],
        "excludes": [],
        "pc_banners": '<img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/imgrc0340011887.jpg" border="0">',
        "sp_banners": '<img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/imgrc0340011887.jpg" width="100%">'
    },
    {
        "name": "CAPSOL 強化イグニッションコイル",
        "must_keywords": ["CAPSOL"],
        "or_keywords": ["コイル", "イグニッションコイル"],
        "excludes": [],
        "pc_banners": '<img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/imgrc0340830822.jpg" border="0">',
        "sp_banners": '<img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/imgrc0340830822.jpg" width="100%">'
    },
    {
        "name": "水鉄砲",
        "must_keywords": [],
        "or_keywords": ["水風船", "水鉄砲"],
        "excludes": [],
        "pc_banners": '<img src="https://image.rakuten.co.jp/s-o-l/cabinet/11276663/12112622/watergun-01.jpg" border="0">',
        "sp_banners": '<img src="https://image.rakuten.co.jp/s-o-l/cabinet/11276663/12112622/watergun-01.jpg" width="100%">'
    },
        {
        "name": "CAPSOL O2センサー",
        "must_keywords": ["CAPSOL"],
        "or_keywords": ["O2センサー"],
        "excludes": [],
        "pc_banners": '<img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/imgrc0336919795.jpg" border="0">',
        "sp_banners": '<img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/imgrc0336919795.jpg" width="100%">'
    },
    {
        "name": "CAPSOL ファンモーター",
        "must_keywords": ["CAPSOL"],
        "or_keywords": ["ファンモーター"],
        "excludes": [],
        "pc_banners": '<img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/imgrc0332449028.jpg" border="0">',
        "sp_banners": '<img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/imgrc0332449028.jpg" width="100%">'
    }
]

# ship-weightに応じた販売価格の加算金額テーブル
SHIP_WEIGHT_PRICE_MAP = {
    0: 770,
    100: 1100,
    1: 1650,
    1000: 3850,
    5000: 2860,
    10000: 5500,
    50000: 3300,
    1000000: 11000
}

# 要件に定義された必須カラム
REQUIRED_COLUMNS = ['code', 'name', 'additional1', 'ship-weight', 'item-image-urls', 'brand-code', 'price']

# 置換用定数定義
target_header = '<center><IMG SRC="https://shopping.c.yimg.jp/lib/solltd/960.jpg"><BR><BR><IMG SRC="https://shopping.c.yimg.jp/lib/solltd/parts01.gif"><BR><BR></center>'
target_header_supplies = '''<center><IMG SRC="https://shopping.c.yimg.jp/lib/solltd/960.jpg"><BR><BR><IMG SRC="https://shopping.c.yimg.jp/lib/solltd/supplies01.gif"><BR><BR></center>'''

rakuten_header = """<div align="left"><img src="https://image.rakuten.co.jp/s-o-l/cabinet/ninteimb.gif" border="0"><br><table border="0" cellpadding="1" cellspacing="1"><tbody><tr><td bgcolor="#999999" height="44" width="745" align="left"><center><b><font size="+1">商品詳細</font></b></center><table bgcolor="#ffffff" border="0" cellpadding="3" cellspacing="0" width="745"><tbody><tr height="25"><td bgcolor="#ffffff" width="745" align="left"><font size="-1">"""

# 用品専用PCヘッダーの定義
rakuten_header_supplies = """<div align="left"><table border="0" cellpadding="1" cellspacing="1"><tbody><tr><td bgcolor="#999999" height="44" width="745" align="left"><center><b><font size="+1">商品詳細</font></b></center><table bgcolor="#ffffff" border="0" cellpadding="3" cellspacing="0" width="745"><tbody><tr height="25"><td bgcolor="#ffffff" width="745" align="left"><font size="-1">"""
rakuten_header_parts010 = rakuten_header
rakuten_header_parts03 = rakuten_header

target_footer = '<B>●保証期間</B><BR>商品到着後6ヶ月間の商品保証を致します。<BR>この商品の初期不良期間は商品到着後14日間です。<br>当店側のミスでお手元に届いた商品が違った場合は、商品到着後14日間以内での対応となりますので、速やかな商品確認をお願い致します。<br><br>'
target_footer_supplies = '''<B>●保証期間</B><BR>商品到着後14日以内の保証となります。<BR>当店側のミスでお手元に届いた商品が違った場合は、商品到着後14日以内での対応となりますので、速やかな商品確認をお願い致します。<br>保証内容はご購入頂いた商品のみとなります。<BR>万が一商品に不具合が生じた場合新たに商品のご手配をさせて頂きますが、ご手配できない場合には商品代金のみご返金させて頂きます。<BR>商品交換時に発生する費用および損害等は保証できませんのでご了承下さい。<BR>保証申請時には商品の不良申請書または診断結果および診断書【コピーでも可】・お車の車検証をご提出いただく必要がございます。<BR>また症状や状態によっては商品の状態の確認がとれるお写真をいただく場合もございます。<BR>取付ミスによる不具合や破損、加工済は保証対象外となります。<br><br>'''

target_header_parts010 = '<center><IMG SRC="https://shopping.c.yimg.jp/lib/solltd/960.jpg"><BR><BR><IMG SRC="https://shopping.c.yimg.jp/lib/solltd/parts010.gif"><BR><BR></center>'
target_footer_parts010 = target_footer

# ==============================================================================
# 店舗共通フッター定数 (ユーザー編集用)
# ==============================================================================

# 1. PC用 共通フッター (通常配送用)
COMMON_FOOTER = """<div align="left"><table width="748"><tbody><tr><td align="left"></td></tr></tbody></table></div><div align="left"><table bgcolor="#999999" border="0" cellpadding="0" cellspacing="1" width="745" height="518"><tbody><tr><td align="center" width="745" colspan="2"><b><font size="+1">INFORMATION</font></b></td></tr><tr><td colspan="2"><table bgcolor="#ffffff" border="0" cellpadding="5" cellspacing="1" width="745"><tbody><tr><td valign="top" align="left" width="360" height="467"><table border="0" cellpadding="3" cellspacing="1" width="355"><tbody><tr><td bgcolor="#f0f0f0" height="16"><font color="#000000"><b>●お支払いについて</b></font></td></tr></tbody></table><table border="0" cellpadding="3" cellspacing="1" width="355"><tbody><tr><td><font color="#000000" size="2">・クレジットカード決済<br>・銀行振込（前払）<br>・セブンイレブン（前払）<br>・ローソン、郵便局ATM等（前払）<br>・後払い決済<br>・代金引換（現金のみ）</font></td></tr></tbody></table><table border="0" cellpadding="3" cellspacing="1" width="355"><tbody><tr><td bgcolor="#f0f0f0" height="16"><font color="#000000"><b>●発送方法について</b></font></td></tr></tbody></table><table border="0" cellpadding="3" cellspacing="1" width="355"><tbody><tr><td><font color="#000000" size="2">佐川急便または、西濃運輸・ゆうパック・クロネコヤマト・福山通運など当社指定の運送会社にて発送となります。<BR>※運送便のご指定は一切できません。<BR><BR>営業所留めを希望される場合、ご注文時にご希望の営業所名・営業所住所をご要望欄へご指定下さい。<BR>※発送予定の運送会社を確認されたい方は、ご注文前に必ずお問い合わせください。<br></font></td></tr><tr><td bgcolor="#f0f0f0" color="#000000"><b>●発送のタイミングについて</b></font></td></tr></tbody></table><table border="0" cellpadding="3" cellspacing="1" width="355"><tbody><tr><td><font color="#ff0000" size="2"><b>当日発送18時まで可能です。</b></font><font color="#000000" size="2"><br>ご注文のタイミングによっては、当日発送が出来ない場合がございますのでご了承下さい。<br><br>※下記該当の場合は当日発送できません。<br>・当店が休みの場合（翌営業日の発送になります）。<br>・お支払方法が銀行振込みで、18時までにお振込みの確認が取れなかった場合(15時以降のお振込みの場合、当社着金が翌営業日になる可能性がございます)。<br><br>決済の審査が必要なお支払い方法（クレジットカード・後払い決済）をご選択された場合、<br>楽天の審査にお時間をいただくことがあり、当日発送ができない場合がございます。予めご了承ください。<br>※銀行振込、コンビニお支払い等、前払い制の決済方法をご選択された場合は、ご入金確認が完了してからの発送となります。</font></font></td></tr></tbody></table></td><td valign="top" align="left" width="360"><table border="0" cellpadding="3" cellspacing="1" width="360"><tbody><tr><td bgcolor="#f0f0f0" colspan="2"><b>●保証について</b></td></tr><tr><td colspan="2"><font color="#000000" size="2">商品到着後6か月間の商品保証を致します。<br>当店側のミスでお手元に届いた商品が違った場合は、商品到着後14日以内での対応となりますので、速やかな商品確認をお願い致します。<br>保証内容はご購入頂いた商品のみとなります。<br>万が一商品に不具合が生じた場合新たに商品のご手配をさせて頂きますが、ご手配できない場合には商品代金のみご返金させて頂きます。<br>商品交換時に発生する費用および損害等は保証できませんのでご了承下さい。<br>取付ミスによる不具合や破損、加工済は保証対象外となります。</font></td></tr><tr><td bgcolor="#f0f0f0" colspan="2"><b>●お取引に関して</b></td></tr><tr><td colspan="2"><font color="#000000" size="2">お振込でお支払の際は、ご注文後5営業日以内にお手続きお願い致します。ご連絡やお手続き頂けない場合には、「お客様都合」によるキャンセルをさせて頂く場合がございます。ご注意ください。<br><br>ご注文の場合には同意されたものとみなさせて頂きますので、ご不明な点がある場合は、必ずご注文前にお問い合わせ下さい。</font></td></tr><tr><td bgcolor="#f0f0f0" colspan="2"><b>●その他</b></td></tr><tr><td colspan="2"><font color="#000000" size="2">パッケージにダメージがある場合が御座います。<br>写真撮影の為、パッケージを開封する場合が御座います。<br><br><a href="https://www.rakuten.co.jp/s-o-l/info2.html">SHOPPING GUIDE</a>をご確認の上ご注文お願いします。</font></td></tr><tr><td bgcolor="#f0f0f0" colspan="2"><b>●お問い合わせ先</b></td></tr><tr><td colspan="2"><font color="#000000" size="2">【株式会社エスオーエル】<br>〒221-0031<br>神奈川県横浜市神奈川区新浦島町一丁目1番地25 <br>GRC横浜ベイリサーチパーク 10階<br>TEL：045-450-6218 / FAX：045-330-4015<br>e-mail：<a href="mailto:sol-info1@s-o-l.co.jp">sol-info1@s-o-l.co.jp</a><br><font size="-1">営業時間<font color="#000000" size="2">：10：00〜18：00<br>(土・日・祝祭日を除く)</font></font></td></tr><tr><td bgcolor="#f0f0f0" colspan="2"><font color="#000000"><b>●出荷倉庫</b></font></td></tr><tr><td width="356" colspan="2"><font size="-1"><font color="#000000" size="2"><font size="-1">【株式会社エスオーエル パーツセンター】<BR>〒292-0824<BR>千葉県木更津市小浜276-3</font></font></font></td></tr></tbody></table></td></tr></tbody></table></td></tr></tbody></table></div>"""

# 1-2. PC用 共通フッター (用品用、保証14日)
COMMON_FOOTER_SUPPLIES = """<div align="left"><table width="748"><tbody><tr><td align="left"></td></tr></tbody></table></div><div align="left"><table bgcolor="#999999" border="0" cellpadding="0" cellspacing="1" width="745" height="518"><tbody><tr><td align="center" width="745" colspan="2"><b><font size="+1">INFORMATION</font></b></td></tr><tr><td colspan="2"><table bgcolor="#ffffff" border="0" cellpadding="5" cellspacing="1" width="745"><tbody><tr><td valign="top" align="left" width="360" height="467"><table border="0" cellpadding="3" cellspacing="1" width="355"><tbody><tr><td bgcolor="#f0f0f0" height="16"><font color="#000000"><b>●お支払いについて</b></font></td></tr></tbody></table><table border="0" cellpadding="3" cellspacing="1" width="355"><tbody><tr><td><font color="#000000" size="2">・クレジットカード決済<br>・銀行振込（前払）<br>・セブンイレブン（前払）<br>・ローソン、郵便局ATM等（前払）<br>・後払い決済<br>・代金引換（現金のみ）</font></td></tr></tbody></table><table border="0" cellpadding="3" cellspacing="1" width="355"><tbody><tr><td bgcolor="#f0f0f0" height="16"><font color="#000000"><b>●発送方法について</b></font></td></tr></tbody></table><table border="0" cellpadding="3" cellspacing="1" width="355"><tbody><tr><td><font color="#000000" size="2">佐川急便または、西濃運輸・ゆうパック・クロネコヤマト・福山通運など当社指定の運送会社にて発送となります。<BR>※運送便のご指定は一切できません。<BR><BR>営業所留めを希望される場合、ご注文時にご希望の営業所名・営業所住所をご要望欄へご指定下さい。<BR>※発送予定の運送会社を確認されたい方は、ご注文前に必ずお問い合わせください。<br></font></td></tr><tr><td bgcolor="#f0f0f0" color="#000000"><b>●発送のタイミングについて</b></font></td></tr></tbody></table><table border="0" cellpadding="3" cellspacing="1" width="355"><tbody><tr><td><font color="#ff0000" size="2"><b>当日発送18時まで可能です。</b></font><font color="#000000" size="2"><br>ご注文のタイミングによっては、当日発送が出来ない場合がございますのでご了承下さい。<br><br>※下記該当の場合は当日発送できません。<br>・当店が休みの場合（翌営業日の発送になります）。<br>・お支払方法が銀行振込みで、18時までにお振込みの確認が取れなかった場合(15時以降のお振込みの場合、当社着金が翌営業日になる可能性がございます)。<br><br>決済の審査が必要なお支払い方法（クレジットカード・後払い決済）をご選択された場合、<br>楽天の審査にお時間をいただくことがあり、当日発送ができない場合がございます。予めご了承ください。<br>※銀行振込、コンビニお支払い等、前払い制の決済方法をご選択された場合は、ご入金確認が完了してからの発送となります。</font></font></td></tr></tbody></table></td><td valign="top" align="left" width="360"><table border="0" cellpadding="3" cellspacing="1" width="360"><tbody><tr><td bgcolor="#f0f0f0" colspan="2"><b>●保証について</b></td></tr><tr><td colspan="2"><font color="#000000" size="2">商品到着後14日以内の保証となります。<br>当店側のミスでお手元に届いた商品が違った場合は、商品到着後14日以内での対応となりますので、速やかな商品確認をお願い致します。<br>保証内容はご購入頂いた商品のみとなります。<br>万が一商品に不具合が生じた場合新たに商品のご手配をさせて頂きますが、ご手配できない場合には商品代金のみご返金させて頂きます。<br>商品交換時に発生する費用および損害等は保証できませんのでご了承下さい。<br>保証申請時には商品の不良申請書または診断結果および診断書【コピーでも可】・お車の車検証をご提出いただく必要がございます。<br>また症状や状態によっては商品の状態の確認がとれるお写真をいただく場合もございます。<br>取付ミスによる不具合や破損、加工済は保証対象外となります。</font></td></tr><tr><td bgcolor="#f0f0f0" colspan="2"><b>●お取引に関して</b></td></tr><tr><td colspan="2"><font color="#000000" size="2">お振込でお支払の際は、ご注文後5営業日以内にお手続きお願い致します。ご連絡やお手続き頂けない場合には、「お客様都合」によるキャンセルをさせて頂く場合がございます。ご注意ください。<br><br>ご注文の場合には同意されたものとみなさせて頂きますので、ご不明な点がある場合は、必ずご注文前にお問い合わせ下さい。</font></td></tr><tr><td bgcolor="#f0f0f0" colspan="2"><b>●その他</b></td></tr><tr><td colspan="2"><font color="#000000" size="2">パッケージにダメージがある場合が御座います。<br>写真撮影の為、パッケージを開封する場合が御座います。<br><br><a href="https://www.rakuten.co.jp/s-o-l/info2.html">SHOPPING GUIDE</a>をご確認の上ご注文お願いします。</font></td></tr><tr><td bgcolor="#f0f0f0" colspan="2"><b>●お問い合わせ先</b></td></tr><tr><td colspan="2"><font color="#000000" size="2">【株式会社エスオーエル】<br>〒221-0031<br>神奈川県横浜市神奈川区新浦島町一丁目1番地25 <br>GRC横浜ベイリサーチパーク 10階<br>TEL：045-450-6218 / FAX：045-330-4015<br>e-mail：<a href="mailto:sol-info1@s-o-l.co.jp">sol-info1@s-o-l.co.jp</a><br><font size="-1">営業時間<font color="#000000" size="2">：10：00〜18：00<br>(土・日・祝祭日を除く)</font></font></td></tr><tr><td bgcolor="#f0f0f0" colspan="2"><font color="#000000"><b>●出荷倉庫</b></font></td></tr><tr><td width="356" colspan="2"><font size="-1"><font color="#000000" size="2"><font size="-1">【株式会社エスオーエル パーツセンター】<BR>〒292-0824<BR>千葉県木更津市小浜276-3</font></font></font></td></tr></tbody></table></td></tr></tbody></table></td></tr></tbody></table></div>"""

# 2. PC用 共通フッター (クリックポスト用)
COMMON_FOOTER_CLICKPOST = """<div align="left"><table width="748"><tbody><tr><td align="left"></td></tr></tbody></table></div><div align="left"><table bgcolor="#999999" border="0" cellpadding="0" cellspacing="1" width="745" height="518"><tbody><tr><td align="center" width="745" colspan="2"><b><font size="+1">INFORMATION</font></b></td></tr><tr><td colspan="2"><table bgcolor="#ffffff" border="0" cellpadding="5" cellspacing="1" width="745"><tbody><tr><td valign="top" align="left" width="360" height="467"><table border="0" cellpadding="3" cellspacing="1" width="355"><tbody><tr><td bgcolor="#f0f0f0" height="16"><font color="#000000"><b>●お支払いについて</b></font></td></tr></tbody></table><table border="0" cellpadding="3" cellspacing="1" width="355"><tbody><tr><td><font color="#000000" size="2">・クレジットカード決済<br>・銀行振込（前払）<br>・セブンイレブン（前払）<br>・ローソン、郵便局ATM等（前払）<br>・後払い決済</font></td></tr></tbody></table><table border="0" cellpadding="3" cellspacing="1" width="355"><tbody><tr><td bgcolor="#f0f0f0" height="16"><font color="#000000"><b>●発送方法について</b></font></td></tr></tbody></table><table border="0" cellpadding="3" cellspacing="1" width="355"><tbody><tr><td><font color="#000000" size="2">クリックポストでの発送になります。<br><br>・日時指定や代引きは出来ません。<br>・手渡しではなく、ポストへの投函になります。<br>・配送日数はおおむね3日前後になります。<br>・追跡可能ですが、紛失や破損等による保証はありませんのでご了承の上ご購入お願いします。<br>・発送は発送連絡を行わせて頂いた当日の夕方、ポストへ投函させて頂きます。<br>・当方の地域柄、集荷時間等の関係上、追跡番号がインターネット上に反映されるに1〜2日程度かかる場合がございます。予めご了承ください。<br>例：発送連絡日(20XX/4/1)→ネット上の集荷日(20XX/4/3)<br></font></td></tr><tr><td bgcolor="#f0f0f0" color="#000000"><b>●発送のタイミングについて</b></td></tr></tbody></table><table border="0" cellpadding="3" cellspacing="1" width="355"><tbody><tr><td><font color="#ff0000" size="2"><b>平日は当日発送18時まで可能です。<br>（土曜・日曜は当日発送9時まで）</b></font><font color="#000000" size="2"><br>ご注文のタイミングによっては、当日発送が出来ない場合がございますのでご了承下さい。<br><br>※下記該当の場合は当日発送できません。<br>・当店が休みの場合（翌営業日の発送になります）。<br>・お支払方法が銀行振込みで、18時までにお振込みの確認が取れなかった場合(15時以降のお振込みの場合、当社着金が翌営業日になる可能性がございます)。<br><br>決済の審査が必要なお支払い方法（クレジットカード・後払い決済）をご選択された場合、<br>楽天の審査にお時間をいただくことがあり、当日発送ができない場合がございます。予めご了承ください。<br>※銀行振込、コンビニお支払い等、前払い制の決済方法をご選択された場合は、ご入金確認が完了してからの発送となります。</font></td></tr></tbody></table></td><td valign="top" align="left" width="360"><table border="0" cellpadding="3" cellspacing="1" width="360"><tbody><tr><td bgcolor="#f0f0f0" colspan="2"><b>●保証について</b></td></tr><tr><td colspan="2"><font color="#000000" size="2">商品到着後6か月間の商品保証を致します。<br>当店側のミスでお手元に届いた商品が違った場合は、商品到着後14日以内での対応となりますので、速やかな商品確認をお願い致します。<br>保証内容はご購入頂いた商品のみとなります。<br>万が一商品に不具合が生じた場合新たに商品のご手配をさせて頂きますが、ご手配できない場合には商品代金のみご返金させて頂きます。<br>商品交換時に発生する費用および損害等は保証できませんのでご了承下さい。<br>取付ミスによる不具合や破損、加工済は保証対象外となります。</font></td></tr><tr><td bgcolor="#f0f0f0" colspan="2"><b>●お取引に関して</b></td></tr><tr><td colspan="2"><font color="#000000" size="2">お振込でお支払の際は、ご注文後5営業日以内にお手続きお願い致します。ご連絡やお手続き頂けない場合には、「お客様都合」によるキャンセルをさせて頂く場合がございます。ご注意ください。<br><br>ご注文の場合には同意されたものとみなさせて頂きますので、ご不明な点がある場合は、必ずご注文前にお問い合わせ下さい。</font></td></tr><tr><td colspan="2" bgcolor="#f0f0f0"><font color="#000000"><b>●その他</b></font></td></tr><tr><td colspan="2"><font size="-1">パッケージにダメージがある場合が御座います。<br>写真撮影の為、パッケージを開封する場合が御座います。</font></td></tr><tr><td bgcolor="#f0f0f0" colspan="2"><font color="#000000"><b>●お問い合わせ先</b></font></td></tr><tr><td width="356" colspan="2"><font color="#000000" size="2">【株式会社エスオーエル】<br>〒221-0031<br>神奈川県横浜市神奈川区新浦島町一丁目1番地25 <br>GRC横浜ベイリサーチパーク 10階<br>TEL：045-450-6218 / FAX：045-330-4015<br>※土曜・日曜はお電話でのお問い合わせは承っておりません。<br>e-mail：<a href="mailto:sol-info1@s-o-l.co.jp">sol-info1@s-o-l.co.jp</a></font><br><font size="-1">営業時間<font color="#000000" size="2">：10：00〜18：00<br>(祝祭日を除く)</font></font></td></tr><tr><td bgcolor="#f0f0f0" colspan="2"><font color="#000000"><b>●出荷倉庫</b></font></td></tr><tr><td width="356" colspan="2"><font size="-1"><font color="#000000" size="2"><font size="-1">【株式会社エスオーエル パーツセンター】<BR>〒292-0824<BR>千葉県木更津市小浜276-3</font></font></font></td></tr></tbody></table></td></tr></tbody></table></td></tr></tbody></table></div>"""

# 3. スマホ用 共通フッター (通常用、保証6ヶ月)
COMMON_SP_FOOTER = """<b>●お支払いについて</b><br>・クレジットカード決済<br>・銀行振込（前払）<br>・セブンイレブン（前払）<br>・ローソン、郵便局ATM等（前払）<br>・後払い決済<br>・代金引換（現金のみ）<br><br><b>●発送方法</b><br>佐川急便または、西濃運輸・ゆうパック・クロネコヤマト・福山通運など当社指定の運送会社にて発送となります。<BR>※運送便のご指定は一切できません。<BR>  <BR>営業所留めを希望される場合、ご注文時にご希望の営業所名・営業所住所をご要望欄へご指定下さい。 <BR> ※発送予定の運送会社を確認されたい方は、ご注文前に必ずお問い合わせください。<br><br><b>●発送のタイミング</b><br><b>当日発送18時まで可能です。</b><br>ご注文のタイミングによっては、当日発送が出来ない場合がございますのでご了承下さい。<br><br>※下記該当の場合は当日発送できません。<br>・当店が休みの場合（翌営業日の発送になります）。<br>・お支払方法が銀行振込みで、18時までにお振込みの確認が取れなかった場合(15時以降のお振込みの場合、当社着金が翌営業日になる可能性がございます。)<br><br>決済の審査が必要なお支払い方法（クレジットカード・後払い決済）をご選択された場合、<br>楽天の審査にお時間をいただくことがあり、当日発送ができない場合がございます。予めご了承ください。<br>※銀行振込、コンビニお支払い等、前払い制の決済方法をご選択された場合は、ご入金確認が完了してからの発送となります。<br><br><b>●保証</b><br>商品到着後6か月間の商品保証を致します。<br>当店側のミスでお手元に届いた商品が違った場合は、商品到着後14日以内での対応となりますので、速やかな商品確認をお願い致します。<br>保証内容はご購入頂いた商品のみとなります。<br>万が一商品に不具合が生じた場合新たに商品のご手配をさせて頂きますが、ご手配できない場合には商品代金のみご返金させて頂きます。<br>商品交換時に発生する費用および損害等は保証できませんのでご了承下さい。<br>取付ミスによる不具合や破損、加工済は保証対象外となります。<br><br><b>●お取引に関して</b><br>お振込でお支払の際は、ご注文後5営業日以内にお手続きお願い致します。ご連絡やお手続き頂けない場合には、「お客様都合」によるキャンセルをさせて頂く場合がございます。ご注意ください。<br><br>ご注文の場合には同意されたものとみなさせて頂きますので、ご不明な点がある場合は、必ずご注文前にお問い合わせ下さい。<br><br><b>●その他</b><br>パッケージにダメージがある場合が御座います。<br>写真撮影の為、パッケージを開封する場合が御座います。<br><br><a href="https://www.rakuten.co.jp/s-o-l/info2.html">SHOPPING GUIDE</a>をご確認の上ご注文お願いします。<br><br><b>●お問い合わせ先</b><br>【株式会社エスオーエル】<br>〒221-0031<br>神奈川県横浜市神奈川区新浦島町一丁目1番地25 <br>GRC横浜ベイリサーチパーク 10階<br>TEL：045-450-6218 / FAX：045-330-4015<br>e-mail：<a href="mailto:sol-info1@s-o-l.co.jp">sol-info1@s-o-l.co.jp</a><br>営業時間：10：00〜18：00<br>(土・日・祝祭日を除く)<br><br><b>●出荷倉庫<br></b>【株式会社エスオーエル パーツセンター】<br>〒292-0824<br>千葉県木更津市小浜276-3"""

# 4. スマホ用 共通フッター (Supplies用、保証14日)
COMMON_SP_FOOTER_SUPPLIES = """<b>●お支払いについて</b><br>・クレジットカード決済<br>・銀行振込（前払）<br>・セブンイレブン（前払）<br>・ローソン、郵便局ATM等（前払）<br>・後払い決済<br>・代金引換（現金のみ）<br><br><b>●発送方法</b><br>佐川急便または、西濃運輸・ゆうパック・クロネコヤマト・福山通運など当社指定の運送会社にて発送となります。<BR>※運送便のご指定は一切できません。<BR><BR>営業所留めを希望される場合、ご注文時にご希望の営業所名・営業所住所をご要望欄へご指定下さい。 <BR> ※発送予定の運送会社を確認されたい方は、ご注文前に必ずお問い合わせください。<br><br><b>●発送のタイミング</b><br><b>当日発送18時まで可能です。</b><br>ご注文のタイミングによっては、当日発送が出来ない場合がございますのでご了承下さい。<br><br>※下記該当の場合は当日発送できません。<br>・当店が休みの場合（翌営業日の発送になります）。<br>・お支払方法が銀行振込みで、18時までにお振込みの確認が取れなかった場合(15時以降のお振込みの場合、当社着金が翌営業日になる可能性がございます。)<br><br>決済の審査が必要なお支払い方法（クレジットカード・後払い決済）をご選択された場合、<br>楽天の審査にお時間をいただくことがあり、当日発送ができない場合がございます。予めご了承ください。<br>※銀行振込、コンビニお支払い等、前払い制の決済方法をご選択された場合は、ご入金確認が完了してからの発送となります。<br><br><b>●保証</b><br>商品到着後14日以内の保証となります。<br>当店側のミスでお手元に届いた商品が違った場合は、商品到着後14日以内での対応となりますので、速やかな商品確認をお願い致します。<br>保証内容はご購入頂いた商品のみとなります。<br>万が一商品に不具合が生じた場合新たに商品のご手配をさせて頂きますが、ご手配できない場合には商品代金のみご返金させて頂きます。<br>商品交換時に発生する費用および損害等は保証できませんのでご了承下さい。<br>保証申請時には商品の不良申請書または診断結果および診断書【コピーでも可】・お車の車検証をご提出いただく必要がございます。<br>また症状や状態によっては商品の状態の確認がとれるお写真をいただく場合もございます。<br>取付ミスによる不具合や破損、加工済は保証対象外となります。<br><br><b>●お取引に関して</b><br>お振込でお支払の際は、ご注文後5営業日以内にお手続きお願い致します。ご連絡やお手続き頂けない場合には、「お客様都合」によるキャンセルをさせて頂く場合がございます. ご注意ください。<br>ご注文の場合には同意されたものとみなさせて頂きますので、ご不明な点がある場合は、必ずご注文前にお問い合わせ下さい。<br><br><b>●その他</b><br>パッケージにダメージがある場合が御座います。<br>写真撮影の為、パッケージを開封する場合が御座います。<br><br><a href="https://www.rakuten.co.jp/s-o-l/info2.html">SHOPPING GUIDE</a>をご確認の上ご注文お願いします。<br><br><b>●お問い合わせ先</b><br>【株式会社エスオーエル】<br>〒221-0031<br>神奈川県横浜市神奈川区新浦島町一丁目1番地25 <br>GRC横浜ベイリサーチパーク 10階<br>TEL：045-450-6218 / FAX：045-330-4015<br>e-mail：<a href="mailto:sol-info1@s-o-l.co.jp">sol-info1@s-o-l.co.jp</a><br>営業時間：10：00〜18：00<br>(土・日・祝祭日を除く)<br><br><b>●出荷倉庫<br></b>【株式会社エスオーエル パーツセンター】<br>〒292-0824<br>千葉県木更津市小浜276-3"""

# 5. スマホ用 共通フッター (Supplies02用、西濃発送、保証14日)
COMMON_SP_FOOTER_SUPPLIES02 = """<b>●お支払いについて</b><br>・クレジットカード決済<br>・銀行振込<br>・後払い決済<br>・セブンイレブン（前払）<br>・ローソン、郵便局ATM等（前払）<br><br><b>●発送方法</b><br>西濃運輸または福山通運での発送になります。<BR>※運送便のご指定は一切できません。<BR> ※個人宅様宛の配送はできません。<BR><BR>営業所留めを希望される場合、ご注文時にご希望の営業所名・営業所住所をご要望欄へご指定下さい。 <BR> ※発送予定の運送会社を確認されたい方は、ご注文前に必ずお問い合わせください。<br><br><b>●発送のタイミング</b><br><b>当日発送16時まで可能です。</b><br>ご注文のタイミングによっては、当日発送が出来ない場合がございますのでご了承下さい。<br><br>※下記該当の場合は当日発送できません。<br>・当店が休みの場合（翌営業日の発送になります）。<br>・お支払方法が銀行振込みで、16時までにお振込みの確認が取れなかった場合(15時以降のお振込みの場合、当社着金が翌営業日になる可能性がございます。)<br><br>決済の審査が必要なお支払い方法（クレジットカード・後払い決済）をご選択された場合、<br>楽天の審査にお時間をいただくことがあり、当日発送ができない場合がございます。予めご了承ください。<br>※銀行振込、コンビニお支払い等、前払い制の決済方法をご選択された場合は、ご入金確認が完了してからの発送となります。<br><br><b>●保証</b><br>商品到着後14日以内の保証となります。<br>当店側のミスでお手元に届いた商品が違った場合は、商品到着後14日以内での対応となりますので、速やかな商品確認をお願い致します。<br>保証内容はご購入頂いた商品のみとなります。<br>万が一商品に不具合が生じた場合新たに商品のご手配をさせて頂きますが、ご手配できない場合には商品代金のみご返金させて頂きます。<br>商品交換時に発生する費用および損害等は保証できませんのでご了承下さい。<br>保証申請時には商品の不良申請書または診断結果および診断書【コピーでも可】・お車の車検証をご提出いただく必要がございます。<br>また症状や状態によっては商品の状態の確認がとれるお写真をいただく場合もございます。<br>取付ミスによる不具合や破損、加工済は保証対象外となります。<br><br><b>●お取引に関して</b><br>お振込でお支払の際は、ご注文後5営業日以内にお手続きお願い致します。ご連絡やお手続き頂けない場合には、「お客様都合」によるキャンセルをさせて頂く場合がございます。ご注意ください。<br><br>ご注文の場合には同意されたものとみなさせて頂きますので、ご不明な点がある場合は、必ずご注文前にお問い合わせ下さい。<br><br><b>●その他</b><br>パッケージにダメージがある場合が御座います。<br>写真撮影の為、パッケージを開封する場合が御座います。<br><br><a href="https://www.rakuten.co.jp/s-o-l/info2.html">SHOPPING GUIDE</a>をご確認の上ご注文お願いします。<br><br><b>●お問い合わせ先</b><br>【株式会社エスオーエル】<br>〒221-0031<br>神奈川県横浜市神奈川区新浦島町一丁目1番地25 <br>GRC横浜ベイリサーチパーク　10階<br>TEL：045-450-6218 / FAX：045-330-4015<br>e-mail：<a href="mailto:sol-info1@s-o-l.co.jp">sol-info1@s-o-l.co.jp</a><br>営業時間：10：00〜18：00<br>(土・日・祝祭日を除く)<br><br><b>●出荷倉庫<br></b>【株式会社エスオーエル　パーツセンター】<br>〒292-0824<br>千葉県木更津市小浜276-3"""

# 6. スマホ用 共通フッター (クリックポスト通常用、保証6ヶ月)
COMMON_SP_FOOTER_CLICKPOST = """<b>●お支払いについて</b><br>・クレジットカード決済<br>・銀行振込（前払）<br>・セブンイレブン（前払）<br>・ローソン、郵便局ATM等（前払）<br>・後払い決済<br><br><b>●発送方法</b><br>クリックポストでの発送になります。<br><br>・日時指定や代引きは出来ません。<br>・手渡しではなく、ポストへの投函になります。<br>・配送日数はおおむね3日前後になります。<br>・追跡可能ですが、紛失や破損等による保証はありませんのでご了承の上ご購入お願いします。<br>・発送は発送連絡を行わせて頂いた当日の夕方、ポストへ投函させて頂きます。<br>・当方の地域柄、集荷時間等の関係上、追跡番号がインターネット上に反映されるに1〜2日程度かかる場合がございます。予めご了承ください。<br>例：発送連絡日(20XX/4/1)→ネット上の集荷日(20XX/4/3)<br><br><b>●発送のタイミング</b><br><b>平日は当日発送18時まで可能です。<br>（土曜・日曜は当日発送9時まで）</b><br>ご注文のタイミングによっては、当日発送が出来ない場合がございますのでご了承下さい。<br><br>※下記該当の場合は当日発送できません。<br>・当店が休みの場合（翌営業日の発送になります）。<br>・お支払方法が銀行振込みで、18時までにお振込みの確認が取れなかった場合(15時以降のお振込みの場合、当社着金が翌営業日になる可能性がございます。)<br><br>決済の審査が必要なお支払い方法（クレジットカード・後払い決済）をご選択された場合、<br>楽天の審査にお時間をいただくことがあり、当日発送ができない場合がございます。予めご了承ください。<br>※銀行振込、コンビニお支払い等、前払い制の決済方法をご選択された場合は、ご入金確認が完了してからの発送となります。<br><br><b>●保証</b><br>商品到着後6か月間の商品保証を致します。<br>当店側のミスでお手元に届いた商品が違った場合は、商品到着後14日以内での対応となりますので、速やかな商品確認をお願い致します。<br>保証内容はご購入頂いた商品のみとなります。<br>万が一商品に不具合が生じた場合新たに商品のご手配をさせて頂きますが、ご手配できない場合には商品代金のみご返金させて頂きます。<br>商品交換時に発生する費用および損害等は保証できませんのでご了承下さい。<br>取付ミスによる不具合や破損、加工済は保証対象外となります。<br><br><b>●お取引に関して</b><br>お振込でお支払の際は、ご注文後5営業日以内にお手続きお願い致します。ご連絡やお手続き頂けない場合には、「お客様都合」によるキャンセルをさせて頂く場合がございます。ご注意ください。<br><br>ご注文の場合には同意されたものとみなさせて頂きますので、ご不明な点がある場合は、必ずご注文前にお問い合わせ下さい。<br><br><b>●その他</b><br>パッケージにダメージがある場合が御座います。<br>写真撮影の為、パッケージを開封する場合が御座います。<br><br><a href="https://www.rakuten.co.jp/s-o-l/info2.html">SHOPPING GUIDE</a>をご確認の上ご注文お願いします。<br><br><b>●お問い合わせ先</b><br>【株式会社エスオーエル】<br>〒221-0031<br>神奈川県横浜市神奈川区新浦島町一丁目1番地25 <br>GRC横浜ベイリサーチパーク　10階<br>TEL：045-450-6218 / FAX：045-330-4015<br>※土曜・日曜はお電話でのお問い合わせは承っておりません。<br>e-mail：<a href="mailto:sol-info1@s-o-l.co.jp">sol-info1@s-o-l.co.jp</a><br>営業時間：10：00〜18：00<br>(祝祭日を除く)<br><br><b>●出荷倉庫<br></b>【株式会社エスオーエル　パーツセンター】<br>〒292-0824<br>千葉県木更津市小浜276-3"""

# 7. スマホ用 共通フッター (クリックポストSupplies用、保証14日)
COMMON_SP_FOOTER_CLICKPOST_SUPPLIES = """<b>●お支払いについて</b><br>・クレジットカード決済<br>・銀行振込（前払）<br>・セブンイレブン（前払）<br>・ローソン、郵便局ATM等（前払）<br>・後払い決済<br><br><b>●発送方法</b><br>クリックポストでの発送になります。<br><br>・日時指定や代引きは出来ません。<br>・手渡しではなく、ポストへの投函になります。<br>・配送日数はおおむね3日前後になります。<br>・追跡可能ですが、紛失や破損等による保証はありませんのでご了承の上ご購入お願いします。<br>・発送は発送連絡を行わせて頂いた当日の夕方、ポストへ投函させて頂きます。<br>・当方の地域柄、集荷時間等の関係上、追跡番号がインターネット上に反映されるに1〜2日程度かかる場合がございます。予めご了承ください。<br>例：発送連絡日(20XX/4/1)→ネット上の集荷日(20XX/4/3)<br><br><b>●発送のタイミング</b><br><b>平日は当日発送18時まで可能です。<br>（土曜・日曜は当日発送9時まで）</b><br>ご注文のタイミングによっては、当日発送が出来ない場合がございますのでご了承下さい。<br><br>※下記該当の場合は当日発送できません。<br>・当店が休みの場合（翌営業日の発送になります）。<br>・お支払方法が銀行振込みで、18時までにお振込みの確認が取れなかった場合(15時以降のお振込みの場合、当社着金が翌営業日になる可能性がございます。)<br><br>決済の審査が必要なお支払い方法（クレジットカード・後払い決済）をご選択された場合、<br>楽天の審査にお時間をいただくことがあり、当日発送ができない場合がございます。予めご了承ください。<br>※銀行振込、コンビニお支払い等、前払い制の決済方法をご選択された場合は、ご入金確認が完了してからの発送となります。<br><br><b>●保証</b><br>商品到着後14日以内の保証となります。<br>当店側のミスでお手元に届いた商品が違った場合は、商品到着後14日以内での対応となりますので、速やかな商品確認をお願い致します。<br>保証内容はご購入頂いた商品のみとなります。<br>万が一商品に不具合が生じた場合新たに商品のご手配をさせて頂きますが、ご手配できない場合には商品代金のみご返金させて頂きます。<br>商品交換時に発生する費用および損害等は保証できませんのでご了承下さい。<br>保証申請時には商品の不良申請書または診断結果および診断書【コピーでも可】・お車の車検証をご提出いただく必要がございます。<br>また症状や状態によっては商品の状態の確認がとれるお写真をいただく場合もございます。<br>取付ミスによる不具合や破損、加工済は保証対象外となります。<br><br><b>●お取引に関して</b><br>お振込でお支払の際は、ご注文後5営業日以内にお手続きお願い致します。ご連絡やお手続き頂けない場合には、「お客様都合」によるキャンセルをさせて頂く場合がございます。ご注意ください。<br>ご注文の場合には同意されたものとみなさせて頂きますので、ご不明な点がある場合は、必ずご注文前にお問い合わせ下さい。<br><br><b>●その他</b><br>パッケージにダメージがある場合が御座います。<br>写真撮影の為、パッケージを開封する場合が御座います。<br><br><a href="https://www.rakuten.co.jp/s-o-l/info2.html">SHOPPING GUIDE</a>をご確認の上ご注文お願いします。<br><br><b>●お問い合わせ先</b><br>【株式会社エスオーエル】<br>〒221-0031<br>神奈川県横浜市神奈川区新浦島町一丁目1番地25 <br>GRC横浜ベイリサーチパーク 10階<br>TEL：045-450-6218 / FAX：045-330-4015<br>※土曜・日曜はお電話でのお問い合わせは承っておりません。<br>e-mail：<a href="mailto:sol-info1@s-o-l.co.jp">sol-info1@s-o-l.co.jp</a><br>営業時間: 10:00〜18:00<br>(祝祭日を除く)<br><br><b>●出荷倉庫<br></b>【株式会社エスオーエル　パーツセンター】<br>〒292-0824<br>千葉県木更津市小浜276-3"""

# スマホ用ヘッダー定数 (通常PC用の置換・スマホ表示に対応する定数群)
base_dir = os.path.dirname(__file__)
header_path = os.path.join(base_dir, 'sp_header.txt')
footer_path = os.path.join(base_dir, 'sp_footer.txt')

rakuten_sp_header = """
<img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013yahoo/960_kyugyo.jpg" width="100%"><br><img src="https://image.rakuten.co.jp/s-o-l/cabinet/ninteimb.gif" width="100%"><br><img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/cart2.gif" width="100%" border="0"><br><br>
"""

rakuten_sp_header_parts010 = rakuten_sp_header
rakuten_sp_header_parts03 = rakuten_sp_header

target_header_parts03 = '<center><IMG SRC="https://shopping.c.yimg.jp/lib/solltd/960.jpg"><BR><BR><IMG SRC="https://shopping.c.yimg.jp/lib/solltd/parts03.gif"><BR><BR></center>'
target_header_parts030 = '<center><IMG SRC="https://shopping.c.yimg.jp/lib/solltd/960.jpg"><BR><BR><IMG SRC="https://shopping.c.yimg.jp/lib/solltd/parts030.gif"><BR><BR></center>'
target_footer_parts03 = target_footer

rakuten_sp_header_supplies = """<img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013yahoo/960_kyugyo.jpg" width="100%"><br><br>"""

target_header_supplies03 = """<center><IMG SRC="https://shopping.c.yimg.jp/lib/solltd/960.jpg"><BR><BR><IMG SRC="https://shopping.c.yimg.jp/lib/solltd/supplies03.gif"><BR><BR></center>"""
target_footer_supplies03 = """<B>●保証期間</B><br>商品到着後14日以内の保証となります。<br>当店側のミスでお手元に届いた商品が違った場合は、商品到着後14日間以内での対応となりますので、速やかな商品確認をお願い致します。<br>保証内容はご購入頂いた商品のみとなります。<br>万が一商品に不具合が生じた場合新たに商品のご手配をさせて頂きますが、ご手配できない場合には商品代金のみご返金させて頂きます。<br>商品交換時に発生する費用および損害等は保証できませんのでご了承下さい。<br><br><B>●備考</B><br>入荷時期により予告なく商品の細かな仕様の変更がある場合がございます。<br>本製品は輸入品の為、ご利用には支障のない程度の微細な小キズ、微妙な撓りや汚れ、型から抜いた際のバリ等が付いている場合がございます。<br>ご理解の上、ご購入お願いします。 <br><br>"""

rakuten_header_supplies03 = """<div align="left"><table border="0" cellpadding="1" cellspacing="1"><tbody><tr><td bgcolor="#999999" height="44" width="745" align="left"><center><b><font size="+1">商品詳細</font></b></center><table bgcolor="#ffffff" border="0" cellpadding="3" cellspacing="0" width="745"><tbody><tr height="25"><td bgcolor="#ffffff" width="745" align="left"><font size="-1">"""

rakuten_sp_header_supplies03 = """<img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013yahoo/960_kyugyo.jpg" width="100%"><br><img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/cart2.gif" width="100%" border="0"><br><img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/post.gif" width="100%" border="0"><br><br>"""

target_header_supplies02 = """<center><IMG SRC="https://shopping.c.yimg.jp/lib/solltd/960.jpg"><BR><BR><IMG SRC="https://shopping.c.yimg.jp/lib/solltd/supplies02.gif"><BR><BR></center>"""
target_footer_supplies02 = """<B>●保証期間</B><BR>商品到着後14日以内の保証となります。<BR>当店側のミスでお手元に届いた商品が違った場合は、商品到着後14日以内での対応となりますので、速やかな商品確認をお願い致します。<br>保証内容はご購入頂いた商品のみとなります。<BR>万が一商品に不具合が生じた場合新たに商品のご手配をさせて頂きますが、ご手配できない場合には商品代金のみご返金させて頂きます。<BR>商品交換時に発生する費用および損害等は保証できませんのでご了承下さい。<BR>保証申請時には商品の不良申請書または診断結果および診断書【コピーでも可】・お車の車検証をご提出いただく必要がございます。<BR>また症状や状態によっては商品の状態の確認がとれるお写真をいただく場合もございます。<BR>取付ミスによる不具合や破損、加工済は保証対象外となります。<br><br><B>●備考</B><br>弊社は専門店ではございませんので、取り付け方法・車検等のご質問にはお答えできかねます。<br>本製品は輸入品の為、メーカー出荷時から塗装を施す前提で製造されております。<br>ご利用には支障のない程度の微細な小キズ、微妙な撓りや汚れ、型から抜いた際のバリ等が付いている場合がございますので、取付け時の板金塗装作業等で修正が必要となります。<br>ご理解の上、ご注文お願いします。 <br><br><B>●発送方法について</b><br>西濃運輸または福山通運での発送になります。<BR>※運送便のご指定は一切できません。<BR> ※個人宅様宛の配送はできません。<br>※企業様宛ての時間指定はできませんのでご了承ください。<BR> <BR>営業所留めを希望される場合、ご注文時にご希望の営業所名・営業所住所をご要望欄へご指定下さい。 <BR>※発送予定の運送会社を確認されたい方は、ご注文前に必ずお問い合わせください。<br><br><b>●発送のタイミングについて</b><br>当日発送16時まで可能です。<br>ご注文のタイミングによっては、当日発送が出来ない場合がございますのでご了承下さい。<br><br>"""

rakuten_header_supplies02 = """<div align="left"><table border="0" cellpadding="1" cellspacing="1"><tbody><tr><td bgcolor="#999999" height="44" width="745" align="left"><center><b><font size="+1">商品詳細</font></b></center><table bgcolor="#ffffff" border="0" cellpadding="3" cellspacing="0" width="745"><tbody><tr height="25"><td bgcolor="#ffffff" width="745" align="left"><font size="-1">"""

rakuten_sp_header_supplies02 = """<img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013yahoo/960_kyugyo.jpg" width="100%"><br><br>"""
NORMAL_ITEM_HEADERS = [
    "商品管理番号（商品URL）", "商品番号", "商品名", "倉庫指定", "サーチ表示", "消費税", "消費税率", "注文ボタン", "商品問い合わせボタン", "在庫表示",
    "代引料", "ジャンルID", "キャッチコピー", "PC用商品説明文", "スマートフォン用商品説明文", "PC用販売説明文", "商品画像タイプ1", "商品画像パス1", "商品画像名（ALT）1", "商品画像タイプ2",
    "商品画像パス2", "商品画像名（ALT）2", "商品画像タイプ3", "商品画像パス3", "商品画像名（ALT）3", "商品画像タイプ4", "商品画像パス4", "商品画像名（ALT）4", "商品画像タイプ5", "商品画像パス5",
    "商品画像名（ALT）5", "商品画像タイプ6", "商品画像パス6", "商品画像名（ALT）6", "商品画像タイプ7", "商品画像パス7", "商品画像名（ALT）7", "商品画像タイプ8", "商品画像パス8", "商品画像名（ALT）8",
    "商品画像タイプ9", "商品画像パス9", "商品画像名（ALT）9", "商品画像タイプ10", "商品画像パス10", "商品画像名（ALT）10", "商品画像タイプ11", "商品画像パス11", "商品画像名（ALT）11", "商品画像タイプ12",
    "商品画像パス12", "商品画像名（ALT）12", "商品画像タイプ13", "商品画像パス13", "商品画像名（ALT）13", "白背景画像タイプ", "白背景画像パス", "商品情報レイアウト", "ヘッダー・フッター・レフトナビ", "表示項目の並び順",
    "共通説明文（小）", "目玉商品", "共通説明文（大）", "レビュー本文表示", "メーカー提供情報表示", "SKU管理番号", "販売価格", "再入荷お知らせボタン", "在庫数", "在庫あり時納期管理番号",
    "在庫あり時出荷リードタイム", "在庫切れ時出荷リードタイム", "配送リードタイム", "配送方法セット管理番号", "送料", "個別送料", "地域別個別送料管理番号", "単品配送設定使用", "送料区分1", "カタログID", "カタログIDなしの理由",
    "商品属性（項目）1", "商品属性（値）1", "商品属性（単位）1",
    "商品属性（項目）2", "商品属性（値）2", "商品属性（単位）2",
    "商品属性（項目）3", "商品属性（値）3", "商品属性（単位）3",
    "商品属性（項目）4", "商品属性（値）4", "商品属性（単位）4",
    "商品属性（項目）5", "商品属性（値）5", "商品属性（単位）5",
    "商品属性（項目）6", "商品属性（値）6", "商品属性（単位）6",
    "商品属性（項目）7", "商品属性（値）7", "商品属性（単位）7",
    "商品属性（項目）8", "商品属性（値）8", "商品属性（単位）8",
    "商品属性（項目）9", "商品属性（値）9", "商品属性（単位）9",
    "商品属性（項目）10", "商品属性（値）10", "商品属性（単位）10",
    "商品属性（項目）11", "商品属性（値）11", "商品属性（単位）11",
    "商品属性（項目）12", "商品属性（値）12", "商品属性（単位）12",
    "商品属性（項目）13", "商品属性（値）13", "商品属性（単位）13",
    "商品属性（項目）14", "商品属性（値）14", "商品属性（単位）14",
    "商品属性（項目）15", "商品属性（値）15", "商品属性（単位）15",
    "商品属性（項目）16", "商品属性（値）16", "商品属性（単位）16",
    "商品属性（項目）17", "商品属性（値）17", "商品属性（単位）17",
    "商品属性（項目）18", "商品属性（値）18", "商品属性（単位）18",
    "商品属性（項目）19", "商品属性（値）19", "商品属性（単位）19",
    "商品属性（項目）20", "商品属性（値）20", "商品属性（単位）20",
    "商品属性（項目）21", "商品属性（値）21", "商品属性（単位）21",
    "商品属性（項目）22", "商品属性（値）22", "商品属性（単位）22",
    "商品属性（項目）23", "商品属性（値）23", "商品属性（単位）23",
    "商品属性（項目）24", "商品属性（値）24", "商品属性（単位）24",
    "商品属性（項目）25", "商品属性（値）25", "商品属性（単位）25",
    "商品属性（項目）26", "商品属性（値）26", "商品属性（単位）26",
    "商品属性（項目）27", "商品属性（値）27", "商品属性（単位）27",
    "商品属性（項目）28", "商品属性（値）28", "商品属性（単位）28",
    "商品属性（項目）29", "商品属性（値）29", "商品属性（単位）29",
    "商品属性（項目）30", "商品属性（値）30", "商品属性（単位）30",
    "商品属性（項目）31", "商品属性（値）31", "商品属性（単位）31",
    "商品属性（項目）32", "商品属性（値）32", "商品属性（単位）32",
    "商品属性（項目）33", "商品属性（値）33", "商品属性（単位）33",
    "商品属性（項目）34", "商品属性（値）34", "商品属性（単位）34",
    "商品属性（項目）35", "商品属性（値）35", "商品属性（単位）35",
    "商品属性（項目）36", "商品属性（値）36", "商品属性（単位）36",
    "商品属性（項目）37", "商品属性（値）37", "商品属性（単位）37",
    "商品属性（項目）38", "商品属性（値）38", "商品属性（単位）38",
    "商品属性（項目）40" if False else "商品属性（項目）39", "商品属性（値）39", "商品属性（単位）39",
    "商品属性（項目）40", "商品属性（値）40", "商品属性（単位）40",
    "商品属性（項目）41", "商品属性（値）41", "商品属性（単位）41",
    "商品属性（項目）42", "商品属性（値）42", "商品属性（単位）42",
    "商品属性（項目）43", "商品属性（値）43", "商品属性（単位）43",
    "商品属性（項目）44", "商品属性（値）44", "商品属性（単位）44",
    "商品属性（項目）45", "商品属性（値）45", "商品属性（単位）45",
    "商品属性（項目）46", "商品属性（値）46", "商品属性（単位）46",
    "商品属性（項目）47", "商品属性（値）47", "商品属性（単位）47",
    "商品属性（項目）48", "商品属性（値）48", "商品属性（単位）48",
    "商品属性（項目）49", "商品属性（値）49", "商品属性（単位）49",
    "商品属性（項目）50", "商品属性（値）50", "商品属性（単位）50",
    "商品属性（項目）51", "商品属性（値）51", "商品属性（単位）51",
    "商品属性（項目）52", "商品属性（値）52", "商品属性（単位）52",
    "商品属性（項目）53", "商品属性（値）53", "商品属性（単位）53",
    "商品属性（項目）54", "商品属性（値）54", "商品属性（単位）54",
    "商品属性（項目）55", "商品属性（値）55", "商品属性（単位）55",
    "商品属性（項目）56", "商品属性（値）56", "商品属性（単位）56",
    "商品属性（項目）57", "商品属性（値）57", "商品属性（単位）57",
    "商品属性（項目）58", "商品属性（値）58", "商品属性（単位）58",
    "商品属性（項目）59", "商品属性（値）59", "商品属性（単位）59",
    "商品属性（項目）60", "商品属性（値）60", "商品属性（単位）60",
    "選択肢タイプ", "商品オプション項目名", "商品オプション選択肢1", "商品オプション選択必須"
]

ITEM_CAT_HEADERS = [
    "コントロールカラム", "商品管理番号（商品URL）", "表示先カテゴリ", "カテゴリセット管理番号", "優先度", "1ページ複数形式"
]

def create_rakuten_description(html_content):
    if not isinstance(html_content, str) or pd.isna(html_content):
        return ""
    result = html_content.replace(target_header, rakuten_header)
    result = result.replace(target_footer, rakuten_footer)
    return result

def load_csv(file):
    content = file.getvalue()
    encodings = ['utf-8', 'cp932', 'shift_jis', 'utf-8-sig']
    
    for enc in encodings:
        try:
            df = pd.read_csv(io.BytesIO(content), encoding=enc, skip_blank_lines=False)
            return df, enc
        except (UnicodeDecodeError, LookupError, pd.errors.ParserError):
            continue
            
    raise ValueError("CSVファイルの読み込みに失敗しました。文字コード（UTF-8 または Shift_JIS/CP932）またはCSVのフォーマットが正しいか確認してください。")

def extract_fitment_info(html_content):
    if not isinstance(html_content, str) or pd.isna(html_content):
        return ""
    
    start_markers = ["＜B＞●適合車種＜/B＞＜br＞", "<B>●適合車種</B><br>"]
    end_markers = ["＜br＞＜br＞＜B＞●", "<br><br><B>●"]
    
    start_idx = -1
    matched_start_marker = ""
    for marker in start_markers:
        idx = html_content.find(marker)
        if idx != -1:
            start_idx = idx
            matched_start_marker = marker
            break
            
    if start_idx == -1:
        return ""
        
    content_start = start_idx + len(matched_start_marker)
    
    end_idx = -1
    for marker in end_markers:
        idx = html_content.find(marker, content_start)
        if idx != -1:
            end_idx = idx
            break
            
    if end_idx == -1:
        return ""
        
    return html_content[content_start:end_idx]

def extract_notes_image(image_urls_str):
    if not isinstance(image_urls_str, str) or pd.isna(image_urls_str):
        return ""
    urls = image_urls_str.split(';')
    for url in urls:
        url = url.strip()
        match = re.search(r'notes\d+\.jpg', url, re.IGNORECASE)
        if match:
            return f"/2013rakuten/{match.group(0)}"
    return ""

def check_notesiso(image_urls_str):
    if not isinstance(image_urls_str, str) or pd.isna(image_urls_str):
        return ""
    if "https://shopping.c.yimg.jp/lib/solltd/notesiso.jpg" in image_urls_str:
        return "/2013rakuten/imgrc0241948677.jpg"
    return ""

def determine_medama_item(brand_code):
    if pd.isna(brand_code) or str(brand_code).strip() == "" or str(brand_code).lower() == "nan":
        return "目玉　共通"
    
    try:
        f_val = float(brand_code)
        if f_val.is_integer():
            code_str = str(int(f_val))
        else:
            code_str = str(brand_code).strip()
    except (ValueError, TypeError):
        code_str = str(brand_code).strip()
        
    if code_str == "53377":
        return "目玉 プール"
    elif code_str in BRAND_CODE_MAP:
        return f"目玉　{BRAND_CODE_MAP[code_str]}"
    else:
        return "目玉　共通"

def truncate_catchcopy(text, max_bytes=174):
    if pd.isna(text):
        return text
    text = str(text)
    while len(text.encode('cp932', errors='replace')) > max_bytes:
        if ' ' not in text:
            while len(text.encode('cp932', errors='replace')) > max_bytes:
                text = text[:-1]
            break
        text = text.rsplit(' ', 1)[0]
    return text

def determine_car_brand(brand_code):
    if pd.isna(brand_code) or str(brand_code).strip() == "" or str(brand_code).lower() == "nan":
        return ""
    
    try:
        f_val = float(brand_code)
        if f_val.is_integer():
            code_str = str(int(f_val))
        else:
            code_str = str(brand_code).strip()
    except (ValueError, TypeError):
        code_str = str(brand_code).strip()
        
    if code_str in CAR_BRAND_MAP:
        return CAR_BRAND_MAP[code_str]
    return ""

def calculate_sales_price(row):
    price_val = row.get('price')
    if pd.isna(price_val) or str(price_val).strip() == "" or str(price_val).lower() == "nan":
        return ""

    try:
        base_price = float(price_val)
    except (ValueError, TypeError):
        return ""

    postage = row.get('postage-set')
    is_cp = False
    if not pd.isna(postage) and str(postage).strip() in ['6', '6.0']:
        is_cp = True
    add1 = str(row.get('additional1', ''))
    if 'parts03' in add1 or 'supplies03.gif' in add1:
        is_cp = True

    addition = 0
    if is_cp:
        addition = 185
    else:
        ship_weight = row.get('ship-weight')
        if not pd.isna(ship_weight) and str(ship_weight).strip() != "" and str(ship_weight).lower() != "nan":
            try:
                f_val = float(ship_weight)
                key = int(f_val) if f_val.is_integer() else f_val
            except (ValueError, TypeError):
                key = str(ship_weight).strip()
            addition = SHIP_WEIGHT_PRICE_MAP.get(key, 0)
        
    final_price = base_price + addition
    if final_price.is_integer():
        return int(final_price)
    return final_price

def determine_attribute_value_1(name):
    if not isinstance(name, str) or pd.isna(name):
        return "エスオーエル"
    if "HAPAD" in name:
        return "HAPAD"
    elif "CAPSOL" in name:
        return "CAPSOL"
    elif "HELLA" in name:
        return "HELLA"
    return "エスオーエル"

def determine_attribute_value_6(attr_val_1):
    if attr_val_1 == "HAPAD":
        return "ハパッド"
    elif attr_val_1 == "CAPSOL":
        return "キャプソル"
    elif attr_val_1 == "HELLA":
        return "ヘラ"
    return "エスオーエル"

def determine_suffix(row):
    postage = row.get('postage-set')
    if not pd.isna(postage):
        try:
            if float(postage) == 6.0:
                return "SSS"
        except (ValueError, TypeError):
            if str(postage).strip() == "6":
                return "SSS"

    ship_weight = row.get('ship-weight')
    if pd.isna(ship_weight):
        return ""
    try:
        f_val = float(ship_weight)
        if f_val == 0.0:
            return "VVV"
        elif f_val == 100.0:
            return "WWW"
        elif f_val == 1.0:
            return "XXX"
        elif f_val == 1000.0:
            return "YYY"
    except (ValueError, TypeError):
        pass
    
    s_val = str(ship_weight).strip()
    if s_val == "0":
        return "VVV"
    elif s_val == "100":
        return "WWW"
    elif s_val == "1":
        return "XXX"
    elif s_val == "1000":
        return "YYY"
        
    return ""

def format_banner_width(banner_html, width_val):
    if "width=" in banner_html:
        return re.sub(r'width="[^"]{1,20}"', f'width="{width_val}"', banner_html)
    else:
        return re.sub(r'(?i)<img', f'<img width="{width_val}"', banner_html)

# CSVファイルのアップローダーを配置
uploaded_file = st.file_uploader(
    "Yahoo!ショッピングからダウンロードしたCSVファイルを選択してください", 
    type=["csv"],
    help="必須列: code, name, additional1"
)

if uploaded_file is not None:
    try:
        df, detected_encoding = load_csv(uploaded_file)
        
        missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        
        if missing_columns:
            st.error(
                f"CSVファイルの読み込みに失敗しました。必要な列が不足しています。\n\n"
                f"不足している列: **{', '.join(missing_columns)}**\n\n"
                f"※CSVファイルには必ず以下の列を含めてください: {', '.join(REQUIRED_COLUMNS)}"
            )
        else:
            additional_clean = df['additional1'].fillna('')
            
            # Yahoo側バナーの更地化（正規表現による削除）
            pattern_clear = r'(?i)(<IMG SRC="https://shopping.c.yimg.jp/lib/solltd/(?:parts|supplies)[^"]*\.gif">)(?:\s*(?:<BR>|<br>)*\s*<IMG SRC="https://shopping.c.yimg.jp/lib/solltd/[^"]+">)+(?:\s*(?:<BR>|<br>)*\s*)(?=</center>)'
            additional_clean = additional_clean.str.replace(pattern_clear, r'\1<BR><BR>', regex=True)
            
            # キーワード判定による挿入用バナー文字列の生成
            pc_insert_banner = pd.Series("", index=df.index)
            sp_insert_banner = pd.Series("", index=df.index)
            
            # 判定用テキストの作成（商品名、カテゴリ、および追加テキスト）
            csv_path = df['path'] if 'path' in df.columns else pd.Series('', index=df.index)
            car_brand_series = df.get('car_brand', pd.Series("", index=df.index))
            mapped_cat = car_brand_series.map(CATEGORY_MAP).fillna('')
            target_text = (
                df['name'].fillna('') + ' ' + 
                csv_path.fillna('') + ' ' + 
                mapped_cat.fillna('') + ' ' + 
                car_brand_series.fillna('') + ' ' +
                selected_path + ' ' + 
                additional_clean
            )
            
            for rule in BANNER_RULES:
                must_keywords = rule.get("must_keywords", [])
                or_keywords = rule.get("or_keywords", [])
                excludes = rule.get("excludes", [])
                
                must_cond = pd.Series(True, index=df.index)
                for kw in must_keywords:
                    must_cond = must_cond & target_text.str.contains(kw, case=False, regex=False)
                    
                if or_keywords:
                    or_cond = pd.Series(False, index=df.index)
                    for kw in or_keywords:
                        or_cond = or_cond | target_text.str.contains(kw, case=False, regex=False)
                else:
                    or_cond = pd.Series(True, index=df.index)
                    
                ex_cond = pd.Series(False, index=df.index)
                for ex in excludes:
                    ex_cond = ex_cond | target_text.str.contains(ex, case=False, regex=False)
                    
                final_cond = must_cond & or_cond & ~ex_cond
                
                # バナー挿入時に属性を付与
                pc_b = format_banner_width(rule["pc_banners"], "745")
                sp_b = format_banner_width(rule["sp_banners"], "100%")
                
                pc_insert_banner = np.where(final_cond, pc_b, pc_insert_banner)
                sp_insert_banner = np.where(final_cond, sp_b, sp_insert_banner)
                
            # 各メディア用バナー挿入つきのヘッダーSeriesの準備 (バナーはここでは結合せず、素のヘッダーとする)
            pc_hdr_supplies = pd.Series(rakuten_header_supplies, index=df.index)
            pc_hdr_parts010 = pd.Series(rakuten_header_parts010, index=df.index)
            pc_hdr_parts03 = pd.Series(rakuten_header_parts03, index=df.index)
            pc_hdr_supplies03 = pd.Series(rakuten_header_supplies03, index=df.index)
            pc_hdr_supplies02 = pd.Series(rakuten_header_supplies02, index=df.index)
            pc_hdr_normal = pd.Series(rakuten_header, index=df.index)

            sp_hdr_supplies = pd.Series(rakuten_sp_header_supplies, index=df.index)
            sp_hdr_parts010 = pd.Series(rakuten_sp_header_parts010, index=df.index)
            sp_hdr_parts03 = pd.Series(rakuten_sp_header_parts03, index=df.index)
            sp_hdr_supplies03 = pd.Series(rakuten_sp_header_supplies03, index=df.index)
            sp_hdr_supplies02 = pd.Series(rakuten_sp_header_supplies02, index=df.index)
            sp_hdr_normal = pd.Series(rakuten_sp_header, index=df.index)
            
            df['fitment_info'] = additional_clean.apply(extract_fitment_info)
            
            # 用品用の更地化処理 (ベンツ認定ロゴおよびISO9001ロゴの完全除去)
            # アスタリスクは一切使用しないため、範囲指定 {0,999} などを使用します。
            logo_pattern = r'(?i)(?:<br\s{0,9}/?>\s{0,9}){0,9}<img\s{1,9}[^>]{0,999}(?:ninteimb|notesiso)\.(?:gif|jpg|png|jpeg)[^>]{0,999}>(?:\s{0,9}(?:<br\s{0,9}/?>|/?>)){0,9}'
            additional_clean_supplies = additional_clean.str.replace(logo_pattern, '', regex=True)

            # Yahoo側の古いクリックポスト発送案内の完全除去
            cp_shipping_pattern = r'(?is)<b[^>]{0,99}>●発送方法について(?:<br\s{0,9}/?>|\s){0,99}</b[^>]{0,99}>.{0,999}?クリックポストとは(?:</a[^>]{0,99}>)?をご確認下さい。(?:<br\s{0,9}/?>|\s){0,99}'
            additional_clean = additional_clean.str.replace(cp_shipping_pattern, '', regex=True)
            additional_clean_supplies = additional_clean_supplies.str.replace(cp_shipping_pattern, '', regex=True)

            # 各種条件の判定
            is_supplies = additional_clean.str.contains('supplies01.gif', regex=False)
            is_parts010 = additional_clean.str.contains('parts010.gif', regex=False)
            is_parts03 = additional_clean.str.contains('parts03', regex=False)
            is_supplies03 = additional_clean.str.contains('supplies03.gif', regex=False)
            is_supplies02 = additional_clean.str.contains('supplies02.gif', regex=False)
            is_postage_6 = df['postage-set'].astype(str).str.strip().isin(['6', '6.0'])
            is_clickpost_global = is_parts03 | is_supplies03 | is_postage_6
            
            # parts03品の商品名から特定の文字列を削除（一括処理）
            df['name'] = np.where(is_parts03, df['name'].str.replace('送料185円 ', '', regex=False), df['name'])
            df['name'] = np.where(is_clickpost_global, df['name'].str.replace('18時まで即日発送', '18時まで即日発送 ポスト投函', regex=False), df['name'])
            
            # 【PC用商品説明文の生成】
            close_supplies = "</font></td></tr></tbody></table></td></tr></tbody></table></div>"
            close_parts010 = "</font></td></tr></tbody></table></td></tr></tbody></table></div>"
            close_parts03 = "</font></td></tr></tbody></table></td></tr></tbody></table></div>"
            close_supplies03 = "</font></td></tr></tbody></table></td></tr></tbody></table></div>"
            close_supplies02 = "</font></td></tr></tbody></table></td></tr></tbody></table></div>"
            close_normal = "</font></td></tr></tbody></table></td></tr></tbody></table></div>"

            pc_supplies_desc = pc_hdr_supplies + additional_clean_supplies.str.replace(target_header_supplies, "", case=False, regex=False).str.replace(target_footer_supplies, "", case=False, regex=False) + close_supplies + COMMON_FOOTER_SUPPLIES
            pc_parts010_desc = pc_hdr_parts010 + additional_clean.str.replace(target_header_parts010, "", case=False, regex=False).str.replace(target_footer_parts010, "", case=False, regex=False) + close_parts010 + COMMON_FOOTER
            pc_parts03_desc = pc_hdr_parts03 + additional_clean.str.replace(target_header_parts03, "", case=False, regex=False).str.replace(target_header_parts030, "", case=False, regex=False).str.replace(target_footer_parts03, "", case=False, regex=False) + close_parts03 + COMMON_FOOTER_CLICKPOST
            pc_supplies03_desc = pc_hdr_supplies03 + additional_clean_supplies.str.replace(target_header_supplies03, "", case=False, regex=False).str.replace(target_footer_supplies03, "", case=False, regex=False) + close_supplies03 + COMMON_FOOTER_CLICKPOST
            pc_supplies02_desc = pc_hdr_supplies02 + additional_clean_supplies.str.replace(target_header_supplies02, "", case=False, regex=False).str.replace(target_footer_supplies02, "", case=False, regex=False) + close_supplies02 + COMMON_FOOTER
            pc_normal_desc = pc_hdr_normal + additional_clean.str.replace(target_header, "", case=False, regex=False).str.replace(target_footer, "", case=False, regex=False) + close_normal + COMMON_FOOTER
            
            df['PC用商品説明文'] = np.select(
                [is_supplies, is_parts010, is_parts03, is_supplies03, is_supplies02],
                [pc_supplies_desc, pc_parts010_desc, pc_parts03_desc, pc_supplies03_desc, pc_supplies02_desc],
                default=pc_normal_desc
            )
            
            # 【スマートフォン用商品説明文の生成】
            sp_supplies_desc = sp_hdr_supplies + additional_clean_supplies.str.replace(target_header_supplies, "", case=False, regex=False).str.replace(target_footer_supplies, "", case=False, regex=False) + COMMON_SP_FOOTER_SUPPLIES
            sp_parts010_desc = sp_hdr_parts010 + additional_clean.str.replace(target_header_parts010, "", case=False, regex=False).str.replace(target_footer_parts010, "", case=False, regex=False) + COMMON_SP_FOOTER
            sp_parts03_desc = sp_hdr_parts03 + additional_clean.str.replace(target_header_parts03, "", case=False, regex=False).str.replace(target_header_parts030, "", case=False, regex=False).str.replace(target_footer_parts03, "", case=False, regex=False) + COMMON_SP_FOOTER_CLICKPOST
            sp_supplies03_desc = sp_hdr_supplies03 + additional_clean_supplies.str.replace(target_header_supplies03, "", case=False, regex=False).str.replace(target_footer_supplies03, "", case=False, regex=False) + COMMON_SP_FOOTER_CLICKPOST_SUPPLIES
            sp_supplies02_desc = sp_hdr_supplies02 + additional_clean_supplies.str.replace(target_header_supplies02, "", case=False, regex=False).str.replace(target_footer_supplies02, "", case=False, regex=False) + COMMON_SP_FOOTER_SUPPLIES02
            sp_normal_desc = sp_hdr_normal + additional_clean.str.replace(target_header, "", case=False, regex=False).str.replace(target_footer, "", case=False, regex=False) + COMMON_SP_FOOTER
            
            df['スマートフォン用商品説明文'] = np.select(
                [is_supplies, is_parts010, is_parts03, is_supplies03, is_supplies02],
                [sp_supplies_desc, sp_parts010_desc, sp_parts03_desc, sp_supplies03_desc, sp_supplies02_desc],
                default=sp_normal_desc
            )
                                    # バナーの結合（最終組み立て段階：HTMLの先頭に安全に結合）
            df['PC用商品説明文'] = np.where(pc_insert_banner != "", pc_insert_banner + df['PC用商品説明文'], df['PC用商品説明文'])
            df['スマートフォン用商品説明文'] = np.where(sp_insert_banner != "", sp_insert_banner + df['スマートフォン用商品説明文'], df['スマートフォン用商品説明文'])
            
            # 改行削除処理を以下に変更
            df['スマートフォン用商品説明文'] = df['スマートフォン用商品説明文'].replace(r'\r\n|\r|\n', ' ', regex=True)
            # タグ同士の間にできた過剰なスペースを整理（必要に応じて）
            df['スマートフォン用商品説明文'] = df['スマートフォン用商品説明文'].str.replace(r'>\s+<', '><', regex=True)

            df['suffix'] = df.apply(determine_suffix, axis=1)
            
            item_image_urls_clean = df['item-image-urls'].fillna('')
            df['notes_image'] = item_image_urls_clean.apply(extract_notes_image)
            df['notesiso_image'] = item_image_urls_clean.apply(check_notesiso)
            
            df['medama_item'] = df['brand-code'].apply(determine_medama_item)
            df['sales_price'] = df.apply(calculate_sales_price, axis=1)
            df['attr_val_1'] = df['name'].apply(determine_attribute_value_1)
            df['attr_val_6'] = df['attr_val_1'].apply(determine_attribute_value_6)
            df['car_brand'] = df['brand-code'].apply(determine_car_brand)
            
            def generate_url_id(row):
                code = row['code']
                if pd.isna(code) or str(code).strip() == "" or str(code).lower() == "nan":
                    return ""
                base_code = str(code).strip()
                # 枝番がSSSの場合、元のコード末尾のpまたはPを削除する
                if row.get('suffix') == 'SSS' and base_code.lower().endswith('p'):
                    base_code = base_code[:-1]
                return base_code + row['suffix']

            def generate_item_id(row):
                code = row['code']
                if pd.isna(code) or str(code).strip() == "" or str(code).lower() == "nan":
                    return ""
                base_code = str(code).strip().split('-')[0]
                return base_code + row['suffix']

            df['url_id'] = df.apply(generate_url_id, axis=1)
            df['item_id'] = df.apply(generate_item_id, axis=1)
            
            st.success(
                f"CSVファイルを正常に読み込みました！ (文字コード: {detected_encoding}, "
                f"総行数: {len(df)}行)"
            )
            
            st.subheader("データプレビュー (先頭5行)")
            preview_cols = ['code', 'url_id', 'item_id', 'ship-weight', 'suffix', 'name', 'fitment_info', 'PC用商品説明文', 'スマートフォン用商品説明文', 'additional1'] + [
                col for col in df.columns if col not in ['code', 'url_id', 'item_id', 'ship-weight', 'suffix', 'name', 'fitment_info', 'PC用商品説明文', 'スマートフォン用商品説明文', 'additional1']
            ]
            st.dataframe(df[preview_cols].head(5), use_container_width=True)
            
            repeated_index = df.index.repeat(4)
            df_normal = pd.DataFrame(index=repeated_index, columns=NORMAL_ITEM_HEADERS)
            
            df_normal['商品管理番号（商品URL）'] = df['url_id'].loc[repeated_index].values
            
            mask = (np.arange(len(df_normal)) % 4 == 0)
            
            def expand_and_mask(series):
                repeated = series.loc[repeated_index].values
                return np.where(mask, repeated, "")
            
            df_normal['商品番号'] = expand_and_mask(df['item_id'])
            df_normal['商品名'] = expand_and_mask(df['name'])
            
            df_normal['倉庫指定'] = np.where(mask, '0', '')
            df_normal['サーチ表示'] = np.where(mask, '1', '')
            df_normal['消費税'] = np.where(mask, '1', '')
            df_normal['注文ボタン'] = np.where(mask, '1', '')
            df_normal['商品問い合わせボタン'] = np.where(mask, '1', '')
            df_normal['在庫表示'] = np.where(mask, '0', '')
            df_normal['代引料'] = np.where(mask, '0', '')
            
            df_normal['商品情報レイアウト'] = np.where(mask, '5', '')
            df_normal['ヘッダー・フッター・レフトナビ'] = np.where(mask, '自動選択', '')
            df_normal['表示項目の並び順'] = np.where(mask, '自動選択', '')
            df_normal['共通説明文（小）'] = np.where(mask, '自動選択', '')
            df_normal['共通説明文（大）'] = np.where(mask, '自動選択', '')
            df_normal['レビュー本文表示'] = np.where(mask, '2', '')
            df_normal['メーカー提供情報表示'] = np.where(mask, '0', '')
            
            df_normal['ジャンルID'] = np.where(mask, genre_id_input, '')
            df_normal['キャッチコピー'] = np.where(mask, catch_copy_input, '')
            
            processed_white_bg = white_bg_input.strip().replace("https://image.rakuten.co.jp/s-o-l/cabinet", "") if white_bg_input else ""
            df_normal['白背景画像パス'] = np.where(mask, processed_white_bg, '')
            white_bg_type = "cabinet" if processed_white_bg else ""
            df_normal['白背景画像タイプ'] = np.where(mask, white_bg_type, '')
            
            for header_name, raw_url in image_inputs.items():
                processed_url = raw_url.strip().replace("https://image.rakuten.co.jp/s-o-l/cabinet", "") if raw_url else ""
                df_normal[header_name] = np.where(mask, processed_url, '')
                
                type_header = header_name.replace("パス", "タイプ")
                image_type_val = "cabinet" if processed_url else ""
                df_normal[type_header] = np.where(mask, image_type_val, '')
                
                alt_header = header_name.replace("パス", "名（ALT）")
                alt_val = df['name'].loc[repeated_index].values if processed_url else ""
                df_normal[alt_header] = np.where(mask, alt_val, '')
            
            df_normal['商品画像パス12'] = expand_and_mask(df['notes_image'])
            df_normal['商品画像タイプ12'] = np.where(df_normal['商品画像パス12'] != "", "cabinet", "")
            alt_val = df['name'].loc[repeated_index].values
            df_normal['商品画像名（ALT）12'] = np.where(df_normal['商品画像パス12'] != "", alt_val, "")
            
            df_normal['商品画像パス13'] = expand_and_mask(df['notesiso_image'])
            df_normal['商品画像タイプ13'] = np.where(df_normal['商品画像パス13'] != "", "cabinet", "")
            df_normal['商品画像名（ALT）13'] = np.where(df_normal['商品画像パス13'] != "", alt_val, "")

            # 各種条件の判定（展開用。前倒しで定義）
            repeated_is_supplies = is_supplies.loc[repeated_index].values
            repeated_is_parts010 = is_parts010.loc[repeated_index].values
            repeated_is_parts03 = is_parts03.loc[repeated_index].values
            repeated_is_supplies03 = is_supplies03.loc[repeated_index].values
            repeated_is_supplies02 = is_supplies02.loc[repeated_index].values
            repeated_is_clickpost = is_clickpost_global.loc[repeated_index].values

            # notes2.jpgの判定（他条件用）
            is_notes2 = df_normal['商品画像パス12'] == '/2013rakuten/notes2.jpg'

            # クリックポスト専用画像（11番・12番）の無条件セット（要件4）
            is_clickpost_target = repeated_is_clickpost & mask
            df_normal['商品画像パス11'] = np.where(is_clickpost_target, '/2013rakuten/notesp2.jpg', df_normal['商品画像パス11'])
            df_normal['商品画像タイプ11'] = np.where(is_clickpost_target, 'cabinet', df_normal['商品画像タイプ11'])
            df_normal['商品画像名（ALT）11'] = np.where(is_clickpost_target, alt_val, df_normal['商品画像名（ALT）11'])
            
            df_normal['商品画像パス12'] = np.where(is_clickpost_target, '/2013rakuten/imgrc0231783254.jpg', df_normal['商品画像パス12'])
            df_normal['商品画像タイプ12'] = np.where(is_clickpost_target, 'cabinet', df_normal['商品画像タイプ12'])
            df_normal['商品画像名（ALT）12'] = np.where(is_clickpost_target, alt_val, df_normal['商品画像名（ALT）12'])

            # parts010専用画像（12番）の無条件セット
            is_parts010_target = repeated_is_parts010 & mask
            df_normal['商品画像パス12'] = np.where(is_parts010_target, '/2013rakuten/notes4.jpg', df_normal['商品画像パス12'])
            df_normal['商品画像タイプ12'] = np.where(is_parts010_target, 'cabinet', df_normal['商品画像タイプ12'])
            df_normal['商品画像名（ALT）12'] = np.where(is_parts010_target, alt_val, df_normal['商品画像名（ALT）12'])

            # supplies02かつnotes2.jpgの複合判定（直前で画像パス12が書き換わるため、書き換え前の判定 is_notes2 を使用）
            is_supplies02_notes2 = repeated_is_supplies02 & is_notes2 & mask
            df_normal['商品画像パス12'] = np.where(is_supplies02_notes2, '/2013rakuten/notes.jpg', df_normal['商品画像パス12'])
            
            df_normal['目玉商品'] = expand_and_mask(df['medama_item'])
            
            # ship-weight による配送方法セット管理番号の動的マッピング
            ship_weight_numeric = pd.to_numeric(df['ship-weight'], errors='coerce')
            ship_weight_map = {
                5000.0: '10',
                50000.0: '4',
                10000.0: '1',
                100000.0: '1',
                1000000.0: '7'
            }
            mapped_delivery_set = ship_weight_numeric.map(ship_weight_map).fillna('')
            repeated_delivery_set = mapped_delivery_set.loc[repeated_index].values
            
            sku_mask = (np.arange(len(df_normal)) % 4 == 1)
            df_normal['SKU管理番号'] = np.where(sku_mask, df_normal['商品管理番号（商品URL）'].str.lower(), '')
            
            repeated_sales_price = df['sales_price'].loc[repeated_index].values
            df_normal['販売価格'] = np.where(sku_mask, repeated_sales_price, '')
            
            df_normal['再入荷お知らせボタン'] = np.where(sku_mask, '1', '')
            df_normal['在庫数'] = np.where(sku_mask, '0', '')
            df_normal['在庫あり時納期管理番号'] = np.where(
                sku_mask,
                np.select(
                    [repeated_is_supplies02, repeated_is_clickpost],
                    ['8', '4'],
                    default='1'
                ),
                ''
            )
            df_normal['在庫あり時出荷リードタイム'] = np.where(sku_mask, '通常配送', '')
            df_normal['配送リードタイム'] = np.where(
                sku_mask,
                np.select(
                    [repeated_is_supplies02, repeated_is_clickpost],
                    ['大型商品配送', 'クリックポスト'],
                    default='通常配送'
                ),
                ''
            )
            df_normal['配送方法セット管理番号'] = np.where(
                sku_mask,
                np.select(
                    [repeated_is_supplies02, repeated_is_clickpost],
                    [repeated_delivery_set, '3'],
                    default=''
                ),
                ''
            )
            df_normal['送料'] = np.where(sku_mask, np.where(repeated_is_supplies02, '0', '1'), '')
            df_normal['個別送料'] = ''
            
            delivery_set_series = pd.Series(repeated_delivery_set).astype(str).str.strip()
            mapped_regional_fee = np.select(
                [
                    delivery_set_series == '10',
                    delivery_set_series == '4',
                    delivery_set_series == '1',
                    delivery_set_series == '7'
                ],
                ['6', '2', '3', '5'],
                default=''
            )
            df_normal['地域別個別送料管理番号'] = np.where(sku_mask & repeated_is_supplies02, mapped_regional_fee, '')
            df_normal['単品配送設定使用'] = np.where(sku_mask, np.where(repeated_is_supplies02, '4', ''), '')
            
            df_normal['カタログIDなしの理由'] = np.where(sku_mask, '5', '')
            
            df_normal['商品属性（項目）1'] = np.where(sku_mask, 'ブランド名', '')
            df_normal['商品属性（項目）2'] = np.where(sku_mask, 'メーカー型番', '')
            df_normal['商品属性（項目）3'] = np.where(sku_mask, '代表カラー', '')
            df_normal['商品属性（項目）4'] = np.where(sku_mask, 'カラー', '')
            df_normal['商品属性（項目）5'] = np.where(sku_mask, 'シリーズ名', '')
            df_normal['商品属性（項目）6'] = np.where(sku_mask, 'ブランド名（カナ）', '')
            df_normal['商品属性（項目）8'] = np.where(sku_mask, '発売年月日', '')
            df_normal['商品属性（項目）9'] = np.where(sku_mask, '状態', '')
            df_normal['商品属性（項目）10'] = np.where(sku_mask, '中古状態', '')
            df_normal['商品属性（項目）11'] = np.where(sku_mask, '販売形態（並行輸入品）', '')
            df_normal['商品属性（項目）12'] = np.where(sku_mask, '販売形態（訳あり）', '')
            df_normal['商品属性（項目）13'] = np.where(sku_mask, 'シリーズ名（カナ）', '')
            df_normal['商品属性（項目）14'] = np.where(sku_mask, '対応車種ブランド', '')
            df_normal['商品属性（項目）15'] = np.where(sku_mask, '発売年月日（テキスト）', '')
            
            repeated_attr_val_1 = df['attr_val_1'].loc[repeated_index].values
            df_normal['商品属性（値）1'] = np.where(sku_mask, repeated_attr_val_1, '')
            
            df_normal['商品属性（値）2'] = np.where(sku_mask, df_normal['商品管理番号（商品URL）'].str.split('-').str[0], '')
            
            df_normal['商品属性（値）3'] = np.where(sku_mask, attr3_input, '')
            df_normal['商品属性（値）5'] = np.where(sku_mask, '-', '')
            
            df_normal['商品属性（値）6'] = np.where(
                sku_mask,
                df_normal['商品属性（値）1'].apply(determine_attribute_value_6),
                ''
            )
            
            repeated_car_brand = df.get('car_brand', pd.Series("", index=df.index)).loc[repeated_index].values
            df_normal['商品属性（値）14'] = np.where(sku_mask, repeated_car_brand, '')
            
            row3_mask = (np.arange(len(df_normal)) % 4 == 2)
            row4_mask = (np.arange(len(df_normal)) % 4 == 3)
            
            df_normal['選択肢タイプ'] = np.select([row3_mask, row4_mask], ['s', 's'], default='')
            
            df_normal['商品オプション項目名'] = np.select(
                [
                    row3_mask & (repeated_is_supplies | repeated_is_supplies03 | repeated_is_supplies02),
                    row3_mask & ~(repeated_is_supplies | repeated_is_supplies03 | repeated_is_supplies02),
                    row4_mask
                ],
                [
                    '商品詳細およびINFORMATION',
                    '純正品番の適合確認及び保証内容',
                    '沖縄、他県離島、中継料金発生エリアは送料着払いです'
                ],
                default=''
            )
            df_normal['商品オプション選択肢1'] = np.select(
                [row3_mask, row4_mask],
                ['確認済', '了承する（当社で発送方法変更）'],
                default=''
            )
            df_normal['商品オプション選択必須'] = np.select([row3_mask, row4_mask], ['1', '1'], default='')
            
            # PC用販売説明文への定型HTML挿入（1行目のみ入力、他は空欄）
            pc_sales_html = '<center><br><img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/cart2.gif" border="0"><br><br><img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/toujitu.gif" border="0"><br><br></center>'
            pc_sales_html_supplies = '<center><br><img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/supplies05.gif" border="0"><br><br><img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/toujitu.gif" border="0"><br><br></center>'
            pc_sales_html_parts010 = '<center><br><img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/supplies05.gif" border="0"><br><br><img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/toujitu.gif" border="0"><br><br></center>'
            pc_sales_html_parts03 = '''<center><br><img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/cart2.gif" border="0"><br><br><img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/toujitu.gif" border="0"><br><br><img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/post.gif" border="0"><br><br></center><br><br></center>'''
            pc_sales_html_supplies03 = '''<center><br><img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/cart2.gif" border="0"><br><br><img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/toujitu.gif" border="0"><br><br><img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/post.gif" border="0"><br><br></center><br><br></center>'''
            pc_sales_html_supplies02 = '''<center><br><img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/supplies05.gif" border="0"><br><img src="https://image.rakuten.co.jp/s-o-l/cabinet/2013rakuten/exlsize.gif" border="0"><br><br></center>'''
            
            df_normal['PC用販売説明文'] = np.where(
                mask,
                np.select(
                    [repeated_is_supplies, repeated_is_parts010, repeated_is_parts03, repeated_is_supplies03, repeated_is_supplies02],
                    [pc_sales_html_supplies, pc_sales_html_parts010, pc_sales_html_parts03, pc_sales_html_supplies03, pc_sales_html_supplies02],
                    default=pc_sales_html
                ),
                ''
            )
            
            df_normal['PC用商品説明文'] = expand_and_mask(df['PC用商品説明文'])
            df_normal['スマートフォン用商品説明文'] = expand_and_mask(df['スマートフォン用商品説明文'])
            
            repeated_index_cat = df.index.repeat(3)
            df_cat = pd.DataFrame(index=repeated_index_cat, columns=ITEM_CAT_HEADERS)
            df_cat['商品管理番号（商品URL）'] = df['url_id'].loc[repeated_index_cat].values
            
            # 固定値のセット
            df_cat['コントロールカラム'] = 'n'
            df_cat['カテゴリセット管理番号'] = '0'
            df_cat['優先度'] = '899999999'
            df_cat['1ページ複数形式'] = ''
            
            # 表示先カテゴリ用の行判定マスク準備
            cat_row1_mask = (np.arange(len(df_cat)) % 3 == 0)
            cat_row2_mask = (np.arange(len(df_cat)) % 3 == 1)
            cat_row3_mask = (np.arange(len(df_cat)) % 3 == 2)
            
            # 1行目「表示先カテゴリ」への車種カテゴリマッピングの適用
            mapped_categories = df.get('car_brand', pd.Series("", index=df.index)).map(CATEGORY_MAP).fillna('')
            expanded_categories = mapped_categories.loc[repeated_index_cat].values
            df_cat.loc[cat_row1_mask, '表示先カテゴリ'] = expanded_categories[cat_row1_mask]
            
            # 2行目「表示先カテゴリ」へのパーツカテゴリパスの適用
            df_cat.loc[cat_row2_mask, '表示先カテゴリ'] = selected_path
            
            # 3行目「表示先カテゴリ」へのUI入力値の適用
            df_cat.loc[cat_row3_mask, '表示先カテゴリ'] = target_cat_row3
            
            # 表示先カテゴリが空欄（空文字列または欠損値）の行を除外
            df_cat['表示先カテゴリ'] = df_cat['表示先カテゴリ'].fillna('')
            df_cat = df_cat[df_cat['表示先カテゴリ'].str.strip() != '']

            # 楽天アップロード用CSVのエラー解消クレンジング処理
            # 商品管理番号（商品URL）の小文字化
            df_normal['商品管理番号（商品URL）'] = df_normal['商品管理番号（商品URL）'].str.lower()
            df_cat['商品管理番号（商品URL）'] = df_cat['商品管理番号（商品URL）'].str.lower()

            # クリックポスト（末尾sss）の場合、沖縄・離島着払いオプション（4行目）の行を削除
            is_sss = df_normal['商品管理番号（商品URL）'].str.endswith('sss')
            is_island_fee = df_normal['商品オプション項目名'] == '沖縄、他県離島、中継料金発生エリアは送料着払いです'
            df_normal = df_normal[~(is_sss & is_island_fee)]


            # キャッチコピーの174byte制限とスマートカット処理
            df_normal['キャッチコピー'] = df_normal['キャッチコピー'].apply(truncate_catchcopy)

            # 商品属性の自動クリーンアップ処理
            for i in range(1, 61):
                item_col = f'商品属性（項目）{i}'
                val_col = f'商品属性（値）{i}'
                unit_col = f'商品属性（単位）{i}'
                if item_col in df_normal.columns and val_col in df_normal.columns:
                    empty_mask = (df_normal[val_col] == '') | (df_normal[val_col].isna())
                    df_normal.loc[empty_mask, item_col] = ''
                    if unit_col in df_normal.columns:
                        df_normal.loc[empty_mask, unit_col] = ''

            # ダウンロードボタンの配置
            st.write("---")
            st.subheader("📥 楽天用CSVダウンロード")
            col1, col2 = st.columns(2)
            with col1:
                normal_csv = df_normal.to_csv(index=False, encoding='cp932', errors='replace').encode('cp932', errors='replace')
                st.download_button(
                    label="normal-item.csvをダウンロード",
                    data=normal_csv,
                    file_name="normal-item.csv",
                    mime="text/csv"
                )
            with col2:
                cat_csv = df_cat.to_csv(index=False, encoding='cp932', errors='replace').encode('cp932', errors='replace')
                st.download_button(
                    label="item-cat.csvをダウンロード",
                    data=cat_csv,
                    file_name="item-cat.csv",
                    mime="text/csv"
                )

    except Exception as e:
        st.error(f"エラーが発生しました: {str(e)}")
else:
    st.info("CSVファイルをアップロードすると、ここにプレビューが表示されます。")