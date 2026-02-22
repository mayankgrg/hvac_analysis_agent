from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.db.connection import get_connection
from backend.tools.co_detail import get_co_detail
from backend.tools.field_notes import get_field_notes
from backend.tools.labor_detail import get_labor_detail
from backend.tools.rfi_detail import get_rfi_detail
from backend.tools.what_if_margin import what_if_margin

router = APIRouter(prefix="/api/tools", tags=["tools"])


class FieldNotesRequest(BaseModel):
    project_id: str
    keyword: str = ""
    limit: int = 20


class LaborDetailRequest(BaseModel):
    project_id: str
    sov_line_id: str


class CoDetailRequest(BaseModel):
    project_id: str
    co_number: str


class RfiDetailRequest(BaseModel):
    project_id: str
    rfi_number: str


class WhatIfMarginRequest(BaseModel):
    project_id: str
    recovery_amount: float


@router.post("/field-notes")
def field_notes(req: FieldNotesRequest):
    conn = get_connection()
    try:
        data = get_field_notes(conn, req.project_id, req.keyword, req.limit)
        return {"count": len(data), "items": data}
    finally:
        conn.close()


@router.post("/labor-detail")
def labor_detail(req: LaborDetailRequest):
    conn = get_connection()
    try:
        return get_labor_detail(conn, req.project_id, req.sov_line_id)
    finally:
        conn.close()


@router.post("/co-detail")
def co_detail(req: CoDetailRequest):
    conn = get_connection()
    try:
        row = get_co_detail(conn, req.co_number)
        if not row or row.get("project_id") != req.project_id:
            raise HTTPException(status_code=404, detail="CO not found for project")
        return row
    finally:
        conn.close()


@router.post("/rfi-detail")
def rfi_detail(req: RfiDetailRequest):
    conn = get_connection()
    try:
        row = get_rfi_detail(conn, req.rfi_number)
        if not row or row.get("project_id") != req.project_id:
            raise HTTPException(status_code=404, detail="RFI not found for project")
        return row
    finally:
        conn.close()


@router.post("/what-if-margin")
def what_if(req: WhatIfMarginRequest):
    conn = get_connection()
    try:
        data = what_if_margin(conn, req.project_id, req.recovery_amount)
        if not data:
            raise HTTPException(status_code=404, detail="Project not found")
        return data
    finally:
        conn.close()
