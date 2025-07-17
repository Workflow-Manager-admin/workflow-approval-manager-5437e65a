from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import router as workflow_router

app = FastAPI(
    title="Approval Workflow API",
    description="""APIs for configuring and running approval workflows. Endpoints support CRUD for approval_workflow_config, approval_workflow_step_config, approval_workflow_block, approval_workflow_instance, approval_workflow_instance_step, and workflow logic triggers.""",
    version="1.0.0",
    openapi_tags=[
        {"name": "Approval Workflow Config", "description": "Manage high-level workflow configuration."},
        {"name": "Approval Workflow Step Config", "description": "Manage step configuration for a workflow."},
        {"name": "Approval Workflow Block", "description": "Reusable approval blocks/rules for workflow."},
        {"name": "Approval Workflow Instance", "description": "Runtime instances of workflows."},
        {"name": "Approval Workflow Instance Step", "description": "Step execution for workflow instances."},
        {"name": "Workflow Execution", "description": "Start workflow or apply approval."},
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"message": "Healthy"}

app.include_router(workflow_router)
