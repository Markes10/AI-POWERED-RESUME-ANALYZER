"""
Multi-Tenant SaaS Architecture Service
Provides tenant isolation, customization, and management.
"""
import os
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship

from db.database import Base

logger = logging.getLogger(__name__)


class TenantTier(str, Enum):
    """Tenant subscription tiers."""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class TenantStatus(str, Enum):
    """Tenant account status."""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    EXPIRED = "expired"
    PENDING = "pending"


@dataclass
class TenantLimits:
    """Resource limits per tenant tier."""
    max_users: int
    max_resumes_per_month: int
    max_api_calls_per_day: int
    max_storage_gb: float
    custom_branding: bool
    sso_enabled: bool
    audit_logs: bool
    priority_support: bool
    custom_integrations: bool
    dedicated_infrastructure: bool


# Default limits per tier
TIER_LIMITS = {
    TenantTier.FREE: TenantLimits(
        max_users=5,
        max_resumes_per_month=50,
        max_api_calls_per_day=1000,
        max_storage_gb=1.0,
        custom_branding=False,
        sso_enabled=False,
        audit_logs=False,
        priority_support=False,
        custom_integrations=False,
        dedicated_infrastructure=False
    ),
    TenantTier.STARTER: TenantLimits(
        max_users=25,
        max_resumes_per_month=500,
        max_api_calls_per_day=10000,
        max_storage_gb=10.0,
        custom_branding=True,
        sso_enabled=False,
        audit_logs=True,
        priority_support=False,
        custom_integrations=False,
        dedicated_infrastructure=False
    ),
    TenantTier.PROFESSIONAL: TenantLimits(
        max_users=100,
        max_resumes_per_month=5000,
        max_api_calls_per_day=100000,
        max_storage_gb=100.0,
        custom_branding=True,
        sso_enabled=True,
        audit_logs=True,
        priority_support=True,
        custom_integrations=True,
        dedicated_infrastructure=False
    ),
    TenantTier.ENTERPRISE: TenantLimits(
        max_users=1000,
        max_resumes_per_month=50000,
        max_api_calls_per_day=1000000,
        max_storage_gb=1000.0,
        custom_branding=True,
        sso_enabled=True,
        audit_logs=True,
        priority_support=True,
        custom_integrations=True,
        dedicated_infrastructure=True
    ),
}


class Tenant(Base):
    """Tenant/Organization model for multi-tenancy."""
    __tablename__ = "tenants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    domain = Column(String(255), unique=True, index=True, nullable=True)  # Custom domain
    
    # Subscription
    tier = Column(String(50), default=TenantTier.FREE.value, nullable=False)
    status = Column(String(50), default=TenantStatus.TRIAL.value, nullable=False)
    trial_ends_at = Column(DateTime, nullable=True)
    subscription_ends_at = Column(DateTime, nullable=True)
    
    # Billing
    stripe_customer_id = Column(String(255), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    billing_email = Column(String(255), nullable=True)
    
    # Branding
    logo_url = Column(String(500), nullable=True)
    primary_color = Column(String(7), default="#2563eb", nullable=False)  # hex color
    secondary_color = Column(String(7), default="#059669", nullable=False)
    favicon_url = Column(String(500), nullable=True)
    custom_css = Column(Text, nullable=True)
    
    # Settings
    settings = Column(JSON, default={}, nullable=False)
    # Settings structure:
    # {
    #   "features": {...},
    #   "integrations": {...},
    #   "security": {...},
    #   "notifications": {...}
    # }
    
    # Limits (overrides tier defaults)
    custom_limits = Column(JSON, default={}, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    api_keys = relationship("TenantAPIKey", back_populates="tenant", cascade="all, delete-orphan")
    audit_logs = relationship("TenantAuditLog", back_populates="tenant", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('ix_tenant_slug_status', 'slug', 'status'),
        Index('ix_tenant_domain', 'domain'),
        Index('ix_tenant_stripe_customer', 'stripe_customer_id'),
    )


class TenantAPIKey(Base):
    """API keys for tenant programmatic access."""
    __tablename__ = "tenant_api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    key_hash = Column(String(255), nullable=False)  # Hashed API key
    key_prefix = Column(String(20), nullable=False)  # First 8 chars for identification
    
    scopes = Column(JSON, default=["read"], nullable=False)  # ["read", "write", "admin"]
    rate_limit = Column(Integer, default=1000, nullable=False)  # requests per hour
    
    last_used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="api_keys")
    creator = relationship("User")


class TenantAuditLog(Base):
    """Audit log for tenant activities."""
    __tablename__ = "tenant_audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    action = Column(String(100), nullable=False)  # e.g., "user.created", "settings.updated"
    resource_type = Column(String(100), nullable=True)  # e.g., "user", "resume", "settings"
    resource_id = Column(String(100), nullable=True)
    
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="audit_logs")
    user = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('ix_audit_log_tenant_created', 'tenant_id', 'created_at'),
        Index('ix_audit_log_user_created', 'user_id', 'created_at'),
        Index('ix_audit_log_action', 'action'),
    )


