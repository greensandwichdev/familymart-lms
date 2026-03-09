# Region-Based Course Enrollment

## Objective

Add Indonesia administrative hierarchy (Province → Regency → District) to enable admin to enroll courses by region/province/regency/district.

---

## Edge Cases

| Scenario | Result |
|----------|--------|
| User with no store | Excluded from region enrollment |
| Store with no region set | Excluded when region filter active |
| Store has partial region | Matches in relevant filters |
| Both rank + region filters | User must match BOTH (AND logic) |

---

## Implementation Status

### Phase 1: Create Administrative DocTypes - COMPLETED

**Created (12 files):**

| File | Description |
|------|-------------|
| `lms/lms/doctype/province/__init__.py` | Province DocType init |
| `lms/lms/doctype/province/province.json` | Province DocType definition (name, code) |
| `lms/lms/doctype/province/province.py` | Province controller with cascade delete for regencies |
| `lms/lms/doctype/province/province.js` | Province client script |
| `lms/lms/doctype/regency/__init__.py` | Regency DocType init |
| `lms/lms/doctype/regency/regency.json` | Regency DocType (name, code, province link) |
| `lms/lms/doctype/regency/regency.py` | Regency controller with cascade delete for districts |
| `lms/lms/doctype/regency/regency.js` | Regency client script |
| `lms/lms/doctype/district/__init__.py` | District DocType init |
| `lms/lms/doctype/district/district.json` | District DocType (name, code, regency link) |
| `lms/lms/doctype/district/district.py` | District controller (leaf node) |
| `lms/lms/doctype/district/district.js` | District client script |

### Phase 2: Create JSON Fixtures - COMPLETED

| File | Records | Description |
|------|---------|-------------|
| `lms/lms/fixtures/province.json` | 34 | Indonesia provinces |
| `lms/lms/fixtures/regency.json` | ~514 | Indonesia regencies |
| `lms/lms/fixtures/district.json` | - | Not used (districts imported via migration script) |

**Data Source:** https://github.com/fityannugroho/idn-area-data

### Phase 3: Extend Store & User - COMPLETED

**Updated `lms/lms/doctype/lms_store/lms_store.json`:**
- Added `region_section` (Section Break)
- Added `province` (Link: Province)
- Added `regency` (Link: Regency, depends_on: province)
- Added `district` (Link: District, depends_on: regency)

**Updated `lms/lms/fixtures/custom_field.json`:**
- Added `region_section` (Section Break) to User
- Added `province` (Link: Province) to User
- Added `regency` (Link: Regency) to User
- Added `district` (Link: District) to User

### Phase 4: Backend API Changes - COMPLETED

**Updated `lms/lms/store.py`:**
- Added `get_provinces()` - Get all provinces
- Added `get_regencies(province)` - Get regencies by province
- Added `get_districts(regency)` - Get districts by regency
- Updated `get_stores()` to return region fields

**Updated `lms/lms/api.py`:**
- Modified `get_users_by_ranks()` to accept optional region filters:
  - `province` - Filter by province
  - `regency` - Filter by regency
  - `district` - Filter by district
- Both rank + region filters use AND logic
- Updated `get_members()` to return region fields

### Phase 5: Frontend Changes - COMPLETED

**Updated `frontend/src/components/Settings/Stores.vue`:**
- Added cascading dropdown filters: Province → Regency → District
- On change: filter next dropdown options based on selection
- Stores can be filtered by region

**Updated `frontend/src/pages/ProgramForm.vue`:**
- Added optional region filter dropdowns in member enrollment section
- When enrollment type is "By Store Rank", admin can filter by province/regency/district
- Region parameters passed to `get_users_by_ranks` API call

**Updated `frontend/src/components/Settings/Members.vue`:**
- Display user's region info (province, regency, district)

---

## API Endpoints

| Endpoint | Method | Parameters |
|----------|--------|------------|
| `lms.lms.store.get_provinces` | GET | - |
| `lms.lms.store.get_regencies` | GET | `province` |
| `lms.lms.store.get_districts` | GET | `regency` |
| `lms.lms.store.get_stores` | GET | Returns region fields |
| `lms.lms.api.get_members` | GET | Returns region info |
| `lms.lms.api.get_users_by_ranks` | GET | `rank`, `province`, `regency`, `district` |

---

## Files Created/Modified

### Created (15 files):

**DocTypes (12 files):**
1. `lms/lms/doctype/province/__init__.py`
2. `lms/lms/doctype/province/province.json`
3. `lms/lms/doctype/province/province.py`
4. `lms/lms/doctype/province/province.js`
5. `lms/lms/doctype/regency/__init__.py`
6. `lms/lms/doctype/regency/regency.json`
7. `lms/lms/doctype/regency/regency.py`
8. `lms/lms/doctype/regency/regency.js`
9. `lms/lms/doctype/district/__init__.py`
10. `lms/lms/doctype/district/district.json`
11. `lms/lms/doctype/district/district.py`
12. `lms/lms/doctype/district/district.js`

**Fixtures (3 files):**
13. `lms/lms/fixtures/province.json`
14. `lms/lms/fixtures/regency.json`
15. `lms/lms/fixtures/district.json`

### Modified (7 files):

1. `lms/lms/doctype/lms_store/lms_store.json` - Added region fields
2. `lms/lms/fixtures/custom_field.json` - Added region fields to User
3. `lms/lms/lms/store.py` - Added region lookup endpoints
4. `lms/lms/lms/api.py` - Updated get_users_by_ranks and get_members
5. `frontend/src/components/Settings/Stores.vue` - Added region filter dropdowns
6. `frontend/src/pages/ProgramForm.vue` - Added region filter in enrollment
7. `frontend/src/components/Settings/Members.vue` - Display region info

### Migration Script (1 file):
16. `lms/lms/district_migration.py` - Script to import ~7,266 districts

---

## District Migration Script

Due to the large number of districts (~7,266), a migration script is provided to import them programmatically.

**File:** `lms/lms/district_migration.py`

**To run:**
```bash
bench --site [site] execute lms.lms.district_migration.run
```

**What it does:**
1. Downloads districts CSV from https://github.com/fityannugroho/idn-area-data
2. Maps regency codes to regency names (requires Regency fixtures to be loaded first)
3. Creates District records in batches of 100
4. Reports progress via Frappe realtime events
5. Skips existing districts (idempotent)

**Prerequisites:**
- Province and Regency fixtures must be loaded first
- Network access to GitHub (or modify script to use local CSV)

---

## Next Steps

1. Run fixtures to import provinces and regencies:
   ```
   bench --site [site] migrate
   ```

2. Run district migration script:
   ```
   bench --site [site] execute lms.lms.district_migration.run
   ```

3. Test the complete flow:
   - Create stores with region
   - Assign users to stores
   - Enroll courses by region
