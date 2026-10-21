"""Write local fixtures shaped exactly like the Google Drive v3 and Jira Cloud v3 API responses.

Vardhan Pumps and Services is a made-up Pune pump maker. Every document carries the sharing
settings it would have in a real company, so the knowledge base has something to enforce.
"""
import json
from pathlib import Path

OUT = Path(__file__).parent / "fixtures"
D = "vardhanpumps.in"


def perm(kind: str, who: str, role: str = "reader") -> dict:
    """One entry of Drive's permissions.list response."""
    if kind == "domain":
        return {"type": "domain", "domain": who, "role": role}
    if kind == "anyone":
        return {"type": "anyone", "role": role}
    return {"type": kind, "emailAddress": who, "role": role}


DRIVE = [
    {"id": "1vS200manual", "name": "VS-200 Service Manual: Troubleshooting", "owner": f"asha.kulkarni@{D}",
     "perms": [perm("domain", D)], "text": """
# VS-200 Service Manual: Troubleshooting

## Pump runs but delivers low flow
Check the suction strainer first; a blocked strainer is the cause in most field visits. Then check the impeller for wear. If the flow is still below 80 percent of the rated 42 cubic metres per hour, measure the suction lift; above 6 metres the VS-200 will cavitate.

## Water leaking at the shaft
A leak at the shaft almost always means the mechanical seal has failed. Replace the seal kit (part VS2-SK-11). Do not tighten the gland, the VS-200 has no packing gland. Running the pump dry for more than 30 seconds damages the seal faces.

## Grinding or rattling noise
A grinding noise points to bearing wear or cavitation. Check the bearing temperature: above 80 degrees Celsius, replace both bearings (part VS2-BR-04). A rattling noise like gravel is cavitation; reduce the suction lift or open the suction valve fully.

## Motor trips on overload
Check the supply voltage. The VS-200 motor needs 415 V three phase, plus or minus 10 percent. A single phasing fault trips the overload within seconds.
"""},
    {"id": "1leavePolicy", "name": "Leave and Holiday Policy 2026", "owner": f"meera.iyer@{D}",
     "perms": [perm("domain", D)], "text": """
# Leave and Holiday Policy 2026

## Annual leave
Every employee gets 21 days of paid annual leave per calendar year. Up to 10 unused days carry over to the next year.

## Sick leave
12 days of paid sick leave per year. A doctor's certificate is needed for more than 3 consecutive days.

## Holidays
The Pune office follows 12 public holidays in 2026, including Gudi Padwa, Ganesh Chaturthi and Diwali. Field service engineers on call during a holiday get a compensatory day off.

## How to apply
Apply on the HR portal at least 7 days in advance for planned leave. Your manager approves it.
"""},
    {"id": "1vpnHowto", "name": "IT: How to get VPN access", "owner": f"priya.nair@{D}",
     "perms": [perm("anyone", "")], "text": """
# How to get VPN access

Raise an IT ticket with the subject VPN access. You will get an email to set up the authenticator app. The VPN client is WireGuard. Field engineers get access to the service portal only; office staff get the full network. Access expires after 90 days without use.
"""},
    {"id": "1dealerPrice", "name": "Dealer Price List FY2026-27", "owner": f"rohan.mehta@{D}",
     "perms": [perm("group", f"sales@{D}"), perm("group", f"leadership@{D}")], "text": """
# Dealer Price List FY2026-27

## List prices (ex-works Pune, before GST)
VS-200 centrifugal pump, 7.5 kW: Rs 1,48,000 per unit.
VP-100 domestic pump, 1 HP: Rs 18,500 per unit.
VS2-SK-11 seal kit: Rs 3,200.

## Dealer discounts
Standard dealer discount is 8 percent. Orders above 25 units can get up to 12 percent with approval from the sales head. Anything above 12 percent needs the managing director.

## Payment terms
30 days for registered dealers, advance payment for new customers.
"""},
    {"id": "1shreeAgro", "name": "Shree Agro: VS-200 fleet deal notes", "owner": f"rohan.mehta@{D}",
     "perms": [perm("group", f"sales@{D}"), perm("user", f"vikram.vardhan@{D}")], "text": """
# Shree Agro: VS-200 fleet deal notes

Customer: Shree Agro Farms, Ahmednagar. Contact: Mr Patil, procurement head.

## The order
40 units of the VS-200 for their drip irrigation network, delivered in two lots: 24 units by 15 November and 16 units by 20 December 2026.

## Pricing
Approved discount: 11 percent on list, approved by the sales head on 3 October. Total order value Rs 52,68,800 before GST. They asked for 14 percent; we said no.

## Risk
Mr Patil mentioned seal leaks on the first 6 units we installed in August. If the service team doesn't fix those before the second lot, he said they will look at a competitor for next year's order.
"""},
    {"id": "1salaryBands", "name": "Salary Bands 2026 (confidential)", "owner": f"meera.iyer@{D}",
     "perms": [perm("group", f"hr@{D}")], "text": """
# Salary Bands 2026 (confidential)

## Engineering
Service engineer (E1): Rs 4.8 to 6.5 lakh per year.
Senior service engineer (E2): Rs 7.2 to 9.8 lakh per year.
Service lead (E3): Rs 11 to 14.5 lakh per year.

## Sales
Sales executive (S1): Rs 5 to 7 lakh fixed plus incentive.
Area sales manager (S2): Rs 9 to 13 lakh fixed plus incentive.

Bands are reviewed every April. Offers outside the band need the managing director's approval.
"""},
    {"id": "1appraisal", "name": "Appraisal Cycle Guidelines 2026", "owner": f"meera.iyer@{D}",
     "perms": [perm("group", f"hr@{D}"), perm("group", f"leadership@{D}")], "text": """
# Appraisal Cycle Guidelines 2026

The appraisal cycle runs from 1 March to 15 April. Ratings are on a 5 point scale. The budget for increments this year is 9 percent of the salary bill, with a maximum individual increment of 18 percent. Ratings of 1 or 2 need a written improvement plan agreed with HR.
"""},
    {"id": "1sealPostmortem", "name": "Postmortem: VS-200 mechanical seal failures (Sep 2026)", "owner": f"asha.kulkarni@{D}",
     "perms": [perm("group", f"engineering@{D}"), perm("group", f"leadership@{D}")], "text": """
# Postmortem: VS-200 mechanical seal failures, September 2026

## What happened
Between 12 August and 20 September, 9 VS-200 units failed at the shaft seal within 30 days of installation, 6 of them at Shree Agro, Ahmednagar.

## Root cause
A batch of seal kits from our supplier SealTech (lot ST-0826) had carbon faces that were 0.3 mm thinner than the drawing. Combined with dry running during commissioning, the faces cracked.

## Fix
All units with lot ST-0826 get a new seal kit from lot ST-0926, which passed inspection. Commissioning checklist now requires priming the pump before first start. The Shree Agro replacements are scheduled for 28 October.

## Owner
Asha Kulkarni, service engineering.
"""},
    {"id": "1boardQ3", "name": "Board update Q3 FY27", "owner": f"vikram.vardhan@{D}",
     "perms": [perm("group", f"leadership@{D}")], "text": """
# Board update, Q3 FY27

Revenue for the quarter was Rs 38.4 crore, up 14 percent on last year. The VS-200 line is now 41 percent of revenue.

## Project Kaveri
We are in talks to acquire Jalgaon Motor Works, a motor winding company with 60 employees, for about Rs 22 crore. This is not to be discussed outside the leadership team until the term sheet is signed in December.
"""},
    {"id": "1fieldChecklist", "name": "Field Service Visit Checklist", "owner": f"asha.kulkarni@{D}",
     "perms": [perm("group", f"engineering@{D}")], "text": """
# Field Service Visit Checklist

Before leaving: carry the seal kit, both bearings and the vibration meter. On site: check voltage, prime the pump, never dry run it, record the bearing temperature after 15 minutes. Before leaving site: get the customer's signature on the job card and upload a photo of the nameplate.
"""},
]

