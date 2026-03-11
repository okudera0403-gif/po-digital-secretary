# PO Digital Secretary - Development Plan

## Design Guidelines

### Design References
- **Medical/Clinical SaaS**: Clean, professional, trustworthy
- **Style**: Modern Professional Medical + Light Theme

### Color Palette
- Primary: #1E40AF (Medical Blue)
- Secondary: #F0F9FF (Light Blue Background)
- Accent: #059669 (Success Green)
- Warning: #D97706 (Amber)
- Background: #F8FAFC (Light Gray)
- Card: #FFFFFF (White)
- Text Primary: #1E293B (Dark Slate)
- Text Secondary: #64748B (Slate)

### Typography
- Font: Inter (clean, professional sans-serif)
- Headings: font-weight 700
- Body: font-weight 400

### Key Component Styles
- Cards: White background, subtle shadow, 8px rounded
- Buttons: Blue primary, rounded-md
- Tables: Clean borders, alternating row colors
- Forms: Clean inputs with labels

## Database Tables (Created)
- insurance_types (11 records)
- product_categories (5 records)
- products (10 records)
- parts (30 records)
- cases (user-owned)

## Files to Create

### Frontend Pages (8 files max)
1. `src/pages/Index.tsx` - Main dashboard with login gate, case list, navigation
2. `src/pages/CaseForm.tsx` - Case input form (create/edit)
3. `src/pages/CaseList.tsx` - Case list table with actions
4. `src/pages/ManufacturingInstruction.tsx` - Manufacturing instruction with PDF export
5. `src/pages/EstimateGeneration.tsx` - Estimate generation with PDF export
6. `src/pages/AIMedicalOpinion.tsx` - AI medical opinion draft generation
7. `src/pages/PartsSearch.tsx` - Parts search by category/product
8. `src/components/Layout.tsx` - Shared layout with navigation sidebar

### App Configuration
- `src/App.tsx` - Routes setup
- `index.html` - Title update

## Implementation Notes
- Use jspdf for PDF generation
- Use web-sdk client.ai.gentxt with deepseek-v3.2 for AI medical opinion
- Use web-sdk client.auth for login
- Use web-sdk client.entities for CRUD operations
- All text in Japanese for UI labels