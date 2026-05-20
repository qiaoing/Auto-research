from local_runner.orchestrator import is_allowed_quality_check, select_pending_task
from local_runner.security import safe_filename_component


def test_select_pending_task_uses_priority_order():
    task = select_pending_task(
        [
            {"id": "B", "status": "pending", "priority": 2},
            {"id": "A", "status": "pending", "priority": 1},
            {"id": "DONE", "status": "done", "priority": 0},
        ]
    )

    assert task["id"] == "A"


def test_quality_check_policy_allows_pytest_forms():
    assert is_allowed_quality_check(["pytest", "-q"])
    assert is_allowed_quality_check(["python", "-m", "pytest", "-q"])
    assert not is_allowed_quality_check(["python", "-c", "print('unsafe')"])


def test_safe_filename_component_removes_path_separators():
    assert safe_filename_component("../SIM-001") == "SIM-001"
