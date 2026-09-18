# -*- coding: utf-8 -*-
"""
Script to generate PDFDock home page and 18 dedicated tool pages.
Features:
- Visual page thumbnails rendered in order using pdfjsLib
- Interactive drag-and-drop and touch-friendly reordering
- File arrangement in Merge PDF
- Complete final PDF preview before export in an embedded viewer
- Brand Name: PDFDock
- Logo: gemini-svg.svg
- Preserved colors, layout, and mobile-friendly design
- One plain sentence on every page (what it is, who it is for, what job it does)
- Real readable HTML facts (never drawn inside images or code)
- One box, one answer workflow with pre-export preview
- Adsterra & Monetag placeholders
"""

import os
import shutil

tools_data = [
    {
        "id": "merge-pdf",
        "file": "merge-pdf.html",
        "title": "Merge PDF",
        "full_title": "Merge PDF Files Online",
        "category": "organize",
        "category_label": "Organize PDF",
        "badge": "Popular",
        "sentence": "This tool is a free online PDF merger designed for students, office administrators, and professionals to combine multiple PDF documents into a single organized file in seconds.",
        "accept": ".pdf,application/pdf",
        "multiple": True,
        "icon": '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M8 2v4M16 2v4M3 10h18M5 4h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z"/><path d="M12 14v6M9 17h6"/></svg>',
        "box_title": "Drop multiple PDF files here",
        "box_sub": "or tap anywhere to select multiple PDF files",
        "mode": "merge"
    },
    {
        "id": "split-pdf",
        "file": "split-pdf.html",
        "title": "Split PDF",
        "full_title": "Split PDF Pages Online",
        "category": "organize",
        "category_label": "Organize PDF",
        "badge": "Popular",
        "sentence": "This tool is a fast online PDF splitter designed for researchers, legal clerks, and students to extract specific pages or page ranges from any PDF document without software.",
        "accept": ".pdf,application/pdf",
        "multiple": False,
        "icon": '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="12" y1="3" x2="12" y2="21"/></svg>',
        "box_title": "Drop your PDF file here",
        "box_sub": "view pages and click to extract",
        "mode": "split"
    },
    {
        "id": "compress-pdf",
        "file": "compress-pdf.html",
        "title": "Compress PDF",
        "full_title": "Compress PDF File Size",
        "category": "organize",
        "category_label": "Organize PDF",
        "badge": "Top",
        "sentence": "This tool is an instant online PDF compressor designed for job seekers, email senders, and mobile users to dramatically shrink PDF file sizes while maintaining readable quality.",
        "accept": ".pdf,application/pdf",
        "multiple": False,
        "icon": '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="4 14 10 14 10 20"/><polyline points="20 10 14 10 14 4"/><line x1="14" y1="10" x2="21" y2="3"/><line x1="3" y1="21" x2="10" y2="14"/></svg>',
        "box_title": "Drop your PDF to compress",
        "box_sub": "select compression level or reduce file size by up to 90%",
        "mode": "compress",
        "action_call": "window.PDFDock.compressPdf(selectedFiles[0])"
    },
    {
        "id": "jpg-to-pdf",
        "file": "jpg-to-pdf.html",
        "title": "JPG → PDF",
        "full_title": "JPG to PDF Converter",
        "category": "convert-to",
        "category_label": "Convert to PDF",
        "badge": "#1 Search",
        "sentence": "This site is a free, instant JPG to PDF converter designed for students, job applicants, and professionals to immediately convert JPG photos into clean, shareable PDF documents directly on their device.",
        "accept": "image/jpeg,image/jpg",
        "multiple": True,
        "icon": '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>',
        "box_title": "Drop your JPG photos here",
        "box_sub": "or tap anywhere to select photos from camera or gallery",
        "mode": "images_to_pdf",
        "action_call": "window.PDFDock.jpgToPdf(selectedFiles)"
    },
    {
        "id": "pdf-to-jpg",
        "file": "pdf-to-jpg.html",
        "title": "PDF → JPG",
        "full_title": "PDF to JPG Converter",
        "category": "convert-from",
        "category_label": "Convert from PDF",
        "badge": "Popular",
        "sentence": "This tool is a high-speed PDF to JPG image extractor designed for designers, students, and social media creators to convert PDF pages into high-resolution JPG images directly in the browser.",
        "accept": ".pdf,application/pdf",
        "multiple": False,
        "icon": '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>',
        "box_title": "Drop your PDF file here",
        "box_sub": "extracts pages into high-definition JPG images",
        "mode": "pdf_to_images",
        "action_call": "window.PDFDock.pdfToJpg(selectedFiles[0])"
    },
    {
        "id": "delete-pdf-pages",
        "file": "delete-pdf-pages.html",
        "title": "Delete PDF Pages",
        "full_title": "Delete PDF Pages Online",
        "category": "organize",
        "category_label": "Organize PDF",
        "badge": "Easy",
        "sentence": "This tool is a free PDF page remover designed for students, accountants, and office workers to permanently delete unwanted pages from any PDF document with zero signups.",
        "accept": ".pdf,application/pdf",
        "multiple": False,
        "icon": '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>',
        "box_title": "Drop your PDF file here",
        "box_sub": "shows all pages visually so you can click to delete",
        "mode": "delete"
    },
    {
        "id": "reorder-pdf-pages",
        "file": "reorder-pdf-pages.html",
        "title": "Reorder PDF Pages",
        "full_title": "Reorder PDF Pages Online",
        "category": "organize",
        "category_label": "Organize PDF",
        "badge": "Organize",
        "sentence": "This tool is an easy PDF page reorganizer designed for book authors, teachers, and business presenters to re-sequence and rearrange PDF pages in any custom order instantly.",
        "accept": ".pdf,application/pdf",
        "multiple": False,
        "icon": '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="7 10 12 15 17 10"/><polyline points="7 14 12 9 17 14"/><circle cx="12" cy="12" r="10"/></svg>',
        "box_title": "Drop your PDF file here",
        "box_sub": "shows all pages in order so you can drag and reorder",
        "mode": "reorder"
    },
    {
        "id": "pdf-to-png",
        "file": "pdf-to-png.html",
        "title": "PDF → PNG",
        "full_title": "PDF to PNG Converter",
        "category": "convert-from",
        "category_label": "Convert from PDF",
        "badge": "HD",
        "sentence": "This tool is a crisp PDF to PNG image converter designed for graphic designers, developers, and presentation creators to turn PDF pages into transparent, high-definition PNG pictures.",
        "accept": ".pdf,application/pdf",
        "multiple": False,
        "icon": '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M20.4 14.5L16 10 4 20"/></svg>',
        "box_title": "Drop your PDF file here",
        "box_sub": "generates lossless high-res PNG images",
        "mode": "pdf_to_images",
        "action_call": "window.PDFDock.pdfToPng(selectedFiles[0])"
    },
    {
        "id": "png-to-pdf",
        "file": "png-to-pdf.html",
        "title": "PNG → PDF",
        "full_title": "PNG to PDF Converter",
        "category": "convert-to",
        "category_label": "Convert to PDF",
        "badge": "Crisp",
        "sentence": "This tool is an instant PNG to PDF converter designed for digital artists, screenshot collectors, and mobile users to turn PNG graphics into standard PDF documents without quality loss.",
        "accept": "image/png",
        "multiple": True,
        "icon": '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>',
        "box_title": "Drop your PNG pictures here",
        "box_sub": "converts screenshots and transparent PNGs to PDF",
        "mode": "images_to_pdf",
        "action_call": "window.PDFDock.pngToPdf(selectedFiles)"
    },
    {
        "id": "pdf-to-text",
        "file": "pdf-to-text.html",
        "title": "PDF → Text",
        "full_title": "PDF to Text Extractor",
        "category": "convert-from",
        "category_label": "Convert from PDF",
        "badge": "Fast",
        "sentence": "This tool is a fast PDF text extractor designed for researchers, copywriters, and students to pull readable text out of PDF files into clean, editable text files.",
        "accept": ".pdf,application/pdf",
        "multiple": False,
        "icon": '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="4 7 4 4 20 4 20 7"/><line x1="9" y1="20" x2="15" y2="20"/><line x1="12" y1="4" x2="12" y2="20"/></svg>',
        "box_title": "Drop your PDF file here",
        "box_sub": "extracts plain text and paragraphs instantly",
        "mode": "single_pdf_direct",
        "action_call": "window.PDFDock.pdfToText(selectedFiles[0])"
    },
    {
        "id": "add-text",
        "file": "add-text.html",
        "title": "Add Text",
        "full_title": "Add Text & Watermark to PDF",
        "category": "edit",
        "category_label": "Edit & Security",
        "badge": "Edit",
        "sentence": "This tool is a free PDF text annotator designed for freelancers, contract signers, and business owners to stamp custom text, headers, or watermarks onto PDF pages directly.",
        "accept": ".pdf,application/pdf",
        "multiple": False,
        "icon": '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>',
        "box_title": "Drop your PDF file here",
        "box_sub": "stamp text, footer, or confidential watermarks",
        "mode": "add_text"
    },
    {
        "id": "sign-pdf",
        "file": "sign-pdf.html",
        "title": "Sign PDF",
        "full_title": "Sign PDF Online",
        "category": "edit",
        "category_label": "Edit & Security",
        "badge": "Signature",
        "sentence": "This tool is an online PDF document signer designed for remote workers, signers, and executives to sign PDFs with finger, mouse, typed cursive, or official signature stamps.",
        "accept": ".pdf,image/*,application/pdf",
        "multiple": True,
        "icon": '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>',
        "box_title": "Drop your PDF file here to sign",
        "box_sub": "draw signature with finger or mouse, type, or stamp signature image",
        "mode": "add_image"
    },
    {
        "id": "protect-pdf",
        "file": "protect-pdf.html",
        "title": "Protect PDF",
        "full_title": "Protect & Secure PDF",
        "category": "edit",
        "category_label": "Edit & Security",
        "badge": "Security",
        "sentence": "This tool is a client-side PDF security locker designed for sensitive document owners, legal teams, and privacy-conscious users to add security locks and restrictions to PDF files.",
        "accept": ".pdf,application/pdf",
        "multiple": False,
        "icon": '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>',
        "box_title": "Drop your PDF to protect",
        "box_sub": "secures document against unauthorized copying",
        "mode": "protect"
    },
    {
        "id": "word-to-pdf",
        "file": "word-to-pdf.html",
        "title": "Word → PDF",
        "full_title": "Word to PDF Converter",
        "category": "convert-to",
        "category_label": "Convert to PDF",
        "badge": "Office",
        "sentence": "This tool is an instant Word to PDF converter designed for resume builders, students, and writers to convert Microsoft Word DOCX documents into clean, universally shareable PDF files.",
        "accept": ".docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "multiple": False,
        "icon": '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>',
        "box_title": "Drop your Word .docx file here",
        "box_sub": "converts Word document into clean printable PDF",
        "mode": "doc_to_pdf",
        "action_call": "window.PDFDock.wordToPdf(selectedFiles[0])"
    },
    {
        "id": "excel-to-pdf",
        "file": "excel-to-pdf.html",
        "title": "Excel → PDF",
        "full_title": "Excel to PDF Converter",
        "category": "convert-to",
        "category_label": "Convert to PDF",
        "badge": "Spreadsheet",
        "sentence": "This tool is a free Excel spreadsheet to PDF converter designed for financial analysts, accountants, and team leads to turn XLSX worksheets into clean printable PDF tables.",
        "accept": ".xlsx,.xls,.csv,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "multiple": False,
        "icon": '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="3" y1="15" x2="21" y2="15"/><line x1="9" y1="3" x2="9" y2="21"/><line x1="15" y1="3" x2="15" y2="21"/></svg>',
        "box_title": "Drop your Excel spreadsheet here",
        "box_sub": "formats sheets and tables into landscape PDF",
        "mode": "doc_to_pdf",
        "action_call": "window.PDFDock.excelToPdf(selectedFiles[0])"
    },
    {
        "id": "powerpoint-to-pdf",
        "file": "powerpoint-to-pdf.html",
        "title": "PowerPoint → PDF",
        "full_title": "PowerPoint to PDF Converter",
        "category": "convert-to",
        "category_label": "Convert to PDF",
        "badge": "Slides",
        "sentence": "This tool is a high-fidelity PowerPoint to PDF converter designed for speakers, educators, and business professionals to render all presentation slides as high-definition JPGs and compile them into a PDF while preserving original layouts, images, and formatting.",
        "accept": ".pptx,.ppt,application/vnd.openxmlformats-officedocument.presentationml.presentation,application/vnd.ms-powerpoint",
        "multiple": False,
        "icon": '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>',
        "box_title": "Drop your PowerPoint .pptx deck here",
        "box_sub": "converts all slides visually to JPGs and packages into PDF",
        "mode": "doc_to_pdf",
        "action_call": "window.PDFDock.powerPointToPdf(selectedFiles[0])"
    },
    {
        "id": "pdf-to-word",
        "file": "pdf-to-word.html",
        "title": "PDF → Word",
        "full_title": "PDF to Word Converter",
        "category": "convert-from",
        "category_label": "Convert from PDF",
        "badge": "Editable",
        "sentence": "This tool is an editable PDF to Word document generator designed for writers, editors, and office teams to convert static PDF pages into editable Microsoft Word DOC files.",
        "accept": ".pdf,application/pdf",
        "multiple": False,
        "icon": '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><path d="M8 13h8M8 17h5"/></svg>',
        "box_title": "Drop your PDF file here",
        "box_sub": "converts into editable Microsoft Word format",
        "mode": "single_pdf_direct",
        "action_call": "window.PDFDock.pdfToWord(selectedFiles[0])"
    },
    {
        "id": "pdf-to-excel",
        "file": "pdf-to-excel.html",
        "title": "PDF → Excel",
        "full_title": "PDF to Excel Converter",
        "category": "convert-from",
        "category_label": "Convert from PDF",
        "badge": "Finance",
        "sentence": "This tool is an automated PDF table extractor designed for accountants, bookkeepers, and data analysts to convert tables in PDF statements into structured Excel XLSX spreadsheets.",
        "accept": ".pdf,application/pdf",
        "multiple": False,
        "icon": '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="3" x2="9" y2="21"/></svg>',
        "box_title": "Drop your PDF table or statement here",
        "box_sub": "pulls tables into structured Excel .xlsx workbook",
        "mode": "single_pdf_direct",
        "action_call": "window.PDFDock.pdfToExcel(selectedFiles[0])"
    }
]