JIRA_PROJECTS = {
    "SERV": {"name": "Field Service", "browse_groups": ["engineering", "leadership"]},
    "SALES": {"name": "Sales Pipeline", "browse_groups": ["sales", "leadership"]},
    "HR": {"name": "HR Cases", "browse_groups": ["hr"]},
}
# Jira issue security levels: a second, narrower lock on single issues inside a project
JIRA_SECURITY_LEVELS = {"10001": {"name": "Safety committee", "groups": ["hr", "leadership"]}}

JIRA = [
    ("SERV-101", "Shree Agro: seal leaks on 6 VS-200 units", None, "In Progress", """
Six VS-200 units installed at Shree Agro, Ahmednagar in August are leaking at the shaft. All six have seal kits from lot ST-0826. Replacement visit booked for 28 October with seal kits from lot ST-0926. Assigned to Asha Kulkarni."""),
    ("SERV-102", "VP-100 rattling noise at Deccan Sugar", None, "Open", """
Customer reports a rattling noise like gravel from two VP-100 pumps. Suction lift measured at 7.2 metres, above the limit. Recommended moving the pumps closer to the sump."""),
    ("SERV-103", "Update commissioning checklist after seal failures", None, "Done", """
Added a mandatory priming step before first start and a 30 second dry run limit to the commissioning checklist. Linked to the September seal postmortem."""),
    ("SERV-104", "Technician injury at Nashik site", "10001", "Open", """
Technician Sunil More cut his hand on an impeller edge on 9 October at the Nashik site. First aid given, two stitches, back at work on 11 October. Gloves were not being worn. Safety committee to review the PPE rule."""),
    ("SALES-210", "Shree Agro: 40 x VS-200 fleet order", None, "Won", """
Order confirmed for 40 VS-200 units at 11 percent discount. First lot of 24 units ships 15 November, second lot of 16 units on 20 December. The customer is unhappy about seal leaks on the first units and wants them fixed before the second lot."""),
    ("SALES-211", "Deccan Sugar: annual maintenance contract renewal", None, "Negotiation", """
AMC for 18 pumps up for renewal on 1 December. Current value Rs 4,20,000 per year. Customer is asking for faster response times, 24 hours instead of 48."""),
    ("HR-31", "Grievance: overtime for field engineers", None, "Under review", """
Three field engineers raised a grievance that weekend call-outs in September were not paid as overtime. HR is checking the attendance records against the job cards. Confidential."""),
    ("HR-32", "Offer approval: senior service engineer above band", None, "Approved", """
Offer of Rs 10.4 lakh for a senior service engineer candidate, above the E2 band maximum. Approved by the managing director on 7 October."""),
]


