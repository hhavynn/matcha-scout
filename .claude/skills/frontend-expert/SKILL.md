---
name: frontend-expert
description: Expertise in Next.js (with React 19 rules), Tailwind CSS, UI components, and Matcha Scout user-facing features.
---

# Frontend Expert Skill

This skill is designed for the Frontend Expert agent. It handles Next.js frontend development, React components, Tailwind styling, state management, and user-facing recommendation displays.

## Guidelines & Responsibilities

1. **Next.js & React 19 Rules**:
   - Follow Next.js App Router rules and convention changes. Pay attention to warnings and constraints outlined in `frontend/AGENTS.md`.
   - Ensure Server Components are used by default; use `"use client"` only when client-side state, context, or event listeners are required.
   - Guard against hydration errors by matching server-side rendering state with initial client-side state.

2. **Tailwind & CSS Styling**:
   - Build responsive grids and layouts suitable for mobile and desktop screens.
   - Use the designated design system, colors, and styling rules. Implement rich aesthetics: custom gradients, hover animations, glassmorphism, and polished typography.
   - Do not use plain raw colors; use custom color palettes matching the matcha theme (e.g., deep forest greens, creamy off-whites, and soft golden-honey accents).

3. **Page & Component Architecture**:
   - Keep page modules and components well-structured inside `frontend/components/` and routing inside `frontend/app/`.
   - Key modules include:
     - Preference Quiz: A multi-step questionnaire that guides the user to define their taste preferences.
     - Recommendations: Ranked matcha list with match percentages and visual breakdowns.
     - Drink Detail & Review Form: Displaying drink taste profiles and allowing new reviews to be submitted.
