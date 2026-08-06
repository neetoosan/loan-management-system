# Responsive Design - Visual Reference Guide

## Screen Size Comparison

### Login Screen

```
MOBILE (768x1024)          TABLET (1000x768)         DESKTOP (1400x900)
┌─────────────────────┐    ┌──────────────────────┐   ┌────────────────────────┐
│  MORNING STAR       │    │  MORNING STAR        │   │ MORNING STAR │ FORM    │
│  COOPERATIVE        │    │  COOPERATIVE         │   │ COOPERATIVE │ ─────   │
│                     │    │                      │   │             │ [inputs]│
│ [Username     ]     │    │ [Username       ]    │   │             │ [btn]   │
│ [Password     ]     │    │ [Password       ]    │   │             │         │
│ [Sign In      ]     │    │ [Sign In        ]    │   │             │         │
└─────────────────────┘    └──────────────────────┘   └────────────────────────┘
```

### Dashboard Summary Cards

```
MOBILE (768x1024)           TABLET (1024x768)          DESKTOP (1400x900)

Card Layout 1x6             Card Layout 2x3            Card Layout 3x2
(vertical stack)            (two columns)              (3 columns)

┌────┐  ┌────┐             ┌────┐ ┌────┐            ┌────┐ ┌────┐ ┌────┐
│    │  │    │             │    │ │    │            │    │ │    │ │    │
├────┤  ├────┤             ├────┤ ├────┤            ├────┤ ├────┤ ├────┤
│ 1  │  │ 2  │             │ 1  │ │ 2  │            │ 1  │ │ 2  │ │ 3  │
└────┘  └────┘             ├────┤ ├────┤            ├────┤ ├────┤ ├────┤
┌────┐  ┌────┐             │ 3  │ │ 4  │            │ 4  │ │ 5  │ │ 6  │
│    │  │    │             ├────┤ ├────┤            └────┘ └────┘ └────┘
├────┤  ├────┤             │ 5  │ │ 6  │
│ 3  │  │ 4  │             └────┘ └────┘
└────┘  └────┘

Icon Sizes:
Mobile: 28px  |  Tablet: 32px  |  Desktop: 36px

Font Sizes:
Mobile: 18px  |  Tablet: 20px  |  Desktop: 24px
```

### Dashboard Charts

```
MOBILE (768x1024)          TABLET (1000x768)        DESKTOP (1400x900)

VERTICAL STACK             OPTION 1 (VERTICAL)      SIDE-BY-SIDE

┌──────────────────┐       ┌──────────────┐         ┌──────────┬──────────┐
│ Contribution     │       │ Contribution │         │Contrib   │ Loan     │
│ Chart           │       │ Chart (250px)│         │ Chart    │ Chart    │
│ (200px high)    │       ├──────────────┤         │(300px)   │(300px)   │
│                  │       │ Loan Chart   │         │          │          │
├──────────────────┤       │ (250px high) │         └──────────┴──────────┘
│ Loan Chart      │       └──────────────┘
│ (200px high)    │
└──────────────────┘

Spacing:
Mobile: 10px  |  Tablet: 15px  |  Desktop: 20px
```

---

## Component Sizing Reference

### Summary Cards

| Size | Mobile | Tablet | Desktop |
|------|--------|--------|---------|
| **Icon** | 28px | 32px | 36px |
| **Value Font** | 18px | 20px | 24px |
| **Title Font** | 10px | 11px | 11px |
| **Height** | 100px | 120px | 140px |
| **Padding** | 12px | 14px | 16px |

### Tables

| Size | Mobile | Tablet | Desktop |
|------|--------|--------|---------|
| **Max Height** | 300px | 400px | 500px |
| **Font Size** | 10px | 11px | 12px |
| **Scroll** | Horizontal | Horizontal | Auto |

### Charts

| Size | Mobile | Tablet | Desktop |
|------|--------|--------|---------|
| **Height** | 200px | 250px | 300px |
| **Layout** | Vertical | Flexible | Side-by-side |
| **Title Font** | 14px | 15px | 17px |
| **Label Font** | 8px | 9px | 10px |

### Dialogs

| Size | Mobile | Tablet | Desktop |
|------|--------|--------|---------|
| **Width** | 100% - 40px | 100% - 60px | 450-500px |
| **Max Height** | 90% screen | 85% screen | 600px |
| **Padding** | 12px | 15px | 15px |

### Buttons

| Size | Mobile | Tablet | Desktop |
|------|--------|--------|---------|
| **Layout** | Stacked (Column) | Row with wrap | Row |
| **Width** | 100% | Auto with wrap | Auto |
| **Height** | 48px+ | 40px | 40px |
| **Font Size** | 14px | 13px | 13px |

---

## Spacing Scale

```
Padding/Margin Values:

Mobile:    10px  (Compact, touch-friendly)
Tablet:    15px  (Balanced)
Desktop:   20px  (Generous, optimal reading)

Header Spacing:
Mobile:    15px between sections
Tablet:    20px between sections
Desktop:   30px between sections

Button Spacing:
Mobile:    12px (vertical stacking)
Tablet:    10px (horizontal)
Desktop:   10px (horizontal)
```

---

## Font Scale

