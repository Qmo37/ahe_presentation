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