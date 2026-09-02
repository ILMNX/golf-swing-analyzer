# Golf Swing Analyzer — Visual Design Moodboard

## 1. Design Direction

**Core aesthetic:** Premium Sports Technology / Performance Analytics

The interface should feel like a professional golf performance tool rather than a generic AI dashboard.

### Design keywords

- Premium
- Technical
- Athletic
- Precise
- Data-driven
- Minimal
- Dark
- Editorial
- Professional
- High contrast
- Performance-focused

### Avoid

- Excessive glassmorphism
- Overuse of gradients
- Neon cyberpunk aesthetics
- Excessive rounded cards
- Generic AI-dashboard layouts
- Decorative 3D elements without purpose
- Too many colors
- Excessive shadows
- Purple/blue "AI" gradients

---

# 2. Color Palette

The primary palette is intentionally restrained. Green is used as the golf/performance accent while the dark neutrals create a premium sports-tech environment.

| Color | Hex | RGB | Usage |
|---|---|---|---|
| Obsidian | `#0B0F14` | 11, 15, 20 | Main background |
| Graphite | `#151A21` | 21, 26, 33 | Cards, panels, secondary surfaces |
| Golf Green | `#1E7A3D` | 30, 122, 61 | Primary accent, active states, charts |
| Fairway Green | `#A6E3A1` | 166, 227, 161 | Highlight, positive metrics, secondary accent |
| Off White | `#E8E8E8` | 232, 232, 232 | Primary text, headings |

## 2.1 Obsidian — `#0B0F14`

**Role:** Primary application background.

Use for:
- Main page background
- Navigation background
- Full-screen analyzer
- Video analysis canvas
- Empty space around major components

**Character:** Almost-black with a subtle blue/neutral undertone.

This should replace pure black (`#000000`) in most situations because it feels less harsh and gives the UI more depth.

---

## 2.2 Graphite — `#151A21`

**Role:** Secondary surface.

Use for:
- Metric cards
- Side panels
- Data containers
- Modal backgrounds
- Navigation containers
- Secondary sections

**Character:** Dark graphite rather than a typical gray card.

The contrast against `#0B0F14` should remain subtle.

---

## 2.3 Golf Green — `#1E7A3D`

**Role:** Primary brand/accent color.

Use for:
- Active navigation
- Primary buttons
- Selected states
- Chart lines
- Swing trajectory
- Detection overlays
- Progress indicators
- Key interactive elements

**Character:** Deep, mature golf green.

Avoid using this as a large background color. It works best as an accent.

---

## 2.4 Fairway Green — `#A6E3A1`

**Role:** Secondary/highlight accent.

Use for:
- Positive performance indicators
- Important data points
- Small highlights
- Chart highlights
- Swing markers
- Success states
- Subtle visual emphasis

**Character:** Soft green that contrasts against the dark interface.

Use sparingly. It should feel like a highlight rather than the primary brand color.

---

## 2.5 Off White — `#E8E8E8`

**Role:** Primary text.

Use for:
- Page titles
- Metric values
- Navigation labels
- Important information
- Main UI copy

Avoid pure white (`#FFFFFF`) for most text.

---

# 3. Recommended Extended Color System

The five core colors can be extended with neutral and semantic colors.

```text
Background
#0B0F14  Obsidian

Surface
#151A21  Graphite

Border
#252C35  Dark Border

Primary
#1E7A3D  Golf Green

Primary Highlight
#A6E3A1  Fairway Green

Text Primary
#E8E8E8  Off White

Text Secondary
#9AA3AD  Muted Gray

Text Disabled
#5C6570  Disabled Gray

Success
#A6E3A1  Fairway Green

Warning
#D6A84F  Muted Amber

Error
#D96C6C  Muted Red
```

### Color usage ratio

A useful starting point:

```text
70%  #0B0F14  Background
15%  #151A21  Surfaces
8%   #E8E8E8  Typography
5%   #1E7A3D  Primary accent
2%   #A6E3A1  Highlight
```

The interface should remain predominantly dark.

---

# 4. Typography

## Primary Display Font — Montserrat

**Recommended weights:**
- 600 — Semibold
- 700 — Bold
- 800 — ExtraBold

