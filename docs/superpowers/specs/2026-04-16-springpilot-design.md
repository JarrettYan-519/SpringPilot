# SpringPilot - Design Spec

## Project Overview

**Name**: SpringPilot (春招领航)

**Description**: A local web application that uses AI to manage the full spring recruitment lifecycle (application tracking, study planning, mock interviews) while simultaneously tracking fitness and weight loss progress (weight, diet, training), with intelligent parsing of trainer-provided training plan documents.

**Target User**: 闫迦淼, a developer preparing for spring recruitment while pursuing a fitness/weight loss goal.

## Architecture

```
┌─────────────────────────────────────────────┐
│              Vue 3 Frontend (SPA)           │
│  ┌──────────┐ ┌──────────┐ ┌──────────────┐ │
│  │ Job Mod  │ │ Fit Mod  │ │ Doc Center   │ │
│  └─────┬────┘ └─────┬────┘ └──────┬───────┘ │
└────────┼────────────┼─────────────┼─────────┘
         │            │             │
┌────────┴────────────┴─────────────┴─────────┐
│            FastAPI Backend                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────────┐ │
│  │ App/Task │ │ Train/   │ │ MinerU Parse │ │
│  │ CRUD API │ │ Diet API │ │ API          │ │
│  └──────────┘ └──────────┘ └──────────────┘ │
│  ┌──────────────────────────────────────────┐│
│  │        LangChain AI Engine               ││
│  │  (Multi-model: GLM/DeepSeek/Claude/     ││
│  │   OpenAI)                                ││
│  │  - JD analysis & resume matching         ││
│  │  - Mock interviews & question generation ││
│  │  - Diet/training suggestions             ││
│  │  - Document intelligent analysis         ││
│  └──────────────────────────────────────────┘│
└────────┬───────────────────────┬─────────────┘
         │                       │
┌────────┴───────┐   ┌──────────┴──────────┐
│    SQLite      │   │  Local File Storage  │
│  (structured)  │   │ (PDF/DOCX/MD/images)│
└────────────────┘   └─────────────────────┘
```

## Tech Stack

| Layer | Technology | Notes |
|---|---|---|
| Frontend | Vue 3 + Vite + Chart.js | Responsive SPA, chart visualization |
| Backend | FastAPI | Async API, auto-generated docs |
| AI | LangChain | Multi-model routing, supports 4 LLM providers |
| Document Parsing | MinerU API | PDF/DOCX -> Markdown conversion |
| Database | SQLite | Lightweight local storage |
| File Storage | Local filesystem | Raw uploaded documents |

## Module 1: Job Management

### 1.1 Application Tracking

- Record each application: company name, position, date, channel, status
- Statuses: Pending / Applied / Written Test / Interviewing / Offer / Rejected
- Status change timeline for each application, tracking every status transition
- List page with filtering by status and date

### 1.2 Study Planning

- Daily/weekly task board: LeetCode practice, interview prep, project learning, etc.
- Tasks support tags (e.g., "algorithm", "system design", "Python")
- Completion status tracking, progress statistics

### 1.3 AI Assistance (LangChain-powered)

- **JD Analysis**: Paste a job description, AI extracts key skill requirements, matches against user's resume, provides gap analysis and improvement suggestions
- **Interview Question Generation**: Generate targeted interview questions (technical + HR) based on target position and resume
- **Mock Interview**: Chat-style interface where AI plays the interviewer, asks follow-up questions based on answers, and provides feedback

## Module 2: Fitness Management

### 2.1 Data Recording

- **Weight Tracking**: Daily weight recording, automatic trend calculation
- **Diet Log**: Record each meal content, support manual calorie input or AI estimation from description
- **Training Check-in**: Record training type (strength/cardio/stretching), duration, content, mark completion status

### 2.2 Data Analysis

- Weight change line chart
- Daily/weekly calorie intake trend
- Training frequency statistics
- Automatic TDEE and calorie deficit calculation

### 2.3 Document Import & AI Analysis

- Upload trainer-provided PDF/DOCX/MD training plans and diet plans
- MinerU parses documents to Markdown -> LangChain extracts structured content (exercises, sets, reps, diet recommendations, etc.)
- AI automatically integrates parsed plans into user's training/diet schedule
- AI provides personalized adjustment suggestions based on recent body data + trainer plans

## Module 3: Dashboard & Settings

### 3.1 LLM Multi-model Configuration

- Settings page to select model provider (GLM / DeepSeek / Claude / OpenAI)
- Independent API Key and Base URL per provider (compatible with third-party proxies)
- Different models can be assigned to different scenarios (e.g., DeepSeek for daily analysis, Claude for mock interviews)

### 3.2 Dashboard Home

- Job overview: weekly application count, interview schedule, pending tasks
- Fitness overview: weekly training count, weight trend, calorie intake summary
- AI daily advice: comprehensive daily suggestions for both job prep and fitness based on user data

### 3.3 User Settings

- Personal info (height, weight, target weight, etc.)
- API Key management (each LLM provider + MinerU)
- Data export (JSON/CSV backup)

## Data Model (Core Entities)

### Job Module

- **Application**: id, company, position, description, channel, status, created_at, updated_at
- **ApplicationStatusLog**: id, application_id, old_status, new_status, note, created_at
- **StudyTask**: id, title, description, tags, due_date, completed, created_at
- **InterviewQuestion**: id, application_id, question, answer, feedback, source_type, created_at

### Fitness Module

- **WeightRecord**: id, weight_kg, recorded_at, note
- **DietLog**: id, meal_type, content, calories, recorded_at
- **TrainingLog**: id, training_type, content, duration_minutes, completed, recorded_at
- **TrainerPlan**: id, title, file_path, parsed_content, plan_date_range, created_at

### System

- **UserConfig**: id, key, value (stores height, target weight, API keys, model preferences, etc.)

## Future Extension (Out of Scope)

- **SpringPilot Sense**: A magnetic IMU motion sensor hardware project for tracking exercise movements (running speed/laps/distance, barbell trajectory/rep counting). This is a separate project to be started after spring recruitment. The current fitness module's data interfaces will be designed to accommodate hardware data input in the future.
