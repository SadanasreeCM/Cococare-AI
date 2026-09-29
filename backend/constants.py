"""
CoconutCare — Fixed Static Agronomic Constants and Disclaimers.

Anti-hallucination guarantee: All agronomic thresholds, fixed lists,
and disclaimer texts are strictly defined here as static code structures.
"""

SOIL_TYPES = ["sandy", "loamy", "clayey", "red", "laterite"]

WATER_SOURCES = ["Well", "Borewell", "Canal", "Rainfed", "River/Stream"]

IRRIGATION_METHODS = ["Drip", "Basin", "Sprinkler", "Manual", "Flood"]

AGRONOMIC_DISCLAIMER = (
    "General guidance only — confirm with local agricultural extension services "
    "or a soil test before applying."
)

DEFAULT_TREE_SPACING_METERS = 7.5  # Standard 7.5m x 7.5m spacing for triangular/square planting
SQ_METERS_PER_ACRE = 4046.86
SQ_METERS_PER_HECTARE = 10000.0

# ---------------------------------------------------------------------------
# Static Defensible Soil Thresholds (Standard Agronomy References e.g. FAO/CDB)
# Anti-hallucination guarantee: Fixed ranges, never LLM-invented.
# ---------------------------------------------------------------------------
SOIL_RANGE_THRESHOLDS = {
    "ph": {
        "label": "Soil pH",
        "optimal_range": "5.5 – 7.5",
        "unit": "pH",
        "reference": "FAO Coconut Agronomy Guide / Coconut Development Board",
        "evaluator": lambda v: (
            "LOW (Acidic)" if v < 5.5 else ("GOOD (Optimal)" if v <= 7.5 else "HIGH (Alkaline)")
        ),
        "status_color": lambda v: (
            "#e76f51" if v < 5.5 else ("#2a9d8f" if v <= 7.5 else "#e9c46a")
        )
    },
    "nitrogen": {
        "label": "Nitrogen (N)",
        "optimal_range": "140 – 280",
        "unit": "kg/ha",
        "reference": "Standard Tropical Soil Testing Criteria",
        "evaluator": lambda v: (
            "LOW (Deficient)" if v < 140 else ("GOOD (Sufficient)" if v <= 280 else "HIGH (Excess)")
        ),
        "status_color": lambda v: (
            "#e76f51" if v < 140 else ("#2a9d8f" if v <= 280 else "#e9c46a")
        )
    },
    "phosphorus": {
        "label": "Phosphorus (P)",
        "optimal_range": "10 – 25",
        "unit": "kg/ha",
        "reference": "Standard Tropical Soil Testing Criteria",
        "evaluator": lambda v: (
            "LOW (Deficient)" if v < 10 else ("GOOD (Sufficient)" if v <= 25 else "HIGH (Excess)")
        ),
        "status_color": lambda v: (
            "#e76f51" if v < 10 else ("#2a9d8f" if v <= 25 else "#e9c46a")
        )
    },
    "potassium": {
        "label": "Potassium (K)",
        "optimal_range": "150 – 300",
        "unit": "kg/ha",
        "reference": "Critical for Palm Drought & Nut Development",
        "evaluator": lambda v: (
            "LOW (Deficient)" if v < 150 else ("GOOD (Sufficient)" if v <= 300 else "HIGH (Excess)")
        ),
        "status_color": lambda v: (
            "#e76f51" if v < 150 else ("#2a9d8f" if v <= 300 else "#e9c46a")
        )
    },
    "organic_carbon": {
        "label": "Organic Carbon",
        "optimal_range": "0.5 – 1.2",
        "unit": "%",
        "reference": "Soil Organic Matter Index for Palm Basins",
        "evaluator": lambda v: (
            "LOW (Needs Mulch/Compost)" if v < 0.5 else ("GOOD (Optimal)" if v <= 1.2 else "HIGH (Rich)")
        ),
        "status_color": lambda v: (
            "#e76f51" if v < 0.5 else ("#2a9d8f" if v <= 1.2 else "#2a9d8f")
        )
    }
}

