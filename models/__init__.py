# Makes models a package
"""
Models package initializer.

This file imports all SQLAlchemy ORM models so they are
automatically discovered by Alembic migrations and
available when `Base.metadata.create_all()` is called.
"""

from db.models import (
    User,
    Resume,
    Job,
    JobMatch,
    Interview,
    PerformanceReview,
    LearningPath,
    AttendanceRecord,
    CompensationRecord,
    DiversityMetric,
)


# Optional: create a dict of models for dynamic access
ALL_MODELS = {
    "User": User,
    "Resume": Resume,
    "Job": Job,
    "JobMatch": JobMatch,
    "Interview": Interview,
    "PerformanceReview": PerformanceReview,
    "LearningPath": LearningPath,
    "AttendanceRecord": AttendanceRecord,
    "CompensationRecord": CompensationRecord,
    "DiversityMetric": DiversityMetric,
}
