---
layout: default
title: James Drawings
---

# James' Drawings

<div style="margin: 10px 0;">
    <a href="https://photos.app.goo.gl/dCoKm685gaj6qguV8" target="_blank" style="text-decoration: none; color: #3498db;">View full album on Google Photos →</a>
</div>

<style>
.pinterest-gallery {
    column-count: 3;
    column-gap: 15px;
    margin: 20px 0;
}

.pinterest-gallery .gallery-item {
    break-inside: avoid;
    margin-bottom: 15px;
    position: relative;
    overflow: hidden;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    cursor: pointer;
}

.pinterest-gallery .gallery-item:hover {
    transform: translateY(-5px);
    box-shadow: 0 4px 16px rgba(0,0,0,0.2);
}

.pinterest-gallery img {
    width: 100%;
    height: auto;
    display: block;
    border-radius: 8px;
}

/* Responsive design */
@media (max-width: 768px) {
    .pinterest-gallery {
        column-count: 2;
    }
}

@media (max-width: 480px) {
    .pinterest-gallery {
        column-count: 1;
    }
}

/* Lightbox styles */
.lightbox {
    display: none;
    position: fixed;
    z-index: 1000;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0,0,0,0.9);
    cursor: pointer;
}

.lightbox img {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    max-width: 90%;
    max-height: 90%;
    border-radius: 8px;
}

.lightbox-close {
    position: absolute;
    top: 20px;
    right: 40px;
    color: #fff;
    font-size: 40px;
    font-weight: bold;
    cursor: pointer;
}
</style>

<div class="pinterest-gallery">
    <div class="gallery-item" onclick="openLightbox(this)">
        <img src="https://lh3.googleusercontent.com/pw/AP1GczOtVx7NLUQ_H28yqVRVT5CJcC8AOoe5_8JMAiMaD38E8r60iZfuhr0VjKPp8T54lrNQRyz26eVStH7V9UChOW0LeVVnWLTxrPK-swLZ86KVnrt3qGar=w800" alt="James' Drawing">
    </div>
    <div class="gallery-item" onclick="openLightbox(this)">
        <img src="https://lh3.googleusercontent.com/pw/AP1GczNM2bqGUAtx7MRpJPEoq8CJaMTeijpGWplLtgxUn9uGISb-9HF6mJubT4xcHBwhRsFZjTIVOzNTZu_WZzkTksx5gVsfySCRw_KIfUgbtC8G_X1lGfhQ=w800" alt="James' Drawing">
    </div>
    <div class="gallery-item" onclick="openLightbox(this)">
        <img src="https://lh3.googleusercontent.com/pw/AP1GczPnVFL6RaDF_wwoKVF4hTcWatmLSlC4dO28E3bmKyEwn7fQFnzuMcGnB9pe09ZVsjOZw1TH9HhBJScHoq5uZn_f-l4jHoyVBn15E0jsTa5XZM-Fy-sQ=w800" alt="James' Drawing">
    </div>
    <div class="gallery-item" onclick="openLightbox(this)">
        <img src="https://lh3.googleusercontent.com/pw/AP1GczOrdRAXeeHPeQhdrzW16ktaYVyk99QogcjWYaEt0lL5L9AGlRqYSsdx0uW8q0adIFFkeUu2Ah1lvoPE4iT51Iv7oCP6enLnyFe2FjxfRY1YaPEhWwLe=w800" alt="James' Drawing">
    </div>
    <div class="gallery-item" onclick="openLightbox(this)">
        <img src="https://lh3.googleusercontent.com/pw/AP1GczMzYRP4Q-FgiMs6qimy724LSPi2-XpqfcCgBkoo0JsiDYa5oYqPKOMwDeqJjEwH3mBwMV5jPTiqgvmXyDNHXFTSUrE_RCA7Y3fccIL5io5WpA6yFB1V=w800" alt="James' Drawing">
    </div>
    <div class="gallery-item" onclick="openLightbox(this)">
        <img src="https://lh3.googleusercontent.com/pw/AP1GczOnMDZF1YKY2ioGWaFkEKCu-8ZxAumu7i6-pVVGFO2X8mOVCRx_syH-bq8Zd3aMWHvPYsf6AczFbIBUktArbO_ETB3Gqo6I8EZhf1VyzWQePo94avdJ=w800" alt="James' Drawing">
    </div>
    <div class="gallery-item" onclick="openLightbox(this)">
        <img src="https://lh3.googleusercontent.com/pw/AP1GczNWyQb1ib6rmRPQjkTrjC-0uIfygzlW8JYZi221sQsO-vZ2dTY_noR-_dKb17RFwMsU8L1qM_AoD_e2IuQlJDukryeIveSscq3PzxccH516RqibQtyK=w800" alt="James' Drawing">
    </div>
    <div class="gallery-item" onclick="openLightbox(this)">
        <img src="https://lh3.googleusercontent.com/pw/AP1GczOwi_DYRgDxKpQPdrPBqOJnXRjvxhrgK72SWmphWF2xexfGVUng4wDGwpD---QcynuLzqPJKQN1Ih_lJDxO7lmw4ByOuOB9jvTsZS47IDTEloBbnOfl=w800" alt="James' Drawing">
    </div>
    <div class="gallery-item" onclick="openLightbox(this)">
        <img src="https://lh3.googleusercontent.com/pw/AP1GczMSaDgFdLnE4Q4onEsHdjZ89njCzHVQRZzsd_Oh-qclMRDTzGkmTuU1wDZtQQ8qtSNqtN_y1042m9R0Mo79c75lsMkjARThp1whqixjaYOp6BpcL7V8=w800" alt="James' Drawing">
    </div>
</div>

<div id="lightbox" class="lightbox" onclick="closeLightbox()">
    <span class="lightbox-close">&times;</span>
    <img id="lightbox-img" src="" alt="Enlarged view">
</div>

<script>
function openLightbox(element) {
    const img = element.querySelector('img');
    const lightbox = document.getElementById('lightbox');
    const lightboxImg = document.getElementById('lightbox-img');

    // Replace w800 with w1920 for higher resolution in lightbox
    const highResUrl = img.src.replace('w800', 'w1920');
    lightboxImg.src = highResUrl;
    lightbox.style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closeLightbox() {
    const lightbox = document.getElementById('lightbox');
    lightbox.style.display = 'none';
    document.body.style.overflow = 'auto';
}

// Close lightbox on Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeLightbox();
    }
});
</script>

