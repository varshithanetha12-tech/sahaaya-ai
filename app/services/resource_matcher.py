from typing import List, Optional
from app.models.schemas import SupportResource, SupportServiceType

RESOURCES_DATABASE: List[SupportResource] = [
    SupportResource(
        id="RES-001",
        name="Telangana State Legal Services Authority (TSLSA)",
        category=SupportServiceType.LEGAL_AID,
        state="Telangana",
        district="Hyderabad",
        phone="040-23446723 / 15100",
        email="tslsa-hyd@nic.in",
        address="City Civil Court Complex, Purani Haveli, Hyderabad - 500002",
        available_24x7=True,
        languages=["Telugu", "Hindi", "English", "Urdu"],
        verified=True,
        active_capacity="Available"
    ),
    SupportResource(
        id="RES-002",
        name="Tele-MANAS Psychological Support Center",
        category=SupportServiceType.COUNSELLING,
        state="Telangana",
        district="Hyderabad",
        phone="14416 / 1800-891-4416",
        email="telemanas.ts@gov.in",
        address="Institute of Mental Health, Erragadda, Hyderabad - 500018",
        available_24x7=True,
        languages=["Telugu", "Hindi", "English", "Tamil", "Kannada"],
        verified=True,
        active_capacity="Available"
    ),
    SupportResource(
        id="RES-003",
        name="District Atrocity Protection Cell & Nodal Officer",
        category=SupportServiceType.POLICE,
        state="Telangana",
        district="Rangareddy",
        phone="040-27852435 / 112",
        email="nodal-atrocity.rr@tspolice.gov.in",
        address="Collectorate Complex, Lakdikapul, Hyderabad / Rangareddy",
        available_24x7=True,
        languages=["Telugu", "Hindi", "English"],
        verified=True,
        active_capacity="High Priority Dispatch Ready"
    ),
    SupportResource(
        id="RES-004",
        name="National Helpline for Prevention of Atrocities (NHPA)",
        category=SupportServiceType.EMERGENCY,
        state="All India",
        district="Central Toll-Free",
        phone="14566 (Toll-Free 24x7)",
        email="nhpa-support@gov.in",
        address="Ministry of Social Justice & Empowerment, Shastri Bhawan, New Delhi",
        available_24x7=True,
        languages=["Telugu", "Hindi", "Tamil", "Kannada", "Malayalam", "Marathi", "Bengali", "Gujarati", "Odia", "English"],
        verified=True,
        active_capacity="National Dispatch Active"
    ),
    SupportResource(
        id="RES-005",
        name="District Legal Aid Defense Counsel System (DLADCS)",
        category=SupportServiceType.LEGAL_AID,
        state="Andhra Pradesh",
        district="Visakhapatnam",
        phone="0891-2564890 / 15100",
        email="dladcs.vsp@ap.gov.in",
        address="District Court Complex, Visakhapatnam - 530002",
        available_24x7=False,
        languages=["Telugu", "English", "Odia"],
        verified=True,
        active_capacity="Available"
    ),
    SupportResource(
        id="RES-006",
        name="One Stop Crisis Centre (Sakhi Center)",
        category=SupportServiceType.EMERGENCY,
        state="Telangana",
        district="Warangal",
        phone="0870-2443100 / 181",
        email="sakhi.warangal@wcd.gov.in",
        address="MGM Hospital Road, Warangal - 506002",
        available_24x7=True,
        languages=["Telugu", "Hindi", "English"],
        verified=True,
        active_capacity="Immediate Shelter & Triage"
    ),
    SupportResource(
        id="RES-007",
        name="NIMHANS Atrocity Trauma & Distress Triage Unit",
        category=SupportServiceType.COUNSELLING,
        state="Karnataka",
        district="Bengaluru Urban",
        phone="080-46110007 / 080-26995000",
        email="trauma-triage@nimhans.ac.in",
        address="Hosur Road, Lakkasandra, Bengaluru - 560029",
        available_24x7=True,
        languages=["Kannada", "Telugu", "Tamil", "Hindi", "English"],
        verified=True,
        active_capacity="Specialized Trauma Care"
    ),
    SupportResource(
        id="RES-008",
        name="District Social Welfare & Rehabilitation Directorate",
        category=SupportServiceType.REHABILITATION,
        state="Maharashtra",
        district="Pune",
        phone="020-26127814",
        email="socialwelfare.pune@maharashtra.gov.in",
        address="Dr. Babasaheb Ambedkar Bhavan, Camp, Pune - 411001",
        available_24x7=False,
        languages=["Marathi", "Hindi", "English"],
        verified=True,
        active_capacity="Relief Disbursement Open"
    ),
    SupportResource(
        id="RES-009",
        name="State Witness Protection Authority Cell",
        category=SupportServiceType.WITNESS_PROTECTION,
        state="Telangana",
        district="Hyderabad",
        phone="040-23454321 / Extension 402",
        email="witness-protection@tspolice.gov.in",
        address="DGP Office Complex, Saifabad, Hyderabad - 500004",
        available_24x7=True,
        languages=["Telugu", "Hindi", "English"],
        verified=True,
        active_capacity="Confidential Protocol"
    ),
    SupportResource(
        id="RES-010",
        name="District Emergency Medical & Trauma Center (OSDU)",
        category=SupportServiceType.MEDICAL,
        state="Telangana",
        district="Hyderabad",
        phone="108 / 040-24600121",
        email="osdu.osmania@telangana.gov.in",
        address="Osmania General Hospital, Afzal Gunj, Hyderabad - 500012",
        available_24x7=True,
        languages=["Telugu", "Hindi", "Urdu", "English"],
        verified=True,
        active_capacity="Trauma ICU Ready"
    )
]

class ResourceMatcherService:
    @classmethod
    def search_resources(
        cls,
        state: Optional[str] = None,
        district: Optional[str] = None,
        category: Optional[str] = None,
        language: Optional[str] = None,
        available_24x7: Optional[bool] = None
    ) -> List[SupportResource]:
        results = RESOURCES_DATABASE

        if state and state.lower() != "all" and state.lower() != "all india":
            results = [r for r in results if r.state.lower() == state.lower() or r.state == "All India"]

        if district and district.lower() != "all":
            results = [r for r in results if r.district.lower() == district.lower() or r.district == "Central Toll-Free"]

        if category and category.lower() != "all":
            results = [r for r in results if r.category.value.lower() == category.lower()]

        if language and language.lower() != "all":
            results = [r for r in results if any(l.lower() == language.lower() for l in r.languages)]

        if available_24x7 is not None and available_24x7 is True:
            results = [r for r in results if r.available_24x7]

        return results
