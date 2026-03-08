# Program Enrollment Consolidation Plan

## Overview

Consolidate the program enrollment mechanism to support two methods:
1. **By Store Rank**: Admin selects a Store Rank → all users with that rank get enrolled
2. **By Member Selection**: Admin directly selects specific users → those users get enrolled

Additionally, new users with a store_rank will automatically be enrolled to programs that have matching store_rank (auto-enrollment - already implemented).

## Background

Current state:
- Program members can only be enrolled via Store Rank selection
- The LMS Program Member DocType requires store_rank (reqd: 1)
- Auto-enrollment for new users is already implemented in user.py

## Requirements

1. **Two enrollment methods**: Support both "By Store Rank" and "By Member Selection"
2. **Store Rank optional**: Make store_rank field optional in LMS Program Member
3. **Multi-select**: Allow selecting multiple users when enrolling by member selection
4. **Separate display**: Show TWO separate lists:
   - **Members by Rank**: Shows unique store ranks with member counts
   - **Members by Selection**: Shows individually selected members with full name and email
5. **Auto-enrollment**: Already covered - new users with store_rank automatically enrolled to matching programs

## Implementation Phases

### Phase 1: DocType Changes

#### 1.1 LMS Program Member - Make store_rank optional
**File:** `lms/lms/lms/doctype/lms_program_member/lms_program_member.json`

| Field | Current | Change To |
|-------|---------|-----------|
| `store_rank` | `reqd: 1` | `reqd: 0` |

---

### Phase 2: Frontend Changes - Enrollment Dialog

#### 2.1 ProgramForm.vue - Add enrollment type toggle
**File:** `frontend/src/pages/ProgramForm.vue`

Add radio buttons/toggle in the "New Program Member" dialog:
- "By Store Rank" (default)
- "By Member Selection"

#### 2.2 Update dialog form fields
**File:** `frontend/src/pages/ProgramForm.vue`

Show appropriate dropdown based on selection:
- **By Store Rank**: Store Rank dropdown (existing - keep as is)
- **By Member Selection**: User dropdown with multi-select support (new)

#### 2.3 Fetch user details for member selection
**File:** `frontend/src/pages/ProgramForm.vue`

When enrolling by "By Member Selection", fetch actual user details:

```javascript
// Method 2: By Member Selection
const userDetails = await call('frappe.client.get', {
    doctype: 'User',
    name: userName,
})
memberList.push({
    member: userName,
    store_rank: null,
    full_name: userDetails.full_name,
    email: userDetails.email,
})
```

---

### Phase 3: Frontend Changes - Separate Lists Display

#### 3.1 Add computed properties to filter members
**File:** `frontend/src/pages/ProgramForm.vue`

```javascript
// Members with store_rank (enrolled by rank)
const membersByRank = computed(() => 
    (program.doc?.program_members || []).filter(m => m.store_rank)
)

// Members without store_rank (enrolled directly)
const membersByMember = computed(() => 
    (program.doc?.program_members || []).filter(m => !m.store_rank)
)

// Unique ranks with member count
const rankSummary = computed(() => {
    const ranks = {}
    membersByRank.value.forEach(m => {
        if (!ranks[m.store_rank]) {
            ranks[m.store_rank] = { 
                rank: m.store_rank, 
                rank_name: m.store_rank_name, 
                count: 0 
            }
        }
        ranks[m.store_rank].count++
    })
    return Object.values(ranks)
})
```

#### 3.2 Add column definitions
**File:** `frontend/src/pages/ProgramForm.vue`

```javascript
// Columns for "Members by Rank" list
const rankColumns = [
    { label: 'Store Rank', key: 'rank_name', width: '60%' },
    { label: 'Members', key: 'count', width: '40%' },
]

// Columns for "Members by Selection" list
const memberDirectColumns = [
    { label: 'Full Name', key: 'full_name', width: '40%' },
    { label: 'Email', key: 'email', width: '40%' },
    { label: 'Progress (%)', key: 'progress', width: '20%' },
]
```

#### 3.3 Update template - Two ListViews
**File:** `frontend/src/pages/ProgramForm.vue`

Replace single ListView with two separate ListViews:

```vue
<!-- Section 1: Members by Rank -->
<div class="mb-8">
    <div class="text-lg font-semibold">{{ __('Members by Rank') }}</div>
    <ListView :columns="rankColumns" :rows="rankSummary" ...>
</div>

<!-- Section 2: Members by Selection -->
<div>
    <div class="text-lg font-semibold">{{ __('Members by Selection') }}</div>
    <ListView :columns="memberDirectColumns" :rows="membersByMember" ...>
</div>
```

---

### Phase 4: Handle Deletion

- **By Rank list**: Deleting a rank removes ALL members with that store_rank
- **By Member list**: Deleting selected members removes only selected individuals

---

### Phase 5: Backend - Auto-enrollment (Already Implemented)

#### 5.1 user.py - sync_user_program_by_rank()
**File:** `lms/lms/lms/user.py`

Already implemented - no changes needed:
- `after_insert` hook: Calls sync on new user creation
- `on_update` hook: Calls sync when user is updated
- `sync_user_program_by_rank()`: Enrolls users to programs matching their store_rank

**Behavior:**
- User gets store_rank → auto-enrolled to programs with matching store_rank
- User store_rank changes → enrollment updated
- User has no store_rank → no auto-enrollment (manual only)

---

## Files Summary

| File | Changes |
|------|---------|
| `lms/lms/lms/doctype/lms_program_member/lms_program_member.json` | 1 change - make store_rank optional |
| `frontend/src/pages/ProgramForm.vue` | ~40 changes - toggle, multi-select, computed properties, two ListViews, deletion logic |

---

## Admin Workflow After Changes

### Adding Members

#### Method 1: By Store Rank
1. Go to **Program** → Click **"Add Member"**
2. Select **"By Store Rank"** (default)
3. Choose **Store Rank** from dropdown
4. Click **Add**
5. **Result**: All users with that store_rank are enrolled
   - Future new users with that store_rank will also be auto-enrolled

#### Method 2: By Member Selection
1. Go to **Program** → Click **"Add Member"**
2. Select **"By Member"**
3. Search and select **specific users** (multi-select supported)
4. Click **Add**
5. **Result**: Selected users are enrolled directly (store_rank is blank)

### Viewing Members

#### Members by Rank Section
- Shows unique store ranks enrolled in the program
- Each rank displays: Store Rank name, Members count
- Deleting a rank removes ALL members with that rank

#### Members by Selection Section
- Shows individually selected members
- Displays: Full Name, Email, Progress
- Deleting removes only selected individual members

---

## Auto-enrollment Behavior

| Scenario | Result |
|----------|--------|
| New user created with store_rank="Staff" | Auto-enrolled to programs with "Staff" store_rank |
| Existing user's store_rank changed to "Manager" | Auto-enrolled to programs with "Manager" store_rank |
| User removed from store_rank | Removed from programs (non-matching) |
| User enrolled by "Member Selection" (no store_rank) | Not affected by auto-enrollment |

---

## Verification Checklist

- [ ] Make store_rank optional in LMS Program Member DocType
- [ ] Test enrollment by store rank
- [ ] Test enrollment by member selection (multi-select)
- [ ] Verify user details (full_name, email) are stored when enrolling by member
- [ ] Verify two separate lists display correctly:
  - Members by Rank shows unique ranks with counts
  - Members by Selection shows full name, email, progress
- [ ] Test deletion from each list:
  - Deleting rank removes all members with that rank
  - Deleting member removes only selected individual
- [ ] Verify auto-enrollment for new users with store_rank
