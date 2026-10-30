# 学習開始とGit運用

## 新しい学習者
1. この共有教材を自分のGitHubにForkする（元教材へ回答PRを送らない）。公開Forkでは回答も公開されるため、非公開を希望する場合は独立した非公開リポジトリに教材をコピーする。実在の業務データは使用しない。
2. 自分のリポジトリをcloneし、AIにREADMEとAGENTSを渡す。Git初心者はAIと一操作ずつ進める。
3. progress/current_state.mdに自分の経験・環境を記録し、01Aから開始する。interview_logは空のまま開始。教員の例を自分の成果にしない。
4. VERSIONを教材版として記録する。教材更新を自動で取り込まない。

既に個人用リポジトリで学んでいる人は、新しく始め直さない。既存提出・ヒアリング・進捗を保ち、docs/curriculum_updates.mdで教材差分だけ取り込む。

## 1課題のサイクル
1. AIが必要な教材・記録更新を個人リポジトリのmaterials/課題名ブランチへ反映。学習者が差分を見てPRを作成しmainへマージ。既に課題が収録済みなら出題状態の記録だけでよい。
2. 学習者がmainをpullし、study/課題IDブランチを作る。
3. 学習者がローカルで課題を行い、submissions/へ回答。コードはapp/に新規Laravelプロジェクトとして配置（異なる配置も記録すれば可）。
4. 学習者が差分確認、commit、push。GitHubでmain宛のPRを作成し、URLをAIへ知らせる。
5. AIがそのPRのコミットを読み、企業への回答とレビューを分けて返す。修正は同じstudyブランチでcommit/pushし、再レビューを依頼。
6. 通過したら学習者がPRをmainへマージ。AIはレビュー/進捗の更新をmaterials/*へ反映し、学習者が取り込む。回答PRの直後に記録PRを作ることで競合を減らす。
7. 次の課題へ。提出前のpushは「提出」、通過後のマージは「確定」。push自体は通過を意味しない。

## コマンドの意味と例
以下は手順の全体例。一括実行せず現在の状態を確認する。01Aならstudy/01a、次はstudy/01b。既存ブランチに-cで重複作成しない。

```sh
# リポジトリ直下。まず未保存変更とブランチを確認
git status
# 作業が保全され、mainへ取り込まれた教材を取得するとき
git switch main
git pull --ff-only origin main
# 新しい課題用ブランチ（未作成の場合だけ）
git switch -c study/01a
# 回答作成後、対象を絞って追加
git diff
git add submissions/01A_v1.txt
git diff --cached
git commit -m "Submit assignment 01A"
git push -u origin study/01a
```

PRはブランチの変更をmainへ取り込む前に比較・確認する場所。GitHubでbase=main、compare=study/01aを選ぶ。Mergeは変更をmainへ統合する操作。pullはその後のmainを手元へ取得する操作。

未コミット変更がある間は不用意に切替・pullしない。必要な変更を今の学習ブランチにcommitするなど保全してから進める。mainが分岐して--ff-onlyで止まったら強制せずAIへ結果を提示。エラー全文に秘密があれば伏せる。
AIと学習者が同じGitHubアカウントを使う場合、レビュー上の通過とGitHubのApproveは別。AIは自分のアカウントのPRにApproveできると約束しない。
