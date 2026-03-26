import streamlit as st
import json
import random

# データの読み込み関数
def load_data():
    try:
        with open('quiz_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"データの読み込みに失敗しました: {e}")
        return []

def main():
    st.set_page_config(page_title="小5漢字マスター", page_icon="✏️")
    
    all_data = load_data()
    if not all_data:
        st.warning("quiz_data.json を確認してください。")
        return

    # --- サイドバー：設定エリア ---
    st.sidebar.title("🛠 設定")
    mode = st.sidebar.radio("モード選択", ["番号ごとに10問", "ランダムに10問"])
    
    page = 0
    if mode == "番号ごとに10問":
        max_page = (len(all_data) - 1) // 10
        page = st.sidebar.number_input(f"開始位置 (0〜{max_page})", 0, max_page, 0, step=1)
        st.sidebar.info(f"【{page*10 + 1}問目】からスタートします")

    # 出題順の選択
    order = st.sidebar.radio("出題順", ["そのまま", "ランダム（10問内）"])

    # 「クイズを開始する」ボタン
    if st.sidebar.button("✨ クイズを開始・リセット"):
        st.session_state.quiz_started = True
        st.session_state.idx = 0
        st.session_state.score = 0
        st.session_state.answered = False
        
        # --- 問題セットの作成 ---
        selected_questions = []
        if mode == "番号ごとに10問":
            start_idx = page * 10
            selected_questions = all_data[start_idx : start_idx + 10]
            # 出題順をシャッフル
            if order == "ランダム（10問内）":
                random.shuffle(selected_questions)
        else:
            # 全体からランダムに10問
            selected_questions = random.sample(all_data, min(10, len(all_data)))

        # --- 選択肢の順番をランダム化 ---
        # 各問題ごとに選択肢の並び順をシャッフルします
        for q in selected_questions:
            # optsのコピーを作ってシャッフル（元データ破壊防止）
            random.shuffle(q['opts'])
        
        st.session_state.quiz_set = selected_questions
        st.rerun()

    # --- メイン画面 ---
    st.title("📖 小5漢字クイズ")

    # クイズ開始前
    if "quiz_started" not in st.session_state or not st.session_state.quiz_started:
        st.write("### 準備ができたら、左の「クイズを開始」ボタンを押してね！")
        st.write(f"現在は **「{mode}」** の **「{order}」** 順が選ばれています。")
        return

    # クイズ実行中
    if st.session_state.idx < len(st.session_state.quiz_set):
        q = st.session_state.quiz_set[st.session_state.idx]
        
        st.progress((st.session_state.idx) / len(st.session_state.quiz_set))
        st.write(f"**第 {st.session_state.idx + 1} 問 / {len(st.session_state.quiz_set)}**")
        
        st.info(f"### {q['q']}")

        # 選択肢ボタン
        if not st.session_state.answered:
            cols = st.columns(2)
            for i, opt in enumerate(q['opts']):
                if cols[i % 2].button(opt, key=f"btn_{st.session_state.idx}_{i}", use_container_width=True):
                    st.session_state.answered = True
                    st.session_state.selected_opt = opt
                    st.rerun()
        else:
            # 回答後の判定
            if st.session_state.selected_opt == q['a']:
                st.success(f"⭕️ 正解！ 【答え：{q['a']}】")
                if "incremented" not in st.session_state:
                    st.session_state.score += 1
                    st.session_state.incremented = True
            else:
                st.error(f"❌ 残念... 【正解：{q['a']}】")
            
            if st.button("次の問題へ ➡️", type="primary"):
                st.session_state.idx += 1
                st.session_state.answered = False
                if "incremented" in st.session_state:
                    del st.session_state.incremented
                st.rerun()
    else:
        # --- 結果画面（豪華演出） ---
        current_score = st.session_state.score
        
        if current_score == 10:
            # 10点満点：特大の祝福
            st.snow()
            st.balloons()
            st.title("🎊🎊🎊 完璧！！！ 🎊🎊🎊")
            st.title(f"🏆 10点満点！！ 🥇")
            st.metric("最高の結果です！", "10 / 10 点", delta="満点達成！")
            st.write("### あなたは漢字マスターです！この調子でどんどん進もう！")
        else:
            # 10点未満：通常の祝福
            st.balloons()
            st.header("🎉 クリア！")
            st.metric("今回のスコア", f"{current_score} / 10 点")
            
            if current_score >= 8:
                st.write("惜しい！あと少しで満点だね。")
            elif current_score >= 5:
                st.write("半分以上正解！次はもっと上を目指そう。")
            else:
                st.write("まずは10問中5問正解を目標にがんばろう！")

        if st.button("もう一度挑戦する"):
            del st.session_state.quiz_started
            st.rerun()

if __name__ == "__main__":
    main()
