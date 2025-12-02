# Human-AI Collaboration Report
**Course**: GCAP3226 - Empowering Citizens Through Data: Participatory Policy Analysis for Hong Kong  
**Student Name**: [Your Name]  
**Date**: December 1, 2025  
**Word Count Target**: 1,000 words

---

## 1. Executive Summary

This project evolved from tentative prompting into a disciplined human–AI partnership. I used GitHub Copilot for implementation and Poe for rapid visualization feedback, while I provided the policy framing, constraints, and validation that grounded the work in reality. The core question was practical and local: should two closely spaced bus stops in Hong Kong be merged to reduce congestion and improve service efficiency? AI helped me collect and process large volumes of ETA snapshots, compare inter-stop travel times, and prototype simulation scenarios. I contributed field observations, route context, and stakeholder considerations, then verified outputs with spot checks and cross-comparisons. The headline insight was concrete: route 272A’s median inter-stop travel time rose about 10.7% in the morning peak versus mid-morning, quantifying congestion I had seen on site. The larger lesson is that high-quality results emerge when human judgment and verification combine with AI’s speed and breadth—accelerating analysis without compromising rigor.

## 2. AI Usage Overview

My workflow shifted from “ask for code” to “co-design methods.” I specified schemas, pairing logic, time-window definitions, and output formats; Copilot implemented, I validated on samples, then we iterated. In monitoring, Copilot helped build a time-window collector with correct Asia/Hong_Kong timezone handling and resilient error checks. In analysis, it produced inter-stop metrics by pairing ETA records across two stops with keys like (snapshot_ts, route, eta_seq), and exported reproducible CSV and Markdown outputs for each run. When anomalies appeared—negative travel seconds or off-peak contamination by deep-night data—I asked for filters and redefined daytime windows so comparisons reflected realistic traffic conditions.

For communication, Poe supported quick visual ideation: animations showing bus movement, bunching, and peak vs off-peak differences helped non-technical viewers grasp the patterns. Across the lifecycle, Copilot excelled at scaffolding code and accelerating iteration, while I kept analyses aligned with policy relevance through targeted prompts and reality checks. A representative iteration: early results mixed midnight data, making off-peak artificially fast. I guided redefinition of off-peak to mid-morning and requested a “Congestion Impact” percentage metric. That change produced interpretable, decision-ready outputs without changing the core algorithm, demonstrating the value of human framing over mere code generation.

## 3. Chat History Portfolio

My collaboration centered on analyzing whether two bus stops (St. Martin Road and Chong San Road, 200 meters apart) should be merged. In early November, I asked: "Can we write code to run monitoring for peak hour tomorrow on 24/11 6:30 to 8:30 HKT?" AI generated `run_monitor_window.py` handling timezone conversions. However, earlier errors mixing naive and timezone-aware datetime objects caused crashes at wrong wall-clock times. I learned Python's `zoneinfo` library through necessity-driven debugging, validating timestamps matched Hong Kong time and adding error handling for fieldwork connections.

After collecting 96 hours of data, I asked AI to quantify congestion by comparing inter-stop travel times. AI created `interstop_eta_compare.py` pairing ETA records and calculating travel_seconds = eta_stop2 - eta_stop1. The first run showed impossible negative times. Through three iterations, I refined: filtering negatives, excluding deep-night contamination, adding percentage metrics. Key finding: Route 272A showed 10.7% increased travel time during peak (112s → 124s median), quantifying congestion I had physically observed.

The most sophisticated collaboration involved policy scenario simulation. I asked AI to build discrete-event simulations comparing baseline versus post-merge scenarios using SimPy. AI generated the framework, but I provided crucial domain knowledge: Hong Kong buses accommodate 70 passengers, boarding takes 2-3 seconds including Octopus taps, berth capacity is 2 per stop. When initial simulations produced unrealistic uniform wait times, I diagnosed passenger arrival rates must vary by scenario—merged stops would concentrate demand. Through refinement, we created simulations showing baseline waits of 250-1,100 seconds, with merging producing 8-12% reductions but increased 90th percentile waits due to bunching. I validated by comparing simulated waits against empirical data (within 15% agreement) and testing sensitivity to boarding assumptions. For visualization, I used Poe briefly to create animated bus graphics for non-technical stakeholders.

Failed attempts taught lessons: vaguely asking "What's the best way to analyze congestion?" produced generic reviews ignoring Hong Kong context. When AI's timezone fix technically worked but produced wrong times, I learned syntactically correct code can be logically flawed—validation against expected behavior is essential.

## 4. Reflection on Human-AI Collaboration

Human inputs were decisive. I contributed local context from site visits (walking the 200‑meter corridor; observing passenger flows), translated “should we merge the stops?” into decision‑ready metrics (peak uplift, percentile shifts), and steered the analysis toward stakeholder concerns like accessibility and convenience. Collaboration became joint problem decomposition: operationalizing congestion; pairing ETA records reliably; selecting time windows that reflected lived traffic; and handling edge cases (skip‑stops, nulls, stale API entries). The anchor was validation. I ran manual spot checks, cross‑validated in Excel, reviewed distributions when filtering negatives to avoid throwing out legitimate near‑zero values, and favored medians for heavy‑tailed travel‑time data per transportation literature. I also ran sensitivity tests—e.g., varying boarding seconds in simulations—to ensure conclusions were robust to plausible operational changes.

Debugging timezone issues forced deeper understanding of Python’s offset‑aware datetime and why naive vs aware comparisons fail. That episode exemplified the learning dynamic: AI accelerates, but only when paired with human conceptual control. I openly disclosed AI assistance and ensured I could explain and reproduce each step without AI—code, assumptions, and conclusions. When AI’s initial choices were reasonable but misaligned with context (e.g., including deep night as off‑peak), I intervened to redefine windows and add congestion metrics that mattered to decision makers. When visualization ideas were promising but vague, I specified the storytelling goal (“make bunching visible”), then iterated until plots served non‑technical audiences.

Most importantly, I recognized AI’s limits. It doesn’t conduct fieldwork, weigh stakeholder trade‑offs, or arbitrate values. It can be syntactically correct yet logically off, producing plausible but wrong outputs without a reality check. My role was stewardship: set constraints, provide context, test assumptions, and decide what evidence is compelling enough for policy discussion. In that mode—AI as augmentation, not substitution—the collaboration produced faster, better analysis while maintaining integrity and local relevance.

## 5. Learning Outcomes and Transferable Skills

I gained transferable capabilities that extend beyond this project. Technically, I built reproducible Python pipelines, integrated public APIs, and translated problem statements into tested algorithms, then validated with samples and cross‑checks. Methodologically, I learned prompt engineering and collaborative reasoning: specify schemas and constraints, anticipate edge cases, and request outputs that are directly decision‑ready. Communication‑wise, I improved translation between technical findings and stakeholder narratives, using animations and succinct markdown summaries to make results legible.

AI increased ambition within limited time, while validation deepened conceptual grasp—producing both breadth and depth. I can carry these skills into government, NGO, or private contexts: lead with human judgment and ethics, use AI as a powerful amplifier, and preserve transparency about assumptions and limitations. I also recognize hard limits: AI can’t do fieldwork, often lacks local nuance, and can’t make value judgments about trade‑offs. My approach is to embed human stewardship—set the frame, verify the logic, and ensure the outputs remain accountable to real‑world constraints.

---

**Note**: Word count applies to sections 1, 2, 4, and 5 only; Section 3 (Chat History Portfolio) is excluded.
