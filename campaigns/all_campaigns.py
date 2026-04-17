"""
arc-fleet-campaign/campaigns/towncar_campaign.py
1988 Lincoln Town Car Signature — 31,511 miles, Hazen/Beulah ND
BaT target: $10,000–$14,000
"""
from .base_campaign import BaseCampaign, Contact
from typing import List, Dict

DEFAULT = """Hello,

I have a 1988 Lincoln Town Car Signature Series for sale — 31,511 actual, original miles.
This is a genuine time capsule survivor in Oxford White. I believe it is a strong Bring a Trailer candidate.

VEHICLE:
• VIN: 1LNBM82FXJY779113
• Year / Trim: 1988 Lincoln Town Car — Signature Series (top trim)
• Mileage: 31,511 — Actual, Original, Verified
• Engine: 5.0L HO V8 (Ford 302) | AOD 4-Speed Automatic
• Exterior: Oxford White — Full Black Landau Vinyl Roof (excellent condition)
• Wheels: Styled Wire Spoke Wheels | Whitewall Tires — All Four
• Interior: Twin Comfort Lounge Split-Bench | Signature Luxury Cloth (Navy Blue)
  Genuine Burl Wood-Grain Accents | 6-Way Power Driver Seat | Dual-Zone Climate
• Title: Clean North Dakota Title — Zero Liens

DISCLOSED ITEMS (fully factored into pricing):
• Driver door interior panel: dry rot — cosmetic (~$200–$300)
• Driver window module: fuse/module repair (~$80–$150)
• A/C: needs R134a recharge (~$120–$180)
• Suspension: on springs (air ride not reinstalled) — drives fine
• Total estimated service: $500–$700

BaT COMPARABLE SALES:
• 31k-mile 1987 Sail America: $10,512 | 22k-mile 1989: $19,300 | 34k-mile 1988: $8,201
• Our target with proper presentation: $10,000–$14,000. Reserve recommendation: $9,500.

LOCATION: Hazen / Beulah, North Dakota. Inspection by appointment.
18-photo gallery available. Full BaT submission package ready.

Kenyon Jones | (701) 870-5235 | kjonesmle@gmail.com
Cynthia Ennis (authorized) | (701) 946-5731"""

BAT_PARTNER = """Hello,

I'm reaching out because I have a strong Bring a Trailer candidate I believe would be a fit for your program.

1988 LINCOLN TOWN CAR SIGNATURE SERIES — 31,511 ACTUAL MILES
VIN: 1LNBM82FXJY779113 | Clean North Dakota Title

This is a documented time capsule. 31,511 miles on a 1988 Signature (top trim) in Oxford White with
the Landau vinyl roof and wire spoke wheels. No rust, no panel damage, excellent Luxury Cloth interior.
The V8 starts and runs without issue.

Disclosed items: dry rot on driver door panel (cosmetic), window module repair, A/C recharge, and
suspension on springs. Total service estimate: $500–$700, fully disclosed. Comps on BaT:
30k-mile 1987 at $10,512; 22k-mile 1989 at $19,300. I'm targeting $10,000–$14,000 with reserve at $9,500.

18-photo catalog and complete documentation available immediately.

LOCATION: Hazen/Beulah, North Dakota.
I coordinate remotely and can arrange transport to your facility.

Am I reaching the right person for consignment inquiries?

Kenyon Jones | (701) 870-5235 | kjonesmle@gmail.com
Cynthia Ennis (authorized) | (701) 946-5731"""


