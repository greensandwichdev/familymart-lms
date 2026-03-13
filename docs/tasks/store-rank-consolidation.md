# Store Rank Consolidation Plan

## Status: COMPLETED

## Overview

Consolidate all rank-related functionality to use `store_rank` (Store Rank DocType) instead of `crew_rank` (Crew Rank DocType). This includes updating backend, frontend, and creating a data migration script.

## Background

The codebase currently has two separate rank systems:
- **Crew Rank**: Used for program membership auto-sync
- **Store Rank**: Created for store management

After this change, only `store_rank` will be used throughout the system.

## Implementation Phases

### Phase 1: Backend Changes

#### 1.1 api.py - get_members()
**File:** `lms/lms/lms/api.py`

| Line | Current | Change To |
|------|---------|-----------|
| 727 | `crew_rank` | `store_rank` |
| 737 | `Crew Rank` | `Store Rank` |
| 743 | `crew_rank_name` | `store_rank_name` |

#### 1.2 api.py - get_users_by_ranks()
**File:** `lms/lms/lms/api.py`

| Line | Current | Change To |
|------|---------|-----------|
| 397 | `crew_rank` | `store_rank` |
| 399 | `crew_rank` | `store_rank` |

#### 1.3 user.py - sync_user_program_by_rank()
**File:** `lms/lms/lms/user.py`

Update function to use `store_rank` instead of `crew_rank`:
- Line 49: Update docstring
- Line 51: Change `doc.crew_rank` to `doc.store_rank`
- Line 60: Change `m.crew_rank` to `m.store_rank`
- Line 72: Change field name in get_value
- Line 73: Change comparison
- Line 77: Change field name in set_value
- Line 86: Change field in append
- Line 99: Change field in query

#### 1.4 lms_program_member.json
**File:** `lms/lms/lms/doctype/lms_program_member/lms_program_member.json`

| Line | Current | Change To |
|------|---------|-----------|
| 10 | `crew_rank` | `store_rank` |
| 39 | `crew_rank` (fieldname) | `store_rank` |
| ~44 | `Crew Rank` (label) | `Store Rank` |
| ~44 | `Crew Rank` (options) | `Store Rank` |

---

### Phase 2: Frontend Changes

#### 2.1 Members.vue
**File:** `frontend/src/components/Settings/Members.vue`

Changes:
1. Line 59: `crew_rank_name` → `store_rank_name`
2. Lines 124-127: Change Link from `Crew Rank` to `Store Rank`, label to "Store Rank"
3. Line 154: Type `crew_rank_name` → `store_rank_name`
4. Line 171: Reactive `crew_rank` → `store_rank`
5. Line 222: API payload `crew_rank` → `store_rank`
6. Line 233: Reset `crew_rank` → `store_rank`

**NEW: Add Store dropdown**
7. Add `lms_store` field to Member type
8. Add `lms_store` to reactive member object
9. Add Store dropdown in form (after store rank)
10. Pass `lms_store` in API payload
11. Reset `lms_store` on success
12. Add store list resource to populate dropdown

Form layout after changes:
- Email (required)
- First Name (required)
- Store (dropdown - optional)
- Store Rank (dropdown - optional)

#### 2.2 ProgramForm.vue
**File:** `frontend/src/pages/ProgramForm.vue`

| Line | Current | Change To |
|------|---------|-----------|
| 229 | `m.crew_rank` | `m.store_rank` |
| 230 | `m.crew_rank` | `m.store_rank` |
| 251 | `m.crew_rank` | `m.store_rank` |
| 252 | `m.crew_rank_name` | `m.store_rank_name` |
| 296 | `crew_rank: u.crew_rank` | `store_rank: u.store_rank` |
| 405 | `crew_rank_name` | `store_rank_name` |

---

### Phase 3: Data Migration

**File:** `lms/lms/patches/store_rank_migration.py` (or similar)

Create migration script to:
1. Copy `crew_rank` values from User doctype to `store_rank` field
2. Copy `crew_rank` values from `lms_program_member` doctype to `store_rank` field
3. Commit changes

