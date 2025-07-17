from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List, Optional

from .models import (
    ApprovalWorkflowConfig,
    ApprovalWorkflowStepConfig,
    ApprovalWorkflowBlock,
    ApprovalWorkflowInstance,
    ApprovalWorkflowInstanceStep,
)
from .schemas import (
    ApprovalWorkflowConfigCreate,
    ApprovalWorkflowStepConfigCreate,
    ApprovalWorkflowBlockCreate,
    ApprovalWorkflowInstanceCreate,
    ApprovalWorkflowInstanceStepCreate,
    InstanceStatusEnum,
    StepStatusEnum,
)

# --- CRUD for ApprovalWorkflowConfig ---
# PUBLIC_INTERFACE
async def create_workflow_config(db: AsyncSession, obj_in: ApprovalWorkflowConfigCreate) -> ApprovalWorkflowConfig:
    db_obj = ApprovalWorkflowConfig(**obj_in.dict())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

# PUBLIC_INTERFACE
async def get_workflow_config(db: AsyncSession, config_id: int) -> Optional[ApprovalWorkflowConfig]:
    q = await db.execute(select(ApprovalWorkflowConfig).where(ApprovalWorkflowConfig.id == config_id))
    return q.scalar_one_or_none()

# PUBLIC_INTERFACE
async def list_workflow_configs(db: AsyncSession) -> List[ApprovalWorkflowConfig]:
    q = await db.execute(select(ApprovalWorkflowConfig))
    return q.scalars().all()

# PUBLIC_INTERFACE
async def update_workflow_config(db: AsyncSession, config_id: int, obj_in: ApprovalWorkflowConfigCreate) -> Optional[ApprovalWorkflowConfig]:
    q = await db.execute(
        update(ApprovalWorkflowConfig)
        .where(ApprovalWorkflowConfig.id == config_id)
        .values(**obj_in.dict())
        .returning(ApprovalWorkflowConfig)
    )
    await db.commit()
    return q.fetchone()

# PUBLIC_INTERFACE
async def delete_workflow_config(db: AsyncSession, config_id: int) -> int:
    q = await db.execute(delete(ApprovalWorkflowConfig).where(ApprovalWorkflowConfig.id == config_id))
    await db.commit()
    return q.rowcount

# --- CRUD for ApprovalWorkflowStepConfig ---
# PUBLIC_INTERFACE
async def create_step_config(db: AsyncSession, obj_in: ApprovalWorkflowStepConfigCreate) -> ApprovalWorkflowStepConfig:
    db_obj = ApprovalWorkflowStepConfig(**obj_in.dict())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

# PUBLIC_INTERFACE
async def get_step_config(db: AsyncSession, step_config_id: int) -> Optional[ApprovalWorkflowStepConfig]:
    q = await db.execute(select(ApprovalWorkflowStepConfig).where(ApprovalWorkflowStepConfig.id == step_config_id))
    return q.scalar_one_or_none()

# PUBLIC_INTERFACE
async def list_step_configs(db: AsyncSession, workflow_config_id: int) -> List[ApprovalWorkflowStepConfig]:
    q = await db.execute(select(ApprovalWorkflowStepConfig).where(ApprovalWorkflowStepConfig.approval_workflow_config_id == workflow_config_id))
    return q.scalars().all()

# PUBLIC_INTERFACE
async def update_step_config(db: AsyncSession, step_config_id: int, obj_in: ApprovalWorkflowStepConfigCreate) -> Optional[ApprovalWorkflowStepConfig]:
    q = await db.execute(
        update(ApprovalWorkflowStepConfig)
        .where(ApprovalWorkflowStepConfig.id == step_config_id)
        .values(**obj_in.dict())
        .returning(ApprovalWorkflowStepConfig)
    )
    await db.commit()
    return q.fetchone()

# PUBLIC_INTERFACE
async def delete_step_config(db: AsyncSession, step_config_id: int) -> int:
    q = await db.execute(delete(ApprovalWorkflowStepConfig).where(ApprovalWorkflowStepConfig.id == step_config_id))
    await db.commit()
    return q.rowcount

# --- CRUD for ApprovalWorkflowBlock ---
# PUBLIC_INTERFACE
async def create_block(db: AsyncSession, obj_in: ApprovalWorkflowBlockCreate) -> ApprovalWorkflowBlock:
    db_obj = ApprovalWorkflowBlock(**obj_in.dict())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

# PUBLIC_INTERFACE
async def get_block(db: AsyncSession, block_id: int) -> Optional[ApprovalWorkflowBlock]:
    q = await db.execute(select(ApprovalWorkflowBlock).where(ApprovalWorkflowBlock.id == block_id))
    return q.scalar_one_or_none()

