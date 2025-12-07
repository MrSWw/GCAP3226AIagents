# Academic Poster Graph Selection Guide
## Simulation Results: 5-Graph Deep Dive (A1/A2 Poster Size)

---

## 🎯 Recommended Combination

### **Graph 1: 01_Key_Finding_272A_Congestion.png**
**Location:** Upper left section (Current Baseline Area)

**Poster Caption:**

> **Why Route 272A: High-Frequency Congestion Problem**
>
> We monitored two nearby bus stops across 19 Hong Kong routes over 96 hours (68,402 transactions). Route 272A emerged as the most frequent service, operating every 2-3 minutes during peak hours. Peak-hour data revealed 124-second average waits versus 112 seconds off-peak—a 10.7% congestion increase establishing urgency for stop consolidation.

---

### **Graph 2: 09_Wait_Distribution_Comparison.png**
**Location:** Upper middle section (Distribution Patterns)

**Poster Caption:**

> **Wait Time Distribution: Baseline vs. Merged**
>
> Baseline (left, blue) shows waits centered at 583 seconds for separate stops. Merged scenario (right, green) shifts distribution leftward to 522 seconds, benefiting most passengers. However, the longer right tail reveals some passengers face much longer waits due to route bunching.

---

### **Graph 3: 10_Percentile_Analysis.png**
**Location:** Upper right section (Percentile Breakdown)

**Poster Caption:**

> **Percentile Analysis: The Hidden Trade-offs**
>
> Percentiles 10-75 show improvements of 5-21%, meaning most passengers benefit substantially. However, 90th-95th percentiles degrade by 8.8-6.7%, harming the most vulnerable riders. This creates stark inequality: 90% of riders win while 5-10% lose, critical for vulnerable populations.

---

### **Graph 4: 11_Queue_Length_Over_Time.png**
**Location:** Lower left section (System Dynamics)

**Poster Caption:**

> **Queue Dynamics Over Time: Why Bunching Matters**
>
> Baseline (top, blue) shows stable queues around 3 passengers at separate stops. Merged (bottom, green) exhibits volatile peaks reaching 8+ passengers due to route bunching. Multiple buses arriving simultaneously create queue spikes, generating worst-case scenarios for unlucky passengers.

---

### **Graph 5 (Alternative): 12_Sensitivity_Analysis_Boarding.png**
**Location:** Lower right section (Robustness Verification)

**Poster Caption:**

> **Robustness Validation: Boarding Time Sensitivity**
>
> Sensitivity analysis tests simulation stability across realistic boarding time variations (±30% from baseline 2-3 seconds). Results show findings hold across parameter ranges with ±7% variation bounds. This confirms the merger's 10.5% efficiency gain is robust and not artifact of specific assumptions.

**When to Use:** Replace Graph 3 (Percentile Analysis) if emphasizing scientific rigor and robustness testing. Demonstrates findings remain stable even when key operational parameters vary by ±30%, proving results hold true in real-world conditions with parameter uncertainty.

---

## 📊 Why These 5 Graphs?

### ✅ **Focused on Simulation Results**
Since problem and research questions appear elsewhere on your poster, these graphs concentrate specifically on what your simulation reveals and what should be done. Graph 1 presents baseline situation and key findings together efficiently, Graph 2 shows who benefits and who loses through distribution analysis, and Graph 3 translates findings into actionable recommendations.

### ✅ **Covers All Poster Requirements**
Visual summary of key findings is demonstrated through the simulation results and percentile analysis. Key data visualizations and charts are strategically placed to support your simulation narrative. Concise recommendations for stakeholders translate data into actionable policy guidance. Since problem and research questions are handled in another section, these graphs maintain focus on quantitative findings and implications.

### ✅ **Visual Presentation Quality**
High contrast colors (red for alerts, green for improvements) make information immediately recognizable. Information density is moderate, avoiding overwhelming viewers with excessive detail. All images are 300 DPI professional quality suitable for projection and printing. Visuals remain clearly readable in both large-format printing and digital presentation contexts.

### ✅ **Academic Rigor**
The graphs present complete analysis rather than just averaging, showing the full distribution of impacts. Both benefits and risks are presented without excessive optimism about the merger. All recommendations are grounded in quantitative data and simulation results rather than speculation.