class TownCarCampaign(BaseCampaign):
    CAMPAIGN_ID = "TOWNCAR_1988_SIGNATURE"

    @property
    def vehicle_info(self) -> Dict:
        return {
            "display":   "1988 Lincoln Town Car Signature",
            "vin":       "1LNBM82FXJY779113",
            "mileage":   "31,511",
            "color":     "Oxford White / Black Landau",
            "title":     "Clean ND Title",
            "location":  "Hazen / Beulah, North Dakota",
            "asking":    "$12,000",
            "bat_range": "$10,000–$14,000",
            "reserve":   "$9,500",
        }

    @property
    def messages(self) -> Dict[str, str]:
        return {
            "BAT_PARTNER": BAT_PARTNER,
            "DEFAULT":     DEFAULT,
        }

    @property
    def priority_contacts(self) -> List[Contact]:
        return [
            Contact("BaT Local Partners Email",  email="localpartners@bringatrailer.com", tier="BAT_PARTNER", method="email"),
            Contact("Motorcar Classics",          email="info@motorcarcl​assics.com",       tier="BAT_PARTNER", method="email",
                    notes="Cash offer this week $9k-$13k range — worth a call"),
            Contact("Hagerty / Hemmings",         email="consign@hagerty.com",             tier="BAT_PARTNER", method="email"),
        ]

    @property
    def contacts(self) -> List[Contact]:
        return self.priority_contacts + [
            Contact("Throttlestop",    email="info@throttlestop.com",  phone="9208762277", tier="BAT_PARTNER", method="email",
                    notes="BaT Local Partner — Elkhart Lake WI"),
            Contact("Black Mountain",  email="John@blackmountainmotorworks.com", tier="BAT_PARTNER", method="email",
                    notes="BaT Local Partner — Denver CO"),
            Contact("Vantage Auto",    url="https://vantageauto.com",  tier="DEFAULT", method="form",
                    notes="BaT Local Partner — NJ"),
            Contact("BaT Submit",      url="https://bringatrailer.com/submit-a-vehicle/", tier="DEFAULT", method="form",
                    notes="Direct BaT submission — attach 50+ photos"),
            Contact("Cars & Bids",     url="https://carsandbids.com",  tier="DEFAULT", method="form",
                    notes="Backup to BaT — modern enthusiasts"),
            Contact("eBay Motors",     url="https://www.ebay.com/motors", tier="DEFAULT", method="form"),
        ]


# ─────────────────────────────────────────────────────────────────────────────

"""
arc-fleet-campaign/campaigns/f350_campaign.py
2006 Ford F-350 King Ranch V10 — 47,000 miles, Douglasville GA
"""

F350_DEFAULT = """Hello,

My name is Kenyon Jones. I have a 2006 Ford F-350 Super Duty King Ranch for sale and I believe
it may be a strong candidate for your consignment or auction program.

THE TRUCK:
• VIN: 1FTWW31Y86EA12357 | Clean Georgia Title
• Year / Trim: 2006 F-350 Super Duty — King Ranch Edition (top trim)
• Engine: 6.8L Triton V10 Gas | 6-Speed SelectShift Automatic
• Cab / Bed: Crew Cab 4-Door / Long Bed (8 ft) with Bed Cap / Topper
• Drivetrain: 4×4 Selectable | Tow Capacity: ~18,000 lbs GCWR
• Mileage: ~47,000 Actual Miles — Verified
• Exterior: Oxford White
• Interior: King Ranch Saddle Brown Full Leather — Heated Front Seats | Power Everything
  King Ranch embossed medallion | Genuine wood-grain accents
• Tow Package: Factory 5th Wheel Kingpin Hitch — pre-wired, day-1 ready

THE STORY: This truck spent its entire life towing a single fifth wheel trailer.
It was never a daily driver or work truck. 47,000 miles on a 2006 F-350 King Ranch
is a genuine standout. Finding a clean V10 King Ranch in long bed/crew cab with this
mileage is nearly impossible. This is the truck for the buyer who wants 1-ton King Ranch
aesthetics and capacity without 6.0L Power Stroke maintenance concerns.

PRE-LISTING PREP NEEDED (transparent disclosure):
• Professional detail and wash (paint is in good shape)
• Standard tune-up (plugs, filter, fluid check)
• Tire inspection
• Estimated total: $400–$900

COMPARABLE BaT SALES: 2006 F-350 Lariat Crew Cab diesel at $21,000; 2006 F-250 Lariat diesel at $24,250.
King Ranch trim above Lariat in all comps. Our realistic range: $20,000–$30,000. Reserve: $18,000.

LOCATION: Douglasville, GA 30134.
On-site contacts: Doug & Sherrie Appleby (770-315-1949) — available for inspection, photos, coordination.

I am open to consignment, BaT partnership, or direct sale. Fully prepared to list truck and trailer
as two separate auctions if that maximizes value.

Kenyon Jones | (701) 870-5235 | kjonesmle@gmail.com
Cynthia Ennis (authorized) | (701) 946-5731"""

