// script.js

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Materialize components
    M.AutoInit();

    const uploadForm = document.getElementById('upload-form');
    const compareBtn = document.getElementById('compare-btn');
    const loader = document.getElementById('loader');
    const differencesSection = document.getElementById('differences-section');
    const differencesList = document.getElementById('differences-list');
    const errorMessage = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');

    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Clear previous results and errors
        differencesList.innerHTML = '';
        differencesSection.style.display = 'none';
        errorMessage.style.display = 'none';

        const fileInput1 = document.getElementById('file1');
        const fileInput2 = document.getElementById('file2');

        const file1 = fileInput1.files[0];
        const file2 = fileInput2.files[0];

        if (!file1 || !file2) {
            showError('Please select both DOCX files.');
            return;
        }

        // Show loader
        loader.style.display = 'block';

        // Prepare form data
        const formData = new FormData();
        formData.append('file1', file1);
        formData.append('file2', file2);

        try {
            const response = await fetch('http://localhost:8000/compare-docx/', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                displayDifferences(result.differences);
            } else {
                showError(result.detail || 'An error occurred while comparing the documents.');
            }
        } catch (error) {
            showError('Failed to connect to the server. Please ensure the backend is running.');
            console.error('Error:', error);
        } finally {
            // Hide loader
            loader.style.display = 'none';
        }
    });

    function displayDifferences(differences) {
        // Split differences into lines
        const lines = differences.split('\n').filter(line => line.trim() !== '');

        lines.forEach(line => {
            const listItem = document.createElement('li');
            listItem.className = 'collection-item';
            listItem.textContent = line;
            differencesList.appendChild(listItem);
        });

        differencesSection.style.display = 'block';
    }

    function showError(message) {
        errorText.textContent = message;
        errorMessage.style.display = 'block';
    }
});