---

## 🎨 Poster Layout Configuration

```
┌─────────────────────────────────────────────┐
│  Title: Data-Driven Transit Planning Analysis│
│  Subtitle: Quantifying Efficiency, Equity,   │
│  and Accessibility in Route Merger Decisions │
└─────────────────────────────────────────────┘

[PROBLEM & RESEARCH QUESTIONS SECTION]
(Covered in separate poster section)

┌────────────┬────────────┬────────────┐
│ Graph 1:   │ Graph 2:   │ Graph 3:   │
│ Current    │ Wait       │ Percentile │
│ Baseline   │ Distribution│ Analysis  │
│ (upper)    │ (upper)    │ (upper)    │
├────────────┼────────────┴────────────┤
│ Graph 4:   │ Graph 5:                │
│ Queue      │ Robustness Check        │
│ Dynamics   │ (Sensitivity Analysis)  │
│ (lower)    │ (lower)                 │
└────────────┴────────────────────────┘
```

---

## 📋 Graph Arrangement Flexibility

### 2-Row Configuration
Place current baseline (Graph 1) top-left, followed by wait distribution (Graph 2) and percentile analysis (Graph 3) across the top row. Position queue dynamics (Graph 4) and robustness validation (Graph 5) on the bottom row. This arrangement tells the complete simulation story while maintaining good visual balance on large posters.

### Alternative: Progressive Revelation
If space permits, arrange graphs left-to-right to show progression: baseline → distribution → percentiles → dynamics → robustness. This guides viewers through your analytical process step-by-step, making the narrative flow more obvious.

### Alternative: By Impact Type
Group graphs showing efficiency impacts (1, 2, 3) on one side and system dynamics plus robustness (4, 5) on the other side. This emphasizes that you measured both outcomes and validated reliability.

---

## 📋 Alternative Combinations (if adjustments needed)

### If emphasizing "Simulation Results"
Replace Graph 3 with Graph 11 (Queue Length Dynamics) to show system behavior more intuitively and demonstrate how buses bunch at the merged stop rather than focusing on policy recommendations.

### If emphasizing "Robustness Verification"
Replace Graph 3 with Graph 12 (Boarding Time Sensitivity) to demonstrate that findings hold across realistic parameter variations and prove scientific rigor of the analysis.

### If emphasizing "Complex Trade-offs"
Replace Graph 3 with Graph 15 (Bunching Risk & Equity Matrix) to display multi-dimensional impacts and show how different scenarios compare across efficiency, reliability, and equity dimensions for policymakers.

---

## 🎯 Final Recommendation

**Use these 5 comprehensive graphs** (1, 9, 10, 11, 12) for complete simulation analysis.

This approach creates a powerful narrative arc grounded in real data. Starting with empirical baseline (Graph 1) immediately establishes credibility. Graphs 2-3 show what the simulation reveals about wait time patterns and inequalities. Graph 4 explains the mechanism causing inequitable impacts through queue dynamics. Graph 5 validates that these findings are robust and not artifacts of unrealistic assumptions. Together they demonstrate rigorous analysis that considers not just average impacts but also system behavior, edge cases, and validation. Viewers see that your conclusions are thoroughly tested and trustworthy.

---

## 📝 Poster Writing Guidelines

### Typography and Layout
Use 28-32pt bold font for section titles to ensure visibility from distance. Employ 18-22pt bold for subsection headers to create clear hierarchy. Regular text should be 12-16pt for readability. Maintain consistent contrast using deep blue for data, green for positive findings, and red for risks or concerns to guide viewer attention.

### Information Density
Keep each caption to under 80 words to prevent visual clutter while allowing explanation of baseline and findings. Use complete sentences for smooth reading flow. Emphasize numbers and percentages as they carry more impact than qualitative statements. Break text into logical paragraphs with clear spacing rather than dense blocks.

### Visual Guidance
Use consistent colors linking graphs to their captions. Highlight critical numbers in prominent boxes with contrasting colors. Maintain color consistency throughout so audiences recognize positive findings (green), negative findings (red), and neutral information (blue).

---

**Ready to design your comprehensive simulation results section?** 🚀
