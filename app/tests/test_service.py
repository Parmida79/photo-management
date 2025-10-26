#!/usr/bin/env python3
"""
Test script for the AI-Powered Photo Management Service
"""

import requests
import json
import time
import os
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TEST_IMAGE_PATH = "test_image.jpg"  # You'll need to provide a test image

def create_test_image():
    """Create a simple test image if none exists."""
    if not Path(TEST_IMAGE_PATH).exists():
        try:
            from PIL import Image, ImageDraw
            
            # Create a simple test image
            img = Image.new('RGB', (200, 200), color='red')
            draw = ImageDraw.Draw(img)
            draw.text((50, 100), "Test Image", fill='white')
            img.save(TEST_IMAGE_PATH)
            print(f"✅ Created test image: {TEST_IMAGE_PATH}")
        except ImportError:
            print("❌ PIL not available. Please provide a test image manually.")
            return False
    return True

def test_health_check():
    """Test the health check endpoint."""
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_root_endpoint():
    """Test the root endpoint."""
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            data = response.json()
            print("✅ Root endpoint working")
            print(f"   Service: {data.get('message')}")
            print(f"   Version: {data.get('version')}")
            return True
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
        return False

def test_photo_upload():
    """Test photo upload."""
    if not Path(TEST_IMAGE_PATH).exists():
        print("❌ Test image not found. Skipping upload test.")
        return None
    
    try:
        with open(TEST_IMAGE_PATH, 'rb') as f:
            files = {'file': (TEST_IMAGE_PATH, f, 'image/jpeg')}
            response = requests.post(f"{BASE_URL}/upload", files=files)
        
        if response.status_code == 200:
            data = response.json()
            photo_id = data.get('photo_id')
            print(f"✅ Photo uploaded successfully: {photo_id}")
            return photo_id
        else:
            print(f"❌ Photo upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Photo upload error: {e}")
        return None

def test_photo_retrieval(photo_id):
    """Test photo retrieval."""
    if not photo_id:
        print("❌ No photo ID provided. Skipping retrieval test.")
        return False
    
    try:
        response = requests.get(f"{BASE_URL}/photo/{photo_id}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Photo retrieval successful")
            print(f"   Filename: {data.get('filename')}")
            print(f"   Analysis Status: {data.get('analysis_status')}")
            return True
        else:
            print(f"❌ Photo retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Photo retrieval error: {e}")
        return False

def test_analysis_status(photo_id):
    """Test analysis status endpoint."""
    if not photo_id:
        print("❌ No photo ID provided. Skipping status test.")
        return False
    
    try:
        response = requests.get(f"{BASE_URL}/photo/{photo_id}/status")
        if response.status_code == 200:
            data = response.json()
            print("✅ Analysis status check successful")
            print(f"   Status: {data.get('analysis_status')}")
            return True
        else:
            print(f"❌ Analysis status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Analysis status check error: {e}")
        return False

def test_search_functionality():
    """Test search functionality."""
    try:
        # Test semantic search
        response = requests.get(f"{BASE_URL}/search?q=test")
        if response.status_code == 200:
            data = response.json()
            print("✅ Semantic search working")
            print(f"   Results found: {data.get('total_found', 0)}")
        else:
            print(f"❌ Semantic search failed: {response.status_code}")
        
        # Test tag search
        response = requests.get(f"{BASE_URL}/search/tags?tags=test")
        if response.status_code == 200:
            data = response.json()
            print("✅ Tag search working")
            print(f"   Results found: {data.get('total_found', 0)}")
        else:
            print(f"❌ Tag search failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Search functionality error: {e}")

def test_smart_features():
    """Test smart features."""
    try:
        # Test album generation
        response = requests.post(f"{BASE_URL}/albums/generate?theme=test&max_photos=5")
        if response.status_code == 200:
            data = response.json()
            print("✅ Album generation working")
            print(f"   Album: {data.get('name')}")
        else:
            print(f"❌ Album generation failed: {response.status_code}")
        
        # Test emotion analysis
        response = requests.get(f"{BASE_URL}/emotion-analysis?limit=10")
        if response.status_code == 200:
            data = response.json()
            print("✅ Emotion analysis working")
            print(f"   Photos analyzed: {data.get('total_analyzed', 0)}")
        else:
            print(f"❌ Emotion analysis failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Smart features error: {e}")

def wait_for_analysis(photo_id, max_wait=60):
    """Wait for photo analysis to complete."""
    if not photo_id:
        return False
    
    print(f"⏳ Waiting for analysis to complete (max {max_wait}s)...")
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(f"{BASE_URL}/photo/{photo_id}/status")
            if response.status_code == 200:
                data = response.json()
                status = data.get('analysis_status')
                print(f"   Analysis status: {status}")
                
                if status == 'completed':
                    print("✅ Analysis completed!")
                    return True
                elif status == 'failed':
                    print("❌ Analysis failed!")
                    return False
                
                time.sleep(2)
            else:
                print(f"❌ Status check failed: {response.status_code}")
                break
        except Exception as e:
            print(f"❌ Status check error: {e}")
            break
    
    print("⏰ Analysis timeout reached")
    return False

def main():
    """Run all tests."""
    print("🧪 AI-Powered Photo Management Service - Test Suite")
    print("=" * 60)
    
    # Create test image
    if not create_test_image():
        print("⚠️  Continuing without test image...")
    
    # Test basic endpoints
    print("\n📡 Testing basic endpoints...")
    test_health_check()
    test_root_endpoint()
    
    # Test photo functionality
    print("\n📸 Testing photo functionality...")
    photo_id = test_photo_upload()
    test_photo_retrieval(photo_id)
    test_analysis_status(photo_id)
    
    # Wait for analysis if photo was uploaded
    if photo_id:
        wait_for_analysis(photo_id)
    
    # Test search functionality
    print("\n🔍 Testing search functionality...")
    test_search_functionality()
    
    # Test smart features
    print("\n🧠 Testing smart features...")
    test_smart_features()
    
    print("\n" + "=" * 60)
    print("✅ Test suite completed!")
    print("\n📚 For more detailed testing, visit: http://localhost:8000/docs")

if __name__ == "__main__":
    main()
