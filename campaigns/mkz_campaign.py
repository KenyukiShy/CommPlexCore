"""
arc-fleet-campaign/campaigns/mkz_campaign.py
2016 Lincoln MKZ Hybrid — rebuilt title, at Lucky's Towing since January 2026.

SPECIAL NOTE: Vehicle has been at Lucky's since January 2026 (now April 2026).
Lucky's Towing has NOT successfully issued us notice. First outreach should include
a transparent offer to sell directly to Lucky's at a disclosed price, with an apology
for the delay in our own outreach efforts.
"""

from .base_campaign import BaseCampaign, Contact
from typing import List, Dict


# ── Lucky's Towing direct offer ──────────────────────────────────────────────
LUCKYS_OFFER_AMOUNT = "$2,500"   # Offer to Lucky's for direct purchase
LUCKYS_MARKET_VALUE = "$5,500"   # What we could get from dealers — disclosed

LUCKYS_OFFER_MESSAGE = f"""Hello,

My name is Kenyon Jones. I'm the owner of the 2016 Lincoln MKZ Hybrid (VIN: 3LN6L2LUXGR630397)
currently on your lot at Lucky's Towing & Repair, 812 2nd St NW, Beulah ND 58523.

First — I want to apologize. The vehicle has been in your care since January 2026 and I have not
reached out sooner than I should have. I'm working to resolve this as quickly as possible and
I appreciate your patience.

DIRECT PURCHASE OFFER TO LUCKY'S:
I want to give you the first option. I am actively marketing this vehicle to dealers who are
offering in the range of $3,500–$5,500 for a rebuilt-title MKZ with this mileage. Clean-title
comps run $9,000+.

I'd like to offer Lucky's the opportunity to purchase the vehicle directly at {LUCKYS_OFFER_AMOUNT},
which saves us both the hassle of a third-party sale and lets you retain any upside if you choose
to resell or use the vehicle. This is a transparent, fair offer — you know exactly what the market
is paying.

VEHICLE:
• VIN: 3LN6L2LUXGR630397
• Year/Make/Model: 2016 Lincoln MKZ Hybrid
• Mileage: ~100,000 | Color: Beige | Trim: Select/Premier
• Title: Rebuilt (Previously Salvaged ND brand) — Bonded title in process (NDCC §39-05-20.3)
• Battery: 12V auxiliary needs deep-cycle recharge (~$100). Hybrid drivetrain fully unaffected.
• Features: Leather heated seats, wood trim, 8\" SYNC 3, backup camera, push-button start
• Fuel Economy: 41 MPG city / 39 MPG highway

OWNERSHIP DOCUMENTATION (complete packet available):
• Signed CA Bill of Sale, Zelle payment records ($4,995), bank statements
• Transport confirmation, active ND GEICO insurance

If you're not interested in purchasing directly, I completely understand. In that case, I'd like
to arrange removal of the vehicle within the next 10 days and would appreciate your patience in
the meantime.

Please reply or call/text:
Kenyon Jones | (701) 870-5235 | kjonesmle@gmail.com
Cynthia Ennis (authorized) | (701) 946-5731

Thank you again for your care of the vehicle.
"""

TIER1_INSTANT = """Hello,

I have a 2016 Lincoln MKZ Hybrid for sale and would like to know if you are interested in making an offer.

VEHICLE:
• VIN: 3LN6L2LUXGR630397
• Mileage: ~100,000 | Color: Beige | Trim: Select/Premier
• Title: Rebuilt (Previously Salvaged ND brand)
• Battery: 12V auxiliary needs recharge (~$100 fix). Hybrid drivetrain unaffected.

LOCATION: Lucky's Towing & Repair, 812 2nd St NW, Beulah ND 58523.
Transport can be arranged after offer agreed.

Kenyon Jones | (701) 870-5235 | kjonesmle@gmail.com
Cynthia Ennis (authorized) | (701) 946-5731"""

