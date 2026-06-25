import streamlit as st
import pandas as pd
import io
import os
import unicodedata
import re
import google.generativeai as genai

# Gemini API設定
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception as e:
    st.error("Gemini APIキーが設定されていません。.streamlit/secrets.toml を確認してください。")

# ==========================================
# 定数設定
# ==========================================
BRAND_DESCRIPTIONS = {
    "HAPAD": "【HAPAD】\n30000点を超えるアイテムを常備している会社が作り出した、ブランド『HAPAD』\n仲介業者を通さない為、工場と直接やりとりができる強みを生かした独自のルートで制作。\n耐久性や制動性、低ダストであることに高い評価を頂いております。",
    "CAPSOL": "【CAPSOL】\nインターネットの自動車部品商としてのパイオニアである\nエスオーエルが作り出したオリジナルブランド『CAPSOL』\n長い年月より蓄積された経験と技術が結晶されたブランドです。\n\n世界的に認めれらている提携工場より中間業者を挟まず直送のため、\n絶対的な品質とコストパフォーマンスの両方を実現。\n品質の高さに高い評価を頂いております。",
    "社外品": "優良品\nISO認証取得工場にて製造・検査を行っており、純正品同等のクオリティを実現しています。",
    "CAPSOLスノーワイパー": "【CAPSOL】\nインターネット自動車部品販売のパイオニアである\nエスオーエルが手掛けるオリジナルブランド「CAPSOL」から、冬専用プロダクトが登場しました\n純正OEM供給メーカーと共同で試行錯誤を重ね、最高の擦拭性能を実現　クリアな視界を提供します\n高品質な金属バネ板により、ワイパーがガラス面にしっかり密着し、静音性の高い擦拭を可能にしました\n数百万回に及ぶ実験室での擦拭テストにより、ワイパーの高い耐久性が保証されています",
    "閃-SEN-": "【閃-SEN-】\nSOLオリジナルブランド『閃-SEN-』\n閃-SEN-のルームランプは高輝度LEDチップ採用\n一つのLEDの中に発光点が三つ搭載されている3チップSMDを採用しているので\n驚くほどの明るさで室内を照らします。",
    "BREMI": "【BREMI】\nBREMI(ブレミ)はイグニッションコイルやプラグコード、エアマスメーター、イグニッションディストリビューターなどの\n電装関連部品を主に生産し、メルセデス・ベンツ、BMW、アウディ、フォルクスワーゲン等に\nOEM供給をしているドイツの自動車部品メーカーです。",
    "BOSCH": "【BOSCH】\nBOSCH社は1886年の創業以来、自動車部品の他電動工具や電子制御部品等を手掛けてきました。\n技術力の高さから多くの自動車メーカーで純正採用されています。\nOEM部品の中でトップクラスの品質となっています。",
    "NGK": "【NGK】\n優れた燃焼力が燃費アップを実現！\nNGKのスパークプラグは着火性、燃焼効率性、耐汚損性、耐消耗性、\nスパークプラグに求められるあらゆる性能を高次元で凌駕したスパークプラグです。",
    "HELLA": "【HELLA】\nHELLA社は、100年以上の歴史と世界約35ヶ国に100ヶ所以上の拠点を持ち\n高品質で高性能な自動車部品や用品を製造する,世界トップ クラスのグローバルな上場企業です。\nその品質は主にBENZやBMWなどの欧州自動車メーカーへOEM(純正部品)として長年供給され続けています。",
    "大野ゴム": "【大野ゴム】\n大野ゴム工業株式会社は、1947年創業の老舗ゴム製品メーカー。\n自動車用の補修ゴム部品を中心に、オイルシールやOリング、ブッシュ、ホースなど多岐にわたる製品を製造・販売しています。\n国内生産にこだわった高品質な製品は、純正品と同等の信頼性と耐久性を誇り、全国の整備工場やパーツ業者から厚い支持を集めています。\n\n純正部品ではコストがかかる場面でも、大野ゴムなら高いコストパフォーマンスで対応可能！\n特に足回りやエンジンまわりのゴムパーツ交換時には、確かな互換性と安心の日本品質で選ばれ続けています。\n補修部品を長く使いたい方、DIYメンテナンスを楽しむ方にもおすすめの、信頼と実績を誇る国産ブランドです。",
    "INTEX": "【INTEX】\nINTEX（インテックス）は、家庭用プールやエアベッド、ウォーター関連製品を中心に展開するアメリカ発の企業で\n世界100か国以上で製品が販売されており、日本国内でも広く流通しているグローバルブランドです。\n手頃な価格で家庭にアウトドア気分を取り入れたい人々にとって、非常に人気のあるブランドとなっています。",
    "BESTWAY": "【BESTWAY】\nBESTWAY（ベストウェイ）は、世界100か国以上で愛されているアウトドア＆レジャー用品ブランドです。\n家庭用プール、エアベッド、SUPなど、手軽に楽しめる高品質なインフレータブル製品を幅広く展開しています。\n手頃な価格と信頼の品質で、世界中のご家庭に楽しい時間をお届けしています。",
    "MAHLE": "【MAHLE】\nMAHLE（マーレ）は、ドイツ発祥の自動車部品メーカーとして世界的に高い信頼を誇るブランドです。\nエンジン部品、フィルター、空調システムなど幅広い製品群を展開し、自動車の性能と環境性能の両立を追求しています。\n多くの自動車メーカーに純正採用されており、その高品質と耐久性は折り紙付き。\n当店ではMAHLE製品を通じて、確かなパフォーマンスと安心のメンテナンスをお届けします。",
    "三ツ星ベルト": "【三ツ星ベルト】\n三ツ星ベルトは、自動車から産業機械まで幅広い分野で選ばれている日本のトップブランドです。\n高い耐久性と安定した性能で、エンジンや機械の動きをしっかりサポート。\nタイミングベルトやファンベルトをはじめ、数多くの車種や設備に純正採用されており\n交換部品としても安心してお使いいただけます。",
    "Miyako": "【Miyako】\nMiyako（ミヤコ）はブレーキ関連部品や油圧ホースなどを中心に高品質な自動車部品を供給する日本メーカーです\n長年にわたり国内外の整備士やカーショップから信頼され、純正互換品として高い適合性と耐久性を誇ります\n優れた制動性能と確かな品質管理により、安心・安全な走行を支えるのがMiyakoの使命です\n国産車から輸入車まで幅広く対応し、コストパフォーマンスにも優れたラインナップで、交換用パーツ選びに最適なブランドです",
    "RAICAM": "【RAICAM】\nRAICAM（ライカム）は、1982年にイタリアで創業したグローバル自動車部品メーカーです。\nクラッチやブレーキシステム、アクチュエーターなどの駆動系部品を中心に、\nOEMからアフターマーケットまで幅広いニーズに応える高品質製品を提供しています。\n特に、摩擦材やトルク伝達技術においては、40年以上にわたる実績と独自の技術力を誇り\nフォード、フィアット、ルノーなど、世界の有力自動車メーカーに採用されています。",
    "DEPO": "【DEPO】\nDEPO（デポ）は、自動車用ヘッドライトやテールランプなどのライティングパーツを中心に展開する台湾の大手自動車部品メーカーです。\n世界中のアフターマーケット市場で高いシェアを誇り、品質とコストパフォーマンスのバランスに優れた製品を提供しています。\nISO認証を取得した自社工場で製造され、厳しい品質基準に基づいた検査体制も整備。\n純正同等のフィッティング性と信頼性で、世界各国のユーザーから支持を集めています。",
    "安心の純正OEM品": "【安心の純正OEM品】\n世界基準のECMマーク取得！\n本商品は、実際に自動車メーカーへ純正部品を供給している信頼のメーカーから直送された高品質なパーツです。\nメーカー純正と同等の品質を、よりお求めやすい価格でご提供！確かな製品をお探しの方におすすめの一品。\n交換用・メンテナンス用として安心してご使用いただけます。",
    "Kashimura": "【Kashimura】\nカシムラは、ドライブをより快適・便利にするカー用品を多数手掛ける日本の老舗メーカーです。\n充電器や変換プラグ、電圧計、車載用アクセサリーなど、実用性と安全性を兼ね備えた製品を幅広く展開。\n確かな品質と使いやすさで、多くのドライバーから信頼を集めています。\n日常のカーライフをサポートするアイテムとして、長く安心してお使いいただけます。",
    "ALIC": "【ALIC】\n国際認証を取得している、大手二輪部品メーカーALIC\n中間業者を通さない当社だから出来る価格にてご案内しております。\n耐久性、安定性にプロメカニックから高い評価を得ています。",
    "INTEX+SOLろ過機": "【INTEX】\nINTEX（インテックス）は、家庭用プールやエアベッド、ウォーター関連製品を中心に展開するアメリカ発の企業で\n世界100か国以上で製品が販売されており、日本国内でも広く流通しているグローバルブランドです。\n手頃な価格で家庭にアウトドア気分を取り入れたい人々にとって、非常に人気のあるブランドとなっています。\n\n【SOL オリジナルモデル PSE認証取得ろ過機】\n暑い季節、プールあそびは子どもたちにとって最高の時間。でも気になるのは、水の汚れや安全性ですよね。\nSOLのろ過機は、PSE認証取得済みで、電気用品としての安全性も国が認めた安心設計。\n小さなお子さまがいるご家庭でも、毎日清潔・安心な水質を保つことができます。"
}

