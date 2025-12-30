from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.orm import Session
from typing import Literal
import io

from src.core.database import get_db
from src.models.matching import MatchingResult
from src.models.workspace import Workspace
from src.services.report_generator import ReportGenerator

router = APIRouter()


@router.get("/matching-result/{result_id}/pdf")
async def download_pdf_report(result_id: str, db: Session = Depends(get_db)):
    """Generate and download PDF reconciliation report"""
    # Verify result exists
    result = db.query(MatchingResult).filter(MatchingResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Matching result not found")

    try:
        generator = ReportGenerator(db)
        pdf_content = generator.generate_pdf_report(result_id)
        
        return StreamingResponse(
            io.BytesIO(pdf_content),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="reconciliation-report-{result_id[:8]}.pdf"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF report: {str(e)}")


@router.get("/matching-result/{result_id}/json")
async def download_json_report(result_id: str, db: Session = Depends(get_db)):
    """Generate and download JSON reconciliation report"""
    # Verify result exists
    result = db.query(MatchingResult).filter(MatchingResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Matching result not found")

    try:
        import json
        generator = ReportGenerator(db)
        json_data = generator.generate_json_report(result_id)
        
        return Response(
            content=json.dumps(json_data, indent=2),
            media_type="application/json",
            headers={
                "Content-Disposition": f'attachment; filename="reconciliation-report-{result_id[:8]}.json"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate JSON report: {str(e)}")


@router.get("/matching-result/{result_id}/csv")
async def download_csv_report(result_id: str, db: Session = Depends(get_db)):
    """Generate and download CSV reconciliation report"""
    # Verify result exists
    result = db.query(MatchingResult).filter(MatchingResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Matching result not found")

    try:
        generator = ReportGenerator(db)
        csv_content = generator.generate_csv_report(result_id)
        
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="reconciliation-report-{result_id[:8]}.csv"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate CSV report: {str(e)}")


@router.get("/workspace/{workspace_id}/export")
async def export_workspace_reports(
    workspace_id: str,
    format: Literal["json", "csv"] = Query(default="json"),
    db: Session = Depends(get_db)
):
    """Export all matching results for a workspace"""
    # Verify workspace exists
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Get all matching results
    results = db.query(MatchingResult).filter(
        MatchingResult.workspace_id == workspace_id
    ).all()

    if not results:
        raise HTTPException(status_code=404, detail="No matching results found for this workspace")

    try:
        generator = ReportGenerator(db)
        
        if format == "json":
            # Export all results as JSON array
            all_reports = []
            for result in results:
                report = generator.generate_json_report(result.id)
                all_reports.append(report)
            
            import json
            return Response(
                content=json.dumps(all_reports, indent=2),
                media_type="application/json",
                headers={
                    "Content-Disposition": f'attachment; filename="workspace-reports-{workspace_id[:8]}.json"'
                }
            )
        else:  # CSV
            # Combine all CSV reports
            import io
            output = io.StringIO()
            
            for idx, result in enumerate(results):
                if idx > 0:
                    output.write("\n\n")
                    output.write(f"=== Matching Result {idx + 1} ===\n")
                
                csv_content = generator.generate_csv_report(result.id)
                output.write(csv_content)
            
            output.seek(0)
            return Response(
                content=output.getvalue(),
                media_type="text/csv",
                headers={
                    "Content-Disposition": f'attachment; filename="workspace-reports-{workspace_id[:8]}.csv"'
                }
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export reports: {str(e)}")

