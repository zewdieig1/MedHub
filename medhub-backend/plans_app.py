from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import pandas as pd
import math

app = FastAPI(title="Wisco Dental Plans")
df_plans = None

# Templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

class Plan(BaseModel):
    plan_id: str
    plan_name: str
    issuer_name: str
    county: str
    plan_type: str
    deductible: Optional[str]
    coinsurance: Optional[str]
    annual_max: Optional[str]
    network_url: Optional[str]
    brochure_url: Optional[str]
    customer_service_local: Optional[str]
    customer_service_toll_free: Optional[str]
    customer_service_tty: Optional[str]

class PlanDetails(BaseModel):
    plan_id: str
    plan_name: str
    issuer_name: str
    county: str
    plan_type: str
    brochure_url: Optional[str]
    network_url: Optional[str]
    rating_area: Optional[str]
    child_only_offering: Optional[str]
    metal_level: Optional[str]
    extra_data: Dict[str, Any]

@app.on_event("startup")
def load_data():
    global df_plans
    df = pd.read_excel(
        "Individual_Market_Dental.xlsx",
        sheet_name="Individual_Market_Dental",
        header=1
    )
    df = df[df["State Code"].astype(str).str.strip().isin(["WI", "IL"])]
    df.columns = df.columns.str.strip()
    df_plans = df

def safe_str(val: Any) -> Optional[str]:
    if val is None:
        return None
    if isinstance(val, float) and math.isnan(val):
        return None
    s = str(val)
    if s.strip() == "":
        return None
    return s

@app.get("/plans", response_class=HTMLResponse)
async def plans_page(request: Request, state: Optional[str] = "WI"):
    return templates.TemplateResponse(
        "plans.html",
        {"request": request, "state": state}
    )

@app.get("/api/plans", response_model=List[Plan])
async def get_plans(
    state: Optional[str] = Query("WI"),
    county: Optional[str] = Query(None),
    issuer: Optional[str] = Query(None),
    plan_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    df = df_plans.copy()
    if state:
        df = df[df["State Code"].astype(str).str.strip() == state]
    if county:
        df = df[df["County Name"].astype(str).str.strip() == county]
    if issuer:
        df = df[df["Issuer Name"].astype(str).str.strip() == issuer]
    if plan_type:
        df = df[df["Plan Type"].astype(str).str.strip() == plan_type]
    if search:
        s = str(search)
        df = df[
            df["Plan Marketing Name"].astype(str).str.contains(s, case=False, na=False)
            | df["Issuer Name"].astype(str).str.contains(s, case=False, na=False)
            | df["Plan ID (Standard Component)"].astype(str).str.contains(s, case=False, na=False)
        ]

    plans: List[Plan] = []
    for _, row in df.iterrows():
        plans.append(
            Plan(
                plan_id=str(row["Plan ID (Standard Component)"]),
                plan_name=safe_str(row.get("Plan Marketing Name")),
                issuer_name=safe_str(row.get("Issuer Name")),
                county=safe_str(row.get("County Name")),
                plan_type=safe_str(row.get("Plan Type")),
                deductible=safe_str(row.get("Deductible")),
                coinsurance=safe_str(row.get("Coinsurance")),
                annual_max=safe_str(row.get("Annual Maximum")),
                network_url=safe_str(row.get("Network URL")),
                brochure_url=safe_str(row.get("Plan Brochure URL")),
                customer_service_local=safe_str(row.get("Customer Service Phone Number Local")),
                customer_service_toll_free=safe_str(row.get("Customer Service Phone Number Toll Free")),
                customer_service_tty=safe_str(row.get("Customer Service Phone Number TTY")),
            )
        )
    return plans

@app.get("/api/filters")
async def get_filters(state: Optional[str] = Query("WI")):
    df = df_plans.copy()
    df["Plan Type"] = df["Plan Type"].astype(str).str.strip()
    if state:
        df = df[df["State Code"].astype(str).str.strip() == state]
    counties = sorted(df["County Name"].dropna().astype(str).str.strip().unique().tolist())
    issuers = sorted(df["Issuer Name"].dropna().astype(str).str.strip().unique().tolist())
    plan_types = sorted(df["Plan Type"].dropna().unique().tolist())
    return {
        "counties": counties,
        "issuers": issuers,
        "plan_types": plan_types,
    }

@app.get("/api/plans/{plan_id}/details", response_model=PlanDetails)
async def get_plan_details(plan_id: str):
    row = df_plans[df_plans["Plan ID (Standard Component)"] == plan_id].iloc[0]

    plan_name = row.get("Plan Marketing Name", "")
    issuer_name = row.get("Issuer Name", "")
    county = row.get("County Name", "")
    plan_type = row.get("Plan Type", "")
    brochure_url = row.get("Plan Brochure URL")
    network_url = row.get("Network URL")
    rating_area = row.get("Rating Area")
    child_only_offering = row.get("Child Only Offering")
    metal_level = row.get("Metal Level")

    standard_fields = {
        "Plan ID (Standard Component)", "Plan Marketing Name", "Issuer Name",
        "County Name", "Plan Type", "Plan Brochure URL", "Network URL",
        "Rating Area", "Child Only Offering", "Metal Level", "State Code",
        "Deductible", "Coinsurance", "Annual Maximum"
    }

    coverage_cols = {
        "Routine Dental Services - Adult (Coverage)",
        "Basic Dental Care - Adult (Coverage)",
        "Major Dental Care - Adult (Coverage)",
        "Orthodontia - Adult (Coverage)",
        "Dental Check-Up for Children (Coverage)",
        "Basic Dental Care - Child (Coverage)",
        "Major Dental Care - Child (Coverage)",
        "Orthodontia - Child (Coverage)",
    }

    extra_data: Dict[str, Any] = {}

    for col in df_plans.columns:
        col_lower = str(col).lower()

        if col in standard_fields:
            continue
        if "premium" in col_lower:
            continue

        if col == "Summary of Benefits URL":
            val_raw = row.get(col)
            if pd.isna(val_raw) or val_raw == "":
                continue
            extra_data[col] = str(val_raw)
            continue

        val = row.get(col)

        if pd.isna(val) or val == "":
            if col in coverage_cols:
                extra_data[col] = "Not provided"
            continue

        if col in coverage_cols:
            if str(val).strip().upper() == "X":
                extra_data[col] = "Yes"
            else:
                extra_data[col] = str(val)
        else:
            extra_data[col] = str(val)

    return PlanDetails(
        plan_id=plan_id,
        plan_name=plan_name,
        issuer_name=issuer_name,
        county=county,
        plan_type=plan_type,
        brochure_url=brochure_url,
        network_url=network_url,
        rating_area=rating_area,
        child_only_offering=child_only_offering,
        metal_level=metal_level,
        extra_data=extra_data
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
