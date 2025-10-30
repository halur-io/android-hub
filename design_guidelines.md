# Modern Asian Fusion Restaurant - Design Guidelines

## Design Approach: Reference-Based (Premium Hospitality)
Drawing inspiration from Airbnb's elegance, premium Asian dining websites, and Shopify's ordering UX. Focus on appetizing food photography, clean layouts, and sophisticated restraint that highlights the cuisine.

## Typography System
**Primary Font**: Playfair Display (serif) - for headings, elegant restaurant feel
**Secondary Font**: Inter (sans-serif) - for body text, menus, interface elements
**Hebrew Support**: Implement Rubik or Assistant for Hebrew RTL text

**Hierarchy**:
- Hero Headlines: text-5xl to text-7xl, font-normal
- Section Titles: text-3xl to text-4xl, font-normal
- Menu Item Names: text-xl to text-2xl, font-medium
- Body Text: text-base to text-lg
- Prices: text-lg to text-xl, font-semibold
- Interface Labels: text-sm, font-medium

## Layout System
**Spacing Primitives**: Tailwind units 4, 6, 8, 12, 16, 24
- Component padding: p-4 to p-8
- Section spacing: py-16 to py-24
- Grid gaps: gap-6 to gap-8

**Container Strategy**:
- Full-width hero: w-full
- Content sections: max-w-7xl mx-auto
- Menu grid: max-w-6xl
- Forms: max-w-2xl

## Core Components

### Navigation
Fixed header with blur backdrop (bg-white/80 backdrop-blur-md)
**Elements**: Restaurant logo (right for RTL), branch selector dropdown, language toggle (HE/EN), menu links, cart icon with badge count, mobile hamburger
**Mobile**: Collapsible drawer from right (RTL), full-screen overlay

### Hero Section
Full-viewport video background (16:9 landscape food preparation footage)
**Overlay**: Dark gradient overlay (bg-black/40) for text readability
**Content**: Centered layout with restaurant name in Playfair, tagline, dual CTAs (Order Now + View Menu) with blurred button backgrounds (bg-white/20 backdrop-blur-sm)
**Height**: h-screen on desktop, h-[70vh] on mobile

### Menu Display System
**Layout**: 3-column grid desktop (lg:grid-cols-3), 2-column tablet (md:grid-cols-2), single mobile
**Menu Cards**: White background, rounded-2xl, overflow-hidden, hover lift effect (subtle)
**Card Structure**: Food image top (aspect-ratio 4:3), content padding p-6, item name, Hebrew/English description, dietary icons row (flex gap-2), price in ₪, Add to Cart button
**Filtering**: Sticky category tabs below hero (Sushi, Ramen, Appetizers, Drinks), smooth scroll to sections
**Dietary Icons**: 32x32 circle badges (vegetarian, vegan, gluten-free, spicy levels)

### Shopping Cart Drawer
Slide-in panel from left (RTL consideration), fixed overlay
**Structure**: Header with close button, scrollable items list, each item shows thumbnail, name, quantity controls (+/-), price, subtotal, sticky footer with total and Checkout button
**Empty State**: Icon + "Your cart is empty" message + Browse Menu CTA

### Photo Gallery
**Layout**: Masonry grid (3 columns desktop, 2 tablet, 1 mobile) using CSS grid auto-flow
**Images**: Restaurant interior, chef preparing dishes, signature dishes, ambiance shots
**Interaction**: Click opens lightbox modal with navigation arrows

### Branch Selection
Floating pill selector (fixed position top-right below nav), shows current branch
**Dropdown**: Card with branch names, addresses, phone numbers, "Get Directions" links
**Icons**: Map pin icons for visual clarity

### Contact Section
**Layout**: 2-column split (lg:grid-cols-2)
**Left**: Contact form (name, phone, email, message textarea, submit button)
**Right**: Branch cards stacked - each shows branch name, address, phone, operating hours, embedded map thumbnail
**Mobile**: Stacks to single column

### Footer
**Multi-column**: Logo + tagline | Quick Links | Branch Info | Social + Newsletter
**Elements**: Payment icons, certifications, social media icons, copyright
**Spacing**: py-12, generous padding

## RTL Implementation
**Direction Switching**: Apply `dir="rtl"` to `<html>` for Hebrew, swap to `dir="ltr"` for English
**Flexbox**: Use `flex-row-reverse` for RTL layouts
**Text Alignment**: `text-right` for Hebrew, `text-left` for English
**Padding/Margin**: Use logical properties (ps, pe instead of pl, pr) or swap in RTL
**Icons**: Mirror directional icons (arrows, chevrons) for RTL

## Mobile-First Responsive Strategy
**Breakpoints**: Design mobile base, then md (768px), lg (1024px), xl (1280px)
**Touch Targets**: Minimum 44x44px for buttons
**Forms**: Full-width inputs on mobile, stacked labels
**Navigation**: Hamburger menu, full-screen drawer
**Menu Grid**: Single column mobile, stack all content
**Hero Video**: Shorter height on mobile (70vh), optimized video source
**Cart**: Full-screen modal on mobile vs drawer on desktop

## Animation Guidelines
**Principle**: Subtle, purposeful animations only
**Allowed**: 
- Menu card hover lift (translate-y-1, duration-300)
- Button hover states (opacity-90)
- Cart drawer slide-in (transition-transform)
- Smooth scroll for navigation
- Lightbox fade-in
**Forbidden**: Parallax effects, excessive scroll animations, auto-playing carousels

## Images Strategy
**Hero**: High-quality video (sushi preparation, chef plating, fresh ingredients), 30-60 second loop
**Menu Items**: Professional food photography, consistent lighting, white/minimal backgrounds, aspect-ratio 4:3
**Gallery**: Mix of dish close-ups (8-12 images), restaurant interior wide shots (4-6 images), chef portraits (2-3 images), atmospheric dining scenes (4-6 images)
**Optimization**: WebP format, lazy loading, multiple sizes for responsive

## Functional Elements
**Dietary Icons**: Use Font Awesome for leaf (vegan), wheat-slash (GF), fire (spicy), fish (pescatarian)
**Price Display**: Always show ₪ symbol, format: "₪48" or "₪120"
**Language Toggle**: Flag icons or HE/EN text toggle, prominent in header
**Cart Badge**: Red notification dot with count, updates on add/remove
**Form Validation**: Inline error states, success confirmation modal

## Special Considerations
**Kosher Certification**: Badge display if applicable, footer trust indicators
**Delivery Integration**: If using third-party, clear CTAs to delivery platforms
**Reservation System**: If booking enabled, modal form or separate page link
**Loading States**: Skeleton screens for menu loading, spinner for cart operations
**Error Handling**: Friendly Hebrew/English error messages, retry options