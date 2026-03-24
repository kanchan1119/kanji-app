import streamlit as st
import json
import random

# データの読み込み
def load_data():
    try:
        with open('quiz_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("quiz_data.json が見つかりません。同じフォルダに置いてください。")
        return []

def main():
    st.set_page_config(page_title="小5漢字マスター", page_icon="✏️")
    
    # データのロード
    all_data = load_data()
    if not all_data:
        return

    # サイドバーでモード選択
    st.sidebar.title("メニュー")
    mode = st.sidebar.radio("モード選択", ["はじめから10問ずつ", "ランダムに10問"])

    # セッション状態のリセット管理（モードが変わったらリセット）
    if "current_mode" not in st.session_state or st.session_state.current_mode != mode:
        st.session_state.current_mode = mode
        st.session_state.idx = 0
        st.session_state.score = 0
        st.session_state.answered = False
        st.session_state.is_correct = False
        
        if mode == "はじめから10問ずつ":
            # ページ選択（0-9問目、10-19問目...）
            max_page = len(all_data) // 10
            page = st.sidebar.number_input(f"開始位置（0〜{max_page}）", 0, max_page, 0, step=1)
            start_idx = page * 10
            st.session_state.quiz_set = all_data[start_idx : start_idx + 10]
        else:
            # ランダムに10問抽出
            st.session_state.quiz_set = random.sample(all_data, min(10, len(all_data)))

    # クイズ画面の構築
    st.title(f"📖 小5漢字：{mode}")
    
    # 全10問終わったかチェック
    if st.session_state.idx < len(st.session_state.quiz_set):
        q = st.session_state.quiz_set[st.session_state.idx]
        
        st.progress((st.session_state.idx) / 10)
        st.subheader(f"第 {st.session_state.idx + 1} 問 / 10")
        
        # 問題文の表示
        st.info(f"### {q['q']}")
        st.caption("正しいものを選んでください")

        # 回答エリア
        if not st.session_state.answered:
            cols = st.columns(2)
            # 選択肢を表示（JSONのoptsを使用）
            for i, opt in enumerate(q['opts']):
                if cols[i % 2].button(opt, key=f"btn_{st.session_state.idx}_{i}", use_container_width=True):
                    st.session_state.answered = True
                    if opt == q['a']:
                        st.session_state.is_correct = True
                        st.session_state.score += 1
                    else:
                        st.session_state.is_correct = False
                    st.rerun()
        else:
            # 正解・不正解のフィードバック
            if st.session_state.is_correct:
                st.success(f"⭕️ 正解！【答え：{q['a']}】")
            else:
                st.error(f"❌ 残念... 【正解：{q['a']}】")
            
            if st.button("次の問題へ ➡️", type="primary"):
                st.session_state.idx += 1
                st.session_state.answered = False
                st.rerun()

    else:
        # 結果表示
        st.balloons()
        st.header("🎉 お疲れさまでした！")
        st.metric("スコア", f"{st.session_state.score} / 10 点")
        
        if st.button("もう一度やる"):
            # セッションをクリアして最初に戻る
            del st.session_state.current_mode
            st.rerun()

if __name__ == "__main__":
    main()