# バナー設定
BANNER_MAPPING = {
    "CAPSOL オルタ": [
        "https://shopping.c.yimg.jp/lib/solltd/str_ignition_coil1.jpg",
        "https://shopping.c.yimg.jp/lib/solltd/CAPSOLALT2.jpg",
        "https://shopping.c.yimg.jp/lib/solltd/CAPSOLALT3.jpg"
    ],
    "CAPSOL 電動ファンモーター": [
        "https://shopping.c.yimg.jp/lib/solltd/str_ignition_coil1.jpg",
        "https://shopping.c.yimg.jp/lib/solltd/CAPSOLFAN2.jpg",
        "https://shopping.c.yimg.jp/lib/solltd/CAPSOLFAN3.jpg"
    ],
    "HAPAD パッド": [
        "https://shopping.c.yimg.jp/lib/solltd/yshapad1.jpg",
        "https://shopping.c.yimg.jp/lib/solltd/yshapad2.jpg",
        "https://shopping.c.yimg.jp/lib/solltd/yshapad3.jpg"
    ],
    "HAPAD ローター": [
        "https://shopping.c.yimg.jp/lib/solltd/ysrotor-1.jpg",
        "https://shopping.c.yimg.jp/lib/solltd/ysrotor-2.jpg",
        "https://shopping.c.yimg.jp/lib/solltd/ysrotor-3.jpg"
    ],
    "プレミアムHAPAD パッド": [
        "https://shopping.c.yimg.jp/lib/solltd/PRMhapad1.jpg",
        "https://shopping.c.yimg.jp/lib/solltd/PRMhapad2.jpg",
        "https://shopping.c.yimg.jp/lib/solltd/prmhapad3.jpg",
        "https://shopping.c.yimg.jp/lib/solltd/PRMhapad4.jpg"
    ],
    "CAPSOL スノーワイパー": [
        "https://shopping.c.yimg.jp/lib/solltd/CAPSNOW1.jpg",
        "https://shopping.c.yimg.jp/lib/solltd/CAPSNOW2.jpg",
        "https://shopping.c.yimg.jp/lib/solltd/CAPSNOW3.jpg"
    ],
    "CAPSOL ラジエーター": [
        "https://shopping.c.yimg.jp/lib/solltd/capsol_raji1.jpg"
    ],
    "CAPSOL 強化コイル": [
        "https://shopping.c.yimg.jp/lib/solltd/str_ignition_coil1.jpg",
        "https://shopping.c.yimg.jp/lib/solltd/str_ignition_coil2.jpg",
        "https://shopping.c.yimg.jp/lib/solltd/str_ignition_coil3.jpg"
    ],
    "CAPSOL コンデンサー": [
        "https://shopping.c.yimg.jp/lib/solltd/str_ignition_coil1.jpg",
        "https://shopping.c.yimg.jp/lib/solltd/CAPSOLCON2.jpg",
        "https://shopping.c.yimg.jp/lib/solltd/CAPSOLCON3.jpg"
    ],
    "CAPSOL エアコンフィルター": [
        "https://shopping.c.yimg.jp/lib/solltd/str_ignition_coil1.jpg",
        "https://shopping.c.yimg.jp/lib/solltd/CAPSOLFIL2.jpg",
        "https://shopping.c.yimg.jp/lib/solltd/CAPSOLFIL3.jpg"
    ],
    "HELLA": [
        "https://shopping.c.yimg.jp/lib/solltd/yshella.jpg"
    ],
    "INTEX": [
        "https://shopping.c.yimg.jp/lib/solltd/INTEX-01.jpg",
        "https://shopping.c.yimg.jp/lib/solltd/INTEX-02.jpg"
    ],
    "水鉄砲": [
        "https://shopping.c.yimg.jp/lib/solltd/watergun-01.jpg",
        "https://shopping.c.yimg.jp/lib/solltd/watergun-02.jpg",
        "https://shopping.c.yimg.jp/lib/solltd/watergun-03.jpg"
    ],
    "CAPSOL ベルト": [
        "https://shopping.c.yimg.jp/lib/solltd/str_ignition_coil1.jpg",
        "https://shopping.c.yimg.jp/lib/solltd/capsolbelt.jpg"
    ],
    "CAPSOL ステアリング": [
        "https://shopping.c.yimg.jp/lib/solltd/str_ignition_coil1.jpg",
        "https://shopping.c.yimg.jp/lib/solltd/capsteering.jpg"
    ],
    "プレミアムHAPAD ローター": [
        "https://shopping.c.yimg.jp/lib/solltd/prmrotor.jpg",
        
    ],
    "CAPSOL ACコンプレッサー": [
        "https://shopping.c.yimg.jp/lib/solltd/str_ignition_coil1.jpg",
        "https://shopping.c.yimg.jp/lib/solltd/CAPSOLACCO2.jpg",
        "https://shopping.c.yimg.jp/lib/solltd/CAPSOLACCO3.jpg",
    ],
    "CAPSOL NOXセンサー": [
        "https://shopping.c.yimg.jp/lib/solltd/str_ignition_coil1.jpg",
        "https://shopping.c.yimg.jp/lib/solltd/NOX1.jpg",
    ]

}

# 特大商品専用HTMLブロック
OVERSIZE_HTML_BLOCK = (
    '<br><br><b>【特大商品の配送について】</b><br>'
    '※本商品は特大サイズのため、<b>西濃運輸</b>または<b>福山通運</b>での配送となります。運送便のご指定は一切できません。<br>'
    '※<b>個人宅様宛の配送はできません。</b>お届け先が個人宅様の場合、最寄りの運送会社営業所留めでの発送となります。<br>'
    '※企業様宛の場合でも、<b>配送時間の指定はできません</b>のでご了承ください。<br>'
    '※営業所留めを希望される場合、ご注文時にご希望の営業所名・営業所住所をご要望欄へご指定ください。<br>'
    '※発送予定の運送会社を確認されたい方は、ご注文前に必ずお問い合わせください。<br>'
    '<b>●発送のタイミングについて</b><br>'
    '当日発送は16時受付分まで可能です（特大商品の場合、集荷時間の都合により翌日以降の発送となる場合がございます）。'
)

