# 0004 - Store Management Page Revamp

## Overview

Transform Stores page from ListView to Grid Card layout and create new StoreDetail page with store info, member CRUD, and enrollment analytics.

---

## Phase 1: Grid Card Layout for Stores Page

### 1.1 Create StoreCard Component

**File:** `frontend/src/components/StoreCard.vue`

Card displaying:
- Store name (title)
- Store code, organization
- Region (province/regency/district)
- Member count badge
- Store image (if available) with gradient fallback
- Hover effect with shadow

### 1.2 Update Stores.vue

**File:** `frontend/src/pages/Stores.vue`

- Replace `ListView` with grid layout
- Wrap cards with `router-link` to `/stores/:storeName`
- Keep search and region filters
- Remove Actions column

---

## Phase 2: StoreDetail Page

### 2.1 Add Route

**File:** `frontend/src/router.js`

```javascript
{
  path: '/stores/:storeName',
  name: 'StoreDetail',
  component: () => import('@/pages/StoreDetail.vue'),
  props: true,
}
```

### 2.2 Create API: get_store_details

**File:** `lms/lms/lms/store.py`

```python
@frappe.whitelist()
def get_store_details(store):
    """Returns comprehensive store details including members and analytics."""
    store_doc = frappe.get_doc("LMS Store", store)
    
    # Get members
    members = frappe.get_all("User", 
        filters={"lms_store": store},
        fields=["name", "full_name", "email", "store_rank", "enabled"]
    )
    
    # Enrich with rank names
    for m in members:
        if m.store_rank:
            rank_doc = frappe.get_doc("Store Rank", m.store_rank)
            m.rank_name = rank_doc.rank_name
    
    # Get member count by rank
    member_stats = {}
    for m in members:
        rank = m.store_rank or "No Rank"
        member_stats[rank] = member_stats.get(rank, 0) + 1
    
    # Get program-level enrollment data
    # For each member, get their program memberships with progress
    enrollments = frappe.get_all(
        "LMS Program Member",
        filters=[["member", "in", [m.name for m in members]]],
        fields=["member", "parent", "progress"]
    )
    
    # Group by program
    program_stats = {}
    for e in enrollments:
        if e.parent not in program_stats:
            program_stats[e.parent] = {"total": 0, "completed": 0, "in_progress": 0}
        program_stats[e.parent]["total"] += 1
        if e.progress == 100:
            program_stats[e.parent]["completed"] += 1
        elif e.progress > 0:
            program_stats[e.parent]["in_progress"] += 1
    
    return {
        "name": store_doc.name,
        "store_name": store_doc.store_name,
        "store_code": store_doc.store_code,
        "organization": store_doc.organization,
        "address": store_doc.address,
        "image": store_doc.image,
        "province": store_doc.province,
        "regency": store_doc.regency,
        "district": store_doc.district,
        "is_active": store_doc.is_active,
        "members": members,
        "member_count": len(members),
        "member_stats": member_stats,
        "enrollments": enrollments,
        "program_stats": program_stats,
    }
```

### 2.3 Create StoreDetail.vue Page

**File:** `frontend/src/pages/StoreDetail.vue`

Structure:
```
┌─────────────────────────────────────────────────────────────┐
│  Breadcrumbs: Home / Stores / Store Name                   │
├─────────────────────────────────────────────────────────────┤
│  Store Name                                                │
│  Store Code | Organization                                 │
├───────────────────────────┬─────────────────────────────────┤
│  MAIN CONTENT (2/3)       │  SIDEBAR (1/3)                 │
│  ─────────────────        │  ─────────────                 │
│  • Store Info Section     │  • Store Image                 │
│    - Address, Region     │    - Image display             │
│                          │    - Change Image button       │
│  • Member List (Table)   │  • Stats Cards                 │
│    - Name, Email, Rank, │    - Total Members              │
│      Status, Actions     │    - Enrollments               │
│    - Add/Edit/Delete    │    - Completed                 │
│                          │                                 │
│  • Program Enrollments   │  • Enrollment Chart            │
│    - List of programs    │    - DonutChart (progress)     │
│      with enrollment     │                                 │
│        stats             │  • Rank Distribution            │
│                          │    - DonutChart                │
└───────────────────────────┴─────────────────────────────────┘
```

