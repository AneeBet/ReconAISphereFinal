from fastapi import APIRouter
from fastapi import Depends
from fastapi import Response

from sqlalchemy.orm import Session

from app.core.dependencies import (
    require_viewer,
)

from app.db.session import (
    get_db,
)

from app.repositories.report_repository import (
    ReportRepository,
)

from app.schemas.report import (
    DashboardReport,
    ReportRequest,
    ReportResponse,
)

from app.services.report_service import (
    ReportService,
)


router = APIRouter(

    prefix="/reports",

    tags=["Reports"]

)


@router.get(

    "/dashboard",

    response_model=DashboardReport

)
def dashboard_report(

    current_user=Depends(
        require_viewer
    ),

    db: Session = Depends(
        get_db
    )

):

    return ReportService(

        ReportRepository(db)

    ).dashboard_report()


@router.post(

    "/export",

    response_model=ReportResponse

)
def export(

    request: ReportRequest,

    current_user=Depends(
        require_viewer
    ),

    db: Session = Depends(
        get_db
    )

):

    return ReportService(

        ReportRepository(db)

    ).export(

        request.report_type

    )


@router.get(

    "/download/{report_name}"

)
def download(

    report_name: str,

    current_user=Depends(
        require_viewer
    ),

    db: Session = Depends(
        get_db
    )

):

    data = ReportService(
        ReportRepository(db)
    ).download(report_name)

    return Response(

        content=data,

        media_type="text/csv",

        headers={
            "Content-Disposition":
            f'attachment; filename="{report_name}"'
        }

    )