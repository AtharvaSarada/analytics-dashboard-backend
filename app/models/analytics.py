"""
Analytics Data Models
Database models for storing time-series analytics data.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, Any, Dict

from sqlalchemy import (
    Boolean, Column, DateTime, String, Text, Numeric, Integer, 
    ForeignKey, Index, JSON, Float, BigInteger
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class MetricCategory(Base):
    """Metric categories for organizing analytics data."""
    
    __tablename__ = "metric_categories"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String(7), default="#3B82F6", nullable=False)  # Hex color
    icon = Column(String(50), nullable=True)  # Icon name/class
    sort_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    metrics = relationship("AnalyticsData", back_populates="category")
    
    def __repr__(self) -> str:
        return f"<MetricCategory(id={self.id}, name={self.name})>"


class AnalyticsData(Base):
    """Time-series analytics data with optimized indexing."""
    
    __tablename__ = "analytics_data"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # Metric Information
    metric_name = Column(String(100), nullable=False, index=True)
    metric_display_name = Column(String(200), nullable=True)
    category_id = Column(String(36), ForeignKey("metric_categories.id"), nullable=True, index=True)
    
    # Data Values
    value = Column(Numeric(precision=20, scale=6), nullable=False)
    value_type = Column(String(20), nullable=False, index=True)  # count, rate, percentage, currency, etc.
    
    # Additional metrics for comprehensive analytics
    previous_value = Column(Numeric(precision=20, scale=6), nullable=True)
    target_value = Column(Numeric(precision=20, scale=6), nullable=True)
    
    # Time Information (optimized for time-series queries)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    date_key = Column(String(10), nullable=False, index=True)  # YYYY-MM-DD for daily aggregation
    hour_key = Column(String(13), nullable=False, index=True)  # YYYY-MM-DD-HH for hourly aggregation
    
    # Dimensions for filtering and grouping
    dimensions = Column(JSON, nullable=True)  # Flexible dimensions storage
    source = Column(String(50), nullable=True, index=True)  # data source identifier
    
    # Geographic Information
    country = Column(String(2), nullable=True, index=True)  # ISO country code
    region = Column(String(100), nullable=True, index=True)
    city = Column(String(100), nullable=True, index=True)
    
    # Device/Platform Information
    device_type = Column(String(20), nullable=True, index=True)  # mobile, desktop, tablet
    platform = Column(String(50), nullable=True, index=True)  # ios, android, web
    browser = Column(String(50), nullable=True, index=True)
    
    # Quality and Metadata
    confidence_score = Column(Float, nullable=True)  # 0.0 - 1.0 confidence in data accuracy
    is_anomaly = Column(Boolean, default=False, nullable=False, index=True)
    tags = Column(JSON, nullable=True)  # Additional tags for categorization
    extra_data = Column(JSON, nullable=True)  # Additional metadata
    
    # Aggregation Information
    aggregation_level = Column(String(20), nullable=False, index=True)  # raw, hourly, daily, weekly, monthly
    aggregation_count = Column(BigInteger, default=1, nullable=False)  # Number of records aggregated
    
    # Data Quality
    is_verified = Column(Boolean, default=False, nullable=False)
    verification_method = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    category = relationship("MetricCategory", back_populates="metrics")
    
    def __repr__(self) -> str:
        return f"<AnalyticsData(id={self.id}, metric={self.metric_name}, value={self.value}, timestamp={self.timestamp})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert analytics data to dictionary."""
        return {
            "id": str(self.id),
            "metric_name": self.metric_name,
            "metric_display_name": self.metric_display_name,
            "category": self.category.name if self.category else None,
            "value": float(self.value) if self.value else None,
            "value_type": self.value_type,
            "previous_value": float(self.previous_value) if self.previous_value else None,
            "target_value": float(self.target_value) if self.target_value else None,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "date_key": self.date_key,
            "hour_key": self.hour_key,
            "dimensions": self.dimensions,
            "source": self.source,
            "country": self.country,
            "region": self.region,
            "city": self.city,
            "device_type": self.device_type,
            "platform": self.platform,
            "browser": self.browser,
            "confidence_score": self.confidence_score,
            "is_anomaly": self.is_anomaly,
            "tags": self.tags,
            "aggregation_level": self.aggregation_level,
            "aggregation_count": self.aggregation_count,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AlertRule(Base):
    """Alert rules for monitoring metrics."""
    
    __tablename__ = "alert_rules"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # Rule Configuration
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    metric_name = Column(String(100), nullable=False, index=True)
    
    # Condition Configuration
    condition_type = Column(String(20), nullable=False)  # threshold, change_rate, anomaly
    threshold_value = Column(Numeric(precision=20, scale=6), nullable=True)
    threshold_operator = Column(String(10), nullable=True)  # gt, lt, eq, gte, lte
    time_window_minutes = Column(Integer, default=5, nullable=False)
    
    # Alert Settings
    severity = Column(String(20), default="medium", nullable=False)  # low, medium, high, critical
    is_active = Column(Boolean, default=True, nullable=False)
    notification_channels = Column(JSON, nullable=True)  # email, slack, webhook
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    alerts = relationship("Alert", back_populates="rule")
    
    def __repr__(self) -> str:
        return f"<AlertRule(id={self.id}, name={self.name}, metric={self.metric_name})>"


class Alert(Base):
    """Generated alerts based on rules."""
    
    __tablename__ = "alerts"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # Alert Information
    rule_id = Column(String(36), ForeignKey("alert_rules.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    
    # Alert Details
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False, index=True)
    
    # Status
    status = Column(String(20), default="open", nullable=False, index=True)  # open, acknowledged, resolved
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Data Context
    trigger_value = Column(Numeric(precision=20, scale=6), nullable=True)
    metric_name = Column(String(100), nullable=False, index=True)
    triggered_at = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Additional Context
    context_data = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    rule = relationship("AlertRule", back_populates="alerts")
    user = relationship("User", back_populates="alerts")
    
    def __repr__(self) -> str:
        return f"<Alert(id={self.id}, title={self.title}, status={self.status})>"


# Optimized indexes for time-series queries
Index('idx_analytics_metric_timestamp', AnalyticsData.metric_name, AnalyticsData.timestamp)
Index('idx_analytics_date_key', AnalyticsData.date_key)
Index('idx_analytics_hour_key', AnalyticsData.hour_key)
Index('idx_analytics_source_timestamp', AnalyticsData.source, AnalyticsData.timestamp)
Index('idx_analytics_category_timestamp', AnalyticsData.category_id, AnalyticsData.timestamp)
Index('idx_analytics_aggregation_level', AnalyticsData.aggregation_level, AnalyticsData.timestamp)

# Indexes for alerts
Index('idx_alerts_status_created', Alert.status, Alert.created_at)
Index('idx_alerts_severity_created', Alert.severity, Alert.created_at)
Index('idx_alerts_triggered_at', Alert.triggered_at)