CATEGORY_MAPPING = {
    "アウトドア　タープ、テントペグ": "2641",
    "その他バイク用　キャブレター、吸気系パーツ": "3533",
    "自動車用　バッテリー充電器、発電機": "3492",
    "その他足回り、サスペンション用品": "42473",
    "バイク ヘッドライトバルブアッシー": "13710",
    "自動車用　ボンネットインシュレーター": "41879",
    "エアクリーナー（純正交換型）": "43968",
    "バイク 外装セット、フルカウル": "13696",
    "自動車用　ダウンサス、スプリング": "13894",
    "その他自転車用ヘルメット": "4920",
    "釣り　タモ網、ランディングネット": "2758",
    "自動車用　その他燃料系パーツ": "41894",
    "自動車用　サンシェイド、バイザー": "13948",
    "その他バイク用　ライト、レンズ": "3555",
    "スタンド（工具箱、ケース、トレー": "42004",
    "自動車用　エンジンヘッドカバー": "21979",
    "ハンドルカバー、ステアリング": "13898",
    "自動車用　オートマオイル(ATF)": "3471",
    "トラック用　ドアサイドマーカー": "42114",
    "自動車用 オイルキャッチタンク": "21980",
    "自転車本体　セグウェイ式車両": "42345",
    "自動車用　負圧計、バキューム計": "22003",
    "その他キッチン、日用品、文具": "4247",
    "自動車用　ホイールシリンダー": "41838",
    "リアスポイラー、ウイング": "13867",
    "自動車用　フューエルフィルター": "3500",
    "マフラーリング、ブッシュ": "41748",
    "バイク バックパック、デイバッグ": "13660",
    "バイク用　イグナイタ、CDI": "13779",
    "自動車用　タペット系パーツ": "3449",
    "その他足回り、サスペンション用品": "42473",
    "ショックアブソーバー": "13895",
    "自動車用インテリアパネル": "21937",
    "ドライブシャフトブーツ": "15109",
    "アウトドア　クーラーボックス": "2597",
    "トラック用　コンプレッサー": "42132",
    "イグニッションコイル": "21981",
    "トラック用　ワイパーパネル": "42095",
    "自動車用　アクチュエーター": "41873",
    "自動車　ミッションマウント": "41849",
    "自動車用　デフマウント": "41850",
    "トラック用　ミラーカバー": "42110",
    "トラック用　ハンドルカバー": "42069",
    "トラック　バンパー用ステー": "42089",
    "バイク用フロントフォーク": "13797",
    "その他ホイール関連用品": "13621",
    "自動車用　消臭、芳香剤": "13973",
    "自動車用　ワイパースタンド": "41803",
    "カナード、ディフューザー": "13870",
    "自動車用　インジェクター": "41888",
    "その他バッグ(子ども用)": "1575",
    "自動車用オイルクーラー": "13885",
    "自動車用　フィラーキャプ": "41877",
    "自動車用　シリコンホース": "41896",
    "空気清浄機交換フィルター": "31695",
    "オイルレベルゲージ": "41880",
    "オイルフィラーキャップ": "41881",
    "ウォッシャーポンプ": "3449",
    "その他ブレーキパーツ": "42472",
    "ウォッシャータンク": "13957",
    "ウォッシャーノズル": "13957",
    "その他冷却系パーツ": "13887",
    "タイミングベルト": "15111",
    "フロントスポイラー": "13865",
    "バイク用フューエルコック": "13757",
    "自動車用外装モール": "41789",
    "バイク用フューエルポンプ": "13759",
    "自動車　タイロッドカバー": "41833",
    "自動車　ドライブシャフト": "15108",
    "自動車用ラゲッジマット": "13942",
    "トラック用　ドアバイザー": "42098",
    "タイヤ、ホイールその他": "5307",
    "バイク ブレーキホース": "13808",
    "バイク 補修、補強用品": "13818",
    "自動車用　ドレンボルト": "41878",
    "車内用ドリンクホルダー": "13849",
    "自動車用　カムプーリー": "21976",
    "自動車用　カムシール": "41885",
    "自動車用プラグコード": "13904",
    "自動車用　パワステベルト": "41883",
    "トラック用　フォグランプ": "42124",
    "自動車用　エンブレム": "41787",
    "自動車　その他ライト": "3465",
    "バイク用スプロケット": "13793",
    "エアコンフィルター": "13962",
    "エアロガーニッシュ": "13871",
    "エンジンマウント": "13878",
    "オルタネーター": "13858",
    "クーラーベルト": "41882",
    "コーナーパネル": "42092",
    "コントロールアーム": "42473",
    "ボールジョイント": "42473",
    "ターボチャージャー": "21998",
    "自動車用バッテリー": "3455",
    "ハブベアリング": "21926",
    "ピロテンションロッド": "13911",
    "フューエルポンプ": "41889",
    "ブレーキローター": "3458",
    "フロントバンパー": "42088",
    "フロントグリル": "21949",
    "ランプレンズASSY": "13923",
    "自動車ワイパー": "22164",
    "ブリーザータンク": "41899",
    "ワイパーブレード": "13927",
    "ラジエターキャップ": "13889",
    "補助照明、イルミネーション": "44760",
    "その他駆動系パーツ": "13883",
    "バイク セルモーター": "13778",
    "バイク スパークプラグ": "3540",
    "バイク レギュレーター": "13777",
    "その他バイク外装パーツ": "3532",
    "アウトドアテーブル": "2635",
    "ロアアームバー": "21988",
    "バイク ブレーキシュー": "22120",
    "自転車 ヘッドライト": "29572",
    "自転車 インナーチューブ": "13619",
    "自動車用スイッチ": "14008",
    "デッドニング用品": "13838",
    "自動車用　燃費グッズ": "41893",
    "ボンネットダンパー": "41768",
    "ワイパー替えゴム": "13928",
    "バイク用プーリー": "13794",
    "その他自動車用工具": "3434",
    "トラック用　丸型テール": "42105",
    "トラック用　ナットカバー": "42129",
    "バイク用　スピーカー": "42166",
    "コンソールボックス": "21943",
    "バイク　ローダウンキット": "13800",
    "フルエアロパーツ": "13864",
    "バイク用フューエルフィルター": "13758",
    "ATFフィルター": "41795",
    "ウォーターポンプ": "15113",
    "ウォッシャー液": "3469",
    "エキマニ、EXマニ": "13917",
    "オイルエレメント": "3499",
    "コンデンサー": "41897",
    "交換、補修パーツ": "41752",
    "サーモスタット": "13886",
    "スタビライザー": "13896",
    "スパークプラグ": "13903",
    "セルモーター": "13856",
    "その他点火系パーツ": "13782",
    "その他外装パーツ": "13957",
    "その他吸気系パーツ": "43969",
    "その他内装用品": "13938",
    "テールライト": "29571",
    "ドアミラー": "41772",
    "トランスミッション": "3545",
    "ファンベルト": "15110",
    "フォグランプ": "13715",
    "ブレーキパッド": "3457",
    "ホイールキャップ": "15102",
    "マッドガード": "41775",
    "ルームランプ": "13937",
    "照明ウィンカー": "42113",
    "その他車内電装品": "3415",
    "レジャーシート": "2636",
    "ブレーキホース": "13906",
    "その他補強パーツ": "13914",
    "車　トランスミッション": "41847",
    "バイク用　ラジエーター": "13747",
    "タイヤチェーン": "41701",
    "バイク ジェネレーター": "13776",
    "トラック用　ミラー": "42109",
    "その他ワイパー": "3466",
    "ドアハンドル": "41776",
    "パワステオイル": "3474",
    "ブレーキシュー": "21986",
    "メーターパネル": "13920",
    "ボディカバー": "3412",
    "ドアバイザー": "41773",
    "サイレンサー": "21992",
    "サイドステップ": "13866",
    "自動車用　ダクト": "41774",
    "トラック用　寝台パネル": "42101",
    "トラック用　泥よけ": "42128",
    "自動車用フェンダー": "13874",
    "塗装用スプレーガン": "3921",
    "バイク 車載工具": "22160",
    "モバイルバッテリー": "31786",
    "PCパーツその他": "14123",
    "ワイヤレス充電器": "14178",
    "スマートキーカバー": "41785",
    "ホイールスペーサー": "14033",
    "自立式ハンモック": "24397",
    "カースピーカー": "41710",
    "ディープソケット": "41975",
    "その他車用マット": "13944",
    "マッサージ器": "44592",
    "その他インテリア時計": "5253",
    "触媒、キャタライザー": "21995",
    "イヤホン本体": "22681",
    "ティッシュケース": "3594",
    "自動車用　ホーン": "41788",
    "電装用テスター": "13995",
    "アウトドアチェア": "2634",
    "潤滑油、作動油": "22037",
    "O2センサー": "21994",
    "エアサス": "13892",
    "クラッチ": "13880",
    "クランクシール": "41886",
    "ロアアーム": "42473",
    "ハブリング": "21926",
    "バンパー": "21951",
    "ペダル": "21938",
    "ヘッドライト": "13707",
    "ヘッドガスケット": "13877",
    "ホーン": "3550",
    "ラジエーター": "13888",
    "電動ファン": "41901",
    "ブロアファン": "41901",
    "ブロワファン": "41901",
    "ブロアモーター": "41901",
    "ブロワモーター": "41901",
    "ファンモーター": "41901",
    "角マーカー": "42118",
    "その他": "3477",
    "家庭用プール": "2151",
    "その他水遊び玩具": "2154",
    "油圧計": "41854",
    "水温計": "22004",
    "アンテナアース": "21948",
    "LED": "21955",
    "HID": "21961",
    "トランクバー": "41783",
    "バイク　ガソリン添加剤": "22142",
    "ハロゲン": "21964",
    "特殊形状ソケット": "41985",
    "モニター": "3423",
    "加湿器": "31702",
    "置き時計": "40555",
    "添加剤": "13961",
    "センサー": "41867",
    "ステップ": "42104",
    "フェンダー": "42102"
}