# PUBLIC_INTERFACE
async def list_blocks(db: AsyncSession, workflow_config_id: Optional[int]=None) -> List[ApprovalWorkflowBlock]:
    q = select(ApprovalWorkflowBlock)
    if workflow_config_id:
        q = q.where(ApprovalWorkflowBlock.approval_workflow_config_id == workflow_config_id)
    result = await db.execute(q)
    return result.scalars().all()

# PUBLIC_INTERFACE
async def update_block(db: AsyncSession, block_id: int, obj_in: ApprovalWorkflowBlockCreate) -> Optional[ApprovalWorkflowBlock]:
    q = await db.execute(
        update(ApprovalWorkflowBlock)
        .where(ApprovalWorkflowBlock.id == block_id)
        .values(**obj_in.dict())
        .returning(ApprovalWorkflowBlock)
    )
    await db.commit()
    return q.fetchone()

# PUBLIC_INTERFACE
async def delete_block(db: AsyncSession, block_id: int) -> int:
    q = await db.execute(delete(ApprovalWorkflowBlock).where(ApprovalWorkflowBlock.id == block_id))
    await db.commit()
    return q.rowcount


# --- CRUD for ApprovalWorkflowInstance ---
# PUBLIC_INTERFACE
async def create_instance(db: AsyncSession, obj_in: ApprovalWorkflowInstanceCreate) -> ApprovalWorkflowInstance:
    db_obj = ApprovalWorkflowInstance(**obj_in.dict())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

# PUBLIC_INTERFACE
async def get_instance(db: AsyncSession, instance_id: int) -> Optional[ApprovalWorkflowInstance]:
    q = await db.execute(select(ApprovalWorkflowInstance).where(ApprovalWorkflowInstance.id == instance_id))
    return q.scalar_one_or_none()

# PUBLIC_INTERFACE
async def list_instances(db: AsyncSession, workflow_config_id: Optional[int]=None) -> List[ApprovalWorkflowInstance]:
    q = select(ApprovalWorkflowInstance)
    if workflow_config_id:
        q = q.where(ApprovalWorkflowInstance.approval_workflow_config_id == workflow_config_id)
    result = await db.execute(q)
    return result.scalars().all()

# PUBLIC_INTERFACE
async def update_instance_status(db: AsyncSession, instance_id: int, new_status: InstanceStatusEnum) -> Optional[ApprovalWorkflowInstance]:
    q = await db.execute(
        update(ApprovalWorkflowInstance)
        .where(ApprovalWorkflowInstance.id == instance_id)
        .values(status=new_status)
        .returning(ApprovalWorkflowInstance)
    )
    await db.commit()
    return q.fetchone()

# PUBLIC_INTERFACE
async def delete_instance(db: AsyncSession, instance_id: int) -> int:
    q = await db.execute(delete(ApprovalWorkflowInstance).where(ApprovalWorkflowInstance.id == instance_id))
    await db.commit()
    return q.rowcount

# --- CRUD for ApprovalWorkflowInstanceStep ---
# PUBLIC_INTERFACE
async def create_instance_step(db: AsyncSession, obj_in: ApprovalWorkflowInstanceStepCreate) -> ApprovalWorkflowInstanceStep:
    db_obj = ApprovalWorkflowInstanceStep(**obj_in.dict())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

# PUBLIC_INTERFACE
async def get_instance_step(db: AsyncSession, instance_step_id: int) -> Optional[ApprovalWorkflowInstanceStep]:
    q = await db.execute(select(ApprovalWorkflowInstanceStep).where(ApprovalWorkflowInstanceStep.id == instance_step_id))
    return q.scalar_one_or_none()

# PUBLIC_INTERFACE
async def list_instance_steps(db: AsyncSession, instance_id: int) -> List[ApprovalWorkflowInstanceStep]:
    q = await db.execute(select(ApprovalWorkflowInstanceStep).where(ApprovalWorkflowInstanceStep.approval_workflow_instance_id == instance_id))
    return q.scalars().all()


# PUBLIC_INTERFACE
async def update_instance_step_status(db: AsyncSession, instance_step_id: int, new_status: StepStatusEnum, comments: Optional[str]=None) -> Optional[ApprovalWorkflowInstanceStep]:
    values = {"status": new_status}
    if comments:
        values["comments"] = comments
    q = await db.execute(
        update(ApprovalWorkflowInstanceStep)
        .where(ApprovalWorkflowInstanceStep.id == instance_step_id)
        .values(**values)
        .returning(ApprovalWorkflowInstanceStep)
    )
    await db.commit()
    return q.fetchone()

# PUBLIC_INTERFACE
async def delete_instance_step(db: AsyncSession, instance_step_id: int) -> int:
    q = await db.execute(delete(ApprovalWorkflowInstanceStep).where(ApprovalWorkflowInstanceStep.id == instance_step_id))
    await db.commit()
    return q.rowcount