Run with: `bench --site [site] execute lms.lms.patches.store_rank_migration.run`

---

### Phase 4: Cleanup (Post-Migration)

After verifying migration was successful:
- Remove `Crew Rank` DocType (if exists and not used elsewhere)
- Remove `crew_rank` field from User doctype (custom field)

---

## Files Summary

| File | Changes |
|------|---------|
| `lms/lms/lms/api.py` | 6 changes |
| `lms/lms/lms/user.py` | 9 changes |
| `lms/lms/lms/doctype/lms_program_member/lms_program_member.json` | 4 changes |
| `frontend/src/components/Settings/Members.vue` | 12 changes |
| `frontend/src/pages/ProgramForm.vue` | 6 changes |

**Total: 5 files to modify + 1 migration script to create**

---

## Admin Workflow After Changes

### Creating a New Member (Settings > Members)
1. Go to **Settings** → **Members**
2. Click **"New"**
3. Fill in:
   - Email (required)
   - First Name (required)
   - Store (optional - dropdown to select LMS Store)
   - Store Rank (optional - dropdown to select Store Rank)
4. Click **Add**

### Assigning Existing Member to Store
1. Go to **Settings** → **Stores**
2. Click the **Users icon** next to a store
3. Click **"Add Member"**
4. Search and select user
5. Select Store Rank
6. Click **Save**

### Editing Member's Store/Rank
1. Go to **Settings** → **Stores**
2. Click the **Users icon** next to a store
3. Click **Pencil icon** next to member
4. Change Store Rank
5. Click **Save**

Or edit directly in Frappe Desk:
1. Go to User list
2. Open User document
3. Edit **LMS Store** and **Store Rank** fields

---

## Verification Checklist

- [x] Run migration script
- [x] Verify User records have `store_rank` populated
- [x] Verify `lms_program_member` records have `store_rank` populated
- [x] Test creating new member via Members.vue with store
- [x] Test editing member rank in Stores.vue
- [x] Test course visibility filtering by rank
- [x] Test auto-sync program enrollment by rank
- [x] Remove Crew Rank DocType (optional)

Consolidate all rank-related functionality to use `store_rank` (Store Rank DocType) instead of `crew_rank` (Crew Rank DocType). This includes updating backend, frontend, and creating a data migration script.

## Background

The codebase currently has two separate rank systems:
- **Crew Rank**: Used for program membership auto-sync
- **Store Rank**: Created for store management

After this change, only `store_rank` will be used throughout the system.

## Implementation Phases

### Phase 1: Backend Changes

#### 1.1 api.py - get_members()
**File:** `lms/lms/lms/api.py`

| Line | Current | Change To |
|------|---------|-----------|
| 727 | `crew_rank` | `store_rank` |
| 737 | `Crew Rank` | `Store Rank` |
| 743 | `crew_rank_name` | `store_rank_name` |

#### 1.2 api.py - get_users_by_ranks()
**File:** `lms/lms/lms/api.py`

| Line | Current | Change To |
|------|---------|-----------|
| 397 | `crew_rank` | `store_rank` |
| 399 | `crew_rank` | `store_rank` |

#### 1.3 user.py - sync_user_program_by_rank()
**File:** `lms/lms/lms/user.py`

Update function to use `store_rank` instead of `crew_rank`:
- Line 49: Update docstring
- Line 51: Change `doc.crew_rank` to `doc.store_rank`
- Line 60: Change `m.crew_rank` to `m.store_rank`
- Line 72: Change field name in get_value
- Line 73: Change comparison
- Line 77: Change field name in set_value
- Line 86: Change field in append
- Line 99: Change field in query

#### 1.4 lms_program_member.json
**File:** `lms/lms/lms/doctype/lms_program_member/lms_program_member.json`

| Line | Current | Change To |
|------|---------|-----------|
| 10 | `crew_rank` | `store_rank` |
| 39 | `crew_rank` (fieldname) | `store_rank` |
| ~44 | `Crew Rank` (label) | `Store Rank` |
| ~44 | `Crew Rank` (options) | `Store Rank` |