```
Base Font Scaling:

Category          Mobile (80%) | Tablet (90%) | Desktop (100%)
─────────────────────────────────────────────────────────────
Heading (32px)       25px     →    28px      →    32px
Title (24px)         19px     →    21px      →    24px
Subtitle (18px)      14px     →    16px      →    18px
Body (14px)          11px     →    12px      →    14px
Small (12px)         10px     →    11px      →    12px
Label (11px)         8px      →    10px      →    11px

Special Cases:
- Chart labels scale differently (important for readability)
- Button text: 12px constant across all sizes
- Icon labels: 9px (mobile) → 10px (desktop)
```

---

## Color & Contrast

```
Colors remain constant across all screen sizes:

Primary:        #0066ff (Blue-200)
Background:     #1a1a1a (Dark)
Surface:        #2a2a2a (Slightly lighter)
Success:        #4CAF50 (Green-400)
Warning:        #FF9800 (Orange-400)
Danger:         #f44336 (Red-400)
Text Primary:   #FFFFFF (White)
Text Secondary: #9E9E9E (Grey)

High contrast maintained for readability at all sizes
```

---

## Breakpoint Reference

```
Screen Size | Device Type | Layout Style | UI Density
──────────────────────────────────────────────────────
< 768px     | Mobile      | Full-width   | Compact
768-1024px  | Tablet      | Flexible     | Balanced
1024-1200px | Tablet      | 2-col        | Balanced
> 1200px    | Desktop     | Multi-col    | Optimal

Window Size Constraints:
- Minimum Width:  768px  (tablet minimum)
- Minimum Height: 700px  (safe minimum)
- Recommended:    1400x900px (desktop)
```

---

## Responsive Flow Diagram

```
                    Page Width Detected
                            |
                ┌───────────┼───────────┐
                ↓           ↓           ↓
            < 768px    768-1024px   > 1200px
              │            │            │
          Mobile        Tablet       Desktop
              │            │            │
        ┌─────┼─────┐  ┌────┼────┐  ┌──┼──┐
        ↓     ↓     ↓  ↓    ↓    ↓  ↓  ↓  ↓
       Font Card  Layout Button Table Font
       Size  Size Select  Style Scroll Color
       80%  Small Vertical Full   H-Scroll Const
       │     │     │       │      │     │
       └─────┴─────┴───────┴──────┴─────┘
            |
            ↓
        Render UI
```

---

## Touch Target Sizes

```
Recommended minimum touch target sizes:

Mobile (< 768px):
- Buttons: 48px × 48px minimum
- Icons: 36px × 36px minimum
- Input fields: 44px height minimum
- Spacing between: 8px minimum

Tablet (768-1024px):
- Buttons: 40px × 40px minimum
- Icons: 32px × 32px minimum
- Spacing between: 10px minimum

Desktop (> 1024px):
- Can use smaller sizes
- Spacing: 10-20px
```

---

## Performance Considerations

```
Responsive Design Impact:

Mobile (Smaller Sizes):
✓ Smaller assets (icons, images)
✓ Reduced chart complexity
✓ Simplified dialogs
✓ Better battery life
✓ Faster rendering

Desktop (Larger Sizes):
✓ Full feature set visible
✓ More detailed charts
✓ Rich animations (500ms transitions)
✓ Optimal layout

All Sizes:
✓ Same functionality
✓ Same data accuracy
✓ Same features
✓ Consistent experience
```

---

## Testing Scenarios

### Mobile Portrait (768x1024)
```
✓ Login flows vertically
✓ Single column dashboard
✓ Charts stack vertically
✓ Buttons full width
✓ Tables scroll horizontally
```

### Tablet Landscape (1024x768)
```
✓ Cards in 2 columns
✓ Charts may be side-by-side
✓ Flexible button layout
✓ Readable font sizes
✓ Balanced spacing
```

### Desktop (1400x900+)
```
✓ Full multi-column layout
✓ Optimal spacing
✓ Side-by-side charts
✓ All features visible
✓ Professional appearance
```

---

## Quick Reference Checklist

### When Adding New Components

- [ ] Import ResponsiveConfig and helpers
- [ ] Detect screen size: `is_small = ResponsiveConfig.is_small_screen(page)`
- [ ] Use responsive sizing: `get_responsive_font_size(page, base_size)`
- [ ] Adapt layout: Use `create_responsive_row()` or conditional Column/Row
- [ ] Test on 3 sizes: Mobile (768), Tablet (1024), Desktop (1400)
- [ ] Verify text readability
- [ ] Check button sizes are tappable
- [ ] Ensure no text overflow
- [ ] Test window resizing

### When Updating Existing Components

- [ ] Replace hardcoded sizes with responsive functions
- [ ] Remove fixed widths (use expand=True or responsive width)
- [ ] Update padding: Use `get_responsive_padding(page)`
- [ ] Scale fonts: Use `get_responsive_font_size(page, size)`
- [ ] Convert layouts: Horizontal ↔ Vertical based on screen
- [ ] Test all breakpoints

---

## File Reference

| File | Purpose | Status |
|------|---------|--------|
| `responsive.py` | Responsive utilities | ✅ Complete |
| `login_screen.py` | Login UI | ✅ Updated |
| `main_window.py` | Dashboard | ✅ Updated |
| `main.py` | Window config | ✅ Updated |
| `loan_screen.py` | Loan management | ⏳ Next |
| `contribution_screen.py` | Contributions | ⏳ Next |

---

**Last Updated:** January 4, 2026
**Status:** Login & Dashboard Complete | Ready for Full Deployment
