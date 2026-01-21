# Gomoku
# Motivation
>在當兵的時候實在是太無聊，每天都在跟鄰兵在格子筆記本上面用鉛筆玩五子棋，當時就想著等退伍後找時間寫一個五子棋的對弈程式，順便當作練練手與復健的小玩具
# Run code
* 執行local gui
```
python -m ui.local_gui
```
* 實際執行效果
![Gomoku Local Demo](/figures/local_gui_demo.gif)
# Codes
```text
gomoku/
├── core/
│   └── board.py        # Game board definition
│   └── game.py         # Game logic
│   └── rule.py         # Win or lose
│
├── players/
|   └── random.py       # A program that paly with random strategy
│
├── ui/
│   └── local_gui.py    # Pygame local gui
|
└── README.md
```

# 心得
> 想說順手試試看AI的寫程式能力(Vibe coding)，結果效果超好= = \
如果是我來寫的話，估計一個下午才剛刻出一個prototype \
讚嘆AI，感恩AI (´-ω-)b
