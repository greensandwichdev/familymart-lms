# 0002 - Store Management Dedicated Page

## Objective

Create two separate standalone pages for Store and Member management to replace the current popup dialog approach in Settings. This will improve user experience by providing full-page interfaces instead of managing data in constrained dialogs.

---

## Current State

### Problems with Current Implementation

1. **Popup Dialog Constraints**: Store and member management happens entirely within a large dialog (`Settings.vue`), which:
   - Limits screen real estate for complex operations
   - Requires users to navigate through multiple dialog layers (Store list → Members dialog → Add/Edit member dialog)
   - Feels cramped when managing many stores or members

2. **Navigation**: Users access stores only through Settings → Stores tab, requiring:
   - Opening the Settings dialog
   - Clicking on Stores section
   - Then managing members opens another nested dialog

3. **No Direct Routing**: Store management is not accessible via URL, making it difficult to:
   - Share direct links
   - Use browser back/forward navigation
   - Bookmark specific views

---

## Proposed Solution

### Page Structure

Create two separate standalone pages:

1. **`/stores`** - Store list page
2. **`/members`** - Member directory page

Both pages use the existing main AppSidebar (not a separate sidebar).

### UI Mockup

```
AppSidebar (existing):
├── Dashboard
├── Courses
├── Batches
├── Certified Members
├── Jobs
├── Statistics
├── Stores        ← NEW (/stores)
└── Members       ← NEW (/members)

Stores Page:
┌─────────────────────────────────────────────────────────────┐
│  Breadcrumbs: Home / Stores                                │
├─────────────────────────────────────────────────────────────┤
│  Stores                                                    │
│  Manage stores and their members                           │
├─────────────────────────────────────────────────────────────┤
│  [Search] [Province] [Regency] [District]                │
├─────────────────────────────────────────────────────────────┤
│  [Store List with filters and actions]                    │
└─────────────────────────────────────────────────────────────┘

Members Page:
┌─────────────────────────────────────────────────────────────┐
│  Breadcrumbs: Home / Members                               │
├─────────────────────────────────────────────────────────────┤
│  Members                                                   │
│  View and manage members across all stores                │
├─────────────────────────────────────────────────────────────┤
│  [Search]                                                 │
├─────────────────────────────────────────────────────────────┤
│  [Member List with profile links and roles]               │
└─────────────────────────────────────────────────────────────┘
```

---

## Edge Cases

### 1. Authentication & Authorization

| Scenario | Expected Behavior |
|----------|-------------------|
| Anonymous user accesses `/stores` or `/members` | Redirect to login or show access denied |
| User without Moderator/System Manager role accesses page | Show permission error or redirect to home |
| User session expires while on page | Redirect to login, then back to page after re-auth |

### 2. Data Loading

| Scenario | Expected Behavior |
|----------|-------------------|
| No stores exist | Show empty state with helpful message |
| No members exist | Show empty state in Members view |
| Large number of stores (100+) | Implement pagination or virtual scrolling |
| Large number of members (1000+) | Implement pagination |
| API request fails | Show error toast, allow retry |
| Slow network connection | Show loading states, don't block UI |

### 3. Navigation

| Scenario | Expected Behavior |
|----------|-------------------|
| User directly visits `/stores` | Load stores page |
| User directly visits `/members` | Load members page |
| User refreshes page | Stay on current page |
| Browser back button from another page | Return to previous page |

### 4. Form Validation

| Scenario | Expected Behavior |
|----------|-------------------|
| Add store with duplicate name | Show validation error, prevent save |
| Add store with missing required fields | Highlight fields, show error messages |
| Edit store while another user edits same store | Last save wins, show warning if stale data detected |
| Add member with email already in system | Show error or offer to link existing user |

### 5. Data Integrity

| Scenario | Expected Behavior |
|----------|-------------------|
| Delete store with members assigned | Warn user, require confirmation or unassign first |
| Change member's store rank to higher than allowed | Show validation error |
| Bulk assign members to store | Show progress, handle partial failures gracefully |

### 6. UX Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Very long store name | Truncate with ellipsis, show full name on hover |
| Many province/regency/district filters | Optimize dropdown loading, consider search |
| User has slow device | Optimize rendering, avoid heavy computations |
| Concurrent operations (add + delete same item) | Handle race conditions gracefully |

