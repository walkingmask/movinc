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
`./movies` にサンプル動画（ＮＨＫクリエイティブ･ライブラリーのものを使用、詳細は[こちら](./movies/README.md)）があるので、それに対するスコアを出してみる。

各動画は、次のようなものになっている。

- mov1.mp4: アオショウビンの動画
- mov2.mp4: インドクジャクの動画
- mov3.mp4: mov2.mp4 を分割したものを mov1.mp4 の前後に合成した動画

```
$ python movinc.py movies/mov1.mp4 movies/mov1.mp4
1.0
$ python movinc.py movies/mov1.mp4 movies/mov2.mp4
0.6315104166666667
$ python movinc.py movies/mov1.mp4 movies/mov3.mp4
0.9986979166666666
$ python movinc.py movies/mov2.mp4 movies/mov1.mp4
0.58203125
$ python movinc.py movies/mov2.mp4 movies/mov2.mp4
1.0
$ python movinc.py movies/mov2.mp4 movies/mov3.mp4
0.9908854166666666
$ python ./movinc.py movies/mov3.mp4 movies/mov1.mp4
0.42838541666666663
$ python ./movinc.py movies/mov3.mp4 movies/mov2.mp4
0.8489583333333334
$ python ./movinc.py movies/mov3.mp4 movies/mov3.mp4
1.0
```

当然だが、同じ動画に対しては 1.0 が出力される。mov1,、mov2 をオリジナル動画に、mov3 をターゲット動画にすると高いスコアが出力される。mov3 をオリジナル動画にすると、mov1 に対しては低いスコアが出力される。ただし、mov2 に対しては 0.84 と比較的高いスコアが出力される。これはあまり望ましくないので、ランダムN点を 100 に変更して実行する。

```
$ python ./movinc.py movies/mov1.mp4 movies/mov1.mp4 -p 100
1.0
$ python ./movinc.py movies/mov1.mp4 movies/mov2.mp4 -p 100
0.1271446078431373
$ python ./movinc.py movies/mov1.mp4 movies/mov3.mp4 -p 100
0.9973958333333334
$ python ./movinc.py movies/mov2.mp4 movies/mov1.mp4 -p 100
0.13541666666666663
$ python ./movinc.py movies/mov2.mp4 movies/mov2.mp4 -p 100
1.0
$ python ./movinc.py movies/mov2.mp4 movies/mov3.mp4 -p 100
0.9905024509803921
$ python ./movinc.py movies/mov3.mp4 movies/mov1.mp4 -p 100
0.12974877450980393
$ python ./movinc.py movies/mov3.mp4 movies/mov2.mp4 -p 100
0.7622549019607843
$ python ./movinc.py movies/mov3.mp4 movies/mov3.mp4 -p 100
1.0
```

精度が上がっていることがわかる。


## Tips
- OpenCV による動画の読み込みに最も時間がかかるので、
    - 同一動画を使う場合は、あらかじめ Perceptual Hash を求めたものを保存しておいた方が良い
    - N点の数はパフォーマンスに大きな影響はない
- mov3 が mov2 との類似度が高いのは、実装上ランダムN点が前方に偏りがちなことが原因な可能性がある。ランダム点をより分散するように実装すると良いかも
