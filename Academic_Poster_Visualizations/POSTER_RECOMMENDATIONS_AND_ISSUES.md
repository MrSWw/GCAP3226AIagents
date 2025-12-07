# Policy Recommendations & Potential Issues
## Based on Graph 01, 09, and 12 Analysis

---

## **Policy Recommendations**

**Graph 01 (272A Congestion) - Target High-Frequency Routes:** Route 272A operates every 2-3 minutes during peak hours with a 10.7% congestion increase, making it an ideal candidate for stop consolidation. High-frequency routes (>20 buses/hour) should be prioritized for merger implementation because more frequent service creates greater opportunities for efficiency gains through consolidation. However, the existing 10.7% baseline congestion presents a potential risk—if bunching increases peak demand at the merged stop, the consolidated location could become a bottleneck during 7-9am and 5-7pm rush hours. To mitigate this risk, staff monitors should be deployed during the first month of peak periods and queue cameras installed to track real-time congestion patterns.

**Graph 09 (Wait Distribution) - Majority Benefit with Tail Risk:** The merged scenario shifts the wait time distribution leftward from 583 seconds to 522 seconds, delivering a 61-second average reduction that benefits over 90% of passengers. This aggregate efficiency gain represents substantial time savings across the passenger population and supports implementation of the merger. However, the distribution reveals a longer right tail in the merged scenario, indicating that some passengers—specifically those arriving just after bus clusters depart due to unlucky timing—will face significantly worse waits. To address this equity concern, real-time app alerts should be deployed showing next bus arrival times and alternative route options, allowing affected passengers to make informed decisions and minimize their wait time impact.

**Graph 12 (Sensitivity Analysis) - Robustness and Real-World Validation:** Sensitivity analysis demonstrates that simulation results remain stable within ±7% across boarding time variations, providing confidence in the model's reliability. Before full rollout, a 2-week pilot should be conducted during diverse conditions (peak/off-peak, weekday/weekend, weather variations) to confirm real-world resilience matches the ±7% simulation bounds. While the simulation tested moderate variations, real-world boarding times can exceed ±30% in practice due to wheelchairs, tourists, payment issues, and other extreme events not fully captured in the model. To address this gap, contingency buffers should be included in capacity planning, with infrastructure designed to accommodate 95th percentile scenarios rather than average conditions.

---

## **Implementation Sequence**

---

### **4. Implementation Sequence**
**Phase 1:** Off-peak pilot (10am-4pm) to test under low-risk conditions

**Phase 2:** Shoulder period expansion (6-7am, 9-10am) with continuous monitoring

**Phase 3:** Full deployment only if Phase 1-2 show <5% degradation vs. simulation predictions

---

## **Anticipated Questions**

1. **"Why 272A specifically?"**
   - Highest frequency (every 2-3 min) = largest efficiency potential per Graph 01

2. **"What about passengers in the distribution tail?"**
   - Real-time alerts + alternative routes minimize impact per Graph 09 findings

3. **"How confident are results under real conditions?"**
   - ±7% robustness per Graph 12; pilot phase validates before full rollout

4. **"What if boarding times vary more than ±30%?"**
   - Contingency planning for 95th percentile scenarios + adaptive capacity

5. **"Reversibility plan?"**
   - 6-month evaluation period; automatic rollback if results deviate >10% from predictions