seo_geo_data = {
    "merge-pdf": {
        "keywords": ["merge pdf", "combine pdf", "merge pdf online", "combine pdf files", "merge pdf free", "join pdf", "pdf merger"],
        "meta_desc": "Merge multiple PDF files into one clean document online for free. Fast, private in-browser PDF merger with page preview and drag-and-drop reordering.",
        "specs": {
            "inputs": "Multiple PDF files (.pdf)",
            "output": "Single Combined PDF (.pdf)",
            "privacy": "100% In-Browser (0 Server Uploads)",
            "speed": "Instant Sub-Second Processing"
        },
        "faqs": [
            {
                "q": "Is it safe to merge confidential PDFs on PDFDock?",
                "a": "Yes, 100%. PDFDock merges your documents locally inside your browser memory. Your files are never uploaded to any remote server or cloud database."
            },
            {
                "q": "Can I reorder the files or pages before merging?",
                "a": "Yes, you can arrange file sequences, view page thumbnails in order, and inspect the final merged document before downloading."
            },
            {
                "q": "Is there any limit on how many PDF files I can combine?",
                "a": "No artificial limits. You can combine multiple PDFs directly using your computer or phone hardware without watermarks or payment."
            }
        ],
        "howto_steps": [
            {"name": "Upload PDFs", "text": "Drag and drop your PDF files into the merge box or tap to select from your device."},
            {"name": "Arrange Order", "text": "Reorder files or view page thumbnails to ensure your documents are in the right sequence."},
            {"name": "Preview & Download", "text": "Inspect the complete final merged PDF in the preview viewer and tap 'Download Final PDF'."}
        ]
    },
    "split-pdf": {
        "keywords": ["split pdf", "separate pdf pages", "split pdf online", "extract pages from pdf", "split pdf free", "pdf splitter", "cut pdf pages"],
        "meta_desc": "Split PDF files and extract specific pages online for free. Fast, secure in-browser PDF splitter with visual thumbnail selection and zero file uploads.",
        "specs": {
            "inputs": "Single PDF document (.pdf)",
            "output": "Extracted PDF pages (.pdf)",
            "privacy": "100% In-Browser (0 Server Uploads)",
            "speed": "Instant Sub-Second Extraction"
        },
        "faqs": [
            {
                "q": "How do I extract specific pages from a PDF?",
                "a": "Drop your PDF, click on the page thumbnails you want to keep or extract, and click 'Extract & Preview Final PDF'."
            },
            {
                "q": "Are my pages sent to an external server to be split?",
                "a": "No. All page extraction happens client-side in your browser. Your sensitive records never leave your device."
            },
            {
                "q": "Can I split password-protected PDFs?",
                "a": "You must enter the document password to unlock it first, after which you can select and extract any pages instantly."
            }
        ],
        "howto_steps": [
            {"name": "Upload PDF", "text": "Drop your PDF file into the splitter box to render all pages visually in order."},
            {"name": "Select Pages", "text": "Click on specific page thumbnails to choose which pages to extract or keep."},
            {"name": "Extract & Download", "text": "Preview the extracted document in the built-in viewer and download your new PDF."}
        ]
    },
    "compress-pdf": {
        "keywords": ["compress pdf", "reduce pdf size", "compress pdf online", "pdf compressor", "reduce pdf file size free", "shrink pdf", "compress pdf to 100kb"],
        "meta_desc": "Compress PDF file size online without losing quality. Choose from 40%, 70%, or 90% size reduction or use custom slider. 100% free, private, and instant.",
        "specs": {
            "inputs": "PDF document (.pdf)",
            "output": "Compressed PDF (.pdf)",
            "privacy": "100% In-Browser (0 Server Uploads)",
            "speed": "Instant Local Compression"
        },
        "faqs": [
            {
                "q": "How much can I reduce my PDF file size?",
                "a": "You can reduce file sizes by up to 90% using the Extreme preset, or choose 70% (Recommended) or 40% (Light) for high-resolution graphics."
            },
            {
                "q": "Will compressing my PDF affect text readability?",
                "a": "PDFDock preserves readable text typography and scales image resolution cleanly according to your chosen compression level."
            },
            {
                "q": "Can I compress a PDF to under 100KB for portal uploads?",
                "a": "Yes, select the Extreme (90%) preset or use the fine-tuning percentage slider to fit strict upload size thresholds."
            }
        ],
        "howto_steps": [
            {"name": "Upload PDF", "text": "Drop or select the PDF document you need to compress."},
            {"name": "Select Compression Level", "text": "Pick from Extreme (90%), Recommended (70%), or Light (40%), or adjust the slider."},
            {"name": "Preview & Save", "text": "Review the compressed PDF in the previewer and download the reduced file instantly."}
        ]
    },
    "jpg-to-pdf": {
        "keywords": ["jpg to pdf", "convert jpg to pdf", "image to pdf", "jpeg to pdf", "jpg to pdf converter", "photos to pdf", "convert image to pdf free"],
        "meta_desc": "Convert JPG images to PDF documents online for free. Combine multiple photos into a single neat PDF in seconds with client-side privacy and instant download.",
        "specs": {
            "inputs": "JPG, JPEG images (.jpg, .jpeg)",
            "output": "Standard Multi-page PDF (.pdf)",
            "privacy": "100% In-Browser (0 Server Uploads)",
            "speed": "Instant Image Compilation"
        },
        "faqs": [
            {
                "q": "Can I convert multiple JPG photos into one single PDF?",
                "a": "Yes, select multiple JPGs or camera pictures at once. PDFDock organizes them into a single multi-page PDF document."
            },
            {
                "q": "Are my photos uploaded to any server?",
                "a": "Never. The entire conversion takes place locally in your web browser. Your private photos remain strictly on your device."
            },
            {
                "q": "Does JPG to PDF conversion reduce photo quality?",
                "a": "No, PDFDock maintains high image resolution and embeds your pictures in their original visual sharpness."
            }
        ],
        "howto_steps": [
            {"name": "Select Images", "text": "Drop or select one or multiple JPG/JPEG photos from your computer, phone, or tablet."},
            {"name": "Arrange Order", "text": "Preview your photos in order and adjust sequence if desired."},
            {"name": "Download PDF", "text": "Download your compiled multi-page PDF document instantly with zero wait time."}
        ]
    },
    "pdf-to-jpg": {
        "keywords": ["pdf to jpg", "convert pdf to jpg", "pdf to image", "pdf to jpeg", "extract images from pdf", "save pdf as jpg", "pdf to jpg converter free"],
        "meta_desc": "Convert PDF pages into high-resolution JPG images online for free. Extract all or selected pages into crisp JPG pictures instantly without registration.",
        "specs": {
            "inputs": "PDF document (.pdf)",
            "output": "High-Definition JPG Images (.jpg)",
            "privacy": "100% In-Browser (0 Server Uploads)",
            "speed": "2x DPI Instant Rendering"
        },
        "faqs": [
            {
                "q": "Can I choose which PDF pages to convert to JPG?",
                "a": "Yes, our visual thumbnail organizer lets you select individual pages, select all, or download single images on demand."
            },
            {
                "q": "What resolution are the converted JPG images?",
                "a": "PDFDock renders pages at high display resolution (2x DPI scale) ensuring crisp text and vibrant graphic details."
            },
            {
                "q": "Do I need to create an account or provide an email address?",
                "a": "No account, login, or email is required. Conversion is completely free and executes instantly in your browser."
            }
        ],
        "howto_steps": [
            {"name": "Upload PDF", "text": "Select or drag your PDF file to instantly render high-res thumbnail previews."},
            {"name": "Select Pages", "text": "Pick specific pages or click 'Select All' to convert all document pages."},
            {"name": "Download JPGs", "text": "Download selected JPG images individually or packaged in high quality."}
        ]
    },
    "delete-pdf-pages": {
        "keywords": ["delete pages from pdf", "remove pages from pdf", "delete pdf pages online", "remove pdf pages free", "pdf page remover", "delete page from pdf online", "how to delete pages from pdf"],
        "meta_desc": "Delete unwanted pages from any PDF document online for free. Click to remove pages visually and download your clean, reorganized PDF instantly.",
        "specs": {
            "inputs": "PDF document (.pdf)",
            "output": "Cleaned PDF (.pdf)",
            "privacy": "100% In-Browser (0 Server Uploads)",
            "speed": "Instant Interactive Removal"
        },
        "faqs": [
            {
                "q": "How do I remove unwanted pages from a PDF?",
                "a": "Simply upload your PDF, view all pages displayed in thumbnail order, click the trash icon on pages to remove, and export."
            },
            {
                "q": "Can I undo deleting a page before downloading?",
                "a": "Yes, you can click on any excluded page thumbnail again to restore it before generating your final document."
            },
            {
                "q": "Is deleting pages permanently destructive to my original file?",
                "a": "No, your original file on your computer is never modified. A new, clean PDF copy is generated for you to download."
            }
        ],
        "howto_steps": [
            {"name": "Upload Document", "text": "Drop your PDF file to render all pages as interactive visual cards."},
            {"name": "Click to Remove", "text": "Click on any unwanted pages or tap the delete icon to mark them for exclusion."},
            {"name": "Preview Clean PDF", "text": "Tap 'Generate & Preview Clean PDF', review the result, and download."}
        ]
    },
    "reorder-pdf-pages": {
        "keywords": ["reorder pdf pages", "rearrange pdf pages", "reorder pages in pdf", "organize pdf pages", "move pages in pdf", "change pdf page order", "sort pdf pages online"],
        "meta_desc": "Reorder and rearrange PDF pages online for free. Drag and drop thumbnails or use mobile-friendly touch arrows to change page sequence in seconds.",
        "specs": {
            "inputs": "PDF document (.pdf)",
            "output": "Re-sequenced PDF (.pdf)",
            "privacy": "100% In-Browser (0 Server Uploads)",
            "speed": "Drag & Drop / Touch Responsive"
        },
        "faqs": [
            {
                "q": "Can I reorder PDF pages on a mobile phone?",
                "a": "Yes! PDFDock includes dedicated left/right touch arrows on each thumbnail card so you can effortlessly rearrange pages on touchscreens."
            },
            {
                "q": "Does page reordering affect PDF links or bookmarks?",
                "a": "PDFDock creates a clean, newly structured PDF preserving page contents while updating the visual sequence seamlessly."
            },
            {
                "q": "Can I preview the rearranged PDF before saving?",
                "a": "Yes, PDFDock includes a full pre-export preview frame so you can inspect every page in its new order before downloading."
            }
        ],
        "howto_steps": [
            {"name": "Upload PDF", "text": "Select your PDF file to lay out all document pages visually in sequence."},
            {"name": "Rearrange Pages", "text": "Drag and drop cards or click the left/right arrow buttons to shift page positions."},
            {"name": "Preview & Save", "text": "Review the newly ordered document in the preview frame and download your PDF."}
        ]
    },
    "pdf-to-png": {
        "keywords": ["pdf to png", "convert pdf to png", "pdf to png high resolution", "pdf to png converter online", "export pdf as png", "save pdf to png free", "turn pdf into png"],
        "meta_desc": "Convert PDF documents into high-definition PNG images with lossless quality online for free. Extract transparent graphic elements and page pictures in browser.",
        "specs": {
            "inputs": "PDF document (.pdf)",
            "output": "Lossless PNG Images (.png)",
            "privacy": "100% In-Browser (0 Server Uploads)",
            "speed": "Lossless 2x Crisp Rendering"
        },
        "faqs": [
            {
                "q": "Why should I convert PDF to PNG instead of JPG?",
                "a": "PNG is a lossless format that preserves razor-sharp edges, typography, diagrams, and transparent background elements better than JPG."
            },
            {
                "q": "Can I download all pages as PNG at once?",
                "a": "Yes, click 'Select All' and 'Download Selected PNGs' to export all document pages in high definition."
            },
            {
                "q": "Are my documents kept private during PNG extraction?",
                "a": "Yes, all rendering occurs in your local browser sandbox. No PDF data ever leaves your computer or phone."
            }
        ],
        "howto_steps": [
            {"name": "Upload Document", "text": "Drop your PDF file into the dropzone to generate crisp page previews."},
            {"name": "Choose Pages", "text": "Select individual pages or click 'Select All' to convert the entire document."},
            {"name": "Download PNG", "text": "Click 'Download Selected PNGs' to save high-resolution lossless images."}
        ]
    },
    "png-to-pdf": {
        "keywords": ["png to pdf", "convert png to pdf", "png to pdf converter", "combine png to pdf", "multiple png to pdf", "png to pdf online free", "turn png into pdf"],
        "meta_desc": "Convert PNG pictures and screenshots into clean PDF files online for free. Combine multiple PNG images into a single professional PDF without watermarks.",
        "specs": {
            "inputs": "PNG images (.png)",
            "output": "Standard Multi-page PDF (.pdf)",
            "privacy": "100% In-Browser (0 Server Uploads)",
            "speed": "Instant Local Conversion"
        },
        "faqs": [
            {
                "q": "Can I merge multiple PNG screenshots into one PDF?",
                "a": "Yes, drop multiple PNG images and PDFDock will arrange them into sequential pages of a single PDF document."
            },
            {
                "q": "Will transparent PNG backgrounds turn black?",
                "a": "No, PDFDock renders transparent PNG areas onto clean white PDF paper backgrounds cleanly and accurately."
            },
            {
                "q": "Is there any software installation required?",
                "a": "None. PDFDock runs directly in any modern browser on Windows, Mac, iOS, and Android."
            }
        ],
        "howto_steps": [
            {"name": "Select PNGs", "text": "Choose or drop your PNG screenshots or graphic files into the converter."},
            {"name": "Verify Sequence", "text": "Inspect the images to confirm page order and visual arrangement."},
            {"name": "Download PDF", "text": "Download your compiled, high-resolution PDF document immediately."}
        ]
    },
    "pdf-to-text": {
        "keywords": ["pdf to text", "convert pdf to text", "extract text from pdf", "pdf to txt converter", "copy text from pdf", "pdf to text online free", "pdf text extractor"],
        "meta_desc": "Extract plain text from any PDF document online for free. Fast, accurate in-browser PDF to text extractor designed for copywriters, researchers, and students.",
        "specs": {
            "inputs": "PDF document (.pdf)",
            "output": "Plain Text Document (.txt)",
            "privacy": "100% In-Browser (0 Server Uploads)",
            "speed": "Instant Character Stream Extraction"
        },
        "faqs": [
            {
                "q": "Can I extract text from multi-page PDFs?",
                "a": "Yes, PDFDock parses all pages and compiles all readable text into an organized, downloadable .txt file or copyable block."
            },
            {
                "q": "Does text extraction work on scanned PDF documents?",
                "a": "It extracts all digital text streams. For scanned image-only PDFs, ensure the document has an embedded text layer."
            },
            {
                "q": "Is my document text kept private?",
                "a": "Absolutely. All text extraction logic executes locally on your CPU; no text is transmitted over the internet."
            }
        ],
        "howto_steps": [
            {"name": "Upload PDF", "text": "Select the PDF file from which you want to extract written text."},
            {"name": "Process Instantly", "text": "PDFDock parses all text layers across every page in milliseconds."},
            {"name": "Download Text", "text": "Download the clean extracted .txt file or copy the content to your clipboard."}
        ]
    },
    "add-text": {
        "keywords": ["add text to pdf", "edit pdf text", "write on pdf", "add watermark to pdf", "type on pdf online", "add text to pdf free", "insert text into pdf"],
        "meta_desc": "Add custom text, page numbers, or confidential watermarks to PDF files online for free. Live visual studio preview with customizable opacity, color, and placement.",
        "specs": {
            "inputs": "PDF document (.pdf)",
            "output": "Annotated / Watermarked PDF (.pdf)",
            "privacy": "100% In-Browser (0 Server Uploads)",
            "speed": "Real-Time Visual Studio Preview"
        },
        "faqs": [
            {
                "q": "Can I stamp diagonal watermarks like 'CONFIDENTIAL' or 'DRAFT'?",
                "a": "Yes! Use one of our quick presets or type your own text, adjust the 45-degree angle, opacity, font size, and color with live visual preview."
            },
            {
                "q": "Can I add dynamic page numbers?",
                "a": "Yes, enter 'Page {n} of {total}' into the text field to automatically stamp accurate page numbers across all pages."
            },
            {
                "q": "Can I place text underneath or on top of document content?",
                "a": "Yes, you can choose 'Overlay' (stamps over content) or 'Underlay' (watermark sits beneath document text)."
            }
        ],
        "howto_steps": [
            {"name": "Upload PDF", "text": "Drop your PDF file into the studio to activate the text and watermark editor."},
            {"name": "Configure Text & Style", "text": "Choose a preset or type custom text, select position, color, and transparency with live preview."},
            {"name": "Preview & Save", "text": "Tap 'Apply Watermark / Text', inspect the final document, and download."}
        ]
    },
    "sign-pdf": {
        "keywords": ["sign pdf", "sign pdf online free", "electronic signature pdf", "digital signature pdf", "add signature to pdf", "how to sign a pdf", "e sign pdf"],
        "meta_desc": "Sign PDF documents online for free. Draw your electronic signature with mouse or finger, type cursive, or stamp signature image with 100% privacy.",
        "specs": {
            "inputs": "PDF document (.pdf)",
            "output": "Signed PDF (.pdf)",
            "privacy": "100% In-Browser (0 Server Uploads)",
            "speed": "Touch & Stylus Responsive"
        },
        "faqs": [
            {
                "q": "Is signing PDFs on PDFDock legally valid?",
                "a": "Yes, electronic signatures created on PDF documents are widely recognized for contracts, agreements, and standard business forms."
            },
            {
                "q": "Is my signature saved or stored on any server?",
                "a": "Never. Your signature graphic is applied locally in your browser memory and disappears as soon as you close the page."
            },
            {
                "q": "Can I draw my signature on my phone or tablet?",
                "a": "Yes, the signature canvas fully supports touchscreen drawing with smooth finger and stylus input on mobile devices."
            }
        ],
        "howto_steps": [
            {"name": "Upload Document", "text": "Select the contract or document requiring signature."},
            {"name": "Create Signature", "text": "Draw with your finger/mouse, type in cursive, or upload an existing signature image."},
            {"name": "Place & Download", "text": "Position the signature on the appropriate page, preview, and download your signed PDF."}
        ]
    },
    "protect-pdf": {
        "keywords": ["protect pdf", "password protect pdf", "lock pdf", "encrypt pdf online", "set password on pdf", "pdf password protect free", "secure pdf file"],
        "meta_desc": "Password protect and encrypt PDF files online for free. Lock sensitive documents with standard PDF encryption directly in your browser with zero data leaks.",
        "specs": {
            "inputs": "PDF document (.pdf)",
            "output": "Encrypted Password-Locked PDF (.pdf)",
            "privacy": "100% In-Browser (0 Server Uploads)",
            "speed": "Standard AES / RC4 WebCrypto"
        },
        "faqs": [
            {
                "q": "What happens if I forget the password I set?",
                "a": "Because PDFDock enforces zero-knowledge client-side encryption, passwords are not stored anywhere. Make sure to record your password safely!"
            },
            {
                "q": "Is my document uploaded to a server to be encrypted?",
                "a": "No. Encryption happens locally on your computer or mobile device using Web Crypto and PDF-lib algorithms."
            },
            {
                "q": "Can locked PDFs be opened in standard viewers like Adobe Acrobat?",
                "a": "Yes, any standard PDF reader on Windows, Mac, iOS, or Android will prompt for the password when opening."
            }
        ],
        "howto_steps": [
            {"name": "Upload PDF", "text": "Select the PDF file that requires password protection and encryption."},
            {"name": "Set Strong Password", "text": "Enter your desired access password and verify with the live strength meter."},
            {"name": "Encrypt & Download", "text": "Tap 'Encrypt & Protect PDF' to download your secure password-locked file."}
        ]
    },
    "word-to-pdf": {
        "keywords": ["word to pdf", "convert word to pdf", "docx to pdf", "doc to pdf converter", "convert docx to pdf online", "word to pdf converter free", "save word document as pdf"],
        "meta_desc": "Convert Microsoft Word DOCX files to PDF online for free. Fast, accurate formatting conversion preserving text, headings, and layouts directly in your browser.",
        "specs": {
            "inputs": "Microsoft Word Document (.docx)",
            "output": "Standard Printable PDF (.pdf)",
            "privacy": "100% In-Browser (0 Server Uploads)",
            "speed": "Instant DOCX DOM Parsing"
        },
        "faqs": [
            {
                "q": "Does Word to PDF work with modern .docx files?",
                "a": "Yes, PDFDock converts modern Microsoft Word .docx files into clean, universally readable PDF documents."
            },
            {
                "q": "Will my original Word document formatting be preserved?",
                "a": "Yes, paragraphs, fonts, alignment, and basic styling are translated cleanly into PDF page structures."
            },
            {
                "q": "Are my corporate or personal Word documents kept secure?",
                "a": "Yes, all parsing runs locally in your browser memory. Your documents are never uploaded to any third-party server."
            }
        ],
        "howto_steps": [
            {"name": "Upload Word DOCX", "text": "Drop your Microsoft Word (.docx) file into the converter box."},
            {"name": "Instant Conversion", "text": "PDFDock parses text structures, tables, and typography locally in browser."},
            {"name": "Download PDF", "text": "Review the converted PDF document and tap download."}
        ]
    },
    "excel-to-pdf": {
        "keywords": ["excel to pdf", "convert excel to pdf", "xlsx to pdf", "xls to pdf converter", "convert spreadsheet to pdf", "excel to pdf online free", "save excel sheet as pdf"],
        "meta_desc": "Convert Excel spreadsheets and XLSX workbooks to printable PDF tables online for free. Formats data grids cleanly in landscape layout with zero server uploads.",
        "specs": {
            "inputs": "Excel Worksheets (.xlsx, .xls, .csv)",
            "output": "Landscape Formatted PDF (.pdf)",
            "privacy": "100% In-Browser (0 Server Uploads)",
            "speed": "Instant Grid-to-Vector Rendering"
        },
        "faqs": [
            {
                "q": "How does Excel to PDF handle wide spreadsheet tables?",
                "a": "PDFDock formats spreadsheet data into landscape PDF pages with optimized column widths for readable viewing and printing."
            },
            {
                "q": "Can I convert .xlsx, .xls, and .csv files?",
                "a": "Yes, all common spreadsheet formats including XLSX and CSV are fully supported."
            },
            {
                "q": "Is my financial spreadsheet data sent to any cloud service?",
                "a": "Never. Calculations and table rendering occur entirely on your local machine with 100% privacy."
            }
        ],
        "howto_steps": [
            {"name": "Upload Spreadsheet", "text": "Drop your Excel (.xlsx, .xls, or .csv) file into the upload zone."},
            {"name": "Automatic Table Formatting", "text": "Sheets are automatically parsed and formatted into landscape PDF pages."},
            {"name": "Download PDF Table", "text": "Download your clean, printable spreadsheet PDF ready for sharing or printing."}
        ]
    },
    "powerpoint-to-pdf": {
        "keywords": ["powerpoint to pdf", "convert ppt to pdf", "pptx to pdf", "ppt to pdf converter", "convert powerpoint to pdf free", "save ppt as pdf online", "slides to pdf"],
        "meta_desc": "Convert PowerPoint PPTX slide decks to PDF online for free. Renders slides with high visual fidelity and compiles them into a shareable PDF document.",
        "specs": {
            "inputs": "PowerPoint Presentations (.pptx, .ppt)",
            "output": "Presentation Slides PDF (.pdf)",
            "privacy": "100% In-Browser (0 Server Uploads)",
            "speed": "Sequential Slide Image Generation"
        },
        "faqs": [
            {
                "q": "Are all presentation slides converted into the PDF?",
                "a": "Yes, each slide in your PowerPoint deck is rendered and ordered sequentially into the resulting PDF document."
            },
            {
                "q": "Can I view the presentation PDF on mobile devices?",
                "a": "Yes, the exported PDF can be opened seamlessly on any iPhone, Android, tablet, or desktop computer."
            },
            {
                "q": "Do I need Microsoft PowerPoint installed on my computer?",
                "a": "No, PDFDock runs independently in your web browser without requiring Office or external software."
            }
        ],
        "howto_steps": [
            {"name": "Upload Presentation", "text": "Drop your PowerPoint (.pptx) presentation deck into the converter."},
            {"name": "Render Slides", "text": "Slides are converted into high-definition vector/image pages in order."},
            {"name": "Download PDF Slides", "text": "Download the completed presentation PDF ready for distribution or projection."}
        ]
    },
    "pdf-to-word": {
        "keywords": ["pdf to word", "convert pdf to word", "pdf to docx", "pdf to doc converter", "pdf to word online free", "editable pdf to word", "convert pdf to editable word"],
        "meta_desc": "Convert PDF files into editable Microsoft Word documents online for free. Extract text, headings, and paragraphs into editable DOC files with zero signups.",
        "specs": {
            "inputs": "PDF document (.pdf)",
            "output": "Editable Word Document (.doc)",
            "privacy": "100% In-Browser (0 Server Uploads)",
            "speed": "Instant Semantic Text Flow"
        },
        "faqs": [
            {
                "q": "Can I edit the text after converting PDF to Word?",
                "a": "Yes, the output document is an editable Microsoft Word document that you can open and edit in Word, Google Docs, or LibreOffice."
            },
            {
                "q": "Are my contracts and confidential files uploaded anywhere?",
                "a": "No, text extraction and DOC generation happen client-side in browser memory, ensuring complete confidentiality."
            },
            {
                "q": "Is there any cost or trial period for PDF to Word conversion?",
                "a": "No, PDFDock is 100% free with no trial limits, subscriptions, or watermarks."
            }
        ],
        "howto_steps": [
            {"name": "Upload PDF", "text": "Select or drag the PDF you want to convert into an editable Word document."},
            {"name": "Process Layout", "text": "PDFDock extracts text lines, headings, and paragraph flows in milliseconds."},
            {"name": "Download Editable Word", "text": "Download your editable Word (.doc) document and start editing immediately."}
        ]
    },
    "pdf-to-excel": {
        "keywords": ["pdf to excel", "convert pdf to excel", "pdf to xlsx", "extract table from pdf to excel", "pdf to excel converter online", "convert pdf to spreadsheet free", "pdf to csv"],
        "meta_desc": "Convert PDF bank statements and data tables into Excel XLSX spreadsheets online for free. Automatically detects rows and columns with 100% client privacy.",
        "specs": {
            "inputs": "PDF tables, invoices, statements (.pdf)",
            "output": "Structured Excel Workbook (.xlsx)",
            "privacy": "100% In-Browser (0 Server Uploads)",
            "speed": "Smart Tabular Grid Extraction"
        },
        "faqs": [
            {
                "q": "Can PDF to Excel extract tables from bank statements and invoices?",
                "a": "Yes, PDFDock detects structured tabular data, rows, and columns and exports them into neat Excel cells."
            },
            {
                "q": "Can I open the exported spreadsheet in Excel and Google Sheets?",
                "a": "Yes, the output is formatted as a standard Microsoft Excel spreadsheet compatible with Excel, Google Sheets, and LibreOffice Calc."
            },
            {
                "q": "Is sensitive financial data safe when converting?",
                "a": "Absolutely. Processing is done entirely in your browser sandbox without transmitting data to remote servers."
            }
        ],
        "howto_steps": [
            {"name": "Upload PDF Statement", "text": "Drop your PDF document containing tables, receipts, or financial reports."},
            {"name": "Detect Columns & Rows", "text": "The engine identifies cell boundaries and organizes data into rows."},
            {"name": "Download Excel Spreadsheet", "text": "Download the structured .xlsx workbook and open it in Excel or Google Sheets."}
        ]
    }
}

# Attach SEO & GEO data to each tool in tools_data
for tool in tools_data:
    tid = tool["id"]
    if tid in seo_geo_data:
        tool["keywords"] = seo_geo_data[tid]["keywords"]
        tool["meta_desc"] = seo_geo_data[tid]["meta_desc"]
        tool["specs"] = seo_geo_data[tid]["specs"]
        tool["faqs"] = seo_geo_data[tid]["faqs"]
        tool["howto_steps"] = seo_geo_data[tid]["howto_steps"]


