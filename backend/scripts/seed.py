"""Seed the database with realistic Richmond VA service requests for demo purposes.

Usage:
    cd backend && .venv/bin/python -m scripts.seed

Idempotent: skips if seed data already exists (checks for reference_number prefix "RVA-SEED-").
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta, timezone

# Ensure the backend package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

load_dotenv()

from sqlalchemy import select

from app.database import AsyncSessionLocal, Base, engine
from app.models.conversation import Conversation, Message
from app.models.service_request import ServiceRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SEED_PREFIX = "RVA-SEED-"

now = datetime.now(timezone.utc)

SEED_REQUESTS = [
    # Potholes
    {
        "reference_number": f"{SEED_PREFIX}001",
        "phone_number": "+18045551001",
        "category": "pothole",
        "description": "Large pothole causing cars to swerve into oncoming traffic",
        "location": "W Broad St & N Boulevard",
        "latitude": 37.5585,
        "longitude": -77.4734,
        "urgency": 5,
        "status": "new",
        "created_at": now - timedelta(hours=2),
        "sms_inbound": "Huge pothole at Broad and Boulevard, cars are swerving to avoid it",
    },
    {
        "reference_number": f"{SEED_PREFIX}002",
        "phone_number": "+18045551002",
        "category": "pothole",
        "description": "Medium pothole near school zone",
        "location": "Floyd Ave & N Sheppard St",
        "latitude": 37.5533,
        "longitude": -77.4790,
        "urgency": 4,
        "status": "in_progress",
        "created_at": now - timedelta(days=1),
        "sms_inbound": "Pothole on Floyd near Sheppard, its right in the school zone",
    },
    # Streetlights
    {
        "reference_number": f"{SEED_PREFIX}003",
        "phone_number": "+18045551003",
        "category": "streetlight",
        "description": "Streetlight flickering and buzzing at night",
        "location": "E Main St & N 25th St",
        "latitude": 37.5315,
        "longitude": -77.4110,
        "urgency": 3,
        "status": "new",
        "created_at": now - timedelta(hours=18),
        "sms_inbound": "Street light on Main and 25th keeps flickering, really annoying at night",
    },
    {
        "reference_number": f"{SEED_PREFIX}004",
        "phone_number": "+18045551004",
        "category": "streetlight",
        "description": "Streetlight completely out on dark residential street",
        "location": "Hanover Ave & N Allen Ave",
        "latitude": 37.5568,
        "longitude": -77.4822,
        "urgency": 4,
        "status": "resolved",
        "created_at": now - timedelta(days=3),
        "sms_inbound": "The streetlight on Hanover and Allen has been out for a week. Its really dark and unsafe",
    },
    # Graffiti
    {
        "reference_number": f"{SEED_PREFIX}005",
        "phone_number": "+18045551005",
        "category": "graffiti",
        "description": "Offensive graffiti spray-painted on bridge underpass wall",
        "location": "I-95 overpass at W Broad St",
        "latitude": 37.5571,
        "longitude": -77.4480,
        "urgency": 3,
        "status": "new",
        "created_at": now - timedelta(hours=6),
        "sms_inbound": "Someone spray painted a bunch of graffiti under the 95 overpass at Broad St",
    },
    {
        "reference_number": f"{SEED_PREFIX}006",
        "phone_number": "+18045551006",
        "category": "graffiti",
        "description": "Graffiti tags on storefront windows in Carytown",
        "location": "W Cary St & S Nansemond St",
        "latitude": 37.5551,
        "longitude": -77.4870,
        "urgency": 2,
        "status": "in_progress",
        "created_at": now - timedelta(days=2),
        "sms_inbound": "Graffiti all over shop windows on Cary Street near Nansemond",
    },
    # Trash / Illegal dumping
    {
        "reference_number": f"{SEED_PREFIX}007",
        "phone_number": "+18045551007",
        "category": "trash",
        "description": "Illegal dumping of mattresses and furniture in alley",
        "location": "Alley behind 1200 W Grace St",
        "latitude": 37.5504,
        "longitude": -77.4590,
        "urgency": 3,
        "status": "new",
        "created_at": now - timedelta(hours=10),
        "sms_inbound": "Someone dumped a bunch of mattresses and old furniture in the alley behind Grace St",
    },
    {
        "reference_number": f"{SEED_PREFIX}008",
        "phone_number": "+18045551008",
        "category": "trash",
        "description": "Overflowing public trash cans in Monroe Park",
        "location": "Monroe Park, W Franklin St",
        "latitude": 37.5475,
        "longitude": -77.4520,
        "urgency": 2,
        "status": "resolved",
        "created_at": now - timedelta(days=4),
        "sms_inbound": "Trash cans in Monroe Park are overflowing and theres litter everywhere",
    },
    # Water
    {
        "reference_number": f"{SEED_PREFIX}009",
        "phone_number": "+18045551009",
        "category": "water",
        "description": "Fire hydrant leaking water steadily onto sidewalk",
        "location": "E Marshall St & N 2nd St",
        "latitude": 37.5420,
        "longitude": -77.4360,
        "urgency": 4,
        "status": "in_progress",
        "created_at": now - timedelta(days=1, hours=4),
        "sms_inbound": "Fire hydrant on Marshall and 2nd is leaking water all over the sidewalk",
    },
    {
        "reference_number": f"{SEED_PREFIX}010",
        "phone_number": "+18045551010",
        "category": "water",
        "description": "Standing water in road after rain cleared everywhere else",
        "location": "Dock St & E Cary St",
        "latitude": 37.5320,
        "longitude": -77.4290,
        "urgency": 2,
        "status": "new",
        "created_at": now - timedelta(hours=14),
        "sms_inbound": "Theres been standing water on Dock St near Cary for days even though it stopped raining",
    },
    # Sidewalk
    {
        "reference_number": f"{SEED_PREFIX}011",
        "phone_number": "+18045551011",
        "category": "sidewalk",
        "description": "Buckled sidewalk creating trip hazard near bus stop",
        "location": "Chamberlayne Ave & Brookland Park Blvd",
        "latitude": 37.5720,
        "longitude": -77.4280,
        "urgency": 4,
        "status": "new",
        "created_at": now - timedelta(hours=4),
        "sms_inbound": "Sidewalk is all buckled up near the bus stop at Chamberlayne and Brookland Park. Someone is going to trip",
    },
    {
        "reference_number": f"{SEED_PREFIX}012",
        "phone_number": "+18045551012",
        "category": "sidewalk",
        "description": "Tree roots cracking sidewalk panels on residential street",
        "location": "Seminary Ave & N Lombardy St",
        "latitude": 37.5610,
        "longitude": -77.4610,
        "urgency": 2,
        "status": "resolved",
        "created_at": now - timedelta(days=5),
        "sms_inbound": "Tree roots pushing up the sidewalk on Seminary near Lombardy, hard to walk on",
    },
    # Noise
    {
        "reference_number": f"{SEED_PREFIX}013",
        "phone_number": "+18045551013",
        "category": "noise",
        "description": "Late-night construction noise from commercial building site",
        "location": "E Grace St & N 17th St",
        "latitude": 37.5365,
        "longitude": -77.4200,
        "urgency": 3,
        "status": "new",
        "created_at": now - timedelta(hours=8),
        "sms_inbound": "Construction site on Grace and 17th is running heavy equipment past midnight every night",
    },
    {
        "reference_number": f"{SEED_PREFIX}014",
        "phone_number": "+18045551014",
        "category": "noise",
        "description": "Persistent loud music from establishment disturbing neighborhood",
        "location": "W Broad St near VCU",
        "latitude": 37.5490,
        "longitude": -77.4530,
        "urgency": 2,
        "status": "in_progress",
        "created_at": now - timedelta(days=2, hours=6),
        "sms_inbound": "Bar on Broad near VCU plays super loud music every night until 3am, the whole block can hear it",
    },
    # Other
    {
        "reference_number": f"{SEED_PREFIX}015",
        "phone_number": "+18045551015",
        "category": "other",
        "description": "Abandoned vehicle parked on street for over two weeks",
        "location": "N 1st St & E Leigh St",
        "latitude": 37.5432,
        "longitude": -77.4350,
        "urgency": 1,
        "status": "new",
        "created_at": now - timedelta(days=1, hours=12),
        "sms_inbound": "Theres a car thats been parked on 1st and Leigh for like 2 weeks, flat tires, looks abandoned",
    },
    {
        "reference_number": f"{SEED_PREFIX}016",
        "phone_number": "+18045551016",
        "category": "other",
        "description": "Missing stop sign at dangerous intersection",
        "location": "Patterson Ave & N Thompson St",
        "latitude": 37.5620,
        "longitude": -77.4920,
        "urgency": 5,
        "status": "in_progress",
        "created_at": now - timedelta(hours=20),
        "sms_inbound": "Stop sign at Patterson and Thompson is completely gone. Almost saw a wreck today",
    },
    {
        "reference_number": f"{SEED_PREFIX}017",
        "phone_number": "+18045551017",
        "category": "pothole",
        "description": "Cluster of potholes on busy commuter route",
        "location": "Midlothian Turnpike & Bainbridge St",
        "latitude": 37.5195,
        "longitude": -77.4560,
        "urgency": 4,
        "status": "new",
        "created_at": now - timedelta(hours=1),
        "sms_inbound": "Multiple potholes on Midlothian Turnpike near Bainbridge, one after another",
    },
    {
        "reference_number": f"{SEED_PREFIX}018",
        "phone_number": "+18045551018",
        "category": "trash",
        "description": "Large pile of yard waste blocking part of the road",
        "location": "Grove Ave & S Meadow St",
        "latitude": 37.5545,
        "longitude": -77.4850,
        "urgency": 3,
        "status": "new",
        "created_at": now - timedelta(hours=5),
        "sms_inbound": "Huge pile of branches and yard waste on Grove near Meadow, taking up half the road",
    },
]


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # Idempotency check
        result = await db.execute(
            select(ServiceRequest).where(
                ServiceRequest.reference_number.like(f"{SEED_PREFIX}%")
            ).limit(1)
        )
        if result.scalar_one_or_none():
            logger.info("Seed data already exists — skipping.")
            return

        for item in SEED_REQUESTS:
            sms_inbound = item.pop("sms_inbound")
            created = item["created_at"]
            item["updated_at"] = created

            sr = ServiceRequest(**item)
            db.add(sr)
            await db.flush()

            conv = Conversation(
                phone_number=item["phone_number"],
                service_request_id=sr.id,
                status="completed",
                current_step="done",
                context={
                    "category": item["category"],
                    "description": item["description"],
                    "location": item["location"],
                    "urgency": item["urgency"],
                },
                started_at=created,
                last_message_at=created,
            )
            db.add(conv)
            await db.flush()

            inbound = Message(
                conversation_id=conv.id,
                direction="inbound",
                body=sms_inbound,
                created_at=created,
            )
            outbound = Message(
                conversation_id=conv.id,
                direction="outbound",
                body=(
                    f"Submitted! Your report ({item['reference_number']}) for "
                    f"{item['category']} at {item['location']} has been received. "
                    f"Reply STATUS anytime to check progress."
                ),
                created_at=created + timedelta(seconds=2),
            )
            db.add(inbound)
            db.add(outbound)

        await db.commit()
        logger.info("Seeded %d service requests.", len(SEED_REQUESTS))


if __name__ == "__main__":
    asyncio.run(seed())
