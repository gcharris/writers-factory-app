# Task: Cleanup Duplicate Files

**Priority:** Low (Technical Debt)
**Estimated Effort:** 15 minutes
**Dependencies:** None

---

## Problem

During development, some files were accidentally duplicated (likely from macOS Finder copy operations). These should be removed.

## Duplicate Files to Remove

### Backend
```
backend/services/llm_service 2.py
backend/services/llm_service 3.py
```

### Frontend
```
frontend/src/lib/stores 2.js
frontend/src/lib/stores 3.js
```

## Verification Steps

1. **Confirm duplicates are identical or older versions:**
   ```bash
   diff "backend/services/llm_service.py" "backend/services/llm_service 2.py"
   diff "backend/services/llm_service.py" "backend/services/llm_service 3.py"
   diff "frontend/src/lib/stores.js" "frontend/src/lib/stores 2.js"
   diff "frontend/src/lib/stores.js" "frontend/src/lib/stores 3.js"
   ```

2. **Check they're not imported anywhere:**
   ```bash
   grep -r "llm_service 2" backend/
   grep -r "llm_service 3" backend/
   grep -r "stores 2" frontend/
   grep -r "stores 3" frontend/
   ```

3. **Remove duplicates:**
   ```bash
   rm "backend/services/llm_service 2.py"
   rm "backend/services/llm_service 3.py"
   rm "frontend/src/lib/stores 2.js"
   rm "frontend/src/lib/stores 3.js"
   ```

4. **Commit cleanup:**
   ```bash
   git add -A
   git commit -m "chore: Remove duplicate files from development"
   ```

---

## Completion Criteria

- [ ] All duplicate files removed
- [ ] No import errors after removal
- [ ] `npm run check` passes
- [ ] Backend starts without errors

---

*Trivial cleanup task - can be done in a few minutes.*
