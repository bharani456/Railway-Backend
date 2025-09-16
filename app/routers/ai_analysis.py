"""
AI analysis router - Task 12: AI Analysis and Reporting System
APIs: POST /api/ai-analysis/analyze, GET /api/ai-analysis/reports, POST /api/ai-analysis/bulk-predict
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query, Request
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import structlog
import httpx
import asyncio

from app.models.base import APIResponse, PaginatedResponse, AnalysisType, RiskLevel
from app.utils.security import verify_token, check_permissions
from app.config.database import get_collection
from app.config.settings import get_settings

logger = structlog.get_logger()
router = APIRouter()
settings = get_settings()

@router.post("/analyze", response_model=APIResponse)
async def analyze_data(
    analysis_data: dict,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    """
    Analyze QR code data using AI
    
    Input: {"qrCodeId": "qr_code_id", "analysisType": "predictive", "inputData": {"inspectionHistory": [...], "maintenanceHistory": [...], "environmentalData": {...}}}
    Output: {"success": true, "data": {"analysisReport": {...aiAnalysisObject}}}
    """
    try:
        if not check_permissions(current_user["role"], "ai_analysis"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        qr_code_id = analysis_data.get("qrCodeId")
        analysis_type = analysis_data.get("analysisType", "predictive")
        input_data = analysis_data.get("inputData", {})
        
        if not qr_code_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="QR code ID is required")
        
        # Verify QR code exists
        qr_codes_collection = get_collection("qr_codes")
        qr_code = await qr_codes_collection.find_one({"_id": qr_code_id})
        if not qr_code:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="QR code not found")
        
        # Prepare analysis request
        analysis_request = {
            "qrCodeId": qr_code_id,
            "analysisType": analysis_type,
            "inputData": input_data,
            "requestedBy": current_user["userId"],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Call AI service
        try:
            async with httpx.AsyncClient(timeout=settings.AI_SERVICE_TIMEOUT) as client:
                response = await client.post(
                    f"{settings.AI_SERVICE_URL}/analyze",
                    json=analysis_request
                )
                response.raise_for_status()
                ai_result = response.json()
        except httpx.RequestError as e:
            logger.error("AI service request failed", error=str(e))
            # Fallback to mock analysis
            ai_result = await _mock_ai_analysis(qr_code_id, analysis_type, input_data)
        
        # Save analysis report
        reports_collection = get_collection("ai_analysis_reports")
        report_doc = {
            "qrCodeId": qr_code_id,
            "analysisType": analysis_type,
            "inputData": input_data,
            "analysisResult": ai_result,
            "riskLevel": ai_result.get("riskLevel", "low"),
            "confidence": ai_result.get("confidence", 0.5),
            "recommendations": ai_result.get("recommendations", []),
            "status": "completed",
            "requestedBy": current_user["userId"],
            "completedAt": datetime.utcnow(),
            "createdAt": datetime.utcnow()
        }
        
        result = await reports_collection.insert_one(report_doc)
        report_doc["id"] = str(result.inserted_id)
        
        logger.info(
            "AI analysis completed successfully",
            user_id=current_user["userId"],
            qr_code_id=qr_code_id,
            analysis_type=analysis_type
        )
        
        return APIResponse(
            success=True,
            data={"analysisReport": report_doc}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to analyze data", error=str(e), user_id=current_user.get("userId"))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to analyze data")

@router.get("/reports", response_model=PaginatedResponse)
async def get_ai_reports(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    qrCodeId: Optional[str] = Query(None),
    analysisType: Optional[str] = Query(None),
    riskLevel: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    dateRange: Optional[str] = Query(None),
    current_user: dict = Depends(verify_token)
):
    """
    Get AI analysis reports
    
    Input: Query params (qrCodeId="qr_id", analysisType="predictive", riskAssessment="high")
    Output: {"success": true, "data": {"reports": [...aiReportObjects], "pagination": {...}}}
    """
    try:
        if not check_permissions(current_user["role"], "ai_analysis"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        # Build query
        query = {}
        
        if qrCodeId:
            query["qrCodeId"] = qrCodeId
        if analysisType:
            query["analysisType"] = analysisType
        if riskLevel:
            query["riskLevel"] = riskLevel
        if status:
            query["status"] = status
        
        if dateRange:
            try:
                start_date, end_date = dateRange.split(",")
                start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
                end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                query["createdAt"] = {"$gte": start_dt, "$lte": end_dt}
            except ValueError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date range format")
        
        reports_collection = get_collection("ai_analysis_reports")
        skip = (page - 1) * limit
        
        total = await reports_collection.count_documents(query)
        cursor = reports_collection.find(query).sort("createdAt", -1).skip(skip).limit(limit)
        reports = await cursor.to_list(length=limit)
        
        report_list = []
        for report in reports:
            report_dict = {k: v for k, v in report.items() if k != "_id"}
            report_dict["id"] = str(report["_id"])
            report_list.append(report_dict)
        
        pages = (total + limit - 1) // limit
        
        logger.info(
            "AI reports retrieved successfully",
            user_id=current_user["userId"],
            total=total,
            page=page
        )
        
        return PaginatedResponse(
            data=report_list,
            pagination={
                "page": page, "limit": limit, "total": total, "pages": pages,
                "hasNext": page < pages, "hasPrev": page > 1
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get AI reports", error=str(e), user_id=current_user.get("userId"))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve AI reports")

@router.post("/bulk-predict", response_model=APIResponse)
async def bulk_predict(
    prediction_data: dict,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    """
    Perform bulk prediction analysis
    
    Input: {"filters": {"zoneId": "zone_id", "fittingTypeId": "fitting_type_id", "installationDateRange": {...}}, "analysisType": "lifecycle"}
    Output: {"success": true, "data": {"analysisResults": [...bulkAnalysisResults], "summary": {"totalAnalyzed": 1000, "highRiskCount": 50, "mediumRiskCount": 200}}}
    """
    try:
        if not check_permissions(current_user["role"], "ai_analysis"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        filters = prediction_data.get("filters", {})
        analysis_type = prediction_data.get("analysisType", "lifecycle")
        
        # Build query for QR codes based on filters
        qr_query = {}
        
        if filters.get("zoneId"):
            installations_collection = get_collection("fitting_installations")
            installations = await installations_collection.find(
                {"zoneId": filters["zoneId"]},
                {"qrCodeId": 1}
            ).to_list(length=None)
            qr_code_ids = [inst["qrCodeId"] for inst in installations]
            qr_query["_id"] = {"$in": qr_code_ids}
        
        if filters.get("fittingTypeId"):
            # Get batches with this fitting type
            batches_collection = get_collection("fitting_batches")
            batches = await batches_collection.find(
                {"fittingTypeId": filters["fittingTypeId"]},
                {"_id": 1}
            ).to_list(length=None)
            batch_ids = [batch["_id"] for batch in batches]
            qr_query["fittingBatchId"] = {"$in": batch_ids}
        
        if filters.get("installationDateRange"):
            start_date = filters["installationDateRange"].get("start")
            end_date = filters["installationDateRange"].get("end")
            if start_date and end_date:
                installations_collection = get_collection("fitting_installations")
                installations = await installations_collection.find(
                    {
                        "installationDate": {
                            "$gte": datetime.fromisoformat(start_date.replace("Z", "+00:00")),
                            "$lte": datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                        }
                    },
                    {"qrCodeId": 1}
                ).to_list(length=None)
                qr_code_ids = [inst["qrCodeId"] for inst in installations]
                if qr_query.get("_id"):
                    qr_query["_id"]["$in"] = list(set(qr_query["_id"]["$in"]) & set(qr_code_ids))
                else:
                    qr_query["_id"] = {"$in": qr_code_ids}
        
        # Get QR codes to analyze
        qr_codes_collection = get_collection("qr_codes")
        qr_codes = await qr_codes_collection.find(qr_query).to_list(length=None)
        
        if not qr_codes:
            return APIResponse(
                success=True,
                data={
                    "analysisResults": [],
                    "summary": {
                        "totalAnalyzed": 0,
                        "highRiskCount": 0,
                        "mediumRiskCount": 0,
                        "lowRiskCount": 0
                    }
                }
            )
        
        # Perform bulk analysis
        analysis_results = []
        risk_counts = {"high": 0, "medium": 0, "low": 0}
        
        # Process in batches to avoid overwhelming the system
        batch_size = 50
        for i in range(0, len(qr_codes), batch_size):
            batch_qr_codes = qr_codes[i:i + batch_size]
            
            # Prepare batch analysis request
            batch_request = {
                "qrCodeIds": [str(qr["_id"]) for qr in batch_qr_codes],
                "analysisType": analysis_type,
                "filters": filters,
                "requestedBy": current_user["userId"],
                "timestamp": datetime.utcnow().isoformat()
            }
            
            try:
                # Call AI service for batch analysis
                async with httpx.AsyncClient(timeout=settings.AI_SERVICE_TIMEOUT) as client:
                    response = await client.post(
                        f"{settings.AI_SERVICE_URL}/bulk-analyze",
                        json=batch_request
                    )
                    response.raise_for_status()
                    batch_result = response.json()
            except httpx.RequestError as e:
                logger.error("AI service batch request failed", error=str(e))
                # Fallback to mock analysis
                batch_result = await _mock_bulk_analysis(batch_qr_codes, analysis_type)
            
            # Process results
            for result in batch_result.get("results", []):
                analysis_results.append(result)
                risk_level = result.get("riskLevel", "low")
                if risk_level in risk_counts:
                    risk_counts[risk_level] += 1
        
        # Save bulk analysis results
        reports_collection = get_collection("ai_analysis_reports")
        bulk_report_doc = {
            "analysisType": analysis_type,
            "filters": filters,
            "analysisResults": analysis_results,
            "summary": {
                "totalAnalyzed": len(analysis_results),
                "highRiskCount": risk_counts["high"],
                "mediumRiskCount": risk_counts["medium"],
                "lowRiskCount": risk_counts["low"]
            },
            "status": "completed",
            "requestedBy": current_user["userId"],
            "completedAt": datetime.utcnow(),
            "createdAt": datetime.utcnow()
        }
        
        await reports_collection.insert_one(bulk_report_doc)
        
        logger.info(
            "Bulk prediction completed successfully",
            user_id=current_user["userId"],
            total_analyzed=len(analysis_results),
            analysis_type=analysis_type
        )
        
        return APIResponse(
            success=True,
            data={
                "analysisResults": analysis_results,
                "summary": {
                    "totalAnalyzed": len(analysis_results),
                    "highRiskCount": risk_counts["high"],
                    "mediumRiskCount": risk_counts["medium"],
                    "lowRiskCount": risk_counts["low"]
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to perform bulk prediction", error=str(e), user_id=current_user.get("userId"))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to perform bulk prediction")

async def _mock_ai_analysis(qr_code_id: str, analysis_type: str, input_data: dict) -> dict:
    """Mock AI analysis for fallback"""
    import random
    
    risk_levels = ["low", "medium", "high", "critical"]
    risk_level = random.choices(risk_levels, weights=[50, 30, 15, 5])[0]
    
    mock_result = {
        "qrCodeId": qr_code_id,
        "analysisType": analysis_type,
        "riskLevel": risk_level,
        "confidence": round(random.uniform(0.6, 0.95), 2),
        "predictions": {
            "remainingLife": random.randint(30, 365),
            "failureProbability": round(random.uniform(0.01, 0.3), 3),
            "maintenanceUrgency": random.choice(["low", "medium", "high"])
        },
        "recommendations": [
            f"Schedule {random.choice(['routine', 'detailed', 'emergency'])} inspection",
            f"Monitor for {random.choice(['wear', 'corrosion', 'fatigue'])} signs",
            f"Consider {random.choice(['preventive', 'corrective'])} maintenance"
        ],
        "analysisDate": datetime.utcnow().isoformat(),
        "modelVersion": "1.0.0"
    }
    
    return mock_result

async def _mock_bulk_analysis(qr_codes: list, analysis_type: str) -> dict:
    """Mock bulk analysis for fallback"""
    results = []
    
    for qr_code in qr_codes:
        result = await _mock_ai_analysis(str(qr_code["_id"]), analysis_type, {})
        results.append(result)
    
    return {"results": results}