TIER2_REBUILT = """Hello,

I understand you may work with rebuilt or salvage title vehicles. I have a 2016 Lincoln MKZ Hybrid for sale.

VEHICLE:
• VIN: 3LN6L2LUXGR630397
• Mileage: ~100,000 | Color: Beige | Trim: Select/Premier
• Features: Leather heated seats, wood trim, 8\" SYNC 3, backup camera, push-button start
• Fuel Economy: 41 MPG city / 39 MPG highway
• Title: Rebuilt (Previously Salvaged ND brand)
• Battery: 12V auxiliary needs recharge (~$100 fix). Hybrid drivetrain fully unaffected.

OWNERSHIP: Signed CA Bill of Sale, Zelle payment records ($4,995), bank statements,
transport confirmation, active ND GEICO insurance. Bonded title in process (NDCC §39-05-20.3).

LOCATION: Lucky's Towing & Repair, 812 2nd St NW, Beulah ND 58523.
Open to direct purchase, consignment, or lot pickup. Flexible for the right buyer.

Kenyon Jones | (701) 870-5235 | kjonesmle@gmail.com
Cynthia Ennis (authorized) | (701) 946-5731"""

TIER3_LOCAL = """Hello,

I have a 2016 Lincoln MKZ Hybrid for sale and would like to know if you are interested in making an offer.

VEHICLE:
• VIN: 3LN6L2LUXGR630397
• Mileage: ~100,000 | Fuel Economy: 41 MPG city / 39 MPG highway
• Color: Beige | Trim: Select/Premier
• Features: Leather heated seats, wood trim, 8\" SYNC 3, backup camera, push-button start
• Title: Rebuilt (Previously Salvaged ND brand)
• Battery: 12V auxiliary needs recharge (~$100 fix). Hybrid drivetrain fully unaffected.

Complete documentation available. Transport can be arranged after offer agreed.
Clean-title comparables $9,000+. Priced well below that.

Kenyon Jones | (701) 870-5235 | kjonesmle@gmail.com
Cynthia Ennis (authorized) | (701) 946-5731"""

DEFAULT = """Hello,

I have a 2016 Lincoln MKZ Hybrid for sale and would like to know if you are interested in making an offer.

VEHICLE:
• VIN: 3LN6L2LUXGR630397
• Mileage: ~100,000 | Color: Beige | Trim: Select/Premier
• Features: Leather heated seats, wood trim, 8\" SYNC 3, backup camera, push-button start
• Fuel Economy: 41 MPG city / 39 MPG highway
• Title: Rebuilt (Previously Salvaged ND brand)
• Battery: 12V auxiliary needs recharge (~$100 fix). Hybrid drivetrain unaffected.

OWNERSHIP: Complete documentation packet available — signed CA Bill of Sale, Zelle payment records ($4,995),
bank statements, transport confirmation, active ND GEICO insurance. Bonded title in process (NDCC §39-05-20.3).

LOCATION: Lucky's Towing & Repair, 812 2nd St NW, Beulah ND 58523.
Transport can be arranged after offer agreed.

Clean-title comparables $9,000+. Priced well below that — flexible for the right buyer.

Kenyon Jones | (701) 870-5235 | kjonesmle@gmail.com
Cynthia Ennis (authorized) | (701) 946-5731"""


