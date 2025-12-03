from fastapi.testclient import TestClient
from app_2 import app, safe_str, Plan, PlanDetails, load_data  # import app here

load_data()
client = TestClient(app)


# Test 1: safe_str
def test1():
    print("test1:", safe_str("hello"), safe_str(""), safe_str(float("nan")))


# Test 2: create a Plan model
def test2():
    p = Plan(
        plan_id="P1",
        plan_name="Test Plan",
        issuer_name="Issuer A",
        county="Dane",
        plan_type="PPO",
        deductible=None,
        coinsurance=None,
        annual_max=None,
        network_url=None,
        brochure_url=None,
        customer_service_local=None,
        customer_service_toll_free=None,
        customer_service_tty=None,
    )
    print("test2:", p)


# Test 3: PlanDetails extra_data logic (minimal)
def test3():
    pd = PlanDetails(
        plan_id="P1",
        plan_name="Test Plan",
        issuer_name="Issuer A",
        county="Dane",
        plan_type="PPO",
        brochure_url=None,
        network_url=None,
        rating_area=None,
        child_only_offering=None,
        metal_level=None,
        extra_data={"Routine Dental Services - Adult (Coverage)": "Yes"},
    )
    print("test3:", pd.extra_data)


# Test 4: endpoint – filters for WI
def test_filters_state_WI():
    r = client.get("/api/filters", params={"state": "WI"})
    print("test4 status:", r.status_code)
    if r.status_code == 200:
        data = r.json()
        print("test4 keys:", list(data.keys()))


# Test 5: endpoint – plans filtered by county
def test_plans_filter_county():
    r = client.get("/api/plans", params={"state": "WI", "county": "Dane"})
    print("test5 status:", r.status_code)
    if r.status_code == 200:
        plans = r.json()
        print("test5 count:", len(plans))
        if plans:
            print("test5 first county:", plans[0].get("county"))


if __name__ == "__main__":
    test1()
    test2()
    test3()
    test_filters_state_WI()
    test_plans_filter_county()
