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

# Load Diana Sterling system prompt
diana_system_prompt_path = Path(__file__).parent / "prompts" / "diana_sterling_system.md"
with open(diana_system_prompt_path, "r") as f:
    diana_system_prompt = f.read()


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

        # =========================================================
        # DIANA STERLING - Performance Psychologist
        # =========================================================
        print("\n" + "=" * 60)
        print("SEEDING DR. DIANA STERLING")
        print("=" * 60)

        # Check if Diana Sterling already exists
        existing_diana = db.query(Judge).filter(Judge.slug == "diana-sterling").first()
        if existing_diana:
            print("⚠️  Dr. Diana Sterling already exists in database")
            print("   Updating existing record...")
            diana = existing_diana
        else:
            print("Creating Dr. Diana Sterling...")
            diana = Judge(slug="diana-sterling")
            db.add(diana)

        # Set/update Diana Sterling data
        diana.name = "Dr. Diana Sterling"
        diana.personality_type = "Performance Psychologist"

        diana.description = """Dr. Diana Sterling is a performance psychologist with a PhD in Performance
Psychology and 15 years of experience working with professional wrestlers, actors, and public speakers.
She analyzes promos through the lens of psychological authenticity, emotional intelligence, and audience
connection. Diana combines scientific rigor with empathetic understanding, helping performers understand
the psychological mechanisms behind great performances."""

        diana.evaluation_focus = """Dr. Sterling focuses on nine psychological categories: Emotional Authenticity
(20%), Psychological Depth (15%), Non-Verbal Communication (15%), Audience Psychology (15%), Vocal Dynamics
(10%), Cognitive Clarity (10%), Character Consistency (5%), Emotional Intelligence (5%), and Presence &
Charisma (5%). She emphasizes authentic emotion and psychological congruence above technical perfection."""

        diana.scoring_criteria = {
            "emotional_authenticity": {
                "weight": 20,
                "description": "Genuine emotion vs. performed emotion",
                "focus": ["authentic expression", "emotional vulnerability", "verbal/non-verbal consistency", "genuine passion"]
            },
            "psychological_depth": {
                "weight": 15,
                "description": "Real psychology behind the character",
                "focus": ["internal motivations", "psychological complexity", "believable journey", "depth beyond surface"]
            },
            "non_verbal_communication": {
                "weight": 15,
                "description": "Body language and micro-expressions",
                "focus": ["facial expressions", "authentic gestures", "posture psychology", "eye contact", "spatial awareness"]
            },
            "audience_psychology": {
                "weight": 15,
                "description": "Understanding how to influence audience minds",
                "focus": ["psychological triggers", "social proof", "anticipation building", "emotional investment"]
            },
            "vocal_dynamics": {
                "weight": 10,
                "description": "Psychological effectiveness of voice use",
                "focus": ["vocal variety", "strategic silence", "tone matching", "prosody", "paralinguistic cues"]
            },
            "cognitive_clarity": {
                "weight": 10,
                "description": "Message clarity and memorability",
                "focus": ["message simplicity", "logical flow", "memorable hooks", "clear thesis", "no confusion"]
            },
            "character_consistency": {
                "weight": 5,
                "description": "Psychological consistency of character",
                "focus": ["behavioral consistency", "psychological believability", "no breaking character", "natural evolution"]
            },
            "emotional_intelligence": {
                "weight": 5,
                "description": "Awareness of own and audience emotions",
                "focus": ["self-awareness", "reading audience", "emotional regulation", "empathy", "emotional timing"]
            },
            "presence_charisma": {
                "weight": 5,
                "description": "Psychological attention command",
                "focus": ["attention capture", "sustained focus", "natural magnetism", "confidence signals", "authority"]
            }
        }

        diana.system_prompt = diana_system_prompt

        diana.user_prompt_template = """Analyze this wrestling promo from a psychological perspective:

**Promo Title:** {promo_title}
**Character Type:** {character_type}
**Promo Type:** {promo_type}
**Context:** {promo_context}
**Duration:** {duration} seconds
**Word Count:** {word_count} words

**TRANSCRIPT:**
{transcript}

---

Provide a detailed psychological analysis with:
1. Overall score (0-100) and grade
2. Category scores for: emotional_authenticity, psychological_depth, non_verbal_communication,
   audience_psychology, vocal_dynamics, cognitive_clarity, character_consistency,
   emotional_intelligence, presence_charisma
3. Psychological assessment (2-3 paragraphs analyzing the psychology)
4. Psychological strengths (3-5 specific observations)
5. Psychological areas for growth (3-5 specific observations)
6. Timestamped psychological observations (reference specific moments with psychological insights)
7. Psychological recommendations (3-5 actionable psychological techniques)

Format your response as JSON."""

        diana.is_active = True

        db.commit()
        db.refresh(diana)

        print(f"✅ Dr. Diana Sterling seeded successfully")
        print(f"   ID: {diana.id}")
        print(f"   Name: {diana.name}")
        print(f"   Slug: {diana.slug}")
        print(f"   Personality: {diana.personality_type}")
        print(f"   Active: {diana.is_active}")

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
