# Manual Test: Terminal UI Interface

## Test Environment
- **URL**: http://localhost:8081
- **Browser**: Any modern browser
- **Date**: 2025-06-11
- **Tester**: Manual verification

## Test Objectives
Verify the terminal-style UI changes and DATA FLOW PIPELINE behavior after departing from TDD paradigm for UI polish.

## Visual Design Tests

### 1. Header Section ✅
- [ ] **Title displays**: "RAG Scraper" (not "RAG_SCRAPER")
- [ ] **Subtitle displays**: "DATA EXTRACTION TERMINAL" 
- [ ] **Subtitle color**: White text (not gray/muted)
- [ ] **No "//" prefix**: Subtitle should NOT have "//" before text
- [ ] **Status bar displays**: "SYSTEM_READY // AWAITING_TARGET_URLs"

### 2. DATA FLOW PIPELINE States ✅
- [ ] **Initial state**: Pipeline is DIMMED (approximately 40% opacity)
- [ ] **Visual elements**: Shows "WEB_SCAN → EXTRACT → RAG_DATA" flow
- [ ] **Icons visible**: 🌐 ⚡ 📊 icons display correctly
- [ ] **Arrows present**: → arrows between steps are visible

### 3. Terminal Aesthetics ✅
- [ ] **Dark theme**: Background is dark (#0a0a0a)
- [ ] **Font**: JetBrains Mono used throughout interface
- [ ] **Colors**: Green (#00ff88), amber (#ffaa00), cyan (#00aaff) accents
- [ ] **Matrix background**: Subtle floating binary digits visible
- [ ] **Terminal styling**: Input fields have terminal appearance

## Functional Tests

### 4. URL Input & Validation ✅
- [ ] **Placeholder text**: Shows example restaurant URLs
- [ ] **Terminal styling**: Input has dark background with green focus
- [ ] **Live validation**: URL validation works as you type
- [ ] **Status updates**: Status bar updates during validation

### 5. Format Selection ✅
- [ ] **Three options**: TEXT, PDF, DUAL format cards
- [ ] **Default selection**: TEXT is selected by default
- [ ] **Visual feedback**: Hover effects and selection states work
- [ ] **Status updates**: Status bar updates when format is selected

### 6. Pipeline Animation Test ✅
**Pre-scraping (INACTIVE):**
- [ ] **Dimmed state**: Pipeline at 40% opacity
- [ ] **No animation**: No pulsing or glowing effects

**During scraping (ACTIVE):**
- [ ] **Bright state**: Pipeline becomes full opacity (100%)
- [ ] **Pulsing animation**: Each step pulses with green glow
- [ ] **Staggered timing**: Steps animate in sequence (0s, 0.5s, 1s delays)
- [ ] **Continuous loop**: Animation repeats throughout extraction

**Post-scraping (INACTIVE):**
- [ ] **Returns to dimmed**: Pipeline dims back to 40% opacity
- [ ] **Animation stops**: No more pulsing effects

## Integration Test with Real Data

### 7. Complete Workflow Test ✅
**Test URLs to use:**
```
https://rudyssteakhouse.com
https://ilovewom.com
```

**Steps:**
1. [ ] Enter test URLs in terminal-style input
2. [ ] Select "TEXT" format
3. [ ] Click "EXECUTE_EXTRACTION"
4. [ ] **Verify**: Pipeline activates (bright + animated)
5. [ ] **Verify**: Status bar shows extraction progress
6. [ ] **Verify**: Terminal-style progress logging appears
7. [ ] **Verify**: Results show with clickable file links
8. [ ] **Verify**: Pipeline deactivates after completion
9. [ ] Test file download links work

## Expected Behavior Summary

### Visual States:
- **IDLE**: Dimmed pipeline, "SYSTEM_READY" status
- **ACTIVE**: Bright animated pipeline, progress updates
- **COMPLETE**: Dimmed pipeline, success message with file links

### Terminal Features:
- Monospace font throughout
- Dark theme with neon accents
- Real-time status updates
- Professional technical language
- Clickable file downloads

## Test Results
**Date Tested**: ___________  
**Browser**: ___________  
**Overall Status**: ⬜ PASS ⬜ FAIL  

**Issues Found**:
- [ ] None
- [ ] List any issues here

**Notes**:
```
[Space for tester notes]
```

---

**Test Completion**: Once all checkboxes are verified, the terminal UI changes are confirmed working outside the TDD cycle and ready for production use.