# PRD: YouTube Comment Analyzer

## Goal
Help YouTube content creators understand audience sentiment and get actionable feedback from their video comments.

## Users
YouTube content creators and video producers who want to improve their content based on audience reactions.

## Core features
1. Accept a YouTube video URL and fetch the top 100 comments (by relevance/engagement)
2. Analyze comments with Claude API: overall sentiment, sentiment breakdown, strengths, areas to improve
3. Display a structured analysis report in the browser

## Out of scope for MVP
- User login or authentication
- Backend server or database
- Comparing multiple videos
- Historical tracking or saved reports
- Filtering or searching comments

## Design
- Dark, minimal tool aesthetic — feels like a developer/creator dashboard
- Clean typography, no decorative elements
- Grayscale palette with a single green/red accent for sentiment only
