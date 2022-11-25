# Stable-Diffusion-Webui-Client

## 概要
### callapi_txt2image.py
- ローカルに立てたautomatic1111/stable_diffution_webuiのWebAPIのtext2imageを使用し、画像をツイートする
- cronを使用して例えば1時間に一度ツイートする
```
0 * * * * path/to/dir/callapi_txt2image.py > sd.log 2>&1 &
```

```mermaid
sequenceDiagram
  autonumber
  participant P as LocalPC
  participant S as StableDiffusionWebUI
  participant T as Twitter
  
  P-->>P: 日時を取得し、プロンプトを編集

  P-)S: http://127.0.0.1:7860/sdapi/v1/txt2img
  Note left of S: 現在の設定だと大体5分以上かかる 
  S--)P: Image as Base64String

  P-->>P: 画像保存
  Note right of P: ディスクに保存

  P-)T: 画像付きツイート
  T--)P: {'data': {'id': 'xxx', 'text': 'yyy https://zzz'}}
```