# ---------------------------------------------------------------------------
# Static Recommended Fertilizer Activities by Age Bracket
# Anti-hallucination guarantee: Pre-written reference schedule, fixed data.
# ---------------------------------------------------------------------------
FERTILIZER_RECOMMENDATIONS_BY_AGE = {
    "0-3 years": [
        {
            "name": "Bi-Annual Organic Compost Application",
            "recommended_period": "May–June & Sept–Oct",
            "reason": "Promotes early root system architecture and soil water holding capacity.",
            "notes": "Apply in a 1m circular ring around palm base. Cover with dry leaves or mulch."
        },
        {
            "name": "Basal Green Manuring (Legume Intercropping)",
            "recommended_period": "June–July",
            "reason": "Fixes atmospheric nitrogen and suppresses weed emergence.",
            "notes": "Sow Sunnhemp or Cowpea seeds in palm basin; incorporate into soil at 50% flowering."
        },
        {
            "name": "Boron & Micronutrient Foliar Inspection",
            "recommended_period": "August",
            "reason": "Prevents young frond stunting and leaf hook symptoms.",
            "notes": "Check newly emerged spindle leaves for deformity or yellowing."
        }
    ],
    "3-6 years": [
        {
            "name": "Pre-Monsoon Organic Manure Ring Application",
            "recommended_period": "May–June",
            "reason": "Builds palm vigour ahead of initial inflorescence and flowering onset.",
            "notes": "Broad ring application 1.5m from trunk. Incorporate lightly into topsoil."
        },
        {
            "name": "Post-Monsoon Basin Aeration & Mulching",
            "recommended_period": "October–November",
            "reason": "Replenishes washed-out nutrients and prevents soil compaction.",
            "notes": "Fork basin gently around 1.5m radius; apply coconut husk or green leaves."
        },
        {
            "name": "Cover Crop Slashing & Incorporation",
            "recommended_period": "July–August",
            "reason": "Enriches soil organic carbon and nitrogen reserves.",
            "notes": "Slash legume cover crops into the basin soil before heavy rains end."
        }
    ],
    "6+ years": [
        {
            "name": "First Split Organic Fertilizer Application",
            "recommended_period": "May–June (Pre-Monsoon)",
            "reason": "Sustains heavy nut production, palm trunk girth, and inflorescence development.",
            "notes": "Apply in circular trench 2m radius from palm trunk during early monsoon moist soil."
        },
        {
            "name": "Second Split Organic & Potash Nutrient Application",
            "recommended_period": "September–October (Post-Monsoon)",
            "reason": "Supports nut weight, kernel thickness, and drought resistance.",
            "notes": "Ensure adequate soil moisture during basin application."
        },
        {
            "name": "Annual Soil pH & Magnesium Health Audit",
            "recommended_period": "December–January",
            "reason": "Monitors soil acidity and magnesium availability for leaf chlorophyll greening.",
            "notes": "Collect core soil samples from 0–30 cm depth around representative bearing trees."
        }
    ]
}

# ---------------------------------------------------------------------------
# Static Expense Categories & Palm Varieties (Fixed lists — Anti-hallucination)
# ---------------------------------------------------------------------------
EXPENSE_CATEGORIES = [
    "Fertilizers & Nutrients",
    "Irrigation & Water Supply",
    "Labor & Wages",
    "Pest & Weed Management",
    "Tools & Equipment Maintenance",
    "Seedlings & Saplings Purchase",
    "Harvesting & Transport",
    "Soil Testing & Diagnostics",
    "Miscellaneous Farm Overhead"
]

PALM_VARIETIES = [
    "West Coast Tall (WCT)",
    "East Coast Tall (ECT)",
    "Chowghat Orange Dwarf (COD)",
    "Malayan Yellow Dwarf (MYD)",
    "Hybrid (DxT / TxD)",
    "Local Tall Variety",
    "Other Variety"
]


