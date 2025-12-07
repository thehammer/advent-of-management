"""
Uploads scenarios to S3 and manages local file storage
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

import boto3
from botocore.exceptions import ClientError

from .scenario_gen import ManagementScenario, MultiLevelScenario

# Union type for both scenario formats
Scenario = ManagementScenario | MultiLevelScenario


class Publisher(Protocol):
    """Protocol for scenario publishers."""

    def publish_scenario(self, scenario: Scenario) -> str:
        """Publish scenario and return its URL/path."""
        ...

    def update_manifest(self, year: int, latest_day: int) -> None:
        """Update the manifest with latest day info."""
        ...

    def get_scenario(self, year: int, day: int) -> dict | None:
        """Retrieve a published scenario."""
        ...


class LocalPublisher:
    """Publishes scenarios to local filesystem for testing."""

    def __init__(self, base_path: str = "scenarios"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def publish_scenario(self, scenario: Scenario) -> str:
        """Save scenario to local JSON file."""
        year_path = self.base_path / str(scenario.year)
        year_path.mkdir(exist_ok=True)

        file_path = year_path / f"day{scenario.day}.json"
        file_path.write_text(scenario.to_json())

        return str(file_path)

    def update_manifest(self, year: int, latest_day: int) -> None:
        """Update local manifest.json."""
        year_path = self.base_path / str(year)
        year_path.mkdir(exist_ok=True)

        manifest = {
            "year": year,
            "latest_day": latest_day,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "base_url": f"file://{self.base_path.absolute()}",
        }

        manifest_path = year_path / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2))

    def get_scenario(self, year: int, day: int) -> dict | None:
        """Load scenario from local file."""
        file_path = self.base_path / str(year) / f"day{day}.json"
        if file_path.exists():
            return json.loads(file_path.read_text())
        return None

    def list_scenarios(self, year: int) -> list[int]:
        """List available days for a year."""
        year_path = self.base_path / str(year)
        if not year_path.exists():
            return []

        days = []
        for file in year_path.glob("day*.json"):
            try:
                day = int(file.stem.replace("day", ""))
                days.append(day)
            except ValueError:
                continue

        return sorted(days)


class S3Publisher:
    """Publishes scenarios to S3."""

    def __init__(
        self,
        bucket_name: str,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        region: str = "us-east-1",
    ):
        self.bucket = bucket_name
        self.region = region

        # Use explicit credentials if provided, otherwise use default chain
        if aws_access_key_id and aws_secret_access_key:
            self.s3 = boto3.client(
                "s3",
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=region,
            )
        else:
            self.s3 = boto3.client("s3", region_name=region)

        self.base_url = f"https://{bucket_name}.s3.{region}.amazonaws.com"

    def publish_scenario(self, scenario: Scenario) -> str:
        """Upload scenario JSON to S3."""
        key = f"{scenario.year}/day{scenario.day}.json"

        self.s3.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=scenario.to_json(),
            ContentType="application/json",
            CacheControl="max-age=3600",  # 1 hour cache
        )

        return f"{self.base_url}/{key}"

    def update_manifest(self, year: int, latest_day: int) -> None:
        """Update manifest.json with latest available day."""
        manifest = {
            "year": year,
            "latest_day": latest_day,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "base_url": self.base_url,
        }

        self.s3.put_object(
            Bucket=self.bucket,
            Key=f"{year}/manifest.json",
            Body=json.dumps(manifest, indent=2),
            ContentType="application/json",
            CacheControl="max-age=300",  # 5 minute cache for manifest
        )

    def get_scenario(self, year: int, day: int) -> dict | None:
        """Retrieve a scenario from S3."""
        key = f"{year}/day{day}.json"
        try:
            response = self.s3.get_object(Bucket=self.bucket, Key=key)
            return json.loads(response["Body"].read().decode("utf-8"))
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                return None
            raise

    def ensure_bucket_exists(self) -> bool:
        """Check if bucket exists, optionally create it."""
        try:
            self.s3.head_bucket(Bucket=self.bucket)
            return True
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "404":
                return False
            raise

    def create_bucket(self, public_read: bool = True) -> None:
        """Create the S3 bucket with optional public read access."""
        # Create bucket
        if self.region == "us-east-1":
            self.s3.create_bucket(Bucket=self.bucket)
        else:
            self.s3.create_bucket(
                Bucket=self.bucket,
                CreateBucketConfiguration={"LocationConstraint": self.region},
            )

        if public_read:
            # Set bucket policy for public read
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "PublicRead",
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "s3:GetObject",
                        "Resource": f"arn:aws:s3:::{self.bucket}/*",
                    }
                ],
            }
            self.s3.put_bucket_policy(
                Bucket=self.bucket,
                Policy=json.dumps(policy),
            )

            # Disable block public access
            self.s3.put_public_access_block(
                Bucket=self.bucket,
                PublicAccessBlockConfiguration={
                    "BlockPublicAcls": False,
                    "IgnorePublicAcls": False,
                    "BlockPublicPolicy": False,
                    "RestrictPublicBuckets": False,
                },
            )
