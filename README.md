
# データサイエンスにおける可読性と再現性

version 1.5, Written by rnagumo, 26-July-2020

# 目的

データ分析の実務でありがちなトラブルとして，

* 他人の書いた特徴量エンジニアリングのコードが何をしているのか理解できない．
* 以前に報告した予測性能が再現できない．
* スパゲッティコードのせいで，特徴量の追加などの拡張ができない．
* Jupyter notebookで書かれたコードを特定の順番で実行しないと意図した結果が出ない．

といったことが挙げられる．

そのようなトラブルを避けるためには，可読性と再現性を上げることが一つの手段である．しかし，そのノウハウは教科書になっておらず，またネット上でも情報が散乱している状況である．そこで，筆者のベストプラクティスをできるだけ体系的にまとめてここに記す．

想定読者は，データ分析のチュートリアルを最後まで進めることはできるが，実務では上述のような問題に突き当たっている技術者，分析者である．一例として，Kaggleの[titanic tutorial](https://www.kaggle.com/startupsci/titanic-data-science-solutions)を最後まで経験していることを想定している．

# 目次

可読性と再現性を高めるためのフォルダ構成やコーディング手法，細かいが重要なテクニックなどを述べる．この資料は以下の順序で述べられており，データ分析プロジェクトではこの順番で進めるのが良いと思われる．

1. 整然としたフォルダを構成する
2. 可読性の高いプログラムを書く
3. 実験の再現性を担保する
4. 信頼できるベースラインを作る
5. モデルや特徴量を作りこむ
6. Pythonパッケージを作る

# 1. 整然としたフォルダを構成する

## 1.1 プロジェクト全体の構成

一般的なデータサイエンスプロジェクトでは，様々な実験（特徴量の追加・削除，モデルの変更，データの追加など）をすることが多い．このとき，フォルダ構成にまとまりが無いと，コードや分析結果が乱雑になってしまい実験の再現性の低下に繋がるので望ましくない．そこで，フォルダ構成をキチンと決めることでデータや実験結果が失われてしまわないようにしたい．一例として，以下のフォルダ構成を提案する．

＜ポイント＞  

* データとコードは別のフォルダに入れる．これはgitでのバージョン管理のためにも必須である．
* データフォルダの中身を役割に応じて分割する．
* 特徴量の分析はnotes，モデルの学習結果はlogsなど，役割毎にフォルダを分割する．
* packageに基本的なクラスを実装して，それらをスクリプトで呼び出す．

```none
package  
│  
├── README.md          <- パッケージ全体のREADME文書
├── setup.py           <- PythonパッケージのSetup tools  
│  
├── data  
│   ├── external       <- 入力以外の役に立つデータ
│   ├── input          <- 生の，変更不可なデータ（データベースからとってきたデータなど）
│   ├── output         <- 機械学習に入れる直前のデータ
│   └── working        <- 特徴量エンジニアリングなどの中間ファイル
│  
├── logs               <- 実験結果を保存するためのフォルダ
│  
├── notes              <- 特徴量分析や，モデル予測の可視化のためのJupyter notebook
│  
├── package            <- システムで動かすためのPythonパッケージ
│   ├── dataset        <- APIやDBからデータをとってくる
│   ├── model          <- 機械学習モデル
│   ├── preprocessing  <- 生データを特徴量エンジニアリングしてテーブルを作る
│   └── train          <- データを使ってモデルを学習させる
│  
└── src                <- スクリプトコード，自作パッケージなどを動かすコードを含む
```

## 1.2 Gitによるバージョン管理

プロジェクトを進める際には，[Git](https://git-scm.com/)などを使ってバージョン管理をすることが必須である．例えば，昔の仕様に戻したい，複数人で開発するときに他人の変更を自分のプログラムに追加したい，といった要求はバージョン管理システムによって叶えられる．ルートディレクトリを作成したらまずはgitを初期化して，それからファイル・フォルダの追加をすると良い．Gitの詳しい説明は「[Pro Git book](https://git-scm.com/book/ja/v2)」にある．また，Gitの運用方法に関しては「[A successful Git branching model](https://nvie.com/posts/a-successful-git-branching-model/)」が参考になる．

## 1.3 スクリプト，jupyter，パッケージの使い分け

上述のフォルダには，pythonの処理プログラムとしてスクリプト(src/)，jupyter(notes/)，パッケージ(package/)の3種類が含まれている．これらの使い分けは分析者によって異なるので，絶対的な方法はない．一般論として，いきなりパッケージを実装するのは労力ばかりが先行するので，まずはjupyterなどで分析を進めた方がよいと言われている．ある程度処理が固まってきた段階でパッケージ化すると，可読性や再現性が担保しやすくなる．

個人的なベストプラクティスを以下に述べる．

* 特徴量生成部分は，jupyter notebookで実装する．理由は，特徴量エンジニアリングはデータの中身を見ながら実装することが多いので，インタラクティブツールであるjupyterと相性が良いからである．特徴量毎や分析日別にjupyterのファイルを分割し，特徴量は個別にcsvファイルとしてdata/working/内に保存する．

* モデル学習部分は，早い段階でスクリプトを書いてしまう．理由は，モデル学習ではjupyterのようなインタラクティブなインターフェースを必要としないからである．パイプライン処理やvalidationなどをキチンと実装すると同時に，後述のconfigやloggerを用意することで確実に実験が再現できる環境を早めに構築する．

* 分析業務の最終段階で，特徴量生成とモデル学習をパッケージ化する．特に，特徴量生成のjupyterを一つにまとめる作業は，システム実装では必須である．ある処理で生み出された中間ファイルを別の処理が使うといった依存関係も明らかになるので，特徴量生成部分は丁寧に実装したい．

# 2. 可読性の高いプログラムを書く

フォルダ構成ができたのならば，実際にコードを書いていく．

## 2.1 コーディング規則に従ったコードを書く

Pythonには，美しいPythonicなコードを書くためのコーディング規則PEP 8（[英語](https://www.python.org/dev/peps/pep-0008/)，[日本語](https://pep8-ja.readthedocs.io/ja/latest/)）が定められている．他にも，各企業が自社のプロダクトに対して追加のルールを定めている場合がある，例えば，Googleでは[Google Python Style Guide](https://github.com/google/styleguide/blob/gh-pages/pyguide.md)を定めて，自社のコードの書き方が統一されるように配慮している．「一貫性にこだわりすぎるのは、狭い心の現れである」ものの，コードを書く人と読む人が同じ思想を共有することが大切である．

ただし，コーディング規則の中でも一行あたりの文字数は柔軟に決めて良い．PEP8 は，[最大文字数を80字と定めている](https://www.python.org/dev/peps/pep-0008/#maximum-line-length)．しかし最近では，1. 80字では一行が短くなりすぎてコードが読みにくくなる，2. 高解像度，高性能のエディタが普及しているので技術的には文字数制限がない，といった理由から，文字数制限を見直す動きもある．例えば，Webフレームワークとして有名なDjangoというプロジェクトは，[文字数制限を120字としている](https://code.djangoproject.com/ticket/23395#no2)．これは，GitHubが一度に表示できる文字数が120字であるため，コードレビューのしやすさのためにその制限を設けているのである．また，PyCharmというIDEも[文字数制限を120字としている](https://stackoverflow.com/questions/17319422/how-do-i-set-the-maximum-line-length-in-pycharm)．以上の背景より，文字数を80字から100字もしくは120字に変更しても良いと考える．また，その場合にはエディタの設定を変更すると文字数制限でエラーが出なくなる．

PyCharmなどのIDEや，VSCodeのようなエディタはPEP 8のチェック機能を備えることが多い．例えば，筆者は以下のようにVSCodeのリンターを設定している．pylint，flake8は共にPythonのリンターであるが，flake8の方が高機能であるために，pylintをオフにしてflake8をオンにしている．これらの項目は，設定画面から検索すれば変更可能である．

```json
"python.linting.pylintEnabled": false
"python.linting.flake8Enabled": true
```

## 2.2 予約語を再定義しない

Pythonに疎い人がやりがちなミスとして，Pythonの予約語を新たに定義し直してしまうことが挙げられる．機械学習・データ分析分野で最も頻繁に見かける再定義のミスは，input及びidを置き換えることだ．

inputは，例えば「処理の入力と出力」という意味で「input/output」の対で使われる場面がある．しかし，[input()](https://docs.python.org/ja/3/library/functions.html#input)は標準入力から1行を読み込むための組み込み関数である．一方で，outputは予約語ではないので問題ない．よって，例えばinputにsuffixをつけることで衝突を回避できる．

ただし，`input`に関してはそこまで神経質にならなくとも良いのかもしれないとも筆者は考える．第一に，`input()`は標準入力からの読み込みを担当する関数であるが，実際に使用される場面は少ない．第二に，有名なライブラリのサンプルコードでも`input`を再定義している場面をよく見かける．以上より，ここまで神経質に`input`を使わないようにすることは「狭い心の現れである」のかもしれない．

```python
# Bad
def func(input):
    output = some_process(input)
    return output

# Good: input_, inputsなどで命名を区別する
def func(inputs):
    output = some_process(inputs)
    return output
```

idは，データ中の人の固有番号という意味で使われることが多い．しかし，[id()](https://docs.python.org/ja/3/library/functions.html#id)はオブジェクトの識別子を返す組み込み関数である．従って，idではなくuser_idとするなど，衝突を回避するための工夫が必要である．

## 2.3 ライブラリの思想に従う

ライブラリの設計思想に則ったコードを書くと，処理スピードが速く，他人にも読みやすいプログラムが完成することが多い．例えば，numpyとpandasは配列の向きが異なる．numpyは行単位でデータを保持するのに対し，pandasは列単位でデータを保持する．この背景には，pandasがデータベースを参考にしているという思想があると筆者は考えている．従って，行単位の数値計算がしたい場合にはnumpyを使い，列単位の特徴量エンジニアリングがしたい場合にはpandasを使うのが効率が良いことが推察される．

このように，各ライブラリの思想に沿ったコードを書くと，読み易く処理速度の速いプログラムができると思われる．

## 2.4 クラス・関数は適切に分割する

データ分析では，定石となる処理手順がおよそ決まっている．例えば，

* 各種の特徴量エンジニアリング
* 全特徴量を一つのデータセットに結合
* 交差検証のためにtrain-validation split
* trainを使ったモデル学習
* validationデータによる精度検証

といった流れである．従って，各処理で関数，クラス，コードを分けることで読みやすいコードになる．また，それはデータリークの防止にも繋がる．

クラスや関数の命名は，名前から処理の中身が推測できるようにした方が可読性は上がる．例えば，何かの処理をした後にその結果をcsvファイルに保存する関数の名前はsome_process_to_csv()のようにするなど，名前から中身が推測できると良い．また，pandasやscikit-learnなどの既存のクラス・関数に似せた命名規則にすると，よりわかりやすい．

## 2.5 docstringやコメントを書く

数か月前の自分は他人であるという俗説に従い，自分や他人のためにコードの説明をdocstringやコメントの形で残すべきである．特に，複雑な数値計算や特徴量エンジニアリングにおいては，実際のプログラムの処理がどのような意図を持っているかを自然言語で記述すべきである．たとえ自分の書いたコードであっても，あとからコードを見たらわからないことが多いというのが筆者の経験談である．

docstringはクラスや関数の先頭に書かれている文章である．docstringの書き方には[Google styleとNumpy Style](http://www.sphinx-doc.org/ja/stable/ext/napoleon.html)があり，どちらを選択してもよい．

# 3. 実験の再現性を担保する

データ分析プロジェクトで最も問題になるのが，調整すべき設定・パラメータが多く存在するためにどの条件でどの結果が出たのかの対応が取れなくなる点だ．この対応が取れなくなると実験の再現性が損なわれるので，設定や結果を管理する必要がある．ここでは，そのような再現性を担保するためのテクニックを述べる．

## 3.1 loggerを使う

最も重要なことは，全ての設定や実験結果をまとめて保存することである．そのためには，Pythonの標準ライブラリに含まれる[logging](https://docs.python.org/ja/3/howto/logging.html)を使うと良い．loggerを適切に設定することで，ファイルとターミナルの両方に同じ内容を吐き出すことができるので，実験の最中に結果を見ながら，同時にその内容をファイルに残すことができる．普段コーディングをする際にはデバッグや途中経過を見るためにprint文を使うことが多いと思われるが，print文ではターミナルで情報を見ることができてもファイルに情報が残らないので推奨されない．

例えば，以下のようなコードでロガーを作ることができる．

```python sample.py
import logging
import pathlib
import time

def init_logger(logdir):
    # Check logdir
    logdir = pathlib.Path(logdir)
    logdir.mkdir(parents=True, exist_ok=True)

    # Log file
    logfn = "training_{}.log".format(time.strftime("%Y%m%d"))
    logpath = logdir / logfn

    # Initialize logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Set stream handler (console)
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    sh_fmt = logging.Formatter(
        "%(asctime)s - %(module)s.%(funcName)s - %(levelname)s : %(message)s")
    sh.setFormatter(sh_fmt)
    logger.addHandler(sh)

    # Set file handler (log file)
    fh = logging.FileHandler(filename=logpath)
    fh.setLevel(logging.INFO)
    fh_fmt = logging.Formatter(
        "%(asctime)s - %(module)s.%(funcName)s - %(levelname)s : %(message)s")
    fh.setFormatter(fh_fmt)
    logger.addHandler(fh)

    return logger
```

例えば，ある値をロガーに記すにはinfo()を使うとよい．

```python
x = 0
logger.info(f"Some value = {x}")
```

## 3.2 configファイルに設定を保存する

機械学習の実験においては様々な設定（特徴量の選択，hyper-parameterの選択）があるので，これらを全てファイルに保存することで再現性を担保したい．そのために，例えばconfig.jsonというファイルを作って，その中に[json形式](https://docs.python.org/ja/3/library/json.html)で全ての設定を保存する方法がある．jsonファイルを読み込むとpythonではdict型オブジェクトとして扱えるようになるので，キーを指定することでそれぞれの設定を反映させることができる．また，一度読み込まれたconfigは指定されたlogsフォルダに実験結果と一緒に保存されるようにすれば，後からそのconfig.jsonファイルを読み込むと実験環境が再現できるようになる．

例えば，config.jsonの中身は以下のように書ける．

```json config.json
{
    "param1": 1,
    "param2": 0.2
}
```

このjsonファイルをPythonコードで読み込み，logdirフォルダにそのまま保存する．

```python sample.py
import json
import pathlib

# jsonファイルを読み込む
def load_config(path):
    with pathlib.Path(path).open() as f:
        config = json.load(f)
    return config


# logdirフォルダにconfigを保存する
def save_config(logdir, config):
    with pathlib.Path(logdir, "config.json").open("w") as f:
        json.dump(config, f)
```

## 3.3 argparseでコマンドライン引数を指定する

もう一つの実験条件の指定方法は，[argparse](https://docs.python.org/ja/3/library/argparse.html)を使ってコマンドライン引数を受け取る方法である．上述のconfigファイルではいちいちファイルを変更しないといけないのに対し，コマンドライン引数ではスクリプトの実行時に手軽に条件を変更できる．ただし，コマンドライン引数の情報は残らないので，loggerに全ての値を出力させるなどの処理をした方がよい．

なお，コマンドラインオプションは「機能をオンにする」 フラグを書き，「機能をオフにする」フラグは書かない．これは，まずベースラインとなる最も単純な処理を書いて，そこにオブションを足していくという考え方をとるからである（参考：[情報系研究者のための研究ノート](https://qiita.com/guicho271828/items/9307ae12248329b71f12)）．

例えば，以下のようにargparseを書く．

```python sample.py
import argparse

def init_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--logdir", type=str, default="../logs/tmp/",
                        help="Log directory")
    parser.add_argument("--config-path", type=str, default="./config.json",
                        help="Path to config json file")
    parser.add_argument("--data-path", type=str,
                        default="../data/output/tmp.csv",
                        help="Path to dataset for ML")
    parser.add_argument("--flag", action="store_true",
                        help="Some flag (default=False)")
    parser.add_argument("--value", type=int, default=0,
                        help="Some value")
    return parser.parse_args()
```

## 3.4 実験結果を保存する

再現性とはあとから実験を再現できることを指すので，そのために必要な情報は全て保存すべきである．例えば，使用したハイパーパラメータ，前処理，特徴量などは全てログファイルやconfigファイルに残した方が良い．また，訓練されたモデルも保存すべきである．できればデータも残したいところだが，データサイズが大きい場合にはPCのストレージを圧迫するので必須ではない．

実験条件の変更は全てconfigかargparseで行うべきであり，コメントアウトやハードコーディングによる条件設定は推奨されない．それらはログに残らない情報であることが多く，手軽に変更することもできないので，再現性を損なうことにつながるからである．

## 3.5 詳細な報告は別ファイルで行う

コードをできるだけシンプルに保つために，モデルの学習プログラムにおける予測性能のレポートなどは最低限に抑えるべきである．交差検証の結果は全てcsvに吐き出してしまい，その平均値は後でjupyter notebookで計算する，ROCカーブは保存されたモデルを使って後で計算して描画するなど，詳細な報告のために必要な処理はあとから行えばよい．学習中に詳細なレポートが見たい場合には学習の関数とは別の関数を作るなど，コードの可読性が下がらないようにされたい．

## 3.6 main関数を実行する

本章で述べたことを全てまとめると，以下のような実行コードが書ける．まず，モデル学習などの主たる処理を担うrun関数を定義する．上述の関数で定義されるlogger, config, argsをrun関数に引数で渡している．このサンプルコードに，データ読み込み，モデル学習などの処理を加えていけば良い．

```python sample.py
def run(logger, config, args):
    logger.info("Start run function")
    logger.info(f"Command line args, {args}")

    # --- some_process ---
    if args.flag:
        logger.info("True process")
    else:
        logger.info("False process")

    logger.info(f"Param1 = {config['param1']}")

    logger.info("End run function")
```

そして，全ての関数を呼び出して処理を実行するmain関数を作る．args, logger, configを定義し，run関数を実行する．なお，run関数はtry-exceptブロックの中で実行することで，発生した例外をロガーでキャッチしてその情報をログに書き込むようにしている．ちなみに，`except Exception`はPEP 8では推奨されていない書き方なのだが，run()関数で発生する全てのエラーを捕捉したいのでこの書き方を採用している．  
なお，以下の処理は全て`if __name__ == "__main__"`ブロックの中で記述することも可能ではある．ただ，mainブロック内の変数はグローバル変数の扱いになるので，それを嫌ってmain関数を実行する形をとっている．

```python sample.py
def main():
    # Settings
    args = init_args()
    logger = init_logger(args.logdir)
    config = load_config(args.config_path)
    save_config(args.logdir, config)

    # Run ml training
    try:
        run(logger, config, args)
    except Exception as e:
        logger.exception(f"Main function error: {e}")

    logger.info("End logger")


if __name__ == "__main__":
    main()
```

# 4. 信頼できるベースラインを作る

## 4.1 モデル評価の重要性

Kaggleというデータ分析コンペのプラットフォームで世界ランク1位(2019/12/01時点)に君臨するbestfitting氏は，インタビュー中で以下のように答えている (ただし，CV: Cross Validation)．

> A good CV is half of success.

出典: [Profiling Top Kagglers: Bestfitting, Currently #1 in the World](http://blog.kaggle.com/2018/05/07/profiling-top-kagglers-bestfitting-currently-1-in-the-world/)

ここからわかるように，信頼できる評価の上に全ての機械学習のテクニックは成り立っている．従って，特徴量エンジニアリングやハイパーパラメータ・チューニングなどの前に，信頼できる評価方法と，予測性能評価を確実に再現するプログラムを先に作るべきである．

例えば，以下のことには注意されたい．  

* 評価指標は解きたい問題を正しく反映しているか．回帰，分類という大分類だけでなく，数多くの指標の中から適切なものを選びたい．参考：[scikit-learn: 3.3. Metrics and scoring: quantifying the quality of predictions](https://scikit-learn.org/stable/modules/model_evaluation.html)
* 実際のシステムで動かすときに使えるデータのみを使っているか．例えば，時系列予測の問題で未来のデータを使っていないか．
* 情報リークは起きていないか．予測ラベルと関係のある特徴量が入り込んでいないか．
* 交差検証は正しくできているか．特に時系列データは要注意である．参考：[scikit-learn: 3.1. Cross-validation: evaluating estimator performance](https://scikit-learn.org/stable/modules/cross_validation.html)

これらに注意した上で，データ分析の結果を確実に再現するためにデータパイプラインを作ることを以下で提案する．パイプラインとは，データの一筋の流れを指し，データ分析の一連のプロセス，つまり，生データの取得，特徴量エンジニアリング，機械学習モデル，最終予測までを一つの道筋で表現する．常にこの道筋の上でデータを処理することにより，処理の再現性や信頼性が担保されやすくなる．

## 4.2 データ処理のパイプラインを作る

ここでは，特徴量エンジニアリングの部分の工夫を述べる．dataフォルダの構造が処理パイプラインを表現できるようになっている．

* input: 本当の生データを置く．例えば，センサー時系列データなどである．ここの中のデータは決して編集せずに生の状態で保管する．

* working: 中間ファイルを置く．例えば，特徴量を一つずつcsvファイルで保存する．特徴量を増やす場合には，まずこのフォルダ内に追加していくとよい．

* output: 機械学習モデルに入れる直前の状態のデータをおく．例えば，workingフォルダ内の特徴量の中から必要なものだけ結合したものなど．このoutput内のデータと学習結果は一対一で対応するように管理しておく．

従って，【DBなど → input → working → output → 機械学習モデル】というようにデータが処理されることになる．そして，この「→」部分をそれぞれ一つのプログラム（関数やクラス）が担当することで，一筆書きのようにデータが流れることを保証する．

## 4.3 モデル学習のパイプラインを作る

本節では，特にモデル学習部分でのパイプラインについて述べる．

* モデル本体においては[scikit-learnのpipeline](https://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html)を使うことが有効である．例えばパラメータ依存の前処理をこのパイプライン中に入れることが挙げられる．これには，特徴量のスケーリングや窓関数を使ったデータの水増し処理などが含まれる．  

* trainデータをさらにtrain-validationに分割する[nested cross-validation](https://scikit-learn.org/stable/auto_examples/model_selection/plot_nested_cross_validation_iris.html)も，信頼できるベースラインを作る上で重要である．

* 正しい[Cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html)を選ぶことも重要である．例えば，stratified k-fold, group k-fold, time series splitなど，CVにも幾つかの種類がある．データサイズに偏りがあるならばstratifiedを選ぶべきであるし，時系列データならば未来のデータで過去を予測しないようにtime series splitを選ぶべきである．解きたい課題に対して適切な評価方法を選ばれたい．

# 5. モデルや特徴量を作りこむ

## 5.1 様々なテクニックを駆使して評価指標を改善する

信頼できる評価方法が確立した後は，その指標の改善に努めるとよい．例えば，特徴量エンジニアリングでよく効く特徴量を見つける，前処理プログラムに工夫を加える，モデルを変更する，ハイパーパラメータ・チューニングを行うなどが挙げられる．評価指標が信頼できるからこそ，安心して様々な処理を加えて，その中から有用なものを選ぶことができる．細かいテクニックなどは書籍「[Kaggleで勝つデータ分析の技術](https://www.amazon.co.jp/dp/4297108437/ref=cm_sw_r_tw_dp_U_x_7o3bEbWMBK560)」に詳しい．

## 5.2 過剰な精度至上主義への戒め

一方で，評価指標の僅かな改善にあまりに固執することも考えものである．如何に信頼できる評価方法を確立して汎化性能を担保したとしても，それはあくまで手元のデータでの汎化性能である．仮にデータの生成過程が変わってしまえばその汎化性能は意味をなさなくなることが一般に知られており，この概念は共変量シフトという言葉で知られている．

また，機械学習モデルの精度は作りたいシステムの一つの評価方法でしかない．精度以外にも，この文書の主題である保守性や拡張性，さらには売り上げへの貢献や時間コストの削減といったビジネスインパクトなどでシステムを評価することもできる．機械学習とビジネスとの関連は書籍「[仕事ではじめる機械学習](https://www.amazon.co.jp/dp/4873118255/ref=cm_sw_r_tw_dp_U_x_Lp3bEbETN28QA)」に詳しい．

このように，機械学習モデルを含めたソリューションの評価は多角的にされるべきであり，精度を向上させることを絶対的な目標に設定することは必ずしも正しくない，というのが筆者の意見である．データ分析を実務として取り組む場合には，我々が真に解くべき問題は何なのか，その問題の解決度合いを適切に評価する方法は何なのか，を常に考え続けるようにしたい．

## 5.3 機械学習モデルの挙動を確認する

できあがった機械学習モデルが期待通りに動いて実務の問題を解決してくれるかを確認するためには，以下の事項を確認するとよい．

### 5.3.1 複数の評価指標を使う

単一の評価指標ではモデルの一側面しか見ることができないので，複数の評価指標を使うことが重要である．例えば，ROC-AUCは正例・負例のクラスバランスに対して頑健であるために絶対値を評価しやすい指標であるが，それ故にクラスバランスに対する評価ができない．その解決方法としては，例えばPR-AUC (Precision-Recall curve)を使うとデータサイズの偏りに即した評価ができる．どの指標が正しいというわけではなく，あくまで総合的に評価するという話である．

### 5.3.2 多様なデータを入れる

機械学習モデルはデータの外挿に弱いものが多いので，学習段階では手に入らなかったデータを頑張って手に入れてモデルの挙動を確かめることが挙げられる．実世界においては想定していなかったデータが入力されることが多いので，定期的にモデルの挙動を確認することも重要である．データの生成過程が変わったと考えられるならば，特徴量の再考やモデルの再学習も考えた方がよい，これらを通じてシステムの頑健性を担保することが求められる．

### 5.3.3 モデルを「説明」する

機械学習モデルはブラックボックスになりがちだという批判があるが，機械学習モデルを「説明」しようとする研究も進んでいる．日本人工知能学会の記事「[私のブックマーク「機械学習における解釈性（Interpretability in Machine Learning）」](https://www.ai-gakkai.or.jp/my-bookmark_vol33-no3/)」に詳しい．

# 6. Pythonパッケージを作る

ある程度分析プロセスが固まったら，パッケージ化してシステムにデプロイしたい．そのときに参考になる情報を記す．

## 6.1 パッケージ化

Pythonのプログラムをパッケージ化することは，システムに載せる上では必須の仕事である．プログラムは書いた本人が一番よくわかっているので，その本人が他人に使いやすい形にまで持っていくことが仕事である．パッケージ化の意義や詳細は「[（インターン向けに書いた）Pythonパッケージを作る方法](https://qiita.com/Kensuke-Mitsuzawa/items/7717f823df5a30c27077)」の記事に詳しい．

データサイエンスにおけるパッケージ化の例として，以下のような構成が挙げられる．これはデータ処理のプロセスに沿ってクラスを分割する目的で設定されている．

* dataset: データセットを用意するサブパッケージ．例えば，データベースやAPIから指定された期間の生データを取ってくることが挙げられる．

* preprocessing: 取得された生データに対して特徴量エンジニアリングを行う．data/input/フォルダ内のデータに処理をして中間ファイルをdata/working/に保存し，最後に特徴量をまとめてdata/output/フォルダ内に入れる．

* model: 機械学習モデル本体である．既存のモデル（scikit-learn, LightGBM等）を使う場合にはこれは不要だが，もしオリジナルのモデルを使う場合にはきちんとオブジェクト指向なモデルを用意したい．  

* train: 学習プログラムである．特徴量テーブルと機械学習モデルを準備して，Cross-Validationなどにより性能を評価する．

## 6.2 インストール

setup.pyを作成して，パッケージを自分の環境にインストールする．その際には仮想環境を作ってからインストールした方が，環境の再現性が担保されてよい．dockerを使うことも手段の一つである．

インストールの際には，通常のパッケージと同じように以下のコマンドを使う．なお，[pipを使わずに直接setup.pyを起動する方法($ python setup.py install)は推奨されていない](https://stackoverflow.com/questions/19048732/python-setup-py-develop-vs-install)．

```bash
pip install package
```

自分でコードを逐次改変していくのならば，[editableモードでinstallする](https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs)ことが推奨されている．これは，ディレクトリ中の.egg-linkへのリンクをsite-packagesに貼るだけなので，fresh reinstallする必要なくコードを改変，使用することができる．

```bash
pip install -e .
```

## 6.3 オブジェクト指向

Pythonは柔軟な書き方のできる言語であるが，基本的にはオブジェクト指向で書くのが良いと思われる．オブジェクト指向の思想は書籍「[オブジェクト指向でなぜつくるのか 第2版](https://www.kinokuniya.co.jp/f/dsg-08-9986783763)」に詳しい．

## 6.4 コード品質担保のためのtesting

「テストの無いコードは技術負債である」という言葉があるように，本番環境で動くコードにはテストが必須である．テストには単体テストや結合テストがあるが，まずは単体テストを導入する．Pythonには[unittest](https://docs.python.org/ja/3/library/unittest.html)という標準モジュールや[pytest](https://pypi.org/project/pytest/)というパッケージが用意されている．個人的にはpytestの方が情報量が多くて使いやすい．テストの重要性は「[機械学習モデルの実装における、テストについて](https://qiita.com/icoxfog417/items/67764a6756c4548b5fb8)」の記事に詳しい．

また，docstringを使ってテストを行う[doctest](https://docs.python.org/ja/3/library/doctest.html)も標準で用意されている．使い方は「[忙しい研究者のためのテストコードとドキュメントの書き方](https://qiita.com/NaokiHamada/items/0689cd85fb3e1adcda1a)」の記事に詳しい．

## 6.5 sphinxによるドキュメント作成

Pythonファイル内に記述されたdocstringを集約してドキュメントにするライブラリとしては[Sphinx](http://www.sphinx-doc.org/ja/stable/index.html)が有名である．ここでは詳述しないが，見やすいドキュメントを手軽に作りたい場合にはお勧めである．

# まとめ

本稿では，以下の6段階でデータ分析を進める方法について述べた．

1. 整然としたフォルダを構成する
2. 可読性の高いプログラムを書く
3. 実験の再現性を担保する
4. 信頼できるベースラインを作る
5. モデルや特徴量を作りこむ
6. Pythonパッケージを作る

可読性と再現性を保ったまま最後までデータ分析プロジェクトを完遂させるための技術的な手段を提示した．また，可読性と再現性の担保は拡張性や保守性，頑健性，公平性の向上にもある程度貢献することが期待される．実務の問題解決をすることのできる機械学習システムの構築に対して，本稿が一定の貢献ができたのならば幸いである．

# 参考文献

## A. Python

### 初心者向け

* [入門　Python 3](https://www.amazon.co.jp/dp/4873117380/ref=cm_sw_r_tw_dp_U_x_bo3bEbT203BJ8 )

### 詳しく勉強したい人向け

* [Fluent Python ―― Pythonicな思考とコーディング手法](https://www.amazon.co.jp/dp/4873118174/ref=cm_sw_r_tw_dp_U_x_Bq3bEb16QHJW2)
* [Effective Python　―― Pythonプログラムを改良する59項目](https://www.amazon.co.jp/dp/4873117569/ref=cm_sw_r_tw_dp_U_x_8q3bEbZ6A549Y)

## B. プログラミング

### アルゴリズムとデータ構造

* [プログラミングコンテスト攻略のためのアルゴリズムとデータ構造](https://www.amazon.co.jp/dp/B00U5MVXZO/ref=cm_sw_r_tw_dp_U_x_Br3bEbP0BY7FV)
* [プログラミングコンテストチャレンジブック](https://www.amazon.co.jp/dp/B00CY9256C/ref=cm_sw_r_tw_dp_U_x_Xr3bEb867EEBJ)
* [Pythonで体験してわかるアルゴリズムとデータ構造]( https://www.amazon.co.jp/dp/B07DWRZWZV/ref=cm_sw_r_tw_dp_U_x_ws3bEbMJE1XFH)
* [AtCoder](https://atcoder.jp/?lang=ja)

### コーディング

* [Pythonではじめるソフトウェアアーキテクチャ](https://www.amazon.co.jp/dp/432012443X/ref=cm_sw_r_tw_dp_U_x_9s3bEbC5AKBST)
* [リーダブルコード ―― より良いコードを書くためのシンプルで実践的なテクニック](https://www.amazon.co.jp/dp/4873115655/ref=cm_sw_r_tw_dp_U_x_dt3bEb5S7Y9ER )
* [テスト駆動開発](https://www.amazon.co.jp/dp/4274217884/ref=cm_sw_r_tw_dp_U_x_Vt3bEb09PNXPX )

## C. データ分析

### 入門

* [Chainer tutorial](https://tutorials.chainer.org/ja/tutorial.html)
* [Titanic Data Science Solutions](https://www.kaggle.com/startupsci/titanic-data-science-solutions)
* [Coursera: How to Win a Data Science Competition: Learn from Top Kagglers](https://ja.coursera.org/learn/competitive-data-science)

### 機械学習

* [Python 機械学習プログラミング 達人データサイエンティストによる理論と実践](https://www.amazon.co.jp/dp/B07BF5QZ41/ref=cm_sw_r_tw_dp_U_x_Ju3bEb06YH91J )
* [Pythonではじめる機械学習――scikit-learnで学ぶ特徴量エンジニアリングと機械学習の基礎](https://www.amazon.co.jp/dp/4873117984/ref=cm_sw_r_tw_dp_U_x_hv3bEbVYT0WSX)
* [はじめてのパターン認識](https://www.amazon.co.jp/dp/4627849710/ref=cm_sw_r_tw_dp_U_x_qv3bEb597PHMT)
* [機械学習のエッセンス](https://www.amazon.co.jp/dp/B07GYS3RG7/ref=cm_sw_r_tw_dp_U_x_mv3bEbFBTYK0G)

### 特徴量エンジニアリング

* [Kaggleで勝つデータ分析の技術](https://www.amazon.co.jp/dp/B07YTDBC3Z/ref=cm_sw_r_tw_dp_U_x_tw3bEb383TCQY)
* [機械学習のための特徴量エンジニアリング ――その原理とPythonによる実践](https://www.amazon.co.jp/dp/4873118689/ref=cm_sw_r_tw_dp_U_x_uw3bEbMN3G95P)
* [前処理大全 -- データ分析のためのSQL/R/Python実践テクニック](https://www.amazon.co.jp/dp/B07C3JFK3V/ref=cm_sw_r_tw_dp_U_x_xw3bEb66YAMCV)

### 書籍のまとめ記事

* [機械学習システム開発や統計分析を仕事にしたい人にオススメの書籍初級5冊＆中級10冊＋テーマ別9冊（2019年1月版）](https://tjo.hatenablog.com/entry/2019/01/10/190000)
* [「データサイエンスのオススメ本 その⑤」](http://datascientist.hatenadiary.com/entry/2018/01/12/193206)

## D. フォルダ構成

### データ分析におけるコード・フォルダ構成

* [データサイエンスプロジェクトのディレクトリ構成どうするか問題](https://takuti.me/note/data-science-project-structure/)
* [機械学習で泣かないためのコード設計 2018](https://www.slideshare.net/takahirokubo7792/2018-97367311)
* [機械学習で泣かないためのコード設計](https://www.slideshare.net/takahirokubo7792/ss-65413290)
* [Pythonの機械学習プロジェクトにおけるプログラミング設計](https://qiita.com/mokemokechicken/items/c9c0b042f3b1a7c383db)
* [解析のためのフォルダ構成](https://qiita.com/sshojiro/items/2f2720ba7697e8758855)
* [データ分析をするときのフォルダ構成をどうするのか問題について](https://www.st-hakky-blog.com/entry/2017/03/24/140738)
* [Cookiecutter Data Science](http://drivendata.github.io/cookiecutter-data-science/)

### 通常のPythonパッケージのフォルダ構成

* [（インターン向けに書いた）Pythonパッケージを作る方法](https://qiita.com/Kensuke-Mitsuzawa/items/7717f823df5a30c27077)
* [Structuring Your Project](https://docs.python-guide.org/writing/structure/)
* [Pythonのパッケージングのベストプラクティスについて考える2018](https://techblog.asahi-net.co.jp/entry/2018/06/15/162951)

### パッケージ構成のベストプラクティスについての論文

* [Best Practices for Scientific Computing](https://journals.plos.org/plosbiology/article?id=10.1371/journal.pbio.1001745)
* [Good enough practices in scientific computing](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005510)

## E. コーディング（再現性・保守性）

* [情報系研究者のためのtips 2019年度版](https://qiita.com/guicho271828/items/3664aec81f6cc7e8f179)
* [機械学習システムにおける「技術的負債」とその回避策](https://qiita.com/fujit33/items/f58055667493ae79e2dd)
* [私が機械学習研究をするときのコード・データ管理方法](https://qiita.com/ysekky/items/3db54349452dd8a336fb)
* [AIエンジニアが気をつけたいPython実装のノウハウ・コツまとめ](https://qiita.com/sugulu/items/c0e8a5e6b177bfe05e99)
* [Coding habits for data scientists](https://www.thoughtworks.com/insights/blog/coding-habits-data-scientists)
