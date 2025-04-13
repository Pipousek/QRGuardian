// File upload handling functionality
const FileUpload = {
    // Initialize drag and drop functionality for all file inputs
    initialize: function() {
        document.querySelectorAll('.file-drop-container').forEach(container => {
            const input = container.querySelector('.file-drop-input');
            const message = container.querySelector('.file-drop-message');
            const icon = container.querySelector('.file-drop-icon');

            // Initialize with translated message
            if (message) {
                message.setAttribute('data-i18n', 'fileUpload.dragDrop');
                if (I18N.translations && I18N.translations.fileUpload) {
                    message.textContent = I18N.translations.fileUpload.dragDrop;
                }
            }

            // Create status element
            const statusElement = document.createElement('div');
            statusElement.className = 'file-upload-status';
            container.appendChild(statusElement);

            // Create delete button container
            const deleteBtnContainer = document.createElement('div');
            deleteBtnContainer.className = 'file-delete-btn-container';

            // Create delete button with translation
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'file-delete-btn';
            deleteBtn.innerHTML = `<i class="fas fa-trash-alt"></i> <span data-i18n="fileUpload.remove">Remove File</span>`;
            deleteBtn.style.display = 'none';
            deleteBtnContainer.appendChild(deleteBtn);
            container.appendChild(deleteBtnContainer);

            // Apply translation to the button
            const span = deleteBtn.querySelector('span');
            if (span && I18N.translations && I18N.translations.fileUpload) {
                span.textContent = I18N.translations.fileUpload.remove;
            }

            // Handle delete button click
            deleteBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                input.value = '';
                this.updateDisplay(input, message, icon, statusElement);
                deleteBtn.style.display = 'none';
                input.dispatchEvent(new Event('change'));
            });

            // Highlight when dragging over
            container.addEventListener('dragover', (e) => {
                e.preventDefault();
                container.classList.add('active');
                if (icon) icon.classList.add('fa-spin');
            });

            container.addEventListener('dragleave', () => {
                container.classList.remove('active');
                if (icon) icon.classList.remove('fa-spin');
            });

            // Handle dropped files
            container.addEventListener('drop', (e) => {
                e.preventDefault();
                container.classList.remove('active');
                if (icon) icon.classList.remove('fa-spin');

                if (e.dataTransfer.files.length) {
                    input.files = e.dataTransfer.files;
                    this.updateDisplay(input, message, icon, statusElement);
                    input.dispatchEvent(new Event('change'));
                }
            });

            // Handle click selection
            input.addEventListener('change', () => {
                this.updateDisplay(input, message, icon, statusElement);
            });

            // For signature files, show different accepted formats
            if (input && input.id === 'verify-sig-input') {
                input.setAttribute('accept', '.txt,.text');
                const message = container.querySelector('.file-drop-message');
                if (message) {
                    message.setAttribute('data-i18n', 'verify.dropSig');
                }
            }
        });
    },

    // Update file display status
    updateDisplay: function(input, message, icon, statusElement) {
        const container = input.closest('.file-drop-container');
        const deleteBtn = container.querySelector('.file-delete-btn');
        const watermarkControls = document.querySelector('#watermark-controls');

        // Clear any existing status elements first
        const existingStatus = container.querySelectorAll('.file-upload-status');
        existingStatus.forEach(el => {
            if (el !== statusElement) {
                el.remove();
            }
        });

        if (input.files && input.files.length > 0) {
            const file = input.files[0];
            container.classList.add('has-file');

            // Show watermark controls if this is the watermark input
            if (input.id === 'watermark-input' && watermarkControls) {
                watermarkControls.style.display = 'block';
            }

            // Change the icon to a checkmark
            if (icon) {
                icon.classList.remove('fa-cloud-upload-alt', 'fa-spin');
                icon.classList.add('fa-check-circle');
                icon.style.color = '#4CAF50';
            }

            // Update the message to show the file name
            if (message) {
                message.textContent = file.name;
                message.style.fontWeight = 'bold';
                message.style.color = '#4CAF50';
            }

            // Show file size info - ensure we only have one status element
            if (statusElement) {
                // Remove any duplicates first
                const allStatusElements = container.querySelectorAll('.file-upload-status');
                allStatusElements.forEach((el, index) => {
                    if (index > 0) el.remove();
                });

                const fileSize = file.size < 1024 ?
                    `${file.size} bytes` :
                    `${(file.size / 1024).toFixed(2)} KB`;
                statusElement.textContent = fileSize;
                statusElement.style.color = '#6c757d';
            }

            // Show delete button
            deleteBtn.style.display = 'block';

            // For image previews
            if (file.type.startsWith('image/') && input.id === 'watermark-input') {
                const preview = document.querySelector('#watermark-preview');
                if (preview) {
                    preview.src = URL.createObjectURL(file);
                    preview.style.display = 'block';
                }
            }
        } else {
            container.classList.remove('has-file');

            // Hide watermark controls if this is the watermark input
            if (input.id === 'watermark-input' && watermarkControls) {
                watermarkControls.style.display = 'none';
            }

            // Revert to original state
            if (icon) {
                icon.classList.add('fa-cloud-upload-alt');
                icon.classList.remove('fa-check-circle', 'fa-spin');
                icon.style.color = '';
            }

            if (message) {
                // Use translation system for the default message
                message.setAttribute('data-i18n', 'fileUpload.dragDrop');
                if (I18N.translations && I18N.translations.fileUpload) {
                    message.textContent = I18N.translations.fileUpload.dragDrop;
                } else {
                    message.textContent = "Drag & drop your file here or click to browse";
                }
                message.style.fontWeight = '';
                message.style.color = '';
            }

            if (statusElement) {
                statusElement.textContent = '';
            }

            // Hide delete button
            deleteBtn.style.display = 'none';
        }
    },

    // Clear all file inputs
    clearAll: function() {
        document.querySelectorAll('input[type="file"]').forEach(input => {
            input.value = '';
        });
    }
};