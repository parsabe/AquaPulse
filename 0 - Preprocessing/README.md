<h1>The Multi-Scale Retinex with Color Restoration (MSRCR) Method</h1>
<p>The MSRCR algorithm is a powerful image processing technique designed to mimic human vision's lightness and color constancy[cite: 5, 14, 15]. The primary utility of a lightness-color constancy algorithm for machine vision is the simultaneous accomplishment of three goals: dynamic range compression, color independence from the spectral distribution of the scene illuminant, and color and lightness rendition[cite: 61, 62, 63].</p>

<h2>1. Multi-Scale Retinex (MSR) Formula</h2>
<p>The MSR formula mathematically separates the illumination from the reflectance. The authors found that the placement of the logarithmic function is important and produces best results when placed after the surround formation[cite: 9, 199]. Furthermore, various functional forms for the retinex surround were evaluated, and a Gaussian form was found to perform better than the inverse square suggested by Land[cite: 11, 216]. Because choosing a single scale forces a trade-off between dynamic range compression and color rendition, a multiscale approach helps balance these complementary visual aspects[cite: 227, 228, 493].</p>

<p>$$ R_{MSR_i}(x,y) = \sum_{n=1}^{N} w_n (\log I_i(x,y) - \log(F_n(x,y) * I_i(x,y))) $$</p>

<p><strong>Notations:</strong></p>
<ul>
    <li>$R_{MSR_i}(x,y)$: The associated retinex output for the $i$th spectral band.</li>
    <li>$I_i(x,y)$: The image distribution in the $i$th color spectral band.</li>
    <li>$N$: The number of scales.</li>
    <li>$w_n$: The weight associated with each scale $n$.</li>
    <li>$F_n(x,y)$: The surround function at scale $n$.</li>
    <li>$*$: Denotes the convolution operation.</li>
</ul>

<hr>

<h2>2. Color Restoration (CR) Function</h2>
<p>While MSR improves contrast and color constancy, it can suffer from "graying" in large uniform zones or global violations of the gray world assumption, which result in a global "graying out" of the image[cite: 85]. The Color Restoration function acts as an adjustment to prevent this. Unlike previous results, the authors found best rendition for a "canonical" gain/offset applied after the retinex operation[cite: 10, 308]. This function ensures the color relationships between the spectral bands remain intact.</p>

<p>$$ C_i(x,y) = \log(\alpha \cdot I'_i(x,y)) - \log\left(\sum_{j=1}^{3} I'_j(x,y)\right) $$</p>

<p><strong>Notations:</strong></p>
<ul>
    <li>$C_i(x,y)$: The color restoration factor for the $i$th spectral band.</li>
    <li>$\alpha$: A constant used to control the strength of the color restoration.</li>
    <li>$I'_i(x,y)$: The $i$th spectral band image adjusted by a gain/offset.</li>
    <li>$j$: The index for the three spectral bands (typically Red, Green, and Blue).</li>
</ul>