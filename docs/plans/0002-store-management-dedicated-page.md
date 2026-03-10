# 0002 - Store Management Dedicated Page

## Objective

Create a dedicated standalone page for Store and Member management to replace the current popup dialog approach in Settings. This will improve user experience by providing a full-page interface instead of managing data in constrained dialogs.

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

Create a new standalone page `/store-management` with:

1. **Sidebar Navigation** (left panel, ~200px width)
   - Stores - Manage stores and their members
   - Members - Member directory across all stores

2. **Main Content Area** (right side, flexible width)
   - Renders the selected component (Stores or Members)

### UI Mockup

```
┌─────────────────────────────────────────────────────────────┐
│  Header (Breadcrumbs, Page Title)                         │
├──────────────┬──────────────────────────────────────────────┤
│              │                                              │
│  Stores     │    [Main Content Area]                      │
│  (nav)      │    - Store list with filters                 │
│              │    - OR Member directory                     │
│  Members    │    - Forms for add/edit                       │
│  (nav)      │                                              │
│              │                                              │
└──────────────┴──────────────────────────────────────────────┘
```

---

## Edge Cases

### 1. Authentication & Authorization

| Scenario | Expected Behavior |
|----------|-------------------|
| Anonymous user accesses `/store-management` | Redirect to login or show access denied |
| User without Store Manager role accesses page | Show permission error or hide sensitive data |
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
| User directly visits `/store-management` | Load page with default tab (Stores) |
| User visits `/store-management?tab=members` | Load page with Members tab active |
| User refreshes page | Preserve current tab selection via URL query param |
| Browser back button from another page | Return to previous page, not previous tab |

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

### Phase 1: Create New Page Component

**File:** `frontend/src/pages/StoreManagement.vue`

Structure:
```vue
<template>
  <div class="flex h-screen">
    <!-- Sidebar Navigation -->
    <aside class="w-56 bg-[#39bdf8] p-4">
      <!-- Nav items -->
    </aside>
    
    <!-- Main Content -->
    <main class="flex-1 overflow-auto p-6">
      <component :is="activeComponent" />
    </main>
  </div>
</template>
```

Key features:
- Route-aware tab state (syncs with URL query param)
- Responsive sidebar (collapsible on mobile)
- Reuses existing `Stores.vue` and `Members.vue` components

### Phase 2: Add Route

**File:** `frontend/src/router.js`

```javascript
{
  path: '/store-management',
  name: 'StoreManagement',
  component: () => import('@/pages/StoreManagement.vue'),
}
```

**Note:** Add route guard to check authentication and permissions.

### Phase 3: Add Sidebar Navigation

**File:** `frontend/src/utils/index.js`

Add to `getSidebarLinks()`:
```javascript
{
  label: 'Stores',
  icon: 'Store',
  to: 'StoreManagement',
  activeFor: ['StoreManagement'],
}
```

### Phase 4: URL State Management

**Query Parameter Strategy:**
- Use `?tab=stores` or `?tab=members` in URL
- Default to `?tab=stores`
- This enables:
  - Browser history navigation
  - Bookmarking
  - Sharing direct links

### Phase 5: Optional Enhancements (Future)

1. **Breadcrumb Integration**: Add proper breadcrumbs for navigation hierarchy
2. **Keyboard Shortcuts**: Add shortcuts for quick navigation (e.g., `Ctrl+1` for Stores, `Ctrl+2` for Members)
3. **Search Everywhere**: Global search across stores and members
4. **Activity Log**: Track recent changes to stores/members

---

## Files to Create/Modify

### Create (1 file)
1. `frontend/src/pages/StoreManagement.vue` - New standalone page

### Modify (3 files)
1. `frontend/src/router.js` - Add new route
2. `frontend/src/utils/index.js` - Add sidebar navigation item
3. `frontend/src/components/Settings/Settings.vue` - Optionally remove Stores tab (or keep for backward compatibility)

---

## Backward Compatibility

- Keep Stores tab in Settings.vue for existing users who may have bookmarked it
- Existing `openSettings('Stores')` calls will still work (open Settings dialog to Stores tab)
- Consider adding a banner in Settings dialog pointing to the new dedicated page

---

## Acceptance Criteria

1. ✅ New `/store-management` page is accessible via sidebar
2. ✅ Page shows Stores tab by default
3. ✅ User can switch between Stores and Members tabs
4. ✅ Tab selection is reflected in URL (e.g., `?tab=members`)
5. ✅ Directly visiting URL with tab param loads correct tab
6. ✅ Sidebar persists when navigating between tabs
7. ✅ Existing popup dialogs in Stores.vue/Members.vue work within the new page
8. ✅ Responsive design works on tablet and desktop
9. ✅ Loading and error states are handled gracefully

---

## Timeline Estimate

- Phase 1-3: ~1-2 hours
- Phase 4: ~30 minutes
- Testing & edge cases: ~1 hour

**Total: ~3-4 hours**
