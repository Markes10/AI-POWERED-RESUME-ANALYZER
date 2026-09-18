"""
SQLAlchemy ORM models for the HR AI Platform.
Supports both Postgres (with pgvector) and MySQL.
Multi-tenant architecture with tenant isolation.
"""
from sqlalchemy import (
    Column, String, Integer, Float, Text, ForeignKey, DateTime, 
    JSON, Boolean, DECIMAL, Date, func, Index
)
from sqlalchemy.orm import relationship
from datetime import datetime

from db.database import Base


# -------------------------------
# Tenant model (Multi-tenancy)
# -------------------------------
class Tenant(Base):
    __tablename__ = "tenants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    domain = Column(String(255), unique=True, index=True, nullable=True)
    
    # Subscription
    tier = Column(String(50), default="free", nullable=False)  # free, starter, professional, enterprise
    status = Column(String(50), default="trial", nullable=False)  # active, suspended, trial, expired, pending
    trial_ends_at = Column(DateTime, nullable=True)
    subscription_ends_at = Column(DateTime, nullable=True)
    
    # Billing
    stripe_customer_id = Column(String(255), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    billing_email = Column(String(255), nullable=True)
    
    # Branding
    logo_url = Column(String(500), nullable=True)
    primary_color = Column(String(7), default="#2563eb", nullable=False)
    secondary_color = Column(String(7), default="#059669", nullable=False)
    favicon_url = Column(String(500), nullable=True)
    custom_css = Column(Text, nullable=True)
    
    # Settings
    settings = Column(JSON, default={}, nullable=False)
    custom_limits = Column(JSON, default={}, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    resumes = relationship("Resume", back_populates="tenant", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="tenant", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="tenant", cascade="all, delete-orphan")
    performance_reviews = relationship("PerformanceReview", back_populates="tenant", cascade="all, delete-orphan")
    learning_paths = relationship("LearningPath", back_populates="tenant", cascade="all, delete-orphan")
    attendance_records = relationship("AttendanceRecord", back_populates="tenant", cascade="all, delete-orphan")
    compensation_records = relationship("CompensationRecord", back_populates="tenant", cascade="all, delete-orphan")
    diversity_metrics = relationship("DiversityMetric", back_populates="tenant", cascade="all, delete-orphan")
    job_matches = relationship("JobMatch", back_populates="tenant", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('ix_tenant_slug_status', 'slug', 'status'),
        Index('ix_tenant_domain', 'domain'),
    )


# -------------------------------
# User model
# -------------------------------
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    username = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="employee")  # employee, hr, admin, manager
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    resumes = relationship("Resume", back_populates="user")
    interviews = relationship("Interview", foreign_keys="Interview.candidate_id", back_populates="candidate")
    reviews_received = relationship("PerformanceReview", foreign_keys="PerformanceReview.user_id", back_populates="user")
    reviews_given = relationship("PerformanceReview", foreign_keys="PerformanceReview.reviewer_id", back_populates="reviewer")
    learning_paths = relationship("LearningPath", back_populates="user")
    attendance_records = relationship("AttendanceRecord", back_populates="user")
    compensation_records = relationship("CompensationRecord", back_populates="user")
    
    # Composite unique constraint
    __table_args__ = (
        Index('ix_user_tenant_email', 'tenant_id', 'email', unique=True),
        Index('ix_user_tenant_username', 'tenant_id', 'username', unique=True),
    )


# -------------------------------
# Resume model
# -------------------------------
class Resume(Base):
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    resume_text = Column(Text)
    skills = Column(JSON)
    vector_embedding = Column(Text)
    source = Column(String(50), default="upload")  # upload, voice, api
    filename = Column(String(255), nullable=True)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="resumes")
    user = relationship("User", back_populates="resumes")
    job_matches = relationship("JobMatch", back_populates="resume")
    
    __table_args__ = (
        Index('ix_resume_tenant_user', 'tenant_id', 'user_id'),
        Index('ix_resume_tenant_created', 'tenant_id', 'created_at'),
    )


# -------------------------------
# Job model
# -------------------------------
class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    required_skills = Column(JSON)
    department = Column(String(100))
    level = Column(String(50), nullable=True)  # junior, mid, senior, lead, manager
    employment_type = Column(String(50), default="full-time")  # full-time, part-time, contract
    location = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="jobs")
    interviews = relationship("Interview", back_populates="job")
    job_matches = relationship("JobMatch", back_populates="job")
    
    __table_args__ = (
        Index('ix_job_tenant_active', 'tenant_id', 'is_active'),
    )