BRAND_CODE_MAPPING = {
    "三菱": "2328",
    "ホンダ": "3909",
    "BMW": "13208",
    "スズキ": "14684",
    "トヨタ": "15839",
    "日産": "15840",
    "マツダ": "15841",
    "スバル": "15842",
    "ダイハツ": "15843",
    "レクサス": "18477",
    "メルセデスベンツ": "18479",
    "フォルクスワーゲン": "18480",
    "アウディ": "18482",
    "ポルシェ": "59744",
    "大野ゴム": "25434",
    "いすゞ": "18485",
    "日野自動車": "61090",
    "光岡自動車": "18517",
    "フィアット": "18495",
    "フォード": "18489",
    "アルファロメオ": "18493",
    "ルノー": "18494",
    "シボレー": "18491",
    "クライスラー": "18503",
    "ダッジ": "18500",
    "ジープ": "18499",
    "ミニ": "18496",
    "サーブ": "18511",
    "オペル": "5972",
    "ランドローバー": "18515",
    "プジョー": "1637",
    "シトロエン": "18497",
    "ボルボ": "18490",
    "ジャガー": "3148",
    "MG": "59746",
    "ローバー": "18501",
    "ヒュンダイ": "35910",
    "ISSE": "70329",
    "ベントレー": "18516",
    "三菱ふそう": "34949",
    "フェラーリ": "3170",
    "Kashimura": "17073",
    "大東プレス": "25447",
    "unknown": "38074",
    "INTEX": "53377",
    "アルピナ": "18498",
    "スマート": "18512",
    "アイシン": "17097",
    "アバルト": "20287",
    "マセラッティ": "18505",
    "キャデラック": "18509",
    "カワサキ": "14683",
    "ヤマハ": "2039",
    "DSオートモビル": "18497",
    "GEELY": "38074",
    "GM": "18491",
    "デイムラー": "3148",
    "テスラ": "38074",
    "ロールスロイス": "18498"
}

def get_lenb_half(text):
    count = 0.0
    for char in text:
        status = unicodedata.east_asian_width(char)
        if status in 'FWA':
            count += 1.0
        else:
            count += 0.5
    return count

# ==========================================
# メインアプリケーション
# ==========================================
def show_seo_generator():
    st.title("📝 AutoPage Generator：SEO・商品説明生成")
    st.markdown("商品名と特徴を入力して、モール向けのテキストを一括生成します。")
    
    with st.container():
        st.subheader("1. 商品情報の入力")
        item_type = st.radio(
            "商品種別",
            ["補修部品", "用品（自動車・バイク）", "その他雑貨（日用品・レジャー等）"],
            horizontal=True
        )
        product_name = st.text_input("商品名", placeholder="例：ラジエーター")
        product_features = st.text_area("商品の特徴", placeholder="例：オリジナルブランド、純正互換、ハイクオリティ、1年保証付など")
        char_count = st.number_input("生成する文字数（目安）", min_value=100, max_value=5000, value=300, step=100)
        
        if st.button("一括生成", type="primary"):
            if not product_name:
                st.warning("商品名を入力してください。")
            else:
                if item_type == "その他雑貨（日用品・レジャー等）":
                    persona = "あなたは幅広い商品のEC販売に特化した、凄腕のマーケティング担当者です。"
                    s1_repair_instr = ""
                    s2_repair_instr = ""
                else:
                    persona = "あなたは自動車部品のEC販売に特化した、凄腕のマーケティング担当者です。"
                    s1_repair_instr = "・関連する不具合症状（例：異音、劣化、水漏れ、故障、修理等）も適宜キーワードとして盛り込んでください。"
                    s2_repair_instr = "・商品名や関連する不具合症状（例：異音、劣化、水漏れ等）を自然な文脈で盛り込んでください。"

                prompt = f"""
{persona}
指示された4つのセクションについて、指定のフォーマットで出力してください。

【厳報・最優先事項】
・入力情報({product_name}, {product_features})にない情報は、決して捏造（ハルシネーション）しないでください。
・特定の車種名、型式、純正番号などが入力されていない場合は、それらを勝手に想像して含めてはいけません。
・不明な情報は含めず、与えられた情報のみで最大限の効果を発揮するテキストを作成してください。

【対象商品】
商品名: {product_name}
商品の特徴: {product_features}

=== セクション1：商品タイトル作成 ===
各モールの規約に合わせ、以下の構成で3パターンずつ出力してください。
・商品に別の呼び方（別名・代替名称）があれば、それらも適宜キーワードとして盛り込んでください。
{s1_repair_instr}

■ 楽天市場（SEOキーワード詰め込み・文字数最大型）
・【絶対遵守】1タイトル100文字〜120文字程度。ギリギリまでキーワードを詰め込んでください。
・入力情報にある場合に限り、[適合車種名] [型式] [純正互換番号] [関連キーワード] を盛り込むこと。
・入力にない車種名や型式は絶対に含めないでください。
- （タイトル案1）
- （タイトル案2）
- （タイトル案3）

■ Yahoo!ショッピング（クリック率重視型）
・65文字以内。
・車種名が入力されている場合のみ、タイトルの先頭に「【車種名 + 商品名】」を配置。
・車種名がない場合は、商品名から開始してください。
- （タイトル案1）
- （タイトル案2）
- （タイトル案3）

■ Amazon（規約準拠・シンプル型）
・65文字以内、特殊記号・「送料無料」等は一切含めないこと。
・構成は「ブランド名 + 商品名 (+ 入力があれば適合車種/主要スペック)」に限定。
- （タイトル案1）
- （タイトル案2）
- （タイトル案3）

=== セクション2：Yahoo!ショッピング用商品説明文 ===
※見出しの直後に改行。
※文章の冒頭は必ず【{product_name}】から書き始めてください。
※全体で約{char_count}文字。
※句点「。」ごとに必ず改行すること。行間に空白行は作らないこと。
{s2_repair_instr}
・商品に別の呼び方（別名・代替名称）があれば、それらも適宜使用してください。
・関連するSEOキーワードを自然に盛り込んでください。

=== セクション3：Yahoo!ショッピング用 仮想レビュー3件 ===
※見出しの直後に改行。
※各レビューは、内容を要約した【魅力的なタイトル】から書き始めてください。
※タイトルのすぐ次の行から本文を書いてください。
※全体で3件作成し、各レビューの間には「必ず1行の空白行」を入れて区切ってください。
※句点「。」で改行し、レビューの本文内には空白行を作らないこと。
※RAG対策：ユーザーの具体的な悩みと解決の結果を含めること。

=== セクション4：想定カテゴリコード・ディレクトリ ===
・主要モールのカテゴリパスを記載。

=== セクション5：部品の属する部位・カテゴリ ===
・入力された商品名から、その商品が自動車やバイクのどの部位に属するか（例：冷却系、エンジン周り、足回り、電装系、内装、外装など）を推測して簡潔に表示してください。
・表示例：ウォーターポンプの場合 → 【冷却系、エンジン周り】
・商品種別で「その他雑貨（日用品・レジャー等）」が選ばれている場合は、その商品の一般的なカテゴリ（例：夏用レジャー用品、生活家電など）を表示してください。

【禁止・厳守事項】
・記号のアスタリスク「*」は絶対に使用しないこと。
・「社外品なので」「ポン付けできない」等のネガティブワードは禁止。
・「絶対に直る」などの断定表現や性能保証は禁止。
・適合確認や注意喚起の文章は不要。
"""
                try:
                    with st.spinner("生成中..."):
                        model = genai.GenerativeModel("gemini-3-flash-preview")
                        response = model.generate_content(prompt)
                        result_text = response.text.replace("\n", "  \n")
                        st.subheader("2. 生成結果")
                        st.markdown(result_text)
                        st.success("完了しました！")
                except Exception as e:
                    st.error(f"生成中にエラーが発生しました: {e}")

