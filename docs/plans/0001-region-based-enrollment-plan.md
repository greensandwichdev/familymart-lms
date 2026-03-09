# 0001 - Region-Based Course Enrollment

## Objective
Add province → regency → district hierarchy to Store doctype and enable admin to enroll courses by region/province/regency/district.

---

## Edge Cases

| Scenario | Result |
|----------|--------|
| User with no store | Excluded from region enrollment |
| Store with no region set | Excluded when region filter active |
| Store has partial region | Matches in relevant filters |
| Both rank + region filters | User must match BOTH (AND logic) |

---

## 1: Create Administrative DocTypes

 Implementation

### Phase| File | Description |
|------|-------------|
| `lms/lms/doctype/province/province.json` | Province (Provinsi) |
| `lms/lms/doctype/province/province.py` | Province DocType |
| `lms/lms/doctype/regency/regency.json` | Regency (Kabupaten/Kota) - child of Province |
| `lms/lms/doctype/regency/regency.py` | Regency DocType |
| `lms/lms/doctype/district/district.json` | District (Kecamatan) - child of Regency |
| `lms/lms/doctype/district/district.py` | District DocType |

**DocType Structure:**

**Province:**
- `name` (Data) - Province name
- `code` (Data) - Province code

**Regency:**
- `name` (Data) - Regency name  
- `code` (Data) - Regency code
- `province` (Link: Province)

**District:**
- `name` (Data) - District name
- `code` (Data) - District code
- `regency` (Link: Regency)

---

### Phase 2: Create JSON Fixtures for Indonesia Data

| File | Description |
|------|-------------|
| `lms/lms/fixtures/province.json` | 34 Provinces |
| `lms/lms/fixtures/regency.json` | ~500 Regencies |
| `lms/lms/fixtures/district.json` | ~7000 Districts |

---

### Phase 3: Extend Store & User

**3.1 Add fields to LMS Store** (`lms/lms/doctype/lms_store/lms_store.json`):

```json
{
  "fieldname": "province",
  "fieldtype": "Link",
  "options": "Province",
  "label": "Province"
},
{
  "fieldname": "regency",
  "fieldtype": "Link",
  "options": "Regency", 
  "label": "Regency"
},
{
  "fieldname": "district",
  "fieldtype": "Link",
  "options": "District",
  "label": "District"
}
```

**3.2 Add fields to User** (via `lms/lms/fixtures/custom_field.json`):

```json
{
  "dt": "User",
  "fieldname": "province",
  "fieldtype": "Link",
  "options": "Province",
  "label": "Province"
},
{
  "dt": "User",
  "fieldname": "regency", 
  "fieldtype": "Link",
  "options": "Regency",
  "label": "Regency"
},
{
  "dt": "User",
  "fieldname": "district",
  "fieldtype": "Link",
  "options": "District", 
  "label": "District"
}
```

---

### Phase 4: Backend API Changes

**4.1 Update `lms/lms/store.py`**:

Add new functions:
```python
@frappe.whitelist()
def get_provinces():
    return frappe.get_all("Province", order_by="name")

@frappe.whitelist()
def get_regencies(province):
    return frappe.get_all("Regency", {"province": province}, order_by="name")

@frappe.whitelist()
def get_districts(regency):
    return frappe.get_all("District", {"regency": regency}, order_by="name")
```

**4.2 Update `lms/lms/api.py`**:

Modify `get_users_by_ranks()` function to accept optional region filters:

```python
@frappe.whitelist()
def get_users_by_ranks(rank, province=None, regency=None, district=None):
    filters = {"enabled": 1, "name": ["not in", ["Administrator", "Guest"]]}
    
    if rank:
        filters["store_rank"] = ["in", rank]
    
    # Region filtering via store
    if any([province, regency, district]):
        store_filters = {"is_active": 1}
        if province:
            store_filters["province"] = province
        if regency:
            store_filters["regency"] = regency  
        if district:
            store_filters["district"] = district
            
        stores = frappe.get_all("LMS Store", store_filters, pluck="name")
        
        if stores:
            filters["lms_store"] = ["in", stores]
        else:
            return []
    
    users = frappe.get_all(
        "User",
        filters=filters,
        fields=["name", "full_name", "user_image", "username", "store_rank"],
    )
    
    return users
```

---

### Phase 5: Frontend Changes

**5.1 Update `frontend/src/components/Settings/Stores.vue`**:

- Add three cascading dropdowns: Province → Regency → District
- On change: filter next dropdown options based on selection
- When saving store: save selected region values

**5.2 Update `frontend/src/pages/ProgramForm.vue`**:

- Add optional region filter dropdowns in member enrollment section
- Pass region parameters to `get_users_by_ranks` API call

**5.3 Update `frontend/src/components/Settings/Members.vue`**:

- Display user's store region info (province, regency, district)

---

## API Endpoints

| Endpoint | Method | Parameters |
|----------|--------|------------|
| `lms.lms.store.get_provinces` | GET | - |
| `lms.lms.store.get_regencies` | GET | `province` |
| `lms.lms.store.get_districts` | GET | `regency` |
| `lms.lms.api.get_users_by_ranks` | GET | `rank`, `province`, `regency`, `district` |

---

## Files to Create/Modify

### Create (6 files):
1. `lms/lms/doctype/province/province.json`
2. `lms/lms/doctype/province/province.py`
3. `lms/lms/doctype/regency/regency.json`
4. `lms/lms/doctype/regency/regency.py`
5. `lms/lms/doctype/district/district.json`
6. `lms/lms/doctype/district/district.py`

### Create Fixtures (3 files):
7. `lms/lms/fixtures/province.json`
8. `lms/lms/fixtures/regency.json`
9. `lms/lms/fixtures/district.json`

### Modify (4 files):
10. `lms/lms/doctype/lms_store/lms_store.json`
11. `lms/lms/fixtures/custom_field.json`
12. `lms/lms/store.py`
13. `lms/lms/api.py`

### Modify Frontend (3 files):
14. `frontend/src/components/Settings/Stores.vue`
15. `frontend/src/pages/ProgramForm.vue`
16. `frontend/src/components/Settings/Members.vue`

---

## Total: 16 files
