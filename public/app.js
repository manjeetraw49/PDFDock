/**
 * Instant Client-Side JPG to PDF Converter
 * Strict Rules: One Box, One Answer, No Logins, No Settings, No Menus.
 * 100% In-Browser Privacy, zero server requests.
 */

document.addEventListener('DOMContentLoaded', () => {
  const dropZone = document.getElementById('drop-zone');
  const fileInput = document.getElementById('file-input');
  const uploadContent = document.getElementById('upload-content');
  const processingState = document.getElementById('processing-state');
  const resultBox = document.getElementById('result-box');
  const resultSummary = document.getElementById('result-summary');
  const downloadBtn = document.getElementById('download-btn');
  const resetBtn = document.getElementById('reset-btn');

  let currentPdfBlob = null;
  let currentPdfUrl = null;
  let currentFileName = 'converted-document.pdf';

  // Format byte sizes for display
  function formatBytes(bytes) {
    if (!bytes || bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  }

  // Drag and Drop Event Listeners
  ['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropZone.classList.add('dragover');
    });
  });

  ['dragleave', 'dragend', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropZone.classList.remove('dragover');
    });
  });

  // Handle dropped files
  dropZone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt ? dt.files : null;
    if (files && files.length > 0) {
      processFiles(files);
    }
  });

  // Handle file picker selection
  fileInput.addEventListener('change', (e) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      processFiles(files);
    }
  });

  // Keyboard accessibility for dropzone
  dropZone.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      fileInput.click();
    }
  });

  // Load single image into an HTMLImageElement
  function loadImage(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const img = new Image();
        img.onload = () => resolve({ img, file });
        img.onerror = () => reject(new Error('Could not read image file: ' + file.name));
        img.src = e.target.result;
      };
      reader.onerror = () => reject(new Error('Failed to read file: ' + file.name));
      reader.readAsDataURL(file);
    });
  }

  // Convert image to normalized JPEG DataURL with white background
  function normalizeToJpeg(img) {
    const canvas = document.createElement('canvas');
    canvas.width = img.naturalWidth || img.width;
    canvas.height = img.naturalHeight || img.height;
    const ctx = canvas.getContext('2d');
    
    // Fill background with clean white (prevents transparent PNG artifacts)
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw image
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    
    return {
      dataUrl: canvas.toDataURL('image/jpeg', 0.92),
      width: canvas.width,
      height: canvas.height
    };
  }

  // Main Conversion Pipeline
  async function processFiles(fileList) {
    // Filter for image files
    const validFiles = Array.from(fileList).filter(f => f.type.startsWith('image/'));
    if (validFiles.length === 0) {
      alert('Please select valid JPG or image files.');
      return;
    }

    // Switch Dropzone to Processing State
    uploadContent.style.display = 'none';
    processingState.style.display = 'flex';

    try {
      // Ensure jsPDF is loaded
      const { jsPDF } = window.jspdf || {};
      if (!jsPDF) {
        throw new Error('PDF generator library not loaded. Please refresh the page.');
      }

      // Load all images in parallel
      const loadedImages = await Promise.all(validFiles.map(file => loadImage(file)));

      let pdfDoc = null;

      loadedImages.forEach((item, index) => {
        const { dataUrl, width, height } = normalizeToJpeg(item.img);
        const orientation = width > height ? 'landscape' : 'portrait';

        if (index === 0) {
          // Initialize PDF with first page dimensions
          pdfDoc = new jsPDF({
            orientation: orientation,
            unit: 'px',
            format: [width, height],
            hotfixes: ['px_scaling']
          });
          pdfDoc.addImage(dataUrl, 'JPEG', 0, 0, width, height);
        } else {
          // Add subsequent pages matching each image's native dimension
          pdfDoc.addPage([width, height], orientation);
          pdfDoc.addImage(dataUrl, 'JPEG', 0, 0, width, height);
        }
      });

      // Generate PDF Blob
      currentPdfBlob = pdfDoc.output('blob');
      if (currentPdfUrl) {
        URL.revokeObjectURL(currentPdfUrl);
      }
      currentPdfUrl = URL.createObjectURL(currentPdfBlob);

      // Name output file
      if (validFiles.length === 1) {
        const baseName = validFiles[0].name.replace(/\.[^/.]+$/, '');
        currentFileName = `${baseName}.pdf`;
      } else {
        currentFileName = 'converted-images.pdf';
      }

      // Transition to THE ONE ANSWER state
      const count = validFiles.length;
      const countText = count === 1 ? '1 JPG photo' : `${count} JPG photos`;
      resultSummary.textContent = `Successfully converted ${countText} into a standard PDF document (${formatBytes(currentPdfBlob.size)}).`;

      // Hide upload box, show result box
      dropZone.style.display = 'none';
      resultBox.style.display = 'block';

    } catch (err) {
      console.error(err);
      alert('An error occurred during conversion: ' + err.message);
      // Reset to upload state
      uploadContent.style.display = 'flex';
      processingState.style.display = 'none';
    }
  }

  // Trigger Download Action
  downloadBtn.addEventListener('click', () => {
    if (!currentPdfUrl) return;
    const a = document.createElement('a');
    a.href = currentPdfUrl;
    a.download = currentFileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  });

  // Convert Another JPG (Reset to One Box)
  resetBtn.addEventListener('click', () => {
    if (currentPdfUrl) {
      URL.revokeObjectURL(currentPdfUrl);
      currentPdfUrl = null;
      currentPdfBlob = null;
    }
    fileInput.value = '';

    // Switch views
    resultBox.style.display = 'none';
    dropZone.style.display = 'flex';
    uploadContent.style.display = 'flex';
    processingState.style.display = 'none';
  });
});
