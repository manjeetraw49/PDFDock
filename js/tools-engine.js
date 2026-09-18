/**
 * PDFDock Client-Side Engine
 * Powers 18 tools 100% in-browser using vendored libraries:
 * - pdf-lib (PDF manipulation: merge, split, delete, reorder, stamp text, stamp image)
 * - pdf.js (PDF rendering & text extraction: PDF to JPG, PDF to PNG, PDF to Text, PDF to Word, PDF to Excel)
 * - jsPDF (Document generation: JPG to PDF, PNG to PDF, Word to PDF, Excel to PDF, PowerPoint to PDF)
 * - SheetJS / XLSX (Spreadsheet conversions: Excel to PDF, PDF to Excel)
 * - Mammoth (Word DOCX parsing)
 * - JSZip (ZIP archives for multi-image exports and PPTX parsing)
 */

window.PDFDock = (function() {
  'use strict';

  // Configure PDF.js worker to use our local vendored file
  if (window.pdfjsLib) {
    window.pdfjsLib.GlobalWorkerOptions.workerSrc = 'js/pdf.worker.min.js';
  }

  // Safe native FileReader cache
  const NativeFileReader = (typeof window !== 'undefined' && window.FileReader) ? window.FileReader : null;

  // Utility: Read File as ArrayBuffer (Safe & Fast native arrayBuffer)
  async function readFileAsArrayBuffer(file) {
    if (!file) throw new Error('No file provided');
    if (typeof file.arrayBuffer === 'function') {
      return await file.arrayBuffer();
    }
    return new Promise((resolve, reject) => {
      const FR = NativeFileReader || window.FileReader;
      const reader = new FR();
      reader.onload = (e) => resolve(e.target.result);
      reader.onerror = (e) => reject(new Error('Failed to read file ' + (file.name || '')));
      reader.readAsArrayBuffer(file);
    });
  }

  // Utility: Read File as Data URL
  function readFileAsDataURL(file) {
    if (!file) throw new Error('No file provided');
    return new Promise((resolve, reject) => {
      const FR = NativeFileReader || window.FileReader;
      const reader = new FR();
      reader.onload = (e) => resolve(e.target.result);
      reader.onerror = (e) => reject(new Error('Failed to read file ' + (file.name || '')));
      reader.readAsDataURL(file);
    });
  }

  // Utility: Load HTMLImageElement
  function loadImageElement(src) {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => resolve(img);
      img.onerror = () => reject(new Error('Failed to load image'));
      img.src = src;
    });
  }

  // Utility: Escape HTML
  function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // Utility: Format File Size
  function formatBytes(bytes) {
    if (!bytes || bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  }

  // ==========================================
  // TOOL 1: MERGE PDF
  // ==========================================
  async function mergePdf(fileList) {
    if (!window.PDFLib) throw new Error('PDF-Lib library not loaded');
    const mergedDoc = await PDFLib.PDFDocument.create();

    for (const file of fileList) {
      const arrayBuffer = await readFileAsArrayBuffer(file);
      const pdf = await PDFLib.PDFDocument.load(arrayBuffer);
      const copiedPages = await mergedDoc.copyPages(pdf, pdf.getPageIndices());
      copiedPages.forEach((page) => mergedDoc.addPage(page));
    }

    const mergedBytes = await mergedDoc.save();
    return {
      blob: new Blob([mergedBytes], { type: 'application/pdf' }),
      filename: 'merged-document.pdf',
      summary: `Successfully merged ${fileList.length} PDF files into one document.`
    };
  }

  // ==========================================
  // TOOL 2: SPLIT PDF
  // ==========================================
  async function splitPdf(file, pageRangeStr) {
    if (!window.PDFLib) throw new Error('PDF-Lib library not loaded');
    const arrayBuffer = await readFileAsArrayBuffer(file);
    const srcDoc = await PDFLib.PDFDocument.load(arrayBuffer);
    const totalPages = srcDoc.getPageCount();

    let targetIndices = [];
    if (!pageRangeStr || pageRangeStr.trim().toLowerCase() === 'all') {
      targetIndices = srcDoc.getPageIndices();
    } else {
      // Parse ranges like "1-3, 5"
      const parts = pageRangeStr.split(',');
      for (const part of parts) {
        const trimmed = part.trim();
        if (trimmed.includes('-')) {
          const [startStr, endStr] = trimmed.split('-');
          const start = Math.max(1, parseInt(startStr, 10));
          const end = Math.min(totalPages, parseInt(endStr, 10));
          for (let i = start; i <= end; i++) targetIndices.push(i - 1);
        } else {
          const num = parseInt(trimmed, 10);
          if (!isNaN(num) && num >= 1 && num <= totalPages) {
            targetIndices.push(num - 1);
          }
        }
      }
    }

    if (targetIndices.length === 0) {
      throw new Error('Please specify valid page numbers within range (1 to ' + totalPages + ').');
    }

    // Deduplicate indices
    targetIndices = Array.from(new Set(targetIndices));

    const newDoc = await PDFLib.PDFDocument.create();
    const copiedPages = await newDoc.copyPages(srcDoc, targetIndices);
    copiedPages.forEach((page) => newDoc.addPage(page));

    const outBytes = await newDoc.save();
    return {
      blob: new Blob([outBytes], { type: 'application/pdf' }),
      filename: `split-pages-${targetIndices.length}.pdf`,
      summary: `Extracted ${targetIndices.length} page(s) from ${file.name}.`
    };
  }

  // ==========================================
  // TOOL 3: COMPRESS PDF
  // ==========================================
  function getCalibratedCompressParameters(targetReduction) {
    const red = Math.min(95, Math.max(20, targetReduction || 70));
    const t = (red - 20) / (95 - 20); // normalized 0 to 1
    // High-resolution scale: 1.75 at 20% down to 1.25 at 95%
    // Keeps DPI well above standard 72 DPI (90-130 DPI equivalent) so text and embedded JPGs stay crisp!
    const scale = 1.75 - t * (1.75 - 1.25);
    // High-fidelity JPEG quality: 0.85 at 20% down to 0.68 at 95%
    // Colors stay rich and boundaries stay clean without JPEG compression blocks!
    const quality = 0.85 - t * (0.85 - 0.68);
    return { scale, quality, t };
  }

  async function resolveCompressProfile(file, targetReduction, sampleCache = null) {
    const red = Math.min(95, Math.max(20, targetReduction || 70));
    if (sampleCache && sampleCache[red] && sampleCache[red].estimatedBytes) {
      return sampleCache[red];
    }

    if (!window.pdfjsLib) {
      const est = Math.max(1024, Math.round(file.size * (1 - red / 100)));
      return { targetReduction: red, scale: 1.4, quality: 0.75, estimatedBytes: est, savingsPercent: red, numPages: 1 };
    }

    const { scale: baseScale, quality: baseQuality } = getCalibratedCompressParameters(red);
    let scale = baseScale;
    let quality = baseQuality;

    try {
      const arrayBuffer = await readFileAsArrayBuffer(file);
      const pdfDoc = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
      const numPages = pdfDoc.numPages;

      const page = await pdfDoc.getPage(1);
      let viewport = page.getViewport({ scale });
      const canvas = document.createElement('canvas');
      canvas.width = Math.round(viewport.width);
      canvas.height = Math.round(viewport.height);
      const ctx = canvas.getContext('2d', { alpha: false });
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.imageSmoothingEnabled = true;
      ctx.imageSmoothingQuality = 'high';
      await page.render({ canvasContext: ctx, viewport }).promise;

      let sampleDataUrl = canvas.toDataURL('image/jpeg', quality);
      let sampleBytes = Math.round((sampleDataUrl.length - 23) * 0.75);
      let estimatedBytes = Math.round((sampleBytes + 850) * numPages + 1500);

      // If document was already compact/vector and rendering at base scale would inflate it,
      // dynamically adapt scale and quality so compressed output is strictly smaller than input
      if (estimatedBytes >= file.size) {
        const targetBytes = Math.max(1024, Math.round(file.size * (1 - (red / 100) * 0.35)));
        const ratio = targetBytes / estimatedBytes;
        const scaleFactor = Math.min(1.0, Math.max(0.65, Math.sqrt(ratio)));
        scale = Math.max(1.05, Math.round(scale * scaleFactor * 100) / 100);
        quality = Math.max(0.65, Math.round((quality - (1 - scaleFactor) * 0.15) * 100) / 100);

        // Re-render sample Page 1 at adjusted scale/quality so estimate and output match 1:1
        viewport = page.getViewport({ scale });
        canvas.width = Math.round(viewport.width);
        canvas.height = Math.round(viewport.height);
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.imageSmoothingEnabled = true;
        ctx.imageSmoothingQuality = 'high';
        await page.render({ canvasContext: ctx, viewport }).promise;

        sampleDataUrl = canvas.toDataURL('image/jpeg', quality);
        sampleBytes = Math.round((sampleDataUrl.length - 23) * 0.75);
        estimatedBytes = Math.round((sampleBytes + 850) * numPages + 1500);
      }

      const savedBytes = Math.max(0, file.size - estimatedBytes);
      const savingsPercent = Math.min(99, Math.max(1, Math.round((savedBytes / file.size) * 100)));

      const profile = {
        targetReduction: red,
        scale,
        quality,
        estimatedBytes,
        savingsPercent,
        numPages
      };

      if (sampleCache) {
        sampleCache[red] = profile;
      }

      return profile;
    } catch (err) {
      const fallback = Math.max(1024, Math.round(file.size * (1 - red / 100)));
      return {
        targetReduction: red,
        scale,
        quality,
        estimatedBytes: fallback,
        savingsPercent: red,
        numPages: 1
      };
    }
  }

  async function estimateCompressedPdfSize(file, targetReduction, sampleCache = null) {
    return await resolveCompressProfile(file, targetReduction, sampleCache);
  }

  async function compressPdf(file, options = {}) {
    if (!window.pdfjsLib || !window.jspdf) throw new Error('PDF libraries not loaded');

    // Resolve target reduction percentage (e.g. 90, 70, 40)
    let targetReduction = 70;
    if (typeof options === 'number') {
      targetReduction = options;
    } else if (options && typeof options.targetReduction === 'number') {
      targetReduction = options.targetReduction;
    } else if (options && options.level) {
      if (options.level === 'extreme') targetReduction = 90;
      else if (options.level === 'light' || options.level === 'low') targetReduction = 40;
      else targetReduction = 70;
    }

    targetReduction = Math.min(95, Math.max(20, targetReduction));

    // Resolve profile (uses identical scale and quality as estimateCompressedPdfSize)
    const profile = await resolveCompressProfile(file, targetReduction, options && options.sampleCache);
    const renderScale = (options && options.scale) || profile.scale;
    const jpegQuality = (options && options.quality) || profile.quality;

    const arrayBuffer = await readFileAsArrayBuffer(file);
    const pdfDoc = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
    const numPages = pdfDoc.numPages;

    const { jsPDF } = window.jspdf;
    let outPdf = null;

    for (let i = 1; i <= numPages; i++) {
      const page = await pdfDoc.getPage(i);
      const viewport = page.getViewport({ scale: renderScale });
      const unscaledViewport = page.getViewport({ scale: 1.0 });

      const canvas = document.createElement('canvas');
      canvas.width = Math.round(viewport.width);
      canvas.height = Math.round(viewport.height);
      const ctx = canvas.getContext('2d', { alpha: false });
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.imageSmoothingEnabled = true;
      ctx.imageSmoothingQuality = 'high';

      await page.render({ canvasContext: ctx, viewport }).promise;

      // Downscale to calibrated high-fidelity JPEG quality
      const compressedDataUrl = canvas.toDataURL('image/jpeg', jpegQuality);
      const orientation = unscaledViewport.width > unscaledViewport.height ? 'landscape' : 'portrait';
      const pageWidth = unscaledViewport.width;
      const pageHeight = unscaledViewport.height;

      if (i === 1) {
        outPdf = new jsPDF({
          orientation,
          unit: 'pt',
          format: [pageWidth, pageHeight],
          hotfixes: ['px_scaling']
        });
        outPdf.addImage(compressedDataUrl, 'JPEG', 0, 0, pageWidth, pageHeight, undefined, 'MEDIUM');
      } else {
        outPdf.addPage([pageWidth, pageHeight], orientation);
        outPdf.addImage(compressedDataUrl, 'JPEG', 0, 0, pageWidth, pageHeight, undefined, 'MEDIUM');
      }
    }

    let compressedBlob = outPdf.output('blob');

    // If rasterized output is larger than original, optimize structure with PDFLib if possible
    if (compressedBlob.size >= file.size && window.PDFLib) {
      try {
        const libDoc = await PDFLib.PDFDocument.load(arrayBuffer, { ignoreEncryption: true });
        const optimizedBytes = await libDoc.save({ useObjectStreams: true, addDefaultPage: false });
        if (optimizedBytes.length < file.size) {
          compressedBlob = new Blob([optimizedBytes], { type: 'application/pdf' });
        }
      } catch (e) {
        console.warn('PDFLib structure optimization skipped:', e);
      }
    }

    const actualSaved = Math.max(0, file.size - compressedBlob.size);
    const savingsPercent = Math.min(99, Math.max(1, Math.round((actualSaved / file.size) * 100)));

    return {
      blob: compressedBlob,
      filename: `compressed-${file.name}`,
      summary: `Compressed from ${formatBytes(file.size)} to ${formatBytes(compressedBlob.size)} (Reduced by ~${savingsPercent}% • JPG Quality Preserved).`
    };
  }

  // ==========================================
  // TOOL 4: JPG -> PDF
  // ==========================================
  async function jpgToPdf(fileList) {
    if (!window.jspdf) throw new Error('jsPDF library not loaded');
    const { jsPDF } = window.jspdf;
    let pdfDoc = null;

    for (let i = 0; i < fileList.length; i++) {
      const file = fileList[i];
      const dataUrl = await readFileAsDataURL(file);
      const img = await loadImageElement(dataUrl);

      const canvas = document.createElement('canvas');
      canvas.width = img.naturalWidth || img.width;
      canvas.height = img.naturalHeight || img.height;
      const ctx = canvas.getContext('2d');
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0);

      const normalizedJpeg = canvas.toDataURL('image/jpeg', 0.92);
      const orientation = canvas.width > canvas.height ? 'landscape' : 'portrait';

      if (i === 0) {
        pdfDoc = new jsPDF({
          orientation,
          unit: 'px',
          format: [canvas.width, canvas.height],
          hotfixes: ['px_scaling']
        });
        pdfDoc.addImage(normalizedJpeg, 'JPEG', 0, 0, canvas.width, canvas.height);
      } else {
        pdfDoc.addPage([canvas.width, canvas.height], orientation);
        pdfDoc.addImage(normalizedJpeg, 'JPEG', 0, 0, canvas.width, canvas.height);
      }
    }

    const blob = pdfDoc.output('blob');
    return {
      blob,
      filename: fileList.length === 1 ? fileList[0].name.replace(/\.[^/.]+$/, '') + '.pdf' : 'converted-images.pdf',
      summary: `Converted ${fileList.length} JPG photo(s) into standard PDF (${formatBytes(blob.size)}).`
    };
  }

  // ==========================================
  // TOOL 5: PDF -> JPG (with Selective Page Extraction)
  // ==========================================
  async function pdfToJpg(file, options = {}) {
    if (!window.pdfjsLib) throw new Error('PDF.js library not loaded');
    const arrayBuffer = await readFileAsArrayBuffer(file);
    const pdfDoc = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
    const numPages = pdfDoc.numPages;

    const scale = typeof options.scale === 'number' ? options.scale : 2.0; // High resolution 2x
    const quality = typeof options.quality === 'number' ? options.quality : 0.95;
    const baseName = file.name.replace(/\.pdf$/i, '');

    // Determine target pages (1-indexed)
    let targetPages = [];
    if (Array.isArray(options.selectedPages) && options.selectedPages.length > 0) {
      targetPages = options.selectedPages.map(p => parseInt(p, 10)).filter(p => !isNaN(p) && p >= 1 && p <= numPages);
    } else if (typeof options.selectedPages === 'number') {
      targetPages = [options.selectedPages];
    } else {
      for (let i = 1; i <= numPages; i++) targetPages.push(i);
    }

    if (targetPages.length === 0) {
      throw new Error('No valid pages selected for JPG conversion.');
    }

    // Helper to render a single page to JPG blob
    async function renderPageToJpgBlob(pageNum) {
      const page = await pdfDoc.getPage(pageNum);
      const viewport = page.getViewport({ scale });
      const canvas = document.createElement('canvas');
      canvas.width = viewport.width;
      canvas.height = viewport.height;
      const ctx = canvas.getContext('2d');
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      await page.render({ canvasContext: ctx, viewport }).promise;
      return new Promise(res => canvas.toBlob(res, 'image/jpeg', quality));
    }

    // Single page output: Return direct high-res JPG
    if (targetPages.length === 1) {
      const pageNum = targetPages[0];
      const blob = await renderPageToJpgBlob(pageNum);
      return {
        blob,
        filename: `${baseName}-page${pageNum}.jpg`,
        summary: `Converted page ${pageNum} to high-resolution JPG (${formatBytes(blob.size)}).`
      };
    }

    // Multiple pages: Bundle selected into ZIP
    if (!window.JSZip) throw new Error('JSZip library not loaded');
    const zip = new JSZip();

    for (const pageNum of targetPages) {
      const pageBlob = await renderPageToJpgBlob(pageNum);
      zip.file(`page-${pageNum}.jpg`, pageBlob);
    }

    const zipBlob = await zip.generateAsync({ type: 'blob' });
    return {
      blob: zipBlob,
      filename: `${baseName}-selected-jpgs.zip`,
      summary: `Converted ${targetPages.length} PDF page(s) into high-res JPG images (Zipped ${formatBytes(zipBlob.size)}).`
    };
  }

  // ==========================================
  // TOOL 6: DELETE PDF PAGES
  // ==========================================
  async function deletePdfPages(file, pagesToDeleteStr) {
    if (!window.PDFLib) throw new Error('PDF-Lib library not loaded');
    const arrayBuffer = await readFileAsArrayBuffer(file);
    const doc = await PDFLib.PDFDocument.load(arrayBuffer);
    const totalPages = doc.getPageCount();

    const deleteIndices = new Set();
    const parts = (pagesToDeleteStr || '').split(',');
    for (const part of parts) {
      const num = parseInt(part.trim(), 10);
      if (!isNaN(num) && num >= 1 && num <= totalPages) {
        deleteIndices.add(num - 1);
      }
    }

    if (deleteIndices.size === 0) {
      throw new Error(`Please specify valid page numbers to delete between 1 and ${totalPages}.`);
    }
    if (deleteIndices.size >= totalPages) {
      throw new Error('Cannot delete all pages from the PDF document.');
    }

    // Keep non-deleted pages
    const keepIndices = doc.getPageIndices().filter(i => !deleteIndices.has(i));
    const newDoc = await PDFLib.PDFDocument.create();
    const copiedPages = await newDoc.copyPages(doc, keepIndices);
    copiedPages.forEach(p => newDoc.addPage(p));

    const bytes = await newDoc.save();
    return {
      blob: new Blob([bytes], { type: 'application/pdf' }),
      filename: `deleted-pages-${file.name}`,
      summary: `Removed ${deleteIndices.size} page(s). New PDF has ${keepIndices.length} page(s).`
    };
  }

  // ==========================================
  // TOOL 7: REORDER PDF PAGES
  // ==========================================
  async function reorderPdfPages(file, orderStr) {
    if (!window.PDFLib) throw new Error('PDF-Lib library not loaded');
    const arrayBuffer = await readFileAsArrayBuffer(file);
    const doc = await PDFLib.PDFDocument.load(arrayBuffer);
    const totalPages = doc.getPageCount();

    const orderParts = (orderStr || '').split(',');
    const newIndices = [];
    for (const part of orderParts) {
      const num = parseInt(part.trim(), 10);
      if (!isNaN(num) && num >= 1 && num <= totalPages) {
        newIndices.push(num - 1);
      }
    }

    if (newIndices.length === 0) {
      throw new Error(`Please specify new page order (e.g., "3, 1, 2" for a ${totalPages}-page PDF).`);
    }

    const newDoc = await PDFLib.PDFDocument.create();
    const copiedPages = await newDoc.copyPages(doc, newIndices);
    copiedPages.forEach(p => newDoc.addPage(p));

    const bytes = await newDoc.save();
    return {
      blob: new Blob([bytes], { type: 'application/pdf' }),
      filename: `reordered-${file.name}`,
      summary: `Successfully reordered ${newIndices.length} pages in specified sequence.`
    };
  }

  // ==========================================
  // TOOL 8: PDF -> PNG (with Selective Page Extraction)
  // ==========================================
  async function pdfToPng(file, options = {}) {
    if (!window.pdfjsLib) throw new Error('PDF.js library not loaded');
    const arrayBuffer = await readFileAsArrayBuffer(file);
    const pdfDoc = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
    const numPages = pdfDoc.numPages;

    const scale = typeof options.scale === 'number' ? options.scale : 2.0;
    const baseName = file.name.replace(/\.pdf$/i, '');

    let targetPages = [];
    if (Array.isArray(options.selectedPages) && options.selectedPages.length > 0) {
      targetPages = options.selectedPages.map(p => parseInt(p, 10)).filter(p => !isNaN(p) && p >= 1 && p <= numPages);
    } else if (typeof options.selectedPages === 'number') {
      targetPages = [options.selectedPages];
    } else {
      for (let i = 1; i <= numPages; i++) targetPages.push(i);
    }

    if (targetPages.length === 0) {
      throw new Error('No valid pages selected for PNG conversion.');
    }

    async function renderPageToPngBlob(pageNum) {
      const page = await pdfDoc.getPage(pageNum);
      const viewport = page.getViewport({ scale });
      const canvas = document.createElement('canvas');
      canvas.width = viewport.width;
      canvas.height = viewport.height;
      const ctx = canvas.getContext('2d');
      await page.render({ canvasContext: ctx, viewport }).promise;
      return new Promise(res => canvas.toBlob(res, 'image/png'));
    }

    if (targetPages.length === 1) {
      const pageNum = targetPages[0];
      const blob = await renderPageToPngBlob(pageNum);
      return {
        blob,
        filename: `${baseName}-page${pageNum}.png`,
        summary: `Converted page ${pageNum} to high-resolution PNG (${formatBytes(blob.size)}).`
      };
    }

    if (!window.JSZip) throw new Error('JSZip library not loaded');
    const zip = new JSZip();

    for (const pageNum of targetPages) {
      const pageBlob = await renderPageToPngBlob(pageNum);
      zip.file(`page-${pageNum}.png`, pageBlob);
    }

    const zipBlob = await zip.generateAsync({ type: 'blob' });
    return {
      blob: zipBlob,
      filename: `${baseName}-selected-pngs.zip`,
      summary: `Converted ${targetPages.length} PDF page(s) into high-res PNG images (Zipped ${formatBytes(zipBlob.size)}).`
    };
  }

  // ==========================================
  // TOOL 9: PNG -> PDF
  // ==========================================
  async function pngToPdf(fileList) {
    return jpgToPdf(fileList); // Same robust canvas-based pipeline
  }

  // ==========================================
  // TOOL 10: PDF -> TEXT
  // ==========================================
  async function pdfToText(file) {
    if (!window.pdfjsLib) throw new Error('PDF.js library not loaded');
    const arrayBuffer = await readFileAsArrayBuffer(file);
    const pdfDoc = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
    const numPages = pdfDoc.numPages;

    let fullText = `=== Extracted Text from ${file.name} ===\n\n`;

    for (let i = 1; i <= numPages; i++) {
      const page = await pdfDoc.getPage(i);
      const content = await page.getTextContent();
      const pageText = content.items.map(item => item.str).join(' ');
      fullText += `--- Page ${i} ---\n${pageText}\n\n`;
    }

    const blob = new Blob([fullText], { type: 'text/plain;charset=utf-8' });
    return {
      blob,
      filename: `${file.name.replace(/\.pdf$/i, '')}.txt`,
      summary: `Extracted readable text across ${numPages} pages (${formatBytes(blob.size)}).`
    };
  }

  // Helper: Hex color to RGB object
  function hexToRgb(hex) {
    if (!hex) return { r: 0.2, g: 0.2, b: 0.2 };
    let c = String(hex).replace('#', '').trim();
    if (c.length === 3) c = c[0] + c[0] + c[1] + c[1] + c[2] + c[2];
    const num = parseInt(c, 16);
    if (isNaN(num)) return { r: 0.2, g: 0.2, b: 0.2 };
    return {
      r: ((num >> 16) & 255) / 255,
      g: ((num >> 8) & 255) / 255,
      b: (num & 255) / 255
    };
  }

  // ==========================================
  // TOOL 11: ADD TEXT & WATERMARK TO PDF
  // ==========================================
  async function addTextToPdf(file, textToAdd, options = {}) {
    if (!window.PDFLib) throw new Error('PDF-Lib library not loaded');
    const arrayBuffer = await readFileAsArrayBuffer(file);
    const doc = await PDFLib.PDFDocument.load(arrayBuffer);

    // Normalize options (supports string or object)
    let opts = {};
    if (typeof options === 'string') {
      opts = { position: options };
    } else if (options && typeof options === 'object') {
      opts = { ...options };
    }

    const stampTextTemplate = (opts.text || textToAdd || 'CONFIDENTIAL').trim();
    const position = opts.position || 'diagonal-45';
    const fontSize = parseInt(opts.fontSize || opts.size, 10) || 48;
    const fontFamily = opts.fontFamily || 'HelveticaBold';
    const opacity = typeof opts.opacity === 'number' ? Math.max(0.05, Math.min(1.0, opts.opacity)) : 0.25;
    const hexColor = opts.color || '#dc2626';
    const rgb = hexToRgb(hexColor);
    const pageSelection = opts.pages || 'all';
    const customRange = opts.pageRange || '';

    // Embed chosen standard font
    let selectedFont = PDFLib.StandardFonts.HelveticaBold;
    if (fontFamily === 'Helvetica') selectedFont = PDFLib.StandardFonts.Helvetica;
    else if (fontFamily === 'TimesRoman') selectedFont = PDFLib.StandardFonts.TimesRoman;
    else if (fontFamily === 'TimesRomanBold') selectedFont = PDFLib.StandardFonts.TimesRomanBold;
    else if (fontFamily === 'Courier') selectedFont = PDFLib.StandardFonts.Courier;
    else if (fontFamily === 'CourierBold') selectedFont = PDFLib.StandardFonts.CourierBold;
    const font = await doc.embedFont(selectedFont);

    // Calculate rotation in degrees
    let rotationDeg = 0;
    if (typeof opts.rotation === 'number') {
      rotationDeg = opts.rotation;
    } else if (position === 'diagonal-45') {
      rotationDeg = 45;
    } else if (position === 'diagonal-minus-45') {
      rotationDeg = -45;
    } else if (position === 'center' || position === 'top' || position === 'bottom') {
      rotationDeg = 0;
    }

    const pages = doc.getPages();
    const totalPages = pages.length;

    // Filter target pages
    const targetPageIndices = new Set();
    if (pageSelection === 'all') {
      for (let i = 0; i < totalPages; i++) targetPageIndices.add(i);
    } else if (pageSelection === 'first') {
      targetPageIndices.add(0);
    } else if (pageSelection === 'last') {
      targetPageIndices.add(totalPages - 1);
    } else if (pageSelection === 'not-first') {
      for (let i = 1; i < totalPages; i++) targetPageIndices.add(i);
    } else if (pageSelection === 'custom' && customRange) {
      const parts = customRange.split(',');
      parts.forEach(p => {
        p = p.trim();
        if (p.includes('-')) {
          const [s, e] = p.split('-').map(n => parseInt(n.trim(), 10));
          if (!isNaN(s) && !isNaN(e)) {
            for (let k = Math.max(1, s); k <= Math.min(totalPages, e); k++) {
              targetPageIndices.add(k - 1);
            }
          }
        } else {
          const num = parseInt(p, 10);
          if (!isNaN(num) && num >= 1 && num <= totalPages) {
            targetPageIndices.add(num - 1);
          }
        }
      });
    }
    if (targetPageIndices.size === 0) {
      for (let i = 0; i < totalPages; i++) targetPageIndices.add(i);
    }

    // Draw on each selected page
    pages.forEach((page, pageIdx) => {
      if (!targetPageIndices.has(pageIdx)) return;

      const { width, height } = page.getSize();

      // Dynamic text replacement for page numbers
      let currentText = stampTextTemplate
        .replace(/\{n\}/gi, String(pageIdx + 1))
        .replace(/\{page\}/gi, String(pageIdx + 1))
        .replace(/\{total\}/gi, String(totalPages))
        .replace(/\{pages\}/gi, String(totalPages));

      const textWidth = font.widthOfTextAtSize(currentText, fontSize);
      const textHeight = font.heightAtSize(fontSize);

      // Determine center anchor (xc, yc)
      let xc = width / 2;
      let yc = height / 2;
      const margin = 36; // 0.5 inch

      if (position.startsWith('top')) {
        yc = height - margin - textHeight / 2;
        if (position === 'top-left') xc = margin + textWidth / 2;
        else if (position === 'top-right') xc = width - margin - textWidth / 2;
        else xc = width / 2;
      } else if (position.startsWith('bottom')) {
        yc = margin + textHeight / 2;
        if (position === 'bottom-left') xc = margin + textWidth / 2;
        else if (position === 'bottom-right') xc = width - margin - textWidth / 2;
        else xc = width / 2;
      } else if (position === 'top') {
        yc = height - margin - textHeight / 2;
      } else if (position === 'bottom') {
        yc = margin + textHeight / 2;
      }

      // Convert rotation angle to radians
      const rad = (rotationDeg * Math.PI) / 180;
      const cosA = Math.cos(rad);
      const sinA = Math.sin(rad);

      // Place center of rotated text at (xc, yc)
      const x = xc - (textWidth / 2 * cosA - textHeight / 2 * sinA);
      const y = yc - (textWidth / 2 * sinA + textHeight / 2 * cosA);

      const drawOptions = {
        x,
        y,
        size: fontSize,
        font,
        color: PDFLib.rgb(rgb.r, rgb.g, rgb.b),
        opacity,
        rotate: PDFLib.degrees(rotationDeg)
      };

      page.drawText(currentText, drawOptions);
    });

    const bytes = await doc.save();
    return {
      blob: new Blob([bytes], { type: 'application/pdf' }),
      filename: `watermarked-${file.name}`,
      summary: `Applied watermark/text to ${targetPageIndices.size} of ${totalPages} page(s).`
    };
  }

  // ==========================================
  // TOOL 12: ADD IMAGE / SIGNATURE TO PDF
  // ==========================================
  async function addImageToPdf(pdfFile, imageFileOrDataUrl, options = {}) {
    if (!window.PDFLib) throw new Error('PDF-Lib library not loaded');
    const pdfBuffer = await readFileAsArrayBuffer(pdfFile);
    const doc = await PDFLib.PDFDocument.load(pdfBuffer);

    let embeddedImg;
    if (typeof imageFileOrDataUrl === 'string' && imageFileOrDataUrl.startsWith('data:')) {
      // Base64 Data URL (drawn signature or typed signature)
      const base64Data = imageFileOrDataUrl.split(',')[1];
      const binaryStr = atob(base64Data);
      const len = binaryStr.length;
      const bytes = new Uint8Array(len);
      for (let i = 0; i < len; i++) {
        bytes[i] = binaryStr.charCodeAt(i);
      }
      try {
        embeddedImg = await doc.embedPng(bytes);
      } catch (e) {
        embeddedImg = await doc.embedJpg(bytes);
      }
    } else {
      const imgBuffer = await readFileAsArrayBuffer(imageFileOrDataUrl);
      try {
        embeddedImg = await doc.embedPng(imgBuffer);
      } catch (e) {
        try {
          embeddedImg = await doc.embedJpg(imgBuffer);
        } catch (err2) {
          // If neither raw png nor jpg, convert via HTMLImageElement to PNG canvas
          const dataUrl = await readFileAsDataURL(imageFileOrDataUrl);
          const imgEl = await loadImageElement(dataUrl);
          const c = document.createElement('canvas');
          c.width = imgEl.width;
          c.height = imgEl.height;
          c.getContext('2d').drawImage(imgEl, 0, 0);
          const pngUrl = c.toDataURL('image/png');
          const pngBytes = Uint8Array.from(atob(pngUrl.split(',')[1]), c => c.charCodeAt(0));
          embeddedImg = await doc.embedPng(pngBytes);
        }
      }
    }

    const pages = doc.getPages();
    const position = options.position || 'bottom-right';
    const targetPage = options.targetPage || 'first';

    let targetPages = [];
    if (targetPage === 'all') {
      targetPages = pages;
    } else if (targetPage === 'last') {
      targetPages = [pages[pages.length - 1]];
    } else {
      targetPages = [pages[0]];
    }

    targetPages.forEach(p => {
      const { width, height } = p.getSize();
      const maxW = 160;
      const maxH = 90;
      const scale = Math.min(maxW / embeddedImg.width, maxH / embeddedImg.height, 1);
      const imgWidth = embeddedImg.width * scale;
      const imgHeight = embeddedImg.height * scale;

      let x = width - imgWidth - 30;
      let y = 30;

      if (position === 'bottom-left') {
        x = 30;
        y = 30;
      } else if (position === 'bottom-center') {
        x = (width - imgWidth) / 2;
        y = 30;
      } else if (position === 'top-right') {
        x = width - imgWidth - 30;
        y = height - imgHeight - 30;
      } else if (position === 'center') {
        x = (width - imgWidth) / 2;
        y = (height - imgHeight) / 2;
      }

      p.drawImage(embeddedImg, {
        x,
        y,
        width: imgWidth,
        height: imgHeight
      });
    });

    const outBytes = await doc.save();
    return {
      blob: new Blob([outBytes], { type: 'application/pdf' }),
      filename: `signed-${pdfFile.name.replace(/\.[^/.]+$/, '')}.pdf`,
      summary: `Successfully signed and embedded signature onto ${pdfFile.name}.`
    };
  }

  // ==========================================
  // TOOL 13: PROTECT PDF (Industry-standard ISO 32000 PDF Encryption)
  // ==========================================
  async function protectPdf(file, password, options = {}) {
    if (!window.PDFLib) throw new Error('PDF-Lib library not loaded');
    if (!window.PDFEncrypt) throw new Error('PDF Encryption module not loaded');
    if (!password || typeof password !== 'string' || password.length === 0) {
      throw new Error('Please provide a valid password to protect this document.');
    }

    const arrayBuffer = await readFileAsArrayBuffer(file);
    const pdfBytes = new Uint8Array(arrayBuffer);

    // Detect environment encryption support (AES-256 requires crypto.subtle in secure context)
    const canUseAES = (typeof window !== 'undefined' && window.crypto && window.crypto.subtle && window.isSecureContext !== false);
    let algo = options.algorithm || (canUseAES ? 'AES-256' : 'RC4');
    if (algo === 'AES-256' && !canUseAES) {
      console.warn('Web Crypto AES-256 not available in non-secure context; falling back to 128-bit RC4');
      algo = 'RC4';
    }

    const encryptOpts = {
      algorithm: algo,
      ownerPassword: options.ownerPassword || password,
      allowPrinting: options.allowPrinting !== false,
      allowCopying: options.allowCopying !== false,
      allowModifying: !!options.allowModifying,
      allowAnnotating: !!options.allowAnnotating,
      allowFillingForms: options.allowFillingForms !== false,
      allowExtraction: options.allowExtraction !== false,
      allowAssembly: !!options.allowAssembly,
      allowHighQualityPrint: options.allowHighQualityPrint !== false
    };

    let encryptedBytes;
    try {
      encryptedBytes = await window.PDFEncrypt.encryptPDF(pdfBytes, password, encryptOpts);
    } catch (err) {
      if (err && (err.name === 'AlreadyEncryptedError' || (err.message && err.message.includes('already encrypted')))) {
        throw new Error('This PDF file is already password-protected. Please select an unencrypted PDF.');
      }
      // If AES-256 threw an error (e.g. unexpected crypto issue), try RC4 as graceful fallback
      if (algo === 'AES-256') {
        console.warn('AES-256 encryption attempt failed, retrying with RC4 fallback:', err);
        encryptOpts.algorithm = 'RC4';
        encryptedBytes = await window.PDFEncrypt.encryptPDF(pdfBytes, password, encryptOpts);
        algo = 'RC4';
      } else {
        throw err;
      }
    }

    const baseName = file.name ? file.name.replace(/\.[^/.]+$/, '') : 'document';
    const algoLabel = algo === 'AES-256' ? 'AES-256 bit' : '128-bit RC4';

    return {
      blob: new Blob([encryptedBytes], { type: 'application/pdf' }),
      filename: `protected-${baseName}.pdf`,
      summary: `Document successfully locked with ${algoLabel} encryption.`,
      algorithm: algo,
      password: password
    };
  }

  // ==========================================
  // TOOL 14: WORD -> PDF (Native 1:1 Word Print Layout & High-DPI Visual Engine)
  // ==========================================
  async function wordToPdf(file, onProgress) {
    if (!window.jspdf) throw new Error('PDF conversion library not loaded');
    const { jsPDF } = window.jspdf;

    if (onProgress) onProgress(10, 'Reading Word document...');
    let arrayBuffer;
    try {
      arrayBuffer = await readFileAsArrayBuffer(file);
    } catch (e) {
      throw new Error('Could not read Word document: ' + e.message);
    }

    // ----------------------------------------------------
    // METHOD 1: Native Microsoft Word Layout Engine (docx-preview)
    // Faithfully reproduces Word's exact page margins, paper dimensions,
    // orientation, fonts, alignments, tables, borders, headers, footers & page breaks.
    // ----------------------------------------------------
    if (window.docx && window.docx.renderAsync) {
      let renderHost = null;
      try {
        if (onProgress) onProgress(25, 'Parsing Word document structure, styles & margins...');

        renderHost = document.createElement('div');
        renderHost.id = 'docx-word-render-host';
        renderHost.style.position = 'fixed';
        renderHost.style.left = '-9999px';
        renderHost.style.top = '0';
        renderHost.style.width = 'auto';
        renderHost.style.height = 'auto';
        renderHost.style.background = '#ffffff';
        renderHost.style.zIndex = '-9999';
        document.body.appendChild(renderHost);

        // Modern typographic font fallback for Office fonts on any platform
        const fontFallback = document.createElement('style');
        fontFallback.textContent = `
          .docx {
            font-family: Calibri, Aptos, "Segoe UI", -apple-system, BlinkMacSystemFont, Roboto, Arial, sans-serif;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
          }
        `;
        renderHost.appendChild(fontFallback);

        await window.docx.renderAsync(arrayBuffer, renderHost, renderHost, {
          breakPages: true,
          ignoreHeight: false,
          ignoreWidth: false,
          ignoreFonts: false,
          renderHeaders: true,
          renderFooters: true,
          renderFootnotes: true,
          renderEndnotes: true,
          ignoreLastRenderedPageBreak: false, // Preserves native Word page breaks
          trimXmlDeclaration: true,
          useBase64URL: true,
          experimental: true,
          inWrapper: true
        });

        // Preload and stabilize all embedded images (physical canvas cropping & container sizing)
        const docImages = Array.from(renderHost.querySelectorAll('img'));
        for (const img of docImages) {
          if (!img.complete) {
            await new Promise(r => { img.onload = r; img.onerror = r; });
          }

          // Uncollapse drawing wrapper divs inside tables or text
          let parent = img.parentElement;
          while (parent && parent !== renderHost && parent.tagName !== 'TD' && parent.tagName !== 'P' && parent.tagName !== 'SECTION') {
            if (parent.tagName === 'DIV' && (parent.style.width === '0px' || parent.style.height === '0px')) {
              parent.style.width = (img.style.width && img.style.width !== '0px') ? img.style.width : 'auto';
              parent.style.height = (img.style.height && img.style.height !== '0px') ? img.style.height : 'auto';
              parent.style.display = 'inline-block';
              parent.style.overflow = 'hidden';
              parent.style.position = 'relative';
            }
            parent = parent.parentElement;
          }

          // Physical canvas crop if image has scale transform or srcRect dataset
          const tf = img.style.transform || '';
          const scaleMatch = tf.match(/scale\(([\d\.]+)\s*,?\s*([\d\.]+)?\)/i);
          let srcRect = null;
          if (img.dataset.srcRect) {
            try { srcRect = JSON.parse(img.dataset.srcRect); } catch (e) {}
          }

          if (!img.dataset.cropped && (srcRect || (scaleMatch && (parseFloat(scaleMatch[1]) > 1.05 || parseFloat(scaleMatch[2] || scaleMatch[1]) > 1.05)))) {
            let a = 0, s = 0, n = 0, l = 0;
            if (srcRect) {
              [a, s, n, l] = srcRect;
            } else if (scaleMatch) {
              const scaleX = parseFloat(scaleMatch[1]) || 1;
              const scaleY = parseFloat(scaleMatch[2] || scaleMatch[1]) || 1;
              const cp = img.style.clipPath || img.getAttribute('style') || '';
              const rectMatch = cp.match(/rect\(([\d\.]+)%\s*([\d\.]+)%\s*([\d\.]+)%\s*([\d\.]+)%\)/i);
              if (rectMatch) {
                s = parseFloat(rectMatch[1]) / 100;
                n = 1 - (parseFloat(rectMatch[2]) / 100);
                l = 1 - (parseFloat(rectMatch[3]) / 100);
                a = parseFloat(rectMatch[4]) / 100;
              } else {
                n = 1.0 - (1.0 / scaleX);
                l = 1.0 - (1.0 / scaleY);
              }
            }

            const nw = img.naturalWidth || img.width;
            const nh = img.naturalHeight || img.height;
            if (nw > 0 && nh > 0) {
              const sx = Math.max(0, Math.round(a * nw));
              const sy = Math.max(0, Math.round(s * nh));
              const sw = Math.min(nw - sx, Math.round((1 - a - n) * nw));
              const sh = Math.min(nh - sy, Math.round((1 - s - l) * nh));

              if (sw > 0 && sh > 0) {
                const cv = document.createElement('canvas');
                cv.width = sw;
                cv.height = sh;
                const ctx = cv.getContext('2d');
                ctx.drawImage(img, sx, sy, sw, sh, 0, 0, sw, sh);

                const newSrc = cv.toDataURL('image/png');
                await new Promise(resolve => {
                  img.onload = resolve;
                  img.onerror = resolve;
                  img.src = newSrc;
                });

                img.dataset.cropped = 'true';
                img.style.transform = 'none';
                img.style.clipPath = 'none';
                img.style.position = 'relative';
                img.style.left = '0';
                img.style.top = '0';
              }
            }
          }
        }

        // Center and format table cells with rowspan
        const allTds = Array.from(renderHost.querySelectorAll('td'));
        allTds.forEach(td => {
          if (td.getAttribute('rowspan')) {
            td.style.verticalAlign = 'middle';
            td.style.textAlign = 'center';
            const ps = td.querySelectorAll('p');
            ps.forEach(p => {
              p.style.textAlign = 'center';
              p.style.margin = '0 auto';
            });
          }
        });

        await new Promise(r => setTimeout(r, 100));

        // Locate all rendered Word page sections
        let pageSections = Array.from(renderHost.querySelectorAll('section.docx'));
        if (pageSections.length === 0) {
          const wrapper = renderHost.querySelector('.docx-wrapper') || renderHost;
          pageSections = [wrapper];
        }

        // Clean web preview styles (remove web container drop-shadows & margins for clean PDF printing)
        const wrapper = renderHost.querySelector('.docx-wrapper');
        if (wrapper) {
          wrapper.style.background = 'transparent';
          wrapper.style.padding = '0';
          wrapper.style.margin = '0';
        }

        pageSections.forEach(s => {
          s.style.boxShadow = 'none';
          s.style.margin = '0';
          s.style.marginBottom = '0';
          s.style.backgroundColor = '#ffffff';
        });

        const totalSections = pageSections.length;
        if (onProgress) onProgress(45, `Rendering ${totalSections} Word page(s) at high resolution...`);

        let pdfDoc = null;
        let compiledPageCount = 0;

        for (let sIdx = 0; sIdx < totalSections; sIdx++) {
          const section = pageSections[sIdx];
          if (onProgress) {
            const pct = 45 + Math.round(((sIdx + 1) / totalSections) * 45);
            onProgress(pct, `Compiling Word page ${sIdx + 1} of ${totalSections}...`);
          }

          const pageW = section.offsetWidth || 794;
          const pageH = section.offsetHeight || 1123;
          const scrollH = section.scrollHeight || pageH;
          const widthPt = (pageW / 96) * 72;
          const heightPt = (pageH / 96) * 72;
          const orientation = widthPt > heightPt ? 'landscape' : 'portrait';

          // Handle unpaginated long content (> 20% taller than target page height)
          if (scrollH > pageH * 1.2) {
            section.style.overflow = 'visible';
            section.style.minHeight = scrollH + 'px';
            section.style.height = scrollH + 'px';

            const fullCanvas = await html2canvas(section, {
              width: pageW,
              height: scrollH,
              scale: 2, // 2x High-DPI for crisp text
              useCORS: true,
              logging: false,
              backgroundColor: '#ffffff',
              windowWidth: pageW
            });

            const pageCanvasH = pageH * 2; // canvas pixels at 2x
            const pageCanvasW = fullCanvas.width;
            let yOffset = 0;

            while (yOffset < fullCanvas.height) {
              const sliceH = Math.min(pageCanvasH, fullCanvas.height - yOffset);
              const sliceCanvas = document.createElement('canvas');
              sliceCanvas.width = pageCanvasW;
              sliceCanvas.height = sliceH;
              const sCtx = sliceCanvas.getContext('2d');
              sCtx.fillStyle = '#ffffff';
              sCtx.fillRect(0, 0, sliceCanvas.width, sliceCanvas.height);
              sCtx.drawImage(fullCanvas, 0, yOffset, pageCanvasW, sliceH, 0, 0, pageCanvasW, sliceH);

              const sliceJpg = sliceCanvas.toDataURL('image/jpeg', 0.96);
              const slicePtH = ((sliceH / 2) / 96) * 72;

              if (!pdfDoc) {
                pdfDoc = new jsPDF({
                  orientation: orientation,
                  unit: 'pt',
                  format: [widthPt, slicePtH],
                  hotfixes: ['px_scaling']
                });
                pdfDoc.addImage(sliceJpg, 'JPEG', 0, 0, widthPt, slicePtH);
              } else {
                pdfDoc.addPage([widthPt, slicePtH], orientation);
                pdfDoc.addImage(sliceJpg, 'JPEG', 0, 0, widthPt, slicePtH);
              }
              compiledPageCount++;
              yOffset += sliceH;
            }
          } else {
            // Standard page within expected bounds
            const canvas = await html2canvas(section, {
              width: pageW,
              height: pageH,
              scale: 2, // 2x High-DPI for razor-sharp typography
              useCORS: true,
              logging: false,
              backgroundColor: '#ffffff',
              windowWidth: pageW
            });
            const pageJpg = canvas.toDataURL('image/jpeg', 0.96);

            if (!pdfDoc) {
              pdfDoc = new jsPDF({
                orientation: orientation,
                unit: 'pt',
                format: [widthPt, heightPt],
                hotfixes: ['px_scaling']
              });
              pdfDoc.addImage(pageJpg, 'JPEG', 0, 0, widthPt, heightPt);
            } else {
              pdfDoc.addPage([widthPt, heightPt], orientation);
              pdfDoc.addImage(pageJpg, 'JPEG', 0, 0, widthPt, heightPt);
            }
            compiledPageCount++;
          }
        }

        if (pdfDoc && compiledPageCount > 0) {
          if (onProgress) onProgress(95, 'Finalizing complete PDF document...');
          const blob = pdfDoc.output('blob');
          return {
            blob,
            filename: file.name.replace(/\.[^/.]+$/, '') + '.pdf',
            summary: `Converted all ${compiledPageCount} Word page(s) preserving exact layout, typography, tables, and margins.`
          };
        }
      } catch (docxErr) {
        console.warn('docx-preview engine encountered an issue, falling back to Mammoth:', docxErr);
      } finally {
        if (renderHost && document.body.contains(renderHost)) {
          document.body.removeChild(renderHost);
        }
      }
    }

    // ----------------------------------------------------
    // METHOD 2: Mammoth Semantic Layout Engine (Fallback)
    // ----------------------------------------------------
    if (!window.mammoth) throw new Error('Word conversion libraries not loaded');
    if (onProgress) onProgress(25, 'Parsing document typography & layout...');
    const result = await mammoth.convertToHtml({ arrayBuffer });
    const rawHtml = result.value || '<p>Empty Document</p>';

    const a4WidthPt = 595.28;
    const a4HeightPt = 841.89;
    const canvasW = 794;  // A4 portrait width at 96 DPI
    const canvasH = 1123; // A4 portrait height at 96 DPI

    // Staging container to hold and measure elements
    const parseHost = document.createElement('div');
    parseHost.style.position = 'fixed';
    parseHost.style.left = '-9999px';
    parseHost.style.top = '0';
    parseHost.style.width = '686px'; // Content width (794 - 54*2)
    parseHost.style.fontSize = '14px';
    parseHost.style.lineHeight = '1.6';
    parseHost.style.fontFamily = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif';
    parseHost.style.visibility = 'hidden';
    parseHost.innerHTML = rawHtml;
    document.body.appendChild(parseHost);

    // Style elements cleanly like authentic Word documents
    const docStyles = document.createElement('style');
    docStyles.textContent = `
      .word-page-stage h1 { font-size: 24px; font-weight: 700; color: #0f172a; margin: 18px 0 10px; line-height: 1.25; }
      .word-page-stage h2 { font-size: 19px; font-weight: 700; color: #1e293b; margin: 15px 0 8px; line-height: 1.3; }
      .word-page-stage h3 { font-size: 16px; font-weight: 600; color: #334155; margin: 12px 0 6px; }
      .word-page-stage h4, .word-page-stage h5, .word-page-stage h6 { font-size: 14px; font-weight: 600; margin: 10px 0 4px; }
      .word-page-stage p { margin: 0 0 10px; line-height: 1.55; }
      .word-page-stage strong, .word-page-stage b { font-weight: 700; color: #0f172a; }
      .word-page-stage em, .word-page-stage i { font-style: italic; }
      .word-page-stage table { width: 100%; border-collapse: collapse; margin: 12px 0 16px; font-size: 13px; }
      .word-page-stage th, .word-page-stage td { border: 1px solid #cbd5e1; padding: 6px 10px; text-align: left; vertical-align: top; }
      .word-page-stage th { background: #f8fafc; font-weight: 600; color: #0f172a; }
      .word-page-stage tr:nth-child(even) td { background: #fbfcfe; }
      .word-page-stage ul, .word-page-stage ol { margin: 0 0 10px 24px; padding: 0; }
      .word-page-stage li { margin-bottom: 4px; line-height: 1.5; }
      .word-page-stage img { max-width: 100%; height: auto; display: block; margin: 12px auto; border-radius: 4px; }
      .word-page-stage blockquote { border-left: 3px solid #cbd5e1; margin: 10px 0; padding: 4px 14px; color: #475569; font-style: italic; }
      .word-page-stage pre, .word-page-stage code { background: #f1f5f9; font-family: monospace; font-size: 12.5px; border-radius: 3px; padding: 1px 4px; }
      .word-page-stage a { color: #10b981; text-decoration: underline; }
    `;
    document.head.appendChild(docStyles);

    // Preload all images
    const allImages = Array.from(parseHost.querySelectorAll('img'));
    await Promise.all(allImages.map(img => {
      if (img.complete) return Promise.resolve();
      return new Promise(res => { img.onload = res; img.onerror = res; });
    }));

    // Build pages array using block element distribution
    const rawBlocks = Array.from(parseHost.childNodes).filter(n => {
      if (n.nodeType === 3 && !n.textContent.trim()) return false;
      return true;
    }).map(n => {
      if (n.nodeType === 3) {
        const p = document.createElement('p');
        p.textContent = n.textContent;
        return p;
      }
      return n;
    });

    const pageStages = [];
    const maxContentHeight = 990; // Usable body height on 1123px A4 canvas (excluding margins & footer)

    function createNewPageStage() {
      const stage = document.createElement('div');
      stage.className = 'word-page-stage';
      stage.style.position = 'fixed';
      stage.style.left = '-9999px';
      stage.style.top = '0';
      stage.style.width = canvasW + 'px';
      stage.style.height = canvasH + 'px';
      stage.style.padding = '48px 54px';
      stage.style.boxSizing = 'border-box';
      stage.style.background = '#ffffff';
      stage.style.color = '#1e293b';
      stage.style.fontFamily = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif';
      stage.style.fontSize = '14px';
      stage.style.lineHeight = '1.6';
      stage.style.overflow = 'hidden';
      stage.style.display = 'flex';
      stage.style.flexDirection = 'column';
      stage.style.justifyContent = 'space-between';

      const bodyDiv = document.createElement('div');
      bodyDiv.className = 'word-page-body';
      bodyDiv.style.flex = '1';
      bodyDiv.style.overflow = 'hidden';

      const footerDiv = document.createElement('div');
      footerDiv.className = 'word-page-footer';
      footerDiv.style.height = '20px';
      footerDiv.style.display = 'flex';
      footerDiv.style.justifyContent = 'space-between';
      footerDiv.style.alignItems = 'center';
      footerDiv.style.borderTop = '1px solid #e2e8f0';
      footerDiv.style.fontSize = '11px';
      footerDiv.style.color = '#94a3b8';
      footerDiv.style.marginTop = '10px';

      stage.appendChild(bodyDiv);
      stage.appendChild(footerDiv);
      document.body.appendChild(stage);

      return { stage, bodyDiv, footerDiv };
    }

    let currentPage = createNewPageStage();
    pageStages.push(currentPage);

    for (let b = 0; b < rawBlocks.length; b++) {
      const block = rawBlocks[b];

      // If block is a multi-row table, check if rows can be cleanly split across pages
      if (block.tagName === 'TABLE') {
        const rows = Array.from(block.querySelectorAll('tr'));
        if (rows.length > 1) {
          const headerRow = block.querySelector('thead tr') || rows[0];
          let tableOnCurrentPage = document.createElement('table');
          tableOnCurrentPage.className = block.className;
          currentPage.bodyDiv.appendChild(tableOnCurrentPage);

          for (let r = 0; r < rows.length; r++) {
            const row = rows[r];
            tableOnCurrentPage.appendChild(row);

            if (currentPage.bodyDiv.scrollHeight > maxContentHeight && tableOnCurrentPage.rows.length > 1) {
              // Move this row to a new page
              tableOnCurrentPage.removeChild(row);
              currentPage = createNewPageStage();
              pageStages.push(currentPage);

              tableOnCurrentPage = document.createElement('table');
              tableOnCurrentPage.className = block.className;
              if (headerRow && row !== headerRow) {
                tableOnCurrentPage.appendChild(headerRow.cloneNode(true));
              }
              tableOnCurrentPage.appendChild(row);
              currentPage.bodyDiv.appendChild(tableOnCurrentPage);
            }
          }
          continue;
        }
      }

      // Normal block (heading, paragraph, list, image, etc.)
      currentPage.bodyDiv.appendChild(block);
      if (currentPage.bodyDiv.scrollHeight > maxContentHeight && currentPage.bodyDiv.childNodes.length > 1) {
        currentPage.bodyDiv.removeChild(block);
        currentPage = createNewPageStage();
        pageStages.push(currentPage);
        currentPage.bodyDiv.appendChild(block);
      }
    }

    // Set page footer numbers
    const totalWordPages = pageStages.length;
    const docDisplayName = file.name.replace(/\.[^/.]+$/, '');
    for (let pIdx = 0; pIdx < totalWordPages; pIdx++) {
      pageStages[pIdx].footerDiv.innerHTML = `<span>${escapeHtml(docDisplayName)}</span><span>Page ${pIdx + 1} of ${totalWordPages}</span>`;
    }

    // Clean up temporary host
    if (document.body.contains(parseHost)) document.body.removeChild(parseHost);

    // Visual Slide/Page-to-JPG-to-PDF Render Pipeline (identical to PowerPoint)
    if (onProgress) onProgress(50, `Rendering ${totalWordPages} page(s) to high-resolution visual PDF...`);
    let pdfDoc = null;

    try {
      if (window.html2canvas) {
        for (let pIdx = 0; pIdx < totalWordPages; pIdx++) {
          if (onProgress) onProgress(50 + Math.round((pIdx / totalWordPages) * 40), `Rendering page ${pIdx + 1} of ${totalWordPages}...`);
          const canvas = await html2canvas(pageStages[pIdx].stage, {
            width: canvasW,
            height: canvasH,
            scale: 2, // 2x High-DPI for razor-sharp typography and images
            useCORS: true,
            logging: false,
            backgroundColor: '#ffffff',
            windowWidth: canvasW
          });
          const pageJpg = canvas.toDataURL('image/jpeg', 0.95);

          if (pIdx === 0) {
            pdfDoc = new jsPDF({
              orientation: 'portrait',
              unit: 'pt',
              format: 'a4',
              hotfixes: ['px_scaling']
            });
            pdfDoc.addImage(pageJpg, 'JPEG', 0, 0, a4WidthPt, a4HeightPt);
          } else {
            pdfDoc.addPage('a4', 'portrait');
            pdfDoc.addImage(pageJpg, 'JPEG', 0, 0, a4WidthPt, a4HeightPt);
          }
        }
      } else {
        // Fallback
        pdfDoc = new jsPDF({ orientation: 'portrait', unit: 'pt', format: 'a4' });
        pdfDoc.setFontSize(12);
        pdfDoc.text('Document converted without html2canvas renderer.', 36, 40);
      }
    } finally {
      // Clean up all DOM page stages
      for (const p of pageStages) {
        if (p.stage && document.body.contains(p.stage)) {
          document.body.removeChild(p.stage);
        }
      }
      if (document.head.contains(docStyles)) {
        document.head.removeChild(docStyles);
      }
    }

    if (onProgress) onProgress(95, 'Finalizing complete PDF document...');
    const blob = pdfDoc.output('blob');
    return {
      blob,
      filename: file.name.replace(/\.[^/.]+$/, '') + '.pdf',
      summary: `Converted all ${totalWordPages} Word page(s) into high-resolution visual PDF without text clipping.`
    };
  }

  // ==========================================
  // TOOL 15: EXCEL -> PDF (High-Fidelity OpenXML & Visual Spreadsheet-to-PDF Engine)
  // ==========================================
  async function excelToPdf(file, onProgress) {
    if (!window.jspdf && !window.jsPDF) throw new Error('PDF library not loaded');
    if (onProgress) onProgress(10, 'Reading spreadsheet workbook...');

    let arrayBuffer;
    try {
      arrayBuffer = await readFileAsArrayBuffer(file);
    } catch (e) {
      throw new Error('Could not read spreadsheet file: ' + e.message);
    }

    const { jsPDF } = window.jspdf || window;

    // Helper: Parse XML string into DOM
    function parseXmlDoc(xmlStr) {
      return new DOMParser().parseFromString(xmlStr, 'application/xml');
    }

    // Helper: Split cell reference like "B2" into { col: 2, row: 2 }
    function splitCellRef(ref) {
      let colStr = '';
      let rowStr = '';
      for (let i = 0; i < ref.length; i++) {
        const ch = ref[i];
        if ((ch >= 'A' && ch <= 'Z') || (ch >= 'a' && ch <= 'z')) {
          colStr += ch.toUpperCase();
        } else {
          rowStr += ch;
        }
      }
      let c = 0;
      for (let i = 0; i < colStr.length; i++) {
        c = c * 26 + (colStr.charCodeAt(i) - 64);
      }
      return { col: c, row: parseInt(rowStr, 10) || 1 };
    }

    // Helper: Apply tint to hex color
    function applyTint(hex, tint) {
      if (!hex || !hex.startsWith('#') || hex.length < 7) return hex;
      let r = parseInt(hex.slice(1, 3), 16);
      let g = parseInt(hex.slice(3, 5), 16);
      let b = parseInt(hex.slice(5, 7), 16);
      if (tint > 0) {
        r = Math.round(r + (255 - r) * tint);
        g = Math.round(g + (255 - g) * tint);
        b = Math.round(b + (255 - b) * tint);
      } else if (tint < 0) {
        r = Math.round(r * (1 + tint));
        g = Math.round(g * (1 + tint));
        b = Math.round(b * (1 + tint));
      }
      return '#' + [r, g, b].map(x => Math.max(0, Math.min(255, x)).toString(16).padStart(2, '0')).join('');
    }

    // Helper: Parse OpenXML Excel (.xlsx) package
    async function parseOpenXmlExcel(zip) {
      try {
        // 1. Theme colors
        const themeColors = [
          '#000000', '#FFFFFF', '#0E2841', '#E8E8E8',
          '#156082', '#E97132', '#196B24', '#0F9ED5',
          '#A02B93', '#4EA72E', '#467886', '#96607D'
        ];
        const themeFile = zip.file('xl/theme/theme1.xml');
        if (themeFile) {
          const themeXml = await themeFile.async('string');
          const themeDoc = parseXmlDoc(themeXml);
          let idx = 0;
          const allClrs = Array.from(themeDoc.querySelectorAll('srgbClr, sysClr'));
          for (const clr of allClrs) {
            if (idx < themeColors.length) {
              const val = clr.getAttribute('val') || clr.getAttribute('lastClr');
              if (val) {
                themeColors[idx] = '#' + val;
                idx++;
              }
            }
          }
        }

        function resolveColor(cElem) {
          if (!cElem) return null;
          const rgb = cElem.getAttribute('rgb');
          if (rgb) {
            return '#' + (rgb.length === 8 ? rgb.substring(2) : rgb);
          }
          const theme = cElem.getAttribute('theme');
          if (theme !== null && theme !== undefined) {
            const tIdx = parseInt(theme, 10);
            if (tIdx >= 0 && tIdx < themeColors.length) {
              let baseClr = themeColors[tIdx];
              const tint = parseFloat(cElem.getAttribute('tint') || '0');
              if (tint !== 0 && baseClr && baseClr.startsWith('#')) {
                baseClr = applyTint(baseClr, tint);
              }
              return baseClr;
            }
          }
          return null;
        }

        // 2. Styles
        const stylesFile = zip.file('xl/styles.xml');
        if (!stylesFile) return null;
        const stylesXml = await stylesFile.async('string');
        const stylesDoc = parseXmlDoc(stylesXml);

        const numFmts = {};
        stylesDoc.querySelectorAll('numFmt').forEach(nf => {
          const id = parseInt(nf.getAttribute('numFmtId'), 10);
          const code = nf.getAttribute('formatCode');
          if (!isNaN(id) && code) numFmts[id] = code;
        });

        const fills = [];
        stylesDoc.querySelectorAll('fills > fill').forEach(f => {
          const pf = f.querySelector('patternFill');
          const patternType = pf ? pf.getAttribute('patternType') : 'none';
          const fg = pf ? pf.querySelector('fgColor') : null;
          fills.push({
            type: patternType,
            color: (patternType && patternType !== 'none') ? resolveColor(fg) : null
          });
        });

        const fonts = [];
        stylesDoc.querySelectorAll('fonts > font').forEach(f => {
          const nameEl = f.querySelector('name');
          const szEl = f.querySelector('sz');
          const bEl = f.querySelector('b');
          const iEl = f.querySelector('i');
          const uEl = f.querySelector('u');
          const colorEl = f.querySelector('color');
          fonts.push({
            name: nameEl ? nameEl.getAttribute('val') : 'Calibri',
            size: szEl ? parseFloat(szEl.getAttribute('val')) : 11,
            bold: !!bEl,
            italic: !!iEl,
            underline: !!uEl,
            color: resolveColor(colorEl) || '#000000'
          });
        });

        const borders = [];
        stylesDoc.querySelectorAll('borders > border').forEach(b => {
          const bInfo = {};
          ['left', 'right', 'top', 'bottom'].forEach(side => {
            const sideEl = b.querySelector(side);
            if (sideEl && sideEl.getAttribute('style')) {
              const cEl = sideEl.querySelector('color');
              bInfo[side] = {
                style: sideEl.getAttribute('style'),
                color: resolveColor(cEl) || '#d4d4d4'
              };
            } else {
              bInfo[side] = null;
            }
          });
          borders.push(bInfo);
        });

        const cellXfs = [];
        stylesDoc.querySelectorAll('cellXfs > xf').forEach(xf => {
          const alignEl = xf.querySelector('alignment');
          const align = {};
          if (alignEl) {
            align.h = alignEl.getAttribute('horizontal');
            align.v = alignEl.getAttribute('vertical');
            align.wrap = alignEl.getAttribute('wrapText') === '1';
          }
          cellXfs.push({
            numFmtId: parseInt(xf.getAttribute('numFmtId') || '0', 10),
            fontId: parseInt(xf.getAttribute('fontId') || '0', 10),
            fillId: parseInt(xf.getAttribute('fillId') || '0', 10),
            borderId: parseInt(xf.getAttribute('borderId') || '0', 10),
            align: align
          });
        });

        // 3. Shared Strings
        const sharedStrings = [];
        const ssFile = zip.file('xl/sharedStrings.xml');
        if (ssFile) {
          const ssXml = await ssFile.async('string');
          const ssDoc = parseXmlDoc(ssXml);
          ssDoc.querySelectorAll('si').forEach(si => {
            const tEl = si.querySelector('t');
            if (tEl && si.querySelectorAll('r').length === 0) {
              sharedStrings.push(tEl.textContent || '');
            } else {
              let fullText = '';
              si.querySelectorAll('t').forEach(t => { fullText += t.textContent || ''; });
              sharedStrings.push(fullText);
            }
          });
        }

        // 4. Sheets from Workbook
        const wbFile = zip.file('xl/workbook.xml');
        if (!wbFile) return null;
        const wbXml = await wbFile.async('string');
        const wbDoc = parseXmlDoc(wbXml);
        const sheetEntries = [];
        wbDoc.querySelectorAll('sheets > sheet').forEach(s => {
          sheetEntries.push({
            name: s.getAttribute('name') || 'Sheet1',
            sheetId: s.getAttribute('sheetId') || '1',
            rId: s.getAttribute('r:id') || s.getAttribute('id')
          });
        });

        const sheetFiles = Object.keys(zip.files).filter(p => p.startsWith('xl/worksheets/sheet') && p.endsWith('.xml'));
        if (sheetFiles.length === 0) return null;

        const parsedSheets = [];
        for (let sIdx = 0; sIdx < sheetFiles.length; sIdx++) {
          const sPath = sheetFiles[sIdx];
          const sheetName = sheetEntries[sIdx] ? sheetEntries[sIdx].name : `Sheet${sIdx + 1}`;
          const sXml = await zip.file(sPath).async('string');
          const sDoc = parseXmlDoc(sXml);

          const mergeMap = {};
          sDoc.querySelectorAll('mergeCells > mergeCell').forEach(mc => {
            const ref = mc.getAttribute('ref');
            if (ref && ref.includes(':')) {
              const [p1, p2] = ref.split(':');
              const from = splitCellRef(p1);
              const to = splitCellRef(p2);
              const rowspan = to.row - from.row + 1;
              const colspan = to.col - from.col + 1;
              mergeMap[`${from.row},${from.col}`] = { rowspan, colspan, origin: true };
              for (let r = from.row; r <= to.row; r++) {
                for (let c = from.col; c <= to.col; c++) {
                  if (r !== from.row || c !== from.col) {
                    mergeMap[`${r},${c}`] = { origin: false, hidden: true };
                  }
                }
              }
            }
          });

          const colWidths = {};
          sDoc.querySelectorAll('cols > col').forEach(c => {
            const min = parseInt(c.getAttribute('min'), 10);
            const max = parseInt(c.getAttribute('max'), 10);
            const w = parseFloat(c.getAttribute('width') || '9.1');
            for (let i = min; i <= max; i++) {
              colWidths[i] = w;
            }
          });

          const rowsData = {};
          let minCol = 9999, maxCol = 1;
          let minRow = 9999, maxRow = 1;

          sDoc.querySelectorAll('sheetData > row').forEach(r => {
            const rIdx = parseInt(r.getAttribute('r'), 10);
            if (isNaN(rIdx)) return;
            minRow = Math.min(minRow, rIdx);
            maxRow = Math.max(maxRow, rIdx);
            const ht = parseFloat(r.getAttribute('ht') || '20');
            const rowCells = {};

            r.querySelectorAll('c').forEach(c => {
              const ref = c.getAttribute('r');
              if (!ref) return;
              const { col, row } = splitCellRef(ref);
              minCol = Math.min(minCol, col);
              maxCol = Math.max(maxCol, col);
              const sIdx = parseInt(c.getAttribute('s') || '0', 10);
              const tType = c.getAttribute('t') || 'n';
              const vEl = c.querySelector('v');
              const rawV = vEl ? vEl.textContent : '';

              let displayV = rawV;
              if (tType === 's' && /^\d+$/.test(rawV)) {
                displayV = sharedStrings[parseInt(rawV, 10)] || '';
              } else if (tType === 'b') {
                displayV = rawV === '1' ? 'TRUE' : 'FALSE';
              } else {
                const xf = cellXfs[sIdx];
                const numId = xf ? xf.numFmtId : 0;
                const fmtCode = (numFmts[numId] || '').toLowerCase();
                if (numId === 14 || fmtCode.includes('yy') || fmtCode.includes('dd') || fmtCode.includes('mm')) {
                  const days = parseFloat(rawV);
                  if (!isNaN(days) && days > 0) {
                    const epoch = new Date(Date.UTC(1899, 11, 30));
                    const d = new Date(epoch.getTime() + days * 86400000);
                    const dd = String(d.getUTCDate()).padStart(2, '0');
                    const mm = String(d.getUTCMonth() + 1).padStart(2, '0');
                    const yyyy = d.getUTCFullYear();
                    displayV = `${dd}-${mm}-${yyyy}`;
                  }
                } else if (numId === 9 || fmtCode.includes('%')) {
                  const val = parseFloat(rawV);
                  if (!isNaN(val)) {
                    if (fmtCode.includes('.0') || fmtCode.includes('0.00%')) {
                      displayV = `${(val * 100).toFixed(1)}%`;
                    } else {
                      displayV = `${Math.round(val * 100)}%`;
                    }
                  }
                } else if (numId === 10) {
                  const val = parseFloat(rawV);
                  if (!isNaN(val)) {
                    displayV = `${(val * 100).toFixed(2)}%`;
                  }
                } else if (numId === 2 || numId === 4) {
                  const val = parseFloat(rawV);
                  if (!isNaN(val)) {
                    displayV = val.toFixed(2);
                  }
                }
              }

              rowCells[col] = {
                raw: rawV,
                val: displayV,
                sIdx: sIdx
              };
            });

            rowsData[rIdx] = { ht, cells: rowCells };
          });

          // Continuous center spanning (centerContinuous)
          for (const rIdxStr of Object.keys(rowsData)) {
            const rIdx = parseInt(rIdxStr, 10);
            const rObj = rowsData[rIdx];
            const cells = rObj.cells;
            const cKeys = Object.keys(cells).map(k => parseInt(k, 10)).sort((a, b) => a - b);
            let idx = 0;
            while (idx < cKeys.length) {
              const cIdx = cKeys[idx];
              const cell = cells[cIdx];
              const xf = cellXfs[cell.sIdx];
              if (xf && xf.align && xf.align.h === 'centerContinuous' && cell.val) {
                let span = 1;
                while (idx + span < cKeys.length) {
                  const nextC = cKeys[idx + span];
                  if (nextC === cIdx + span) {
                    const nextCell = cells[nextC];
                    const nextXf = cellXfs[nextCell.sIdx];
                    if (nextXf && nextXf.align && nextXf.align.h === 'centerContinuous' && !nextCell.val) {
                      span++;
                    } else {
                      break;
                    }
                  } else {
                    break;
                  }
                }
                if (span > 1) {
                  mergeMap[`${rIdx},${cIdx}`] = { rowspan: 1, colspan: span, origin: true };
                  for (let k = 1; k < span; k++) {
                    mergeMap[`${rIdx},${cIdx + k}`] = { origin: false, hidden: true };
                  }
                  idx += span;
                  continue;
                }
              }
              idx++;
            }
          }

          // Identify table column header row (row with >= 3 non-empty cells)
          let tableStartRow = minRow;
          for (let r = minRow; r <= Math.min(maxRow, minRow + 15); r++) {
            const rObj = rowsData[r];
            if (rObj) {
              const nonEmptyCount = Object.values(rObj.cells).filter(c => c && c.val && String(c.val).trim() !== '').length;
              if (nonEmptyCount >= 3) {
                tableStartRow = r;
                break;
              }
            }
          }

          let firstCol = minCol;
          if ((colWidths[firstCol] || 10) < 6) {
            let hasContent = false;
            for (let r = minRow; r <= maxRow; r++) {
              if (rowsData[r] && rowsData[r].cells[firstCol] && rowsData[r].cells[firstCol].val) {
                hasContent = true;
                break;
              }
            }
            if (!hasContent) firstCol = minCol + 1;
          }

          let lastCol = maxCol;
          while (lastCol > firstCol) {
            let hasContent = false;
            for (let r = minRow; r <= maxRow; r++) {
              if (rowsData[r] && rowsData[r].cells[lastCol] && rowsData[r].cells[lastCol].val) {
                hasContent = true;
                break;
              }
            }
            if (hasContent) break;
            lastCol--;
          }

          parsedSheets.push({
            name: sheetName,
            minRow, maxRow, minCol, maxCol,
            firstCol, lastCol, tableStartRow,
            colWidths, rowsData, mergeMap,
            cellXfs, fonts, fills, borders
          });
        }

        return parsedSheets;
      } catch (e) {
        console.warn('OpenXML parser encountered an issue, falling back:', e);
        return null;
      }
    }

    // Helper: Render an individual row of an OpenXML parsed sheet to HTML
    function renderSheetRowHtml(sheet, r) {
      const rObj = sheet.rowsData[r];
      const rHt = rObj ? rObj.ht : 20;
      const totalCols = sheet.lastCol - sheet.firstCol + 1;

      // If empty spacer row before data table, render clean blank row without vertical gridlines
      if (r < sheet.tableStartRow) {
        const hasContent = rObj && Object.values(rObj.cells).some(c => c && c.val && String(c.val).trim() !== '');
        if (!hasContent) {
          return `<tr style="height: ${rHt.toFixed(1)}pt;"><td colspan="${totalCols}" style="border: none; padding: 0;"></td></tr>`;
        }
      }

      let html = `<tr style="height: ${rHt.toFixed(1)}pt;">`;
      let c = sheet.firstCol;
      while (c <= sheet.lastCol) {
        const mKey = `${r},${c}`;
        const mInfo = sheet.mergeMap[mKey];
        if (mInfo && mInfo.hidden) {
          c++;
          continue;
        }

        const rowspanAttr = (mInfo && mInfo.rowspan > 1) ? ` rowspan="${mInfo.rowspan}"` : '';
        const colspanAttr = (mInfo && mInfo.colspan > 1) ? ` colspan="${mInfo.colspan}"` : '';

        const cell = (rObj && rObj.cells) ? rObj.cells[c] : null;
        const val = cell ? cell.val : '';
        const sIdx = cell ? cell.sIdx : 0;
        const xf = sheet.cellXfs[sIdx];

        const styles = ['box-sizing: border-box;', 'padding: 4px 6px;', 'line-height: 1.2;'];

        if (xf) {
          const font = sheet.fonts[xf.fontId];
          if (font) {
            styles.push(`font-family: '${font.name}', Calibri, sans-serif;`);
            styles.push(`font-size: ${font.size}pt;`);
            if (font.bold) styles.push('font-weight: 700;');
            if (font.italic) styles.push('font-style: italic;');
            if (font.color) styles.push(`color: ${font.color};`);
          }

          const fill = sheet.fills[xf.fillId];
          if (fill && fill.color) {
            styles.push(`background-color: ${fill.color};`);
          }

          const align = xf.align || {};
          if (align.h === 'center' || align.h === 'centerContinuous') {
            styles.push('text-align: center;');
          } else if (align.h === 'right') {
            styles.push('text-align: right;');
          } else if (align.h === 'left') {
            styles.push('text-align: left;');
          } else {
            if (val && (val.endsWith('%') || /^-?\d+(\.\d+)?$/.test(val))) {
              styles.push('text-align: right;');
            } else if (val && /^\d{2}-\d{2}-\d{4}$/.test(val)) {
              styles.push('text-align: center;');
            } else {
              styles.push('text-align: left;');
            }
          }

          styles.push('vertical-align: middle;');

          const border = sheet.borders[xf.borderId];
          if (border) {
            ['top', 'bottom', 'left', 'right'].forEach(side => {
              const bSide = border[side];
              if (bSide && bSide.style) {
                const wPx = (bSide.style === 'medium' || bSide.style === 'thick') ? '2px' : '1px';
                styles.push(`border-${side}: ${wPx} solid ${bSide.color || '#d4d4d4'};`);
              } else if (r >= sheet.tableStartRow) {
                styles.push(`border-${side}: 1px solid #d4d4d4;`);
              } else {
                styles.push(`border-${side}: none;`);
              }
            });
          } else if (r >= sheet.tableStartRow) {
            styles.push('border: 1px solid #d4d4d4;');
          } else {
            styles.push('border: none;');
          }
        } else if (r >= sheet.tableStartRow) {
          styles.push('border: 1px solid #d4d4d4;');
        } else {
          styles.push('border: none;');
        }

        html += `<td${rowspanAttr}${colspanAttr} style="${styles.join(' ')}">${escapeHtml(val)}</td>`;

        if (mInfo && mInfo.colspan > 1) {
          c += mInfo.colspan;
        } else {
          c++;
        }
      }
      html += '</tr>';
      return html;
    }

    // Try parsing using high-fidelity OpenXML parser
    let openXmlSheets = null;
    if (window.JSZip) {
      try {
        const zip = await JSZip.loadAsync(arrayBuffer);
        openXmlSheets = await parseOpenXmlExcel(zip);
      } catch (zipErr) {
        // Not a valid zip (e.g. .xls binary or .csv)
        openXmlSheets = null;
      }
    }

    const sheetPageStages = [];
    const canvasW = 1123;
    const canvasH = 794;
    const pageWidthPt = 841.89;
    const pageHeightPt = 595.28;

    if (openXmlSheets && openXmlSheets.length > 0) {
      // -------------------------------------------------------------
      // PRIMARY PIPELINE: High-Fidelity OpenXML Layout & Styles Engine
      // -------------------------------------------------------------
      if (onProgress) onProgress(30, 'Formatting authentic Excel layout and styles...');

      for (let s = 0; s < openXmlSheets.length; s++) {
        const sheet = openXmlSheets[s];
        if (sheet.maxRow < sheet.minRow || Object.keys(sheet.rowsData).length === 0) continue;

        // Partition rows into pages (Target usable height ~480pt or ~28 rows)
        const MAX_PAGE_HT_PT = 480;
        const pages = [];
        let currPageRows = [];
        let currHt = 0;

        // Page 1 gets header/banner rows up to tableStartRow
        for (let r = sheet.minRow; r <= sheet.tableStartRow; r++) {
          currPageRows.push(r);
          const rObj = sheet.rowsData[r];
          currHt += (rObj ? rObj.ht : 20);
        }

        // Paginate remaining data rows
        for (let r = sheet.tableStartRow + 1; r <= sheet.maxRow; r++) {
          const rObj = sheet.rowsData[r];
          const ht = rObj ? rObj.ht : 20;

          if (currPageRows.length > 0 && (currHt + ht > MAX_PAGE_HT_PT || currPageRows.length >= 28)) {
            pages.push(currPageRows);
            currPageRows = [];
            currHt = 0;
            if (sheet.tableStartRow) {
              const hdrObj = sheet.rowsData[sheet.tableStartRow];
              currHt += (hdrObj ? hdrObj.ht : 20);
            }
          }

          currPageRows.push(r);
          currHt += ht;
        }
        if (currPageRows.length > 0) {
          pages.push(currPageRows);
        }

        for (let p = 0; p < pages.length; p++) {
          const pageRowIndices = pages[p];
          const stage = document.createElement('div');
          stage.className = 'excel-render-stage';
          stage.style.position = 'fixed';
          stage.style.left = '-9999px';
          stage.style.top = '0';
          stage.style.width = canvasW + 'px';
          stage.style.height = canvasH + 'px';
          stage.style.boxSizing = 'border-box';
          stage.style.background = '#ffffff';
          stage.style.padding = '36px 40px';
          stage.style.display = 'flex';
          stage.style.flexDirection = 'column';
          stage.style.alignItems = 'center';
          stage.style.overflow = 'hidden';

          let tableHtml = '<table style="border-collapse: collapse; margin: 0 auto; table-layout: fixed;">';
          tableHtml += '<colgroup>';
          for (let c = sheet.firstCol; c <= sheet.lastCol; c++) {
            const cw = (sheet.colWidths[c] || 12) * 7.5;
            tableHtml += `<col style="width: ${cw.toFixed(1)}px;">`;
          }
          tableHtml += '</colgroup>';

          // Repeat column header on continuation pages
          if (p > 0 && sheet.tableStartRow && !pageRowIndices.includes(sheet.tableStartRow)) {
            tableHtml += renderSheetRowHtml(sheet, sheet.tableStartRow);
          }

          for (const rowIdx of pageRowIndices) {
            tableHtml += renderSheetRowHtml(sheet, rowIdx);
          }
          tableHtml += '</table>';

          stage.innerHTML = tableHtml;
          document.body.appendChild(stage);
          sheetPageStages.push(stage);
        }
      }
    } else {
      // -------------------------------------------------------------
      // FALLBACK PIPELINE: Enhanced SheetJS Engine for CSV / legacy .XLS
      // -------------------------------------------------------------
      if (!window.XLSX) throw new Error('Spreadsheet library XLSX is not available');
      if (onProgress) onProgress(30, 'Reading spreadsheet via fallback engine...');

      const wb = XLSX.read(arrayBuffer, { type: 'array', cellDates: true, cellNF: true });
      if (!wb.SheetNames || wb.SheetNames.length === 0) {
        throw new Error('No worksheets found in this spreadsheet.');
      }

      const ROWS_PER_PAGE = 25;
      for (let s = 0; s < wb.SheetNames.length; s++) {
        const sheetName = wb.SheetNames[s];
        const sheet = wb.Sheets[sheetName];
        const rawRows = XLSX.utils.sheet_to_json(sheet, { header: 1, defval: '', raw: false });
        const validRows = rawRows.filter(row => row && row.some(c => c !== null && c !== undefined && String(c).trim() !== ''));

        if (validRows.length === 0) continue;

        const headerRow = validRows[0];
        const dataRows = validRows.slice(1);
        const colCount = Math.max(...validRows.map(r => r.length));
        const totalPages = Math.max(1, Math.ceil(dataRows.length / ROWS_PER_PAGE));

        for (let pIdx = 0; pIdx < totalPages; pIdx++) {
          const startR = pIdx * ROWS_PER_PAGE;
          const pageData = dataRows.slice(startR, startR + ROWS_PER_PAGE);

          const stage = document.createElement('div');
          stage.className = 'excel-render-stage';
          stage.style.position = 'fixed';
          stage.style.left = '-9999px';
          stage.style.top = '0';
          stage.style.width = canvasW + 'px';
          stage.style.height = canvasH + 'px';
          stage.style.boxSizing = 'border-box';
          stage.style.background = '#ffffff';
          stage.style.padding = '36px 40px';
          stage.style.display = 'flex';
          stage.style.flexDirection = 'column';
          stage.style.overflow = 'hidden';

          let ths = '<tr>';
          for (let c = 0; c < colCount; c++) {
            ths += `<th style="border: 1px solid #cbd5e1; background: #f8fafc; padding: 6px 8px; font-weight: bold; text-align: left; font-family: Calibri, sans-serif; font-size: 11pt;">${escapeHtml(headerRow[c] || '')}</th>`;
          }
          ths += '</tr>';

          let trs = '';
          for (let r = 0; r < pageData.length; r++) {
            trs += '<tr>';
            for (let c = 0; c < colCount; c++) {
              trs += `<td style="border: 1px solid #e2e8f0; padding: 5px 8px; font-family: Calibri, sans-serif; font-size: 10pt;">${escapeHtml(pageData[r][c] || '')}</td>`;
            }
            trs += '</tr>';
          }

          stage.innerHTML = `
            <table style="width: 100%; border-collapse: collapse; table-layout: auto;">
              <thead>${ths}</thead>
              <tbody>${trs}</tbody>
            </table>
          `;
          document.body.appendChild(stage);
          sheetPageStages.push(stage);
        }
      }
    }

    if (sheetPageStages.length === 0) {
      throw new Error('Spreadsheet contains no printable worksheets or rows.');
    }

    // High-DPI Visual Sheet-to-JPG-to-PDF Render Pipeline
    const totalPages = sheetPageStages.length;
    if (onProgress) onProgress(50, `Rendering ${totalPages} spreadsheet page(s) to visual PDF...`);
    let pdfDoc = null;

    try {
      if (window.html2canvas) {
        for (let pIdx = 0; pIdx < totalPages; pIdx++) {
          if (onProgress) onProgress(50 + Math.round((pIdx / totalPages) * 45), `Rendering page ${pIdx + 1} of ${totalPages}...`);
          const canvas = await html2canvas(sheetPageStages[pIdx], {
            width: canvasW,
            height: canvasH,
            scale: 2,
            useCORS: true,
            logging: false,
            backgroundColor: '#ffffff',
            windowWidth: canvasW
          });
          const pageJpg = canvas.toDataURL('image/jpeg', 0.95);

          if (pIdx === 0) {
            pdfDoc = new jsPDF({
              orientation: 'landscape',
              unit: 'pt',
              format: 'a4',
              hotfixes: ['px_scaling']
            });
            pdfDoc.addImage(pageJpg, 'JPEG', 0, 0, pageWidthPt, pageHeightPt);
          } else {
            pdfDoc.addPage('a4', 'landscape');
            pdfDoc.addImage(pageJpg, 'JPEG', 0, 0, pageWidthPt, pageHeightPt);
          }
        }
      } else {
        pdfDoc = new jsPDF({ orientation: 'landscape', unit: 'pt', format: 'a4' });
        pdfDoc.setFontSize(12);
        pdfDoc.text('Spreadsheet converted without html2canvas renderer.', 30, 40);
      }
    } finally {
      for (const st of sheetPageStages) {
        if (st && document.body.contains(st)) {
          document.body.removeChild(st);
        }
      }
    }

    if (onProgress) onProgress(98, 'Finalizing complete PDF document...');
    const blob = pdfDoc.output('blob');
    return {
      blob,
      filename: file.name.replace(/\.[^/.]+$/, '') + '.pdf',
      summary: `Converted all ${totalPages} spreadsheet page(s) into high-resolution visual landscape PDF.`
    };
  }

  // ==========================================
  // TOOL 16: POWERPOINT -> PDF (Visual Slide-to-JPG-to-PDF Engine)
  // ==========================================
  async function powerPointToPdf(file) {
    if (!window.jsPDF && !window.jspdf) throw new Error('PDF library not loaded');
    const { jsPDF } = window.jspdf;
    if (!window.JSZip) throw new Error('JSZip library not loaded');

    let arrayBuffer;
    try {
      arrayBuffer = await readFileAsArrayBuffer(file);
    } catch (e) {
      throw new Error('Could not read presentation file: ' + e.message);
    }

    let zip;
    try {
      zip = await JSZip.loadAsync(arrayBuffer);
    } catch (e) {
      throw new Error('Please upload a PowerPoint presentation in .pptx format. Older .ppt binary files are not supported.');
    }

    // Helper: Find XML elements regardless of namespaces
    function findXmlElements(parent, tagName) {
      if (!parent) return [];
      let found = [];
      if (parent.getElementsByTagNameNS) {
        try {
          found = Array.from(parent.getElementsByTagNameNS('*', tagName));
          if (found.length) return found;
        } catch (e) {}
      }
      if (parent.getElementsByTagName) {
        found = Array.from(parent.getElementsByTagName('p:' + tagName))
          .concat(Array.from(parent.getElementsByTagName('a:' + tagName)))
          .concat(Array.from(parent.getElementsByTagName(tagName)));
      }
      return found;
    }

    // Load all embedded media images from ppt/media/
    const mediaMap = {};
    const mediaFiles = Object.keys(zip.files).filter(name => name.startsWith('ppt/media/'));
    for (const mName of mediaFiles) {
      const ext = mName.split('.').pop().toLowerCase();
      const mime = (ext === 'png') ? 'image/png' : (ext === 'jpg' || ext === 'jpeg') ? 'image/jpeg' : (ext === 'svg') ? 'image/svg+xml' : 'image/png';
      const base64 = await zip.files[mName].async('base64');
      mediaMap[mName.replace('ppt/', '')] = `data:${mime};base64,${base64}`;
    }

    // Check presentation slide size in ppt/presentation.xml (EMUs)
    let slideWidthEmu = 9144000;  // default 16:9 widescreen: 10 inches
    let slideHeightEmu = 5143500; // 5.625 inches
    if (zip.files['ppt/presentation.xml']) {
      try {
        const presXml = await zip.files['ppt/presentation.xml'].async('text');
        const presDoc = new DOMParser().parseFromString(presXml, 'application/xml');
        const sldSzList = findXmlElements(presDoc, 'sldSz');
        if (sldSzList.length > 0) {
          const sz = sldSzList[0];
          const cx = parseInt(sz.getAttribute('cx'), 10);
          const cy = parseInt(sz.getAttribute('cy'), 10);
          if (cx && cy) {
            slideWidthEmu = cx;
            slideHeightEmu = cy;
          }
        }
      } catch (e) {
        console.warn('Could not parse ppt/presentation.xml dimensions', e);
      }
    }

    // Canvas dimensions based on aspect ratio
    const canvasW = 1280;
    const canvasH = Math.max(300, Math.round((slideHeightEmu / slideWidthEmu) * canvasW));

    // Default theme color scheme (Office Theme defaults)
    const themeColors = {
      'dk1': '000000',
      'lt1': 'ffffff',
      'dk2': '1f497d',
      'lt2': 'eeece1',
      'accent1': '4f81bd',
      'accent2': 'c0504d',
      'accent3': '9bbb59',
      'accent4': '8064a2',
      'accent5': '4bacc6',
      'accent6': 'f79646',
      'hlink': '0000ff',
      'folHlink': '800080'
    };
    themeColors['bg1'] = themeColors['lt1'];
    themeColors['bg2'] = themeColors['lt2'];
    themeColors['tx1'] = themeColors['dk1'];
    themeColors['tx2'] = themeColors['dk2'];

    // Discover and parse theme XML if available
    const themeFile = Object.keys(zip.files).find(name => name.startsWith('ppt/theme/theme') && name.endsWith('.xml'));
    if (themeFile) {
      try {
        const themeXml = await zip.files[themeFile].async('text');
        const themeDoc = new DOMParser().parseFromString(themeXml, 'application/xml');
        const clrScheme = findXmlElements(themeDoc, 'clrScheme');
        if (clrScheme.length > 0) {
          const schemeNode = clrScheme[0];
          const colorKeys = ['dk1', 'lt1', 'dk2', 'lt2', 'accent1', 'accent2', 'accent3', 'accent4', 'accent5', 'accent6', 'hlink', 'folHlink'];
          for (const key of colorKeys) {
            const el = findXmlElements(schemeNode, key);
            if (el.length > 0) {
              const srgb = findXmlElements(el[0], 'srgbClr');
              if (srgb.length && srgb[0].getAttribute('val')) {
                themeColors[key] = srgb[0].getAttribute('val');
              } else {
                const sys = findXmlElements(el[0], 'sysClr');
                if (sys.length && sys[0].getAttribute('lastClr')) {
                  themeColors[key] = sys[0].getAttribute('lastClr');
                }
              }
            }
          }
          themeColors['bg1'] = themeColors['lt1'];
          themeColors['bg2'] = themeColors['lt2'];
          themeColors['tx1'] = themeColors['dk1'];
          themeColors['tx2'] = themeColors['dk2'];
        }
      } catch (e) {
        console.warn('Could not parse ppt/theme XML', e);
      }
    }

    // Helper: Extract color hex from any DrawingML color container (srgbClr, schemeClr, sysClr, prstClr)
    function extractColor(node) {
      if (!node) return null;
      if (findXmlElements(node, 'noFill').length > 0) return null;

      const srgbList = findXmlElements(node, 'srgbClr');
      if (srgbList.length > 0 && srgbList[0].getAttribute('val')) {
        return '#' + srgbList[0].getAttribute('val');
      }

      const schemeList = findXmlElements(node, 'schemeClr');
      if (schemeList.length > 0 && schemeList[0].getAttribute('val')) {
        const sVal = schemeList[0].getAttribute('val');
        if (themeColors[sVal]) {
          return '#' + themeColors[sVal];
        }
      }

      const sysList = findXmlElements(node, 'sysClr');
      if (sysList.length > 0) {
        const lastClr = sysList[0].getAttribute('lastClr');
        if (lastClr) return '#' + lastClr;
        const sVal = sysList[0].getAttribute('val');
        if (sVal === 'window') return '#ffffff';
        if (sVal === 'windowText') return '#000000';
      }

      const prstList = findXmlElements(node, 'prstClr');
      if (prstList.length > 0 && prstList[0].getAttribute('val')) {
        const pMap = {
          'black': '#000000', 'white': '#ffffff', 'red': '#ff0000', 'green': '#008000',
          'blue': '#0000ff', 'yellow': '#ffff00', 'cyan': '#00ffff', 'magenta': '#ff00ff',
          'gray': '#808080', 'grey': '#808080', 'lightgray': '#d3d3d3', 'darkgray': '#a9a9a9'
        };
        const pVal = prstList[0].getAttribute('val').toLowerCase();
        if (pMap[pVal]) return pMap[pVal];
      }

      return null;
    }

    // Helper: Perceived luminance checker
    function isColorDark(hex) {
      if (!hex || typeof hex !== 'string' || !hex.startsWith('#')) return false;
      let c = hex.substring(1);
      if (c.length === 3) c = c[0] + c[0] + c[1] + c[1] + c[2] + c[2];
      if (c.length !== 6) return false;
      const r = parseInt(c.substring(0, 2), 16) || 0;
      const g = parseInt(c.substring(2, 4), 16) || 0;
      const b = parseInt(c.substring(4, 6), 16) || 0;
      return ((r * 299 + g * 587 + b * 114) / 1000) < 130;
    }

    // Discover all slide XML files
    const slideFiles = Object.keys(zip.files).filter(name => 
      name.startsWith('ppt/slides/slide') && name.endsWith('.xml') && !name.includes('/') == false
    );
    slideFiles.sort((a, b) => {
      const numA = parseInt(a.replace(/[^0-9]/g, ''), 10) || 0;
      const numB = parseInt(b.replace(/[^0-9]/g, ''), 10) || 0;
      return numA - numB;
    });

    if (slideFiles.length === 0) {
      throw new Error('No presentation slides found. Please make sure this is a valid PowerPoint .pptx deck.');
    }

    const emuToPxX = (emu) => (emu / slideWidthEmu) * canvasW;
    const emuToPxY = (emu) => (emu / slideHeightEmu) * canvasH;
    const slideJpgs = [];

    for (let sIdx = 0; sIdx < slideFiles.length; sIdx++) {
      const slidePath = slideFiles[sIdx];
      const relsPath = slidePath.replace('ppt/slides/', 'ppt/slides/_rels/') + '.rels';

      // Parse slide relationships for media links
      const relsMap = {};
      if (zip.files[relsPath]) {
        try {
          const relsXml = await zip.files[relsPath].async('text');
          const relsDoc = new DOMParser().parseFromString(relsXml, 'application/xml');
          const relEls = findXmlElements(relsDoc, 'Relationship');
          for (let r = 0; r < relEls.length; r++) {
            const id = relEls[r].getAttribute('Id');
            const target = relEls[r].getAttribute('Target');
            if (id && target) {
              relsMap[id] = target.replace('../', '');
            }
          }
        } catch (e) {
          console.warn('Could not parse relationships for ' + slidePath, e);
        }
      }

      const slideXml = await zip.files[slidePath].async('text');
      const slideDoc = new DOMParser().parseFromString(slideXml, 'application/xml');

      // Detect slide background color
      let bgColor = '#ffffff';
      const bgPrList = findXmlElements(slideDoc, 'bgPr');
      const bgList = findXmlElements(slideDoc, 'bg');
      const bgRoot = bgPrList.length ? bgPrList[0] : bgList.length ? bgList[0] : null;
      if (bgRoot) {
        const clr = extractColor(bgRoot);
        if (clr) bgColor = clr;
      }
      const isDarkSlide = isColorDark(bgColor);
      const defaultSlideTextColor = isDarkSlide ? '#f8fafc' : '#0f172a';

      // High-Fidelity Slide Render (DOM + html2canvas for 100% layout and font preservation)
      let slideJpgDataUrl = null;

      if (window.html2canvas) {
        let slideStage = null;
        try {
          slideStage = document.createElement('div');
          slideStage.style.position = 'fixed';
          slideStage.style.left = '-9999px';
          slideStage.style.top = '0';
          slideStage.style.width = canvasW + 'px';
          slideStage.style.height = canvasH + 'px';
          slideStage.style.backgroundColor = bgColor;
          slideStage.style.overflow = 'hidden';
          slideStage.style.boxSizing = 'border-box';

          // 1. Shapes and Text Frames (<p:sp>)
          const shapes = findXmlElements(slideDoc, 'sp');
          for (let s = 0; s < shapes.length; s++) {
            const sp = shapes[s];
            const xfrmList = findXmlElements(sp, 'xfrm');
            let x = 40, y = 40, w = canvasW - 80, h = 60;
            if (xfrmList.length > 0) {
              const xfrm = xfrmList[0];
              const offList = findXmlElements(xfrm, 'off');
              const extList = findXmlElements(xfrm, 'ext');
              if (offList.length && extList.length) {
                x = emuToPxX(parseInt(offList[0].getAttribute('x'), 10) || 0);
                y = emuToPxY(parseInt(offList[0].getAttribute('y'), 10) || 0);
                w = emuToPxX(parseInt(extList[0].getAttribute('cx'), 10) || 0);
                h = emuToPxY(parseInt(extList[0].getAttribute('cy'), 10) || 0);
              }
            }

            const shapeDiv = document.createElement('div');
            shapeDiv.style.position = 'absolute';
            shapeDiv.style.left = x + 'px';
            shapeDiv.style.top = y + 'px';
            shapeDiv.style.width = w + 'px';
            shapeDiv.style.height = h + 'px';
            shapeDiv.style.boxSizing = 'border-box';
            shapeDiv.style.padding = '4px 6px';

            // Shape Fill, Border and Geometry
            let shapeBgColor = null;
            const spPrList = findXmlElements(sp, 'spPr');
            if (spPrList.length > 0) {
              const spPr = spPrList[0];

              // Solid fill
              const solidFillList = findXmlElements(spPr, 'solidFill');
              if (solidFillList.length > 0) {
                const fillClr = extractColor(solidFillList[0]);
                if (fillClr) {
                  shapeBgColor = fillClr;
                  shapeDiv.style.backgroundColor = fillClr;
                }
              }

              // Shape border outline - ONLY apply if explicitly defined with solid fill and color!
              // NEVER default border to #94a3b8!
              const lnList = findXmlElements(spPr, 'ln');
              if (lnList.length > 0) {
                const lnEl = lnList[0];
                const noFillList = findXmlElements(lnEl, 'noFill');
                if (noFillList.length === 0) {
                  const lnSolid = findXmlElements(lnEl, 'solidFill');
                  if (lnSolid.length > 0) {
                    const borderClr = extractColor(lnSolid[0]);
                    if (borderClr) {
                      let lnWidth = 1;
                      if (lnEl.getAttribute('w')) {
                        lnWidth = Math.max(1, Math.round(emuToPxX(parseInt(lnEl.getAttribute('w'), 10) || 12700)));
                      }
                      shapeDiv.style.border = `${lnWidth}px solid ${borderClr}`;
                    }
                  }
                }
              }

              const geomList = findXmlElements(spPr, 'prstGeom');
              if (geomList.length > 0) {
                const prst = geomList[0].getAttribute('prst');
                if (prst === 'roundRect') shapeDiv.style.borderRadius = '10px';
                else if (prst === 'ellipse') shapeDiv.style.borderRadius = '50%';
              }
            }

            // Determine active text color for this shape
            const activeShapeBg = shapeBgColor || bgColor;
            const shapeDefaultTextColor = isColorDark(activeShapeBg) ? '#f8fafc' : '#0f172a';

            // Vertical Alignment
            const bodyPrList = findXmlElements(sp, 'bodyPr');
            let vAnchor = 't';
            if (bodyPrList.length > 0 && bodyPrList[0].getAttribute('anchor')) {
              vAnchor = bodyPrList[0].getAttribute('anchor');
            }
            shapeDiv.style.display = 'flex';
            shapeDiv.style.flexDirection = 'column';
            shapeDiv.style.justifyContent = (vAnchor === 'ctr' ? 'center' : vAnchor === 'b' ? 'flex-end' : 'flex-start');

            // Text formatting
            const txBodyList = findXmlElements(sp, 'txBody');
            if (txBodyList.length > 0) {
              const paragraphs = findXmlElements(txBodyList[0], 'p');
              for (let p = 0; p < paragraphs.length; p++) {
                const pEl = paragraphs[p];
                const pPrList = findXmlElements(pEl, 'pPr');
                const align = (pPrList.length && pPrList[0].getAttribute('algn')) ? pPrList[0].getAttribute('algn') : 'l';

                const pDiv = document.createElement('div');
                pDiv.style.textAlign = (align === 'ctr' ? 'center' : align === 'r' ? 'right' : align === 'just' ? 'justify' : 'left');
                pDiv.style.margin = '0 0 4px 0';
                pDiv.style.padding = '0';
                pDiv.style.lineHeight = '1.3';
                pDiv.style.wordBreak = 'break-word';

                const runs = pEl.childNodes;
                for (let r = 0; r < runs.length; r++) {
                  const node = runs[r];
                  const nodeName = node.nodeName.toLowerCase();
                  if (nodeName.endsWith('r')) {
                    const tList = findXmlElements(node, 't');
                    const rText = tList.length ? tList[0].textContent : '';
                    if (rText) {
                      const span = document.createElement('span');
                      span.textContent = rText;

                      const rPrList = findXmlElements(node, 'rPr');
                      let fontSizePx = Math.round(18 * (canvasW / 1280));
                      let isBold = false;
                      let isItalic = false;
                      let textColor = shapeDefaultTextColor;
                      let fontFamily = 'Segoe UI, -apple-system, sans-serif';

                      if (rPrList.length > 0) {
                        const rPr = rPrList[0];
                        if (rPr.getAttribute('sz')) {
                          fontSizePx = Math.round((parseInt(rPr.getAttribute('sz'), 10) / 100) * 1.333 * (canvasW / 1280));
                        }
                        if (rPr.getAttribute('b') === '1' || rPr.getAttribute('b') === 'true') isBold = true;
                        if (rPr.getAttribute('i') === '1' || rPr.getAttribute('i') === 'true') isItalic = true;

                        const clr = extractColor(rPr);
                        if (clr) textColor = clr;

                        const latinList = findXmlElements(rPr, 'latin');
                        if (latinList.length && latinList[0].getAttribute('typeface')) {
                          fontFamily = `"${latinList[0].getAttribute('typeface')}", Segoe UI, sans-serif`;
                        }
                      }

                      span.style.fontSize = Math.max(10, fontSizePx) + 'px';
                      span.style.fontWeight = isBold ? '700' : '400';
                      if (isItalic) span.style.fontStyle = 'italic';
                      span.style.color = textColor;
                      span.style.fontFamily = fontFamily;
                      pDiv.appendChild(span);
                    }
                  } else if (nodeName.endsWith('br')) {
                    pDiv.appendChild(document.createElement('br'));
                  }
                }
                shapeDiv.appendChild(pDiv);
              }
            }
            slideStage.appendChild(shapeDiv);
          }

          // 2. Graphic Frames & Tables (<p:graphicFrame> & <a:tbl>)
          const graphicFrames = findXmlElements(slideDoc, 'graphicFrame');
          for (let g = 0; g < graphicFrames.length; g++) {
            const gf = graphicFrames[g];
            const xfrmList = findXmlElements(gf, 'xfrm');
            let gx = 40, gy = 40, gw = canvasW - 80, gh = 200;
            if (xfrmList.length > 0) {
              const offList = findXmlElements(xfrmList[0], 'off');
              const extList = findXmlElements(xfrmList[0], 'ext');
              if (offList.length && extList.length) {
                gx = emuToPxX(parseInt(offList[0].getAttribute('x'), 10) || 0);
                gy = emuToPxY(parseInt(offList[0].getAttribute('y'), 10) || 0);
                gw = emuToPxX(parseInt(extList[0].getAttribute('cx'), 10) || 0);
                gh = emuToPxY(parseInt(extList[0].getAttribute('cy'), 10) || 0);
              }
            }
            const tblList = findXmlElements(gf, 'tbl');
            if (tblList.length > 0) {
              const tbl = tblList[0];
              const tblDiv = document.createElement('div');
              tblDiv.style.position = 'absolute';
              tblDiv.style.left = gx + 'px';
              tblDiv.style.top = gy + 'px';
              tblDiv.style.width = gw + 'px';
              tblDiv.style.height = gh + 'px';

              const tableEl = document.createElement('table');
              tableEl.style.width = '100%';
              tableEl.style.height = '100%';
              tableEl.style.borderCollapse = 'collapse';
              tableEl.style.fontSize = '14px';

              const trs = findXmlElements(tbl, 'tr');
              for (let trIdx = 0; trIdx < trs.length; trIdx++) {
                const trEl = document.createElement('tr');
                const tcs = findXmlElements(trs[trIdx], 'tc');
                for (let tcIdx = 0; tcIdx < tcs.length; tcIdx++) {
                  const tdEl = document.createElement('td');
                  tdEl.style.border = 'none';
                  tdEl.style.padding = '4px 8px';
                  tdEl.style.verticalAlign = 'middle';

                  // Cell background and optional explicit borders
                  let cellBgColor = null;
                  const tcPrList = findXmlElements(tcs[tcIdx], 'tcPr');
                  if (tcPrList.length > 0) {
                    const tcPr = tcPrList[0];
                    const solid = findXmlElements(tcPr, 'solidFill');
                    if (solid.length > 0) {
                      const clr = extractColor(solid[0]);
                      if (clr) {
                        cellBgColor = clr;
                        tdEl.style.backgroundColor = clr;
                      }
                    }

                    // Only set borders if explicitly specified with solidFill
                    const borderSides = { 'lnL': 'borderLeft', 'lnR': 'borderRight', 'lnT': 'borderTop', 'lnB': 'borderBottom' };
                    for (const [tag, styleProp] of Object.entries(borderSides)) {
                      const sideLn = findXmlElements(tcPr, tag);
                      if (sideLn.length > 0 && findXmlElements(sideLn[0], 'noFill').length === 0) {
                        const sideSolid = findXmlElements(sideLn[0], 'solidFill');
                        if (sideSolid.length > 0) {
                          const sideClr = extractColor(sideSolid[0]);
                          if (sideClr) {
                            let sideW = 1;
                            if (sideLn[0].getAttribute('w')) {
                              sideW = Math.max(1, Math.round(emuToPxX(parseInt(sideLn[0].getAttribute('w'), 10) || 12700)));
                            }
                            tdEl.style[styleProp] = `${sideW}px solid ${sideClr}`;
                          }
                        }
                      }
                    }
                  }

                  const activeCellBg = cellBgColor || bgColor;
                  const cellDefaultTextColor = isColorDark(activeCellBg) ? '#f8fafc' : '#0f172a';

                  // Cell text
                  const txList = findXmlElements(tcs[tcIdx], 'txBody');
                  if (txList.length > 0) {
                    const paragraphs = findXmlElements(txList[0], 'p');
                    for (let p = 0; p < paragraphs.length; p++) {
                      const pEl = paragraphs[p];
                      const pPrList = findXmlElements(pEl, 'pPr');
                      const align = (pPrList.length && pPrList[0].getAttribute('algn')) ? pPrList[0].getAttribute('algn') : 'l';

                      const cellP = document.createElement('div');
                      cellP.style.textAlign = (align === 'r' ? 'right' : align === 'ctr' ? 'center' : 'left');
                      cellP.style.margin = '0';
                      cellP.style.padding = '0';
                      cellP.style.lineHeight = '1.3';

                      const runs = pEl.childNodes;
                      for (let r = 0; r < runs.length; r++) {
                        const node = runs[r];
                        const nodeName = node.nodeName.toLowerCase();
                        if (nodeName.endsWith('r')) {
                          const tList = findXmlElements(node, 't');
                          const rText = tList.length ? tList[0].textContent : '';
                          if (rText) {
                            const span = document.createElement('span');
                            span.textContent = rText;

                            const rPrList = findXmlElements(node, 'rPr');
                            let fontSizePx = Math.round(14 * (canvasW / 1280));
                            let isBold = false;
                            let isItalic = false;
                            let cellTextColor = cellDefaultTextColor;
                            let fontFamily = 'Segoe UI, -apple-system, sans-serif';

                            if (rPrList.length > 0) {
                              const rPr = rPrList[0];
                              if (rPr.getAttribute('sz')) {
                                fontSizePx = Math.round((parseInt(rPr.getAttribute('sz'), 10) / 100) * 1.333 * (canvasW / 1280));
                              }
                              if (rPr.getAttribute('b') === '1' || rPr.getAttribute('b') === 'true') isBold = true;
                              if (rPr.getAttribute('i') === '1' || rPr.getAttribute('i') === 'true') isItalic = true;
                              const clr = extractColor(rPr);
                              if (clr) cellTextColor = clr;
                              const latinList = findXmlElements(rPr, 'latin');
                              if (latinList.length && latinList[0].getAttribute('typeface')) {
                                fontFamily = `"${latinList[0].getAttribute('typeface')}", Segoe UI, sans-serif`;
                              }
                            }

                            span.style.fontSize = Math.max(10, fontSizePx) + 'px';
                            span.style.fontWeight = isBold ? '700' : '400';
                            if (isItalic) span.style.fontStyle = 'italic';
                            span.style.color = cellTextColor;
                            span.style.fontFamily = fontFamily;
                            cellP.appendChild(span);
                          }
                        } else if (nodeName.endsWith('br')) {
                          cellP.appendChild(document.createElement('br'));
                        }
                      }
                      if (cellP.childNodes.length > 0) {
                        tdEl.appendChild(cellP);
                      }
                    }
                  }
                  trEl.appendChild(tdEl);
                }
                tableEl.appendChild(trEl);
              }
              tblDiv.appendChild(tableEl);
              slideStage.appendChild(tblDiv);
            }
          }

          // 3. Embedded Pictures (<p:pic>)
          const pics = findXmlElements(slideDoc, 'pic');
          for (let p = 0; p < pics.length; p++) {
            const pic = pics[p];
            const blipList = findXmlElements(pic, 'blip');
            const xfrmList = findXmlElements(pic, 'xfrm');
            if (blipList.length > 0 && xfrmList.length > 0) {
              const embedId = blipList[0].getAttribute('r:embed');
              const targetMedia = relsMap[embedId];
              const mediaDataUrl = mediaMap[targetMedia];
              if (mediaDataUrl) {
                const offList = findXmlElements(xfrmList[0], 'off');
                const extList = findXmlElements(xfrmList[0], 'ext');
                const px = offList.length ? emuToPxX(parseInt(offList[0].getAttribute('x'), 10) || 0) : 0;
                const py = offList.length ? emuToPxY(parseInt(offList[0].getAttribute('y'), 10) || 0) : 0;
                const pw = extList.length ? emuToPxX(parseInt(extList[0].getAttribute('cx'), 10) || 0) : canvasW;
                const ph = extList.length ? emuToPxY(parseInt(extList[0].getAttribute('cy'), 10) || 0) : canvasH;

                const imgEl = document.createElement('img');
                imgEl.src = mediaDataUrl;
                imgEl.style.position = 'absolute';
                imgEl.style.left = px + 'px';
                imgEl.style.top = py + 'px';
                imgEl.style.width = pw + 'px';
                imgEl.style.height = ph + 'px';
                imgEl.style.objectFit = 'contain';
                slideStage.appendChild(imgEl);
              }
            }
          }

          document.body.appendChild(slideStage);

          // Preload all images in the slide
          const slideImages = Array.from(slideStage.querySelectorAll('img'));
          await Promise.all(slideImages.map(img => {
            if (img.complete) return Promise.resolve();
            return new Promise(res => { img.onload = res; img.onerror = res; });
          }));

          const renderedCanvas = await html2canvas(slideStage, {
            width: canvasW,
            height: canvasH,
            scale: 2, // 2x resolution for razor-sharp presentation slides
            useCORS: true,
            logging: false,
            backgroundColor: bgColor,
            windowWidth: canvasW
          });
          slideJpgDataUrl = renderedCanvas.toDataURL('image/jpeg', 0.95);
        } catch (domErr) {
          console.warn('DOM html2canvas slide render failed, falling back to 2D canvas:', domErr);
        } finally {
          if (slideStage && document.body.contains(slideStage)) {
            document.body.removeChild(slideStage);
          }
        }
      }

      // 2D Canvas Fallback (if html2canvas is not present or failed)
      if (!slideJpgDataUrl) {
        const canvas = document.createElement('canvas');
        canvas.width = canvasW;
        canvas.height = canvasH;
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = bgColor;
        ctx.fillRect(0, 0, canvasW, canvasH);

        const shapes = findXmlElements(slideDoc, 'sp');
        for (let s = 0; s < shapes.length; s++) {
          const sp = shapes[s];
          const xfrmList = findXmlElements(sp, 'xfrm');
          let x = 40, y = 40, w = canvasW - 80, h = 60;
          if (xfrmList.length > 0) {
            const offList = findXmlElements(xfrmList[0], 'off');
            const extList = findXmlElements(xfrmList[0], 'ext');
            if (offList.length && extList.length) {
              x = emuToPxX(parseInt(offList[0].getAttribute('x'), 10) || 0);
              y = emuToPxY(parseInt(offList[0].getAttribute('y'), 10) || 0);
              w = emuToPxX(parseInt(extList[0].getAttribute('cx'), 10) || 0);
              h = emuToPxY(parseInt(extList[0].getAttribute('cy'), 10) || 0);
            }
          }

          let shapeFillColor = null;
          const spPrList = findXmlElements(sp, 'spPr');
          if (spPrList.length > 0) {
            const solidFillList = findXmlElements(spPrList[0], 'solidFill');
            if (solidFillList.length > 0) {
              const clr = extractColor(solidFillList[0]);
              if (clr) {
                shapeFillColor = clr;
                ctx.fillStyle = clr;
                ctx.fillRect(x, y, w, h);
              }
            }
          }

          const activeShapeBg = shapeFillColor || bgColor;
          const shapeDefaultTextColor = isColorDark(activeShapeBg) ? '#f8fafc' : '#0f172a';

          const txBodyList = findXmlElements(sp, 'txBody');
          if (txBodyList.length > 0) {
            const paragraphs = findXmlElements(txBodyList[0], 'p');
            let currentY = y + 24;

            for (let p = 0; p < paragraphs.length; p++) {
              const pEl = paragraphs[p];
              const pPrList = findXmlElements(pEl, 'pPr');
              const align = (pPrList.length && pPrList[0].getAttribute('algn')) ? pPrList[0].getAttribute('algn') : 'l';

              const runs = findXmlElements(pEl, 'r');
              let pText = '';
              let fontSize = 20;
              let isBold = false;
              let textColor = shapeDefaultTextColor;

              for (let r = 0; r < runs.length; r++) {
                const tList = findXmlElements(runs[r], 't');
                if (tList.length && tList[0].textContent) pText += tList[0].textContent;
                const rPrList = findXmlElements(runs[r], 'rPr');
                if (rPrList.length > 0) {
                  const rPr = rPrList[0];
                  if (rPr.getAttribute('sz')) fontSize = Math.round(parseInt(rPr.getAttribute('sz'), 10) / 100 * 1.3);
                  if (rPr.getAttribute('b') === '1' || rPr.getAttribute('b') === 'true') isBold = true;
                  const clr = extractColor(rPr);
                  if (clr) textColor = clr;
                }
              }

              if (pText.trim()) {
                ctx.font = `${isBold ? 'bold ' : ''}${Math.max(12, fontSize)}px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`;
                ctx.fillStyle = textColor;
                let textX = (align === 'ctr' ? x + w / 2 : align === 'r' ? x + w - 8 : x + 8);
                ctx.textAlign = (align === 'ctr' ? 'center' : align === 'r' ? 'right' : 'left');

                const words = pText.split(' ');
                let line = '';
                for (let n = 0; n < words.length; n++) {
                  const testLine = line + words[n] + ' ';
                  const metrics = ctx.measureText(testLine);
                  if (metrics.width > w - 16 && n > 0) {
                    ctx.fillText(line, textX, currentY);
                    line = words[n] + ' ';
                    currentY += fontSize * 1.3;
                  } else {
                    line = testLine;
                  }
                }
                ctx.fillText(line, textX, currentY);
                currentY += fontSize * 1.4;
              }
            }
          }
        }

        const pics = findXmlElements(slideDoc, 'pic');
        for (let p = 0; p < pics.length; p++) {
          const blipList = findXmlElements(pics[p], 'blip');
          const xfrmList = findXmlElements(pics[p], 'xfrm');
          if (blipList.length > 0 && xfrmList.length > 0) {
            const embedId = blipList[0].getAttribute('r:embed');
            const mediaDataUrl = mediaMap[relsMap[embedId]];
            if (mediaDataUrl) {
              const offList = findXmlElements(xfrmList[0], 'off');
              const extList = findXmlElements(xfrmList[0], 'ext');
              const px = offList.length ? emuToPxX(parseInt(offList[0].getAttribute('x'), 10) || 0) : 0;
              const py = offList.length ? emuToPxY(parseInt(offList[0].getAttribute('y'), 10) || 0) : 0;
              const pw = extList.length ? emuToPxX(parseInt(extList[0].getAttribute('cx'), 10) || 0) : canvasW;
              const ph = extList.length ? emuToPxY(parseInt(extList[0].getAttribute('cy'), 10) || 0) : canvasH;

              try {
                const imgEl = await loadImageElement(mediaDataUrl);
                ctx.drawImage(imgEl, px, py, pw, ph);
              } catch (e) {}
            }
          }
        }

        slideJpgDataUrl = canvas.toDataURL('image/jpeg', 0.95);
      }

      slideJpgs.push({
        dataUrl: slideJpgDataUrl,
        width: canvasW,
        height: canvasH
      });
    }

    if (slideJpgs.length === 0) {
      throw new Error('Could not render any slides from this PowerPoint presentation.');
    }

    // Assemble all slide JPG images into final landscape PDF
    let pdfDoc = null;
    for (let i = 0; i < slideJpgs.length; i++) {
      const slide = slideJpgs[i];
      if (i === 0) {
        pdfDoc = new jsPDF({
          orientation: 'landscape',
          unit: 'px',
          format: [slide.width, slide.height],
          hotfixes: ['px_scaling']
        });
        pdfDoc.addImage(slide.dataUrl, 'JPEG', 0, 0, slide.width, slide.height);
      } else {
        pdfDoc.addPage([slide.width, slide.height], 'landscape');
        pdfDoc.addImage(slide.dataUrl, 'JPEG', 0, 0, slide.width, slide.height);
      }
    }

    const pdfBlob = pdfDoc.output('blob');
    return {
      blob: pdfBlob,
      filename: file.name.replace(/\.[^/.]+$/, '') + '.pdf',
      summary: `Converted all ${slideJpgs.length} slide(s) to high-resolution visual JPGs and compiled into PDF.`
    };
  }

  // ==========================================
  // TOOL 17: PDF -> WORD
  // ==========================================
  async function pdfToWord(file) {
    if (!window.pdfjsLib) throw new Error('PDF.js library not loaded');
    const arrayBuffer = await readFileAsArrayBuffer(file);
    const pdfDoc = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
    const numPages = pdfDoc.numPages;

    let fullHtml = `<!DOCTYPE html><html><head><meta charset="utf-8"><title>${file.name}</title></head><body>`;
    fullHtml += `<h1>${file.name}</h1>`;

    for (let i = 1; i <= numPages; i++) {
      const page = await pdfDoc.getPage(i);
      const content = await page.getTextContent();
      const pageText = content.items.map(item => item.str).join(' ');
      fullHtml += `<h3>Page ${i}</h3><p>${pageText}</p><hr/>`;
    }
    fullHtml += `</body></html>`;

    // Standard Word MIME container for formatted HTML document
    const blob = new Blob(['\ufeff', fullHtml], {
      type: 'application/msword'
    });

    return {
      blob,
      filename: file.name.replace(/\.pdf$/i, '') + '.doc',
      summary: `Converted ${numPages} PDF pages into an editable Word document.`
    };
  }

  // ==========================================
  // TOOL 18: PDF -> EXCEL
  // ==========================================
  async function pdfToExcel(file) {
    if (!window.pdfjsLib || !window.XLSX) throw new Error('Conversion libraries not loaded');
    const arrayBuffer = await readFileAsArrayBuffer(file);
    const pdfDoc = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
    const numPages = pdfDoc.numPages;

    const rows = [];
    rows.push(['Source PDF', file.name]);
    rows.push(['Page', 'Line / Field Content']);

    for (let i = 1; i <= numPages; i++) {
      const page = await pdfDoc.getPage(i);
      const content = await page.getTextContent();
      const items = content.items;

      // Group text items roughly by Y coordinate into table rows
      const yMap = {};
      items.forEach(item => {
        const y = Math.round(item.transform[5]);
        if (!yMap[y]) yMap[y] = [];
        yMap[y].push(item.str);
      });

      const sortedY = Object.keys(yMap).sort((a, b) => b - a);
      sortedY.forEach(y => {
        const rowText = yMap[y].join('  ');
        if (rowText.trim()) {
          rows.push([`Page ${i}`, rowText]);
        }
      });
    }

    const ws = XLSX.utils.aoa_to_sheet(rows);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Extracted Data');
    const outBytes = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });

    const blob = new Blob([outBytes], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    return {
      blob,
      filename: file.name.replace(/\.pdf$/i, '') + '.xlsx',
      summary: `Extracted table and text rows into an Excel spreadsheet (${formatBytes(blob.size)}).`
    };
  }

  // ========================================================
  // INTERACTIVE VISUAL ORGANIZER & PREVIEW HELPERS
  // ========================================================

  /**
   * Render all pages of a PDF into visual canvas thumbnails in order
   */
  async function renderPdfPagesToCanvases(file, scale = 0.45) {
    if (!window.pdfjsLib) throw new Error('PDF.js library not loaded');
    let arrayBuffer;
    if (file instanceof ArrayBuffer) {
      arrayBuffer = file;
    } else if (file && typeof file.arrayBuffer === 'function') {
      arrayBuffer = await file.arrayBuffer();
    } else {
      arrayBuffer = await readFileAsArrayBuffer(file);
    }
    const pdfDoc = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
    const numPages = pdfDoc.numPages;
    const pageCanvases = [];

    for (let i = 1; i <= numPages; i++) {
      const page = await pdfDoc.getPage(i);
      const viewport = page.getViewport({ scale });
      const canvas = document.createElement('canvas');
      canvas.width = viewport.width;
      canvas.height = viewport.height;
      const ctx = canvas.getContext('2d');
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      await page.render({ canvasContext: ctx, viewport }).promise;

      const dataUrl = canvas.toDataURL('image/jpeg', 0.85);

      pageCanvases.push({
        pageNum: i,
        originalIndex: i - 1,
        canvas: canvas,
        dataUrl: dataUrl,
        width: viewport.width,
        height: viewport.height
      });
    }

    return pageCanvases;
  }

  /**
   * Reorder PDF pages according to an array of 0-based page indices
   */
  async function reorderPdfPagesByArray(file, newIndexOrder) {
    if (!window.PDFLib) throw new Error('PDF-Lib library not loaded');
    const arrayBuffer = await readFileAsArrayBuffer(file);
    const doc = await PDFLib.PDFDocument.load(arrayBuffer);

    const newDoc = await PDFLib.PDFDocument.create();
    const copiedPages = await newDoc.copyPages(doc, newIndexOrder);
    copiedPages.forEach(p => newDoc.addPage(p));

    const bytes = await newDoc.save();
    return {
      blob: new Blob([bytes], { type: 'application/pdf' }),
      filename: `reordered-${file.name}`,
      summary: `Successfully arranged ${newIndexOrder.length} pages in your custom order.`
    };
  }

  /**
   * Merge PDF files in custom user-specified order
   */
  async function mergePdfOrdered(orderedFiles) {
    return await mergePdf(orderedFiles);
  }

  /**
   * Delete pages by keeping specified indices
   */
  async function deletePdfPagesByIndices(file, keepIndices) {
    if (!window.PDFLib) throw new Error('PDF-Lib library not loaded');
    const arrayBuffer = await readFileAsArrayBuffer(file);
    const doc = await PDFLib.PDFDocument.load(arrayBuffer);
    const totalPages = doc.getPageCount();

    if (keepIndices.length === 0) {
      throw new Error('Cannot delete all pages. At least one page must be kept.');
    }

    const newDoc = await PDFLib.PDFDocument.create();
    const copiedPages = await newDoc.copyPages(doc, keepIndices);
    copiedPages.forEach(p => newDoc.addPage(p));

    const bytes = await newDoc.save();
    const deletedCount = totalPages - keepIndices.length;
    return {
      blob: new Blob([bytes], { type: 'application/pdf' }),
      filename: `deleted-pages-${file.name}`,
      summary: `Successfully removed ${deletedCount} page(s). Remaining: ${keepIndices.length} page(s).`
    };
  }

  // Public API
  return {
    formatBytes,
    readFileAsArrayBuffer,
    renderPdfPagesToCanvases,
    reorderPdfPagesByArray,
    mergePdfOrdered,
    deletePdfPagesByIndices,
    resolveCompressProfile,
    getCalibratedCompressParameters,
    estimateCompressedPdfSize,
    mergePdf,
    splitPdf,
    compressPdf,
    jpgToPdf,
    pdfToJpg,
    deletePdfPages,
    reorderPdfPages,
    pdfToPng,
    pngToPdf,
    pdfToText,
    addTextToPdf,
    addImageToPdf,
    protectPdf,
    wordToPdf,
    excelToPdf,
    powerPointToPdf,
    pdfToWord,
    pdfToExcel
  };
})();
