from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.schemas.budget import BudgetCreate, BudgetUpdate, BudgetOut
from app.services.budget_service import BudgetService
from app.utils.dependencies import get_current_user
import os
import subprocess
import tempfile
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/budgets", tags=["Budgets"])

def get_budget_service(db: Session = Depends(get_db)):
    return BudgetService(db)

@router.post("/", response_model=BudgetOut)
async def create_budget(
    budget: BudgetCreate,
    current_user: User = Depends(get_current_user),
    service: BudgetService = Depends(get_budget_service)
):
    permissions = current_user.get_permissions()
    if not permissions.can_create_budget():
        raise HTTPException(status_code=403, detail="No tienes permiso para crear presupuestos")
    db_budget = service.create_budget(budget, current_user.id)
    return db_budget

@router.get("/{budget_id}", response_model=BudgetOut)
async def get_budget(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    service: BudgetService = Depends(get_budget_service)
):
    permissions = current_user.get_permissions()
    if not permissions.can_read_budget():
        raise HTTPException(status_code=403, detail="No tienes permiso para leer presupuestos")
    return service.get_budget(budget_id, current_user.id)

@router.get("/", response_model=List[BudgetOut])
async def get_all_budgets(
    current_user: User = Depends(get_current_user),
    service: BudgetService = Depends(get_budget_service)
):
    permissions = current_user.get_permissions()
    if not permissions.can_read_budget():
        raise HTTPException(status_code=403, detail="No tienes permiso para leer presupuestos")
    return service.get_all_budgets(current_user.id)

@router.put("/{budget_id}", response_model=BudgetOut)
async def update_budget(
    budget_id: int,
    budget_update: BudgetUpdate,
    current_user: User = Depends(get_current_user),
    service: BudgetService = Depends(get_budget_service)
):
    permissions = current_user.get_permissions()
    if not permissions.can_update_budget():
        raise HTTPException(status_code=403, detail="No tienes permiso para actualizar presupuestos")
    budget_dict = budget_update.dict(exclude_unset=True)
    return service.update_budget(budget_id, budget_dict, current_user.id)

@router.delete("/{budget_id}")
async def delete_budget(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    service: BudgetService = Depends(get_budget_service)
):
    permissions = current_user.get_permissions()
    if not permissions.can_delete_budget():
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar presupuestos")
    return service.delete_budget(budget_id, current_user.id)

@router.patch("/{budget_id}/sync")
def sync_budget(budget_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    budget_service = BudgetService(db)
    return budget_service.sync_budget(budget_id, user.id)

@router.get("/{budget_id}/report")
async def get_budget_report(budget_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    budget_service = BudgetService(db)
    report_data = budget_service.generate_budget_report(budget_id, user.id)

    # Cargar plantilla LaTeX
    template_path = "app/templates/budget_report_template.tex"
    if not os.path.exists(template_path):
        raise HTTPException(status_code=500, detail="Plantilla LaTeX no encontrada")
    with open(template_path, "r") as f:
        template = f.read()

    # Reemplazar placeholders
    deviations_table = ""
    for category, data in report_data["analysis"]["deviations"].items():
        deviations_table += (
            f"{category} & ${data['recommended']:,.0f} & ${data['actual']:,.0f} & ${data['deviation']:,.0f} \\\\ \n"
        )

    recommendations_list = ""
    for rec in report_data["recommendations"]:
        recommendations_list += f"\\item {rec}\n"

    template = template.replace("REPORT_PERIOD", report_data["period"])
    template = template.replace("RECOMMENDED_TOTAL", f"{report_data['analysis']['total_recommended']:,.0f}")
    template = template.replace("ACTUAL_TOTAL", f"{report_data['analysis']['total_actual']:,.0f}")
    template = template.replace("DIFFERENCE", f"{report_data['analysis']['difference']:,.0f}")
    template = template.replace("STATUS", report_data["analysis"]["status"])
    template = template.replace("DEVIATIONS_TABLE", deviations_table)
    template = template.replace("RECOMMENDATIONS_LIST", recommendations_list)
    template = template.replace("BAR_CHART_PATH", report_data["charts"]["bar_chart"])
    if report_data["charts"]["pie_chart"]:
        template = template.replace("PIE_CHART_PATH", report_data["charts"]["pie_chart"])
        template = template.replace("\\ifdefined\\PIE_CHART_PATH", "")
        template = template.replace("\\fi", "")
    else:
        template = template.replace("\\ifdefined\\PIE_CHART_PATH", "%")
        template = template.replace("\\fi", "%")

    # Crear archivo LaTeX temporal
    with tempfile.NamedTemporaryFile(suffix=".tex", delete=False) as tex_file:
        tex_file.write(template.encode("utf-8"))
        tex_file_path = tex_file.name

    # Compilar LaTeX a PDF
    pdf_path = tex_file_path.replace(".tex", ".pdf")
    try:
        subprocess.run(
            ["latexmk", "-pdf", "-interaction=nonstopmode", tex_file_path],
            check=True,
            cwd=os.path.dirname(tex_file_path)
        )
        logger.info(f"PDF generado en {pdf_path}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error al compilar LaTeX: {e}")
        raise HTTPException(status_code=500, detail="Error al generar el reporte PDF")
    except FileNotFoundError:
        logger.error("latexmk no está instalado")
        raise HTTPException(status_code=500, detail="latexmk no está instalado en el servidor")

    # Devolver el PDF
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"budget_report_{budget_id}.pdf"
    )