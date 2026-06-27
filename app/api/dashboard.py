from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.dependencies import (
    require_viewer,
)

from app.db.session import (
    get_db,
)

from app.repositories.dashboard_repository import (
    DashboardRepository,
)

from app.schemas.dashboard import (
    BankSummaryResponse,
    DashboardSummaryResponse,
    ExceptionChartResponse,
    RecentRunResponse,
)

from app.services.dashboard_service import (
    DashboardService,
)


router = APIRouter(

    prefix="/dashboard",

    tags=["Dashboard"]

)


@router.get(

    "/summary",

    response_model=DashboardSummaryResponse

)
def summary(

    current_user=Depends(
        require_viewer
    ),

    db: Session = Depends(
        get_db
    )

):

    return DashboardService(

        DashboardRepository(db)

    ).summary()


@router.get(

    "/reconciliation-runs",

    response_model=list[RecentRunResponse]

)
def reconciliation_runs(

    current_user=Depends(
        require_viewer
    ),

    db: Session = Depends(
        get_db
    )

):

    return DashboardService(

        DashboardRepository(db)

    ).recent_runs()


@router.get(

    "/bank-summary",

    response_model=list[BankSummaryResponse]

)
def bank_summary(

    current_user=Depends(
        require_viewer
    ),

    db: Session = Depends(
        get_db
    )

):

    return DashboardService(

        DashboardRepository(db)

    ).bank_summary()


@router.get(

    "/exception-chart",

    response_model=ExceptionChartResponse

)
def exception_chart(

    current_user=Depends(
        require_viewer
    ),

    db: Session = Depends(
        get_db
    )

):

    return DashboardService(

        DashboardRepository(db)

    ).exception_chart()
