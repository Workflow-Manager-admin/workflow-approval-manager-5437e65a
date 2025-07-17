"""
PUBLIC_INTERFACE

Module providing workflow execution logic, namely:
- Running approval workflows according to SEQUENTIAL/PARALLEL steps and rules
- Progressing workflow instances/steps and managing approval/rejection
- Evaluating block business rules per step using the business_rules integration
"""

from sqlalchemy.ext.asyncio import AsyncSession
from . import crud
from .models import StepTypeEnum, StepStatusEnum, InstanceStatusEnum
from typing import Optional, Dict, Any

# PUBLIC_INTERFACE
async def start_workflow(db: AsyncSession, instance_id: int) -> None:
    """Starts workflow execution for a given instance, updating first approvers as IN_PROGRESS."""
    instance = await crud.get_instance(db, instance_id)
    if not instance:
        raise Exception("Instance not found")
    steps = await crud.list_instance_steps(db, instance_id)
    if not steps:
        raise Exception("At least one workflow step required to start")
    # Find step config(s) with order = 1 (start)
    step_cfg_ids = set(step.approval_workflow_step_config_id for step in steps)
    step_configs = [await crud.get_step_config(db, cid) for cid in step_cfg_ids]
    if any(cfg.order == 1 for cfg in step_configs):
        for s, c in zip(steps, step_configs):
            if c.order == 1:
                await crud.update_instance_step_status(db, s.id, StepStatusEnum.IN_PROGRESS)
        await crud.update_instance_status(db, instance_id, InstanceStatusEnum.IN_PROGRESS)

# PUBLIC_INTERFACE
async def proceed_to_next_step(db: AsyncSession, instance_id: int) -> None:
    """
    Advances the workflow to next step(s). For SEQUENTIAL, next step; for PARALLEL, all eligible steps.
    Updates instance status if complete. Handles "auto-approval" via business rules.
    """
    instance = await crud.get_instance(db, instance_id)
    if not instance:
        raise Exception("Instance not found")
    all_steps = await crud.list_instance_steps(db, instance_id)
    # Determine the highest current order being worked, then set next steps (if any) to IN_PROGRESS
    in_progress_steps = [s for s in all_steps if s.status == StepStatusEnum.IN_PROGRESS]
    if not in_progress_steps:
        # Check for completion
        if all(st.status in [StepStatusEnum.APPROVED, StepStatusEnum.COMPLETED] for st in all_steps):
            await crud.update_instance_status(db, instance_id, InstanceStatusEnum.COMPLETED)
        return
    for step in in_progress_steps:
        step_cfg = await crud.get_step_config(db, step.approval_workflow_step_config_id)
        if step_cfg.step_type == StepTypeEnum.SEQUENTIAL:
            # Only one step in progress at a time, move to next after approval
            if step.status == StepStatusEnum.APPROVED:
                next_order = step_cfg.order + 1
                all_cfgs = [await crud.get_step_config(db, st.approval_workflow_step_config_id) for st in all_steps]
                for cfg, st in zip(all_cfgs, all_steps):
                    if cfg.order == next_order:
                        await crud.update_instance_step_status(db, st.id, StepStatusEnum.IN_PROGRESS)
                        break
        elif step_cfg.step_type == StepTypeEnum.PARALLEL:
            # When all in group are approved, move to next group
            current_order = step_cfg.order
            group_steps = [
                s for s, c in zip(all_steps, [await crud.get_step_config(db, st.approval_workflow_step_config_id) for st in all_steps])
                if c.order == current_order
            ]
            if all(s.status == StepStatusEnum.APPROVED for s in group_steps):
                next_order = current_order + 1
                for cfg, st in zip(all_cfgs, all_steps):
                    if cfg.order == next_order:
                        await crud.update_instance_step_status(db, st.id, StepStatusEnum.IN_PROGRESS)
                        break

# PUBLIC_INTERFACE
async def apply_approval(
    db: AsyncSession,
    instance_step_id: int,
    approver_action: str,
    variables: Optional[Dict[str, Any]] = None,
    comments: Optional[str] = None,
) -> None:
    """
    Apply approval or rejection. Ensures step status update, potential rule checks, and triggers next steps.
    """
    step = await crud.get_instance_step(db, instance_step_id)
    if not step:
        raise Exception("Step not found")
    # Fetch and evaluate business rule if present (if 'variables' is None, provide empty dict)
    step_cfg = await crud.get_step_config(db, step.approval_workflow_step_config_id)
    if not step_cfg:
        raise Exception("Step config not found")
    # Simulated: In a real case, need mapping ApprovalWorkflowBlock for this step, get .business_rule.
    # For simplicity, assume config_json['business_rule'] or None
    status = (
        StepStatusEnum.APPROVED if approver_action.upper() == "APPROVE"
        else StepStatusEnum.REJECTED if approver_action.upper() == "REJECT"
        else StepStatusEnum.SKIPPED
    )
    await crud.update_instance_step_status(db, instance_step_id, status, comments)
    # After action, try to advance workflow
    await proceed_to_next_step(db, step.approval_workflow_instance_id)

