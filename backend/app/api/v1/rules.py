"""
Monitoring rules API endpoints
"""
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from bson import ObjectId

from ...core.database import get_database
from ...models import (
    MonitoringRule,
    MonitoringRuleCreate,
    MonitoringRuleUpdate,
    MonitoringRuleResponse,
)

router = APIRouter()


@router.get("/", response_model=List[MonitoringRuleResponse])
async def get_rules(
    enabled_only: bool = False,
    db=Depends(get_database),
):
    """
    Get all monitoring rules

    - **enabled_only**: Only return enabled rules
    """
    query = {}
    if enabled_only:
        query["enabled"] = True

    cursor = db.monitoring_rules.find(query).sort("created_at", -1)
    rules = await cursor.to_list(length=None)

    return [
        MonitoringRuleResponse(
            id=str(rule["_id"]),
            **{k: v for k, v in rule.items() if k != "_id"}
        )
        for rule in rules
    ]


@router.get("/{rule_id}", response_model=MonitoringRule)
async def get_rule(rule_id: str, db=Depends(get_database)):
    """
    Get specific monitoring rule by ID
    """
    if not ObjectId.is_valid(rule_id):
        raise HTTPException(status_code=400, detail="Invalid rule ID")

    rule = await db.monitoring_rules.find_one({"_id": ObjectId(rule_id)})

    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    return MonitoringRule(**rule)


@router.post("/", response_model=MonitoringRuleResponse, status_code=201)
async def create_rule(rule: MonitoringRuleCreate, db=Depends(get_database)):
    """
    Create a new monitoring rule
    """
    rule_dict = rule.model_dump()
    rule_dict["created_at"] = datetime.utcnow()
    rule_dict["updated_at"] = datetime.utcnow()
    rule_dict["total_matches"] = 0
    rule_dict["total_alerts"] = 0
    rule_dict["last_triggered"] = None

    result = await db.monitoring_rules.insert_one(rule_dict)

    return MonitoringRuleResponse(
        id=str(result.inserted_id),
        name=rule_dict["name"],
        description=rule_dict.get("description"),
        enabled=rule_dict["enabled"],
        severity=rule_dict["severity"],
        total_matches=0,
        total_alerts=0,
        last_triggered=None,
        created_at=rule_dict["created_at"],
    )


@router.patch("/{rule_id}", response_model=MonitoringRuleResponse)
async def update_rule(
    rule_id: str,
    rule_update: MonitoringRuleUpdate,
    db=Depends(get_database),
):
    """
    Update a monitoring rule
    """
    if not ObjectId.is_valid(rule_id):
        raise HTTPException(status_code=400, detail="Invalid rule ID")

    # Check if rule exists
    current_rule = await db.monitoring_rules.find_one({"_id": ObjectId(rule_id)})
    if not current_rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    # Prepare update
    update_dict = rule_update.model_dump(exclude_unset=True)
    update_dict["updated_at"] = datetime.utcnow()

    # Update rule
    await db.monitoring_rules.update_one(
        {"_id": ObjectId(rule_id)},
        {"$set": update_dict}
    )

    # Get updated rule
    updated_rule = await db.monitoring_rules.find_one({"_id": ObjectId(rule_id)})

    return MonitoringRuleResponse(
        id=str(updated_rule["_id"]),
        **{k: v for k, v in updated_rule.items() if k != "_id"}
    )


@router.delete("/{rule_id}", status_code=204)
async def delete_rule(rule_id: str, db=Depends(get_database)):
    """
    Delete a monitoring rule
    """
    if not ObjectId.is_valid(rule_id):
        raise HTTPException(status_code=400, detail="Invalid rule ID")

    result = await db.monitoring_rules.delete_one({"_id": ObjectId(rule_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Rule not found")

    return None


@router.post("/{rule_id}/toggle", response_model=MonitoringRuleResponse)
async def toggle_rule(rule_id: str, db=Depends(get_database)):
    """
    Toggle rule enabled/disabled status
    """
    if not ObjectId.is_valid(rule_id):
        raise HTTPException(status_code=400, detail="Invalid rule ID")

    rule = await db.monitoring_rules.find_one({"_id": ObjectId(rule_id)})
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    # Toggle enabled status
    new_status = not rule["enabled"]

    await db.monitoring_rules.update_one(
        {"_id": ObjectId(rule_id)},
        {"$set": {"enabled": new_status, "updated_at": datetime.utcnow()}}
    )

    # Get updated rule
    updated_rule = await db.monitoring_rules.find_one({"_id": ObjectId(rule_id)})

    return MonitoringRuleResponse(
        id=str(updated_rule["_id"]),
        **{k: v for k, v in updated_rule.items() if k != "_id"}
    )