def make_navbar(active_page="index.html"):
    categories = [
        {"id": "organize", "label": "Organize PDF"},
        {"id": "convert-to", "label": "Convert to PDF"},
        {"id": "convert-from", "label": "Convert from PDF"},
        {"id": "edit", "label": "Edit & Security"},
    ]

    categorized_cols = []
    for cat in categories:
        cat_tools = [t for t in tools_data if t["category"] == cat["id"]]
        tool_links = []
        for t in cat_tools:
            act = " active" if t["file"] == active_page else ""
            tool_links.append(f'<a href="{t["file"]}" class="mega-tool-link{act}">{t["title"]}</a>')
        links_str = "".join(tool_links)
        categorized_cols.append(f"""
          <div class="mega-col">
            <div class="mega-col-title">{cat["label"]}</div>
            <div class="mega-col-links">
              {links_str}
            </div>
          </div>
        """)
    mega_grid_html = "".join(categorized_cols)

    tools_active = " active" if active_page == "index.html" else ""
    jpg_active = " active" if active_page == "jpg-to-pdf.html" else ""
    pdf_active = " active" if active_page == "pdf-to-jpg.html" else ""
    comp_active = " active" if active_page == "compress-pdf.html" else ""
    all_active = " active" if active_page == "index.html" else ""

    return f"""
  <nav class="site-nav" aria-label="Main Navigation">
    <div class="nav-container">
      <a href="index.html" class="brand-link" title="PDFDock - Everything You Need, All in One Place">
        <img src="gemini-svg.svg" alt="PDFDock" class="brand-logo" width="114" height="40">
      </a>
      <div class="nav-tools-menu">
        <div class="nav-dropdown-wrap">
          <button type="button" class="nav-dropdown-btn{tools_active}" id="menu-toggle-btn" aria-expanded="false" aria-label="Toggle Tools Menu">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
            <span>Tools</span>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>
          </button>
          <div class="tools-menu-drawer" id="tools-drawer">
            <div class="mega-menu-header">
              <span class="mega-header-title">All {len(tools_data)} PDFDock Tools</span>
              <a href="index.html" class="mega-all-link{all_active}">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="vertical-align: -1px; margin-right: 3px;"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
                All Tools Directory &rarr;
              </a>
            </div>
            <div class="mega-menu-grid">
              {mega_grid_html}
            </div>
          </div>
        </div>
        <a href="jpg-to-pdf.html" class="nav-link{jpg_active}">JPG to PDF</a>
        <a href="pdf-to-jpg.html" class="nav-link{pdf_active}">PDF to JPG</a>
        <a href="compress-pdf.html" class="nav-link{comp_active}">Compress PDF</a>
      </div>
    </div>
  </nav>
"""

def make_footer():
    categories = [
        {"id": "organize", "label": "Organize PDF"},
        {"id": "convert-to", "label": "Convert to PDF"},
        {"id": "convert-from", "label": "Convert from PDF"},
        {"id": "edit", "label": "Edit & Security"},
    ]

    cols_html = ""
    for cat in categories:
        cat_tools = [t for t in tools_data if t["category"] == cat["id"]]
        tool_links = "".join([f'<a href="{t["file"]}" class="footer-tool-link">{t["title"]}</a>' for t in cat_tools])
        cols_html += f"""
        <div class="footer-col">
          <h4 class="footer-col-title">{cat["label"]}</h4>
          <div class="footer-links-list">
            {tool_links}
          </div>
        </div>
        """

    return f"""
  <footer class="site-footer">
    <div class="footer-container">
      <div class="footer-main-grid">
        <div class="footer-brand-col">
          <a href="index.html" class="footer-brand-link" title="PDFDock - Everything You Need, All in One Place">
            <img src="gemini-svg.svg" alt="PDFDock Logo" class="footer-logo" width="145" height="51">
          </a>
          <p class="footer-tagline">Everything You Need, All in One Place.</p>
        </div>
        <div class="footer-nav-grid">
          {cols_html}
        </div>
      </div>
      <div class="footer-bottom-bar">
        <p class="footer-copyright">&copy; 2026 PDFDock &bull; All rights reserved. <a href="https://omg10.com/4/11833285" target="_blank" rel="noopener sponsored" class="footer-partner-link">Partner Deals</a></p>
        <p class="footer-author">Developed By Manjeet Raw</p>
      </div>
    </div>
  </footer>
"""

def make_smartlink_banner(position="top"):
    badge_text = "Sponsored" if position == "top" else ("Partner Offer" if position == "mid" else "Recommended")
    title_text = "Fast Cloud Storage &amp; Secure File Transfer" if position == "top" else ("Premium Productivity Apps &amp; Cloud Tools" if position == "mid" else "Fast File Archiving &amp; Document Solutions")
    desc_text = "Free high-speed file storage, document backup &amp; instant sharing offers." if position == "top" else ("Special offers on document utilities, cloud backup, and PDF software." if position == "mid" else "Explore verified partners for secure file compression, cloud tools &amp; storage.")
    action_text = "Explore Deals &rarr;" if position == "top" else ("Get Access &rarr;" if position == "mid" else "Learn More &rarr;")
    icon_svg = '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>' if position == "top" else ('<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>' if position == "mid" else '<path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>')

    return f"""
  <aside class="ad-container ad-banner-{position}" id="ad-{position}" aria-label="Sponsored Recommendation" style="width: 100%; max-width: 760px; margin: 1.25rem auto; padding: 0 1rem; display: flex; justify-content: center; box-sizing: border-box;">
    <a href="https://omg10.com/4/11833285" target="_blank" rel="noopener sponsored" class="smartlink-banner-link" style="display: block; width: 100%; text-decoration: none !important; color: inherit;" title="Explore Partner Offers">
      <div class="smartlink-card" style="width: 100%; background: #ffffff; background-image: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); border: 1px solid #e2e8f0; border-radius: 12px; padding: 14px 18px; display: flex; align-items: center; gap: 14px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); position: relative; text-decoration: none !important; box-sizing: border-box; transition: transform 0.2s ease, border-color 0.2s ease;">
        <span class="smartlink-badge" style="position: absolute; top: 8px; right: 12px; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b; background: #f1f5f9; padding: 2px 7px; border-radius: 4px; text-decoration: none !important;">{badge_text}</span>
        <div class="smartlink-icon" style="width: 42px; height: 42px; min-width: 42px; border-radius: 10px; background: #ffe4e6; color: #e11d48; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">{icon_svg}</svg>
        </div>
        <div class="smartlink-info" style="flex: 1; display: flex; flex-direction: column; gap: 3px; min-width: 0; text-decoration: none !important;">
          <span class="smartlink-title" style="font-size: 14.5px; font-weight: 700; color: #0f172a; text-decoration: none !important; line-height: 1.35; display: block;">{title_text}</span>
          <span class="smartlink-desc" style="font-size: 12.5px; color: #64748b; text-decoration: none !important; line-height: 1.35; display: block;">{desc_text}</span>
        </div>
        <span class="smartlink-action" style="background: #0f172a; color: #ffffff; font-size: 13px; font-weight: 600; padding: 8px 16px; border-radius: 8px; white-space: nowrap; flex-shrink: 0; text-decoration: none !important; display: inline-block;">{action_text}</span>
      </div>
    </a>
  </aside>
"""

def make_download_recommendation():
    return """
        <div class="sponsored-recommendation-box" style="margin-top: 1.25rem; padding-top: 1rem; border-top: 1px dashed #e2e8f0; text-align: center; width: 100%; box-sizing: border-box;">
          <span class="sponsored-badge" style="display: inline-block; font-size: 10.5px; text-transform: uppercase; font-weight: 700; color: #94a3b8; letter-spacing: 0.05em; margin-bottom: 6px;">Sponsored Recommendation</span>
          <br>
          <a href="https://omg10.com/4/11833285" target="_blank" rel="noopener sponsored" class="sponsored-recommendation-link" style="display: inline-flex; align-items: center; gap: 8px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 8px 16px; color: #334155; text-decoration: none !important; font-size: 13px; box-sizing: border-box;">
            <span class="sponsored-link-icon" style="font-size: 16px; text-decoration: none !important;">⚡</span>
            <span class="sponsored-link-text" style="color: #334155; text-decoration: none !important;">Need fast, unlimited cloud storage for your files? <strong style="color: #e11d48; text-decoration: underline !important;">Explore Free Cloud Partner &rarr;</strong></span>
          </a>
        </div>
"""