F350_BAT_UNICORN = """Hello,

I'm reaching out because I have what I believe is a rare Bring a Trailer candidate currently
stored in Douglasville, Georgia.

2006 FORD F-350 KING RANCH V10 — THE "UNICORN" SPEC
• Crew Cab, 8-ft Long Bed, Single Rear Wheel, 4×4
• 47,000 original miles. Clean Georgia Title. Zero accidents.
• 6.8L Triton V10 — No diesel headaches, no 6.0L risk
• Factory 5th Wheel Kingpin Hitch installed

Why BaT: This is for the collector who wants the King Ranch aesthetic and 1-ton capacity
and specifically avoids the diesel. A clean, low-mile V10 King Ranch in this configuration
is nearly impossible to find. The truck spent its entire life towing one fifth wheel —
never a daily driver.

I understand the V10 trades differently than the diesel. I am not chasing an unrealistic number;
I am looking for a market-correct result for a rare, survivor-grade truck.

I also have a 2017 Jayco Eagle HT 26.5BHS (4-season bunkhouse, ~2,400 miles) stored at the
same location. I am fully prepared to list them as two separate, consecutive auctions if that
maximizes value for the truck.

Photos, documentation, and on-site access available through Doug & Sherrie Appleby (770-315-1949)
in Douglasville. I am ready to sign and transport immediately.

Kenyon Jones | (701) 870-5235 | kjonesmle@gmail.com"""


class F350Campaign(BaseCampaign):
    CAMPAIGN_ID = "F350_2006_KING_RANCH"

    @property
    def vehicle_info(self) -> Dict:
        return {
            "display":    "2006 Ford F-350 King Ranch V10",
            "vin":        "1FTWW31Y86EA12357",
            "mileage":    "~47,000",
            "color":      "Oxford White",
            "title":      "Clean GA Title",
            "location":   "Douglasville, GA",
            "onsite":     "Doug & Sherrie Appleby | (770) 315-1949",
            "asking":     "$27,500",
            "bat_range":  "$20,000–$30,000",
            "reserve":    "$18,000",
        }

    @property
    def messages(self) -> Dict[str, str]:
        return {
            "BAT_UNICORN": F350_BAT_UNICORN,
            "DEFAULT":     F350_DEFAULT,
        }

    @property
    def priority_contacts(self) -> List[Contact]:
        return [
            Contact("BaT Local Partners",    email="localpartners@bringatrailer.com", tier="BAT_UNICORN", method="email"),
            Contact("The Patina Group NC",   email=None, phone=None,
                    url="https://www.bringatrailer.com/local-partners/",
                    tier="BAT_UNICORN", method="form",
                    notes="Statesville NC — closest BaT partner to Douglasville GA (~330mi). Added April 2025."),
            Contact("RK Motors Charlotte",   email=None, phone="7045965211",
                    url="https://rkmotors.com",
                    tier="BAT_UNICORN", method="email",
                    notes="Charlotte NC ~240mi — huge classic car dealer, professional"),
            Contact("Bullet Motorsports",    email="sales@bulletmotorsport.com", phone="9543632261",
                    tier="BAT_UNICORN", method="email",
                    notes="Fort Lauderdale FL — BaT partner, good for truck"),
            Contact("Gulf Coast Exotic",     email=None, phone=None,
                    tier="BAT_UNICORN", method="email",
                    notes="Gulfport MS ~370mi — BaT partner, added April 2025"),
        ]

    @property
    def contacts(self) -> List[Contact]:
        return self.priority_contacts + [
            Contact("GAA Classic Cars",   url="https://www.gaaclassiccars.com/how-to-sell",   tier="DEFAULT", method="form",
                    notes="Greensboro NC — July 23-25 2026. Best summer option."),
            Contact("Vicari Auction",     url="https://vicariauction.com/sell-a-car/",         tier="DEFAULT", method="form",
                    notes="Biloxi MS May 1-2 2026. Deadline: consign NOW."),
            Contact("Mecum Auctions",     url="https://www.mecum.com/consign/",               tier="DEFAULT", method="form"),
            Contact("BaT Direct Submit",  url="https://bringatrailer.com/submit-a-vehicle/",  tier="DEFAULT", method="form"),
            Contact("Cars & Bids",        url="https://carsandbids.com",                      tier="DEFAULT", method="form"),
        ]


