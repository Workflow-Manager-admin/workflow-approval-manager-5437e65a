"""
PUBLIC_INTERFACE

Module providing workflow execution logic, namely:
- Running approval workflows according to SEQUENTIAL/PARALLEL steps and rules
- Progressing workflow instances/steps and managing approval/rejection
- Evaluating block business rules per step using the business_rules integration
"""

from sqlalchemy.ext.asyncio import AsyncSession
from . import crud
from .models import StepStatusEnum, InstanceStatusEnum, ApprovalWorkflowInstanceStepApprover
from typing import Optional, Dict, Any
from sqlalchemy import select
import datetime

async def _get_step_approvers_from_config(step_config):
    """
    Utility: Get list of approvers for this step config. Assumes 'approvers' list in config_json.
    """
    config = step_config.config_json or {}
    return config.get("approvers", [])

async def _get_any_one_can_approve_flag(step_config):
    """
    Utility: Returns True if the config_json has 'any_one_can_approve' set truthy, else False (default: False).
    """
    config = step_config.config_json or {}
    return bool(config.get("any_one_can_approve", False))

async def _create_instance_step_approvers(db, step, step_config):
    """
    On step IN_PROGRESS, create a record for each assigned approver for the step.
    """
    approvers = await _get_step_approvers_from_config(step_config)
    # Query existing assigned to avoid duplicates.
    existing = getattr(step, "approvers", [])
    existing_approver_set = set(a.approver for a in existing)
    new_objs = []
    for approver_id in approvers:
        if approver_id and approver_id not in existing_approver_set:
            obj = ApprovalWorkflowInstanceStepApprover(
                instance_step_id=step.id,
                approver=approver_id,
                status=StepStatusEnum.PENDING
            )
            db.add(obj)
            new_objs.append(obj)
    if new_objs:
        await db.commit()
    return new_objs

# PUBLIC_INTERFACE
async def start_workflow(db: AsyncSession, instance_id: int) -> None:
    """Starts workflow execution for a given instance, updating first approvers as IN_PROGRESS, and creates step-approver assignments."""
    instance = await crud.get_instance(db, instance_id)
    if not instance:
        raise Exception("Instance not found")
    steps = await crud.list_instance_steps(db, instance_id)
    if not steps:
        raise Exception("At least one workflow step required to start")
    # Find step config(s) with order = 1 (start)
    step_cfg_ids = set(step.approval_workflow_step_config_id for step in steps)
    step_configs_map = {cid: await crud.get_step_config(db, cid) for cid in step_cfg_ids}
    # Progress all steps with order==1 to IN_PROGRESS, and assign step-approver records
    for s in steps:
        cfg = step_configs_map[s.approval_workflow_step_config_id]
        if cfg.order == 1:
            await crud.update_instance_step_status(db, s.id, StepStatusEnum.IN_PROGRESS)
            await _create_instance_step_approvers(db, s, cfg)
    await crud.update_instance_status(db, instance_id, InstanceStatusEnum.IN_PROGRESS)


