# Presentation Content Outline: Adaptive Histogram Equalization in Constant Time

This document outlines the structure and content of the presentation defined in `ahe_presentation.html`.

## Slide 0: Title Slide
- **Title:** Adaptive Histogram Equalization in Constant Time - Presentation
- **Authors:** Philipp Härtinger & Carsten Steger
- **Journal:** Journal of Real-Time Image Processing (2024) 21:93

## Slide 1: Why This Paper Matters
- Introduction to the significance of the paper (AHE/CLAHE optimization).
- **The Problem:** AHE/CLAHE is computationally expensive for large filter radii.
- **The Solution:** O(1) complexity with respect to filter radius — first exact constant-time algorithm.

## Slide 2: The Problem with Dark Photos
- Illustrates the issue with unevenly illuminated images (e.g., dark photos) that require enhancement.
- Shows example of histogram equalization improving overall contrast but potentially overenhancing some regions.

## Slide 3: Global vs Local Enhancement
- Comparison between Global Histogram Equalization (HE) and Adaptive Histogram Equalization (AHE).
- Highlights that local enhancement (AHE) is better for preserving details but is computationally expensive.

## Slide 4: The Computational Bottleneck
- Explains why AHE is slow.
- **AHE Pipeline:** For each pixel → Compute Local Histogram (BOTTLENECK) → Compute Transfer Function → Output Pixel
- **Notation:** Image, filter radius r, histogram bins L=256
- **Numbers:** Shows how window size explodes as radius r increases (e.g., 361,201 pixels for r=300).

## Slide 5: Sliding-window Histogram Computation
- Introduces the concept of optimization via sliding windows (inspired by median filtering).
- **Comparison Table:**
    - Naive: $O(r^2)$
    - Huang et al.: $O(r)$
    - Zig-zag (Kong): $O(r)$
    - Perreault-Hébert: $O(1)$

## Slide 6: Naive O(r²) vs Huang O(r)
- **Naive Method:** Recomputes the full histogram for every pixel.
- **Huang's Method:** Uses an incremental update (remove left column, add right column) as the window slides.
- **Interactive Demo:** Allows comparing Naive and Huang methods with a visual grid and histogram.

## Slide 7: The Revolutionary Insight: Column Histograms
- **Key Insight:** Updating *entire columns* at once instead of individual pixels.
- **Definition:** Column Histogram $h_c$ and Kernel Histogram $H$.
- **Equation (4):** $H_{i,j} = \sum_{c=j-r}^{j+r} h_c$
- **Interactive Demo:** Step-by-step column update logic (removing $h_{left}$, adding $h_{right}$).

## Slide 8: The O(1) Update Rule
- Explains the vector update operation: $H_{new} = H_{old} - h_{remove} + h_{add}$.
- Shows this is constant time relative to the window size r.
- **Cost:** $L$ subtractions + $L$ additions = $2L = 512$ operations (constant!).
- **Interactive Demo:** Vector operation visualization.

## Slide 9: Why It's O(1): Complete Analysis
- **Per-Pixel Cost:** Breakdown showing $2L$ operations (vector add/sub) + amortized column update.
- **Complexity Comparison Table:** Compares operation counts for Naive, Huang, and Perreault methods at different radii ($r$).
- **Theoretical vs. Practical Crossover:** Theory says $r>128$, but in practice (due to SIMD/Cache), it wins at $r \approx 9$.
- **Why Faster Than Theory:** SIMD, Cache-Friendly, No Branches.

## Slide 10: Interactive: Processing Time Race
- **Demo:** A simulation racing the three methods (Naive, Huang, Perreault) to process 1M pixels.
- User can adjust the filter radius $r$ to see how it affects the speed of each method.

## Slide 11: Section 3.3: Transfer Function Optimization
- Discusses optimizing the calculation of the cumulative distribution function (CDF) for the transfer function.
- **Split-Sum Optimization (Equation 7):** Computing the sum from the closer end ($0$ or $L-1$) to halve the operations.
- Enables multilevel histogram optimization (26-32% speedup).