# ─────────────────────────────────────────────────────────────────────────────

"""
arc-fleet-campaign/campaigns/jayco_campaign.py
2017 Jayco Eagle HT 26.5BHS — ~2,400 miles, Douglasville GA
Corral Sales Mandan ND primary channel; no BaT (BaT doesn't take 5th wheels)
"""

JAYCO_DEFAULT = """Hello,

My name is Kenyon Jones. I have a 2017 Jayco Eagle HT 26.5BHS Four-Season Bunkhouse Fifth Wheel
for sale — approximately 2,400 actual tow miles — and I believe it may be a strong fit for your program.

UNIT:
• VIN: 1UJCJ0BPXH1P20237 | GA Title #770175206127980 — Clean, Zero Liens
• Mileage: ~2,400 actual tow miles — essentially new use
• GVWR / UVW: 9,950 lbs / 7,582 lbs | Hitch Weight: 1,370 lbs — Half-ton towable
• Four-Season: Jayco Climate Shield — fully enclosed heated underbelly rated to 0°F
  PEX plumbing, double-layer fiberglass insulation, forced-air heated underbelly tank system
• Floorplan: Rear bunkhouse — double-over-double bunks, private bath, sleeps 8–10
• Slide: Single living area — dinette and hide-a-bed sofa
• Kitchen: 3-burner range, microwave, 8 cu ft gas/electric refrigerator
• Full Bath: Walk-in shower with skylight | Porcelain toilet | Dual exterior access
• Systems: Lippert auto-level | MORryde CRE-3000 suspension | Electric 18-ft patio awning w/ LED
• Interior: Extra Clean 9/10 — no water damage, smoke, pets, or odors
• Southeast stored — ZERO road salt. Currently in Douglasville, GA.

DISCLOSED ITEMS (transparent, fully factored into pricing):
• Tires: Full tread, 2017 DOT date code — age-recommend replacement (~$600–$800)
• Underbelly: Localized coroplast repair at one entry point, frame unaffected (~$293)
• Lippert rear auto-level jacks disengaged — front jacks and slide fully operational
• One cabinet hinge needs re-hanging (~$50)
• Total disclosed: ~$950–$1,200

ASKING: $26,500 as-is | $28,000–$30,000 if staged and issues addressed

LOCATION: Douglasville, GA.
On-site contacts: Doug & Sherrie Appleby (770-315-1949).
Full 29-photo catalog, Sherrie walkthrough video, systems documentation available on request.

NOTE ON MARKET: Climate Shield is not optional in ND/SD/MT — it's a survival requirement.
Zero competing 26.5BHS bunkhouse units in ND as of spring 2026.

Kenyon Jones | (701) 870-5235 | kjonesmle@gmail.com
Cynthia Ennis (authorized) | (701) 946-5731"""

