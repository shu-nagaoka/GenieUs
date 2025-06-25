"""エージェントルーティング安定化テストケース

ルーティング安定化修正の動作確認用テストケース
"""

# 期待されるルーティング結果のテストケース
ROUTING_TEST_CASES = [
    # 栄養・食事関連（nutrition_specialist期待）
    {"message": "離乳食を食べてくれません", "expected_primary": "nutrition_specialist", "test_type": "nutrition_basic"},
    {"message": "栄養バランスが心配です", "expected_primary": "nutrition_specialist", "test_type": "nutrition_concern"},
    {
        "message": "アレルギーのある食材を避けたいです",
        "expected_primary": "nutrition_specialist",
        "test_type": "nutrition_allergy",
    },
    # 睡眠関連（sleep_specialist期待）
    {"message": "夜泣きがひどくて困っています", "expected_primary": "sleep_specialist", "test_type": "sleep_basic"},
    {"message": "寝かしつけに時間がかかります", "expected_primary": "sleep_specialist", "test_type": "sleep_routine"},
    {"message": "昼寝をしてくれません", "expected_primary": "sleep_specialist", "test_type": "sleep_nap"},
    # 健康管理関連（health_specialist期待 - 強制ルーティング）
    {
        "message": "熱が38度あります",
        "expected_primary": "health_specialist",
        "test_type": "health_emergency",
        "force_routing": True,
    },
    {"message": "咳が止まらなくて心配です", "expected_primary": "health_specialist", "test_type": "health_symptoms"},
    # 発達支援関連（development_specialist期待）
    {
        "message": "言葉が遅いように感じます",
        "expected_primary": "development_specialist",
        "test_type": "development_language",
    },
    {
        "message": "他の子より歩くのが遅いです",
        "expected_primary": "development_specialist",
        "test_type": "development_motor",
    },
    # 行動・しつけ関連（behavior_specialist期待）
    {"message": "イヤイヤ期がひどいです", "expected_primary": "behavior_specialist", "test_type": "behavior_tantrum"},
    {"message": "叱り方がわからない", "expected_primary": "behavior_specialist", "test_type": "behavior_discipline"},
    # 安全関連（safety_specialist期待 - 強制ルーティング）
    {
        "message": "転落して頭を打ちました",
        "expected_primary": "safety_specialist",
        "test_type": "safety_emergency",
        "force_routing": True,
    },
    {
        "message": "誤飲の可能性があります",
        "expected_primary": "safety_specialist",
        "test_type": "safety_choking",
        "force_routing": True,
    },
    # 曖昧なケース（coordinator期待）
    {"message": "子育てについて相談したいです", "expected_primary": "coordinator", "test_type": "general_inquiry"},
    {"message": "初めての子育てで不安です", "expected_primary": "coordinator", "test_type": "general_anxiety"},
    # 複合的なケース（priority高いほうが選択される期待）
    {
        "message": "熱があるときの離乳食はどうすればいい？",
        "expected_primary": "health_specialist",  # 健康が優先度高
        "test_type": "complex_health_nutrition",
        "secondary_keywords": ["nutrition_specialist"],
    },
    {
        "message": "夜泣きで栄養不足が心配",
        "expected_primary": "sleep_specialist",  # 両方同じ優先度だが、スコア計算で決定
        "test_type": "complex_sleep_nutrition",
        "secondary_keywords": ["nutrition_specialist"],
    },
    # 否定形テスト
    {
        "message": "食べてくれない時はどうする？",
        "expected_primary": "nutrition_specialist",
        "test_type": "negative_eating",
    },
    {"message": "寝てくれないんです", "expected_primary": "sleep_specialist", "test_type": "negative_sleeping"},
    # 並列・順次分析
    {
        "message": "総合的に子どもの発達を分析してほしい",
        "expected_primary": "parallel",
        "test_type": "parallel_analysis",
    },
    {"message": "段階的にアドバイスをください", "expected_primary": "sequential", "test_type": "sequential_analysis"},
]

# 不適切ルーティングのテストケース（修正されるべき）
INAPPROPRIATE_ROUTING_CASES = [
    {
        "message": "離乳食について",
        "inappropriate_agent": "sleep_specialist",
        "expected_correction": "nutrition_specialist",
    },
    {
        "message": "夜泣きがひどい",
        "inappropriate_agent": "nutrition_specialist",
        "expected_correction": "sleep_specialist",
    },
    {
        "message": "熱が出ています",
        "inappropriate_agent": "play_learning_specialist",
        "expected_correction": "health_specialist",
    },
]


def validate_routing_accuracy(test_results: list) -> dict:
    """ルーティング精度の検証結果"""
    total_tests = len(test_results)
    correct_routing = sum(1 for result in test_results if result["routing_correct"])
    force_routing_tests = [r for r in test_results if r.get("force_routing")]
    force_routing_correct = sum(1 for result in force_routing_tests if result["routing_correct"])

    return {
        "total_tests": total_tests,
        "correct_routing": correct_routing,
        "accuracy": (correct_routing / total_tests) * 100 if total_tests > 0 else 0,
        "force_routing_accuracy": (force_routing_correct / len(force_routing_tests)) * 100
        if force_routing_tests
        else 0,
        "detailed_results": test_results,
    }
