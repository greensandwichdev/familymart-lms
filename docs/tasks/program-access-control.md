# Program Access Control - Store Rank + Region Based

## Problem

Currently, when adding a Store Rank to a Program, the system:
1. Fetches all users with that rank
2. Attempts to add ALL of them to the program
3. Shows error "All selected members are already in the program" if they already exist

This doesn't match the expected behavior where Store Rank should be a **program configuration** (which ranks can access), not an enrollment action.

## Goal

Implement a flexible program access control system where a program can be assigned to:
- Specific store rank(s)
- Specific region(s) (province/regency/district)
- Specific member(s)
- Or any combination of all

User matches ANY rule → gets access to the program.

---

## Implementation Plan

### Phase 1: Backend

#### 1.1 Create Child DocType: LMS Program Rank

File: `lms/lms/lms/doctype/lms_program_rank/lms_program_rank.json`

Fields:
- `store_rank`: Link → Store Rank (required)
- `rank_name`: Data (fetched from store_rank.rank_name, read_only)
- `province`: Data (optional - region filter)
- `regency`: Data (optional - region filter)
- `district`: Data (optional - region filter)
- `date_added`: Date (default: today)

#### 1.2 Update LMS Program DocType

File: `lms/lms/lms/doctype/lms_program/lms_program.json`

Add field:
```json
{
  "fieldname": "program_ranks",
  "fieldtype": "Table",
  "label": "Program Ranks",
  "options": "LMS Program Rank"
}
```

Keep existing `program_members` for manual member assignments.

#### 1.3 Create API: `sync_program_members_by_ranks`

File: `lms/lms/lms/api.py`

```python
@frappe.whitelist()
def sync_program_members_by_ranks(program):
    """Sync program members based on program_ranks configuration."""
    # 1. Get all program_ranks for the program
    # 2. For each rank + region combo, find users with that rank
    # 3. Add users to program_members (skip if already exists)
    # 4. Update store_rank field on each program_member row
```

#### 1.4 Modify `assign_member_to_store` in store.py

File: `lms/lms/lms/store.py`

After assigning rank, call `sync_program_members_by_ranks` for programs that have this rank configured.

#### 1.5 Modify `update_member_rank` in store.py

File: `lms/lms/lms/store.py`

When user's rank changes, re-sync all programs.

#### 1.6 Migration Script

- Extract unique store_ranks from existing program_members
- Create program_ranks rows for each unique rank
- Clear store_rank from program_members (keep members but mark as manual)

---

### Phase 2: Frontend

#### 2.1 Update ProgramForm.vue

File: `frontend/src/pages/ProgramForm.vue`

**Dialog Changes:**
- Keep region filters (not removed)
- Just select Store Rank → add to program_ranks with optional region filters
- Store rank + region filters together in program_ranks table

**UI Display:**
- Rename "Members by Rank" → "Program Ranks"
- Display ranks from program_ranks table
- Show rank + region info in each row
- Show member count per rank (computed from program_members where store_rank matches)

**Remove/Edit Rank:**
- Remove from program_ranks:
  - Members with progress > 1%: Keep in program, clear store_rank (becomes manual)
  - Members with progress = 0%: Remove from program

---

### Phase 3: Access Check (Future)

When checking if user can access program:

```python
def user_can_access_program(user, program):
    # Check program_members - direct assignment
    if frappe.db.exists('LMS Program Member', {'parent': program, 'member': user}):
        return True
    
    # Check program_ranks - by rank
    user_rank = frappe.db.get_value('User', user, 'store_rank')
    if frappe.db.exists('LMS Program Rank', {'parent': program, 'store_rank': user_rank}):
        return True
    
    # Check program_ranks - by region
    user_store = frappe.db.get_value('User', user, 'lms_store')
    # ... check if user's store region matches any program region
    
    return False
```

---

## Data Structure Summary

### LMS Program

| Field | Type | Description |
|-------|------|-------------|
| title | Data | Program name |
| program_courses | Table | Program courses |
| program_ranks | Table | Rank-based access config |
| program_members | Table | Manual member assignments |

### LMS Program Rank (Child)

| Field | Type | Description |
|-------|------|-------------|
| store_rank | Link | Store Rank |
| rank_name | Data | Rank name (fetched) |
| province | Data | Filter by province (optional) |
| regency | Data | Filter by regency (optional) |
| district | Data | Filter by district (optional) |
| date_added | Date | When added |

### LMS Program Member (Child) - Existing

| Field | Type | Description |
|-------|------|-------------|
| member | Link | User |
| store_rank | Link | Store Rank (optional - null = manual) |
| full_name | Data | User full name |
| progress | Int | Progress percentage |