JAYCO_ND_COLD = """Hello,

I have a 2017 Jayco Eagle HT 26.5BHS — a 4-Season bunkhouse fifth wheel with approximately
2,400 actual tow miles, currently in Douglasville, Georgia, moving to North Dakota spring/summer 2026.

WHY THIS UNIT FOR YOUR MARKET:
The Climate Shield package (0°F rated, fully enclosed heated underbelly, PEX plumbing,
double-layer fiberglass, forced-air heated tank system) is not a luxury feature in ND/SD/MT —
it's a necessity. This unit has it. Southeast-stored — zero road salt exposure. Clean GA title.

SPECS: Half-ton towable (GVWR 9,950 lbs) | Sleeps 8–10 | Double-over-double bunkhouse |
Single living area slide | Walk-in shower with skylight | Full kitchen | Extra Clean 9/10 interior.

ASKING: $26,500 as-is. Flexible for consignment terms.

On-site contact in GA: Doug & Sherrie Appleby (770-315-1949).
29-photo catalog + video walkthrough available.

Kenyon Jones | (701) 870-5235 | kjonesmle@gmail.com"""


class JaycoCampaign(BaseCampaign):
    CAMPAIGN_ID = "JAYCO_2017_EAGLE_HT"

    @property
    def vehicle_info(self) -> Dict:
        return {
            "display":   "2017 Jayco Eagle HT 26.5BHS",
            "vin":       "1UJCJ0BPXH1P20237",
            "ga_title":  "770175206127980",
            "mileage":   "~2,400",
            "gvwr":      "9,950 lbs",
            "title":     "Clean GA Title, No Liens",
            "location":  "Douglasville, GA",
            "onsite":    "Doug & Sherrie Appleby | (770) 315-1949",
            "corral":    "Corral Sales RV | (701) 663-9538 | hello@corralsales.com",
            "asking":    "$26,500",
            "range":     "$20,000–$30,000",
            "note":      "BaT does NOT accept 5th wheels. Use Corral Sales + RV Trader + AuctionTime.",
        }

    @property
    def messages(self) -> Dict[str, str]:
        return {
            "ND_COLD": JAYCO_ND_COLD,
            "DEFAULT": JAYCO_DEFAULT,
        }

    @property
    def priority_contacts(self) -> List[Contact]:
        return [
            Contact("Corral Sales RV Mandan",  email="hello@corralsales.com", phone="7016639538",
                    tier="ND_COLD", method="email",
                    notes="Primary ND consignment channel. Ask for lot space and listing terms."),
            Contact("Integrity RV Douglasville", email=None, phone="7706931186",
                    tier="DEFAULT", method="phone",
                    notes="3 miles from storage. Call Jeff or Greg. Ask: need a bunkhouse 5th wheel?"),
            Contact("Capital RV Bismarck",      email=None, phone="7012557878",
                    url="https://www.capitalrv.com/bismarck/contact-us",
                    tier="ND_COLD", method="form",
                    notes="Big dog in western ND — Climate Shield pitch"),
            Contact("Roughrider RVs Dickinson", email=None, phone="7014839844",
                    url="https://www.roughriderrvs.net/contactus",
                    tier="ND_COLD", method="form",
                    notes="Oil field market — sell as housing/survival capsule"),
        ]

    @property
    def contacts(self) -> List[Contact]:
        return self.priority_contacts + [
            Contact("Southland RV Norcross",    email=None, phone="7707172890",
                    url="https://www.southlandrv.com/consignment",
                    tier="DEFAULT", method="form",
                    notes="Atlanta area, high-end clientele"),
            Contact("PPL Motor Homes Houston",  email=None, phone="8007554775",
                    url="https://www.pplmotorhomes.com/rvconsignment",
                    tier="DEFAULT", method="form",
                    notes="Largest RV consignment dealer in USA. 10% commission."),
            Contact("Pifer's Auction Steele",   email=None, phone="7014757653",
                    url="https://www.pifers.com/contact",
                    tier="ND_COLD", method="form",
                    notes="King of ND equipment — market as oil field/hunting rig"),
            Contact("Steffes Group West Fargo", email=None, phone=None,
                    tier="ND_COLD", method="email",
                    notes="BaT-equivalent for ND RV auction"),
            Contact("RV Trader Listing",        url="https://www.rvtrader.com",
                    tier="DEFAULT", method="form"),
            Contact("AuctionTime ND",           url="https://www.auctiontime.com",
                    tier="ND_COLD", method="form"),
        ]