**Features:**
- **Member CRUD**: Add, Edit, Delete members (reuse existing API endpoints)
- **Member Table**: Show name, email, rank, status, actions
- **Add/Edit Member Dialog**: Form with email, name, store_rank
- **Store Image**: Display and upload image using FileUploader
- **Enrollment Charts**: 
  - DonutChart: Member progress (completed/in-progress/not started)
  - DonutChart: Member distribution by rank

---

## Phase 3: Remove Store from Settings

### Overview

Store management is now accessible only from the main sidebar (`/stores` page), not from Settings popup dialog.

### 3.1 Remove Stores from Settings

**File:** `frontend/src/components/Settings/Settings.vue`

- Removed Stores import
- Removed Stores tab from settings menu

### Result

- **Stores** are only accessible via `/stores` page (main sidebar)
- **Store Detail** accessible via `/stores/:storeName`
- No longer available in Settings popup

---

## Phase 4: Store Image Support

### Overview

Allow admin to set a custom image for each store that displays in the StoreCard grid.

### 4.1 Add Image Field to LMS Store DocType

**File:** `lms/lms/lms/doctype/lms_store/lms_store.json`

Added image field:
```json
{
  "fieldname": "image",
  "fieldtype": "Attach Image",
  "label": "Store Image"
}
```

### 4.2 Update Backend API

**File:** `lms/lms/lms/store.py`

Updated `get_stores()` and `get_stores_with_member_count()` to include image field.

### 4.3 StoreCard.vue

Already has logic to display `store.image` - no changes needed.

### 4.4 Add Image Upload in StoreDetail Page

**File:** `frontend/src/pages/StoreDetail.vue`

Added Store Image section in sidebar with:
- Display current image (or gradient fallback)
- "Change Image" button using Frappe's FileUploader
- Uses `lms.lms.store.update_store` API to save

---

## Files Summary

| File | Action | Description |
|------|--------|-------------|
| `frontend/src/components/StoreCard.vue` | Create | Grid card component |
| `frontend/src/pages/Stores.vue` | Modify | Replace ListView with grid |
| `frontend/src/pages/StoreDetail.vue` | Create | New detail page with member CRUD & image upload |
| `frontend/src/router.js` | Modify | Add `/stores/:storeName` route |
| `frontend/src/components/Settings/Settings.vue` | Modify | Remove Stores tab |
| `lms/lms/lms/store.py` | Modify | Add `get_store_details()` and `get_stores_with_member_count()` endpoints |
| `lms/lms/lms/doctype/lms_store/lms_store.json` | Modify | Add image field |

---

## Requirements Summary

1. ✅ **Analytics**: Include program-level enrollment data
2. ✅ **Member Actions**: CRUD for members directly in detail page
3. ✅ **Store Management**: Only accessible from main sidebar (not Settings)
4. ✅ **Store Image**: Upload via StoreDetail page using FileUploader

---

## How Admin Uses It

### Access Stores
1. Go to **Stores** in the main sidebar
2. Click on a store card to view details
3. Manage members, view analytics

### Upload Store Image
1. Go to **Stores** → Click on a store
2. In the sidebar, click **Change Image**
3. Select an image file
4. Image will display on store cards

### Alternative: Via Frappe Desk
1. Go to **Frappe Desk** → **LMS Store** list
2. Open a store document
3. Click "Attach Image" in the "Store Image" field
4. Save

---

## Timeline Estimate

- Phase 1 (Grid Card): ~20 min
- Phase 2 (StoreDetail): ~1.5 hours
- Phase 3 (Remove from Settings): ~10 min
- Phase 4 (Image Support): ~30 min
- Testing: ~30 min

**Total: ~3 hours**
