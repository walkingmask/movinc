# MovInc: Does the target movie include the original movie?
ある動画（ターゲット動画）に、ある動画（オリジナル動画）が含まれているか確認する Python スクリプト。

含まれているか否かを閾値を設定して求めるモードと、含まれているであろう度合いを数値で求めるモードがある。


## Requirements
- opencv-python
- ImageHash


## Usage
```
git clone https://github.com/walkingmask/movinc.git
cd movinc
python movinc.py /path/to/origin.mov /path/to/target.mov
```


## How its works
- OpenCV で動画フレームを切り出し
- Perceptual Hash を利用して動画フレームをハッシュ化

上記２点を用いて、

1. オリジナル動画の始点終点およびランダムに選んだ中間N点をハッシュ化
    - `-p 100` で指定可能
1. ターゲット動画の全フレームをハッシュ化
1. オリジナル動画のハッシュとターゲット動画のハッシュのハミング距離を求め、最も小さいものを線形探索
    - この時、オリジナル動画のハッシュ`i`とターゲット動画のハッシュ`j`をペアとして用いた場合、`i+1`のペアは`k(k<j)`となる
    - つまり時系列を加味する
1. 求めたハミング距離を配列として保存
1. 求めたハミング距離配列の平均を求める
1. (64 - 平均)/64 をスコアとする
    - ハミング距離の最大値が 64 なので
    - スコアの範囲は 0.0 ~ 1.0 (確率ではくスコア)


## Mode
- `-r b` を指定すると、スコアではなく、オリジナル動画がターゲット動画に含まれていると判断した場合は 1、そうでない場合は 0 を返す
    - `-t 5` のように閾値（同じフレームと判断するハミング距離）を設定可能
- デフォルトは `-r p`


## Example
以下の二つの動画に対してスコアを求める。

- https://www.youtube.com/watch?v=aSUcCc7hgmI
- https://www.youtube.com/watch?v=5g2-7ZzDhjg

```
$ python ./movinc.py ./aSUcCc7hgmI.mp4 ./5g2-7ZzDhjg.mp4 
0.39583333333333337
```

ちなみに、同一の動画に仕様した場合は

```
$ python ./movinc.py ./aSUcCc7hgmI.mp4 ./aSUcCc7hgmI.mp4
1.0
```

となる。


## Tips
- OpenCV による動画の読み込みに最も時間がかかるので、
    - 同一動画を使う場合は、あらかじめ Perceptual Hash を求めたものを保存しておいた方が良い
    - N点の数はパフォーマンスに大きな影響はない

