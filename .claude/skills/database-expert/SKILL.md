---
name: database-expert
description: Expertise in PostgreSQL schema design, Neon serverless Postgres features, migrations, and DynamoDB compatibility.
---

# Database Expert Skill

This skill is designed for the Database Expert agent. It handles PostgreSQL database administration, SQL schemas, migrations, query optimization, and Neon serverless features like branching.

## Guidelines & Responsibilities

1. **PostgreSQL Schema & Migrations**:
   - Maintain SQL schema scripts and migration files under `backend/migrations/`.
   - Create tables, constraints, indexes, and primary/foreign keys properly to support cafe, drink, review, and taste profile models.
   - Ensure migrations are reproducible and run safely.

2. **Neon Integration & Branch-First Workflows**:
   - Work with Neon Serverless Postgres features including branching, autoscaling, and connection pooling.
   - Review Neon integration instructions as described in the `neon-postgres` skill.
   - Ensure the application properly handles the connection string via `DATABASE_URL` environment variables.

3. **DynamoDB Compatibility Layer**:
   - Maintain the temporary JSONB compatibility layer that allows backend legacy DynamoDB access patterns to query PostgreSQL.
   - Work toward cleaning and migrating models to pure relational tables where appropriate.
