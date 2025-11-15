"""
Seed database with AI judge personalities
Run once to initialize judges table
"""

from pathlib import Path
from database import SessionLocal, init_db
from models import Judge

# Load Jake Morrison system prompt
jake_system_prompt_path = Path(__file__).parent / "prompts" / "jake_morrison_system.md"
with open(jake_system_prompt_path, "r") as f:
    jake_system_prompt = f.read()


def seed_judges():
    """Seed judges table with initial AI personalities"""

    print("=" * 60)
    print("SEEDING JUDGES TABLE")
    print("=" * 60)

    db = SessionLocal()

    try:
        # Check if Jake Morrison already exists
        existing_jake = db.query(Judge).filter(Judge.slug == "jake-morrison").first()
        if existing_jake:
            print("⚠️  Jake Morrison already exists in database")
            print("   Updating existing record...")
            jake = existing_jake
        else:
            print("Creating Jake Morrison...")
            jake = Judge(slug="jake-morrison")
            db.add(jake)

        # Set/update Jake Morrison data
        jake.name = "Jake Morrison"
        jake.personality_type = "Veteran Coach"

        jake.description = """Jake Morrison is a veteran wrestling coach with 25 years of experience
training world champions. He's direct, honest, and passionate about the craft. Jake has seen
thousands of promos and knows exactly what separates amateur work from main-event material.
He balances old-school wisdom with modern sensibilities, and his feedback is always constructive
and actionable."""

        jake.evaluation_focus = """Jake focuses on six core categories: Psychology (25%), Character
Work (20%), Delivery (20%), Story Structure (15%), Crowd Connection (15%), and Originality (5%).
He emphasizes the mental game and storytelling above all else, believing that technical skills
mean nothing without solid psychology."""

        jake.scoring_criteria = {
            "psychology": {
                "weight": 25,
                "description": "Understanding of the mental game and storytelling",
                "focus": ["character motivation", "emotional progression", "tension building", "heel/face dynamics"]
            },
            "character_work": {
                "weight": 20,
                "description": "Authenticity and distinctiveness of persona",
                "focus": ["authenticity", "commitment", "unique voice", "natural evolution"]
            },
            "delivery": {
                "weight": 20,
                "description": "Voice projection, pacing, and emotional range",
                "focus": ["confidence", "natural pauses", "varied pacing", "emotional authenticity"]
            },
            "story_structure": {
                "weight": 15,
                "description": "Beginning, middle, end with logical progression",
                "focus": ["opening hook", "momentum building", "strong closing", "logical flow"]
            },
            "crowd_connection": {
                "weight": 15,
                "description": "Ability to work with a live audience",
                "focus": ["pop moments", "heat generation", "relatability", "audience awareness"]
            },
            "originality": {
                "weight": 5,
                "description": "Fresh takes and creative perspective",
                "focus": ["original ideas", "fresh language", "unexpected moments", "personal touches"]
            }
        }

        jake.system_prompt = jake_system_prompt

        jake.user_prompt_template = """Analyze this wrestling promo transcript:

**Promo Title:** {promo_title}
**Character Type:** {character_type}
**Promo Type:** {promo_type}
**Context:** {promo_context}
**Duration:** {duration} seconds
**Word Count:** {word_count} words

**TRANSCRIPT:**
{transcript}

---

Provide a detailed analysis with:
1. Overall score (0-100)
2. Category scores for: psychology, character_work, delivery, story_structure, crowd_connection, originality
3. Summary (2-3 paragraphs)
4. Strengths (3-5 bullet points)
5. Weaknesses (3-5 bullet points)
6. Timestamped feedback (reference specific moments)
7. Specific recommendations (3-5 actionable items)

Format your response as JSON."""

        jake.is_active = True

        db.commit()
        db.refresh(jake)

        print(f"✅ Jake Morrison seeded successfully")
        print(f"   ID: {jake.id}")
        print(f"   Name: {jake.name}")
        print(f"   Slug: {jake.slug}")
        print(f"   Personality: {jake.personality_type}")
        print(f"   Active: {jake.is_active}")

        # Future judges (placeholders)
        print("\n📋 Future judges to implement:")
        print("   - Marcus Dante (Harsh Critic)")
        print("   - David Chen (Technical Analyst)")

    except Exception as e:
        print(f"❌ Error seeding judges: {e}")
        db.rollback()
        raise
    finally:
        db.close()

    print("=" * 60)


if __name__ == "__main__":
    # Initialize database if needed
    print("Checking database...")
    init_db()

    # Seed judges
    seed_judges()

    print("\n✅ Database seeding complete!")
