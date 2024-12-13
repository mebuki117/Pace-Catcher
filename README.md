## 説明
[Simple MultiView Controller](https://github.com/mebuki117/Simple-MultiView-Controller)、[PaceMan](https://paceman.gg/)と併用して使うスクリプト。  
併用することで、自動的な走者の入れ替え、シーン切り替えが可能になる。

使用には、`allpaces.txt`を、Simple MultiView Controllerの`data`フォルダに作成する。  

`allpaces.txt`にはPBペースを、`MCID : FS/SS/Blind/SH/End/PB`を行ごとに記述する。  
なお、`FS`は使用していないため、`1`にする。
```
player1 : 1/5/6/8/9/10:00
test_player : 1/6:30/8/9/9:30/10:30
minecrafter : 1/6/8/10/11/11:30
```
