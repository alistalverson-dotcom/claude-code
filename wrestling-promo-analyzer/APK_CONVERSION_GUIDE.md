# Convert Wrestling Promo Analyzer to Android APK

**Turn your web app into a real Android app that users can install!**

---

## Overview

This guide shows you how to convert the Wrestling Promo Analyzer React web app into an Android APK using **Capacitor** (the best option for this project).

### Why Capacitor?

✅ Uses your existing React code - NO rewrite needed
✅ Access to native Android features (camera, file system, etc.)
✅ Professional-looking native app
✅ Easy to maintain and update
✅ Can publish to Google Play Store

### Architecture

```
┌─────────────────────────────────────┐
│      Android APK (Phone)           │
│  ┌────────────────────────────┐   │
│  │  React Frontend (WebView)  │   │  ← Your existing frontend
│  │  runs inside native shell  │   │  ← NO changes needed!
│  └────────────────────────────┘   │
│              ↓                     │
│      Capacitor Bridge              │  ← Gives access to native features
│              ↓                     │
│      Android Native APIs           │
└─────────────────────────────────────┘
                ↓
         Internet/WiFi
                ↓
┌─────────────────────────────────────┐
│   Backend API (Cloud Hosted)        │  ← Needs to be on internet
│   • Railway / Render / DigitalOcean │
│   • PostgreSQL + Redis + Python     │
└─────────────────────────────────────┘
```

---

## Part 1: Prepare Your Backend for Cloud

Your Android app needs the backend accessible via internet. You can't run PostgreSQL/Redis on a phone!

### Option A: Deploy to Railway (Easiest - $5/month)

**Why Railway?**
- Dead simple setup
- Automatic SSL certificates
- Built-in PostgreSQL + Redis
- Free trial available

**Steps:**

1. **Sign up**: https://railway.app
2. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   railway login
   ```

3. **Deploy your backend**:
   ```bash
   cd wrestling-promo-analyzer
   railway init
   railway up
   ```

4. **Add Services**:
   - Click "+ New" → "Database" → "PostgreSQL"
   - Click "+ New" → "Database" → "Redis"

5. **Set Environment Variables**:
   ```bash
   # In Railway dashboard, add these:
   ANTHROPIC_API_KEY=your-key-here
   DATABASE_URL=postgresql://... (auto-set by Railway)
   REDIS_URL=redis://... (auto-set by Railway)
   CORS_ORIGINS=capacitor://localhost,http://localhost,https://yourdomain.com
   ```

6. **Get Your API URL**:
   - Railway gives you: `https://your-app.railway.app`
   - Save this - you'll need it for the mobile app!

### Option B: Deploy to Render (Free Tier Available)

1. **Sign up**: https://render.com
2. **Create Web Service**:
   - Connect your GitHub repo
   - Build command: `cd backend && pip install -r requirements.txt`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. **Add PostgreSQL**: Click "New+" → "PostgreSQL"
4. **Add Redis**: Click "New+" → "Redis"
5. **Set Environment Variables** (same as Railway)

### Option C: DigitalOcean App Platform ($5/month)

1. Sign up: https://www.digitalocean.com/
2. Create App → Import from GitHub
3. Add PostgreSQL and Redis databases
4. Configure environment variables
5. Deploy!

---

## Part 2: Convert Frontend to Android APK

Now that your backend is online, let's make the Android app!

### Step 1: Install Prerequisites

```bash
# Node.js (you probably have this)
node --version  # Should be 18+

# Install Android Studio
# Download from: https://developer.android.com/studio
# Install it and open once to finish setup

# Set ANDROID_HOME environment variable (add to ~/.bashrc or ~/.zshrc):
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/tools
export PATH=$PATH:$ANDROID_HOME/platform-tools
```

### Step 2: Install Capacitor in Your Project

```bash
cd wrestling-promo-analyzer/frontend

# Install Capacitor
npm install @capacitor/core @capacitor/cli

# Initialize Capacitor
npx cap init
```

**When prompted:**
- App name: `Wrestling Promo Analyzer`
- App ID: `com.yourname.promanalyzer` (use your own domain reversed)
- Web directory: `dist` (this is where Vite builds to)

### Step 3: Add Android Platform

```bash
# Install Android plugin
npm install @capacitor/android

# Add Android platform
npx cap add android
```

This creates an `android/` folder with your Android project!

### Step 4: Configure API URL for Mobile

