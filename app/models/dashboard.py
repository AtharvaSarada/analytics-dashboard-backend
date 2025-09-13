"""
Dashboard Models
Database models for dashboard configuration and layout management.
"""

import uuid
from datetime import datetime
from typing import Optional, Any, Dict, List

from sqlalchemy import (
    Boolean, Column, DateTime, String, Text, Integer, 
    ForeignKey, Index, JSON
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class Dashboard(Base):
    """Dashboard configuration and metadata."""
    
    __tablename__ = "dashboards"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Basic Information
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    slug = Column(String(100), nullable=True, index=True)  # URL-friendly identifier
    
    # Ownership and Access
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    is_public = Column(Boolean, default=False, nullable=False)
    is_template = Column(Boolean, default=False, nullable=False)
    
    # Layout Configuration
    layout_type = Column(String(20), default="grid", nullable=False)  # grid, flex, custom
    grid_columns = Column(Integer, default=12, nullable=False)
    grid_gap = Column(Integer, default=4, nullable=False)  # Gap in pixels/rem
    
    # Styling
    theme = Column(String(20), default="light", nullable=False)  # light, dark, auto
    primary_color = Column(String(7), default="#3B82F6", nullable=False)  # Hex color
    background_color = Column(String(7), nullable=True)  # Custom background
    
    # Behavior Settings
    auto_refresh = Column(Boolean, default=True, nullable=False)
    refresh_interval = Column(Integer, default=30, nullable=False)  # seconds
    enable_filters = Column(Boolean, default=True, nullable=False)
    enable_export = Column(Boolean, default=True, nullable=False)
    
    # Metadata
    tags = Column(JSONB, nullable=True)  # Dashboard tags for categorization
    settings = Column(JSONB, nullable=True)  # Additional dashboard settings
    
    # Statistics
    view_count = Column(Integer, default=0, nullable=False)
    last_viewed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    status = Column(String(20), default="active", nullable=False, index=True)  # active, archived, draft
    is_favorite = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    owner = relationship("User", back_populates="dashboards")
    widgets = relationship("DashboardWidget", back_populates="dashboard", cascade="all, delete-orphan")
    shared_access = relationship("DashboardAccess", back_populates="dashboard", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Dashboard(id={self.id}, name={self.name}, owner_id={self.owner_id})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert dashboard to dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "slug": self.slug,
            "owner_id": str(self.owner_id),
            "is_public": self.is_public,
            "is_template": self.is_template,
            "layout_type": self.layout_type,
            "grid_columns": self.grid_columns,
            "grid_gap": self.grid_gap,
            "theme": self.theme,
            "primary_color": self.primary_color,
            "background_color": self.background_color,
            "auto_refresh": self.auto_refresh,
            "refresh_interval": self.refresh_interval,
            "enable_filters": self.enable_filters,
            "enable_export": self.enable_export,
            "tags": self.tags,
            "settings": self.settings,
            "view_count": self.view_count,
            "last_viewed_at": self.last_viewed_at.isoformat() if self.last_viewed_at else None,
            "status": self.status,
            "is_favorite": self.is_favorite,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "widget_count": len(self.widgets) if self.widgets else 0,
        }


class DashboardWidget(Base):
    """Individual widgets within a dashboard."""
    
    __tablename__ = "dashboard_widgets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Dashboard Association
    dashboard_id = Column(UUID(as_uuid=True), ForeignKey("dashboards.id"), nullable=False, index=True)
    
    # Widget Configuration
    widget_type = Column(String(50), nullable=False, index=True)  # chart, metric, table, text, etc.
    title = Column(String(200), nullable=True)
    subtitle = Column(String(300), nullable=True)
    
    # Data Configuration
    metric_names = Column(JSONB, nullable=True)  # Metrics to display
    data_source = Column(String(100), nullable=True, index=True)
    query_config = Column(JSONB, nullable=True)  # Query parameters and filters
    
    # Chart Configuration
    chart_type = Column(String(50), nullable=True)  # line, bar, pie, area, gauge, etc.
    chart_config = Column(JSONB, nullable=True)  # Chart.js configuration
    
    # Layout and Position
    position_x = Column(Integer, default=0, nullable=False)
    position_y = Column(Integer, default=0, nullable=False)
    width = Column(Integer, default=4, nullable=False)  # Grid columns
    height = Column(Integer, default=3, nullable=False)  # Grid rows
    min_width = Column(Integer, default=2, nullable=False)
    min_height = Column(Integer, default=2, nullable=False)
    max_width = Column(Integer, nullable=True)
    max_height = Column(Integer, nullable=True)
    
    # Display Settings
    show_title = Column(Boolean, default=True, nullable=False)
    show_border = Column(Boolean, default=True, nullable=False)
    show_legend = Column(Boolean, default=True, nullable=False)
    show_export = Column(Boolean, default=True, nullable=False)
    
    # Styling
    background_color = Column(String(7), nullable=True)
    border_color = Column(String(7), nullable=True)
    text_color = Column(String(7), nullable=True)
    
    # Behavior
    is_resizable = Column(Boolean, default=True, nullable=False)
    is_draggable = Column(Boolean, default=True, nullable=False)
    auto_refresh = Column(Boolean, default=True, nullable=False)
    refresh_interval = Column(Integer, nullable=True)  # Override dashboard default
    
    # Data and Cache
    cached_data = Column(JSONB, nullable=True)  # Cached widget data
    last_data_update = Column(DateTime(timezone=True), nullable=True)
    
    # Sorting and Grouping
    sort_order = Column(Integer, default=0, nullable=False)
    group_name = Column(String(100), nullable=True, index=True)
    
    # Status
    is_visible = Column(Boolean, default=True, nullable=False)
    is_locked = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    dashboard = relationship("Dashboard", back_populates="widgets")
    
    def __repr__(self) -> str:
        return f"<DashboardWidget(id={self.id}, type={self.widget_type}, dashboard_id={self.dashboard_id})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert widget to dictionary."""
        return {
            "id": str(self.id),
            "dashboard_id": str(self.dashboard_id),
            "widget_type": self.widget_type,
            "title": self.title,
            "subtitle": self.subtitle,
            "metric_names": self.metric_names,
            "data_source": self.data_source,
            "query_config": self.query_config,
            "chart_type": self.chart_type,
            "chart_config": self.chart_config,
            "position": {
                "x": self.position_x,
                "y": self.position_y,
                "width": self.width,
                "height": self.height,
            },
            "constraints": {
                "min_width": self.min_width,
                "min_height": self.min_height,
                "max_width": self.max_width,
                "max_height": self.max_height,
            },
            "display_settings": {
                "show_title": self.show_title,
                "show_border": self.show_border,
                "show_legend": self.show_legend,
                "show_export": self.show_export,
            },
            "styling": {
                "background_color": self.background_color,
                "border_color": self.border_color,
                "text_color": self.text_color,
            },
            "behavior": {
                "is_resizable": self.is_resizable,
                "is_draggable": self.is_draggable,
                "auto_refresh": self.auto_refresh,
                "refresh_interval": self.refresh_interval,
            },
            "sort_order": self.sort_order,
            "group_name": self.group_name,
            "is_visible": self.is_visible,
            "is_locked": self.is_locked,
            "last_data_update": self.last_data_update.isoformat() if self.last_data_update else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class DashboardAccess(Base):
    """Shared access control for dashboards."""
    
    __tablename__ = "dashboard_access"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Access Configuration
    dashboard_id = Column(UUID(as_uuid=True), ForeignKey("dashboards.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    
    # Access Control
    access_type = Column(String(20), default="view", nullable=False)  # view, edit, admin
    shared_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Public Sharing
    is_public_link = Column(Boolean, default=False, nullable=False)
    public_token = Column(String(255), nullable=True, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Usage Tracking
    access_count = Column(Integer, default=0, nullable=False)
    last_accessed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    dashboard = relationship("Dashboard", back_populates="shared_access")
    user = relationship("User", foreign_keys=[user_id])
    shared_by = relationship("User", foreign_keys=[shared_by_user_id])
    
    def __repr__(self) -> str:
        return f"<DashboardAccess(id={self.id}, dashboard_id={self.dashboard_id}, access_type={self.access_type})>"


# Optimized indexes for dashboard queries
Index('idx_dashboard_owner_status', Dashboard.owner_id, Dashboard.status)
Index('idx_dashboard_public_status', Dashboard.is_public, Dashboard.status)
Index('idx_widget_dashboard_position', DashboardWidget.dashboard_id, DashboardWidget.position_x, DashboardWidget.position_y)
Index('idx_widget_dashboard_order', DashboardWidget.dashboard_id, DashboardWidget.sort_order)
Index('idx_access_dashboard_user', DashboardAccess.dashboard_id, DashboardAccess.user_id)
Index('idx_access_public_token', DashboardAccess.public_token)
