import json
from dataclasses import dataclass

VALID_STATUSES = {"SUCCESS", "FAILED", "CANCELLED"}


@dataclass
class Build:
    build_id: str
    branch: str
    status: str
    duration_seconds: float
    tests_passed: int
    tests_failed: int

    def __post_init__(self):
        if not self.build_id.strip():
            raise ValueError("Build ID cannot be empty")

        if not self.branch.strip():
            raise ValueError("Branch cannot be empty")

        if self.status not in VALID_STATUSES:
            raise ValueError(f"Invalid build status: {self.status}")

        if self.duration_seconds < 0:
            raise ValueError("Build duration cannot be negative")

        if self.tests_passed < 0 or self.tests_failed < 0:
            raise ValueError("Test counts cannot be negative")

    @property
    def total_tests(self) -> int:
        return self.tests_passed + self.tests_failed

    @property
    def test_pass_rate(self) -> float:
        if self.total_tests == 0:
            return 0.0

        return (self.tests_passed / self.total_tests) * 100


class BuildAnalyzer:

    def __init__(self, builds: list[Build]):
        self.builds = builds

    def successful_builds(self) -> list[Build]:
        return [
            build for build in self.builds
            if build.status == "SUCCESS"
        ]

    def failed_builds(self) -> list[Build]:
        return [
            build for build in self.builds
            if build.status == "FAILED"
        ]

    def success_rate(self) -> float:
        if not self.builds:
            return 0.0

        successful = len(self.successful_builds())

        return (successful / len(self.builds)) * 100

    def average_duration(self) -> float:
        if not self.builds:
            return 0.0

        total = sum(
            build.duration_seconds
            for build in self.builds
        )

        return total / len(self.builds)

    def overall_test_pass_rate(self) -> float:
        total_passed = sum(
            build.tests_passed
            for build in self.builds
        )

        total_failed = sum(
            build.tests_failed
            for build in self.builds
        )

        total_tests = total_passed + total_failed

        if total_tests == 0:
            return 0.0

        return (total_passed / total_tests) * 100

    def deployment_ready(self) -> bool:
        if not self.builds:
            return False

        latest_build = self.builds[-1]

        return (
            latest_build.status == "SUCCESS"
            and latest_build.tests_failed == 0
        )

    def summary(self) -> dict:
        return {
            "total_builds": len(self.builds),
            "successful_builds": len(self.successful_builds()),
            "failed_builds": len(self.failed_builds()),
            "success_rate": round(self.success_rate(), 2),
            "average_duration_seconds": round(
                self.average_duration(), 2
            ),
            "overall_test_pass_rate": round(
                self.overall_test_pass_rate(), 2
            ),
            "deployment_ready": self.deployment_ready(),
        }


def create_builds(data: list) -> list[Build]:
    return [
        Build(
            build_id=item["build_id"],
            branch=item["branch"],
            status=item["status"],
            duration_seconds=item["duration_seconds"],
            tests_passed=item["tests_passed"],
            tests_failed=item["tests_failed"],
        )
        for item in data
    ]


def analyze_build_history(data: list) -> dict:
    builds = create_builds(data)

    analyzer = BuildAnalyzer(builds)

    return analyzer.summary()


def lambda_handler(event, context):
    try:
        body = event.get("body", event)

        if isinstance(body, str):
            body = json.loads(body)

        builds = body.get("builds", [])

        result = analyze_build_history(builds)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Build analysis completed successfully",
                "analysis": result
            })
        }

    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "Invalid build data",
                "error": str(error)
            })
        }