# Generate all 18 dedicated tool pages
for tool in tools_data:
    page_filename = tool["file"]
    mode = tool.get("mode", "single_pdf_direct")

    # Interactive workspace markup
    interactive_workspace = ""
    if mode == "reorder":
        interactive_workspace = """
      <!-- INTERACTIVE PAGE REORDERING WORKSPACE -->
      <div class="pages-organizer" id="pages-organizer" style="display: none;">
        <div class="organizer-header">
          <div>
            <h3 class="organizer-title">Arrange Page Sequence</h3>
            <p class="organizer-hint">Drag pages or use &larr; / &rarr; arrow buttons to reorder your PDF</p>
          </div>
          <div class="organizer-actions">
            <button type="button" class="btn-primary" id="btn-preview-reordered">
              Preview Final PDF
            </button>
          </div>
        </div>
        <div class="pages-grid" id="pages-grid"></div>
      </div>
        """
    elif mode == "merge":
        interactive_workspace = """
      <!-- INTERACTIVE MERGE FILE ARRANGER WORKSPACE -->
      <div class="pages-organizer" id="pages-organizer" style="display: none;">
        <div class="organizer-header">
          <div>
            <h3 class="organizer-title">Arrange PDF Merge Order</h3>
            <p class="organizer-hint">Drag files or use &uarr; / &darr; to arrange the exact merge sequence</p>
          </div>
          <div class="organizer-actions">
            <button type="button" class="btn-primary" id="btn-preview-merged">
              Merge &amp; Preview Final PDF
            </button>
          </div>
        </div>
        <div class="merge-files-list" id="merge-files-list"></div>
      </div>
        """
    elif mode == "delete":
        interactive_workspace = """
      <!-- INTERACTIVE DELETE PAGES WORKSPACE -->
      <div class="pages-organizer" id="pages-organizer" style="display: none;">
        <div class="organizer-header">
          <div>
            <h3 class="organizer-title">Select Pages to Delete</h3>
            <p class="organizer-hint" id="delete-count-hint">Click on any page thumbnail to delete or restore it</p>
          </div>
          <div class="organizer-actions">
            <button type="button" class="btn-primary" id="btn-preview-deleted">
              Generate &amp; Preview Clean PDF
            </button>
          </div>
        </div>
        <div class="pages-grid" id="pages-grid"></div>
      </div>
        """
    elif mode == "split":
        interactive_workspace = """
      <!-- INTERACTIVE SPLIT PAGES WORKSPACE -->
      <div class="pages-organizer" id="pages-organizer" style="display: none;">
        <div class="organizer-header">
          <div>
            <h3 class="organizer-title">Select Pages to Extract</h3>
            <p class="organizer-hint" id="split-count-hint">Click thumbnails to select pages for extraction</p>
          </div>
          <div class="organizer-actions">
            <button type="button" class="btn-primary" id="btn-preview-split">
              Extract &amp; Preview Final PDF
            </button>
          </div>
        </div>
        <div class="pages-grid" id="pages-grid"></div>
      </div>
        """
    elif mode == "pdf_to_images":
        img_fmt = "PNG" if "png" in page_filename else "JPG"
        hint_id = f"{img_fmt.lower()}-select-hint"
        interactive_workspace = f"""
      <!-- INTERACTIVE {img_fmt} PAGE SELECTION WORKSPACE -->
      <div class="pages-organizer" id="pages-organizer" style="display: none;">
        <div class="organizer-header">
          <div>
            <h3 class="organizer-title">Choose Pages to Download as {img_fmt}</h3>
            <p class="organizer-hint" id="{hint_id}">Click cards to select/deselect pages, or download individual {img_fmt}s instantly</p>
          </div>
          <div class="organizer-actions" style="display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap;">
            <button type="button" class="btn-secondary" id="btn-select-all" style="padding: 0.45rem 0.85rem; font-size: 0.85rem; cursor: pointer;">
              Select All
            </button>
            <button type="button" class="btn-secondary" id="btn-deselect-all" style="padding: 0.45rem 0.85rem; font-size: 0.85rem; cursor: pointer;">
              Deselect All
            </button>
            <button type="button" class="btn-primary" id="btn-download-selected" style="padding: 0.5rem 1.1rem; cursor: pointer;">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="margin-right: 4px; vertical-align: -3px;"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
              Download Selected {img_fmt}s
            </button>
          </div>
        </div>
        <div class="pages-grid" id="pages-grid"></div>
      </div>
        """
    elif mode == "add_text":
        interactive_workspace = """
      <!-- WATERMARK & TEXT STUDIO WORKSPACE -->
      <div class="watermark-studio-card" id="options-card" style="display: none;">
        <!-- File Badge Header -->
        <div class="watermark-file-badge">
          <div style="display: flex; align-items: center; gap: 0.5rem; overflow: hidden;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="flex-shrink:0; color:var(--primary);"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
            <span id="wm-file-name" style="font-weight: 600; color: var(--slate-900); white-space: nowrap; text-overflow: ellipsis; overflow: hidden;">Document.pdf</span>
          </div>
          <div style="display: flex; align-items: center; gap: 0.75rem; flex-shrink: 0;">
            <span id="wm-file-size" style="font-weight: 700; color: var(--slate-600);">-- KB</span>
            <button type="button" class="btn-ctrl" id="btn-change-wm-file" style="font-size: 0.75rem; padding: 0.25rem 0.55rem;">Change File</button>
          </div>
        </div>

        <div style="text-align: center; margin-bottom: 0.25rem;">
          <h3 style="font-size: 1.2rem; font-weight: 700; color: var(--slate-900); margin-bottom: 0.25rem;">Watermark &amp; Text Studio</h3>
          <p style="font-size: 0.85rem; color: var(--slate-500);">Stamp diagonal security watermarks, headers, footers, or page numbers with live visual preview</p>
        </div>

        <!-- Quick Preset Chips -->
        <div class="wm-presets-wrap">
          <span style="font-size: 0.75rem; font-weight: 700; color: var(--slate-500); text-transform: uppercase;">Quick Presets:</span>
          <div class="wm-presets-list">
            <button type="button" class="wm-preset-btn" data-text="CONFIDENTIAL" data-color="#dc2626" data-pos="diagonal-45" data-opacity="0.25" data-size="48">🔴 Confidential</button>
            <button type="button" class="wm-preset-btn" data-text="DRAFT" data-color="#ea580c" data-pos="diagonal-45" data-opacity="0.28" data-size="52">🟠 Draft</button>
            <button type="button" class="wm-preset-btn" data-text="APPROVED" data-color="#16a34a" data-pos="center" data-opacity="0.35" data-size="44">🟢 Approved</button>
            <button type="button" class="wm-preset-btn" data-text="DO NOT COPY" data-color="#2563eb" data-pos="diagonal-45" data-opacity="0.25" data-size="46">🔵 Do Not Copy</button>
            <button type="button" class="wm-preset-btn" data-text="SAMPLE" data-color="#475569" data-pos="diagonal-45" data-opacity="0.22" data-size="56">⚪ Sample</button>
            <button type="button" class="wm-preset-btn" data-text="TOP SECRET" data-color="#b91c1c" data-pos="diagonal-45" data-opacity="0.30" data-size="48">🔒 Top Secret</button>
            <button type="button" class="wm-preset-btn" data-text="Page {n} of {total}" data-color="#334155" data-pos="bottom-center" data-opacity="0.85" data-size="12">📄 Page Numbers</button>
          </div>
        </div>

        <!-- Two-Column Studio Layout: Settings + Live Preview -->
        <div class="wm-studio-grid">
          <!-- Left Column: Controls -->
          <div class="wm-controls-col">
            <!-- Text Content -->
            <div class="option-group">
              <label class="option-label" for="stamp-text">Watermark / Text Content:</label>
              <input type="text" id="stamp-text" class="option-input" value="CONFIDENTIAL" placeholder="e.g. Confidential, Approved, Page {n} of {total}">
              <span style="font-size: 0.72rem; color: var(--slate-400);">Tip: Use <code>{n}</code> for page number and <code>{total}</code> for total pages</span>
            </div>

            <!-- Placement / Position -->
            <div class="option-group">
              <label class="option-label" for="stamp-pos">Placement &amp; Position:</label>
              <select id="stamp-pos" class="option-input">
                <option value="diagonal-45" selected>📐 Diagonal Center (+45°) &mdash; Security Watermark</option>
                <option value="diagonal-minus-45">📐 Diagonal Center (-45°)</option>
                <option value="center">⬛ Center Horizontal (0°)</option>
                <option value="top-center">⬆️ Top Center (Header)</option>
                <option value="top-left">↖️ Top Left</option>
                <option value="top-right">↗️ Top Right</option>
                <option value="bottom-center">⬇️ Bottom Center (Footer / Page Number)</option>
                <option value="bottom-left">↙️ Bottom Left</option>
                <option value="bottom-right">↘️ Bottom Right</option>
              </select>
            </div>

            <!-- Font Family & Size -->
            <div style="display: grid; grid-template-columns: 1.2fr 1fr; gap: 0.75rem;">
              <div class="option-group">
                <label class="option-label" for="stamp-font">Font Style:</label>
                <select id="stamp-font" class="option-input">
                  <option value="HelveticaBold" selected>Helvetica Bold</option>
                  <option value="Helvetica">Helvetica Normal</option>
                  <option value="TimesRomanBold">Times Bold (Serif)</option>
                  <option value="TimesRoman">Times Normal (Serif)</option>
                  <option value="CourierBold">Courier Bold (Mono)</option>
                  <option value="Courier">Courier Normal (Mono)</option>
                </select>
              </div>
              <div class="option-group">
                <div style="display: flex; justify-content: space-between;">
                  <label class="option-label" for="stamp-size">Size (pt):</label>
                  <span id="stamp-size-val" style="font-size: 0.8rem; font-weight: 700; color: var(--primary);">48 pt</span>
                </div>
                <input type="range" id="stamp-size" class="compress-range-input" min="10" max="90" step="2" value="48">
              </div>
            </div>

            <!-- Color & Opacity -->
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
              <div class="option-group">
                <label class="option-label" for="stamp-color">Color:</label>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                  <input type="color" id="stamp-color" value="#dc2626" style="width: 42px; height: 38px; border: 1px solid var(--slate-300); border-radius: 4px; padding: 2px; cursor: pointer;">
                  <span id="stamp-color-hex" style="font-size: 0.85rem; font-family: monospace; color: var(--slate-700);">#DC2626</span>
                </div>
              </div>
              <div class="option-group">
                <div style="display: flex; justify-content: space-between;">
                  <label class="option-label" for="stamp-opacity">Opacity / Transparency:</label>
                  <span id="stamp-opacity-val" style="font-size: 0.8rem; font-weight: 700; color: var(--primary);">25%</span>
                </div>
                <input type="range" id="stamp-opacity" class="compress-range-input" min="5" max="100" step="5" value="25">
              </div>
            </div>

            <!-- Rotation Angle Fine-Tuning -->
            <div class="option-group">
              <div style="display: flex; justify-content: space-between;">
                <label class="option-label" for="stamp-angle">Rotation Angle:</label>
                <span id="stamp-angle-val" style="font-size: 0.8rem; font-weight: 700; color: var(--primary);">+45°</span>
              </div>
              <input type="range" id="stamp-angle" class="compress-range-input" min="-90" max="90" step="5" value="45">
            </div>

            <!-- Target Pages -->
            <div class="option-group">
              <label class="option-label" for="stamp-pages">Apply to Pages:</label>
              <select id="stamp-pages" class="option-input">
                <option value="all" selected>All Pages in Document</option>
                <option value="first">First Page Only</option>
                <option value="not-first">All Pages Except First Page</option>
                <option value="last">Last Page Only</option>
                <option value="custom">Custom Page Range (e.g. 1, 3-5)</option>
              </select>
              <input type="text" id="stamp-custom-range" class="option-input" placeholder="e.g. 1, 3-5" style="display: none; margin-top: 0.35rem;">
            </div>

            <!-- Layer Mode -->
            <div class="option-group">
              <label class="option-label" for="stamp-layer">Layering Mode:</label>
              <select id="stamp-layer" class="option-input">
                <option value="over" selected>Overlay (Stamps over content with transparency)</option>
                <option value="under">Underlay (Watermark beneath document text)</option>
              </select>
            </div>
          </div>

          <!-- Right Column: Live Visual Page Mockup Preview -->
          <div class="wm-preview-col">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
              <span style="font-size: 0.8rem; font-weight: 700; color: var(--slate-700);">Interactive Page Simulation</span>
              <span class="upload-tag" style="font-size: 0.7rem; padding: 0.15rem 0.5rem;">Live Dynamic Preview</span>
            </div>
            <div class="wm-preview-sheet" id="wm-preview-sheet">
              <!-- Faux content lines simulating document -->
              <div class="wm-preview-lines">
                <div class="wm-line line-title"></div>
                <div class="wm-line line-full"></div>
                <div class="wm-line line-full"></div>
                <div class="wm-line line-3-4"></div>
                <div class="wm-line line-full" style="margin-top: 0.75rem;"></div>
                <div class="wm-line line-full"></div>
                <div class="wm-line line-half"></div>
                <div class="wm-line line-full" style="margin-top: 0.75rem;"></div>
                <div class="wm-line line-3-4"></div>
              </div>
              <!-- Live Watermark Text Element -->
              <div id="wm-live-stamp" class="wm-live-stamp">CONFIDENTIAL</div>
            </div>
            <p style="font-size: 0.75rem; color: var(--slate-400); text-align: center; margin-top: 0.5rem;">
              Mockup updates in real-time as you tweak styling &amp; position
            </p>
          </div>
        </div>

        <button type="button" class="action-trigger-btn" id="btn-apply-text" style="background: var(--primary); margin-top: 0.5rem;">
          ⚡ Apply Watermark / Text &amp; Preview Final Document
        </button>
      </div>
        """
    elif mode == "protect":
        interactive_workspace = """
      <div class="protect-options-card" id="options-card" style="display: none;">
        <!-- File Info Badge -->
        <div class="protect-file-badge">
          <div style="display: flex; align-items: center; gap: 0.5rem; overflow: hidden;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="flex-shrink:0; color:var(--primary);"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            <span id="protect-file-name" style="font-weight: 600; color: var(--slate-900); white-space: nowrap; text-overflow: ellipsis; overflow: hidden;">Document.pdf</span>
          </div>
          <div style="display: flex; align-items: center; gap: 0.75rem; flex-shrink: 0;">
            <span id="protect-orig-size" style="font-weight: 700; color: var(--slate-600);">-- KB</span>
            <button type="button" class="btn-ctrl" id="btn-change-protect-file" style="font-size: 0.75rem; padding: 0.25rem 0.55rem;">Change File</button>
          </div>
        </div>

        <div style="text-align: center; margin-bottom: -0.25rem;">
          <h3 style="font-size: 1.25rem; font-weight: 800; color: var(--slate-900); margin-bottom: 0.25rem;">Set PDF Access Password</h3>
          <p style="font-size: 0.85rem; color: var(--slate-500);">Enter a password to encrypt and lock your PDF document</p>
        </div>

        <!-- Password Field with Show/Hide Toggle -->
        <div class="option-group">
          <label class="option-label" for="pdf-password">Document Password:</label>
          <div class="password-input-wrap">
            <input type="password" id="pdf-password" class="option-input" placeholder="Enter password (e.g. MySecretPass123)" autocomplete="new-password">
            <button type="button" class="password-toggle-btn" id="btn-toggle-pass" aria-label="Toggle password visibility" title="Show/Hide Password">
              <svg id="eye-icon-pass" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            </button>
          </div>

          <!-- Password Strength Meter -->
          <div class="strength-meter-wrap">
            <div class="strength-bar-bg">
              <div class="strength-bar-fill" id="pass-strength-fill"></div>
            </div>
            <div class="strength-text-row">
              <span style="color: var(--slate-500);">Strength: <span class="strength-label" id="pass-strength-label">Enter a password</span></span>
              <span style="color: var(--slate-400); font-size: 0.7rem;" id="pass-strength-hint">Min 6 characters recommended</span>
            </div>
          </div>
        </div>

        <!-- Confirm Password Field -->
        <div class="option-group">
          <label class="option-label" for="pdf-confirm-password">Confirm Password:</label>
          <div class="password-input-wrap">
            <input type="password" id="pdf-confirm-password" class="option-input" placeholder="Re-type password to verify" autocomplete="new-password">
            <button type="button" class="password-toggle-btn" id="btn-toggle-confirm" aria-label="Toggle confirm password visibility" title="Show/Hide Password">
              <svg id="eye-icon-confirm" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            </button>
          </div>
          <div class="pass-match-feedback" id="pass-match-feedback" style="display: none;"></div>
        </div>

        <!-- Advanced Security Options (Accordion) -->
        <div class="protect-options-accordion">
          <button type="button" class="protect-accordion-toggle" id="btn-toggle-advanced" aria-expanded="false">
            <span>⚙️ Security &amp; Permissions Settings</span>
            <svg id="accordion-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="transition: transform 0.2s;"><polyline points="6 9 12 15 18 9"/></svg>
          </button>
          <div class="protect-accordion-body" id="protect-advanced-panel" style="display: none;">
            <!-- Encryption Standard -->
            <div>
              <label class="option-label" style="margin-bottom: 0.35rem;">Encryption Algorithm:</label>
              <div class="protect-algo-picker">
                <div class="algo-card active" id="algo-aes" data-algo="AES-256">
                  <div class="algo-card-title">
                    <span>AES-256 bit</span>
                    <span style="color: #059669; font-size: 0.7rem; background: #dcfce7; padding: 2px 6px; border-radius: 9999px;">Recommended</span>
                  </div>
                  <div class="algo-card-desc">Standard ISO 32000 encryption. Supported by modern PDF readers, Acrobat, Chrome, iOS &amp; Android.</div>
                </div>
                <div class="algo-card" id="algo-rc4" data-algo="RC4">
                  <div class="algo-card-title">
                    <span>128-bit RC4</span>
                    <span style="color: var(--slate-500); font-size: 0.7rem;">Legacy</span>
                  </div>
                  <div class="algo-card-desc">High compatibility mode for older PDF readers (Acrobat 5.0+ and legacy devices).</div>
                </div>
              </div>
            </div>

            <!-- Permission Flags -->
            <div>
              <label class="option-label" style="margin-bottom: 0.35rem;">Document Permissions (When Opened):</label>
              <div class="permission-checkbox-group">
                <label class="perm-checkbox-item">
                  <input type="checkbox" id="perm-allow-printing" checked>
                  <span>Allow High-Quality Printing</span>
                </label>
                <label class="perm-checkbox-item">
                  <input type="checkbox" id="perm-allow-copying" checked>
                  <span>Allow Copying Text &amp; Images</span>
                </label>
                <label class="perm-checkbox-item">
                  <input type="checkbox" id="perm-allow-modifying">
                  <span>Allow Modifying Pages &amp; Annotations</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <!-- Privacy & Caution Notice -->
        <div class="security-warning-callout">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          <div>
            <strong>100% Client-Side Privacy Notice:</strong> All encryption executes inside your browser. We never transmit or save your document or passkey. Lost passwords cannot be retrieved.
          </div>
        </div>

        <!-- Protect Button -->
        <button type="button" class="action-trigger-btn" id="btn-apply-protect" style="background: #1e293b;">
          🔒 Encrypt &amp; Protect PDF
        </button>
      </div>
        """
    elif mode == "add_image":
        interactive_workspace = """
      <div class="tool-options-card" id="options-card" style="display: none; max-width: 620px;">
        <h3 style="font-size: 1.15rem; font-weight: 700; color: var(--slate-900); margin-bottom: 0.35rem; text-align: center;">Sign Document Studio</h3>
        <p style="font-size: 0.85rem; color: var(--slate-500); text-align: center; margin-bottom: 1.25rem;">Draw with your finger or mouse, type your name, or upload an image stamp.</p>

        <!-- Signature Mode Tabs -->
        <div style="display: flex; gap: 0.5rem; margin-bottom: 1rem; border-bottom: 1px solid var(--slate-200); padding-bottom: 0.75rem;">
          <button type="button" class="btn-ctrl signature-tab-btn active" id="tab-draw" style="flex: 1; padding: 0.6rem; font-weight: 600;">✍️ Draw Signature</button>
          <button type="button" class="btn-ctrl signature-tab-btn" id="tab-type" style="flex: 1; padding: 0.6rem; font-weight: 600;">🔤 Type Name</button>
          <button type="button" class="btn-ctrl signature-tab-btn" id="tab-upload" style="flex: 1; padding: 0.6rem; font-weight: 600;">📁 Upload Stamp</button>
        </div>

        <!-- Draw Mode Pane -->
        <div id="sig-draw-pane" style="display: block; margin-bottom: 1rem;">
          <div style="border: 2px dashed var(--slate-300); border-radius: 8px; background: #ffffff; position: relative; overflow: hidden;">
            <canvas id="sig-pad" width="560" height="150" style="display: block; width: 100%; height: 150px; touch-action: none; cursor: crosshair;"></canvas>
            <button type="button" id="btn-clear-sig" class="btn-ctrl" style="position: absolute; top: 8px; right: 8px; font-size: 0.75rem; padding: 0.25rem 0.6rem;">Clear</button>
          </div>
          <p style="font-size: 0.75rem; color: var(--slate-400); margin-top: 0.35rem;">Draw smoothly using mouse, trackpad, or touch screen</p>
        </div>

        <!-- Type Mode Pane -->
        <div id="sig-type-pane" style="display: none; margin-bottom: 1rem;">
          <label class="option-label" for="sig-typed-input">Type your signature name:</label>
          <input type="text" id="sig-typed-input" class="option-input" placeholder="e.g. Jane Doe" value="Authorized Signature">
          <div id="sig-typed-preview" style="margin-top: 0.75rem; padding: 0.75rem 1rem; border: 1px solid var(--slate-200); border-radius: 6px; background: #ffffff; font-family: 'Brush Script MT', 'Dancing Script', cursive, sans-serif; font-size: 2.2rem; color: #1e3a8a; text-align: center; min-height: 60px;">
            Authorized Signature
          </div>
        </div>

        <!-- Upload Mode Pane -->
        <div id="sig-upload-pane" style="display: none; margin-bottom: 1rem;">
          <label class="option-label" for="sig-file-input">Choose stamp or signature image (PNG/JPG):</label>
          <input type="file" id="sig-file-input" accept="image/*" class="option-input" style="padding: 0.5rem;">
          <div id="sig-upload-preview" style="margin-top: 0.75rem; text-align: center;"></div>
        </div>

        <!-- Position & Page Selection -->
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.25rem;">
          <div class="option-group">
            <label class="option-label" for="sig-pos">Placement Position:</label>
            <select id="sig-pos" class="option-input">
              <option value="bottom-right">Bottom Right (Standard)</option>
              <option value="bottom-left">Bottom Left</option>
              <option value="bottom-center">Bottom Center</option>
              <option value="top-right">Top Right</option>
              <option value="center">Center Stamp</option>
            </select>
          </div>
          <div class="option-group">
            <label class="option-label" for="sig-page">Target Page:</label>
            <select id="sig-page" class="option-input">
              <option value="last">Last Page (Contracts)</option>
              <option value="first">First Page</option>
              <option value="all">All Pages</option>
            </select>
          </div>
        </div>

        <button type="button" class="action-trigger-btn" id="btn-apply-signature">
          Sign Document &amp; Preview Final PDF
        </button>
      </div>
        """
    elif mode == "compress":
        interactive_workspace = """
      <!-- COMPRESSION LEVEL OPTIONS CARD -->
      <div class="compress-options-card" id="options-card" style="display: none;">
        <div class="compress-file-badge">
          <div style="display: flex; align-items: center; gap: 0.5rem; overflow: hidden;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="flex-shrink:0; color:var(--primary);"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
            <span id="compress-file-name" style="font-weight: 600; color: var(--slate-900); white-space: nowrap; text-overflow: ellipsis; overflow: hidden;">Document.pdf</span>
          </div>
          <div style="display: flex; align-items: center; gap: 0.75rem; flex-shrink: 0;">
            <span id="compress-orig-size" style="font-weight: 700; color: var(--slate-600);">-- KB</span>
            <button type="button" class="btn-ctrl" id="btn-change-compress-file" style="font-size: 0.75rem; padding: 0.25rem 0.55rem;">Change File</button>
          </div>
        </div>

        <div style="text-align: center;">
          <h3 style="font-size: 1.15rem; font-weight: 700; color: var(--slate-900); margin-bottom: 0.25rem;">Select Compression Level</h3>
          <p style="font-size: 0.85rem; color: var(--slate-500);">Choose how much to reduce your PDF or set a custom target percentage</p>
        </div>

        <!-- 3 Level Presets -->
        <div class="compress-levels-grid">
          <!-- Extreme 90% -->
          <div class="compress-level-card" id="level-extreme" data-reduction="90" role="button" tabindex="0">
            <span class="compress-level-badge">Reduce by ~90%</span>
            <div class="compress-level-title">Extreme</div>
            <p class="compress-level-desc">Maximum file size reduction. Lower resolution, readable text. Ideal for strict portal upload limits (under 100KB-500KB) and email attachments.</p>
            <div class="compress-level-est" id="est-extreme">~90% smaller</div>
          </div>

          <!-- Recommended 70% -->
          <div class="compress-level-card active" id="level-recommended" data-reduction="70" role="button" tabindex="0">
            <span class="compress-level-badge">Reduce by ~70%</span>
            <div class="compress-level-title">Recommended</div>
            <p class="compress-level-desc">Optimal balance between sharp visual quality and significant size reduction. Standard for resumes, reports, and archiving.</p>
            <div class="compress-level-est" id="est-recommended">~70% smaller</div>
          </div>

          <!-- Light 40% -->
          <div class="compress-level-card" id="level-light" data-reduction="40" role="button" tabindex="0">
            <span class="compress-level-badge">Reduce by ~40%</span>
            <div class="compress-level-title">Less / Light</div>
            <p class="compress-level-desc">Highest document resolution with moderate compression. Best when maintaining maximum image and typography sharpness is critical.</p>
            <div class="compress-level-est" id="est-light">~40% smaller</div>
          </div>
        </div>

        <!-- Fine-tuning Slider -->
        <div class="compress-slider-box">
          <div class="compress-slider-header">
            <label for="compress-slider" class="compress-slider-label">Target Reduction Percentage:</label>
            <span class="compress-slider-val" id="compress-slider-val">70%</span>
          </div>
          <input type="range" id="compress-slider" class="compress-range-input" min="20" max="95" step="5" value="70">
          <div class="compress-size-estimate">
            <span>Original Size: <strong id="est-orig-label">--</strong></span>
            <span>Estimated Output: <strong id="est-new-label" style="color: #059669;">--</strong></span>
          </div>
        </div>

        <button type="button" class="action-trigger-btn" id="btn-apply-compress" style="background: #059669;">
          ⚡ Compress PDF (Reduce by 70%) &amp; Preview
        </button>
      </div>
        """

    # Prepare JSON-LD schemas and SEO/GEO blocks
    tool_keywords_str = ", ".join(tool.get("keywords", []))
    canonical_url = f"https://pdfdock-ten.vercel.app/{page_filename}"

    # FAQ Schema & Markup
    faq_schema_list = []
    faq_cards_html = ""
    for faq in tool.get("faqs", []):
        faq_schema_list.append({
            "@type": "Question",
            "name": faq["q"],
            "acceptedAnswer": {
                "@type": "Answer",
                "text": faq["a"]
            }
        })
        faq_cards_html += f"""
        <article class="faq-card" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
          <h3 class="faq-question" itemprop="name">{faq["q"]}</h3>
          <div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
            <p class="faq-answer" itemprop="text">{faq["a"]}</p>
          </div>
        </article>
        """

    # HowTo Schema Steps
    howto_schema_steps = []
    for idx, step in enumerate(tool.get("howto_steps", []), 1):
        howto_schema_steps.append({
            "@type": "HowToStep",
            "position": idx,
            "name": step["name"],
            "text": step["text"]
        })

    import json
    schemas_json = json.dumps([
        {
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "name": f"PDFDock {tool['title']}",
            "applicationCategory": "UtilitiesApplication",
            "operatingSystem": "Any Web Browser",
            "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD"
            },
            "description": tool["meta_desc"],
            "featureList": "100% In-Browser Execution, Complete Privacy, No Server Uploads, Mobile Friendly"
        },
        {
            "@context": "https://schema.org",
            "@type": "HowTo",
            "name": f"How to {tool['title']} Online with PDFDock",
            "description": tool["sentence"],
            "step": howto_schema_steps
        },
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": faq_schema_list
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": 1,
                    "name": "Home",
                    "item": "https://pdfdock-ten.vercel.app/"
                },
                {
                    "@type": "ListItem",
                    "position": 2,
                    "name": tool["category_label"],
                    "item": f"https://pdfdock-ten.vercel.app/index.html#{tool['category']}"
                },
                {
                    "@type": "ListItem",
                    "position": 3,
                    "name": tool["title"],
                    "item": canonical_url
                }
            ]
        }
    ], indent=2)

    specs = tool.get("specs", {})
    specs_inputs = specs.get("inputs", "PDF (.pdf)")
    specs_output = specs.get("output", "PDF (.pdf)")
    specs_privacy = specs.get("privacy", "100% In-Browser (0 Server Uploads)")
    specs_speed = specs.get("speed", "Instant Local Processing")

    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <!-- Monetag In-Page Push / Vignette Ad Tag -->
  <script>(function(s){{s.dataset.zone='11833252',s.src='https://nap5k.com/tag.min.js'}})([document.documentElement, document.body].filter(Boolean).pop().appendChild(document.createElement('script')))</script>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{tool["full_title"]} - Free Online PDF Tool | PDFDock</title>
  <meta name="description" content="{tool["meta_desc"]}">
  <meta name="keywords" content="{tool_keywords_str}">
  <link rel="canonical" href="{canonical_url}">
  <meta name="robots" content="index, follow">
  <meta name="google-site-verification" content="google951b33abc70cfe21">

  <!-- OpenGraph / Social Metadata (GEO & Rich Snippets) -->
  <meta property="og:title" content="{tool["full_title"]} - Free Online Tool | PDFDock">
  <meta property="og:description" content="{tool["meta_desc"]}">
  <meta property="og:url" content="{canonical_url}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="PDFDock">
  <meta property="og:image" content="https://pdfdock-ten.vercel.app/gemini-svg.svg">

  <!-- Twitter Card Tags -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{tool["full_title"]} - Free Online Tool | PDFDock">
  <meta name="twitter:description" content="{tool["meta_desc"]}">
  <meta name="twitter:image" content="https://pdfdock-ten.vercel.app/gemini-svg.svg">

  <!-- JSON-LD Structured Data for AI & Search Engines (GEO) -->
  <script type="application/ld+json">
{schemas_json}
  </script>

  <link rel="icon" type="image/svg+xml" href="favicon.svg">
  <link rel="stylesheet" href="styles.css?v=2.5">
  <style>
    .smartlink-banner-link {{ text-decoration: none !important; }}
    .smartlink-card:hover {{ transform: translateY(-2px); border-color: #e11d48 !important; }}
    .smartlink-card:hover .smartlink-action {{ background: #e11d48 !important; }}
    .sponsored-recommendation-link:hover {{ border-color: #e11d48 !important; background: #fff !important; }}
  </style>

  <!-- ADSTERRA / MONETAG HEADER SCRIPT PLACEHOLDER -->
  <!-- START HEADER AD CODE -->
  <!-- Example: Adsterra Popunder or Monetag In-Page Push -->
  <!-- END HEADER AD CODE -->
</head>
<body>
  {make_navbar(page_filename)}

  {make_smartlink_banner("top")}

  <main class="main-wrapper tool-page-wrapper">
    <header class="hero-header">
      <h1 class="hero-title">{tool["full_title"]}</h1>
      <!-- REQUIRED PLAIN SENTENCE: What it is, who it is for, and what job it does -->
      <p class="hero-statement">
        {tool["sentence"]}
      </p>
    </header>

    <!-- THE ONE TOOL AREA -->
    <section class="tool-section" id="tool-container">
      
      <!-- THE ONE BOX: DROPZONE -->
      <div class="upload-box" id="drop-zone" tabindex="0" role="button" aria-label="Upload files for {tool["title"]}">
        <input type="file" id="file-input" accept="{tool["accept"]}" {'multiple' if tool["multiple"] else ''} aria-hidden="true">
        
        <div class="upload-content" id="upload-content">
          <div class="upload-icon" aria-hidden="true">
            {tool["icon"]}
          </div>
          <p class="upload-title">{tool["box_title"]}</p>
          <p class="upload-subtitle">{tool["box_sub"]}</p>
          <span class="upload-tag">100% Free &bull; No Signup &bull; Fast In-Browser</span>
        </div>

        <!-- Processing State -->
        <div class="processing-state" id="processing-state" style="display: none;">
          <div class="spinner" aria-hidden="true"></div>
          <p class="processing-text" id="processing-msg">Loading and rendering document pages...</p>
        </div>
      </div>

      {interactive_workspace}

      <!-- PRE-EXPORT COMPLETE FINAL PDF PREVIEW -->
      <div class="final-preview-container" id="final-preview-container" style="display: none;">
        <div class="final-preview-header">
          <div class="result-check" aria-hidden="true">✓</div>
          <h2 class="final-preview-title">Complete Final PDF Preview</h2>
          <p class="final-preview-sub" id="preview-summary">Scroll and review your final document below before downloading.</p>
        </div>

        <div class="preview-frame-wrap">
          <iframe id="pdf-preview-frame" class="pdf-preview-iframe" title="Complete Final PDF Preview"></iframe>
          <div id="preview-mobile-scroll" class="preview-mobile-scroll"></div>
        </div>

        <div class="final-actions-bar">
          <button type="button" class="btn-primary" id="download-final-btn">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            Download Final PDF
          </button>
          <button type="button" class="btn-secondary" id="rearrange-btn">
            &larr; Re-arrange / Edit Pages
          </button>
        </div>
        {make_download_recommendation()}
      </div>

      <!-- STANDARD RESULT BOX (Used for Non-PDF outputs like JPG/PNG/Text/Word/Excel) -->
      <div class="result-box" id="result-box" style="display: none;">
        <div class="result-check" aria-hidden="true">✓</div>
        <h2 class="result-title">Your File is Ready!</h2>
        <p class="result-summary" id="result-summary">Processed successfully in your browser.</p>

        <div class="result-actions">
          <button type="button" class="btn-primary" id="download-btn">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            Download Result
          </button>
          <button type="button" class="btn-secondary" id="back-to-pages-btn" style="display: none;">
            &larr; Choose Other Pages
          </button>
          <button type="button" class="btn-secondary" id="reset-btn">
            Process Another File
          </button>
        </div>
        {make_download_recommendation()}
      </div>

    </section>

    {make_smartlink_banner("mid")}

    <!-- REAL READABLE FACTS SECTION -->
    <section class="facts-section" aria-labelledby="facts-title">
      <h2 class="facts-heading" id="facts-title">Key Facts &amp; Technical Specifications</h2>
      <div class="facts-grid">
        <article class="fact-card">
          <h3 class="fact-title">100% In-Browser Execution</h3>
          <p class="fact-description">All page rendering and modifications take place strictly inside your browser memory. Documents are never uploaded to remote servers.</p>
        </article>
        <article class="fact-card">
          <h3 class="fact-title">Full Visual Inspection</h3>
          <p class="fact-description">See every page thumbnail in order before making changes, and inspect the complete final document before saving.</p>
        </article>
        <article class="fact-card">
          <h3 class="fact-title">Sub-Second Processing</h3>
          <p class="fact-description">Operates locally at device speed. No waiting in cloud queues or slow upload timeouts.</p>
        </article>
        <article class="fact-card">
          <h3 class="fact-title">Mobile Phone &amp; Touch Optimized</h3>
          <p class="fact-description">Engineered with dedicated touch arrow controls for effortless page shifting on iPhone and Android screens.</p>
        </article>
      </div>
    </section>

    <!-- TECHNICAL SPECIFICATIONS TABLE / GRID (GEO GROUNDING) -->
    <section class="specs-section" aria-labelledby="specs-title">
      <h2 class="facts-heading" id="specs-title">{tool["title"]} Technical Specifications</h2>
      <div class="specs-grid">
        <div class="specs-card">
          <span class="specs-label">Supported Input</span>
          <span class="specs-val">{specs_inputs}</span>
          <span class="specs-note">Native document formats</span>
        </div>
        <div class="specs-card">
          <span class="specs-label">Generated Output</span>
          <span class="specs-val">{specs_output}</span>
          <span class="specs-note">Standard universal format</span>
        </div>
        <div class="specs-card">
          <span class="specs-label">Privacy &amp; Security</span>
          <span class="specs-val">{specs_privacy}</span>
          <span class="specs-note">Zero server uploads</span>
        </div>
        <div class="specs-card">
          <span class="specs-label">Processing Speed</span>
          <span class="specs-val">{specs_speed}</span>
          <span class="specs-note">Hardware-accelerated CPU</span>
        </div>
      </div>
    </section>

    <!-- 3-STEP HOW TO USE GUIDE -->
    <section class="guide-section" aria-labelledby="guide-title">
      <h2 class="facts-heading" id="guide-title">How to Use {tool["title"]}</h2>
      <ol class="steps-list">
        <li class="step-item"><strong>Step 1: {tool["howto_steps"][0]["name"]}</strong> &mdash; {tool["howto_steps"][0]["text"]}</li>
        <li class="step-item"><strong>Step 2: {tool["howto_steps"][1]["name"]}</strong> &mdash; {tool["howto_steps"][1]["text"]}</li>
        <li class="step-item"><strong>Step 3: {tool["howto_steps"][2]["name"]}</strong> &mdash; {tool["howto_steps"][2]["text"]}</li>
      </ol>
    </section>

    <!-- FREQUENTLY ASKED QUESTIONS (GEO & SEARCH SNIPPETS) -->
    <section class="faq-section" aria-labelledby="faq-title">
      <h2 class="facts-heading" id="faq-title">Frequently Asked Questions</h2>
      <div class="faq-list">
        {faq_cards_html}
      </div>
    </section>

    {make_smartlink_banner("bottom")}
  </main>

  {make_footer()}

  <!-- Core Libraries -->
  <script src="js/jspdf.umd.min.js"></script>
  <script src="js/pdf-lib.min.js"></script>
  <script src="js/pdf-encrypt.umd.js"></script>
  <script src="js/pdf.min.js"></script>
  <script src="js/jszip.min.js"></script>
  <script src="js/docx-preview.min.js"></script>
  <script src="js/xlsx.full.min.js"></script>
  <script src="js/mammoth.browser.min.js"></script>
  <script src="js/html2canvas.min.js"></script>
  <script src="js/tools-engine.js"></script>

  <script>
    document.addEventListener('DOMContentLoaded', () => {{
      // Menu Drawer Hover & Click Toggle
      const dropdownWrap = document.querySelector('.nav-dropdown-wrap');
      const drawer = document.getElementById('tools-drawer');
      const menuBtn = document.getElementById('menu-toggle-btn');
      if (dropdownWrap && drawer) {{
        let hideTimer = null;
        const openMenu = () => {{
          clearTimeout(hideTimer);
          drawer.classList.add('show');
          if (menuBtn) menuBtn.setAttribute('aria-expanded', 'true');
        }};
        const closeMenu = () => {{
          hideTimer = setTimeout(() => {{
            drawer.classList.remove('show');
            if (menuBtn) menuBtn.setAttribute('aria-expanded', 'false');
          }}, 220);
        }};

        dropdownWrap.addEventListener('mouseenter', openMenu);
        dropdownWrap.addEventListener('mouseleave', closeMenu);
        drawer.addEventListener('mouseenter', openMenu);
        drawer.addEventListener('mouseleave', closeMenu);

        if (menuBtn) {{
          menuBtn.addEventListener('click', (e) => {{
            e.stopPropagation();
            const isOpen = drawer.classList.toggle('show');
            menuBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
          }});
        }}

        drawer.addEventListener('click', (e) => {{
          if (e.target.tagName !== 'A') e.stopPropagation();
        }});

        document.addEventListener('click', (e) => {{
          if (!dropdownWrap.contains(e.target)) {{
            drawer.classList.remove('show');
            if (menuBtn) menuBtn.setAttribute('aria-expanded', 'false');
          }}
        }});
      }}

      const dropZone = document.getElementById('drop-zone');
      const fileInput = document.getElementById('file-input');
      const uploadContent = document.getElementById('upload-content');
      const processingState = document.getElementById('processing-state');
      const processingMsg = document.getElementById('processing-msg');
      const finalPreviewContainer = document.getElementById('final-preview-container');
      const pdfPreviewFrame = document.getElementById('pdf-preview-frame');
      const previewMobileScroll = document.getElementById('preview-mobile-scroll');
      const previewSummary = document.getElementById('preview-summary');
      const downloadFinalBtn = document.getElementById('download-final-btn');
      const rearrangeBtn = document.getElementById('rearrange-btn');

      const resultBox = document.getElementById('result-box');
      const resultSummary = document.getElementById('result-summary');
      const downloadBtn = document.getElementById('download-btn');
      const resetBtn = document.getElementById('reset-btn');

      const pagesOrganizer = document.getElementById('pages-organizer');
      const pagesGrid = document.getElementById('pages-grid');
      const mergeFilesList = document.getElementById('merge-files-list');
      const optionsCard = document.getElementById('options-card');

      const btnSelectAll = document.getElementById('btn-select-all');
      const btnDeselectAll = document.getElementById('btn-deselect-all');
      const btnDownloadSelected = document.getElementById('btn-download-selected');
      const backToPagesBtn = document.getElementById('back-to-pages-btn');
      const imgSelectHint = document.getElementById('img-select-hint') || document.getElementById('jpg-select-hint') || document.getElementById('png-select-hint');

      let selectedFiles = [];
      let currentPdfFile = null;
      let renderedPages = []; // array of {{ pageNum, originalIndex, canvas }}
      let selectedPageNumbers = new Set();
      let finalPdfBlob = null;
      let finalPdfUrl = null;
      let finalFilename = 'pdfdock-output.pdf';

      // Drag & Drop for upload zone
      ['dragenter', 'dragover'].forEach(n => {{
        dropZone.addEventListener(n, (e) => {{ e.preventDefault(); dropZone.classList.add('dragover'); }});
      }});
      ['dragleave', 'dragend', 'drop'].forEach(n => {{
        dropZone.addEventListener(n, (e) => {{ e.preventDefault(); dropZone.classList.remove('dragover'); }});
      }});

      dropZone.addEventListener('drop', (e) => {{
        if (e.dataTransfer && e.dataTransfer.files.length) handleFiles(e.dataTransfer.files);
      }});
      fileInput.addEventListener('change', (e) => {{
        if (e.target.files.length) handleFiles(e.target.files);
      }});
      dropZone.addEventListener('click', () => {{
        fileInput.click();
      }});
      dropZone.addEventListener('keydown', (e) => {{
        if (e.key === 'Enter' || e.key === ' ') {{ e.preventDefault(); fileInput.click(); }}
      }});

      // Handle Files
      async function handleFiles(files) {{
        selectedFiles = Array.from(files);
        if (!selectedFiles.length) return;

        const toolMode = "{mode}";

        if (toolMode === "pdf_to_images") {{
          currentPdfFile = selectedFiles[0];
          uploadContent.style.display = 'none';
          processingMsg.textContent = "Rendering PDF pages for preview...";
          processingState.style.display = 'flex';

          try {{
            renderedPages = await window.PDFDock.renderPdfPagesToCanvases(currentPdfFile, 0.5);
            buildImageSelectionGrid();
            dropZone.style.display = 'none';
            processingState.style.display = 'none';
            pagesOrganizer.style.display = 'block';
          }} catch (err) {{
            alert('Error rendering PDF: ' + err.message);
            uploadContent.style.display = 'flex';
            processingState.style.display = 'none';
          }}
        }} else if (toolMode === "reorder" || toolMode === "delete" || toolMode === "split") {{
          currentPdfFile = selectedFiles[0];
          uploadContent.style.display = 'none';
          processingMsg.textContent = "Rendering all PDF pages in order...";
          processingState.style.display = 'flex';

          try {{
            renderedPages = await window.PDFDock.renderPdfPagesToCanvases(currentPdfFile, 0.45);
            buildPagesGrid(toolMode);
            dropZone.style.display = 'none';
            processingState.style.display = 'none';
            pagesOrganizer.style.display = 'block';
          }} catch (err) {{
            alert('Error rendering PDF: ' + err.message);
            uploadContent.style.display = 'flex';
            processingState.style.display = 'none';
          }}
        }} else if (toolMode === "merge") {{
          dropZone.style.display = 'none';
          pagesOrganizer.style.display = 'block';
          buildMergeFilesList();
        }} else if (toolMode === "compress") {{
          currentPdfFile = selectedFiles[0];
          dropZone.style.display = 'none';
          optionsCard.style.display = 'flex';
          initCompressOptions();
        }} else if (toolMode === "add_text") {{
          currentPdfFile = selectedFiles[0];
          dropZone.style.display = 'none';
          optionsCard.style.display = 'flex';
          initWatermarkStudio();
        }} else if (toolMode === "protect") {{
          currentPdfFile = selectedFiles[0];
          dropZone.style.display = 'none';
          optionsCard.style.display = 'flex';
          initProtectStudio();
        }} else if (toolMode === "add_image") {{
          let pdfF = null, imgF = null;
          selectedFiles.forEach(f => {{
            if (f.name.toLowerCase().endsWith('.pdf') || f.type.includes('pdf')) pdfF = f;
            else if (f.type.startsWith('image/')) imgF = f;
          }});
          if (!pdfF && selectedFiles[0] && (selectedFiles[0].type.includes('pdf') || selectedFiles[0].name.toLowerCase().endsWith('.pdf'))) {{
            pdfF = selectedFiles[0];
          }}
          if (!pdfF) {{
            alert('Please select a PDF file to sign or stamp.');
            return;
          }}
          currentPdfFile = pdfF;
          dropZone.style.display = 'none';
          optionsCard.style.display = 'flex';
          initSignaturePad();
          if (imgF) {{
            switchSigTab('upload');
            handleStampImageUpload(imgF);
          }}
        }} else {{
          // Direct execution tools (Compress, JPG->PDF, Word->PDF, etc.)
          executeDirectTool();
        }}
      }}

      // Build Pages Selection Grid for PDF -> Images (JPG / PNG)
      function buildImageSelectionGrid() {{
        if (!pagesGrid) return;
        pagesGrid.innerHTML = '';
        selectedPageNumbers = new Set();
        const imgExt = "{tool.get('id', '')}".includes('png') ? 'PNG' : 'JPG';

        renderedPages.forEach((pageObj, idx) => {{
          const pageNum = idx + 1;
          selectedPageNumbers.add(pageNum);

          const card = document.createElement('div');
          card.className = 'page-card is-selected';
          card.dataset.pageNum = pageNum;
          card.style.cursor = 'pointer';

          const header = document.createElement('div');
          header.className = 'page-card-header';
          header.innerHTML = `
            <span class="page-card-checkbox">✓</span>
            <span class="page-badge">Page ${{pageNum}}</span>
          `;
          card.appendChild(header);

          const canvasWrap = document.createElement('div');
          canvasWrap.className = 'card-canvas-wrap';

          if (pageObj.dataUrl) {{
            const img = document.createElement('img');
            img.src = pageObj.dataUrl;
            img.alt = `Page ${{pageNum}} preview`;
            img.className = 'page-card-preview-img';
            canvasWrap.appendChild(img);
          }} else if (pageObj.canvas) {{
            const copyCanvas = document.createElement('canvas');
            copyCanvas.width = pageObj.canvas.width;
            copyCanvas.height = pageObj.canvas.height;
            const copyCtx = copyCanvas.getContext('2d');
            copyCtx.drawImage(pageObj.canvas, 0, 0);
            copyCanvas.className = 'page-card-preview-img';
            canvasWrap.appendChild(copyCanvas);
          }}
          card.appendChild(canvasWrap);

          const controls = document.createElement('div');
          controls.className = 'page-card-controls';
          const btnDl = document.createElement('button');
          btnDl.type = 'button';
          btnDl.className = 'btn-ctrl btn-download-page';
          btnDl.innerHTML = `⬇ Download Page ${{pageNum}}`;
          btnDl.title = `Download Page ${{pageNum}} as ${{imgExt}}`;
          btnDl.onclick = (e) => {{
            e.stopPropagation();
            downloadSingleImage(pageNum);
          }};
          controls.appendChild(btnDl);
          card.appendChild(controls);

          // Clicking card toggles selection
          card.onclick = () => {{
            if (selectedPageNumbers.has(pageNum)) {{
              selectedPageNumbers.delete(pageNum);
              card.classList.remove('is-selected');
              card.classList.add('is-deselected');
            }} else {{
              selectedPageNumbers.add(pageNum);
              card.classList.remove('is-deselected');
              card.classList.add('is-selected');
            }}
            updateImageSelectionState();
          }};

          pagesGrid.appendChild(card);
        }});

        updateImageSelectionState();
      }}

      function updateImageSelectionState() {{
        const total = renderedPages.length;
        const count = selectedPageNumbers.size;
        const imgExt = "{tool.get('id', '')}".includes('png') ? 'PNG' : 'JPG';
        if (imgSelectHint) {{
          imgSelectHint.textContent = `Selected ${{count}} of ${{total}} page(s) • Click cards to toggle selection`;
        }}
        if (btnDownloadSelected) {{
          if (count === 1) {{
            const pNum = Array.from(selectedPageNumbers)[0];
            btnDownloadSelected.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="margin-right: 4px; vertical-align: -3px;"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg> Download Page ${{pNum}} ${{imgExt}}`;
          }} else {{
            btnDownloadSelected.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="margin-right: 4px; vertical-align: -3px;"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg> Download ${{count}} Selected ${{imgExt}}s`;
          }}
        }}
      }}

      function triggerDirectDownload(blob, filename) {{
        const a = document.createElement('a');
        const url = URL.createObjectURL(blob);
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        setTimeout(() => {{
          document.body.removeChild(a);
          URL.revokeObjectURL(url);
        }}, 1500);
      }}

      async function downloadSingleImage(pageNum) {{
        if (!currentPdfFile) return;
        const isPng = "{tool.get('id', '')}".includes('png');
        const imgExt = isPng ? 'PNG' : 'JPG';
        pagesOrganizer.style.display = 'none';
        dropZone.style.display = 'flex';
        uploadContent.style.display = 'none';
        processingMsg.textContent = `Converting Page ${{pageNum}} to high-resolution ${{imgExt}}...`;
        processingState.style.display = 'flex';

        try {{
          const result = isPng
            ? await window.PDFDock.pdfToPng(currentPdfFile, {{ selectedPages: [pageNum] }})
            : await window.PDFDock.pdfToJpg(currentPdfFile, {{ selectedPages: [pageNum] }});
          triggerDirectDownload(result.blob, result.filename);
          showStandardResult(result.blob, result.filename, result.summary);
        }} catch (err) {{
          alert('Error converting page: ' + err.message);
          pagesOrganizer.style.display = 'block';
          dropZone.style.display = 'none';
          processingState.style.display = 'none';
        }}
      }}

      async function downloadSelectedImages() {{
        if (!currentPdfFile) return;
        const isPng = "{tool.get('id', '')}".includes('png');
        const imgExt = isPng ? 'PNG' : 'JPG';
        const selected = Array.from(selectedPageNumbers).sort((a, b) => a - b);
        if (selected.length === 0) {{
          alert('Please select at least one page to download.');
          return;
        }}

        pagesOrganizer.style.display = 'none';
        dropZone.style.display = 'flex';
        uploadContent.style.display = 'none';
        processingMsg.textContent = `Converting ${{selected.length}} selected page(s) to high-resolution ${{imgExt}}...`;
        processingState.style.display = 'flex';

        try {{
          const result = isPng
            ? await window.PDFDock.pdfToPng(currentPdfFile, {{ selectedPages: selected }})
            : await window.PDFDock.pdfToJpg(currentPdfFile, {{ selectedPages: selected }});
          triggerDirectDownload(result.blob, result.filename);
          showStandardResult(result.blob, result.filename, result.summary);
        }} catch (err) {{
          alert('Error converting pages: ' + err.message);
          pagesOrganizer.style.display = 'block';
          dropZone.style.display = 'none';
          processingState.style.display = 'none';
        }}
      }}

      // Build Pages Grid for Reorder, Delete, Split
      function buildPagesGrid(mode) {{
        if (!pagesGrid) return;
        pagesGrid.innerHTML = '';

        renderedPages.forEach((pageObj, idx) => {{
          const card = document.createElement('div');
          card.className = 'page-card';
          card.setAttribute('draggable', mode === 'reorder' ? 'true' : 'false');
          card.dataset.index = idx;
          card.dataset.original = pageObj.originalIndex;

          const header = document.createElement('div');
          header.className = 'page-card-header';
          header.innerHTML = `<span class="page-badge">#${{idx + 1}}</span> <span>Orig. p.${{pageObj.originalIndex + 1}}</span>`;
          card.appendChild(header);

          const canvasWrap = document.createElement('div');
          canvasWrap.className = 'card-canvas-wrap';

          if (pageObj.dataUrl) {{
            const img = document.createElement('img');
            img.src = pageObj.dataUrl;
            img.alt = `Page ${{idx + 1}} preview`;
            img.className = 'page-card-preview-img';
            canvasWrap.appendChild(img);
          }} else if (pageObj.canvas) {{
            const copyCanvas = document.createElement('canvas');
            copyCanvas.width = pageObj.canvas.width;
            copyCanvas.height = pageObj.canvas.height;
            const copyCtx = copyCanvas.getContext('2d');
            copyCtx.drawImage(pageObj.canvas, 0, 0);
            copyCanvas.className = 'page-card-preview-img';
            canvasWrap.appendChild(copyCanvas);
          }}
          card.appendChild(canvasWrap);

          const controls = document.createElement('div');
          controls.className = 'page-card-controls';

          if (mode === 'reorder') {{
            const btnLeft = document.createElement('button');
            btnLeft.className = 'btn-ctrl';
            btnLeft.innerHTML = '&larr; Left';
            btnLeft.title = 'Move Left';
            btnLeft.onclick = (e) => {{ e.stopPropagation(); movePage(idx, idx - 1); }};

            const btnRight = document.createElement('button');
            btnRight.className = 'btn-ctrl';
            btnRight.innerHTML = 'Right &rarr;';
            btnRight.title = 'Move Right';
            btnRight.onclick = (e) => {{ e.stopPropagation(); movePage(idx, idx + 1); }};

            controls.appendChild(btnLeft);
            controls.appendChild(btnRight);
          }} else if (mode === 'delete') {{
            const btnDel = document.createElement('button');
            btnDel.className = 'btn-ctrl btn-del';
            btnDel.textContent = '✕ Remove';
            btnDel.onclick = (e) => {{
              e.stopPropagation();
              card.classList.toggle('marked-delete');
              btnDel.textContent = card.classList.contains('marked-delete') ? '✓ Keep' : '✕ Remove';
              updateDeleteCount();
            }};
            controls.appendChild(btnDel);
          }} else if (mode === 'split') {{
            card.onclick = () => card.classList.toggle('drag-target');
            controls.innerHTML = '<span style="font-size:0.75rem;color:var(--slate-500);">Tap to select</span>';
          }}

          card.appendChild(controls);

          // Drag and drop events for desktop
          if (mode === 'reorder') {{
            card.addEventListener('dragstart', (e) => {{
              card.classList.add('dragging');
              e.dataTransfer.setData('text/plain', idx);
            }});
            card.addEventListener('dragend', () => card.classList.remove('dragging'));
            card.addEventListener('dragover', (e) => {{
              e.preventDefault();
              card.classList.add('drag-target');
            }});
            card.addEventListener('dragleave', () => card.classList.remove('drag-target'));
            card.addEventListener('drop', (e) => {{
              e.preventDefault();
              card.classList.remove('drag-target');
              const fromIdx = parseInt(e.dataTransfer.getData('text/plain'), 10);
              const toIdx = idx;
              if (fromIdx !== toIdx) movePage(fromIdx, toIdx);
            }});
          }}

          pagesGrid.appendChild(card);
        }});
      }}

      function movePage(from, to) {{
        if (to < 0 || to >= renderedPages.length) return;
        const item = renderedPages.splice(from, 1)[0];
        renderedPages.splice(to, 0, item);
        buildPagesGrid("{mode}");
      }}

      function updateDeleteCount() {{
        const allCards = pagesGrid.querySelectorAll('.page-card');
        const deletedCards = pagesGrid.querySelectorAll('.page-card.marked-delete');
        const countHint = document.getElementById('delete-count-hint');
        if (countHint) {{
          countHint.textContent = `Keeping ${{allCards.length - deletedCards.length}} of ${{allCards.length}} pages (Deleting ${{deletedCards.length}})`;
        }}
      }}

      // Build Merge Files List
      function buildMergeFilesList() {{
        if (!mergeFilesList) return;
        mergeFilesList.innerHTML = '';

        selectedFiles.forEach((file, idx) => {{
          const row = document.createElement('div');
          row.className = 'merge-file-row';
          row.innerHTML = `
            <div class="merge-file-info">
              <span class="merge-file-idx">#${{idx + 1}}</span>
              <div>
                <p class="merge-file-name">${{file.name}}</p>
                <p class="merge-file-meta">${{window.PDFDock.formatBytes(file.size)}}</p>
              </div>
            </div>
            <div class="merge-file-actions">
              <button type="button" class="btn-ctrl" title="Move Up" onclick="moveMergeFile(${{idx}}, ${{idx - 1}})" ${{idx === 0 ? 'disabled style="opacity:0.3;"' : ''}}>&uarr;</button>
              <button type="button" class="btn-ctrl" title="Move Down" onclick="moveMergeFile(${{idx}}, ${{idx + 1}})" ${{idx === selectedFiles.length - 1 ? 'disabled style="opacity:0.3;"' : ''}}>&darr;</button>
              <button type="button" class="btn-ctrl btn-del" title="Remove" onclick="removeMergeFile(${{idx}})">✕</button>
            </div>
          `;
          mergeFilesList.appendChild(row);
        }});
      }}

      window.moveMergeFile = function(from, to) {{
        if (to < 0 || to >= selectedFiles.length) return;
        const f = selectedFiles.splice(from, 1)[0];
        selectedFiles.splice(to, 0, f);
        buildMergeFilesList();
      }};

      window.removeMergeFile = function(idx) {{
        selectedFiles.splice(idx, 1);
        if (selectedFiles.length === 0) {{
          pagesOrganizer.style.display = 'none';
          dropZone.style.display = 'flex';
          uploadContent.style.display = 'flex';
          fileInput.value = '';
        }} else {{
          buildMergeFilesList();
        }}
      }};

      // Action Handlers
      const btnPreviewReordered = document.getElementById('btn-preview-reordered');
      if (btnPreviewReordered) {{
        btnPreviewReordered.addEventListener('click', async () => {{
          const orderIndices = renderedPages.map(p => p.originalIndex);
          pagesOrganizer.style.display = 'none';
          dropZone.style.display = 'flex';
          uploadContent.style.display = 'none';
          processingMsg.textContent = "Compiling reordered PDF...";
          processingState.style.display = 'flex';

          try {{
            const result = await window.PDFDock.reorderPdfPagesByArray(currentPdfFile, orderIndices);
            showFinalPdfPreview(result.blob, result.filename, result.summary);
          }} catch (err) {{
            alert('Error: ' + err.message);
            pagesOrganizer.style.display = 'block';
            dropZone.style.display = 'none';
            processingState.style.display = 'none';
          }}
        }});
      }}

      const btnPreviewMerged = document.getElementById('btn-preview-merged');
      if (btnPreviewMerged) {{
        btnPreviewMerged.addEventListener('click', async () => {{
          if (selectedFiles.length < 2) {{
            alert('Please add at least 2 PDF files to merge.');
            return;
          }}
          pagesOrganizer.style.display = 'none';
          dropZone.style.display = 'flex';
          uploadContent.style.display = 'none';
          processingMsg.textContent = "Merging all PDFs in arranged order...";
          processingState.style.display = 'flex';

          try {{
            const result = await window.PDFDock.mergePdfOrdered(selectedFiles);
            showFinalPdfPreview(result.blob, result.filename, result.summary);
          }} catch (err) {{
            alert('Error: ' + err.message);
            pagesOrganizer.style.display = 'block';
            dropZone.style.display = 'none';
            processingState.style.display = 'none';
          }}
        }});
      }}

      const btnPreviewDeleted = document.getElementById('btn-preview-deleted');
      if (btnPreviewDeleted) {{
        btnPreviewDeleted.addEventListener('click', async () => {{
          const cards = pagesGrid.querySelectorAll('.page-card');
          const keepIndices = [];
          cards.forEach((c) => {{
            if (!c.classList.contains('marked-delete')) {{
              keepIndices.push(parseInt(c.dataset.original, 10));
            }}
          }});

          if (keepIndices.length === 0) {{
            alert('You must keep at least one page in the document.');
            return;
          }}

          pagesOrganizer.style.display = 'none';
          dropZone.style.display = 'flex';
          uploadContent.style.display = 'none';
          processingMsg.textContent = "Creating clean PDF with deleted pages removed...";
          processingState.style.display = 'flex';

          try {{
            const result = await window.PDFDock.deletePdfPagesByIndices(currentPdfFile, keepIndices);
            showFinalPdfPreview(result.blob, result.filename, result.summary);
          }} catch (err) {{
            alert('Error: ' + err.message);
            pagesOrganizer.style.display = 'block';
            dropZone.style.display = 'none';
            processingState.style.display = 'none';
          }}
        }});
      }}

      const btnPreviewSplit = document.getElementById('btn-preview-split');
      if (btnPreviewSplit) {{
        btnPreviewSplit.addEventListener('click', async () => {{
          const cards = pagesGrid.querySelectorAll('.page-card.drag-target');
          let extractIndices = [];
          cards.forEach(c => extractIndices.push(parseInt(c.dataset.original, 10)));
          if (!extractIndices.length) {{
            // Default to page 1 if none highlighted
            extractIndices = [0];
          }}
          pagesOrganizer.style.display = 'none';
          dropZone.style.display = 'flex';
          uploadContent.style.display = 'none';
          processingMsg.textContent = "Extracting selected pages...";
          processingState.style.display = 'flex';

          try {{
            const result = await window.PDFDock.reorderPdfPagesByArray(currentPdfFile, extractIndices);
            result.filename = `split-extracted-${{currentPdfFile.name}}`;
            result.summary = `Extracted ${{extractIndices.length}} selected page(s) into a separate document.`;
            showFinalPdfPreview(result.blob, result.filename, result.summary);
          }} catch (err) {{
            alert('Error: ' + err.message);
            pagesOrganizer.style.display = 'block';
            dropZone.style.display = 'none';
            processingState.style.display = 'none';
          }}
        }});
      }}

      // Watermark & Text Studio Logic
      function initWatermarkStudio() {{
        if (!currentPdfFile) return;

        const nameEl = document.getElementById('wm-file-name');
        const sizeEl = document.getElementById('wm-file-size');
        const btnChangeFile = document.getElementById('btn-change-wm-file');

        if (nameEl) nameEl.textContent = currentPdfFile.name;
        if (sizeEl) sizeEl.textContent = window.PDFDock.formatBytes(currentPdfFile.size);

        if (btnChangeFile) {{
          btnChangeFile.onclick = () => {{
            optionsCard.style.display = 'none';
            dropZone.style.display = 'flex';
            uploadContent.style.display = 'flex';
            fileInput.value = '';
          }};
        }}

        const textInput = document.getElementById('stamp-text');
        const posSelect = document.getElementById('stamp-pos');
        const fontSelect = document.getElementById('stamp-font');
        const sizeInput = document.getElementById('stamp-size');
        const sizeVal = document.getElementById('stamp-size-val');
        const colorInput = document.getElementById('stamp-color');
        const colorHex = document.getElementById('stamp-color-hex');
        const opacityInput = document.getElementById('stamp-opacity');
        const opacityVal = document.getElementById('stamp-opacity-val');
        const angleInput = document.getElementById('stamp-angle');
        const angleVal = document.getElementById('stamp-angle-val');
        const pagesSelect = document.getElementById('stamp-pages');
        const customRangeInput = document.getElementById('stamp-custom-range');
        const liveStamp = document.getElementById('wm-live-stamp');
        const previewSheet = document.getElementById('wm-preview-sheet');

        function updateWatermarkPreview() {{
          if (!liveStamp || !previewSheet) return;

          const text = (textInput ? textInput.value : '') || 'CONFIDENTIAL';
          const pos = posSelect ? posSelect.value : 'diagonal-45';
          const font = fontSelect ? fontSelect.value : 'HelveticaBold';
          const size = parseInt(sizeInput ? sizeInput.value : 48, 10);
          const color = colorInput ? colorInput.value : '#dc2626';
          const opacity = parseInt(opacityInput ? opacityInput.value : 25, 10) / 100;
          const customAngle = parseInt(angleInput ? angleInput.value : 45, 10);

          if (sizeVal) sizeVal.textContent = size + ' pt';
          if (colorHex) colorHex.textContent = color.toUpperCase();
          if (opacityVal) opacityVal.textContent = Math.round(opacity * 100) + '%';
          if (angleVal) angleVal.textContent = (customAngle > 0 ? '+' : '') + customAngle + '°';

          // Sample simulation text
          const displayText = text.split('{{n}}').join('1').split('{{page}}').join('1').split('{{total}}').join('5').split('{{pages}}').join('5');
          liveStamp.textContent = displayText;
          liveStamp.style.color = color;
          liveStamp.style.opacity = opacity;

          if (font.includes('Times')) {{
            liveStamp.style.fontFamily = '"Times New Roman", Times, serif';
          }} else if (font.includes('Courier')) {{
            liveStamp.style.fontFamily = '"Courier New", Courier, monospace';
          }} else {{
            liveStamp.style.fontFamily = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
          }}
          liveStamp.style.fontWeight = font.includes('Bold') ? '800' : '500';

          const scaledSize = Math.max(9, Math.round(size * 0.42));
          liveStamp.style.fontSize = scaledSize + 'px';

          let angle = customAngle;
          if (pos === 'diagonal-45') angle = 45;
          else if (pos === 'diagonal-minus-45') angle = -45;
          else if (pos === 'center') angle = customAngle;

          liveStamp.style.top = 'auto';
          liveStamp.style.bottom = 'auto';
          liveStamp.style.left = 'auto';
          liveStamp.style.right = 'auto';

          if (pos === 'diagonal-45' || pos === 'diagonal-minus-45' || pos === 'center') {{
            liveStamp.style.top = '50%';
            liveStamp.style.left = '50%';
            liveStamp.style.transform = 'translate(-50%, -50%) rotate(' + (-angle) + 'deg)';
          }} else if (pos === 'top-center') {{
            liveStamp.style.top = '10px';
            liveStamp.style.left = '50%';
            liveStamp.style.transform = 'translateX(-50%) rotate(' + (-angle) + 'deg)';
          }} else if (pos === 'top-left') {{
            liveStamp.style.top = '10px';
            liveStamp.style.left = '10px';
            liveStamp.style.transform = 'rotate(' + (-angle) + 'deg)';
          }} else if (pos === 'top-right') {{
            liveStamp.style.top = '10px';
            liveStamp.style.right = '10px';
            liveStamp.style.transform = 'rotate(' + (-angle) + 'deg)';
          }} else if (pos === 'bottom-center') {{
            liveStamp.style.bottom = '10px';
            liveStamp.style.left = '50%';
            liveStamp.style.transform = 'translateX(-50%) rotate(' + (-angle) + 'deg)';
          }} else if (pos === 'bottom-left') {{
            liveStamp.style.bottom = '10px';
            liveStamp.style.left = '10px';
            liveStamp.style.transform = 'rotate(' + (-angle) + 'deg)';
          }} else if (pos === 'bottom-right') {{
            liveStamp.style.bottom = '10px';
            liveStamp.style.right = '10px';
            liveStamp.style.transform = 'rotate(' + (-angle) + 'deg)';
          }}
        }}

        // Preset buttons
        const presetButtons = document.querySelectorAll('.wm-preset-btn');
        presetButtons.forEach(btn => {{
          btn.onclick = () => {{
            const pText = btn.dataset.text;
            const pColor = btn.dataset.color;
            const pPos = btn.dataset.pos;
            const pOpacity = parseFloat(btn.dataset.opacity) * 100;
            const pSize = parseInt(btn.dataset.size, 10);

            if (textInput && pText) textInput.value = pText;
            if (colorInput && pColor) colorInput.value = pColor;
            if (posSelect && pPos) posSelect.value = pPos;
            if (opacityInput && !isNaN(pOpacity)) opacityInput.value = pOpacity;
            if (sizeInput && !isNaN(pSize)) sizeInput.value = pSize;
            if (angleInput) {{
              if (pPos === 'diagonal-45') angleInput.value = 45;
              else if (pPos === 'diagonal-minus-45') angleInput.value = -45;
              else angleInput.value = 0;
            }}
            updateWatermarkPreview();
          }};
        }});

        // Input listeners
        if (textInput) textInput.oninput = updateWatermarkPreview;
        if (colorInput) colorInput.oninput = updateWatermarkPreview;
        if (sizeInput) sizeInput.oninput = updateWatermarkPreview;
        if (opacityInput) opacityInput.oninput = updateWatermarkPreview;
        if (angleInput) angleInput.oninput = updateWatermarkPreview;
        if (fontSelect) fontSelect.onchange = updateWatermarkPreview;

        if (posSelect) {{
          posSelect.onchange = () => {{
            if (posSelect.value === 'diagonal-45' && angleInput) angleInput.value = 45;
            else if (posSelect.value === 'diagonal-minus-45' && angleInput) angleInput.value = -45;
            else if (posSelect.value.startsWith('bottom') || posSelect.value.startsWith('top')) {{
              if (angleInput && (angleInput.value === '45' || angleInput.value === '-45')) angleInput.value = 0;
              if (sizeInput && parseInt(sizeInput.value, 10) > 24) sizeInput.value = 14;
              if (opacityInput && parseInt(opacityInput.value, 10) < 50) opacityInput.value = 85;
            }}
            updateWatermarkPreview();
          }};
        }}

        if (pagesSelect && customRangeInput) {{
          pagesSelect.onchange = () => {{
            customRangeInput.style.display = pagesSelect.value === 'custom' ? 'block' : 'none';
          }};
        }}

        updateWatermarkPreview();
      }}

      // Add Text Action
      const btnApplyText = document.getElementById('btn-apply-text');
      if (btnApplyText) {{
        btnApplyText.addEventListener('click', async () => {{
          if (!currentPdfFile) return;

          const text = (document.getElementById('stamp-text') ? document.getElementById('stamp-text').value : '') || 'CONFIDENTIAL';
          const pos = document.getElementById('stamp-pos') ? document.getElementById('stamp-pos').value : 'diagonal-45';
          const font = document.getElementById('stamp-font') ? document.getElementById('stamp-font').value : 'HelveticaBold';
          const size = parseInt(document.getElementById('stamp-size') ? document.getElementById('stamp-size').value : 48, 10);
          const color = document.getElementById('stamp-color') ? document.getElementById('stamp-color').value : '#dc2626';
          const opacity = (parseInt(document.getElementById('stamp-opacity') ? document.getElementById('stamp-opacity').value : 25, 10)) / 100;
          const angle = parseInt(document.getElementById('stamp-angle') ? document.getElementById('stamp-angle').value : 45, 10);
          const pages = document.getElementById('stamp-pages') ? document.getElementById('stamp-pages').value : 'all';
          const customRange = (document.getElementById('stamp-custom-range') ? document.getElementById('stamp-custom-range').value : '').trim();
          const layer = document.getElementById('stamp-layer') ? document.getElementById('stamp-layer').value : 'over';

          optionsCard.style.display = 'none';
          dropZone.style.display = 'flex';
          uploadContent.style.display = 'none';
          processingMsg.textContent = "Applying custom watermark & text styling to PDF...";
          processingState.style.display = 'flex';

          try {{
            const result = await window.PDFDock.addTextToPdf(currentPdfFile, text, {{
              position: pos,
              fontFamily: font,
              fontSize: size,
              color: color,
              opacity: opacity,
              rotation: angle,
              pages: pages,
              pageRange: customRange,
              layer: layer
            }});
            showFinalPdfPreview(result.blob, result.filename, result.summary);
          }} catch (err) {{
            alert('Error adding watermark/text: ' + err.message);
            optionsCard.style.display = 'flex';
            dropZone.style.display = 'none';
            processingState.style.display = 'none';
          }}
        }});
      }}

      // Protect PDF Studio Logic
      let protectInitialized = false;
      let selectedProtectAlgo = 'AES-256';

      function initProtectStudio() {{
        if (!currentPdfFile) return;

        const nameEl = document.getElementById('protect-file-name');
        const origSizeEl = document.getElementById('protect-orig-size');
        const btnChangeFile = document.getElementById('btn-change-protect-file');
        const passInput = document.getElementById('pdf-password');
        const confirmInput = document.getElementById('pdf-confirm-password');
        const btnTogglePass = document.getElementById('btn-toggle-pass');
        const btnToggleConfirm = document.getElementById('btn-toggle-confirm');
        const strengthFill = document.getElementById('pass-strength-fill');
        const strengthLabel = document.getElementById('pass-strength-label');
        const strengthHint = document.getElementById('pass-strength-hint');
        const matchFeedback = document.getElementById('pass-match-feedback');
        const btnToggleAdvanced = document.getElementById('btn-toggle-advanced');
        const advancedPanel = document.getElementById('protect-advanced-panel');
        const accordionArrow = document.getElementById('accordion-arrow');
        const algoAes = document.getElementById('algo-aes');
        const algoRc4 = document.getElementById('algo-rc4');

        if (nameEl) nameEl.textContent = currentPdfFile.name;
        if (origSizeEl) origSizeEl.textContent = window.PDFDock.formatBytes(currentPdfFile.size);

        if (btnChangeFile) {{
          btnChangeFile.onclick = () => {{
            optionsCard.style.display = 'none';
            dropZone.style.display = 'flex';
            uploadContent.style.display = 'flex';
            fileInput.value = '';
            if (passInput) passInput.value = '';
            if (confirmInput) confirmInput.value = '';
            updateProtectPasswordState();
          }};
        }}

        function updateProtectPasswordState() {{
          const pass = passInput ? passInput.value : '';
          const confirm = confirmInput ? confirmInput.value : '';

          // Strength calculation
          let score = 0;
          if (pass.length >= 6) score++;
          if (pass.length >= 10) score++;
          if (/[A-Z]/.test(pass) && /[a-z]/.test(pass)) score++;
          if (/[0-9]/.test(pass)) score++;
          if (/[^A-Za-z0-9]/.test(pass)) score++;

          if (strengthFill && strengthLabel && strengthHint) {{
            strengthFill.className = 'strength-bar-fill';
            strengthLabel.className = 'strength-label';

            if (pass.length === 0) {{
              strengthFill.style.width = '0%';
              strengthLabel.textContent = 'Enter a password';
              strengthHint.textContent = 'Min 6 characters recommended';
            }} else if (pass.length < 6 || score <= 1) {{
              strengthFill.classList.add('weak');
              strengthLabel.classList.add('weak');
              strengthLabel.textContent = 'Weak';
              strengthHint.textContent = 'Add numbers, symbols & length';
            }} else if (score <= 3) {{
              strengthFill.classList.add('medium');
              strengthLabel.classList.add('medium');
              strengthLabel.textContent = 'Good / Medium';
              strengthHint.textContent = 'Strong enough for everyday use';
            }} else {{
              strengthFill.classList.add('strong');
              strengthLabel.classList.add('strong');
              strengthLabel.textContent = 'Very Strong';
              strengthHint.textContent = 'High entropy, maximum security';
            }}
          }}

          // Match check
          if (matchFeedback) {{
            if (confirm.length === 0) {{
              matchFeedback.style.display = 'none';
            }} else if (pass === confirm) {{
              matchFeedback.style.display = 'flex';
              matchFeedback.className = 'pass-match-feedback match';
              matchFeedback.innerHTML = '✓ Passwords match';
            }} else {{
              matchFeedback.style.display = 'flex';
              matchFeedback.className = 'pass-match-feedback mismatch';
              matchFeedback.innerHTML = '✕ Passwords do not match';
            }}
          }}
        }}

        if (!protectInitialized) {{
          protectInitialized = true;

          if (passInput) passInput.addEventListener('input', updateProtectPasswordState);
          if (confirmInput) confirmInput.addEventListener('input', updateProtectPasswordState);

          function toggleVisibility(inputEl, btnEl) {{
            if (!inputEl) return;
            const isPass = inputEl.type === 'password';
            inputEl.type = isPass ? 'text' : 'password';
            btnEl.innerHTML = isPass
              ? '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>'
              : '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>';
            btnEl.title = isPass ? 'Hide Password' : 'Show Password';
          }}

          if (btnTogglePass && passInput) {{
            btnTogglePass.addEventListener('click', () => toggleVisibility(passInput, btnTogglePass));
          }}
          if (btnToggleConfirm && confirmInput) {{
            btnToggleConfirm.addEventListener('click', () => toggleVisibility(confirmInput, btnToggleConfirm));
          }}

          // Advanced settings accordion toggle
          if (btnToggleAdvanced && advancedPanel) {{
            btnToggleAdvanced.addEventListener('click', () => {{
              const isHidden = advancedPanel.style.display === 'none';
              advancedPanel.style.display = isHidden ? 'flex' : 'none';
              btnToggleAdvanced.setAttribute('aria-expanded', isHidden ? 'true' : 'false');
              if (accordionArrow) {{
                accordionArrow.style.transform = isHidden ? 'rotate(180deg)' : 'rotate(0deg)';
              }}
            }});
          }}

          // Algorithm selection
          if (algoAes && algoRc4) {{
            algoAes.addEventListener('click', () => {{
              algoAes.classList.add('active');
              algoRc4.classList.remove('active');
              selectedProtectAlgo = 'AES-256';
            }});
            algoRc4.addEventListener('click', () => {{
              algoRc4.classList.add('active');
              algoAes.classList.remove('active');
              selectedProtectAlgo = 'RC4';
            }});
          }}
        }}

        updateProtectPasswordState();
        if (passInput) passInput.focus();
      }}

      function showProtectedResult(blob, filename, summaryText, algorithm, appliedPassword) {{
        finalPdfBlob = blob;
        window.finalPdfBlob = blob;
        finalFilename = filename;
        if (finalPdfUrl) URL.revokeObjectURL(finalPdfUrl);
        finalPdfUrl = URL.createObjectURL(blob);

        const resCheck = resultBox.querySelector('.result-check');
        if (resCheck) {{
          resCheck.innerHTML = '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>';
          resCheck.style.background = '#059669';
        }}
        const resTitle = resultBox.querySelector('.result-title');
        if (resTitle) resTitle.textContent = 'Your PDF is Securely Protected!';

        const algoLabel = algorithm === 'AES-256' ? 'AES-256 bit' : '128-bit RC4';
        resultSummary.innerHTML = `
          <div class="protected-badge">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            <span>Lock Active &bull; ${{algoLabel}} Encryption</span>
          </div>
          <p style="margin: 0.35rem 0 0.5rem; color: var(--slate-800); font-weight: 700; font-size: 1.05rem;">${{filename}}</p>
          <p style="margin: 0 0 0.75rem; font-size: 0.85rem; color: var(--slate-500);">${{summaryText}} (${{window.PDFDock.formatBytes(blob.size)}})</p>
          <div style="margin: 0.75rem auto 1.25rem; max-width: 480px; padding: 0.75rem 1rem; background: #f8fafc; border: 1px dashed var(--slate-300); border-radius: 8px; font-size: 0.82rem; color: var(--slate-600); text-align: left; line-height: 1.5;">
            🔒 <strong>Verification Guarantee:</strong> When you open this PDF in Adobe Acrobat, Google Chrome, Microsoft Edge, or Apple Preview, you will be prompted to enter your password before any content is shown.
          </div>
        `;

        if (downloadBtn) {{
          downloadBtn.innerHTML = `
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            Download Protected PDF
          `;
        }}

        dropZone.style.display = 'none';
        processingState.style.display = 'none';
        if (optionsCard) optionsCard.style.display = 'none';
        resultBox.style.display = 'block';
      }}

      // Protect PDF Action
      const btnApplyProtect = document.getElementById('btn-apply-protect');
      if (btnApplyProtect) {{
        btnApplyProtect.addEventListener('click', async () => {{
          if (!currentPdfFile) return;

          const passInput = document.getElementById('pdf-password');
          const confirmInput = document.getElementById('pdf-confirm-password');
          const pass = (passInput ? passInput.value : '').trim();
          const confirm = (confirmInput ? confirmInput.value : '').trim();

          if (!pass) {{
            alert('Please enter a password to protect your PDF.');
            if (passInput) passInput.focus();
            return;
          }}

          if (confirmInput && pass !== confirm) {{
            alert('Password and Confirm Password do not match. Please re-enter.');
            if (confirmInput) confirmInput.focus();
            return;
          }}

          const allowPrint = document.getElementById('perm-allow-printing') ? document.getElementById('perm-allow-printing').checked : true;
          const allowCopy = document.getElementById('perm-allow-copying') ? document.getElementById('perm-allow-copying').checked : true;
          const allowMod = document.getElementById('perm-allow-modifying') ? document.getElementById('perm-allow-modifying').checked : false;

          optionsCard.style.display = 'none';
          dropZone.style.display = 'flex';
          uploadContent.style.display = 'none';
          processingMsg.textContent = `Applying ${{selectedProtectAlgo}} encryption & locking PDF...`;
          processingState.style.display = 'flex';

          try {{
            const result = await window.PDFDock.protectPdf(currentPdfFile, pass, {{
              algorithm: selectedProtectAlgo,
              allowPrinting: allowPrint,
              allowCopying: allowCopy,
              allowModifying: allowMod
            }});
            showProtectedResult(result.blob, result.filename, result.summary, result.algorithm, pass);
          }} catch (err) {{
            alert('Error protecting PDF: ' + err.message);
            optionsCard.style.display = 'flex';
            dropZone.style.display = 'none';
            processingState.style.display = 'none';
          }}
        }});
      }}

      // Compress PDF Options Logic
      let currentReductionTarget = 70;
      let compressSampleCache = {{}};

      function initCompressOptions() {{
        if (!currentPdfFile) return;
        compressSampleCache = {{}};
        const nameEl = document.getElementById('compress-file-name');
        const origSizeEl = document.getElementById('compress-orig-size');
        const estOrigLabel = document.getElementById('est-orig-label');
        const estNewLabel = document.getElementById('est-new-label');
        const slider = document.getElementById('compress-slider');
        const sliderVal = document.getElementById('compress-slider-val');
        const btnCompress = document.getElementById('btn-apply-compress');
        const btnChangeFile = document.getElementById('btn-change-compress-file');

        if (btnChangeFile) {{
          btnChangeFile.onclick = () => {{
            optionsCard.style.display = 'none';
            dropZone.style.display = 'flex';
            uploadContent.style.display = 'flex';
            fileInput.value = '';
          }};
        }}

        const origBytes = currentPdfFile.size;
        const origFormatted = window.PDFDock.formatBytes(origBytes);

        if (nameEl) nameEl.textContent = currentPdfFile.name;
        if (origSizeEl) origSizeEl.textContent = origFormatted;
        if (estOrigLabel) estOrigLabel.textContent = origFormatted;

        let currentEstimateReq = 0;

        async function updateReductionUI(reduction) {{
          currentReductionTarget = reduction;
          if (slider) slider.value = reduction;
          if (sliderVal) sliderVal.textContent = reduction + '%';

          // Update card active states
          const cards = document.querySelectorAll('.compress-level-card');
          cards.forEach(card => {{
            const cardRed = parseInt(card.dataset.reduction, 10);
            card.classList.toggle('active', cardRed === reduction);
          }});

          if (btnCompress) {{
            btnCompress.textContent = `⚡ Compress PDF (Reduce by ${{reduction}}%) & Preview`;
          }}

          const reqId = ++currentEstimateReq;

          // Check sample cache first for immediate update
          if (compressSampleCache[reduction] && typeof compressSampleCache[reduction].estimatedBytes === 'number') {{
            const est = compressSampleCache[reduction];
            if (estNewLabel) estNewLabel.textContent = '~' + window.PDFDock.formatBytes(est.estimatedBytes) + ` (-${{est.savingsPercent}}%)`;
            return;
          }}

          // If estimator is available, sample Page 1 at target scale & quality
          if (window.PDFDock && window.PDFDock.estimateCompressedPdfSize) {{
            try {{
              const est = await window.PDFDock.estimateCompressedPdfSize(currentPdfFile, reduction, compressSampleCache);
              if (reqId === currentEstimateReq && estNewLabel) {{
                estNewLabel.textContent = '~' + window.PDFDock.formatBytes(est.estimatedBytes) + ` (-${{est.savingsPercent}}%)`;
              }}
            }} catch (err) {{
              const estBytes = Math.max(1024, Math.round(origBytes * (1 - reduction / 100)));
              if (estNewLabel) estNewLabel.textContent = '~' + window.PDFDock.formatBytes(estBytes) + ` (-${{reduction}}%)`;
            }}
          }} else {{
            const estBytes = Math.max(1024, Math.round(origBytes * (1 - reduction / 100)));
            if (estNewLabel) estNewLabel.textContent = '~' + window.PDFDock.formatBytes(estBytes) + ` (-${{reduction}}%)`;
          }}
        }}

        // Card clicks
        const cards = document.querySelectorAll('.compress-level-card');
        cards.forEach(card => {{
          card.onclick = () => {{
            const red = parseInt(card.dataset.reduction, 10);
            updateReductionUI(red);
          }};
          card.onkeydown = (e) => {{
            if (e.key === 'Enter' || e.key === ' ') {{
              e.preventDefault();
              const red = parseInt(card.dataset.reduction, 10);
              updateReductionUI(red);
            }}
          }};
        }});

        // Slider input
        if (slider) {{
          slider.oninput = (e) => {{
            const val = parseInt(e.target.value, 10);
            updateReductionUI(val);
          }};
        }}

        // Default to Recommended 70%
        updateReductionUI(70);
      }}

      const btnApplyCompress = document.getElementById('btn-apply-compress');
      if (btnApplyCompress) {{
        btnApplyCompress.addEventListener('click', async () => {{
          if (!currentPdfFile) return;
          optionsCard.style.display = 'none';
          dropZone.style.display = 'flex';
          uploadContent.style.display = 'none';
          processingMsg.textContent = `Compressing PDF to reduce file size by ~${{currentReductionTarget}}%...`;
          processingState.style.display = 'flex';

          try {{
            const result = await window.PDFDock.compressPdf(currentPdfFile, {{
              targetReduction: currentReductionTarget,
              sampleCache: compressSampleCache
            }});
            showFinalPdfPreview(result.blob, result.filename, result.summary);
          }} catch (err) {{
            alert('Error compressing PDF: ' + err.message);
            optionsCard.style.display = 'flex';
            dropZone.style.display = 'none';
            processingState.style.display = 'none';
          }}
        }});
      }}

      // Sign PDF & Add Image Studio
      let sigPadCanvas = null;
      let sigPadCtx = null;
      let isDrawingSig = false;
      let sigHasDrawn = false;
      let activeSigMode = 'draw';
      let uploadedStampSource = null;

      function generateTypedSignatureImage(text) {{
        const c = document.createElement('canvas');
        c.width = 600;
        c.height = 150;
        const ctx = c.getContext('2d');
        ctx.clearRect(0, 0, c.width, c.height);
        ctx.font = 'italic 50px "Brush Script MT", "Dancing Script", cursive, sans-serif';
        ctx.fillStyle = '#1e3a8a';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(text, c.width / 2, c.height / 2);
        return c.toDataURL('image/png');
      }}

      function handleStampImageUpload(file) {{
        const reader = new FileReader();
        reader.onload = (e) => {{
          uploadedStampSource = e.target.result;
          const previewDiv = document.getElementById('sig-upload-preview');
          if (previewDiv) {{
            previewDiv.innerHTML = `<img src="${{uploadedStampSource}}" alt="Stamp Preview" style="max-height: 80px; max-width: 100%; border: 1px solid var(--slate-300); border-radius: 4px; padding: 4px; background: #fff;">`;
          }}
        }};
        reader.readAsDataURL(file);
      }}

      function switchSigTab(mode) {{
        activeSigMode = mode;
        const tabDraw = document.getElementById('tab-draw');
        const tabType = document.getElementById('tab-type');
        const tabUpload = document.getElementById('tab-upload');
        const paneDraw = document.getElementById('sig-draw-pane');
        const paneType = document.getElementById('sig-type-pane');
        const paneUpload = document.getElementById('sig-upload-pane');

        if (tabDraw) tabDraw.classList.toggle('active', mode === 'draw');
        if (tabType) tabType.classList.toggle('active', mode === 'type');
        if (tabUpload) tabUpload.classList.toggle('active', mode === 'upload');

        if (paneDraw) paneDraw.style.display = mode === 'draw' ? 'block' : 'none';
        if (paneType) paneType.style.display = mode === 'type' ? 'block' : 'none';
        if (paneUpload) paneUpload.style.display = mode === 'upload' ? 'block' : 'none';
      }}

      function initSignaturePad() {{
        sigPadCanvas = document.getElementById('sig-pad');
        if (!sigPadCanvas) return;
        sigPadCtx = sigPadCanvas.getContext('2d');
        sigPadCtx.lineWidth = 2.5;
        sigPadCtx.lineCap = 'round';
        sigPadCtx.lineJoin = 'round';
        sigPadCtx.strokeStyle = '#1e3a8a';

        function getCanvasPos(e) {{
          const rect = sigPadCanvas.getBoundingClientRect();
          const clientX = e.touches ? e.touches[0].clientX : e.clientX;
          const clientY = e.touches ? e.touches[0].clientY : e.clientY;
          const scaleX = sigPadCanvas.width / rect.width;
          const scaleY = sigPadCanvas.height / rect.height;
          return {{
            x: (clientX - rect.left) * scaleX,
            y: (clientY - rect.top) * scaleY
          }};
        }}

        function startDraw(e) {{
          isDrawingSig = true;
          sigHasDrawn = true;
          const pos = getCanvasPos(e);
          sigPadCtx.beginPath();
          sigPadCtx.moveTo(pos.x, pos.y);
          if (e.touches) e.preventDefault();
        }}

        function moveDraw(e) {{
          if (!isDrawingSig) return;
          const pos = getCanvasPos(e);
          sigPadCtx.lineTo(pos.x, pos.y);
          sigPadCtx.stroke();
          if (e.touches) e.preventDefault();
        }}

        function stopDraw(e) {{
          if (!isDrawingSig) return;
          isDrawingSig = false;
          if (e.touches) e.preventDefault();
        }}

        sigPadCanvas.addEventListener('mousedown', startDraw);
        sigPadCanvas.addEventListener('mousemove', moveDraw);
        window.addEventListener('mouseup', stopDraw);

        sigPadCanvas.addEventListener('touchstart', startDraw, {{ passive: false }});
        sigPadCanvas.addEventListener('touchmove', moveDraw, {{ passive: false }});
        sigPadCanvas.addEventListener('touchend', stopDraw, {{ passive: false }});

        const btnClearSig = document.getElementById('btn-clear-sig');
        if (btnClearSig) {{
          btnClearSig.addEventListener('click', () => {{
            sigPadCtx.clearRect(0, 0, sigPadCanvas.width, sigPadCanvas.height);
            sigHasDrawn = false;
          }});
        }}

        const tabDraw = document.getElementById('tab-draw');
        const tabType = document.getElementById('tab-type');
        const tabUpload = document.getElementById('tab-upload');
        if (tabDraw) tabDraw.addEventListener('click', () => switchSigTab('draw'));
        if (tabType) tabType.addEventListener('click', () => switchSigTab('type'));
        if (tabUpload) tabUpload.addEventListener('click', () => switchSigTab('upload'));

        const sigTypedInput = document.getElementById('sig-typed-input');
        const sigTypedPreview = document.getElementById('sig-typed-preview');
        if (sigTypedInput && sigTypedPreview) {{
          sigTypedInput.addEventListener('input', (e) => {{
            sigTypedPreview.textContent = e.target.value || '(Empty)';
          }});
        }}

        const sigFileInput = document.getElementById('sig-file-input');
        if (sigFileInput) {{
          sigFileInput.addEventListener('change', (e) => {{
            if (e.target.files && e.target.files.length) {{
              handleStampImageUpload(e.target.files[0]);
            }}
          }});
        }}
      }}

      const btnApplySignature = document.getElementById('btn-apply-signature');
      if (btnApplySignature) {{
        btnApplySignature.addEventListener('click', async () => {{
          let sigSource = null;
          if (activeSigMode === 'draw') {{
            if (!sigHasDrawn) {{
              alert('Please draw your signature first or switch to Type / Upload Stamp.');
              return;
            }}
            sigSource = sigPadCanvas.toDataURL('image/png');
          }} else if (activeSigMode === 'type') {{
            const typedText = (document.getElementById('sig-typed-input').value || '').trim();
            if (!typedText) {{
              alert('Please type your name for the signature.');
              return;
            }}
            sigSource = generateTypedSignatureImage(typedText);
          }} else if (activeSigMode === 'upload') {{
            if (!uploadedStampSource) {{
              alert('Please select an image stamp or signature file.');
              return;
            }}
            sigSource = uploadedStampSource;
          }}

          if (!sigSource) {{
            alert('Please provide a signature or image stamp.');
            return;
          }}

          const position = document.getElementById('sig-pos') ? document.getElementById('sig-pos').value : 'bottom-right';
          const targetPage = document.getElementById('sig-page') ? document.getElementById('sig-page').value : 'last';

          optionsCard.style.display = 'none';
          dropZone.style.display = 'flex';
          uploadContent.style.display = 'none';
          processingMsg.textContent = "Signing PDF document...";
          processingState.style.display = 'flex';

          try {{
            const result = await window.PDFDock.addImageToPdf(currentPdfFile, sigSource, {{ position, targetPage }});
            showFinalPdfPreview(result.blob, result.filename, result.summary);
          }} catch (err) {{
            alert('Error signing PDF: ' + err.message);
            optionsCard.style.display = 'flex';
            dropZone.style.display = 'none';
            processingState.style.display = 'none';
          }}
        }});
      }}

      // Direct Tool Execution (Compress, JPG->PDF, Word->PDF, etc.)
      async function executeDirectTool() {{
        uploadContent.style.display = 'none';
        const fileExt = (selectedFiles[0] && selectedFiles[0].name) ? selectedFiles[0].name.split('.').pop().toLowerCase() : '';
        if (fileExt === 'docx') {{
          processingMsg.textContent = "Converting Word document layout, styles & tables into PDF...";
        }} else if (fileExt === 'xlsx' || fileExt === 'xls' || fileExt === 'csv') {{
          processingMsg.textContent = "Formatting Excel sheets & gridlines into PDF...";
        }} else if (fileExt === 'pptx' || fileExt === 'ppt') {{
          processingMsg.textContent = "Rendering PowerPoint presentation slides into PDF...";
        }} else {{
          processingMsg.textContent = "Processing file in browser...";
        }}
        processingState.style.display = 'flex';

        try {{
          let result;
          const mode = "{mode}";
          if (mode === "images_to_pdf") {{
            result = await {tool.get("action_call", "window.PDFDock.jpgToPdf(selectedFiles)")};
          }} else if (mode === "pdf_to_images") {{
            result = await {tool.get("action_call", "window.PDFDock.pdfToJpg(selectedFiles[0])")};
          }} else if (mode === "doc_to_pdf" || mode === "single_pdf_direct") {{
            result = await {tool.get("action_call", "window.PDFDock.compressPdf(selectedFiles[0])")};
          }} else if (mode === "add_image") {{
            return;
          }}

          if (result.blob.type === 'application/pdf') {{
            showFinalPdfPreview(result.blob, result.filename, result.summary);
          }} else {{
            // Non-PDF output (ZIP, JPG, PNG, DOC, XLSX, TXT)
            showStandardResult(result.blob, result.filename, result.summary);
          }}
        }} catch (err) {{
          alert('Error: ' + err.message);
          uploadContent.style.display = 'flex';
          processingState.style.display = 'none';
        }}
      }}

      // Display Complete Pre-Export PDF Preview
      async function showFinalPdfPreview(blob, filename, summaryText) {{
        finalPdfBlob = blob;
        finalFilename = filename;
        if (finalPdfUrl) URL.revokeObjectURL(finalPdfUrl);
        finalPdfUrl = URL.createObjectURL(blob);

        previewSummary.textContent = summaryText + ` (${{window.PDFDock.formatBytes(blob.size)}})`;
        pdfPreviewFrame.src = finalPdfUrl + '#toolbar=1&navpanes=0';

        // Also render scrollable previews for mobile browsers
        try {{
          const previewPages = await window.PDFDock.renderPdfPagesToCanvases(blob, 0.6);
          previewMobileScroll.innerHTML = '';
          previewPages.forEach(p => {{
            if (p.dataUrl) {{
              const img = document.createElement('img');
              img.src = p.dataUrl;
              img.alt = `Page ${{p.pageNum}} preview`;
              img.style.maxWidth = '100%';
              img.style.height = 'auto';
              img.style.display = 'block';
              img.style.borderRadius = '4px';
              img.style.boxShadow = '0 2px 8px rgba(0,0,0,0.15)';
              img.style.marginBottom = '1rem';
              previewMobileScroll.appendChild(img);
            }} else {{
              previewMobileScroll.appendChild(p.canvas);
            }}
          }});
        }} catch (e) {{
          console.warn('Mobile canvas preview fallback skipped', e);
        }}

        if (rearrangeBtn) {{
          const tMode = "{mode}";
          if (tMode === "compress") {{
            rearrangeBtn.innerHTML = '&larr; Change Compression Level';
          }} else if (tMode === "reorder" || tMode === "delete" || tMode === "split" || tMode === "merge") {{
            rearrangeBtn.innerHTML = '&larr; Re-arrange / Edit Pages';
          }} else if (tMode === "add_text") {{
            rearrangeBtn.innerHTML = '&larr; Modify Watermark Settings';
          }} else if (tMode === "protect" || tMode === "add_image") {{
            rearrangeBtn.innerHTML = '&larr; Modify Settings';
          }} else {{
            rearrangeBtn.innerHTML = '&larr; Convert Another File';
          }}
        }}

        dropZone.style.display = 'none';
        processingState.style.display = 'none';
        if (pagesOrganizer) pagesOrganizer.style.display = 'none';
        if (optionsCard) optionsCard.style.display = 'none';
        finalPreviewContainer.style.display = 'block';
      }}

      // Display Standard Result Box (for non-PDF outputs)
      function showStandardResult(blob, filename, summaryText) {{
        finalPdfBlob = blob;
        finalFilename = filename;
        if (finalPdfUrl) URL.revokeObjectURL(finalPdfUrl);
        finalPdfUrl = URL.createObjectURL(blob);

        resultSummary.textContent = summaryText + ` (${{window.PDFDock.formatBytes(blob.size)}})`;
        dropZone.style.display = 'none';
        processingState.style.display = 'none';
        if (pagesOrganizer) pagesOrganizer.style.display = 'none';
        if (backToPagesBtn && renderedPages && renderedPages.length > 0) {{
          backToPagesBtn.style.display = 'inline-flex';
        }}
        resultBox.style.display = 'block';
      }}

      // Download Handler
      downloadFinalBtn.addEventListener('click', () => {{
        if (!finalPdfUrl) return;
        const a = document.createElement('a');
        a.href = finalPdfUrl;
        a.download = finalFilename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
      }});

      if (downloadBtn) {{
        downloadBtn.addEventListener('click', () => {{
          if (!finalPdfUrl) return;
          const a = document.createElement('a');
          a.href = finalPdfUrl;
          a.download = finalFilename;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
        }});
      }}

      // Wire up selection action buttons
      if (btnSelectAll) {{
        btnSelectAll.addEventListener('click', () => {{
          renderedPages.forEach((_, idx) => selectedPageNumbers.add(idx + 1));
          if (pagesGrid) {{
            pagesGrid.querySelectorAll('.page-card').forEach(card => {{
              card.classList.remove('is-deselected');
              card.classList.add('is-selected');
            }});
          }}
          if (typeof updateImageSelectionState === 'function') updateImageSelectionState();
        }});
      }}

      if (btnDeselectAll) {{
        btnDeselectAll.addEventListener('click', () => {{
          selectedPageNumbers.clear();
          if (pagesGrid) {{
            pagesGrid.querySelectorAll('.page-card').forEach(card => {{
              card.classList.remove('is-selected');
              card.classList.add('is-deselected');
            }});
          }}
          if (typeof updateImageSelectionState === 'function') updateImageSelectionState();
        }});
      }}

      if (btnDownloadSelected) {{
        btnDownloadSelected.addEventListener('click', () => {{
          if (typeof downloadSelectedImages === 'function') downloadSelectedImages();
        }});
      }}

      if (backToPagesBtn) {{
        backToPagesBtn.addEventListener('click', () => {{
          resultBox.style.display = 'none';
          if (pagesOrganizer) pagesOrganizer.style.display = 'block';
        }});
      }}

      // Rearrange / Edit Pages Button
      rearrangeBtn.addEventListener('click', () => {{
        finalPreviewContainer.style.display = 'none';
        if (pagesOrganizer) {{
          pagesOrganizer.style.display = 'block';
        }} else if (optionsCard) {{
          optionsCard.style.display = 'flex';
        }} else {{
          dropZone.style.display = 'flex';
          uploadContent.style.display = 'flex';
        }}
      }});

      if (resetBtn) {{
        resetBtn.addEventListener('click', () => {{
          resultBox.style.display = 'none';
          dropZone.style.display = 'flex';
          uploadContent.style.display = 'flex';
          fileInput.value = '';
          const p1 = document.getElementById('pdf-password');
          const p2 = document.getElementById('pdf-confirm-password');
          if (p1) p1.value = '';
          if (p2) p2.value = '';
          const resCheck = resultBox.querySelector('.result-check');
          if (resCheck) {{
            resCheck.innerHTML = '✓';
            resCheck.style.background = 'var(--success)';
          }}
          const resTitle = resultBox.querySelector('.result-title');
          if (resTitle) resTitle.textContent = 'Your File is Ready!';
          if (downloadBtn) {{
            downloadBtn.innerHTML = `
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
              Download Result
            `;
          }}
        }});
      }}
    }});
  </script>

  <!-- ADSTERRA / MONETAG FOOTER SCRIPT PLACEHOLDER -->
  <!-- START FOOTER AD CODE -->
  <!-- Example: Adsterra Social Bar or Monetag OnClick -->
  <!-- END FOOTER AD CODE -->
</body>
</html>
"""
    with open(page_filename, "w", encoding="utf-8") as f:
        f.write(page_html)
    print(f"Generated {page_filename}")

# Generate index.html (PDFDock Main Portal)
tool_cards_html = ""
for t in tools_data:
    tool_cards_html += f"""
      <a href="{t["file"]}" class="tool-card" data-category="{t["category"]}">
        <span class="tool-card-badge">{t["badge"]}</span>
        <div class="tool-card-icon" aria-hidden="true">{t["icon"]}</div>
        <h3 class="tool-card-title">{t["title"]}</h3>
        <p class="tool-card-desc">{t["sentence"]}</p>
      </a>
    """

import json
index_schemas_json = json.dumps([
    {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "PDFDock",
        "url": "https://pdfdock-ten.vercel.app/",
        "description": "PDFDock: Everything You Need, All in One Place. 100% free, private online PDF tools with no signup.",
        "potentialAction": {
            "@type": "SearchAction",
            "target": "https://pdfdock-ten.vercel.app/?q={search_term_string}",
            "query-input": "required name=search_term_string"
        }
    },
    {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": "PDFDock Online PDF Suite",
        "url": "https://pdfdock-ten.vercel.app/",
        "applicationCategory": "UtilitiesApplication",
        "operatingSystem": "Any Web Browser",
        "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "USD"
        },
        "description": "Comprehensive suite of 100% free client-side PDF tools. Merge, split, compress, convert, sign, and protect documents with complete in-browser privacy.",
        "featureList": "Zero server uploads, 100% in-browser processing, No signup required, Fast CPU execution"
    }
], indent=2)

index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <!-- Monetag In-Page Push / Vignette Ad Tag -->
  <script>(function(s){{s.dataset.zone='11833252',s.src='https://nap5k.com/tag.min.js'}})([document.documentElement, document.body].filter(Boolean).pop().appendChild(document.createElement('script')))</script>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>PDFDock - Everything You Need, All in One Place | Free Online PDF Tools</title>
  <meta name="description" content="PDFDock: Everything You Need, All in One Place. 100% free, private online PDF tools with no signup. Merge, split, compress, convert, edit, and sign PDFs in browser.">
  <meta name="keywords" content="online pdf tools, pdf editor free, convert pdf online, free pdf tools no signup, merge compress pdf, pdf converter, client side pdf tools">
  <link rel="canonical" href="https://pdfdock-ten.vercel.app/">
  <meta name="robots" content="index, follow">
  <meta name="google-site-verification" content="google951b33abc70cfe21">

  <!-- OpenGraph / Social (GEO Metadata) -->
  <meta property="og:title" content="PDFDock - Everything You Need, All in One Place">
  <meta property="og:description" content="100% free, private online PDF tools with no signup. Merge, split, compress, convert, edit, and sign PDFs directly in browser.">
  <meta property="og:url" content="https://pdfdock-ten.vercel.app/">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="PDFDock">
  <meta property="og:image" content="https://pdfdock-ten.vercel.app/gemini-svg.svg">

  <!-- Twitter Cards -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="PDFDock - Everything You Need, All in One Place">
  <meta name="twitter:description" content="100% free, private online PDF tools with no signup. Merge, split, compress, convert, edit, and sign PDFs directly in browser.">
  <meta name="twitter:image" content="https://pdfdock-ten.vercel.app/gemini-svg.svg">

  <!-- JSON-LD Structured Data for AI & Search Engines -->
  <script type="application/ld+json">
{index_schemas_json}
  </script>

  <link rel="icon" type="image/svg+xml" href="favicon.svg">
  <link rel="stylesheet" href="styles.css?v=2.5">
  <style>
    .smartlink-banner-link {{ text-decoration: none !important; }}
    .smartlink-card:hover {{ transform: translateY(-2px); border-color: #e11d48 !important; }}
    .smartlink-card:hover .smartlink-action {{ background: #e11d48 !important; }}
    .sponsored-recommendation-link:hover {{ border-color: #e11d48 !important; background: #fff !important; }}
  </style>

  <!-- ADSTERRA / MONETAG HEADER SCRIPT PLACEHOLDER -->
  <!-- START HEADER AD CODE -->
  <!-- Example: Adsterra Popunder or Monetag In-Page Push -->
  <!-- END HEADER AD CODE -->
</head>
<body>
  {make_navbar("index.html")}

  {make_smartlink_banner("top")}

  <main class="main-wrapper">
    <header class="hero-header">
      <div class="hero-logo-container">
        <img src="gemini-svg.svg" alt="PDFDock Logo" class="hero-logo" width="250" height="88">
      </div>
      <h1 class="hero-title">Everything You Need, All in One Place.</h1>
      <div class="hero-keywords-bar">
        <span class="keyword-pill"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg> 100% Free</span>
        <span class="keyword-pill"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><line x1="18" y1="8" x2="23" y2="13"/><line x1="23" y1="8" x2="18" y2="13"/></svg> No Signup</span>
        <span class="keyword-pill"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg> Fast In-Browser</span>
      </div>
      <!-- REQUIRED PLAIN SENTENCE: What this site is, who it is for, and what job it does -->
      <p class="hero-statement">
        PDFDock is a 100% free, fast online document platform with no signup required. Designed for students, office workers, and professionals to merge, split, compress, convert, edit, and protect PDF files directly in your browser with zero server uploads.
      </p>
    </header>

    <!-- SEARCH & CATEGORY FILTER TABS -->
    <div class="search-and-filter-section">
      <div class="tool-search-box">
        <svg class="search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"/>
          <line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        <input type="text" id="tool-search-input" class="tool-search-input" placeholder="Search all {len(tools_data)} tools (e.g. compress, merge, word, sign, image)..." aria-label="Search tools">
        <button type="button" id="clear-search-btn" class="clear-search-btn" style="display: none;" aria-label="Clear search">&times;</button>
      </div>

      <div class="category-tabs" role="tablist">
        <button type="button" class="category-pill active" data-filter="all">All Tools ({len(tools_data)})</button>
        <button type="button" class="category-pill" data-filter="organize">Organize PDF</button>
        <button type="button" class="category-pill" data-filter="convert-to">Convert to PDF</button>
        <button type="button" class="category-pill" data-filter="convert-from">Convert from PDF</button>
        <button type="button" class="category-pill" data-filter="edit">Edit &amp; Security</button>
      </div>
    </div>

    {make_smartlink_banner("mid")}

    <!-- ALL TOOLS SHOWCASE GRID -->
    <section class="tools-grid" id="tools-grid" aria-label="Available PDF Tools">
      {tool_cards_html}
    </section>

    <div id="no-tools-found" class="no-tools-found" style="display: none;">
      <p>No tools matched your search. Try searching for "pdf", "word", or "image".</p>
    </div>

    <!-- READABLE FACTS SECTION -->
    <section class="facts-section" aria-labelledby="facts-title">
      <h2 class="facts-heading" id="facts-title">Key Facts About PDFDock</h2>
      <div class="facts-grid">
        <article class="fact-card">
          <h3 class="fact-title">100% In-Browser Privacy</h3>
          <p class="fact-description">PDFDock executes all transformations locally inside your browser sandbox. None of your sensitive business documents, contracts, or photos ever touch an external server.</p>
        </article>
        <article class="fact-card">
          <h3 class="fact-title">Visual Page Inspection</h3>
          <p class="fact-description">See all PDF pages laid out in order before applying changes, drag to reorder pages, arrange merge order, and review complete documents prior to export.</p>
        </article>
        <article class="fact-card">
          <h3 class="fact-title">Instant Zero-Queue Speed</h3>
          <p class="fact-description">Because generation runs locally on your computer or phone CPU, tasks complete in milliseconds without queueing or network congestion delays.</p>
        </article>
        <article class="fact-card">
          <h3 class="fact-title">Zero Paywalls &amp; No Logins</h3>
          <p class="fact-description">There are no logins, no credit cards, no watermark traps, and no trial limits. Pure, uncluttered utility built for maximum efficiency.</p>
        </article>
      </div>
    </section>

    <!-- 3-STEP GUIDE -->
    <section class="guide-section" aria-labelledby="guide-title">
      <h2 class="facts-heading" id="guide-title">How to Use PDFDock</h2>
      <ol class="steps-list">
        <li class="step-item"><strong>Step 1: Choose Your Tool</strong> &mdash; Select any of our {len(tools_data)} dedicated tools from the grid above.</li>
        <li class="step-item"><strong>Step 2: Inspect &amp; Arrange</strong> &mdash; Select your file, preview pages visually, and customize options.</li>
        <li class="step-item"><strong>Step 3: Preview &amp; Download</strong> &mdash; Review your final document in the complete viewer and download instantly.</li>
      </ol>
    </section>

    {make_smartlink_banner("bottom")}
  </main>

  {make_footer()}

  <script>
    document.addEventListener('DOMContentLoaded', () => {{
      // Menu Drawer Hover & Click Toggle
      const dropdownWrap = document.querySelector('.nav-dropdown-wrap');
      const drawer = document.getElementById('tools-drawer');
      const menuBtn = document.getElementById('menu-toggle-btn');
      if (dropdownWrap && drawer) {{
        let hideTimer = null;
        const openMenu = () => {{
          clearTimeout(hideTimer);
          drawer.classList.add('show');
          if (menuBtn) menuBtn.setAttribute('aria-expanded', 'true');
        }};
        const closeMenu = () => {{
          hideTimer = setTimeout(() => {{
            drawer.classList.remove('show');
            if (menuBtn) menuBtn.setAttribute('aria-expanded', 'false');
          }}, 220);
        }};

        dropdownWrap.addEventListener('mouseenter', openMenu);
        dropdownWrap.addEventListener('mouseleave', closeMenu);
        drawer.addEventListener('mouseenter', openMenu);
        drawer.addEventListener('mouseleave', closeMenu);

        if (menuBtn) {{
          menuBtn.addEventListener('click', (e) => {{
            e.stopPropagation();
            const isOpen = drawer.classList.toggle('show');
            menuBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
          }});
        }}

        drawer.addEventListener('click', (e) => {{
          if (e.target.tagName !== 'A') e.stopPropagation();
        }});

        document.addEventListener('click', (e) => {{
          if (!dropdownWrap.contains(e.target)) {{
            drawer.classList.remove('show');
            if (menuBtn) menuBtn.setAttribute('aria-expanded', 'false');
          }}
        }});
      }}

      // Category & Search Filters
      const searchInput = document.getElementById('tool-search-input');
      const clearBtn = document.getElementById('clear-search-btn');
      const pills = document.querySelectorAll('.category-pill');
      const cards = document.querySelectorAll('.tool-card');
      const noTools = document.getElementById('no-tools-found');
      let currentCategory = 'all';

      function applyFilters() {{
        const query = (searchInput.value || '').trim().toLowerCase();
        if (clearBtn) clearBtn.style.display = query ? 'flex' : 'none';
        let visibleCount = 0;

        cards.forEach(card => {{
          const cat = card.getAttribute('data-category');
          const text = (card.textContent || '').toLowerCase();
          const matchesCat = (currentCategory === 'all' || cat === currentCategory);
          const matchesQuery = !query || text.includes(query);

          if (matchesCat && matchesQuery) {{
            card.style.display = 'flex';
            visibleCount++;
          }} else {{
            card.style.display = 'none';
          }}
        }});

        if (noTools) {{
          noTools.style.display = (visibleCount === 0) ? 'block' : 'none';
        }}
      }}

      pills.forEach(pill => {{
        pill.addEventListener('click', () => {{
          pills.forEach(p => p.classList.remove('active'));
          pill.classList.add('active');
          currentCategory = pill.getAttribute('data-filter') || 'all';
          applyFilters();
        }});
      }});

      if (searchInput) {{
        searchInput.addEventListener('input', applyFilters);
      }}
      if (clearBtn) {{
        clearBtn.addEventListener('click', () => {{
          searchInput.value = '';
          applyFilters();
          searchInput.focus();
        }});
      }}
    }});
  </script>

  <!-- ADSTERRA / MONETAG FOOTER SCRIPT PLACEHOLDER -->
  <!-- START FOOTER AD CODE -->
  <!-- Example: Adsterra Social Bar or Monetag OnClick -->
  <!-- END FOOTER AD CODE -->
</body>
</html>
"""


with open("index.html", "w", encoding="utf-8") as f:
    f.write(index_html)
print("Generated index.html (PDFDock Main Portal)")

# GENERATE 404.HTML FOR VERCEL DEPLOYMENT
not_found_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <!-- Monetag In-Page Push / Vignette Ad Tag -->
  <script>(function(s){{s.dataset.zone='11833252',s.src='https://nap5k.com/tag.min.js'}})([document.documentElement, document.body].filter(Boolean).pop().appendChild(document.createElement('script')))</script>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>404 - Page Not Found | PDFDock</title>
  <meta name="robots" content="noindex, follow">
  <link rel="icon" type="image/svg+xml" href="favicon.svg">
  <link rel="stylesheet" href="styles.css?v=2.5">
</head>
<body>
  {make_navbar("404.html")}

  <main class="main-wrapper" style="text-align: center; padding: 5rem 1.5rem 4rem; max-width: 860px; margin: 0 auto; min-height: 60vh;">
    <div style="font-size: 5.5rem; font-weight: 900; color: #10b981; line-height: 1; margin-bottom: 1rem; letter-spacing: -2px;">404</div>
    <h1 style="font-size: 2.25rem; font-weight: 800; color: var(--slate-900); margin-bottom: 1rem;">Page Not Found</h1>
    <p style="font-size: 1.125rem; color: var(--slate-600); margin-bottom: 2.5rem; max-width: 580px; margin-left: auto; margin-right: auto; line-height: 1.6;">
      The page or PDF tool you are looking for does not exist, has been renamed, or has moved. Explore our popular tools below or return to the main portal.
    </p>

    <div style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap; margin-bottom: 3.5rem;">
      <a href="index.html" class="action-btn" style="background: var(--slate-900); color: #fff; text-decoration: none; padding: 0.85rem 1.75rem; border-radius: 8px; font-weight: 600; display: inline-flex; align-items: center; gap: 0.5rem;">
        &larr; Back to Homepage
      </a>
      <a href="merge-pdf.html" class="action-btn" style="background: var(--primary); color: #fff; text-decoration: none; padding: 0.85rem 1.75rem; border-radius: 8px; font-weight: 600;">
        Merge PDF
      </a>
      <a href="compress-pdf.html" class="action-btn" style="background: #059669; color: #fff; text-decoration: none; padding: 0.85rem 1.75rem; border-radius: 8px; font-weight: 600;">
        Compress PDF
      </a>
      <a href="jpg-to-pdf.html" class="action-btn" style="background: #2563eb; color: #fff; text-decoration: none; padding: 0.85rem 1.75rem; border-radius: 8px; font-weight: 600;">
        JPG to PDF
      </a>
    </div>

    <div style="background: #fff; border: 1px solid var(--slate-200); border-radius: 12px; padding: 2rem; text-align: left; box-shadow: 0 4px 16px rgba(0,0,0,0.04);">
      <h2 style="font-size: 1.25rem; font-weight: 700; margin-bottom: 1.25rem; color: var(--slate-800);">Quick Links to Free Online PDF Tools</h2>
      <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 0.85rem;">
        <a href="merge-pdf.html" style="color: var(--primary); text-decoration: none; font-weight: 500;">&bull; Merge PDF</a>
        <a href="split-pdf.html" style="color: var(--primary); text-decoration: none; font-weight: 500;">&bull; Split PDF</a>
        <a href="compress-pdf.html" style="color: var(--primary); text-decoration: none; font-weight: 500;">&bull; Compress PDF</a>
        <a href="jpg-to-pdf.html" style="color: var(--primary); text-decoration: none; font-weight: 500;">&bull; JPG to PDF</a>
        <a href="pdf-to-jpg.html" style="color: var(--primary); text-decoration: none; font-weight: 500;">&bull; PDF to JPG</a>
        <a href="pdf-to-word.html" style="color: var(--primary); text-decoration: none; font-weight: 500;">&bull; PDF to Word</a>
        <a href="word-to-pdf.html" style="color: var(--primary); text-decoration: none; font-weight: 500;">&bull; Word to PDF</a>
        <a href="excel-to-pdf.html" style="color: var(--primary); text-decoration: none; font-weight: 500;">&bull; Excel to PDF</a>
        <a href="sign-pdf.html" style="color: var(--primary); text-decoration: none; font-weight: 500;">&bull; Sign PDF</a>
        <a href="protect-pdf.html" style="color: var(--primary); text-decoration: none; font-weight: 500;">&bull; Protect PDF</a>
      </div>
    </div>
  </main>

  {make_footer()}
  <script src="app.js"></script>
</body>
</html>
"""

with open("404.html", "w", encoding="utf-8") as f:
    f.write(not_found_html)
print("Generated 404.html (Vercel Not Found Page)")

# AUTOMATED SITEMAP.XML GENERATION FOR VERCEL HOSTING & SEARCH ENGINES
sitemap_urls = [
    """  <url>
    <loc>https://pdfdock-ten.vercel.app/</loc>
    <lastmod>2026-09-18</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>"""
]

top_tools = {"merge-pdf.html", "compress-pdf.html", "jpg-to-pdf.html", "pdf-to-jpg.html", "split-pdf.html"}
for t in tools_data:
    filename = t["file"]
    prio = "0.9" if filename in top_tools else "0.8"
    sitemap_urls.append(f"""  <url>
    <loc>https://pdfdock-ten.vercel.app/{filename}</loc>
    <lastmod>2026-09-18</lastmod>
    <changefreq>weekly</changefreq>
    <priority>{prio}</priority>
  </url>""")

sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(sitemap_urls)}
</urlset>
"""

with open("sitemap.xml", "w", encoding="utf-8") as f:
    f.write(sitemap_xml)
print(f"Generated sitemap.xml with all {len(sitemap_urls)} URLs")

robots_txt = """User-agent: *
Allow: /

Sitemap: https://pdfdock-ten.vercel.app/sitemap.xml
"""
with open("robots.txt", "w", encoding="utf-8") as f:
    f.write(robots_txt)
print("Generated robots.txt")

print(f"ALL {len(tools_data) + 1} PAGES + SITEMAP.XML + ROBOTS.TXT GENERATED WITH SEO, GEO & VERCEL READINESS!")

# SYNC ALL ASSETS TO public/ DIRECTORY FOR VERCEL DEPLOYMENT
base_dir = os.path.dirname(os.path.abspath(__file__))
public_dir = os.path.join(base_dir, "public")
os.makedirs(public_dir, exist_ok=True)

# Copy static assets to public/
for item in os.listdir(base_dir):
    if item.startswith("sample_") or item in ["public", ".git", ".vercel", "__pycache__", "New folder", "copy-public.js"]:
        continue
    src_path = os.path.join(base_dir, item)
    dst_path = os.path.join(public_dir, item)
    if os.path.isfile(src_path):
        if item.endswith(('.html', '.css', '.js', '.svg', '.xml', '.txt', '.ico', '.png', '.jpg', '.webp')):
            shutil.copy2(src_path, dst_path)
    elif os.path.isdir(src_path) and item == "js":
        if os.path.exists(dst_path):
            shutil.rmtree(dst_path)
        shutil.copytree(src_path, dst_path)

print("Successfully synced all static files and js/ directory to public/ for Vercel deployment.")


