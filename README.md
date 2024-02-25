# variabrain
変数を持つbrainfuckスーパーセット(の予定)  

私が作ったbrainfuckインタプリンタの拡張として作りました  
https://github.com/35enidoi/honi-programs/tree/main/honis/brainfuck

import時のvariabrainの引数は元のリポジトリのreadmeを見てください。
# 特徴
変数を持つことができます。  
(要はマクロです。)  

brainfuckとの違いはそれだけです。
# コード例
## AからZまで出力するコード
```bf
A(++++++++)A[>A<-]AAA++[>+.<-]
```
## Hello World!
```bf
A(++++++++++)>A[>A--->A>A+>A+>A+>+++>A->A+>A+>A+>A>+++>+[<]>-]
>++>+>-->-->+>++>--->+>++++>-->>+++
[<]>[.>]
```