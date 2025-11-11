"""
Threat API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from datetime import datetime, timedelta
from bson import ObjectId

from ...core.database import get_database
from ...models import (
    ThreatModel,
    ThreatCreate,
    ThreatUpdate,
    ThreatResponse,
    ThreatSeverity,
    ThreatType,
    DataSource,
)

router = APIRouter()


@router.get("/", response_model=List[ThreatResponse])
async def get_threats(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    severity: Optional[ThreatSeverity] = None,
    threat_type: Optional[ThreatType] = None,
    source: Optional[DataSource] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    reviewed: Optional[bool] = None,
    false_positive: Optional[bool] = None,
    db=Depends(get_database),
):
    """
    Get list of threats with optional filters

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **severity**: Filter by severity level
    - **threat_type**: Filter by threat type
    - **source**: Filter by data source
    - **start_date**: Filter threats discovered after this date
    - **end_date**: Filter threats discovered before this date
    - **reviewed**: Filter by review status
    - **false_positive**: Filter by false positive flag
    """
    # Build query
    query = {}

    if severity:
        query["severity"] = severity

    if threat_type:
        query["threat_type"] = threat_type

    if source:
        query["source"] = source

    if reviewed is not None:
        query["reviewed"] = reviewed

    if false_positive is not None:
        query["false_positive"] = false_positive

    if start_date or end_date:
        query["discovered_at"] = {}
        if start_date:
            query["discovered_at"]["$gte"] = start_date
        if end_date:
            query["discovered_at"]["$lte"] = end_date

    # Execute query
    cursor = db.threats.find(query).sort("discovered_at", -1).skip(skip).limit(limit)
    threats = await cursor.to_list(length=limit)

    # Convert to response model
    return [
        ThreatResponse(
            id=str(threat["_id"]),
            **{k: v for k, v in threat.items() if k != "_id"}
        )
        for threat in threats
    ]


@router.get("/stats")
async def get_threat_stats(
    days: int = Query(7, ge=1, le=365),
    db=Depends(get_database),
):
    """
    Get threat statistics

    - **days**: Number of days to include in statistics
    """
    start_date = datetime.utcnow() - timedelta(days=days)

    # Total threats
    total = await db.threats.count_documents({"discovered_at": {"$gte": start_date}})

    # By severity
    pipeline = [
        {"$match": {"discovered_at": {"$gte": start_date}}},
        {"$group": {"_id": "$severity", "count": {"$sum": 1}}},
    ]
    by_severity = {item["_id"]: item["count"] async for item in db.threats.aggregate(pipeline)}

    # By type
    pipeline = [
        {"$match": {"discovered_at": {"$gte": start_date}}},
        {"$group": {"_id": "$threat_type", "count": {"$sum": 1}}},
    ]
    by_type = {item["_id"]: item["count"] async for item in db.threats.aggregate(pipeline)}

    # By source
    pipeline = [
        {"$match": {"discovered_at": {"$gte": start_date}}},
        {"$group": {"_id": "$source", "count": {"$sum": 1}}},
    ]
    by_source = {item["_id"]: item["count"] async for item in db.threats.aggregate(pipeline)}

    # Critical unreviewed
    critical_unreviewed = await db.threats.count_documents({
        "discovered_at": {"$gte": start_date},
        "severity": ThreatSeverity.CRITICAL,
        "reviewed": False,
    })

    return {
        "period_days": days,
        "total_threats": total,
        "by_severity": by_severity,
        "by_type": by_type,
        "by_source": by_source,
        "critical_unreviewed": critical_unreviewed,
    }


@router.get("/{threat_id}", response_model=ThreatModel)
async def get_threat(threat_id: str, db=Depends(get_database)):
    """
    Get specific threat by ID
    """
    if not ObjectId.is_valid(threat_id):
        raise HTTPException(status_code=400, detail="Invalid threat ID")

    threat = await db.threats.find_one({"_id": ObjectId(threat_id)})

    if not threat:
        raise HTTPException(status_code=404, detail="Threat not found")

    return ThreatModel(**threat)


@router.post("/", response_model=ThreatResponse, status_code=201)
async def create_threat(threat: ThreatCreate, db=Depends(get_database)):
    """
    Create a new threat manually
    """
    threat_dict = threat.model_dump()
    threat_dict["discovered_at"] = datetime.utcnow()
    threat_dict["false_positive"] = False
    threat_dict["reviewed"] = False
    threat_dict["alert_triggered"] = False
    threat_dict["alert_sent"] = False

    result = await db.threats.insert_one(threat_dict)

    return ThreatResponse(
        id=str(result.inserted_id),
        **threat_dict
    )


@router.patch("/{threat_id}", response_model=ThreatResponse)
async def update_threat(
    threat_id: str,
    threat_update: ThreatUpdate,
    db=Depends(get_database),
):
    """
    Update a threat
    """
    if not ObjectId.is_valid(threat_id):
        raise HTTPException(status_code=400, detail="Invalid threat ID")

    # Get current threat
    current_threat = await db.threats.find_one({"_id": ObjectId(threat_id)})
    if not current_threat:
        raise HTTPException(status_code=404, detail="Threat not found")

    # Prepare update
    update_dict = threat_update.model_dump(exclude_unset=True)

    if update_dict.get("reviewed"):
        update_dict["reviewed_at"] = datetime.utcnow()

    # Update threat
    await db.threats.update_one(
        {"_id": ObjectId(threat_id)},
        {"$set": update_dict}
    )

    # Get updated threat
    updated_threat = await db.threats.find_one({"_id": ObjectId(threat_id)})

    return ThreatResponse(
        id=str(updated_threat["_id"]),
        **{k: v for k, v in updated_threat.items() if k != "_id"}
    )


@router.delete("/{threat_id}", status_code=204)
async def delete_threat(threat_id: str, db=Depends(get_database)):
    """
    Delete a threat
    """
    if not ObjectId.is_valid(threat_id):
        raise HTTPException(status_code=400, detail="Invalid threat ID")

    result = await db.threats.delete_one({"_id": ObjectId(threat_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Threat not found")

    return None


@router.post("/search")
async def search_threats(
    query: str = Query(..., min_length=3),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db=Depends(get_database),
):
    """
    Full-text search for threats

    - **query**: Search query
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records
    """
    # MongoDB text search
    search_query = {
        "$text": {"$search": query}
    }

    cursor = db.threats.find(
        search_query,
        {"score": {"$meta": "textScore"}}
    ).sort([("score", {"$meta": "textScore"})]).skip(skip).limit(limit)

    threats = await cursor.to_list(length=limit)

    return [
        ThreatResponse(
            id=str(threat["_id"]),
            **{k: v for k, v in threat.items() if k not in ["_id", "score"]}
        )
        for threat in threats
    ]