---

## Implementation Plan

### Phase 1: Cleanup

Delete incorrect implementation files:
- `frontend/src/pages/StoreManagement.vue`
- `frontend/src/components/StoreManagement/` folder

### Phase 2: Add Routes

**File:** `frontend/src/router.js`

```javascript
{
  path: '/stores',
  name: 'Stores',
  component: () => import('@/pages/Stores.vue'),
},
{
  path: '/members',
  name: 'Members',
  component: () => import('@/pages/Members.vue'),
},
```

### Phase 3: Add Sidebar Navigation

**File:** `frontend/src/utils/index.js`

Add to `getSidebarLinks()`:
```javascript
{
  label: 'Stores',
  icon: 'Store',
  to: 'Stores',
  activeFor: ['Stores'],
},
{
  label: 'Members',
  icon: 'Users',
  to: 'Members',
  activeFor: ['Members'],
},
```

### Phase 4: Create Pages

**File:** `frontend/src/pages/Stores.vue`

- Full-page layout (like Statistics.vue)
- Breadcrumbs, header, description
- Search and region filters (province, regency, district)
- Store list with member management (using ListView component)
- Reuse API calls from Settings/Stores.vue

**File:** `frontend/src/pages/Members.vue`

- Full-page layout (like Statistics.vue)
- Breadcrumbs, header, description
- Search functionality
- Member list with profile links (using ListView component)
- Pagination (load more)
- Reuse API calls from Settings/Members.vue

---

## Files to Create/Modify

### Create (2 files)

1. `frontend/src/pages/Stores.vue` - Stores page with full-page layout
2. `frontend/src/pages/Members.vue` - Members page with full-page layout

### Modify (2 files)

1. `frontend/src/router.js` - Add `/stores` and `/members` routes
2. `frontend/src/utils/index.js` - Add Stores and Members sidebar links

### Delete

1. `frontend/src/pages/StoreManagement.vue` - Incorrect implementation
2. `frontend/src/components/StoreManagement/` - Incorrect implementation

### Keep Unchanged (for backward compatibility)

1. `frontend/src/components/Settings/Stores.vue` - Existing dialog component
2. `frontend/src/components/Settings/Members.vue` - Existing dialog component
3. `frontend/src/components/Settings/Settings.vue` - Keep Stores tab in Settings dialog

---

## Backward Compatibility

- Keep Stores tab in Settings.vue for existing users who may have bookmarked it
- Existing `openSettings('Stores')` calls will still work (open Settings dialog to Stores tab)
- New `/stores` and `/members` pages provide better UX for store and member management

---

## Acceptance Criteria

### Functional Requirements

1. ✅ New `/stores` page is accessible via main sidebar
2. ✅ New `/members` page is accessible via main sidebar
3. ✅ Stores page displays store list with filters
4. ✅ Stores page allows managing store members
5. ✅ Members page displays member directory
6. ✅ Members page allows viewing member profiles
7. ✅ Existing popup dialogs in Stores.vue/Members.vue continue to work (Settings dialog)
8. ✅ Loading and error states are handled gracefully

### Permission Requirements

9. ✅ Anonymous user accessing `/stores` or `/members` is redirected or shown access denied
10. ✅ User without Moderator/System Manager role cannot access the pages
11. ✅ Session expiry handling (redirect to login)

### Navigation Requirements

12. ✅ Browser back/forward navigation works correctly
13. ✅ Pages can be bookmarked

### UX Requirements

14. ✅ Responsive design works on tablet and desktop
15. ✅ Empty states show helpful messages
16. ✅ Loading states are displayed during data fetch
17. ✅ Pages follow existing layout patterns (Statistics.vue style)

---

## Timeline Estimate

### Phase 1: Cleanup
- Delete incorrect files: ~5 minutes

### Phase 2: Add Routes
- router.js modifications: ~10 minutes

### Phase 3: Add Sidebar Navigation
- utils/index.js modifications: ~10 minutes

### Phase 4: Create Pages
- Stores.vue: ~30 minutes
- Members.vue: ~20 minutes

### Phase 5: Testing
- ~30 minutes

**Total: ~1.5 hours**
