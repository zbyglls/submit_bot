"""违禁词配置"""

FORBIDDEN_WORDS = {
    "违法内容": [
        "毒品", "走私", "犯罪", "非法", 
        "假证", "伪造", "诈骗"
    ],
    
    "违规内容": [
        "黄赌毒", "赌博", "情色",
        "色情", "淫秽", "援交"
    ],
    
    "敏感词": [
        "私密", "约炮", "一夜情",
        "包养", "小姐", "特殊服务"
    ]
}

# 展平所有违禁词
ALL_FORBIDDEN_WORDS = []
for category in FORBIDDEN_WORDS.values():
    ALL_FORBIDDEN_WORDS.extend(category)