<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
<title>Nexa PDF Player</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>

<style>
    html, body { background-color: #120a08; color: #fff; height: 100%; margin: 0; }
    .glass-panel { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); }
    .glass-btn { 
        background: rgba(18, 10, 8, 0.78); 
        backdrop-filter: blur(12px); 
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.22); 
    }
    #pdf-scroll-container::-webkit-scrollbar { width: 5px; height: 5px; }
    #pdf-scroll-container::-webkit-scrollbar-track { background: transparent; }
    #pdf-scroll-container::-webkit-scrollbar-thumb { background: rgba(249, 115, 22, 0.4); border-radius: 10px; }
    .pdf-page-canvas {
        height: auto;
        border-radius: 0.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        background-color: #1a110e;
        transition: width 0.2s ease;
    }
    /* Fullscreen Mode Class */
    .pdf-fullscreen-mode {
        position: fixed !important;
        inset: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        max-width: none !important;
        z-index: 9999 !important;
        border-radius: 0 !important;
        background-color: #120a08 !important;
    }
</style>
</head>
<body class="flex flex-col items-center min-h-screen select-none">

<!-- HEADER -->
<div id="top-header" class="flex flex-col items-center mt-5 mb-3">
    <div class="w-16 h-16 bg-gradient-to-tr from-orange-500 to-red-500 rounded-2xl flex items-center justify-center shadow-[0_0_20px_rgba(249,115,22,0.5)] mb-2">
        <svg class="w-8 h-8 text-white translate-x-0.5" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
    </div>
    <h1 class="text-xl font-bold tracking-wide">Nexa Player</h1>
    <p id="file-name" class="text-gray-400 text-xs mt-1 truncate max-w-xs"></p>
</div>

<!-- PDF VIEWER BOX -->
<div class="w-full flex-1 flex flex-col items-center px-2 pb-3">
    <div id="pdf-wrapper" class="relative w-full max-w-2xl h-[78vh] glass-panel rounded-2xl overflow-hidden flex flex-col transition-all">
        
        <!-- Top-Left: Zoom Controls -->
        <div class="absolute top-2.5 left-2.5 z-30 flex items-center gap-1 glass-btn px-2 py-1 rounded-lg shadow-lg">
            <button id="zoom-out-btn" class="text-gray-200 hover:text-orange-400 font-bold px-1.5 text-sm">−</button>
            <span id="zoom-label" class="text-[11px] font-medium text-gray-300 min-w-[36px] text-center">100%</span>
            <button id="zoom-in-btn" class="text-gray-200 hover:text-orange-400 font-bold px-1.5 text-sm">+</button>
        </div>

        <!-- Top-Right: Page Badge + Quality Dropdown + Infinity/Page Mode -->
        <div class="absolute top-2.5 right-2.5 z-30 flex items-center gap-1.5">
            <span id="pdf-page-indicator" class="glass-btn text-[11px] font-medium text-gray-200 px-2 py-1.5 rounded-lg shadow-lg">
                PDF
            </span>

            <!-- Quality Dropdown Menu -->
            <div class="relative">
                <button id="pdf-quality-btn" 
                    class="glass-btn hover:bg-orange-500/30 active:scale-95 text-[11px] font-bold text-orange-400 px-2.5 py-1.5 rounded-lg flex items-center gap-1 transition-all shadow-lg">
                    <span id="quality-current-text">HD</span>
                    <span class="text-[9px] text-gray-300">▼</span>
                </button>

                <div id="quality-dropdown-menu" class="hidden absolute right-0 mt-1.5 w-28 glass-btn rounded-xl overflow-hidden shadow-2xl flex flex-col z-40 border border-orange-500/30">
                    <button data-q="0" class="quality-opt text-left px-3 py-2 text-xs text-gray-200 hover:bg-orange-500/30 flex justify-between items-center">
                        <span>SD</span><span class="text-[10px] text-gray-400">Fast</span>
                    </button>
                    <button data-q="1" class="quality-opt text-left px-3 py-2 text-xs text-orange-400 font-bold bg-orange-500/10 hover:bg-orange-500/30 flex justify-between items-center border-y border-white/10">
                        <span>HD</span><span class="text-[10px] text-gray-300">Clear</span>
                    </button>
                    <button data-q="2" class="quality-opt text-left px-3 py-2 text-xs text-gray-200 hover:bg-orange-500/30 flex justify-between items-center">
                        <span>ULTRA</span><span class="text-[10px] text-gray-400">4K</span>
                    </button>
                </div>
            </div>

            <!-- Mode Toggle Button (Infinity vs Page Mode) -->
            <button id="pdf-mode-btn" 
                class="glass-btn hover:bg-orange-500/30 active:scale-95 text-xs font-semibold text-white px-2.5 py-1.5 rounded-lg flex items-center gap-1 transition-all shadow-lg">
                <span id="pdf-mode-icon" class="text-orange-400 text-sm leading-none">∞</span>
                <span id="pdf-mode-label">Infinity</span>
            </button>
        </div>

        <!-- PDF Loading Spinner -->
        <div id="pdf-loader" class="absolute inset-0 z-20 flex flex-col items-center justify-center bg-[#120a08]/90 backdrop-blur-sm">
            <div class="w-9 h-9 border-4 border-orange-500 border-t-transparent rounded-full animate-spin mb-2"></div>
            <p id="pdf-loader-text" class="text-xs text-gray-300">Loading PDF...</p>
        </div>

        <!-- Engine 1: PDF.js Canvas Container -->
        <div id="pdf-scroll-container" class="w-full h-full overflow-auto p-2.5 pt-12 pb-14 flex flex-col items-center gap-3 scroll-smooth"></div>

        <!-- Engine 2: CORS-Free Cloud Fallback Container (Google GView) -->
        <div id="pdf-iframe-wrapper" class="hidden w-full h-full relative overflow-hidden">
            <iframe id="pdf-cloud-iframe" class="w-full h-full border-0" allowfullscreen></iframe>
        </div>

        <!-- Bottom Center: Floating Controls (Page Mode) -->
        <div id="pdf-page-controls" class="hidden absolute bottom-3.5 left-1/2 -translate-x-1/2 z-30 flex items-center gap-3 glass-btn px-4 py-2 rounded-xl shadow-xl">
            <button id="prev-page-btn" class="text-white hover:text-orange-400 disabled:opacity-30 text-sm font-bold px-2 py-0.5 transition">
                ◀ Prev
            </button>
            <div class="h-4 w-[1px] bg-white/15"></div>
            <button id="next-page-btn" class="text-white hover:text-orange-400 disabled:opacity-30 text-sm font-bold px-2 py-0.5 transition">
                Next ▶
            </button>
        </div>

        <!-- Bottom Right: Floating Full Screen Button -->
        <button id="fullscreen-btn" 
            class="absolute bottom-3.5 right-3 z-30 glass-btn hover:bg-orange-500/30 active:scale-95 text-xs font-semibold text-white px-3 py-2 rounded-xl flex items-center gap-1.5 shadow-xl transition-all">
            <svg class="w-4 h-4 text-orange-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4 8V4h4M20 8V4h-4M4 16v4h4M20 16v4h-4"/>
            </svg>
            <span id="fs-label">Full</span>
        </button>
    </div>
