"""
Data models for Training Plan Nomination System.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class NominationStatus(Enum):
    """Status of a training nomination."""
    PENDING = "pending"
    NOTIFIED = "notified"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    COMPLETED = "completed"


class TrainingPriority(Enum):
    """Priority level for training."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Employee:
    """Employee data model."""
    id: str
    name: str
    email: str
    department: str
    role: str
    manager_id: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'department': self.department,
            'role': self.role,
            'manager_id': self.manager_id
        }


@dataclass
class AreaOfWork:
    """Area of Work (AOW) within a training plan."""
    id: str
    name: str
    description: str
    skills: List[str]
    duration_hours: int
    resources: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'skills': self.skills,
            'duration_hours': self.duration_hours,
            'resources': self.resources,
            'prerequisites': self.prerequisites
        }


@dataclass
class TrainingPlan:
    """Training plan containing multiple areas of work."""
    id: str
    name: str
    description: str
    areas_of_work: List[AreaOfWork]
    created_by: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'areas_of_work': [aow.to_dict() for aow in self.areas_of_work],
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active
        }

    def get_total_duration(self) -> int:
        """Get total duration of all areas of work."""
        return sum(aow.duration_hours for aow in self.areas_of_work)


@dataclass
class Nomination:
    """Training nomination for an employee."""
    id: str
    training_plan_id: str
    aow_id: str
    employee_id: str
    nominated_by: str
    status: NominationStatus = NominationStatus.PENDING
    priority: TrainingPriority = TrainingPriority.MEDIUM
    nominated_at: datetime = field(default_factory=datetime.now)
    notified_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    notes: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'training_plan_id': self.training_plan_id,
            'aow_id': self.aow_id,
            'employee_id': self.employee_id,
            'nominated_by': self.nominated_by,
            'status': self.status.value,
            'priority': self.priority.value,
            'nominated_at': self.nominated_at.isoformat(),
            'notified_at': self.notified_at.isoformat() if self.notified_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'notes': self.notes
        }


@dataclass
class EmailNotification:
    """Email notification record."""
    id: str
    recipient_email: str
    recipient_name: str
    subject: str
    body: str
    nomination_id: str
    sent_at: datetime = field(default_factory=datetime.now)
    is_sent: bool = False
    error_message: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'recipient_email': self.recipient_email,
            'recipient_name': self.recipient_name,
            'subject': self.subject,
            'body': self.body,
            'nomination_id': self.nomination_id,
            'sent_at': self.sent_at.isoformat(),
            'is_sent': self.is_sent,
            'error_message': self.error_message
        }
