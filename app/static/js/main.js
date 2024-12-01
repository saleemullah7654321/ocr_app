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
    }

    newScanBtn.addEventListener('click', () => {
        resultsSection.classList.add('hidden');
        form.parentElement.classList.remove('hidden');
        form.reset();
        selectedFile.textContent = '';
        processBtn.disabled = true;
    });
}); 