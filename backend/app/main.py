"""
EcoRestore Somalia backend (FastAPI).

Goal for MVP:
- Load district indicator data
- Compute Priority Score + risk category
- Recommend intervention package + expected impact
- Serve a tiny dashboard frontend (optional)

This file is intentionally kept as a scaffold with TODOs so the team can
fill in implementation during the hackathon.
"""

# from __future__ import annotations

# from fastapi import FastAPI

# app = FastAPI(title="EcoRestore Somalia API", version="0.0.1")

# TODO: (optional) serve the static frontend in `../frontend/`
# - mount StaticFiles for `/assets`
# - return `frontend/index.html` on `/`

# TODO: implement API routes the frontend can call:
# - GET `/api/districts` -> list districts with computed `priorityScore` + `riskCategory`
# - GET `/api/districts/{id}` -> one district + computed fields
# - GET `/api/districts/{id}/package` -> recommendations + impact + actionPlan
# - POST `/api/score` -> compute score for custom weights / indicators



from fastapi import FastAPI, HTTPException, Query

from sqlalchemy import (
    asc,
    create_engine,
    Column,
    Integer,
    Float,
    String,
    desc
)

from sqlalchemy.orm import (
    declarative_base,
    sessionmaker
)

import csv

# ==================================================
# CONFIG
# ==================================================

DATABASE_URL = "sqlite:///./database.db"

FOREST_CSV = "app/treecover_extent_2010_by_region__ha.csv"
REGIONS_CSV = "app/adm1_metadata.csv"

# ==================================================
# DATABASE
# ==================================================

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

Base = declarative_base()

# ==================================================
# MODELS
# ==================================================

class ForestData(Base):
    __tablename__ = "forest_data"

    id = Column(Integer, primary_key=True, index=True)

    iso = Column(String)
    adm1 = Column(Integer)

    umd_tree_cover_extent_2010_ha = Column(Float)
    area_ha = Column(Float)


class Region(Base):
    __tablename__ = "regions"

    adm1__id = Column(Integer, primary_key=True)
    name = Column(String)


# IMPORTANT:
# create tables AFTER all models exist
Base.metadata.create_all(bind=engine)

# ==================================================
# FASTAPI
# ==================================================

app = FastAPI()

# ==================================================
# IMPORT FOREST CSV
# ==================================================

@app.post("/import-forest")
async def import_forest():

    session = SessionLocal()

    try:

        with open(FOREST_CSV, "r", encoding="utf-8") as file:

            reader = csv.DictReader(file)

            records = []

            for row in reader:

                records.append(
                    ForestData(
                        iso=row["iso"],
                        adm1=int(row["adm1"]),
                        umd_tree_cover_extent_2010_ha=float(
                            row["umd_tree_cover_extent_2010__ha"]
                        ),
                        area_ha=float(
                            row["area__ha"]
                        )
                    )
                )

            session.bulk_save_objects(records)
            session.commit()

        return {
            "rows_inserted": len(records)
        }

    finally:
        session.close()

# ==================================================
# IMPORT REGIONS CSV
# ==================================================

@app.post("/import-regions")
async def import_regions():

    session = SessionLocal()

    try:

        with open(REGIONS_CSV, "r", encoding="utf-8") as file:

            reader = csv.DictReader(file)

            records = []

            for row in reader:

                records.append(
                    Region(
                        adm1__id=int(row["adm1__id"]),
                        name=row["name"]
                    )
                )

            session.bulk_save_objects(records)
            session.commit()

        return {
            "rows_inserted": len(records)
        }

    finally:
        session.close()

# ==================================================
# GET FOREST DATA
# ==================================================

@app.get("/forest")
async def get_forest():

    session = SessionLocal()

    try:

        rows = session.query(ForestData).all()

        return [
            {
                "id": row.id,
                "iso": row.iso,
                "adm1": row.adm1,
                "tree_cover": row.umd_tree_cover_extent_2010_ha,
                "area": row.area_ha
            }
            for row in rows
        ]

    finally:
        session.close()

# ==================================================
# GET REGIONS
# ==================================================

@app.get("/regions")
async def get_regions():

    session = SessionLocal()

    try:

        rows = session.query(Region).all()

        return [
            {
                "adm1__id": row.adm1__id,
                "name": row.name
            }
            for row in rows
        ]

    finally:
        session.close()

# ==================================================
# INNER JOIN
# ==================================================

# @app.get("/forest-with-regions")
# async def forest_with_regions():

#     session = SessionLocal()

#     try:

#         rows = (
#             session.query(
#                 ForestData.id,
#                 ForestData.iso,
#                 ForestData.adm1,
#                 ForestData.umd_tree_cover_extent_2010_ha,
#                 ForestData.area_ha,
#                 Region.name
#             )
#             .join(
#                 Region,
#                 ForestData.adm1 == Region.adm1__id
#             )
#             .all()
#         )

#         return [
#             {
#                 "id": row.id,
#                 "region": row.name,
#                 "iso": row.iso,
#                 "adm1": row.adm1,
#                 "tree_cover": row.umd_tree_cover_extent_2010_ha,
#                 "area": row.area_ha
#             }
#             for row in rows
#         ]

#     finally:
#         session.close()

# ==================================================
# DELETE FOREST RECORD
# ==================================================

@app.get("/forest-with-regions")
async def forest_with_regions(
    sort_by: str = Query("region"),
    order: str = Query("asc")
):

    session = SessionLocal()

    try:

        query = (
            session.query(
                ForestData.id,
                ForestData.iso,
                ForestData.adm1,
                ForestData.umd_tree_cover_extent_2010_ha,
                ForestData.area_ha,
                Region.name
            )
            .join(
                Region,
                ForestData.adm1 == Region.adm1__id
            )
        )

        columns = {
            "region": Region.name,
            "iso": ForestData.iso,
            "adm1": ForestData.adm1,
            "tree_cover": ForestData.umd_tree_cover_extent_2010_ha,
            "area": ForestData.area_ha
        }

        sort_column = columns.get(sort_by, Region.name)

        if order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        rows = query.all()

        return [
            {
                "id": row.id,
                "region": row.name,
                "iso": row.iso,
                "adm1": row.adm1,
                "tree_cover": row.umd_tree_cover_extent_2010_ha,
                "area": row.area_ha
            }
            for row in rows
        ]

    finally:
        session.close()

@app.delete("/forest/{record_id}")
async def delete_forest_record(record_id: int):

    session = SessionLocal()

    try:

        row = session.get(ForestData, record_id)

        if row is None:
            raise HTTPException(
                status_code=404,
                detail="Record not found"
            )

        session.delete(row)
        session.commit()

        return {
            "message": "Deleted"
        }

    finally:
        session.close()


