# 0003 - Members Page CRUD Implementation

## Objective

Add full CRUD (Create, Read, Update, Delete) functionality to the `/members` page for store member management.

---

## Current State

The `/members` page currently only supports:
- **Read**: Display member list with search and pagination

Missing functionality:
- **Create**: Add new member button and form
- **Update**: Edit member's store/rank
- **Delete**: Remove member from store

---

## Implementation Plan

### Phase 1: Add Create Member (New Button)

- [ ] 1.1 Add "New Member" button in header (next to Search)
- [ ] 1.2 Create Dialog form with fields:
  - Email (required)
  - First Name (required)
  - Store (Link to LMS Store)
  - Store Rank (Link to Store Rank)
- [ ] 1.3 Implement form submission using `frappe.client.insert` API

### Phase 2: Add Update Member (Edit)

- [ ] 2.1 Add Actions column to ListView (after Role column)
- [ ] 2.2 Add Edit button in each row's actions
- [ ] 2.3 Pre-populate form with existing member data
- [ ] 2.4 Use existing `lms.lms.store.assign_member_to_store` API for updates

### Phase 3: Add Delete Member (Remove)

- [ ] 3.1 Add Delete button in each row's actions (next to Edit)
- [ ] 3.2 Show confirmation dialog before delete
- [ ] 3.3 Use existing `lms.lms.store.remove_member_from_store` API

### Phase 4: Testing

- [ ] 4.1 Test Create - add new member
- [ ] 4.2 Test Read - view member list
- [ ] 4.3 Test Update - edit member store/rank
- [ ] 4.4 Test Delete - remove member from store

---

## Backend APIs (Already Available)

| Operation | API | Parameters |
|-----------|-----|------------|
| Create | `frappe.client.insert` | `{doctype: 'User', email, first_name, store_rank, lms_store}` |
| Update | `lms.lms.store.assign_member_to_store` | `member, store, rank` |
| Delete | `lms.lms.store.remove_member_from_store` | `member` |

---

## UI Mockup (After Implementation)

```
┌─────────────────────────────────────────────────────────────┐
│  Members                              [Search] [New Member] │
├─────────────────────────────────────────────────────────────┤
│  [Name] [Email] [Rank] [Region] [Role] [Actions]          │
├─────────────────────────────────────────────────────────────┤
│  John Doe | john@... | Staff | DKI Jakarta | - | [✏️][🗑️] │
│  Jane Doe | jane@... | Manager | Jawa Barat | - | [✏️][🗑️] │
└─────────────────────────────────────────────────────────────┘
```

---

## Files to Modify

### Modify (1 file)

1. `frontend/src/pages/Members.vue`
   - Add "New Member" button in header
   - Add Actions column to ListView
   - Add Create/Edit/Delete dialogs
   - Implement form submissions

---

## Acceptance Criteria

### Functional Requirements

1. ✅ User can click "New Member" button to open add member form
2. ✅ User can fill in email, first name, store, and rank to create new member
3. ✅ User can see member list with search functionality
4. ✅ User can click Edit button to modify member's store and rank
5. ✅ User can click Delete button to remove member from store
6. ✅ Confirmation dialog appears before deletion

### UX Requirements

7. ✅ Form validation shows error for required fields
8. ✅ Loading states are displayed during API calls
9. ✅ Success/error messages are shown after operations
10. ✅ Forms are properly reset after successful operations

---

## Timeline Estimate

- Phase 1 (Create): ~20 minutes
- Phase 2 (Update): ~15 minutes
- Phase 3 (Delete): ~10 minutes
- Phase 4 (Testing): ~15 minutes

**Total: ~1 hour**
