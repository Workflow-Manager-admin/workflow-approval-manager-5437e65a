from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Enum,
    Text,
    func,
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import JSONB
import enum

Base = declarative_base()


class StepTypeEnum(str, enum.Enum):
    SEQUENTIAL = "SEQUENTIAL"
    PARALLEL = "PARALLEL"


class InstanceStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"


class StepStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SKIPPED = "SKIPPED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class ApprovalWorkflowConfig(Base):
    __tablename__ = "approval_workflow_config"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text)
    blocks = relationship("ApprovalWorkflowBlock", back_populates="workflow_config")
    step_configs = relationship("ApprovalWorkflowStepConfig", back_populates="workflow_config")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ApprovalWorkflowStepConfig(Base):
    __tablename__ = "approval_workflow_step_config"
    id = Column(Integer, primary_key=True, index=True)
    approval_workflow_config_id = Column(Integer, ForeignKey("approval_workflow_config.id"))
    name = Column(String, nullable=False)
    description = Column(Text)
    step_type = Column(Enum(StepTypeEnum), nullable=False, default=StepTypeEnum.SEQUENTIAL)
    order = Column(Integer, nullable=False)
    config_json = Column(JSONB)
    workflow_config = relationship("ApprovalWorkflowConfig", back_populates="step_configs")
    blocks = relationship("ApprovalWorkflowBlock", back_populates="step_config")


class ApprovalWorkflowBlock(Base):
    __tablename__ = "approval_workflow_block"
    id = Column(Integer, primary_key=True, index=True)
    approval_workflow_config_id = Column(Integer, ForeignKey("approval_workflow_config.id"))
    approval_workflow_step_config_id = Column(Integer, ForeignKey("approval_workflow_step_config.id"), nullable=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    business_rule = Column(JSONB, nullable=True)  # JSON representation of rule
    config_json = Column(JSONB, nullable=True)
    workflow_config = relationship("ApprovalWorkflowConfig", back_populates="blocks")
    step_config = relationship("ApprovalWorkflowStepConfig", back_populates="blocks")


class ApprovalWorkflowInstance(Base):
    __tablename__ = "approval_workflow_instance"
    id = Column(Integer, primary_key=True, index=True)
    approval_workflow_config_id = Column(Integer, ForeignKey("approval_workflow_config.id"))
    status = Column(Enum(InstanceStatusEnum), default=InstanceStatusEnum.PENDING)
    initiator = Column(String)
    context_data = Column(JSONB, nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    steps = relationship("ApprovalWorkflowInstanceStep", back_populates="instance")


class ApprovalWorkflowInstanceStep(Base):
    __tablename__ = "approval_workflow_instance_step"
    id = Column(Integer, primary_key=True, index=True)
    approval_workflow_instance_id = Column(Integer, ForeignKey("approval_workflow_instance.id"))
    approval_workflow_step_config_id = Column(Integer, ForeignKey("approval_workflow_step_config.id"))
    status = Column(Enum(StepStatusEnum), default=StepStatusEnum.PENDING)
    # Remove 'approver' field; use one-to-many with new approver table
    actioned_at = Column(DateTime(timezone=True), nullable=True)
    comments = Column(Text, nullable=True)
    instance = relationship("ApprovalWorkflowInstance", back_populates="steps")
    approvers = relationship("ApprovalWorkflowInstanceStepApprover", back_populates="step", cascade="all, delete-orphan")
    # Do not include relationship to config for brevity


class ApprovalWorkflowInstanceStepApprover(Base):
    """
    PUBLIC_INTERFACE

    New model representing an approver (user) assigned to a specific instance step.
    Tracks per-approver status/comments/actioned_at for "any" or "all" approval logic.
    """
    __tablename__ = "approval_workflow_instance_step_approver"
    id = Column(Integer, primary_key=True, index=True)
    instance_step_id = Column(Integer, ForeignKey("approval_workflow_instance_step.id"), nullable=False)
    approver = Column(String, nullable=False)  # user id or email
    status = Column(Enum(StepStatusEnum), default=StepStatusEnum.PENDING, nullable=False)
    comments = Column(Text, nullable=True)
    actioned_at = Column(DateTime(timezone=True), nullable=True)

    step = relationship("ApprovalWorkflowInstanceStep", back_populates="approvers")
