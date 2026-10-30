# 教材の更新と個人学習の互換性

## 共有の正本
VERSION、curriculum/learning_topics.txt、curriculum/assignment_plan.txt、assignments/、materials/、templates/、docs/、AGENTS.mdが共通教材。scenario/company_facts.mdは初期設定。
教材変更は共有側で版とCHANGELOGを更新し、出題済み課題への影響を示す。学習者ごとの会社回答は共有初期設定へ混ぜない。

## 個人側に残すもの
submissions/、reviews/、progress/current_state.md、scenario/interview_log.md、学習者固有の追加資料、app/。これらを共有版の空ファイルで上書きしない。
既存company_factsに個人の追記があれば残すか、出典付きでinterview_logへ移してから初期設定との差を確認する。確認なく削除しない。

## 取り込み方法
AIは個人リポジトリの最新mainと変更中ファイルを読み、materials/*ブランチに教材の差分だけ反映する。元教材のmainを無条件にmerge/pullしない。課題本文・資料・AI規則を比較し、個人記録は編集対象を絞る。
curriculum/source.mdに共有リポジトリURL、教材版、取得コミット、対象ファイル、個人差分を記す。学習者がPRを確認・マージ後にmainをpullする。
作業中のstudyブランチへ取り込む場合、回答をcommitして保全後、mainとの差分を確認してmergeする。競合は自動上書きせず相談する。やり直しや再cloneは不要。

## v2→3.0.0
01Aの本文、提出テンプレート、現行Excelはバイト単位で維持。01B〜12を詳細化し、外部連携用サービスと試験資料を追加。01Aの採点要件は増えない。
Git運用を「提出をpush→AIレビュー→通過後merge」に統一。全課題収録済みでも出題状態は個人progressに従う。
実際のアプリ・SQL・設計図は学習者が作成する。模擬APIは外部サービス役であり、学習者の連携実装の解答ではない。
