from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
import enum

# --- ENUMS ---

# PUBLIC_INTERFACE
class StepTypeEnum(str, enum.Enum):
    SEQUENTIAL = "SEQUENTIAL"
    PARALLEL = "PARALLEL"

# PUBLIC_INTERFACE
class InstanceStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"

# PUBLIC_INTERFACE
class StepStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SKIPPED = "SKIPPED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

# --- SCHEMAS ---

# PUBLIC_INTERFACE
class ApprovalWorkflowBlockBase(BaseModel):
    name: str
    description: Optional[str] = None
    business_rule: Optional[dict] = Field(default=None, description="JSON describing business rule")
    config_json: Optional[dict] = None

# PUBLIC_INTERFACE
class ApprovalWorkflowBlockCreate(ApprovalWorkflowBlockBase):
    approval_workflow_config_id: int
    approval_workflow_step_config_id: Optional[int]

# PUBLIC_INTERFACE
class ApprovalWorkflowBlockRead(ApprovalWorkflowBlockBase):
    id: int
    approval_workflow_config_id: int
    approval_workflow_step_config_id: Optional[int]

    class Config:
        from_attributes = True

# PUBLIC_INTERFACE
class ApprovalWorkflowConfigBase(BaseModel):
    name: str
    description: Optional[str] = None

# PUBLIC_INTERFACE
class ApprovalWorkflowConfigCreate(ApprovalWorkflowConfigBase):
    pass

# PUBLIC_INTERFACE
class ApprovalWorkflowConfigRead(ApprovalWorkflowConfigBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# PUBLIC_INTERFACE
class ApprovalWorkflowStepConfigBase(BaseModel):
    name: str
    description: Optional[str] = None
    step_type: StepTypeEnum = Field(..., description="Step type: SEQUENTIAL or PARALLEL")
    order: int
    config_json: Optional[dict] = None

# PUBLIC_INTERFACE
class ApprovalWorkflowStepConfigCreate(ApprovalWorkflowStepConfigBase):
    approval_workflow_config_id: int

# PUBLIC_INTERFACE
class ApprovalWorkflowStepConfigRead(ApprovalWorkflowStepConfigBase):
    id: int
    approval_workflow_config_id: int

    class Config:
        from_attributes = True

# PUBLIC_INTERFACE
class ApprovalWorkflowInstanceBase(BaseModel):
    approval_workflow_config_id: int
    initiator: str
    context_data: Optional[dict] = None

# PUBLIC_INTERFACE
class ApprovalWorkflowInstanceCreate(ApprovalWorkflowInstanceBase):
    pass

# PUBLIC_INTERFACE
class ApprovalWorkflowInstanceRead(ApprovalWorkflowInstanceBase):
    id: int
    status: InstanceStatusEnum
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# PUBLIC_INTERFACE
class ApprovalWorkflowInstanceStepBase(BaseModel):
    approval_workflow_instance_id: int
    approval_workflow_step_config_id: int
    approver: str
    comments: Optional[str] = None

# PUBLIC_INTERFACE
class ApprovalWorkflowInstanceStepCreate(ApprovalWorkflowInstanceStepBase):
    pass

# PUBLIC_INTERFACE
class ApprovalWorkflowInstanceStepRead(ApprovalWorkflowInstanceStepBase):
    id: int
    status: StepStatusEnum
    actioned_at: Optional[datetime] = None

    class Config:
        from_attributes = True