Edit `frontend/src/config.ts` (create if it doesn't exist):

```typescript
// src/config.ts
const getApiUrl = () => {
  // Check if running in Capacitor (mobile app)
  if (window.Capacitor) {
    return 'https://your-backend.railway.app';  // Your cloud backend!
  }

  // Running in browser (development)
  return import.meta.env.VITE_API_URL || 'http://localhost:8000';
};

export const API_BASE_URL = getApiUrl();
```

Update `frontend/src/services/api.ts` to use this:

```typescript
import { API_BASE_URL } from '../config';

// Replace hardcoded API_BASE_URL with imported one
export async function uploadVideo(formData: VideoUploadForm): Promise<VideoResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/videos/upload`, {
    // ... rest of code
  });
}
```

### Step 5: Build Your React App

```bash
cd wrestling-promo-analyzer/frontend

# Production build
npm run build

# This creates frontend/dist/ folder
```

### Step 6: Sync to Android

```bash
# Copy web assets to Android project
npx cap sync android

# This copies everything from dist/ to android/app/src/main/assets/public/
```

### Step 7: Open in Android Studio

```bash
# Open Android project
npx cap open android
```

Android Studio will open!

### Step 8: Configure Android Permissions

Edit `android/app/src/main/AndroidManifest.xml`:

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <!-- Add these permissions -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.CAMERA" />

    <!-- For file uploads -->
    <uses-permission android:name="android.permission.READ_MEDIA_VIDEO" android:minSdkVersion="33" />

    <application
        android:label="Promo Analyzer"
        android:icon="@mipmap/ic_launcher"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:usesCleartextTraffic="true"  <!-- Only for development -->
        ...
    >
        <!-- ... -->
    </application>
</manifest>
```

### Step 9: Build APK

In Android Studio:

1. **Build** menu → **Build Bundle(s) / APK(s)** → **Build APK(s)**
2. Wait for build to complete (2-5 minutes first time)
3. APK location appears in notification: `android/app/build/outputs/apk/debug/app-debug.apk`

**Or via command line:**

```bash
cd android

# Debug APK (for testing)
./gradlew assembleDebug

# Release APK (for distribution - requires signing)
./gradlew assembleRelease
```

### Step 10: Install on Your Phone

**Method 1: USB Cable**

```bash
# Enable USB debugging on your Android phone:
# Settings → About Phone → Tap "Build Number" 7 times
# Settings → Developer Options → Enable "USB Debugging"

# Connect phone via USB

# Install APK
adb install android/app/build/outputs/apk/debug/app-debug.apk

# Or click "Run" button in Android Studio
```

**Method 2: Send APK File**

```bash
# Email yourself the APK file, or upload to Google Drive
# Download on phone and tap to install
# You may need to allow "Install from Unknown Sources"
```

---

## Part 3: Advanced Features

### Add Camera Support (Record Promos in App!)

```bash
npm install @capacitor/camera

# In your component:
import { Camera, CameraResultType } from '@capacitor/camera';

async function recordPromo() {
  const video = await Camera.getPhoto({
    resultType: CameraResultType.Uri,
    quality: 90,
    allowEditing: false,
  });

  // Upload video.webPath to your API
}
```

### Add File Picker

```bash
npm install @capacitor/filesystem

# Choose video from phone gallery
import { Filesystem } from '@capacitor/filesystem';
```

### Add Push Notifications

```bash
npm install @capacitor/push-notifications

# Notify when analysis completes
```

### Add Offline Support

```bash
npm install @capacitor/storage

# Cache analysis results locally
```

---

## Part 4: Publishing to Google Play Store

### Step 1: Create Signed APK

**Generate Keystore:**

```bash
cd android
keytool -genkey -v -keystore my-release-key.jks \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias my-key-alias
```

**Configure Signing:**

Edit `android/app/build.gradle`:

```gradle
android {
    ...
    signingConfigs {
        release {
            storeFile file('my-release-key.jks')
            storePassword 'your-password'
            keyAlias 'my-key-alias'
            keyPassword 'your-password'
        }
    }
    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled false
            ...
        }
    }
}
```

**Build Release APK:**

```bash
./gradlew assembleRelease

# APK at: android/app/build/outputs/apk/release/app-release.apk
```

### Step 2: Create Google Play Developer Account

1. Go to: https://play.google.com/console
2. Pay one-time $25 registration fee
3. Fill out account details

### Step 3: Create App Listing

1. **Create app** → Enter app details
2. **App icon**: 512x512px PNG
3. **Screenshots**:
   - Phone: 4-8 screenshots (16:9 ratio)
   - Tablet: Optional but recommended
4. **Description**:
   ```
   Wrestling Promo Analyzer uses AI to give you detailed feedback on your
   wrestling promos. Choose between traditional coaching or psychological
   analysis. Upload videos, get scored on 9 categories, and improve your
   performance!

   Features:
   • AI-powered video analysis
   • Two expert judge personalities
   • Detailed category scoring
   • Visual analysis of gestures and expressions
   • Actionable feedback and recommendations
   ```
5. **Category**: Entertainment or Sports
6. **Privacy Policy URL**: Create at https://app-privacy-policy-generator.firebaseapp.com/

