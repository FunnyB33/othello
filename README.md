``` text
othello/
├── app/
│   ├── __init__.py
│   ├── routes.py          ← 画面遷移とマッチ処理
│   ├── game.py            ← オセロロジック処理
│   ├── socketio_events.py ← WebSocket用イベント管理
│   └── templates/
│       ├── index.html     ← 合言葉入力
│       └── game.html      ← ゲーム画面（ログ右側）
│   └── static/
│       ├── css/
│       └── js/
│           └── game.js    ← JSでWebSocket通信・盤面描画
├── run.py                 ← アプリ起動用
├── requirements.txt
└── README.md

```

[ChatGPT](https://chatgpt.com/share/67ff37dc-66b0-800e-aabd-99c3d58fa7bc)