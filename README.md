# Azure FaceAPIを使用したLineBOT 

Line チャンネルに送られた写真が TK(友人)か判定する  
写真の表情を読み取り感情分布を出力する

チャンネル：https://lin.ee/VXHTd9K

## 使用技術

- Line API
- Azure(FaceAPI)
- Python
- jupyter Notebook
- Flask

## 概要

- Line の公式チャンネルを作成
- Python を使用し Azure の FaceAPI に友人の顔写真を学習させる
- FaceAPI サーバと Line 公式チャンネルを繋ぐ 中継(Webhook)サーバを作成する
- 中継サーバの処理は Python で作成し、FaceAPI に対するリクエスト、レスポンスを処理し Line チャンネルに返す
<img width="705" alt="image" src="https://github.com/naitoyuma7110/Line-FaceAI/assets/128150297/431a306f-afd6-4065-9137-857fd69e5950">
