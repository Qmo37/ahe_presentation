# Presentation Content Outline: Adaptive Histogram Equalization in Constant Time

This document outlines the structure and content of the presentation defined in `ahe_presentation.html`.

## Slide 0: Title Slide
- **Title:** Adaptive Histogram Equalization in Constant Time - Presentation

## Slide 1: Why This Paper Matters
- Introduction to the significance of the paper (AHE/CLAHE optimization).

## Slide 2: The Problem with Dark Photos
- Illustrates the issue with unevenly illuminated images (e.g., dark photos) that require enhancement.

## Slide 3: Global vs Local Enhancement
- Comparison between Global Histogram Equalization (GHE) and Adaptive Histogram Equalization (AHE).
- Highlights that local enhancement (AHE) is better for preserving details but is computationally expensive.

## Slide 4: The Computational Bottleneck
- Explains why AHE is slow.
- **Metric:** The cost is proportional to the window size ($r^2$), leading to a bottleneck.
- **Numbers:** Shows how operations explode as radius $r$ increases (e.g., $361,201$ pixels for $r=300$).

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
- **Interactive Demo:** "Slide 05" (internal ID) showing the step-by-step column update logic (removing $h_{left}$, adding $h_{right}$).

## Slide 8: The O(1) Update Rule
- Explains the vector update operation: $H_{new} = H_{old} - h_{remove} + h_{add}$.
- Shows this is constant time relative to the window size $r$.

## Slide 9: Why It's O(1): Complete Analysis
- **Per-Pixel Cost:** Breakdown showing $2L$ operations (vector add/sub) + amortized column update.
- **Complexity Comparison Table:** Compares operation counts for Naive, Huang, and Perreault methods at different radii ($r$).
- **Theoretical vs. Practical Crossover:** Theory says $r>128$, but in practice (due to SIMD/Cache), it wins at $r \approx 9$.

## Slide 10: Interactive: Processing Time Race
- **Demo:** A simulation racing the three methods (Naive, Huang, Perreault) to process 1M pixels.
- User can adjust the filter radius $r$ to see how it affects the speed of each method.

## Slide 11: Section 3.3: Transfer Function Optimization
- Discusses optimizing the calculation of the cumulative distribution function (CDF) for the transfer function.
- **Split-Sum Optimization:** Computing the sum from the closer end ($0$ or $L-1$) to halve the operations.

## Slide 12: Section 3.4: CLAHE Optimization
- **CLAHE:** Contrast Limited Adaptive Histogram Equalization.
- Explains the need for clipping histograms to prevent noise amplification in uniform regions.
- Shows "Before Clipping" vs "After Clipping" histograms.

## Slide 13: Recommended Configurations
- (Inferred Content) Likely discusses optimal parameters for the algorithm based on the paper's findings.

## Slide 14: Experimental Results
- (Inferred Content) Presentations of benchmarks, speedup graphs, and image quality comparisons.

## Slide 15: Key Takeaways
- Summary of the main points:
    - Column histograms allow $O(1)$ updates.
    - SIMD provides a massive practical speedup.
    - Optimization applies to CLAHE as well.

## Slide 16: Thank You!
- Closing slide.


# Q&A: Why Can't Other Methods Apply SIMD?

Great question! This is the key reason why Perreault's method achieves such dramatic real-world speedups. Here's why SIMD works for Perreault but not really for Naive/Huang:

## Why SIMD Works for Perreault But Not Others

### Perreault's Method: Perfect for SIMD ✅

The core operation is **vector addition/subtraction**:

```
H_new = H_old - h_left + h_right
```

This means:
- **256 independent additions** (one per histogram bin)
- **All bins processed identically** (same operation, no conditionals)
- **Contiguous memory access** (histogram arrays are stored sequentially)

With **AVX2**, you can process **8 bins per instruction** (256 bits / 32 bits per bin). With **AVX-512**, that's **16 bins per instruction**!

---

### Naive Method: Can't Vectorize ❌

The core operation is **counting pixels**:

```
for each pixel in (2r+1)×(2r+1) window:
    histogram[pixel_value]++
```

**Problems:**
- **Random memory access**: Each pixel has a different intensity (0-255), so you're accessing random histogram bins
- **Data dependencies**: You can't parallelize `histogram[x]++` because multiple pixels might have the same value (race condition)
- **Scattered writes**: SIMD requires writing to contiguous memory, not scattered locations

---

### Huang's Method: Limited SIMD Benefit ⚠️

The core operation is **adding/removing one column of pixels**:

```
for each pixel in column (2r+1 pixels):
    histogram[pixel_value]++  or  histogram[pixel_value]--
```

**Same problems as Naive:**
- **Random bin access**: Each pixel maps to a different histogram bin
- **Scatter/gather operations**: You're updating random locations, not contiguous memory
- **Data-dependent indexing**: `pixel_value` determines which bin to update

While modern CPUs have scatter/gather SIMD instructions, they're **much slower** than the contiguous vector operations Perreault uses.

---

## Summary Table

| Method     | Operation                | Memory Pattern     | SIMD Benefit |
|------------|--------------------------|-------------------|--------------|
| Naive      | Count each pixel         | Scattered writes  | ❌ None      |
| Huang      | Add/remove column pixels | Scattered writes  | ⚠️ Minimal   |
| Perreault  | Vector add/subtract      | Contiguous        | ✅ 8-16×     |

---

## Key Insight

This is why the **theoretical crossover** ($r=128$) becomes **practical at $r≈9$** — Perreault gets an **8× SIMD multiplier** that the other methods can't match!