class TenantInvitation(Base):
    """Tenant user invitations."""
    __tablename__ = "tenant_invitations"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    role = Column(String(50), default="member", nullable=False)  # admin, manager, member
    
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    
    accepted_at = Column(DateTime, nullable=True)
    accepted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    tenant = relationship("Tenant")


class TenantService:
    """Service for managing multi-tenant operations."""
    
    def __init__(self, db_session):
        self.db = db_session
    
    def create_tenant(
        self,
        name: str,
        slug: str,
        admin_email: str,
        admin_password: str,
        tier: TenantTier = TenantTier.FREE,
        domain: Optional[str] = None
    ) -> Tenant:
        """Create a new tenant with admin user."""
        from services.auth import get_password_hash
        from db.models import User
        
        # Check slug availability
        existing = self.db.query(Tenant).filter(Tenant.slug == slug).first()
        if existing:
            raise ValueError("Tenant slug already exists")
        
        # Create tenant
        tenant = Tenant(
            name=name,
            slug=slug,
            domain=domain,
            tier=tier.value,
            status=TenantStatus.TRIAL.value,
            trial_ends_at=datetime.utcnow().replace(day=datetime.utcnow().day + 14),
            settings={
                "features": {
                    "resume_analysis": True,
                    "interview_copilot": True,
                    "compensation_analysis": tier != TenantTier.FREE,
                    "turnover_prediction": tier in [TenantTier.PROFESSIONAL, TenantTier.ENTERPRISE],
                    "learning_paths": tier != TenantTier.FREE,
                    "diversity_analysis": tier == TenantTier.ENTERPRISE
                },
                "integrations": {
                    "ats": tier in [TenantTier.PROFESSIONAL, TenantTier.ENTERPRISE],
                    "hris": tier == TenantTier.ENTERPRISE,
                    "sso": tier in [TenantTier.PROFESSIONAL, TenantTier.ENTERPRISE],
                    "webhooks": tier in [TenantTier.PROFESSIONAL, TenantTier.ENTERPRISE]
                },
                "security": {
                    "password_min_length": 8,
                    "require_2fa": tier in [TenantTier.PROFESSIONAL, TenantTier.ENTERPRISE],
                    "session_timeout_minutes": 480,
                    "password_history": 5
                },
                "notifications": {
                    "email_enabled": True,
                    "slack_enabled": tier in [TenantTier.PROFESSIONAL, TenantTier.ENTERPRISE],
                    "in_app_enabled": True
                }
            }
        )
        
        self.db.add(tenant)
        self.db.flush()
        
        # Create admin user
        admin_user = User(
            tenant_id=tenant.id,
            username=admin_email.split("@")[0],
            email=admin_email,
            password_hash=get_password_hash(admin_password),
            role="admin",
            is_active=True
        )
        
        self.db.add(admin_user)
        self.db.commit()
        self.db.refresh(tenant)
        
        logger.info(f"Created tenant: {tenant.slug} (ID: {tenant.id})")
        return tenant
    
    def get_tenant_by_slug(self, slug: str) -> Optional[Tenant]:
        """Get tenant by slug."""
        return self.db.query(Tenant).filter(
            Tenant.slug == slug,
            Tenant.deleted_at.is_(None)
        ).first()
    
    def get_tenant_by_domain(self, domain: str) -> Optional[Tenant]:
        """Get tenant by custom domain."""
        return self.db.query(Tenant).filter(
            Tenant.domain == domain,
            Tenant.deleted_at.is_(None)
        ).first()
    
    def get_tenant_limits(self, tenant: Tenant) -> TenantLimits:
        """Get effective limits for a tenant (tier + custom overrides)."""
        base_limits = TIER_LIMITS.get(TenantTier(tenant.tier), TIER_LIMITS[TenantTier.FREE])
        
        # Apply custom overrides
        custom = tenant.custom_limits or {}
        return TenantLimits(
            max_users=custom.get("max_users", base_limits.max_users),
            max_resumes_per_month=custom.get("max_resumes_per_month", base_limits.max_resumes_per_month),
            max_api_calls_per_day=custom.get("max_api_calls_per_day", base_limits.max_api_calls_per_day),
            max_storage_gb=custom.get("max_storage_gb", base_limits.max_storage_gb),
            custom_branding=custom.get("custom_branding", base_limits.custom_branding),
            sso_enabled=custom.get("sso_enabled", base_limits.sso_enabled),
            audit_logs=custom.get("audit_logs", base_limits.audit_logs),
            priority_support=custom.get("priority_support", base_limits.priority_support),
            custom_integrations=custom.get("custom_integrations", base_limits.custom_integrations),
            dedicated_infrastructure=custom.get("dedicated_infrastructure", base_limits.dedicated_infrastructure)
        )
    
    def check_limit(self, tenant: Tenant, resource: str, current_usage: int) -> bool:
        """Check if tenant has exceeded a resource limit."""
        limits = self.get_tenant_limits(tenant)
        
        limit_map = {
            "users": limits.max_users,
            "resumes_per_month": limits.max_resumes_per_month,
            "api_calls_per_day": limits.max_api_calls_per_day,
            "storage_gb": limits.max_storage_gb
        }
        
        limit = limit_map.get(resource)
        if limit is None:
            return True  # No limit defined
        
        return current_usage < limit
    
    def get_tenant_branding(self, tenant: Tenant) -> Dict[str, Any]:
        """Get tenant branding configuration."""
        return {
            "name": tenant.name,
            "logo_url": tenant.logo_url,
            "primary_color": tenant.primary_color,
            "secondary_color": tenant.secondary_color,
            "favicon_url": tenant.favicon_url,
            "custom_css": tenant.custom_css
        }
    
    def update_tenant_settings(self, tenant: Tenant, settings: Dict[str, Any]) -> Tenant:
        """Update tenant settings."""
        tenant.settings = {**tenant.settings, **settings}
        tenant.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(tenant)
        return tenant
    
    def update_tenant_branding(
        self,
        tenant: Tenant,
        logo_url: Optional[str] = None,
        primary_color: Optional[str] = None,
        secondary_color: Optional[str] = None,
        favicon_url: Optional[str] = None,
        custom_css: Optional[str] = None
    ) -> Tenant:
        """Update tenant branding."""
        limits = self.get_tenant_limits(tenant)
        
        if not limits.custom_branding:
            raise PermissionError("Custom branding not available for this tier")
        
        if logo_url is not None:
            tenant.logo_url = logo_url
        if primary_color is not None:
            tenant.primary_color = primary_color
        if secondary_color is not None:
            tenant.secondary_color = secondary_color
        if favicon_url is not None:
            tenant.favicon_url = favicon_url
        if custom_css is not None:
            tenant.custom_css = custom_css
        
        tenant.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(tenant)
        return tenant
    
    def create_api_key(
        self,
        tenant: Tenant,
        name: str,
        scopes: List[str],
        rate_limit: int = 1000,
        expires_at: Optional[datetime] = None,
        created_by: int = None
    ) -> tuple[TenantAPIKey, str]:
        """Create a new API key for tenant."""
        import secrets
        import hashlib
        
        # Generate API key
        raw_key = f"hr_{tenant.slug}_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        key_prefix = raw_key[:8]
        
        api_key = TenantAPIKey(
            tenant_id=tenant.id,
            name=name,
            key_hash=key_hash,
            key_prefix=key_prefix,
            scopes=scopes,
            rate_limit=rate_limit,
            expires_at=expires_at,
            created_by=created_by
        )
        
        self.db.add(api_key)
        self.db.commit()
        self.db.refresh(api_key)
        
        return api_key, raw_key  # Return raw key only once
    
    def validate_api_key(self, api_key: str) -> Optional[TenantAPIKey]:
        """Validate an API key and return associated tenant API key record."""
        import hashlib
        
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        api_key_record = self.db.query(TenantAPIKey).filter(
            TenantAPIKey.key_hash == key_hash,
            TenantAPIKey.is_active == True
        ).first()
        
        if not api_key_record:
            return None
        
        if api_key_record.expires_at and api_key_record.expires_at < datetime.utcnow():
            return None
        
        # Update last used
        api_key_record.last_used_at = datetime.utcnow()
        self.db.commit()
        
        return api_key_record
    
    def log_audit(
        self,
        tenant_id: int,
        action: str,
        user_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        old_values: Optional[Dict] = None,
        new_values: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> TenantAuditLog:
        """Log an audit event."""
        audit_log = TenantAuditLog(
            tenant_id=tenant_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        return audit_log
    
    def get_tenant_usage(self, tenant: Tenant) -> Dict[str, Any]:
        """Get current resource usage for a tenant."""
        from db.models import User, Resume
        from sqlalchemy import func
        from datetime import datetime, timedelta
        
        # User count
        user_count = self.db.query(func.count(User.id)).filter(
            User.tenant_id == tenant.id,
            User.is_active == True
        ).scalar() or 0
        
        # Resume count (current month)
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        resume_count = self.db.query(func.count(Resume.id)).filter(
            Resume.tenant_id == tenant.id,
            Resume.created_at >= month_start
        ).scalar() or 0
        
        # Storage usage (approximate)
        storage_result = self.db.query(func.sum(func.length(Resume.resume_text))).filter(
            Resume.tenant_id == tenant.id
        ).scalar()
        storage_gb = (storage_result or 0) / (1024 * 1024 * 1024)
        
        limits = self.get_tenant_limits(tenant)
        
        return {
            "users": {
                "current": user_count,
                "limit": limits.max_users,
                "percentage": round((user_count / limits.max_users) * 100, 1) if limits.max_users > 0 else 0
            },
            "resumes_per_month": {
                "current": resume_count,
                "limit": limits.max_resumes_per_month,
                "percentage": round((resume_count / limits.max_resumes_per_month) * 100, 1) if limits.max_resumes_per_month > 0 else 0
            },
            "storage_gb": {
                "current": round(storage_gb, 2),
                "limit": limits.max_storage_gb,
                "percentage": round((storage_gb / limits.max_storage_gb) * 100, 1) if limits.max_storage_gb > 0 else 0
            },
            "tier": tenant.tier,
            "status": tenant.status
        }
    
    def invite_user(
        self,
        tenant: Tenant,
        email: str,
        role: str = "member",
        invited_by: int = None
    ) -> TenantInvitation:
        """Invite a user to the tenant."""
        import secrets
        from datetime import timedelta
        
        # Check if user already exists in tenant
        from db.models import User
        existing = self.db.query(User).filter(
            User.email == email,
            User.tenant_id == tenant.id
        ).first()
        
        if existing:
            raise ValueError("User already exists in this tenant")
        
        # Check for existing pending invitation
        existing_inv = self.db.query(TenantInvitation).filter(
            TenantInvitation.tenant_id == tenant.id,
            TenantInvitation.email == email,
            TenantInvitation.accepted_at.is_(None),
            TenantInvitation.expires_at > datetime.utcnow()
        ).first()
        
        if existing_inv:
            raise ValueError("Pending invitation already exists for this email")
        
        token = secrets.token_urlsafe(32)
        invitation = TenantInvitation(
            tenant_id=tenant.id,
            email=email,
            role=role,
            token=token,
            expires_at=datetime.utcnow() + timedelta(days=7),
            created_by=invited_by
        )
        
        self.db.add(invitation)
        self.db.commit()
        self.db.refresh(invitation)
        
        # TODO: Send invitation email
        logger.info(f"Invitation sent to {email} for tenant {tenant.slug}")
        
        return invitation
    
    def accept_invitation(self, token: str, password: str) -> User:
        """Accept a tenant invitation."""
        from services.auth import get_password_hash
        from db.models import User
        
        invitation = self.db.query(TenantInvitation).filter(
            TenantInvitation.token == token,
            TenantInvitation.expires_at > datetime.utcnow(),
            TenantInvitation.accepted_at.is_(None)
        ).first()
        
        if not invitation:
            raise ValueError("Invalid or expired invitation")
        
        # Create user
        user = User(
            tenant_id=invitation.tenant_id,
            username=invitation.email.split("@")[0],
            email=invitation.email,
            password_hash=get_password_hash(password),
            role=invitation.role,
            is_active=True
        )
        
        self.db.add(user)
        
        # Mark invitation as accepted
        invitation.accepted_at = datetime.utcnow()
        invitation.accepted_by = user.id
        
        self.db.commit()
        self.db.refresh(user)
        
        return user


# Middleware for tenant resolution
class TenantResolver:
    """Middleware to resolve tenant from request."""
    
    def __init__(self, app, db_session_factory):
        self.app = app
        self.db_session_factory = db_session_factory
    
    async def __call__(self, scope, receive, send):
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return
        
        # Extract tenant from headers or subdomain
        headers = dict(scope.get("headers", []))
        host = headers.get(b"host", b"").decode()
        
        tenant = None
        db = self.db_session_factory()
        
        try:
            # Try custom domain first
            if host and ":" in host:
                host = host.split(":")[0]
            
            if host and not host.startswith("localhost") and not host.startswith("127.0.0.1"):
                # Check if it's a custom domain
                tenant_service = TenantService(db)
                tenant = tenant_service.get_tenant_by_domain(host)
            
            # Fallback to header
            if not tenant:
                tenant_slug = headers.get(b"x-tenant-slug")
                if tenant_slug:
                    tenant_slug = tenant_slug.decode()
                    tenant_service = TenantService(db)
                    tenant = tenant_service.get_tenant_by_slug(tenant_slug)
            
            # Store tenant in scope for downstream use
            scope["tenant"] = tenant
            scope["tenant_service"] = TenantService(db)
            
        finally:
            db.close()
        
        await self.app(scope, receive, send)


# Dependency for FastAPI
def get_tenant_service(request) -> TenantService:
    """FastAPI dependency to get tenant service."""
    return request.scope.get("tenant_service")


def get_current_tenant(request) -> Optional[Tenant]:
    """FastAPI dependency to get current tenant."""
    return request.scope.get("tenant")


def require_tenant(request) -> Tenant:
    """FastAPI dependency that requires a valid tenant."""
    tenant = request.scope.get("tenant")
    if not tenant:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Tenant not found")
    return tenant


def require_tier(*allowed_tiers: TenantTier):
    """FastAPI dependency that requires specific tenant tier."""
    def _check_tier(request) -> Tenant:
        tenant = require_tenant(request)
        if TenantTier(tenant.tier) not in allowed_tiers:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=403,
                detail=f"This feature requires one of: {[t.value for t in allowed_tiers]}"
            )
        return tenant
    return _check_tier


# Usage tracking for billing
class UsageTracker:
    """Track tenant resource usage for billing."""
    
    def __init__(self, tenant_service: TenantService):
        self.tenant_service = tenant_service
    
    def track_resume_upload(self, tenant: Tenant) -> bool:
        """Track resume upload. Returns True if allowed, False if limit exceeded."""
        usage = self.tenant_service.get_tenant_usage(tenant)
        current = usage["resumes_per_month"]["current"]
        limit = usage["resumes_per_month"]["limit"]
        
        if current >= limit:
            return False
        return True
    
    def track_api_call(self, tenant: Tenant) -> bool:
        """Track API call. Returns True if allowed, False if limit exceeded."""
        # In production, would use Redis for real-time counting
        # For now, just check against limit
        usage = self.tenant_service.get_tenant_usage(tenant)
        limits = self.tenant_service.get_tenant_limits(tenant)
        
        # Would check against Redis counter
        return True  # Simplified
    
    def get_usage_report(self, tenant: Tenant) -> Dict[str, Any]:
        """Get detailed usage report for billing."""
        return self.tenant_service.get_tenant_usage(tenant)