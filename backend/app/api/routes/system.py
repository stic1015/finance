from fastapi import APIRouter, Request

from app.schemas.models import HealthResponse

router = APIRouter()


@router.get("/system/health")
async def system_health(request: Request):
    settings = request.app.state.settings
    market_diagnostic = request.app.state.market_service.diagnose()
    news_diagnostic = request.app.state.news_service.diagnose()
    status = "ok"
    if market_diagnostic.status in {"fixture", "unavailable"}:
        status = "degraded"
    if news_diagnostic.status == "unavailable":
        status = "degraded"
    if getattr(request.app.state, "database_warning", ""):
        status = "degraded"
    if request.app.state.backtest_jobs.executor_mode == "thread_pool":
        status = "degraded"
    response = HealthResponse(
        status=status,
        environment=settings.app_env,
        market_provider=settings.market_provider,
        news_provider=settings.news_provider,
        fixture_mode=settings.enable_fixture_mode,
        database_mode=request.app.state.repository.storage_mode,
        database_path=str(request.app.state.database_path),
        database_message=getattr(request.app.state, "database_warning", "") or None,
        executor_mode=request.app.state.backtest_jobs.executor_mode,
        executor_message=request.app.state.backtest_jobs.executor_message or None,
        market_provider_status=market_diagnostic.status,
        market_provider_message=market_diagnostic.detail,
        news_provider_status=news_diagnostic.status,
        news_provider_message=news_diagnostic.detail,
    )
    return {"data": response}