</div>

<p class="text-gray-600 text-[11px] mt-auto mb-3 tracking-wider">POWERED BY NEXA ENGINE · SECURE</p>

<script>
    const tg = window.Telegram.WebApp;
    tg.expand();
    tg.ready();

    pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

    const params = new URLSearchParams(window.location.search);
    const streamUrl = params.get('stream');
    const fileName  = params.get('name') || 'PDF Document';

    document.getElementById('file-name').textContent = fileName;

    let pdfDoc = null;
    let pdfMode = 'infinity';
    let usingFallbackIframe = false;
    let currentPage = 1;
    let totalPages = 1;
    let renderedPages = new Set();
    let isFullscreen = false;

    const qualityLevels = [
        { label: 'SD', scale: 1.2 },
        { label: 'HD', scale: 2.2 },
        { label: 'ULTRA', scale: 3.5 }
    ];
    let currentQualityIndex = 1;
    let currentZoom = 100;

    const pdfWrapper = document.getElementById('pdf-wrapper');
    const pdfContainer = document.getElementById('pdf-scroll-container');
    const pdfIframeWrapper = document.getElementById('pdf-iframe-wrapper');
    const pdfCloudIframe = document.getElementById('pdf-cloud-iframe');
    const pdfLoader = document.getElementById('pdf-loader');
    const pdfLoaderText = document.getElementById('pdf-loader-text');
    const pdfModeBtn = document.getElementById('pdf-mode-btn');
    const pdfModeIcon = document.getElementById('pdf-mode-icon');
    const pdfModeLabel = document.getElementById('pdf-mode-label');
    const pdfQualityBtn = document.getElementById('pdf-quality-btn');
    const qualityCurrentText = document.getElementById('quality-current-text');
    const qualityDropdownMenu = document.getElementById('quality-dropdown-menu');
    const pdfPageIndicator = document.getElementById('pdf-page-indicator');
    const pdfPageControls = document.getElementById('pdf-page-controls');
    const prevPageBtn = document.getElementById('prev-page-btn');
    const nextPageBtn = document.getElementById('next-page-btn');
    const zoomInBtn = document.getElementById('zoom-in-btn');
    const zoomOutBtn = document.getElementById('zoom-out-btn');
    const zoomLabel = document.getElementById('zoom-label');
    const fullscreenBtn = document.getElementById('fullscreen-btn');
    const fsLabel = document.getElementById('fs-label');

    async function initPdfViewer(url) {
        if (!url) {
            pdfLoaderText.textContent = "Invalid PDF link.";
            return;
        }

        try {
            const loadingTask = pdfjsLib.getDocument({ url: url, withCredentials: false });
            loadingTask.onProgress = (p) => {
                if (p.total > 0) {
                    pdfLoaderText.textContent = `Loading PDF... ${Math.round((p.loaded / p.total) * 100)}%`;
                }
            };

            pdfDoc = await loadingTask.promise;
            usingFallbackIframe = false;
            totalPages = pdfDoc.numPages;
            currentPage = 1;
            renderedPages.clear();
            pdfContainer.innerHTML = '';

            for (let i = 1; i <= totalPages; i++) {
                const canvas = document.createElement('canvas');
                canvas.id = `pdf-page-${i}`;
                canvas.dataset.pageNumber = i;
                canvas.className = 'pdf-page-canvas';
                canvas.style.width = `${currentZoom}%`;
                pdfContainer.appendChild(canvas);
            }

            pdfLoader.classList.add('hidden');
            applyPdfMode();
            setupLazyRenderObserver();
        } catch (corsOrFetchError) {
            console.warn('Direct fetch blocked by CORS, switching to Cloud Viewer:', corsOrFetchError);
            loadCorsFreeFallback(url);
        }
    }

    function loadCorsFreeFallback(url) {
        usingFallbackIframe = true;
        pdfContainer.classList.add('hidden');
        pdfIframeWrapper.classList.remove('hidden');
        pdfLoaderText.textContent = 'Opening PDF reader...';

        const gviewUrl = `https://docs.google.com/gview?embedded=true&url=${encodeURIComponent(url)}`;
        pdfCloudIframe.src = gviewUrl;

        pdfCloudIframe.onload = () => {
            pdfLoader.classList.add('hidden');
        };
        setTimeout(() => pdfLoader.classList.add('hidden'), 3500);
        applyFallbackMode();
    }

    function applyFallbackMode() {
        const vh = pdfIframeWrapper.clientHeight || 500;
        const scaleVal = currentZoom / 100;
        pdfCloudIframe.style.transformOrigin = 'top center';

        if (pdfMode === 'infinity') {
            pdfModeIcon.textContent = '∞';
            pdfModeLabel.textContent = 'Infinity';
            pdfPageIndicator.textContent = 'Scroll';
            pdfPageControls.classList.add('hidden');
            pdfCloudIframe.style.height = '100%';
            pdfCloudIframe.style.transform = `scale(${scaleVal}) translateY(0px)`;
        } else {
            pdfModeIcon.textContent = '📄';
            pdfModeLabel.textContent = 'Page Mode';
            pdfPageIndicator.textContent = `Page ${currentPage}`;
            pdfPageControls.classList.remove('hidden');
            prevPageBtn.disabled = currentPage <= 1;
            nextPageBtn.disabled = false;
            pdfCloudIframe.style.height = `${vh * 25}px`;
            pdfCloudIframe.style.transform = `scale(${scaleVal}) translateY(-${(currentPage - 1) * (vh - 60)}px)`;
            pdfCloudIframe.style.transition = 'transform 0.25s ease-out';
        }
    }

    async function renderPage(pageNum, forceReRender = false) {
        if (!pdfDoc || (renderedPages.has(pageNum) && !forceReRender)) return;
        renderedPages.add(pageNum);

        const page = await pdfDoc.getPage(pageNum);
        const canvas = document.getElementById(`pdf-page-${pageNum}`);
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const qualityMultiplier = qualityLevels[currentQualityIndex].scale;
        const containerWidth = pdfContainer.clientWidth - 20;
        const unscaledViewport = page.getViewport({ scale: 1 });
        const finalScale = (containerWidth / unscaledViewport.width) * qualityMultiplier;
        const viewport = page.getViewport({ scale: finalScale });

        canvas.width = viewport.width;
        canvas.height = viewport.height;

        await page.render({ canvasContext: ctx, viewport }).promise;
    }

    function setupLazyRenderObserver() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const pageNum = parseInt(entry.target.dataset.pageNumber, 10);
                    renderPage(pageNum);
                    if (pdfMode === 'infinity') {
                        currentPage = pageNum;
                        updatePageIndicator();
                    }
                }
            });
        }, { root: pdfContainer, rootMargin: '300px 0px' });

        document.querySelectorAll('.pdf-page-canvas').forEach(c => observer.observe(c));
    }

    function applyPdfMode() {
        if (usingFallbackIframe) return applyFallbackMode();

        const canvases = document.querySelectorAll('.pdf-page-canvas');

        if (pdfMode === 'infinity') {
            pdfModeIcon.textContent = '∞';
            pdfModeLabel.textContent = 'Infinity';
            pdfPageControls.classList.add('hidden');
            canvases.forEach(c => c.classList.remove('hidden'));
            const target = document.getElementById(`pdf-page-${currentPage}`);
            if (target) target.scrollIntoView({ block: 'start' });
        } else {
            pdfModeIcon.textContent = '📄';
            pdfModeLabel.textContent = 'Page Mode';
            pdfPageControls.classList.remove('hidden');
            pdfContainer.scrollTop = 0;

            canvases.forEach((c, idx) => {
                if (idx + 1 === currentPage) c.classList.remove('hidden');
                else c.classList.add('hidden');
            });
            renderPage(currentPage);
            if (currentPage + 1 <= totalPages) renderPage(currentPage + 1);
        }
        updatePageIndicator();
    }

    function updatePageIndicator() {
        pdfPageIndicator.textContent = `${currentPage} / ${totalPages}`;
        prevPageBtn.disabled = currentPage <= 1;
        nextPageBtn.disabled = currentPage >= totalPages;
    }

    // Quality Dropdown Open / Close & Selection
    pdfQualityBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        qualityDropdownMenu.classList.toggle('hidden');
    });

    document.querySelectorAll('.quality-opt').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            currentQualityIndex = parseInt(btn.dataset.q, 10);
            qualityCurrentText.textContent = qualityLevels[currentQualityIndex].label;
            qualityDropdownMenu.classList.add('hidden');

            document.querySelectorAll('.quality-opt').forEach((el, idx) => {
                if (idx === currentQualityIndex) {
                    el.classList.add('text-orange-400', 'font-bold', 'bg-orange-500/10');
                } else {
                    el.classList.remove('text-orange-400', 'font-bold', 'bg-orange-500/10');
                }
            });

            if (usingFallbackIframe) {
                const zoomBoost = currentQualityIndex === 0 ? 90 : (currentQualityIndex === 2 ? 125 : 100);
                updateZoom(zoomBoost);
            } else if (pdfDoc) {
                renderedPages.clear();
                renderPage(currentPage, true);
                if (currentPage + 1 <= totalPages) renderPage(currentPage + 1, true);
            }
        });
    });

    document.addEventListener('click', () => {
        qualityDropdownMenu.classList.add('hidden');
    });

    // Zoom In / Out
    function updateZoom(newZoom) {
        currentZoom = Math.min(250, Math.max(75, newZoom));
        zoomLabel.textContent = `${currentZoom}%`;
        if (usingFallbackIframe) {
            applyFallbackMode();
        } else {
            document.querySelectorAll('.pdf-page-canvas').forEach(c => {
                c.style.width = `${currentZoom}%`;
            });
        }
    }
    zoomInBtn.addEventListener('click', () => updateZoom(currentZoom + 25));
    zoomOutBtn.addEventListener('click', () => updateZoom(currentZoom - 25));

    // Toggle Infinity / Page Mode
    pdfModeBtn.addEventListener('click', () => {
        pdfMode = pdfMode === 'infinity' ? 'page' : 'infinity';
        applyPdfMode();
    });

    // Prev / Next Page Buttons
    prevPageBtn.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            applyPdfMode();
        }
    });
    nextPageBtn.addEventListener('click', () => {
        if (usingFallbackIframe || currentPage < totalPages) {
            currentPage++;
            applyPdfMode();
        }
    });

    // Bottom-Right Fullscreen Button
    fullscreenBtn.addEventListener('click', () => {
        isFullscreen = !isFullscreen;
        pdfWrapper.classList.toggle('pdf-fullscreen-mode', isFullscreen);
        fsLabel.textContent = isFullscreen ? 'Exit' : 'Full';
    });

    // Start Viewer Automatically
    initPdfViewer(streamUrl);
</script>
</body>
</html>