def write() -> None:
    drive = OUT / "drive"
    (drive / "content").mkdir(parents=True, exist_ok=True)
    files = []
    for d in DRIVE:
        files.append({"id": d["id"], "name": d["name"], "mimeType": "application/vnd.google-apps.document",
                      "modifiedTime": "2026-10-15T09:30:00.000Z",
                      "owners": [{"emailAddress": d["owner"]}],
                      "webViewLink": f"https://docs.google.com/document/d/{d['id']}/edit",
                      "permissions": d["perms"]})
        (drive / "content" / f"{d['id']}.txt").write_text(d["text"].strip() + "\n")
    (drive / "files.json").write_text(json.dumps({"files": files}, indent=2))

    jira = OUT / "jira"
    jira.mkdir(parents=True, exist_ok=True)
    issues = [{"key": key, "fields": {
        "summary": summary, "description": desc.strip(), "status": {"name": status},
        "project": {"key": key.split("-")[0]}, "updated": "2026-10-16T11:00:00.000+0530",
        "security": {"id": sec, "name": JIRA_SECURITY_LEVELS[sec]["name"]} if sec else None}}
        for key, summary, sec, status, desc in JIRA]
    (jira / "issues.json").write_text(json.dumps({"issues": issues}, indent=2))
    (jira / "projects.json").write_text(json.dumps(JIRA_PROJECTS, indent=2))
    (jira / "security_levels.json").write_text(json.dumps(JIRA_SECURITY_LEVELS, indent=2))
    print(f"drive: {len(files)} files, jira: {len(issues)} issues in {len(JIRA_PROJECTS)} projects")


if __name__ == "__main__":
    write()