## Slide 12: Section 3.4: CLAHE Optimization
- **CLAHE:** Contrast Limited Adaptive Histogram Equalization.
- Explains the need for clipping histograms to prevent noise amplification in uniform regions.
- Shows "Before Clipping" vs "After Clipping" histograms.
- **Algorithm 3: Implicit Clipping** — Compute clipped cumulative $\hat{C}(g)$ directly in one pass!
- **Key Insight:** Naive CLAHE requires 3 passes; implicit approach does it in 1 pass.
- **Speedup:** 8.6–14.5% vs naive CLAHE.

## Slide 13: Section 3.5: Multilevel Histograms (NEW)
- **Key Optimization:** Maintain two histograms at different granularities.
- **Two-Level Structure:**
    - Fine Histogram (256 bins): counts each gray value
    - Coarse Histogram (8 or 16 bins): sums of consecutive fine bins
- **Faster Cumulative Sum:** ~24 ops instead of up to 255.
- **Trade-offs:**
    - Works well for: AHE (always), CLAHE with high clip limit (α ≥ 0.1), smooth images
    - Problematic for: CLAHE with low clip limit (α < 0.1) — up to −47% slowdown!
- **Future Work:** Finding better criterion for when to update fine segments.

## Slide 14: Recommended Configurations
- **AHE:** 8-bin Multilevel → +26-32% speedup
- **CLAHE (Mild, α ≥ 0.1):** 8-bin + Implicit → +26-36% speedup
- **CLAHE (Aggressive, α < 0.1):** Implicit Only → +8-9% speedup (avoid multilevel!)
- **Correctness:** SAD = 0 for all variants (bit-identical output).

## Slide 15: Section 4: Experimental Setup (NEW)
- **Dataset:** 25 grayscale images from MVTec HALCON library (1000×1000 pixels)
- **Test Configuration:**
    - CPU: Intel Core i9-10900X
    - Single-threaded execution
    - Language: C (optimized)
    - Warm-up: 3 runs before timing
    - Measurement: Average of 10 runs
    - Filter radii: r ∈ {1, 2, ..., 300}
- **Correctness Verification:** SAD = 0 (all methods produce bit-identical output)
- **What's Measured:** Sliding-window methods, transfer function optimizations, CLAHE variants.

## Slide 16: Experimental Results (Tables 1 & 2) (ENHANCED)
- **Table 1: AHE Sliding-Window Methods (ms)**
    - Naive O(r²): ~1000ms at r=22, >60,000ms at r=300
    - Huang O(r): ~100ms at r=22, ~850ms at r=300
    - Zig-zag O(r): ~95ms at r=22, ~780ms at r=300
    - **Ours O(1): ~45ms constant regardless of radius**
    - Key: O(1) method is ~94% faster than O(r) at r=300
- **Table 2: Transfer Function Optimizations (ms)**
    - AHE Baseline: 40.4–47.8ms
    - + Split-sum: 0.6–1.5% speedup
    - + Multilevel (16-bin): 17–30% speedup
    - **+ Multilevel (8-bin): 26–32% speedup** (best)
- **Summary: Best Configuration**
    - AHE: 27–35 ms
    - CLAHE (α ≥ 0.1): 44–56 ms
    - CLAHE (α < 0.1): 60–75 ms

## Slide 17: Key Takeaways
- **Core Contribution:** Think in histogram vectors, not pixels!
    - Kernel H = sum of column histograms h_c
    - Update: $H_{new} = H_{old} - h_{left} + h_{right}$
    - Cost: $2L = 512$ ops (constant w.r.t. r)
- **Performance Summary:**
    - Speedup at r=300: 20× vs Huang
    - Practical crossover: r ≈ 9
    - Memory overhead: O(N·L) ≈ 256KB
    - Accuracy loss: None (exact)
- **Why It Works:** SIMD-friendly, Cache-efficient, Branch-free
- **Practical Guidelines:**
    - Use 8-bin multilevel for AHE
    - Use implicit clipping for CLAHE
    - Avoid multilevel with aggressive clipping (α < 0.1)
- **Bottom Line:** First exact O(1) AHE/CLAHE algorithm — enables real-time processing even with large filter radii!

## Slide 18: Thank You!
- Closing slide with references.
- **Reference:** Härtinger, M., & Steger, C. (2024). Adaptive histogram equalization in constant time. Journal of Real-Time Image Processing, 21:93.
