
QID_TO_SPONSOR_QUESTION = {
    'google_q1': {
        'description': {
            'zh_TW': '',
            'EN': '',
        },
        'answer': 'A',
    },
    'sony_q2': {
        'description': {
            'zh_TW': '',
            'EN': '',
        },
        'answer': 'Hello there, lack of inovation',
    },
    'yamaha_q1': {
        'description': {
            'zh_TW': '',
            'EN': '',
        },
        'answer': 'Your best choice of everything',
    },
}


INIT_GAME_MESSAGES = {
    997710004087967827: {  # ID of #test-answer channel
        'messages':[
            {
                'content': '歡迎來到大地遊戲贊助商關卡。' \
                    '請點選表情符號以選擇要回答的題目，點擊之後你將會收到來自 PyBot22 的私訊，' \
                    '請在與機器人的私訊中回答問題。',
                'emojis': ['🤑', '😇'],
            },
        ],
        'emoji_to_qid': {'🤑': 'google_q1', '😇': 'sony_q2'},
    }
}