# -------------------------------
# Job Match model
# -------------------------------
class JobMatch(Base):
    __tablename__ = "job_matches"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    resume_id = Column(Integer, ForeignKey("resumes.id"))
    match_score = Column(Float)
    skill_overlap_score = Column(Float, nullable=True)
    skills_matched = Column(JSON)
    missing_skills = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="job_matches")
    job = relationship("Job", back_populates="job_matches")
    resume = relationship("Resume", back_populates="job_matches")
    
    __table_args__ = (
        Index('ix_jobmatch_tenant_job', 'tenant_id', 'job_id'),
        Index('ix_jobmatch_tenant_resume', 'tenant_id', 'resume_id'),
    )


# -------------------------------
# Interview model
# -------------------------------
class Interview(Base):
    __tablename__ = "interviews"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    candidate_id = Column(Integer, ForeignKey("users.id"))
    interviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    interview_date = Column(DateTime)
    duration_minutes = Column(Integer, default=60)
    questions = Column(JSON)
    answers = Column(JSON)
    feedback = Column(Text)
    score = Column(Integer, nullable=True)  # 1-100
    status = Column(String(20), default="scheduled")  # scheduled, in_progress, completed, cancelled
    transcript = Column(Text, nullable=True)  # Full transcript from STT
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="interviews")
    job = relationship("Job", back_populates="interviews")
    candidate = relationship("User", foreign_keys=[candidate_id], back_populates="interviews")
    interviewer = relationship("User", foreign_keys=[interviewer_id])
    
    __table_args__ = (
        Index('ix_interview_tenant_date', 'tenant_id', 'interview_date'),
        Index('ix_interview_tenant_status', 'tenant_id', 'status'),
    )


# -------------------------------
# Performance Review model
# -------------------------------
class PerformanceReview(Base):
    __tablename__ = "performance_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    reviewer_id = Column(Integer, ForeignKey("users.id"))
    review_period = Column(String(50))
    goals = Column(JSON)
    achievements = Column(Text)
    feedback = Column(Text)
    rating = Column(Integer)
    strengths = Column(JSON, nullable=True)
    areas_for_improvement = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="performance_reviews")
    user = relationship("User", foreign_keys=[user_id], back_populates="reviews_received")
    reviewer = relationship("User", foreign_keys=[reviewer_id], back_populates="reviews_given")
    
    __table_args__ = (
        Index('ix_perf_review_tenant_user', 'tenant_id', 'user_id'),
        Index('ix_perf_review_tenant_period', 'tenant_id', 'review_period'),
    )


# -------------------------------
# Learning Path model
# -------------------------------
class LearningPath(Base):
    __tablename__ = "learning_paths"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    current_skills = Column(JSON)
    target_skills = Column(JSON)
    recommended_courses = Column(JSON)
    progress = Column(Integer, default=0)
    target_role = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="learning_paths")
    user = relationship("User", back_populates="learning_paths")
    
    __table_args__ = (
        Index('ix_learning_path_tenant_user', 'tenant_id', 'user_id'),
    )


# -------------------------------
# Attendance Record model
# -------------------------------
class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    check_in = Column(DateTime)
    check_out = Column(DateTime, nullable=True)
    status = Column(String(20))  # present, absent, late, early_leave
    anomaly_score = Column(Float, default=0.0)
    location = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="attendance_records")
    user = relationship("User", back_populates="attendance_records")
    
    __table_args__ = (
        Index('ix_attendance_tenant_user_date', 'tenant_id', 'user_id', 'check_in'),
    )


# -------------------------------
# Compensation Record model
# -------------------------------
class CompensationRecord(Base):
    __tablename__ = "compensation_records"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    salary = Column(DECIMAL(10, 2))
    bonus = Column(DECIMAL(10, 2))
    effective_date = Column(Date)
    department = Column(String(100))
    position = Column(String(100))
    currency = Column(String(3), default="USD")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="compensation_records")
    user = relationship("User", back_populates="compensation_records")
    
    __table_args__ = (
        Index('ix_compensation_tenant_user', 'tenant_id', 'user_id'),
        Index('ix_compensation_tenant_date', 'tenant_id', 'effective_date'),
    )


# -------------------------------
# Diversity Metric model
# -------------------------------
class DiversityMetric(Base):
    __tablename__ = "diversity_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    department = Column(String(100))
    metrics = Column(JSON)
    report_date = Column(Date)
    recommendations = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="diversity_metrics")
    
    __table_args__ = (
        Index('ix_diversity_tenant_dept_date', 'tenant_id', 'department', 'report_date'),
    )


# Import Tenant models from tenant_service to avoid circular imports
# These are defined in services/tenant_service.py and need to be imported here
# for the Base.metadata.create_all() to work properly

# The following models are imported from services.tenant_service:
# - TenantAPIKey
# - TenantAuditLog
# - TenantInvitation

# They will be automatically registered with Base.metadata when tenant_service is imported