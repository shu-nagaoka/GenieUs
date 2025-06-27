"""現在のルーティングシステムの問題点を実証するテスト

このファイルは問題点の可視化のためのもので、実際のテストスイートではありません
"""

from src.agents.constants import AGENT_KEYWORDS, AGENT_PRIORITY, FORCE_ROUTING_KEYWORDS


class MockLogger:
    """テスト用のモックロガー"""

    def info(self, msg, **kwargs):
        print(f"[INFO] {msg}")

    def error(self, msg, **kwargs):
        print(f"[ERROR] {msg}")

    def warning(self, msg, **kwargs):
        print(f"[WARNING] {msg}")


def test_context_problem():
    """文脈理解の問題を実証"""
    print("\n=== 文脈理解の問題 ===")

    # AgentManagerの_determine_specialist_agentメソッドを模倣
    test_cases = [
        ("熱はありません", "health_specialist", "「熱」にマッチして健康専門家へ"),
        ("食べ過ぎではないです", "nutrition_specialist", "「食べ過ぎ」にマッチして栄養専門家へ"),
        ("夜泣きしなくなりました", "sleep_specialist", "「夜泣き」にマッチして睡眠専門家へ"),
    ]

    for message, expected_wrong_agent, reason in test_cases:
        message_lower = message.lower()
        agent_scores = {}

        # 現在のロジックを再現
        for agent_id, keywords in AGENT_KEYWORDS.items():
            if agent_id in AGENT_PRIORITY:
                matched_keywords = [kw for kw in keywords if kw in message_lower]
                if matched_keywords:
                    keyword_weight = sum(len(kw) for kw in matched_keywords)
                    score = len(matched_keywords) * AGENT_PRIORITY[agent_id] * (1 + keyword_weight * 0.1)
                    agent_scores[agent_id] = {
                        "score": score,
                        "matched_keywords": matched_keywords[:3],
                        "match_count": len(matched_keywords),
                    }

        if agent_scores:
            best_agent = max(agent_scores.items(), key=lambda x: x[1]["score"])
            agent_id, score_info = best_agent
            print(f"\nメッセージ: 「{message}」")
            print(f"誤ルーティング: {agent_id} (期待: coordinator)")
            print(f"理由: {reason}")
            print(f"マッチキーワード: {score_info['matched_keywords']}")


def test_complex_intent_problem():
    """複雑な意図の解釈問題を実証"""
    print("\n\n=== 複雑な意図の解釈問題 ===")

    complex_messages = [
        "2歳の子どもが最近野菜を食べなくなって、発達に影響がないか心配です",
        "夜泣きがひどくて私も眠れず、精神的に参っています",
        "離乳食を始めたいけど、アレルギーが心配で、どう進めればいいかわかりません",
    ]

    for message in complex_messages:
        message_lower = message.lower()
        agent_scores = {}

        for agent_id, keywords in AGENT_KEYWORDS.items():
            if agent_id in AGENT_PRIORITY:
                matched_keywords = [kw for kw in keywords if kw in message_lower]
                if matched_keywords:
                    keyword_weight = sum(len(kw) for kw in matched_keywords)
                    score = len(matched_keywords) * AGENT_PRIORITY[agent_id] * (1 + keyword_weight * 0.1)
                    agent_scores[agent_id] = {
                        "score": score,
                        "matched_keywords": matched_keywords,
                        "match_count": len(matched_keywords),
                    }

        print(f"\nメッセージ: 「{message}」")
        print("マッチしたエージェント:")
        sorted_agents = sorted(agent_scores.items(), key=lambda x: x[1]["score"], reverse=True)
        for agent_id, score_info in sorted_agents[:3]:
            print(f"  - {agent_id}: スコア {score_info['score']:.1f}, キーワード {score_info['matched_keywords']}")
        print("問題: 複数の専門性が必要だが、単一エージェントに決定される")


def test_priority_rigidity():
    """優先度の硬直性問題を実証"""
    print("\n\n=== 優先度の硬直性問題 ===")

    print("現在の固定優先度:")
    for agent_id, priority in sorted(AGENT_PRIORITY.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {agent_id}: {priority}")

    print("\n問題: 文脈によって優先度が変わるべきケース")
    print("例: 「検索」キーワード")
    print("  - 「近くの小児科を検索して」→ search_specialist（優先度10）が適切")
    print("  - 「子育て情報を検索したい」→ coordinator（一般相談）が適切")
    print("  しかし現在は常にsearch_specialistが優先される")


def test_maintenance_problem():
    """保守性の問題を実証"""
    print("\n\n=== 保守性の問題 ===")

    total_keywords = sum(len(keywords) for keywords in AGENT_KEYWORDS.values())
    force_keywords = sum(len(keywords) for keywords in FORCE_ROUTING_KEYWORDS.values())

    print(f"総キーワード数: {total_keywords + force_keywords}")
    print(f"  - 通常キーワード: {total_keywords}")
    print(f"  - 強制ルーティングキーワード: {force_keywords}")

    print("\n問題:")
    print("1. 新しい表現が出るたびに追加が必要")
    print("2. 方言（例：「めし」「まんま」）への対応")
    print("3. 若者言葉（例：「ワンチャン」「エモい」）への対応")
    print("4. 誤字脱字への対応（例：「離乳職」「夜鳴き」）")


if __name__ == "__main__":
    print("GenieUs ルーティングシステムの問題点デモンストレーション")
    print("=" * 60)

    test_context_problem()
    test_complex_intent_problem()
    test_priority_rigidity()
    test_maintenance_problem()

    print("\n\n=== まとめ ===")
    print("現在のキーワードベースルーティングの限界:")
    print("1. 否定文や文脈を理解できない")
    print("2. 複雑な相談内容の意図を適切に解釈できない")
    print("3. 優先度が固定で柔軟性がない")
    print("4. キーワードの保守が困難")
    print("\n→ LLMベースまたはハイブリッドアプローチが必要")