---

### Phase 2: Frontend Changes

#### 2.1 Members.vue
**File:** `frontend/src/components/Settings/Members.vue`

Changes:
1. Line 59: `crew_rank_name` → `store_rank_name`
2. Lines 124-127: Change Link from `Crew Rank` to `Store Rank`, label to "Store Rank"
3. Line 154: Type `crew_rank_name` → `store_rank_name`
4. Line 171: Reactive `crew_rank` → `store_rank`
5. Line 222: API payload `crew_rank` → `store_rank`
6. Line 233: Reset `crew_rank` → `store_rank`

**NEW: Add Store dropdown**
7. Add `lms_store` field to Member type
8. Add `lms_store` to reactive member object
9. Add Store dropdown in form (after store rank)
10. Pass `lms_store` in API payload
11. Reset `lms_store` on success
12. Add store list resource to populate dropdown

Form layout after changes:
- Email (required)
- First Name (required)
- Store (dropdown - optional)
- Store Rank (dropdown - optional)

#### 2.2 ProgramForm.vue
**File:** `frontend/src/pages/ProgramForm.vue`

| Line | Current | Change To |
|------|---------|-----------|
| 229 | `m.crew_rank` | `m.store_rank` |
| 230 | `m.crew_rank` | `m.store_rank` |
| 251 | `m.crew_rank` | `m.store_rank` |
| 252 | `m.crew_rank_name` | `m.store_rank_name` |
| 296 | `crew_rank: u.crew_rank` | `store_rank: u.store_rank` |
| 405 | `crew_rank_name` | `store_rank_name` |

---

### Phase 3: Data Migration

**File:** `lms/lms/patches/store_rank_migration.py` (or similar)

Create migration script to:
1. Copy `crew_rank` values from User doctype to `store_rank` field
2. Copy `crew_rank` values from `lms_program_member` doctype to `store_rank` field
3. Commit changes

Run with: `bench --site [site] execute lms.lms.patches.store_rank_migration.run`

---

### Phase 4: Cleanup (Post-Migration)

After verifying migration was successful:
- Remove `Crew Rank` DocType (if exists and not used elsewhere)
- Remove `crew_rank` field from User doctype (custom field)

---

## Files Summary

| File | Changes |
|------|---------|
| `lms/lms/lms/api.py` | 6 changes |
| `lms/lms/lms/user.py` | 9 changes |
| `lms/lms/lms/doctype/lms_program_member/lms_program_member.json` | 4 changes |
| `frontend/src/components/Settings/Members.vue` | 12 changes |
| `frontend/src/pages/ProgramForm.vue` | 6 changes |

**Total: 5 files to modify + 1 migration script to create**

---

## Admin Workflow After Changes

### Creating a New Member (Settings > Members)
1. Go to **Settings** → **Members**
2. Click **"New"**
3. Fill in:
   - Email (required)
   - First Name (required)
   - Store (optional - dropdown to select LMS Store)
   - Store Rank (optional - dropdown to select Store Rank)
4. Click **Add**

### Assigning Existing Member to Store
1. Go to **Settings** → **Stores**
2. Click the **Users icon** next to a store
3. Click **"Add Member"**
4. Search and select user
5. Select Store Rank
6. Click **Save**

### Editing Member's Store/Rank
1. Go to **Settings** → **Stores**
2. Click the **Users icon** next to a store
3. Click **Pencil icon** next to member
4. Change Store Rank
5. Click **Save**

Or edit directly in Frappe Desk:
1. Go to User list
2. Open User document
3. Edit **LMS Store** and **Store Rank** fields

---

## Verification Checklist

- [ ] Run migration script
- [ ] Verify User records have `store_rank` populated
- [ ] Verify `lms_program_member` records have `store_rank` populated
- [ ] Test creating new member via Members.vue with store
- [ ] Test editing member rank in Stores.vue
- [ ] Test course visibility filtering by rank
- [ ] Test auto-sync program enrollment by rank
- [ ] Remove Crew Rank DocType (optional)
