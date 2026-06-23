---
name: ai-integration
description: Expertise in LLM prompt engineering, Gemini API structured outputs, and taste profile parsing.
---

# AI Integration Expert Skill

This skill is designed for the AI Integration agent. It handles prompt engineering, structured review parsing, confidence score calculations, and fallback parser systems.

## Guidelines & Responsibilities

1. **Gemini API Integration**:
   - Implement natural-language review parsing using Gemini structured JSON outputs.
   - Map review texts into the five taste dimensions: Sweet, Creamy, Mellow, Earthy, Strong.
   - Maintain configuration flags to toggle between real Gemini API calls and the fallback mock parser for safe/offline development.

2. **Taste Profiles & Confidence Scoring**:
   - Compute aggregate taste profiles for drinks using community reviews.
   - Calculate confidence scores and labels (Unrated, Low, Medium, High) based on the number and consistency of review data.
   - Never rely on Yelp ratings for Matcha Scout taste profiles or confidence scores.
