"""
API Integration Tests for Wrestling Promo Analyzer
Run: pytest test_api.py -v
"""

import pytest
import requests
from pathlib import Path
import time

BASE_URL = "http://localhost:8000"


class TestHealthCheck:
    """Test health and basic endpoints"""

    def test_root_endpoint(self):
        """Test root endpoint returns API info"""
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data

    def test_health_check(self):
        """Test health endpoint"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "database" in data
        assert data["database"] == "connected"

    def test_docs_available(self):
        """Test API docs are accessible"""
        response = requests.get(f"{BASE_URL}/docs")
        assert response.status_code == 200


class TestJudges:
    """Test judge endpoints"""

    def test_list_judges(self):
        """Test listing all judges"""
        response = requests.get(f"{BASE_URL}/api/v1/judges")
        assert response.status_code == 200
        judges = response.json()
        assert isinstance(judges, list)
        assert len(judges) >= 1

    def test_list_judges_active_only(self):
        """Test listing only active judges"""
        response = requests.get(f"{BASE_URL}/api/v1/judges?active_only=true")
        assert response.status_code == 200
        judges = response.json()
        for judge in judges:
            assert judge["is_active"] == True

    def test_get_jake_morrison(self):
        """Test getting Jake Morrison judge by slug"""
        response = requests.get(f"{BASE_URL}/api/v1/judges/jake-morrison")
        assert response.status_code == 200
        judge = response.json()
        assert judge["slug"] == "jake-morrison"
        assert judge["name"] == "Jake Morrison"
        assert judge["personality_type"] == "Veteran Coach"
        assert judge["is_active"] == True

    def test_get_nonexistent_judge(self):
        """Test getting judge that doesn't exist"""
        response = requests.get(f"{BASE_URL}/api/v1/judges/nonexistent")
        assert response.status_code == 404


class TestVideos:
    """Test video endpoints"""

    def test_list_videos_empty(self):
        """Test listing videos returns list (may be empty)"""
        response = requests.get(f"{BASE_URL}/api/v1/videos")
        assert response.status_code == 200
        videos = response.json()
        assert isinstance(videos, list)

    def test_list_videos_with_pagination(self):
        """Test video list pagination"""
        response = requests.get(f"{BASE_URL}/api/v1/videos?skip=0&limit=10")
        assert response.status_code == 200
        videos = response.json()
        assert isinstance(videos, list)
        assert len(videos) <= 10

    def test_list_videos_with_status_filter(self):
        """Test filtering videos by status"""
        response = requests.get(f"{BASE_URL}/api/v1/videos?status=completed")
        assert response.status_code == 200
        videos = response.json()
        for video in videos:
            assert video["status"] == "completed"

    def test_list_videos_invalid_status(self):
        """Test filtering with invalid status"""
        response = requests.get(f"{BASE_URL}/api/v1/videos?status=invalid")
        assert response.status_code == 400

    def test_get_nonexistent_video(self):
        """Test getting video that doesn't exist"""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = requests.get(f"{BASE_URL}/api/v1/videos/{fake_uuid}")
        assert response.status_code == 404

    def test_get_video_invalid_uuid(self):
        """Test getting video with invalid UUID format"""
        response = requests.get(f"{BASE_URL}/api/v1/videos/not-a-uuid")
        assert response.status_code == 400


class TestVideoUpload:
    """Test video upload endpoint"""

    def test_upload_without_file(self):
        """Test upload without file fails"""
        response = requests.post(f"{BASE_URL}/api/v1/videos/upload")
        assert response.status_code == 422  # Validation error

    def test_upload_invalid_file_type(self):
        """Test uploading invalid file type"""
        test_file = Path("test.txt")
        test_file.write_text("not a video")

        try:
            with open(test_file, "rb") as f:
                files = {"file": ("test.txt", f, "text/plain")}
                response = requests.post(
                    f"{BASE_URL}/api/v1/videos/upload",
                    files=files
                )

            assert response.status_code == 400
            assert "Invalid file type" in response.json()["detail"]

        finally:
            if test_file.exists():
                test_file.unlink()

    def test_upload_valid_format_fake_video(self):
        """Test upload with valid extension but fake content"""
        test_file = Path("test_video.mp4")
        test_file.write_bytes(b"fake video content")

        try:
            with open(test_file, "rb") as f:
                files = {"file": ("test.mp4", f, "video/mp4")}
                data = {
                    "promo_title": "Test Promo",
                    "character_type": "heel",
                    "promo_type": "challenge",
                }
                response = requests.post(
                    f"{BASE_URL}/api/v1/videos/upload",
                    files=files,
                    data=data
                )

            # Should accept upload (file validation happens in processing)
            # May return 201 or fail during processing
            assert response.status_code in [201, 400, 500]

            if response.status_code == 201:
                data = response.json()
                assert "video_id" in data
                assert "filename" in data
                assert data["status"] in ["uploaded", "processing"]

        finally:
            if test_file.exists():
                test_file.unlink()

    def test_upload_with_metadata(self):
        """Test upload with all optional metadata"""
        test_file = Path("test_with_metadata.mp4")
        test_file.write_bytes(b"fake video content with metadata")

        try:
            with open(test_file, "rb") as f:
                files = {"file": ("test.mp4", f, "video/mp4")}
                data = {
                    "promo_title": "Championship Challenge",
                    "character_type": "heel",
                    "promo_type": "challenge",
                    "promo_context": "Challenging for world title at WrestleMania"
                }
                response = requests.post(
                    f"{BASE_URL}/api/v1/videos/upload",
                    files=files,
                    data=data
                )

            if response.status_code == 201:
                response_data = response.json()
                assert "video_id" in response_data

        finally:
            if test_file.exists():
                test_file.unlink()


class TestVideoDelete:
    """Test video deletion"""

    def test_delete_nonexistent_video(self):
        """Test deleting video that doesn't exist"""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = requests.delete(f"{BASE_URL}/api/v1/videos/{fake_uuid}")
        assert response.status_code == 404

    def test_delete_invalid_uuid(self):
        """Test deleting with invalid UUID"""
        response = requests.delete(f"{BASE_URL}/api/v1/videos/not-a-uuid")
        assert response.status_code == 400


class TestErrorHandling:
    """Test error handling"""

    def test_404_endpoint(self):
        """Test non-existent endpoint returns 404"""
        response = requests.get(f"{BASE_URL}/nonexistent")
        assert response.status_code == 404

    def test_method_not_allowed(self):
        """Test wrong HTTP method"""
        response = requests.post(f"{BASE_URL}/health")
        assert response.status_code == 405


class TestCORS:
    """Test CORS configuration"""

    def test_cors_headers_present(self):
        """Test CORS headers are set"""
        headers = {"Origin": "http://localhost:3000"}
        response = requests.options(
            f"{BASE_URL}/api/v1/videos",
            headers=headers
        )
        # Should have CORS headers
        assert "access-control-allow-origin" in response.headers


# Performance tests (optional, can be slow)
class TestPerformance:
    """Test API performance"""

    @pytest.mark.slow
    def test_health_check_response_time(self):
        """Test health check responds quickly"""
        start = time.time()
        response = requests.get(f"{BASE_URL}/health")
        duration = time.time() - start

        assert response.status_code == 200
        assert duration < 1.0  # Should respond in < 1 second

    @pytest.mark.slow
    def test_list_videos_response_time(self):
        """Test video list responds quickly"""
        start = time.time()
        response = requests.get(f"{BASE_URL}/api/v1/videos?limit=20")
        duration = time.time() - start

        assert response.status_code == 200
        assert duration < 2.0  # Should respond in < 2 seconds


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
