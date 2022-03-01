consumer_key = ""
consumer_secret = ""
access_token_key = ""
access_token_secret = ""
proxy = None    # 代理设置 当你的服务器需要使用代理访问Twitter时设置

follows = {
    "twitter-stream-test": ["Ice9Coffee"],
    "kc-twitter": ["KanColle_STAFF", "C2_STAFF", "ywwuyi", "FlatIsNice"],
    "pcr-twitter": ["priconne_redive", "priconne_anime"],
    "uma-twitter": ["uma_musu", "uma_musu_anime"],
    "pripri-twitter": ["pripri_anime"],
    "coffee-favorite-twitter": ["shiratamacaron", "k_yuizaki", "suzukitoto0323", "usagicandy_taku", "usagi_takumichi"],
    "depress-artist-twitter": ["tkmiz"],
    "moe-artist-twitter": [
        "koma_momozu", "santamatsuri", "panno_mimi", "suimya", "Anmi_", "mamgon",
        "kazukiadumi", "Setmen_uU", "bakuPA", "kantoku_5th", "done_kanda", "hoshi_u3",
        "siragagaga", "fuzichoco", "miyu_miyasaka", "naco_miyasaka", "tsukimi08",
        "tsubakininiwawa", "_Dan_ball", "ominaeshin", "gomalio_y", "izumiyuhina",
        "1kurusk", "amsrntk3", "kani_biimu", "Nakkar7", "li_hongbo", "nahaki_401",
        "ukiukisoda", "yukkieeeeeen", "t_takahashi0830", "riko0202", "enoki_art",
        "Zoirun", "rulu_py", "zo3mie",
    ],
}

media_only_users = [
    *follows["moe-artist-twitter"],
    *follows["depress-artist-twitter"],
]

forward_retweet_users = []

uma_ura9_black_list = [
    'YaibA_No9', 'ReToken',
]