def show_template_expansion():
    st.title("📊 AutoPage Generator：マスターページメーカー")
    st.markdown("マスタデータを適合車種ごとに展開し、管理番号を自動採番します。")
    
    uploaded_file = st.file_uploader("Excelファイルをアップロード (.xlsx)", type=["xlsx"])
    
    if uploaded_file:
        try:
            xl = pd.ExcelFile(uploaded_file)
            sheet_names = xl.sheet_names
            required_sheets = ["マスタ", "適合車種", "その他"]
            missing_sheets = [s for s in required_sheets if s not in sheet_names]
            
            if missing_sheets:
                st.error(f"以下のシートが見つかりません: {', '.join(missing_sheets)}")
                return
            
            df_master = pd.read_excel(uploaded_file, sheet_name="マスタ").fillna('')
            if "ブランド" in df_master.columns:
                df_master["ブランド"] = df_master["ブランド"].replace("なし", "")
                
            df_compat = pd.read_excel(uploaded_file, sheet_name="適合車種")
            if "ヤフオクカテゴリ" in df_compat.columns:
                df_compat["ヤフオクカテゴリ"] = df_compat["ヤフオクカテゴリ"].ffill()
            df_compat = df_compat.fillna('')
                
            df_others = pd.read_excel(uploaded_file, sheet_name="その他").fillna('')
            
            if df_master.empty:
                st.error("「マスタ」シートにデータがありません。")
                return

            if st.button("テンプレート展開を実行", type="primary"):
                with st.status("データ処理中...", expanded=True) as status:
                    master_row = df_master.iloc[0]
                    others_row = df_others.iloc[0] if not df_others.empty else pd.Series()
                    
                    base_id = str(master_row.get("管理番号", "NO_ID"))
                    st.write(f"ベース管理番号: `{base_id}` を取得しました。")
                    
                    st.write("適合車種をフィルタリング中...")
                    vehicles_data = []
                    current_maker_full = ""
                    current_maker_short = ""
                    auc_cat_col = "ヤフオクカテゴリ" if "ヤフオクカテゴリ" in df_compat.columns else None

                    for idx, row in df_compat.iterrows():
                        val = row.iloc[0]
                        val_str = str(val).strip()
                        if val_str.lower() == "nan": val_str = ""
                            
                        auc_cat_val = ""
                        if auc_cat_col:
                            raw_cat = row[auc_cat_col]
                            if pd.notna(raw_cat):
                                auc_cat_val = str(raw_cat).replace(".0", "").strip()
                                if auc_cat_val.lower() == "nan": auc_cat_val = ""
                                    
                        if not val_str and not auc_cat_val:
                            continue
                            
                        # メーカー行の判定（"/"が含まれるか、辞書に存在するか）
                        check_maker = val_str.split("/")[0].strip()
                        if "/" in val_str or check_maker in BRAND_CODE_MAPPING:
                            current_maker_full = val_str
                            current_maker_short = check_maker
                            continue
                            
                        vehicles_data.append((val_str, current_maker_full, current_maker_short, auc_cat_val))
                    
                    if not vehicles_data:
                        vehicles_data = [("", "", "", "")]
                    
                    st.write(f"対象車種数: {len(vehicles_data)} 件")
                    
                    expanded_data = []
                    for i, (vehicle, maker_full, maker_short, auc_cat) in enumerate(vehicles_data):
                        seq = f"{i+1:03}"
                        new_id = f"{base_id}-{seq}"
                        new_row = master_row.to_dict()
                        if not others_row.empty:
                            for k, v in others_row.to_dict().items():
                                if v: new_row[k] = v
                        new_row["新管理番号"] = new_id
                        if vehicle: new_row["車種名"] = vehicle
                        if maker_short: new_row["メーカー名"] = maker_short
                        if maker_full: new_row["メーカー名_フル"] = maker_full
                        if auc_cat: new_row["ヤフオクカテゴリ"] = auc_cat
                        expanded_data.append(new_row)
                    
                    st.write("CSV出力用に51項目へマッピング中...")
                    columns_51 = [
                        "path", "name", "code", "sub-code", "original-price", "price", "headline", "caption", "abstract", "explanation", 
                        "additional1", "additional2", "additional3", "jan", "ship-weight", "taxable", "meta-desc", "sale-period-start", 
                        "sale-period-end", "sale-limit", "sp-code", "pr-rate", "brand-code", "product-code", "delivery", "condition", 
                        "product-category", "display", "sp-additional", "lead-time-instock", "lead-time-outstock", "keep-stock", 
                        "postage-set", "taxrate-type", "auc-bcid", "auc-category", "auc-store-keyword", "auc-pref-code", "auc-postage", 
                        "auc-payment", "auc-condition", "auc-shipment", "auc-cod", "auc-taxable", "item-tag", "reserve-price", 
                        "reserve-sale-price", "reserve-member-price", "reserve-selling-period-start", "reserve-selling-period-end", 
                        "item-image-urls"
                    ]
                    
                    df_export = pd.DataFrame(columns=columns_51, index=range(len(expanded_data)))
                    
                    for i, data in enumerate(expanded_data):
                        df_export.loc[i, "path"] = "新規作成中"
                        df_export.loc[i, "code"] = data.get("新管理番号", "")
                        
                        brand = str(data.get("ブランド", "")).strip()
                        if brand == "社外品": brand = ""
                        maker = str(data.get("メーカー名", "")).strip()
                        maker_full = str(data.get("メーカー名_フル", maker)).strip()
                        vehicle = str(data.get("車種名", "")).strip()
                        title_str = str(data.get("タイトル", "")).strip()
                        title_words = title_str.split()
                        genuine_raw = str(data.get("純正品番", "")).strip()
                        genuine = genuine_raw.split("/")[0].strip()
                        fixed_phrase = "18時まで即日発送"
                        
                        base_parts = []
                        if brand: base_parts.append(brand)
                        if maker: base_parts.append(maker)
                        if vehicle: base_parts.append(vehicle)

                        current_parts = base_parts.copy()
                        
                        # タイトルの単語を前から順に足し算テスト
                        for word in title_words:
                            test_parts = current_parts + [word]
                            # genuineを含めた状態での文字数をテスト（全角換算）
                            test_full = test_parts.copy()
                            if genuine: test_full.append(genuine)
                            if get_lenb_half(" ".join(test_full)) <= 65.0:
                                current_parts.append(word)
                            else:
                                break
                                
                        if genuine:
                            current_parts.append(genuine)
                            
                        # 最後に fixed_phrase (18時まで即日発送) の足し算テスト
                        test_with_fixed = current_parts + [fixed_phrase]
                        if get_lenb_half(" ".join(test_with_fixed)) <= 65.0:
                            current_parts.append(fixed_phrase)
                            
                        final_name = " ".join(current_parts)
                        
                        # 安全装置：万が一オーバーする場合は末尾からカット
                        while get_lenb_half(final_name) > 65.0:
                            final_name = final_name[:-1]
                            
                        df_export.loc[i, "name"] = final_name.strip()
                        
                        h_maker = maker
                        h_vehicle = vehicle
                        h_part = title_words[0] if title_words else ""
                        def build_headline_base(m, v, p):
                            parts = [x for x in [m, v, p] if x]
                            return " ".join(parts)
                        res_headline = build_headline_base(h_maker, h_vehicle, h_part)
                        if get_lenb_half(res_headline) > 30.0:
                            for k in ["ターボ", "ワイド", "ロング", "クーペ"]:
                                h_vehicle = h_vehicle.replace(k, "").strip()
                            res_headline = build_headline_base(h_maker, h_vehicle, h_part)
                        if get_lenb_half(res_headline) > 30.0:
                            h_maker = ""
                            res_headline = build_headline_base(h_maker, h_vehicle, h_part)
                        if get_lenb_half(res_headline) > 30.0:
                            v_parts = h_vehicle.split()
                            if len(v_parts) > 1:
                                h_vehicle = v_parts[0]
                            res_headline = build_headline_base(h_maker, h_vehicle, h_part)
                        if get_lenb_half(res_headline) < 30.0:
                            item_type_for_headline = str(data.get("種別", "")).strip()
                            if item_type_for_headline == "用品":
                                # 種別が用品の場合：タイトルの2単語目以降を追加キーワードの候補にする
                                add_keywords = title_words[1:] if len(title_words) > 1 else []
                            else:
                                # 用品以外の場合：従来の固定キーワード
                                add_keywords = ["純正互換", "故障", "補修", "メンテナンス"]
                                
                            for kw in add_keywords:
                                temp_headline = f"{res_headline} {kw}".strip()
                                if get_lenb_half(temp_headline) <= 30.0:
                                    res_headline = temp_headline
                                else:
                                    break
                        df_export.loc[i, "headline"] = res_headline
                        df_export.loc[i, "price"] = data.get("販売価格", "")
                        
                        def safe_str(val):
                            if pd.isna(val) or val is None:
                                return ""
                            return str(val).strip()


                        shipping_val = safe_str(data.get("送料"))
                        is_oversize = shipping_val in ["特大A", "特大B", "特大C", "特大D"]

                        # 変数の再定義（J列処理削除による欠落の復旧）
                        spec = safe_str(data.get("商品仕様"))
                        desc_raw = safe_str(data.get("商品説明"))
                        desc_styled = re.sub(r'(【.+?】)', r'<B><font color="#ff0000">\1</font></B>', desc_raw) if desc_raw else ""
                        gen_no = safe_str(data.get("純正品番"))
                        suffix = "いずれかの取付車両に限ります。" if "/" in gen_no else "の取付車両に限ります。"

                        # --- K列 (additional1) と AC列 (sp-additional) のコンテンツ構築 ---
                        main_content_parts = []
                        
                        # 1. 商品の状態
                        item_status = safe_str(data.get('商品状態'))
                        if item_status:
                            main_content_parts.append(f"<B>●商品の状態</B><BR>{item_status.replace(chr(10), '<BR>')}<BR><BR>")
                        
                        # 2. 適合車種
                        if maker_full or vehicle:
                            main_content_parts.append(f"<B>●適合車種</B><BR>{maker_full}<BR>{vehicle}<BR>※上記車種にグレードや型式記載されている場合でも、年式・仕様等により適合しない場合が御座います。必ず実車に取付されている純正品番をご確認の上ご注文お願いします。<BR><BR>")
                        
                        # 3. 商品仕様
                        if spec:
                            main_content_parts.append(f"<B>●商品仕様</B><BR>{spec.replace(chr(10), '<BR>')}<BR><BR>")
                            
                        # 4. 商品説明
                        if desc_raw:
                            main_content_parts.append(f"<B>●商品説明</B><BR>{desc_styled.replace(chr(10), '<BR>')}<BR><BR>")
                            
                        # 5. 純正品番
                        if gen_no:
                            main_content_parts.append(f"<B>●純正品番</B><BR>{gen_no}{suffix}<BR>※適合にご不安がある場合、ご注文前に車体番号をご連絡頂ければ当店にてお調べ致します。<BR><BR>")
                        
                        # 5.5 セット内容
                        set_content = safe_str(data.get("セット内容"))
                        if set_content:
                            main_content_parts.append(f"<B>●セット内容</B><BR>{set_content.replace(chr(10), '<BR>')}<BR><BR>")
                        
                        # 6. ブランド説明
                        if brand and brand in BRAND_DESCRIPTIONS:
                            brand_desc_styled = BRAND_DESCRIPTIONS[brand].replace("\n", "<BR>")
                            brand_desc_styled = re.sub(r'(【.+?】)', r'<B><font color="#ff0000">\1</font></B>', brand_desc_styled)
                            main_content_parts.append(f"<B>●ブランド</B><BR>{brand_desc_styled}<BR><BR>")
                            
                        # 7. 管理番号
                        base_bcid = str(master_row.get("管理番号", "")).strip()
                        main_content_parts.append(f"<B>●管理番号</B><BR>{base_bcid}<BR><BR>")
                        
                        # 8. お客様の声
                        voc_raw = safe_str(data.get("お客様の声"))
                        if voc_raw:
                            main_content_parts.append(f"<B>●お客様の声</B><BR>{voc_raw.replace(chr(10), '<BR>')}<BR><BR>")
                        
                        # ===== 再構築ロジックここまで =====
                            
                        item_type = safe_str(data.get("種別"))
                        if item_type == "外装品" or item_type == "大型":
                            guarantee_block = (
                                '<B>●保証期間</B><BR>商品到着後14日以内の保証となります。<BR>'
                                '当店側のミスでお手元に届いた商品が違った場合は、商品到着後14日以内での対応となりますので、速やかな商品確認をお願い致します。<br><br>'
                                '<b>●保証について</b><br>保証内容はご購入頂いた商品のみとなります。<BR>'
                                '万が一商品に不具合が生じた場合新たに商品のご手配をさせて頂きますが、ご手配できない場合には商品代金のみご返金させて頂きます。<BR>'
                                '商品交換時に発生する費用および損害等は保証できませんのでご了承下さい。<BR>'
                                '保証申請時には商品の不良申請書または診断結果および診断書【コピーでも可】・お車の車検証をご提出いただく必要がございます。<BR>'
                                'また症状や状態によっては商品の状態の確認がとれるお写真をいただく場合もございます。<BR>'
                                '取付ミスによる不具合や破損、加工済は保証対象外となります。<br><br>'
                                '<B>●備考</B><br>弊社は専門店ではございませんので、取り付け方法・車検等のご質問にはお答えできかねます。<br>'
                                '本製品は輸入品の為、メーカー出荷時から塗装を施す前提で製造されております。<br>'
                                'ご利用には支障のない程度の微細な小キズ、微妙な撓りや汚れ、型から抜いた際のバリ等が付いている場合がございますので、'
                                '取付け時の板金塗装作業等で修正が必要となります。<br>ご理解の上、ご注文お願いします。 <br><br>'
                                '<B>●発送方法について</b><br>西濃運輸または福山通運での発送になります。<BR>'
                                '※運送便のご指定は一切できません。<BR>※個人宅様宛の配送はできません。<br>'
                                '※企業様宛ての時間指定はできませんのでご了承ください。<BR> <BR>'
                                '営業所留めを希望される場合、ご注文時にご希望の営業所名・営業所住所をご要望欄へご指定下さい。 <BR>'
                                '※発送予定の運送会社を確認されたい方は、ご注文前に必ずお問い合わせください。<br><br>'
                                '<b>●発送のタイミングについて</b><br>当日発送16時まで可能です。<br>'
                                'ご注文のタイミングによっては、当日発送が出来ない場合がございますのでご了承下さい。'
                            )
                        elif item_type == "用品":
                            guarantee_block = (
                                '<B>●保証期間</B><BR>商品到着後14日以内の保証となります。<BR>'
                                '当店側のミスでお手元に届いた商品が違った場合は、商品到着後14日以内での対応となりますので、速やかな商品確認をお願い致します。<br><br>'
                                '<b>●保証について</b><br>保証内容はご購入頂いた商品のみとなります。<BR>'
                                '万が一商品に不具合が生じた場合新たに商品のご手配をさせて頂きますが、ご手配できない場合には商品代金のみご返金させて頂きます。<BR>'
                                '商品交換時に発生する費用および損害等は保証できませんのでご了承下さい。<BR>'
                                '保証申請時には商品の不良申請書または診断結果および診断書【コピーでも可】・お車の車検証をご提出いただく必要がございます。<BR>'
                                'また症状や状態によっては商品の状態の確認がとれるお写真をいただく場合もございます。<BR>'
                                '取付ミスによる不具合や破損、加工済は保証対象外となります。<br><br>'
                            )
                        else:
                            guarantee_block = (
                                '<B>●保証期間</B><BR>商品到着後6ヶ月間の商品保証を致します。<BR>'
                                'この商品の初期不良期間は商品到着後14日間です。<br>'
                                '当店側のミスでお手元に届いた商品が違った場合は、商品到着後14日間以内での対応となりますので、速やかな商品確認をお願い致します。<br><br>'
                            )
                        main_content_parts.append(guarantee_block)
                        if is_oversize:
                            main_content_parts.append(OVERSIZE_HTML_BLOCK)
                        main_content_html = "".join(main_content_parts)

                        # --- J列 (explanation) の構築（完全最適化＆スマートカット版） ---
                        status_block = f"●商品の状態\n{item_status}" if item_status else ""
                        
                        valid_maker = maker_full if maker_full.lower() not in ["nan", "none", ""] else ""
                        valid_vehicle = vehicle if vehicle.lower() not in ["nan", "none", ""] else ""
                        compat_block = ""
                        if valid_maker or valid_vehicle:
                            v_lines = [x for x in [valid_maker, valid_vehicle] if x]
                            v_lines.append("※上記車種にグレードや型式記載されている場合でも、年式・仕様等により適合しない場合が御座います。必ず実車に取付されている純正品番をご確認の上ご注文お願いします。")
                            compat_block = "●適合車種\n" + "\n".join(v_lines)
                            
                        spec_block = f"●商品仕様\n{spec}" if spec else ""
                        
                        desc_header = ""
                        desc_body_lines = []
                        if desc_raw:
                            desc_lines = [line.strip() for line in desc_raw.strip().split("\n") if line.strip()]
                            if desc_lines:
                                desc_header = f"●商品説明\n{desc_lines[0]}"
                                desc_body_lines = desc_lines[1:]
                                
                        is_fit_check_impossible = str(data.get("適合確認可否", "")).strip() == "不可"
                        fit_check_notes = "※こちらの商品は当社側で適合確認ができないメーカーの為、メーカー品番又は純正品番のご確認をお願い致します。" if is_fit_check_impossible else "※適合にご不安がある場合、ご注文前に車体番号をご連絡頂ければ当店にてお調べ致します。"
                        genuine_block = f"●純正品番\n{gen_no}{suffix}\n{fit_check_notes}" if gen_no else ""
                        
                        set_block = f"●セット内容\n{set_content}" if set_content else ""
                        brand_block = f"●ブランド\n{BRAND_DESCRIPTIONS[brand]}" if (brand and brand in BRAND_DESCRIPTIONS) else ""
                        
                        voc_raw = safe_str(data.get("お客様の声"))
                        if voc_raw.startswith("●お客様の声"):
                            voc_raw = re.sub(r'^●お客様の声\s*', '', voc_raw)
                        voc_list = [r.strip() for r in re.split(r'\n\s*\n', voc_raw) if r.strip()] if voc_raw else []

                        def get_sjis_bytes(text):
                            plain = re.sub(r'<[^>]+>', '', text)
                            return len(plain.encode('cp932', errors='ignore'))
                            
                        def build_candidate(voc_to_use, desc_body_to_use, use_empty_lines=True, include_optional=True):
                            all_blocks = []
                            if status_block: all_blocks.append(status_block)
                            if compat_block: all_blocks.append(compat_block)
                            
                            if include_optional:
                                if spec_block: all_blocks.append(spec_block)
                                desc_block = ""
                                if desc_header:
                                    if desc_body_to_use:
                                        desc_block = desc_header + "\n" + "\n".join(desc_body_to_use)
                                    else:
                                        desc_block = desc_header
                                if desc_block: all_blocks.append(desc_block)
                                
                            if genuine_block: all_blocks.append(genuine_block)
                            if set_block: all_blocks.append(set_block)
                            
                            if include_optional:
                                if brand_block: all_blocks.append(brand_block)
                                voc_block = ""
                                if voc_to_use:
                                    voc_block = "●お客様の声\n" + "\n\n".join(voc_to_use)
                                if voc_block: all_blocks.append(voc_block)
                                
                            join_sep = "\n\n" if use_empty_lines else "\n"
                            res = join_sep.join(all_blocks)
                            if not use_empty_lines:
                                lines = [line.strip() for line in res.split("\n") if line.strip()]
                                res = "\n".join(lines)
                            return res

                        final_exp = ""
                        
                        # --- 通常状態 (ステップ0) ---
                        candidate = build_candidate(voc_list, desc_body_lines, use_empty_lines=True, include_optional=True)
                        if get_sjis_bytes(candidate) <= 1000:
                            final_exp = candidate
                            
                        # --- ステップ1: 空白行の削除 ---
                        if not final_exp:
                            candidate = build_candidate(voc_list, desc_body_lines, use_empty_lines=False, include_optional=True)
                            if get_sjis_bytes(candidate) <= 1000:
                                final_exp = candidate
                                
                        # --- ステップ2: お客様の声の下からブロック単位削除 ---
                        if not final_exp:
                            for i_voc in range(len(voc_list) - 1, -1, -1):
                                candidate = build_candidate(voc_list[:i_voc], desc_body_lines, use_empty_lines=False, include_optional=True)
                                if get_sjis_bytes(candidate) <= 1000:
                                    final_exp = candidate
                                    break
                                    
                        # --- ステップ3: 商品説明の下から1行ずつ削除 ---
                        if not final_exp:
                            for j_line in range(len(desc_body_lines) - 1, -1, -1):
                                candidate = build_candidate([], desc_body_lines[:j_line], use_empty_lines=False, include_optional=True)
                                if get_sjis_bytes(candidate) <= 1000:
                                    final_exp = candidate
                                    break
                                    
                        # --- ステップ4: 優先度の低いブロックの丸ごと削除 (必須ブロックのみ残す) ---
                        if not final_exp:
                            candidate = build_candidate([], [], use_empty_lines=False, include_optional=False)
                            if get_sjis_bytes(candidate) <= 1000:
                                final_exp = candidate
                                
                        # --- ステップ5: 最終命綱 (必須ブロックの強制カット) ---
                        if not final_exp:
                            candidate = build_candidate([], [], use_empty_lines=False, include_optional=False)
                            while get_sjis_bytes(candidate) > 1000:
                                candidate = candidate[:-1]
                            final_exp = candidate
                            
                        df_export.loc[i, "explanation"] = final_exp

                        # ヘッダーHTMLの組み立て
                        banner_val = safe_str(data.get("バナー"))
                        add1_banner_html = ""
                        sp_banner_html = ""
                        
                        if banner_val in BANNER_MAPPING:
                            for b_url in BANNER_MAPPING[banner_val]:
                                add1_banner_html += f'<IMG SRC="{b_url}"><BR><BR>'
                                sp_banner_html += f'<IMG SRC="{b_url}" style="width: 100%;"><BR><BR>'
                            
                            if banner_val == "INTEX":
                                add1_banner_html += '<A HREF="https://store.shopping.yahoo.co.jp/solltd/search.html?p=intex#CentSrchFilter1" TARGET="new"><IMG SRC="https://shopping.c.yimg.jp/lib/solltd/INTEX-03.jpg"></a><BR><BR>'
                                sp_banner_html += '<A HREF="https://store.shopping.yahoo.co.jp/solltd/search.html?p=intex#CentSrchFilter1" TARGET="new"><IMG SRC="https://shopping.c.yimg.jp/lib/solltd/INTEX-03.jpg" style="width: 100%;"></a><BR><BR>'

                        # ベース画像の選択
                        base_img_file = "hapadparts01.jpg" if banner_val in ["HAPAD パッド", "HAPAD ローター", "プレミアムHAPAD パッド"] else "parts01.gif"

                        add1_header = f'<center><IMG SRC="https://shopping.c.yimg.jp/lib/solltd/960.jpg"><BR><BR><IMG SRC="https://shopping.c.yimg.jp/lib/solltd/{base_img_file}"><BR><BR>{add1_banner_html}</center><B>【商品詳細】<BR></B>'
                        df_export.loc[i, "additional1"] = add1_header + main_content_html
                        
                        sp_main_content = re.sub(r'</?font[^>]*>', '', main_content_html)
                        sp_header = f'<IMG SRC="https://shopping.c.yimg.jp/lib/solltd/960.jpg" style="width: 100%;"><BR><BR><IMG SRC="https://shopping.c.yimg.jp/lib/solltd/{base_img_file}" style="width: 100%;"><BR><BR>{sp_banner_html}<B>【商品詳細】<BR></B>'
                        df_export.loc[i, "sp-additional"] = sp_header + sp_main_content

                        # additional2 の共通ブロックを定義
                        guarantee_link_block = '<div style="border: 3px solid #ff9933; border-radius:5px; padding:10px;"><p><b>保証について</b><br>保証内容はご購入頂いた商品のみとなります。<br>当社では初期不良、商品保証期間で対応が異なります。<br><span style="color:red"><b><a href="https://store.shopping.yahoo.co.jp/solltd/solpage01.html" target="new">コチラ</a></b>をご一読ください。</span></p></div><br>'

                        # HAPADパッド専用の追加リンク処理
                        if banner_val == "HAPAD パッド":
                            df_export.loc[i, "additional3"] = '<A HREF="https://store.shopping.yahoo.co.jp/solltd/grease-001.html" TARGET="new"><IMG SRC="https://shopping.c.yimg.jp/lib/solltd/to_grease.jpg"></a>'
                            df_export.loc[i, "sp-additional"] = str(df_export.loc[i, "sp-additional"]) + '<A HREF="https://store.shopping.yahoo.co.jp/solltd/grease-001.html" TARGET="new"><IMG SRC="https://shopping.c.yimg.jp/lib/solltd/to_grease.jpg" style="width: 100%;"><BR></A><br><br>'
                        
                        # additional2 と sp-additional の末尾に保証リンクを追加
                        df_export.loc[i, "additional2"] = guarantee_link_block
                        df_export.loc[i, "sp-additional"] = str(df_export.loc[i, "sp-additional"]) + guarantee_link_block
                        
                        shipping_map = {"770": 0, "1100": 100, "1650": 1, "3850": 1000, "特大A": 5000, "特大B": 50000, "特大C": 10000, "特大D": 1000000}
                        df_export.loc[i, "ship-weight"] = shipping_map.get(shipping_val, "")
                        postage_set_map = {"770": 1, "1100": 1, "1650": 1, "3850": 1, "特大A": 7, "特大B": 5, "特大C": 4, "特大D": 2}
                        df_export.loc[i, "postage-set"] = postage_set_map.get(shipping_val, "")
                        df_export.loc[i, "taxable"] = "1"
                        df_export.loc[i, "brand-code"] = BRAND_CODE_MAPPING.get(maker, "")
                        df_export.loc[i, "condition"] = "2"
                        df_export.loc[i, "delivery"] = "0"
                        # ===== ここから復旧・追加ロジック =====
                        
                        # Q列（meta-desc）: nameと同じ値を代入
                        df_export.loc[i, "meta-desc"] = df_export.loc[i, "name"]
                        
                        # AA列（product-category）: 品名から辞書マッチング（文字数降順）、見つからなければ14024
                        prod_name_raw = str(data.get("品名", title_words[0] if title_words else "")).strip()
                        matched_cat = "14024"
                        for key, val in CATEGORY_MAPPING.items():
                            if key in prod_name_raw:
                                matched_cat = val
                                break
                        df_export.loc[i, "product-category"] = matched_cat
                        
                        # 固定値群の代入
                        df_export.loc[i, "display"] = "1"                     # AB列
                        df_export.loc[i, "lead-time-instock"] = "1000"        # AD列
                        df_export.loc[i, "lead-time-outstock"] = "3"          # AE列
                        df_export.loc[i, "keep-stock"] = "1"                  # AF列
                        df_export.loc[i, "taxrate-type"] = "0.1"              # AH列
                        df_export.loc[i, "auc-pref-code"] = "12"              # AL列
                        
                        # AI列（auc-bcid）: 大元の管理番号
                        base_bcid = str(master_row.get("管理番号", "")).strip()
                        df_export.loc[i, "auc-bcid"] = base_bcid
                        
                        # AJ列（auc-category）: 優先順位：適合車種 > マスタ/その他
                        auc_cat_final = str(data.get("ヤフオクカテゴリ", "")).strip()
                        if not auc_cat_final:
                            # 最終バックアップ：マスタシートの値を直接確認
                            auc_cat_final = str(master_row.get("ヤフオクカテゴリ", "")).strip()
                        df_export.loc[i, "auc-category"] = auc_cat_final
                        
                        # AK列（auc-store-keyword）: 管理番号 メーカー名 品名 (バイト数制限付き)
                        base_part_name = title_words[0] if title_words else ""
                        keyword_full = f"{base_bcid} {maker} {base_part_name}".strip()
                        if get_lenb_half(keyword_full) <= 20.0:  # LENB/2が20以内（=40バイト以内）
                            df_export.loc[i, "auc-store-keyword"] = keyword_full
                        else:
                            # オーバーする場合はメーカー名を外す
                            df_export.loc[i, "auc-store-keyword"] = f"{base_bcid} {base_part_name}".strip()
                        
                        # AY列（item-image-urls）: ブランドごとの画像URL割り当て
                        orig_brand = str(data.get("ブランド", "")).strip()
                        if banner_val == "プレミアムHAPAD パッド":
                            base_urls = ";;;;;;https://shopping.c.yimg.jp/lib/solltd/sub_prhapadA.jpg;https://shopping.c.yimg.jp/lib/solltd/sub_prhapadB.jpg;https://shopping.c.yimg.jp/lib/solltd/sub_prhapadC.jpg;https://shopping.c.yimg.jp/lib/solltd/notes2.jpg;;;;;;https://shopping.c.yimg.jp/lib/solltd/notesiso.jpg;;;;;https://shopping.c.yimg.jp/lib/solltd/ys1_kanban_1200.jpg"
                        elif orig_brand in ["HAPAD", "CAPSOL", "社外品"]:
                            base_urls = ";;;;;;;;;https://shopping.c.yimg.jp/lib/solltd/notes2.jpg;;;;;;https://shopping.c.yimg.jp/lib/solltd/notesiso.jpg;;;;;https://shopping.c.yimg.jp/lib/solltd/ys1_kanban_1200.jpg"
                        else:
                            base_urls = ";;;;;;;;;https://shopping.c.yimg.jp/lib/solltd/notes2.jpg;;;;;;;;;;;https://shopping.c.yimg.jp/lib/solltd/ys1_kanban_1200.jpg"
                        
                        # F列「適合確認可否」が「不可」の場合の専用差し替え処理（K列、AC列、AY列）
                        is_fit_check_impossible = str(data.get("適合確認可否", "")).strip() == "不可"
                        
                        # 用品または特大の画像差し替え処理
                        if is_oversize:
                            # 特大の場合
                            base_urls = base_urls.replace("notes2.jpg", "notes.jpg")
                            df_export.loc[i, "additional1"] = str(df_export.loc[i, "additional1"]).replace("parts01.gif", "supplies02.gif")
                            df_export.loc[i, "sp-additional"] = str(df_export.loc[i, "sp-additional"]).replace("parts01.gif", "supplies02.gif")
                        elif item_type == "用品":
                            # 用品（かつ特大ではない）の場合
                            base_urls = base_urls.replace("notes2.jpg", "notes4.jpg")
                            df_export.loc[i, "additional1"] = str(df_export.loc[i, "additional1"]).replace("parts01.gif", "supplies01.gif")
                            df_export.loc[i, "sp-additional"] = str(df_export.loc[i, "sp-additional"]).replace("parts01.gif", "supplies01.gif")
                            
                        # 不可の場合の差し替え
                        if is_fit_check_impossible:
                            base_urls = base_urls.replace("notes2.jpg", "notes4.jpg")
                            df_export.loc[i, "additional1"] = str(df_export.loc[i, "additional1"]).replace("parts01.gif", "parts010.gif")
                            df_export.loc[i, "sp-additional"] = str(df_export.loc[i, "sp-additional"]).replace("parts01.gif", "parts010.gif")
                            
                            target_text = "※適合にご不安がある場合、ご注文前に車体番号をご連絡頂ければ当店にてお調べ致します。"
                            replace_text = "※こちらの商品は当社側で適合確認ができないメーカーの為、メーカー品番又は純正品番のご確認をお願い致します。"
                            df_export.loc[i, "explanation"] = str(df_export.loc[i, "explanation"]).replace(target_text, replace_text)
                            df_export.loc[i, "additional1"] = str(df_export.loc[i, "additional1"]).replace(target_text, replace_text)
                            df_export.loc[i, "sp-additional"] = str(df_export.loc[i, "sp-additional"]).replace(target_text, replace_text)
                            
                        df_export.loc[i, "item-image-urls"] = base_urls
                        
                        # 最終仕上げ：J列（explanation）のHTMLタグ除去
                        df_export.loc[i, "explanation"] = re.sub(r'<[^>]+>', '', str(df_export.loc[i, "explanation"]))

                        # ===== 復旧・追加ロジックここまで =====

                    st.success("全データのマッピングが完了しました。")
                    csv_buffer = io.StringIO()
                    df_export.to_csv(csv_buffer, index=False, lineterminator='\r\n')
                    csv_data = csv_buffer.getvalue().encode('cp932', errors='replace')
                    st.download_button(label="CSVをダウンロード", data=csv_data, file_name=f"yahoo_items_{base_id}.csv", mime="text/csv")
            
            st.divider()
            st.info("※マスタシートの1行目を全車種に展開します。")
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

def main():
    st.set_page_config(page_title="AutoPage Generator", layout="wide")
    st.markdown("""<style>div.stButton > button[kind="primary"] { background-color: #ff4b4b; color: white; border: none; width: 100%; height: 3em; font-weight: bold; }</style>""", unsafe_allow_html=True)
    st.sidebar.title("🛠️ メニュー")
    app_mode = st.sidebar.radio("機能を選択してください", ["SEO・商品説明生成", "マスターページメーカー"])
    
    if app_mode == "SEO・商品説明生成":
        show_seo_generator()
    else:
        show_template_expansion()

if __name__ == "__main__":
    main()
