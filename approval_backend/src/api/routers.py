from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from .db import get_db
from . import schemas, crud, workflow_logic

router = APIRouter()


# --- ApprovalWorkflowConfig APIs ---
@router.post("/workflow-configs/", response_model=schemas.ApprovalWorkflowConfigRead, tags=["Approval Workflow Config"])
# PUBLIC_INTERFACE
async def create_workflow_config(obj: schemas.ApprovalWorkflowConfigCreate, db: AsyncSession = Depends(get_db)):
    """Create new approval workflow configuration."""
    return await crud.create_workflow_config(db, obj)

@router.get("/workflow-configs/", response_model=List[schemas.ApprovalWorkflowConfigRead], tags=["Approval Workflow Config"])
# PUBLIC_INTERFACE
async def list_workflow_configs(db: AsyncSession = Depends(get_db)):
    """List all approval workflow configs."""
    return await crud.list_workflow_configs(db)

@router.get("/workflow-configs/{config_id}/", response_model=schemas.ApprovalWorkflowConfigRead, tags=["Approval Workflow Config"])
# PUBLIC_INTERFACE
async def get_workflow_config(config_id: int, db: AsyncSession = Depends(get_db)):
    """Get a workflow config by ID."""
    obj = await crud.get_workflow_config(db, config_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Workflow config not found")
    return obj

@router.put("/workflow-configs/{config_id}/", response_model=schemas.ApprovalWorkflowConfigRead, tags=["Approval Workflow Config"])
# PUBLIC_INTERFACE
async def update_workflow_config(config_id: int, obj: schemas.ApprovalWorkflowConfigCreate, db: AsyncSession = Depends(get_db)):
    """Update a workflow config."""
    updated = await crud.update_workflow_config(db, config_id, obj)
    if not updated:
        raise HTTPException(status_code=404, detail="Workflow config not found")
    return updated

@router.delete("/workflow-configs/{config_id}/", tags=["Approval Workflow Config"])
# PUBLIC_INTERFACE
async def delete_workflow_config(config_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a workflow config."""
    count = await crud.delete_workflow_config(db, config_id)
    if count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"deleted": count}

# --- ApprovalWorkflowStepConfig APIs ---
@router.post("/step-configs/", response_model=schemas.ApprovalWorkflowStepConfigRead, tags=["Approval Workflow Step Config"])
# PUBLIC_INTERFACE
async def create_step_config(obj: schemas.ApprovalWorkflowStepConfigCreate, db: AsyncSession = Depends(get_db)):
    """Create step config."""
    return await crud.create_step_config(db, obj)

@router.get("/step-configs/", response_model=List[schemas.ApprovalWorkflowStepConfigRead], tags=["Approval Workflow Step Config"])
# PUBLIC_INTERFACE
async def list_step_configs(workflow_config_id: int, db: AsyncSession = Depends(get_db)):
    """List step configs for a workflow."""
    return await crud.list_step_configs(db, workflow_config_id)

@router.get("/step-configs/{step_config_id}/", response_model=schemas.ApprovalWorkflowStepConfigRead, tags=["Approval Workflow Step Config"])
# PUBLIC_INTERFACE
async def get_step_config(step_config_id: int, db: AsyncSession = Depends(get_db)):
    obj = await crud.get_step_config(db, step_config_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    return obj

@router.put("/step-configs/{step_config_id}/", response_model=schemas.ApprovalWorkflowStepConfigRead, tags=["Approval Workflow Step Config"])
# PUBLIC_INTERFACE
async def update_step_config(step_config_id: int, obj: schemas.ApprovalWorkflowStepConfigCreate, db: AsyncSession = Depends(get_db)):
    updated = await crud.update_step_config(db, step_config_id, obj)
    if not updated:
        raise HTTPException(status_code=404, detail="Not found")
    return updated

@router.delete("/step-configs/{step_config_id}/", tags=["Approval Workflow Step Config"])
# PUBLIC_INTERFACE
async def delete_step_config(step_config_id: int, db: AsyncSession = Depends(get_db)):
    count = await crud.delete_step_config(db, step_config_id)
    if count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"deleted": count}


# --- ApprovalWorkflowBlock APIs ---
@router.post("/blocks/", response_model=schemas.ApprovalWorkflowBlockRead, tags=["Approval Workflow Block"])
# PUBLIC_INTERFACE
async def create_block(obj: schemas.ApprovalWorkflowBlockCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_block(db, obj)

@router.get("/blocks/", response_model=List[schemas.ApprovalWorkflowBlockRead], tags=["Approval Workflow Block"])
# PUBLIC_INTERFACE
async def list_blocks(workflow_config_id: Optional[int]=None, db: AsyncSession = Depends(get_db)):
    return await crud.list_blocks(db, workflow_config_id)

@router.get("/blocks/{block_id}/", response_model=schemas.ApprovalWorkflowBlockRead, tags=["Approval Workflow Block"])
# PUBLIC_INTERFACE
async def get_block(block_id: int, db: AsyncSession = Depends(get_db)):
    obj = await crud.get_block(db, block_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    return obj

@router.put("/blocks/{block_id}/", response_model=schemas.ApprovalWorkflowBlockRead, tags=["Approval Workflow Block"])
# PUBLIC_INTERFACE
async def update_block(block_id: int, obj: schemas.ApprovalWorkflowBlockCreate, db: AsyncSession = Depends(get_db)):
    updated = await crud.update_block(db, block_id, obj)
    if not updated:
        raise HTTPException(status_code=404, detail="Not found")
    return updated

@router.delete("/blocks/{block_id}/", tags=["Approval Workflow Block"])
# PUBLIC_INTERFACE
async def delete_block(block_id: int, db: AsyncSession = Depends(get_db)):
    count = await crud.delete_block(db, block_id)
    if count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"deleted": count}

# --- ApprovalWorkflowInstance APIs ---
@router.post("/instances/", response_model=schemas.ApprovalWorkflowInstanceRead, tags=["Approval Workflow Instance"])
# PUBLIC_INTERFACE
async def create_instance(obj: schemas.ApprovalWorkflowInstanceCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_instance(db, obj)

@router.get("/instances/", response_model=List[schemas.ApprovalWorkflowInstanceRead], tags=["Approval Workflow Instance"])
# PUBLIC_INTERFACE
async def list_instances(workflow_config_id: Optional[int]=None, db: AsyncSession = Depends(get_db)):
    return await crud.list_instances(db, workflow_config_id)

@router.get("/instances/{instance_id}/", response_model=schemas.ApprovalWorkflowInstanceRead, tags=["Approval Workflow Instance"])
# PUBLIC_INTERFACE
async def get_instance(instance_id: int, db: AsyncSession = Depends(get_db)):
    obj = await crud.get_instance(db, instance_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    return obj

@router.put("/instances/{instance_id}/status/", tags=["Approval Workflow Instance"])
# PUBLIC_INTERFACE
async def update_instance_status(instance_id: int, new_status: schemas.InstanceStatusEnum, db: AsyncSession = Depends(get_db)):
    updated = await crud.update_instance_status(db, instance_id, new_status)
    if not updated:
        raise HTTPException(status_code=404, detail="Not found")
    return updated

@router.delete("/instances/{instance_id}/", tags=["Approval Workflow Instance"])
# PUBLIC_INTERFACE
async def delete_instance(instance_id: int, db: AsyncSession = Depends(get_db)):
    count = await crud.delete_instance(db, instance_id)
    if count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"deleted": count}

# --- ApprovalWorkflowInstanceStep APIs ---
@router.post("/instance-steps/", response_model=schemas.ApprovalWorkflowInstanceStepRead, tags=["Approval Workflow Instance Step"])
# PUBLIC_INTERFACE
async def create_instance_step(obj: schemas.ApprovalWorkflowInstanceStepCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_instance_step(db, obj)

@router.get("/instance-steps/", response_model=List[schemas.ApprovalWorkflowInstanceStepRead], tags=["Approval Workflow Instance Step"])
# PUBLIC_INTERFACE
async def list_instance_steps(instance_id: int, db: AsyncSession = Depends(get_db)):
    return await crud.list_instance_steps(db, instance_id)

@router.get("/instance-steps/{instance_step_id}/", response_model=schemas.ApprovalWorkflowInstanceStepRead, tags=["Approval Workflow Instance Step"])
# PUBLIC_INTERFACE
async def get_instance_step(instance_step_id: int, db: AsyncSession = Depends(get_db)):
    obj = await crud.get_instance_step(db, instance_step_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    return obj

@router.put("/instance-steps/{instance_step_id}/status/", tags=["Approval Workflow Instance Step"])
# PUBLIC_INTERFACE
async def update_instance_step_status(instance_step_id: int, new_status: schemas.StepStatusEnum, comments: Optional[str]=None, db: AsyncSession = Depends(get_db)):
    updated = await crud.update_instance_step_status(db, instance_step_id, new_status, comments)
    if not updated:
        raise HTTPException(status_code=404, detail="Not found")
    return updated

@router.delete("/instance-steps/{instance_step_id}/", tags=["Approval Workflow Instance Step"])
# PUBLIC_INTERFACE
async def delete_instance_step(instance_step_id: int, db: AsyncSession = Depends(get_db)):
    count = await crud.delete_instance_step(db, instance_step_id)
    if count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"deleted": count}

# --- Workflow Triggers ---
@router.post("/instances/{instance_id}/start/", tags=["Workflow Execution"])
# PUBLIC_INTERFACE
async def start_workflow(instance_id: int, db: AsyncSession = Depends(get_db)):
    """Explicitly start a workflow instance."""
    await workflow_logic.start_workflow(db, instance_id)
    return {"started": True}

@router.post("/instance-steps/{instance_step_id}/action/", tags=["Workflow Execution"])
# PUBLIC_INTERFACE
async def approve_or_reject_step(instance_step_id: int, action: str, comments: Optional[str]=None, db: AsyncSession = Depends(get_db)):
    """Approve/reject/skip a workflow step."""
    await workflow_logic.apply_approval(db, instance_step_id, action, comments=comments)
    return {"updated": True}

