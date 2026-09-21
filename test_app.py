import pytest

from app import (
    Build,
    BuildAnalyzer,
    analyze_build_history,
    create_builds,
    lambda_handler,
)


@pytest.fixture
def sample_builds():
    return [
        Build(
            build_id="build-001",
            branch="main",
            status="SUCCESS",
            duration_seconds=120,
            tests_passed=10,
            tests_failed=0,
        ),
        Build(
            build_id="build-002",
            branch="main",
            status="FAILED",
            duration_seconds=180,
            tests_passed=7,
            tests_failed=3,
        ),
        Build(
            build_id="build-003",
            branch="develop",
            status="SUCCESS",
            duration_seconds=90,
            tests_passed=15,
            tests_failed=0,
        ),
    ]


def test_build_creation():
    build = Build(
        "build-001",
        "main",
        "SUCCESS",
        100,
        10,
        0,
    )

    assert build.build_id == "build-001"
    assert build.status == "SUCCESS"


def test_total_tests():
    build = Build(
        "build-001",
        "main",
        "SUCCESS",
        100,
        8,
        2,
    )

    assert build.total_tests == 10


def test_test_pass_rate():
    build = Build(
        "build-001",
        "main",
        "SUCCESS",
        100,
        8,
        2,
    )

    assert build.test_pass_rate == 80.0


def test_empty_build_id():
    with pytest.raises(ValueError):
        Build("", "main", "SUCCESS", 100, 10, 0)


def test_invalid_status():
    with pytest.raises(ValueError):
        Build(
            "build-001",
            "main",
            "UNKNOWN",
            100,
            10,
            0,
        )


def test_negative_duration():
    with pytest.raises(ValueError):
        Build(
            "build-001",
            "main",
            "SUCCESS",
            -10,
            10,
            0,
        )


def test_successful_builds(sample_builds):
    analyzer = BuildAnalyzer(sample_builds)

    assert len(analyzer.successful_builds()) == 2


def test_failed_builds(sample_builds):
    analyzer = BuildAnalyzer(sample_builds)

    assert len(analyzer.failed_builds()) == 1


def test_success_rate(sample_builds):
    analyzer = BuildAnalyzer(sample_builds)

    assert round(analyzer.success_rate(), 2) == 66.67


def test_average_duration(sample_builds):
    analyzer = BuildAnalyzer(sample_builds)

    assert analyzer.average_duration() == 130


def test_overall_test_pass_rate(sample_builds):
    analyzer = BuildAnalyzer(sample_builds)

    assert round(analyzer.overall_test_pass_rate(), 2) == 91.43


def test_deployment_ready(sample_builds):
    analyzer = BuildAnalyzer(sample_builds)

    assert analyzer.deployment_ready() is True


def test_analysis_summary(sample_builds):
    analyzer = BuildAnalyzer(sample_builds)

    summary = analyzer.summary()

    assert summary["total_builds"] == 3
    assert summary["successful_builds"] == 2
    assert summary["failed_builds"] == 1
    assert summary["success_rate"] == 66.67


def test_create_builds():
    data = [
        {
            "build_id": "build-001",
            "branch": "main",
            "status": "SUCCESS",
            "duration_seconds": 100,
            "tests_passed": 10,
            "tests_failed": 0,
        }
    ]

    builds = create_builds(data)

    assert len(builds) == 1
    assert builds[0].build_id == "build-001"


def test_analyze_build_history():
    data = [
        {
            "build_id": "build-001",
            "branch": "main",
            "status": "SUCCESS",
            "duration_seconds": 100,
            "tests_passed": 10,
            "tests_failed": 0,
        }
    ]

    result = analyze_build_history(data)

    assert result["total_builds"] == 1
    assert result["success_rate"] == 100.0


def test_lambda_handler():
    event = {
        "body": {
            "builds": [
                {
                    "build_id": "build-001",
                    "branch": "main",
                    "status": "SUCCESS",
                    "duration_seconds": 100,
                    "tests_passed": 10,
                    "tests_failed": 0,
                }
            ]
        }
    }

    response = lambda_handler(event, None)

    assert response["statusCode"] == 200


def test_lambda_handler_invalid_data():
    event = {
        "body": {
            "builds": [
                {
                    "build_id": "",
                    "branch": "main",
                    "status": "SUCCESS",
                    "duration_seconds": 100,
                    "tests_passed": 10,
                    "tests_failed": 0,
                }
            ]
        }
    }

    response = lambda_handler(event, None)

    assert response["statusCode"] == 400