### Step 4: Upload APK/AAB

**Better option: Build AAB (Android App Bundle):**

```bash
cd android
./gradlew bundleRelease

# Upload: android/app/build/outputs/bundle/release/app-release.aab
```

### Step 5: Content Rating & Pricing

1. Complete content rating questionnaire
2. Set price (Free or Paid)
3. Select countries to distribute

### Step 6: Submit for Review

- Review all sections have green checkmarks
- Click "Submit for review"
- Wait 1-7 days for approval

---

## Part 5: Testing Your APK

### Test Checklist

- [ ] App launches without crashes
- [ ] Can select video from gallery
- [ ] Can record video (if camera enabled)
- [ ] Video upload works
- [ ] Progress bar updates during processing
- [ ] Results display correctly
- [ ] Judge selection works
- [ ] All 9 category scores show
- [ ] Visual analysis displays
- [ ] Navigation works
- [ ] Back button behaves correctly
- [ ] App handles network errors gracefully
- [ ] Works on WiFi and mobile data
- [ ] No memory leaks during long sessions

### Test on Multiple Devices

Test on:
- Small phone (5" screen)
- Large phone (6.5"+ screen)
- Tablet
- Different Android versions (9+)

Use Android emulators in Android Studio!

---

## Part 6: Updating Your App

When you make changes:

```bash
# 1. Update frontend code
cd frontend
# ... make changes ...

# 2. Build
npm run build

# 3. Sync to Android
npx cap sync android

# 4. Rebuild APK
cd android
./gradlew assembleRelease

# 5. Upload new version to Play Store
# Increment version code in android/app/build.gradle:
# versionCode 2
# versionName "1.1.0"
```

---

## Costs Breakdown

| Item | Cost | Notes |
|------|------|-------|
| **Google Play Developer** | $25 one-time | Required to publish |
| **Backend Hosting** | $5-20/month | Railway, Render, or DigitalOcean |
| **Anthropic API** | Per-use | ~$0.05 per video analysis |
| **Domain (optional)** | $10/year | For custom backend URL |
| **SSL Certificate** | Free | Railway/Render include this |

**Total to get started: $25-50**

---

## Troubleshooting

### "Cleartext HTTP traffic not permitted"

**Fix:** Add to `AndroidManifest.xml`:

```xml
<application android:usesCleartextTraffic="true">
```

(Only for development! Production should use HTTPS)

### "Cannot upload video"

1. Check `AndroidManifest.xml` has file permissions
2. Check backend CORS allows capacitor://localhost
3. Test backend API directly with curl

### "App crashes on startup"

1. Check Android Studio logs (Logcat)
2. Ensure `capacitor.config.json` is correct
3. Clean and rebuild:
   ```bash
   cd android
   ./gradlew clean
   ./gradlew build
   ```

### "Build fails in Android Studio"

1. Update Gradle: File → Project Structure → Update
2. Sync Gradle files: File → Sync Project with Gradle Files
3. Invalidate caches: File → Invalidate Caches / Restart

---

## Alternative Approaches

### React Native (NOT RECOMMENDED)

**Why not:**
- Requires complete rewrite of frontend
- Different components (not HTML/CSS)
- Months of work
- Two codebases to maintain

**When to use:**
- Need maximum native performance
- Complex native integrations
- Building from scratch

### Progressive Web App (PWA)

**Pros:**
- No app store needed
- Works on any device
- Easy updates

**Cons:**
- Can't access all native features
- Requires internet connection always
- Less discoverable (not in Play Store)

**How to do it:**
1. Add service worker to frontend
2. Add manifest.json
3. Users add to home screen via browser

---

## Summary

**Quick Steps:**

1. ✅ Deploy backend to Railway/Render ($5/month)
2. ✅ Install Capacitor in frontend
3. ✅ Configure API URL for mobile
4. ✅ Build React app
5. ✅ Add Android platform
6. ✅ Build APK in Android Studio
7. ✅ Test on your phone
8. ✅ Publish to Play Store ($25 one-time)

**Time estimate:**
- First-time: 4-6 hours
- Once you know the process: 30 minutes

**You'll have:**
- Real Android app
- Available in Play Store
- Professional looking UI
- Access to native features
- Easy to update

---

## Next Steps

1. **Read**: `QUICKSTART.md` to understand the full app
2. **Deploy**: Choose Railway, Render, or DigitalOcean
3. **Build**: Follow steps above to create APK
4. **Test**: Install on your phone
5. **Publish**: Submit to Google Play Store
6. **Promote**: Share with wrestling community!

**Questions? Check the logs:**
- `npx cap doctor` - Check Capacitor setup
- `adb logcat` - View Android logs
- Android Studio Logcat window

**Good luck building your app!** 📱🎤🔥