# PUBLIC_INTERFACE
async def proceed_to_next_step(db: AsyncSession, instance_id: int) -> None:
    """
    Advances the workflow to next step(s). For SEQUENTIAL, next step; for PARALLEL, all eligible steps.
    For steps with multiple approvers, check 'any_one_can_approve' logic before completing the step.
    Updates instance status if complete.
    """
    instance = await crud.get_instance(db, instance_id)
    if not instance:
        raise Exception("Instance not found")
    all_steps = await crud.list_instance_steps(db, instance_id)
    if not all_steps:
        return

    # For each IN_PROGRESS step, check if satisfied via approvers, then move to APPROVED and next step as appropriate
    for step in all_steps:
        if step.status != StepStatusEnum.IN_PROGRESS:
            continue

        step_cfg = await crud.get_step_config(db, step.approval_workflow_step_config_id)
        approver_flag = await _get_any_one_can_approve_flag(step_cfg)
        # Fetch all approvers assigned to the step
        stmt = select(ApprovalWorkflowInstanceStepApprover).where(ApprovalWorkflowInstanceStepApprover.instance_step_id == step.id)
        result = await db.execute(stmt)
        approver_assignments = result.scalars().all()

        if approver_assignments:
            if approver_flag:
                # OR logic: any one can approve to progress this step
                if any(a.status == StepStatusEnum.APPROVED for a in approver_assignments):
                    # Mark all approvers as SKIPPED if still PENDING
                    for a in approver_assignments:
                        if a.status == StepStatusEnum.PENDING:
                            a.status = StepStatusEnum.SKIPPED
                    # Mark main step as APPROVED
                    await crud.update_instance_step_status(db, step.id, StepStatusEnum.APPROVED)
            else:
                # Default AND logic: all must approve to progress step
                if all(a.status == StepStatusEnum.APPROVED for a in approver_assignments):
                    await crud.update_instance_step_status(db, step.id, StepStatusEnum.APPROVED)

    # After updating statuses, check for next step progression
    refreshed_steps = await crud.list_instance_steps(db, instance_id)
    if all(st.status in [StepStatusEnum.APPROVED, StepStatusEnum.COMPLETED] for st in refreshed_steps):
        await crud.update_instance_status(db, instance_id, InstanceStatusEnum.COMPLETED)
        return

    # Find latest IN_PROGRESS steps again after updates
    in_progress_steps = [s for s in refreshed_steps if s.status == StepStatusEnum.IN_PROGRESS]
    if not in_progress_steps:
        # Try to progress steps in order
        max_order_approved = max((await crud.get_step_config(db, s.approval_workflow_step_config_id)).order
                                 for s in refreshed_steps if s.status == StepStatusEnum.APPROVED) \
                             if any(s.status == StepStatusEnum.APPROVED for s in refreshed_steps) else 0
        all_cfgs = [await crud.get_step_config(db, st.approval_workflow_step_config_id) for st in refreshed_steps]
        for cfg, st in zip(all_cfgs, refreshed_steps):
            if cfg.order == max_order_approved + 1 and st.status == StepStatusEnum.PENDING:
                await crud.update_instance_step_status(db, st.id, StepStatusEnum.IN_PROGRESS)
                await _create_instance_step_approvers(db, st, cfg)
    # For parallel, activate all steps of the next order together
    else:
        step_orders = set((await crud.get_step_config(db, s.approval_workflow_step_config_id)).order for s in in_progress_steps)
        for order in step_orders:
            group = [s for s in in_progress_steps if (await crud.get_step_config(db, s.approval_workflow_step_config_id)).order == order]
            if all(s.status == StepStatusEnum.APPROVED for s in group):
                next_order = order + 1
                for cfg, st in zip(all_cfgs, refreshed_steps):
                    if cfg.order == next_order and st.status == StepStatusEnum.PENDING:
                        await crud.update_instance_step_status(db, st.id, StepStatusEnum.IN_PROGRESS)
                        await _create_instance_step_approvers(db, st, cfg)
# PUBLIC_INTERFACE
async def apply_approval(
    db: AsyncSession,
    instance_step_id: int,
    approver_action: str,
    variables: Optional[Dict[str, Any]] = None,
    comments: Optional[str] = None,
    approver_id: Optional[str] = None,
) -> None:
    """
    Apply approval or rejection. Updates the individual approver's record and, if rules are satisfied, updates the step status and triggers the workflow progression.
    """
    step = await crud.get_instance_step(db, instance_step_id)
    if not step:
        raise Exception("Step not found")

    step_cfg = await crud.get_step_config(db, step.approval_workflow_step_config_id)
    if not step_cfg:
        raise Exception("Step config not found")

    # Update the individual approver assignment (if using multi-approver logic).
    stmt = select(ApprovalWorkflowInstanceStepApprover).where(
        ApprovalWorkflowInstanceStepApprover.instance_step_id == instance_step_id
    )
    result = await db.execute(stmt)
    approver_assignments = result.scalars().all()
    if approver_assignments:
        # Identify which approver is performing the action.
        matched_approver = None
        # Try to match using supplied approver_id; fallback to first PENDING if not supplied.
        if approver_id:
            for a in approver_assignments:
                if a.approver == approver_id and a.status == StepStatusEnum.PENDING:
                    matched_approver = a
                    break
        if not matched_approver:
            for a in approver_assignments:
                if a.status == StepStatusEnum.PENDING:
                    matched_approver = a
                    break
        if not matched_approver:
            raise Exception("No approver record found for action or already finalized")
        new_status = (
            StepStatusEnum.APPROVED if approver_action.upper() == "APPROVE"
            else StepStatusEnum.REJECTED if approver_action.upper() == "REJECT"
            else StepStatusEnum.SKIPPED
        )
        matched_approver.status = new_status
        matched_approver.comments = comments
        matched_approver.actioned_at = datetime.datetime.utcnow()
        await db.commit()
    else:
        # No approver assignment table: fallback to legacy/update step status directly.
        status = (
            StepStatusEnum.APPROVED if approver_action.upper() == "APPROVE"
            else StepStatusEnum.REJECTED if approver_action.upper() == "REJECT"
            else StepStatusEnum.SKIPPED
        )
        await crud.update_instance_step_status(db, instance_step_id, status, comments)

    # After action, try to advance workflow
    await proceed_to_next_step(db, step.approval_workflow_instance_id)