Use Montserrat for:
- Hero headings
- Page titles
- Large metric numbers
- Section headings
- Score displays
- Important labels

### Example

```text
SWING ANALYSIS

86
OVERALL SCORE

CLUB SPEED
78 MPH
```

Montserrat gives the product a strong athletic/editorial character.

---

# 5. Secondary UI Font — Inter

**Recommended weights:**
- 400 — Regular
- 500 — Medium
- 600 — Semibold

Use Inter for:
- Body text
- Descriptions
- Navigation
- Tables
- Metric labels
- Tooltips
- Form elements
- Small UI text

### Example

```text
Your swing has improved by 8%
compared with your previous session.
```

Inter keeps dense analytical information readable.

---

# 6. Typography Hierarchy

| Element | Font | Weight | Suggested Size |
|---|---|---:|---:|
| Hero | Montserrat | 700–800 | 48–72px |
| Page Title | Montserrat | 700 | 32–40px |
| Section Title | Montserrat | 600 | 20–24px |
| Large Metric | Montserrat | 700 | 40–64px |
| Metric Value | Montserrat | 600–700 | 24–32px |
| UI Label | Inter | 500–600 | 11–13px |
| Body | Inter | 400 | 14–16px |
| Caption | Inter | 400 | 11–12px |

---

# 7. Layout Style

## General principle

Use **structured asymmetry** rather than a generic centered dashboard.

The UI should feel closer to:

> Golf performance lab + sports broadcast graphics + professional analytics software

than:

> Generic SaaS dashboard.

### Recommended layout

```text
┌──────────────────────────────────────────────────────┐
│ Navigation                                            │
├───────────────┬──────────────────────────┬───────────┤
│               │                          │           │
│   Controls    │      Swing Video        │ Metrics   │
│               │                          │           │
│               │                          │           │
├───────────────┴──────────────────────────┴───────────┤
│ Swing Timeline                                        │
├──────────────────────────────────────────────────────┤
│ Performance Analytics                                 │
└──────────────────────────────────────────────────────┘
```

Prioritize the **actual swing video** over generic dashboard cards.

---

# 8. Card Style

Cards should be restrained.

### Recommended

```text
Background: #151A21
Border: 1px solid #252C35
Radius: 8–12px
Shadow: Minimal or none
```

Avoid:

```text
Huge radius
Strong shadows
Heavy glass blur
Gradient backgrounds
Floating cards everywhere
```

The product should feel like professional equipment software.

---

# 9. Border Style

Use borders to establish hierarchy instead of shadows.

### Primary border

```text
#252C35
1px
```

### Active border

```text
#1E7A3D
1px
```

### Highlight

```text
#A6E3A1
```

A subtle 1px border is preferable to a large shadow.

---

# 10. Border Radius

Recommended scale:

```text
4px   Small controls
6px   Inputs / buttons
8px   Standard cards
12px  Major panels
16px  Large media containers
```

Avoid making every element `rounded-full` or excessively rounded.

---

# 11. Buttons

## Primary Button

```text
Background: #1E7A3D
Text: #E8E8E8
Radius: 6–8px
Weight: 600
```

Example:

```text
[ Analyze Swing ]
```

## Secondary Button

```text
Background: transparent
Border: #252C35
Text: #E8E8E8
Radius: 6–8px
```

Example:

```text
[ Compare Session ]
```

## Ghost Button

```text
Background: transparent
Text: #9AA3AD
```

Use for low-priority actions.

---

# 12. Data Visualization

The analytics should look like **sports performance instrumentation**, not a generic business dashboard.

## Chart style

Use:
- Thin lines
- Minimal grid
- Strong primary data line
- Small data points
- Clear units
- Dark background
- Green accents

### Example metrics

```text
CLUB SPEED
78 MPH

SWING TEMPO
2.8 : 1

ATTACK ANGLE
-3.2°

CLUB PATH
1.4° IN → OUT

FACE ANGLE
0.8°
```

Avoid pie charts unless they communicate something genuinely useful.

For swing analysis, prefer:
- Line charts
- Scatter plots
- Trajectory visualization
- Timeline visualization
- Comparison graphs
- Radar charts only when useful
- Video overlays

