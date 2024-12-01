document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('upload-form');
    const fileInput = document.getElementById('image-input');
    const dropZone = document.querySelector('.drop-zone');
    const selectedFile = document.querySelector('.selected-file');
    const processBtn = document.querySelector('.process-btn');
    const browseBtn = document.querySelector('.browse-btn');
    const loadingOverlay = document.getElementById('loading');
    const resultsSection = document.getElementById('results-section');
    const newScanBtn = document.querySelector('.new-scan-btn');

    // Handle drag and drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.add('dragover');
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.remove('dragover');
        });
    });

    dropZone.addEventListener('drop', handleDrop);
    
    browseBtn.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', handleFileSelect);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    function handleFileSelect(e) {
        const files = e.target.files;
        handleFiles(files);
    }

    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            if (file.type.startsWith('image/')) {
                selectedFile.textContent = `Selected: ${file.name}`;
                processBtn.disabled = false;
            } else {
                alert('Please select an image file.');
                selectedFile.textContent = '';
                processBtn.disabled = true;
            }
        }
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        try {
            loadingOverlay.classList.remove('hidden');
            
            const response = await fetch('/process', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                displayResults(data);
                resultsSection.classList.remove('hidden');
                form.parentElement.classList.add('hidden');
            } else {
                alert(data.error || 'Processing failed');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while processing the image');
        } finally {
            loadingOverlay.classList.add('hidden');
        }
    });

    function showToast(message) {
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 2300);
    }

    function formatTextForCopy(textData) {
        return textData.map(item => `${item.text} (Confidence: ${(item.confidence * 100).toFixed(2)}%)`).join('\n');
    }

    function formatJSON(textData) {
        return JSON.stringify(textData, null, 2);
    }

    function formatCSV(textData) {
        const header = 'Text,Confidence\n';
        const rows = textData.map(item => 
            `"${item.text}",${(item.confidence * 100).toFixed(2)}`
        ).join('\n');
        return header + rows;
    }

    function formatDOCX(textData) {
        return textData.map(item => 
            `${item.text}\nConfidence: ${(item.confidence * 100).toFixed(2)}%\n`
        ).join('\n');
    }

    function downloadFile(content, filename, type) {
        const blob = new Blob([content], { type });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    function displayResults(data) {
        const resultDiv = document.getElementById('text-results');
        resultDiv.innerHTML = '<h3>Detected Text:</h3>';
        
        data.text_results.text_data.forEach(item => {
            const confidence = (item.confidence * 100).toFixed(2);
            const color = `rgb(${item.color.join(',')})`;
            
            resultDiv.innerHTML += `
                <p style="border-left: 4px solid ${color}; margin: 0.5rem 0; padding-left: 1rem;">
                    <strong>${item.text}</strong>
                    <span style="color: #666; font-size: 0.9rem;">
                        (Confidence: ${confidence}%)
                    </span>
                </p>
            `;
        });

        document.getElementById('original-image').src = `data:image/jpeg;base64,${data.text_results.original_image}`;
        document.getElementById('result-image').src = `data:image/jpeg;base64,${data.text_results.annotated_image}`;

        // Add copyable text
        const copyableText = document.getElementById('copyable-text');
        const plainText = formatTextForCopy(data.text_results.text_data);
        copyableText.textContent = plainText;

        // Add copy button functionality
        const copyBtn = document.querySelector('.copy-btn');
        copyBtn.addEventListener('click', async () => {
            try {
                await navigator.clipboard.writeText(plainText);
                copyBtn.classList.add('copied');
                showToast('Text copied to clipboard!');
                setTimeout(() => copyBtn.classList.remove('copied'), 2000);
            } catch (err) {
                showToast('Failed to copy text');
            }
        });

        // Add export button functionality
        document.querySelectorAll('.export-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const type = btn.dataset.type;
                let content, filename, mimeType;

                switch(type) {
                    case 'txt':
                        content = plainText;
                        filename = 'extracted_text.txt';
                        mimeType = 'text/plain';
                        break;
                    case 'json':
                        content = formatJSON(data.text_results.text_data);
                        filename = 'extracted_text.json';
                        mimeType = 'application/json';
                        break;
                    case 'csv':
                        content = formatCSV(data.text_results.text_data);
                        filename = 'extracted_text.csv';
                        mimeType = 'text/csv';
                        break;
                    case 'docx':
                        content = formatDOCX(data.text_results.text_data);
                        filename = 'extracted_text.docx';
                        mimeType = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document';
                        break;
                }

                downloadFile(content, filename, mimeType);
                showToast(`Downloaded as ${type.toUpperCase()}`);
            });
        });
    }

    newScanBtn.addEventListener('click', () => {
        resultsSection.classList.add('hidden');
        form.parentElement.classList.remove('hidden');
        form.reset();
        selectedFile.textContent = '';
        processBtn.disabled = true;
    });
}); 