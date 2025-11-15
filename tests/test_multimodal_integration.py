"""
Test script for multimodal pipeline integration
Run after deployment to verify all tasks work correctly

Usage:
    python tests/test_multimodal_integration.py

Requirements:
    - Docker services running (backend, celery_worker, postgres, redis)
    - Test video at test_videos/sample_promo.mp4
    - Backend accessible at http://localhost:8000
"""

import requests
import time
import json
from pathlib import Path
import sys

# Configuration
BASE_URL = "http://localhost:8000"
TEST_VIDEO_PATH = Path("test_videos/sample_promo.mp4")
MAX_WAIT_SECONDS = 300  # 5 minutes timeout


def print_header(text):
    """Print formatted header"""
    print(f"\n{text}")
    print("=" * 60)


def print_step(number, text):
    """Print formatted step"""
    print(f"\n{number}️⃣ {text}")


def print_success(text):
    """Print success message"""
    print(f"✅ {text}")


def print_error(text):
    """Print error message"""
    print(f"❌ {text}")


def print_warning(text):
    """Print warning message"""
    print(f"⚠️  {text}")


def test_multimodal_pipeline():
    """Test complete multimodal processing pipeline"""

    print_header("🧪 MULTIMODAL INTEGRATION TEST")

    # ========================================================================
    # STEP 1: Upload Test Video
    # ========================================================================
    print_step("1", "Uploading test video...")

    if not TEST_VIDEO_PATH.exists():
        print_error(f"Test video not found: {TEST_VIDEO_PATH}")
        print(f"   Please place a test video at {TEST_VIDEO_PATH}")
        return False

    try:
        with open(TEST_VIDEO_PATH, 'rb') as f:
            files = {'file': (TEST_VIDEO_PATH.name, f, 'video/mp4')}
            response = requests.post(f"{BASE_URL}/api/v1/videos/upload", files=files)

        if response.status_code != 200:
            print_error(f"Upload failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False

        data = response.json()
        video_id = data.get('video_id')

        if not video_id:
            print_error("No video_id in upload response")
            return False

        print_success(f"Video uploaded: {video_id}")

    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to backend")
        print("   Make sure services are running: docker-compose ps")
        return False
    except Exception as e:
        print_error(f"Upload failed: {str(e)}")
        return False

    # ========================================================================
    # STEP 2: Monitor Processing Pipeline
    # ========================================================================
    print_step("2", "Monitoring processing pipeline...")
    print("   Expected: Metadata → Audio → Transcribe → Visual → Vocal → Comprehensive → Jake")

    start_time = time.time()

    while time.time() - start_time < MAX_WAIT_SECONDS:
        try:
            response = requests.get(f"{BASE_URL}/api/v1/videos/{video_id}")

            if response.status_code != 200:
                print_error(f"Failed to get video status: HTTP {response.status_code}")
                return False

            data = response.json()
            status = data.get('status')

            # Print status on same line (overwrite)
            elapsed = int(time.time() - start_time)
            print(f"   Status: {status} (elapsed: {elapsed}s)", end='\r')

            if status == "completed":
                print(f"\n{print_success(f'Processing completed in {elapsed}s')}")
                break
            elif status == "failed":
                print(f"\n{print_error('Processing failed')}")
                print("   Check logs: docker-compose logs -f celery_worker")
                return False

            time.sleep(5)

        except Exception as e:
            print_error(f"Error checking status: {str(e)}")
            return False
    else:
        print(f"\n{print_error(f'Timeout after {MAX_WAIT_SECONDS}s')}")
        return False

    # ========================================================================
    # STEP 3: Verify Multimodal Data
    # ========================================================================
    print_step("3", "Verifying multimodal data...")

    try:
        response = requests.get(f"{BASE_URL}/api/v1/videos/{video_id}")
        data = response.json()
    except Exception as e:
        print_error(f"Failed to get video data: {str(e)}")
        return False

    # Check visual insights
    visual_insights = data.get('visual_insights')
    if not visual_insights:
        print_error("No visual insights found")
        return False

    print_success("Visual insights present")
    print(f"   - Conviction: {visual_insights.get('conviction_score', 0):.1f}/100")
    print(f"   - Intensity: {visual_insights.get('intensity_score', 0):.1f}/100")
    print(f"   - Eye Contact: {visual_insights.get('eye_contact_score', 0):.1f}/100")

    # Check vocal insights
    vocal_insights = data.get('vocal_insights')
    if not vocal_insights:
        print_error("No vocal insights found")
        return False

    print_success("Vocal insights present")
    print(f"   - Vocal Conviction: {vocal_insights.get('vocal_conviction_score', 0):.1f}/100")
    print(f"   - Vocal Intensity: {vocal_insights.get('vocal_intensity_score', 0):.1f}/100")
    print(f"   - Confidence: {vocal_insights.get('speaking_confidence_score', 0):.1f}/100")

    # Check comprehensive analysis
    analyses = data.get('analyses', [])
    if not analyses or len(analyses) == 0:
        print_error("No analyses found")
        return False

    analysis = analyses[0]

    # Check comprehensive scores
    if analysis.get('congruence_score') is None:
        print_error("No congruence score found")
        return False

    print_success("Comprehensive scores present")
    print(f"   - Congruence: {analysis.get('congruence_score', 0)}/100")
    print(f"   - Authenticity: {analysis.get('authenticity_score', 0)}/100")
    print(f"   - Intensity: {analysis.get('intensity_score', 0)}/100")
    print(f"   - Impact: {analysis.get('impact_score', 0)}/100")

    # Check grades
    character_grade = analysis.get('character_grade')
    if not character_grade:
        print_warning("No grades found (may be null for some performances)")
    else:
        print_success("Grades assigned")
        print(f"   - Character: {character_grade}")
        print(f"   - Delivery: {analysis.get('delivery_grade')}")
        print(f"   - Psychology: {analysis.get('psychology_grade')}")

    # Check moment-by-moment feedback
    moment_by_moment = analysis.get('moment_by_moment', [])
    if not moment_by_moment or len(moment_by_moment) == 0:
        print_warning("No moment-by-moment feedback (may be empty for short videos)")
    else:
        print_success(f"Moment-by-moment feedback: {len(moment_by_moment)} moments")

        # Show first moment as sample
        if len(moment_by_moment) > 0:
            moment = moment_by_moment[0]
            print(f"\n   Sample moment at {moment.get('timestamp')}s:")
            print(f"   - Category: {moment.get('category')}")
            print(f"   - Alignment: {moment.get('alignment')}")
            jake_obs = moment.get('jake_observation', '')
            print(f"   - Jake's observation: {jake_obs[:80]}...")

    # ========================================================================
    # STEP 4: Verify Jake Morrison's Enhanced Feedback
    # ========================================================================
    print_step("4", "Verifying Jake Morrison's enhanced feedback...")

    feedback = analysis.get('detailed_feedback')
    if not feedback:
        print_error("No detailed feedback found")
        return False

    # Check if feedback references multimodal observations
    keywords = ['face', 'voice', 'visual', 'vocal', 'eye', 'tone', 'congruence', 'authentic']
    found_keywords = [kw for kw in keywords if kw.lower() in feedback.lower()]

    if len(found_keywords) < 3:
        print_warning(f"Feedback may not be using multimodal data (found only: {found_keywords})")
    else:
        print_success(f"Jake's feedback references multimodal data: {', '.join(found_keywords)}")

    # ========================================================================
    # SUCCESS
    # ========================================================================
    print_header("🎉 MULTIMODAL INTEGRATION TEST PASSED!")

    print("\nSummary:")
    print(f"  Video ID: {video_id}")
    print(f"  Processing Time: {elapsed}s")
    print(f"  Visual Conviction: {visual_insights.get('conviction_score', 0):.1f}/100")
    print(f"  Vocal Conviction: {vocal_insights.get('vocal_conviction_score', 0):.1f}/100")
    print(f"  Congruence Score: {analysis.get('congruence_score', 0)}/100")
    print(f"  Authenticity Score: {analysis.get('authenticity_score', 0)}/100")
    if character_grade:
        print(f"  Character Grade: {character_grade}")
    print(f"  Moment-by-Moment: {len(moment_by_moment)} moments")

    return True


def main():
    """Main test execution"""
    try:
        success = test_multimodal_pipeline()

        if success:
            print("\n✅ All tests passed!")
            sys.exit(0)
        else:
            print("\n❌ Tests failed!")
            print("\nTroubleshooting:")
            print("  1. Check services: docker-compose ps")
            print("  2. Check logs: docker-compose logs -f celery_worker")
            print("  3. See docs/04-troubleshooting.md")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