class MKZCampaign(BaseCampaign):
    CAMPAIGN_ID = "MKZ_2016_HYBRID"
    VERSION = "3.0"

    @property
    def vehicle_info(self) -> Dict:
        return {
            "display":     "2016 Lincoln MKZ Hybrid",
            "year":        "2016",
            "make":        "Lincoln",
            "model":       "MKZ Hybrid",
            "vin":         "3LN6L2LUXGR630397",
            "mileage":     "~100,000",
            "color":       "Beige / Champagne",
            "trim":        "Select/Premier",
            "title":       "Rebuilt (Previously Salvaged ND)",
            "location":    "Lucky's Towing & Repair, 812 2nd St NW, Beulah ND 58523",
            "location_phone": "(701) 870-1613",
            "asking":      "$5,500",
            "range_low":   "$3,500",
            "range_high":  "$5,500",
            "note":        "At Lucky's since January 2026 — priority removal needed",
            "alert":       "LUCKY'S OFFER PENDING — send Lucky's message FIRST",
        }

    @property
    def messages(self) -> Dict[str, str]:
        return {
            "LUCKY_OFFER":    LUCKYS_OFFER_MESSAGE,
            "TIER1_INSTANT":  TIER1_INSTANT,
            "TIER2_REBUILT":  TIER2_REBUILT,
            "TIER3_LOCAL":    TIER3_LOCAL,
            "DEFAULT":        DEFAULT,
        }

    @property
    def priority_contacts(self) -> List[Contact]:
        return [
            Contact(
                name="Lucky's Towing & Repair",
                email=None,            # No email on file — call/visit
                phone="7018701613",
                tier="LUCKY_OFFER",
                method="phone",        # Phone call first, then in-person
                notes="Vehicle on lot since Jan 2026. Offer direct purchase at $2,500. Apologize for delay.",
            ),
        ]

    @property
    def contacts(self) -> List[Contact]:
        return self.priority_contacts + [
            # Tier 1 — Instant cash / salvage
            Contact("Peddle",               url="https://www.peddle.com/sell-my-car",                tier="TIER1_INSTANT", method="form"),
            Contact("AutoSavvy",            url="https://app.autosavvy.com",                         tier="TIER2_REBUILT", method="form"),
            # Tier 2 — Rebuilt specialists
            Contact("The Homework Guy",     url="https://thehomeworkguy.com/contact-us/",            tier="TIER2_REBUILT", method="form"),
            Contact("Dan Porter Motors",    url="https://www.dpmotors.com/contact",                  tier="TIER2_REBUILT", method="form"),
            Contact("Ken's Auto Body",      url="https://kensautobody.com/contact",                  tier="TIER2_REBUILT", method="form"),
            # Tier 3 — Local dealers
            Contact("Autorama Dickinson",   email="autoramadickinson@gmail.com",                     tier="TIER3_LOCAL",   method="email"),
            Contact("Gerald Wetzel Motors", url="https://www.geraldwetzel.com/contact",              tier="TIER3_LOCAL",   method="form"),
            Contact("Heiser Motors",        url="https://heisermotors.com/contact-us",               tier="TIER3_LOCAL",   method="form"),
            Contact("Valley Imports",       url="https://www.valleyimports.com/contact.htm",         tier="TIER3_LOCAL",   method="form"),
            Contact("The Auto Spot Fargo",  url="https://theautospotfargo.com/contact",              tier="TIER3_LOCAL",   method="form"),
            Contact("Torgerson Auto",       url="https://torgersonautocenter.com/contact",           tier="TIER3_LOCAL",   method="form"),
            Contact("Rides Auto Sales",     url="https://www.rides-autosales.com/contact",           tier="TIER3_LOCAL",   method="form"),
            # Tier 4 — Email-only direct
            Contact("Peak Auto — Cliff",    email="cliff@peakautogroup.com",                         tier="DEFAULT",       method="email"),
            Contact("Exotic Motors — Danny",email="danny@exoticmotorsag.com",                        tier="DEFAULT",       method="email"),
            # Tier 4 — National / misc
            Contact("Zara Auto Sales",      url="https://zaraauto.net/contact",                      tier="DEFAULT",       method="form"),
            Contact("Iowa Auto Exchange",   url="https://iowaautoexchange.com/contact",              tier="DEFAULT",       method="form"),
            Contact("Luxury Auto Selection",url="https://luxuryautoselection.com/contact",           tier="DEFAULT",       method="form"),
            Contact("Trust N Ride",         url="https://trustnride.net/contact",                    tier="DEFAULT",       method="form"),
            Contact("ONYX Automotive",      url="https://onyxautomotive.com/contact",                tier="DEFAULT",       method="form"),
            Contact("Empire Auto Sales",    url="https://www.empireautosf.com/contact",              tier="DEFAULT",       method="form"),
            Contact("Big City Motors",      url="https://bigcitymotors.biz/contact",                 tier="DEFAULT",       method="form"),
            Contact("Mainstreet Motor Co",  url="https://mainstreetmotor.com/contact",               tier="DEFAULT",       method="form"),
            Contact("Royal Drive Autos",    url="https://royaldriveautos.com/contact",               tier="DEFAULT",       method="form"),
            Contact("AutoValley",           url="https://theautovalley.com/contact",                 tier="DEFAULT",       method="form"),
            Contact("Efkamp Auto Sales",    url="https://efkampautos.com/contact",                   tier="DEFAULT",       method="form"),
            Contact("Dana Motors",          url="https://danamotors.com/contact",                    tier="DEFAULT",       method="form"),
            Contact("Exotic Motors Midwest",url="https://exoticmotorsag.com/contact",               tier="DEFAULT",       method="form"),
            Contact("Indy Luxury",          url="https://indyluxurymotorsports.com/contact",         tier="DEFAULT",       method="form"),
            Contact("Fishers Imports",      url="https://fishersimports.com/contact",                tier="DEFAULT",       method="form"),
            Contact("Peak Automotive",      url="https://peakautogroup.com/contact",                 tier="DEFAULT",       method="form"),
            Contact("Capital City Motor",   url="https://capitalcitymotorworx.com/contact",          tier="TIER3_LOCAL",   method="form"),
        ]