---

# 13. Golf Swing Visualization

This should be the visual centerpiece.

Potential overlays:

```text
        Shoulder Line
       ───────────────

             ○
            /|
           / |
          /  |
         /   |
        /    |
       /     |
      ●───────→ Club Path
```

Use:

- `#A6E3A1` for important detected points
- `#1E7A3D` for trajectory/path
- `#E8E8E8` for neutral anatomical guides

Keep overlays thin and technical.

---

# 14. Video Timeline

The swing timeline should resemble professional video-analysis software.

### Structure

```text
[ Address ][ Takeaway ][ Top ][ Downswing ][ Impact ][ Follow Through ]

━━━━━━━━━━━━━━━━●━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                ↑
             Impact
```

Use frame thumbnails when available.

Important moments:
- Address
- Takeaway
- Top
- Transition
- Downswing
- Impact
- Follow-through

---

# 15. Iconography

## Style

Use simple line icons.

Recommended characteristics:

- 1.5–2px stroke
- Minimal detail
- Geometric
- Consistent stroke width
- No colorful emoji-like icons

Good icon categories:

- Play
- Pause
- Camera
- Golf club
- User
- Analytics
- Video
- Settings
- Compare
- Upload
- History

Icons should support the UI rather than become decoration.

---

# 16. Photography Direction

Photography should feel authentic and editorial.

### Preferred

- Real golf courses
- Natural lighting
- Slightly cinematic compositions
- Golfers captured mid-swing
- Close-up equipment shots
- Camera/sensor setups
- Grass textures
- Driving range environments
- Professional training environments

### Avoid

- Obvious AI-generated golfers
- Perfectly symmetrical hero shots
- Generic stock-photo smiles
- Unrealistic golf poses
- Overly saturated landscapes
- Futuristic holograms
- Fake floating UI

The photography should make the product feel like it belongs in the real world.

---

# 17. Image Treatment

Recommended treatment:

```text
Natural photography
+
Slightly reduced saturation
+
Deep shadows
+
High contrast
+
Dark UI framing
+
Green data overlays
```

Do not put a giant gradient over every image.

---

# 18. Motion & Animation

Animation should communicate analysis.

### Recommended

- Smooth timeline scrubbing
- Frame-by-frame swing playback
- Subtle chart transitions
- Metric count-up when results load
- Path drawing during swing playback
- Skeleton tracking appearing progressively
- Small active-state transitions

### Avoid

- Excessive bouncing
- Parallax everywhere
- Glowing neon animations
- Constant particle effects
- Decorative loading animations

---

# 19. AI / Computer Vision Presentation

If the application uses AI/computer vision, **do not visually advertise "AI" everywhere**.

Instead, show the result.

Bad:

```text
✨ AI POWERED SWING ANALYSIS ✨
```

Better:

```text
SWING PLANE

+2.4°
Within target range
```

Or:

```text
Detected
Shoulder rotation: 91°
Hip rotation: 42°
```

The technology should feel like an instrument.

---

# 20. Overall UI Personality

The final product should communicate:

```text
PRECISION
    ↓
PERFORMANCE
    ↓
ANALYSIS
    ↓
IMPROVEMENT
```

Not:

```text
AI
+
Gradients
+
Glassmorphism
+
Generic SaaS Cards
```

---

# 21. Design Reference Keywords

When looking for visual references, use keywords such as:

- Golf performance technology
- Professional golf launch monitor
- Sports analytics UI
- Golf swing analysis software
- Performance lab interface
- Sports broadcast graphics
- Golf simulator interface
- Athletic performance dashboard
- Camera tracking software
- Computer vision sports analysis
- Professional coaching software
- Technical sports instrumentation

---

# 22. Design Philosophy

The most important rule:

> **Make the product look like a tool a serious golfer would use to improve their swing, not an AI demo.**

The interface should prioritize the **swing, measurements, comparison, and actionable feedback**.

Every visual element should answer one of these questions:

1. What happened?
2. Why did it happen?
3. How good was it?
4. What should I improve?
5. Did I improve compared with my previous swing?

If an element does not help answer one of those questions, remove it.
