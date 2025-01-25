document.addEventListener('DOMContentLoaded', function() {
    const imageUpload = document.getElementById('imageUpload');
    const markdownContent = document.getElementById('markdownContent');
    const uploadedImages = document.getElementById('uploadedImages');
    const preview = document.getElementById('preview');

    if (imageUpload && markdownContent) {
        // Handle image uploads
        imageUpload.addEventListener('change', async function(e) {
            const files = e.target.files;
            
            for (let file of files) {
                const formData = new FormData();
                formData.append('image', file);

                try {
                    const response = await fetch('/documents/upload_image', {
                        method: 'POST',
                        body: formData
                    });

                    const data = await response.json();
                    
                    if (response.ok) {
                        // Insert markdown at cursor position
                        const cursorPos = markdownContent.selectionStart;
                        const textBefore = markdownContent.value.substring(0, cursorPos);
                        const textAfter = markdownContent.value.substring(cursorPos);
                        
                        markdownContent.value = textBefore + '\n' + data.markdown + '\n' + textAfter;
                        
                        // Add image preview
                        const imgPreview = document.createElement('div');
                        imgPreview.innerHTML = `
                            <div class="flex items-center gap-2 p-2 bg-gray-50 rounded">
                                <img src="${data.url}" alt="${file.name}" class="w-8 h-8 object-cover rounded">
                                <span class="text-sm text-gray-600">${file.name}</span>
                            </div>
                        `;
                        uploadedImages.appendChild(imgPreview);
                        
                        // Update preview
                        updatePreview();
                    } else {
                        throw new Error(data.error);
                    }
                } catch (error) {
                    console.error('Upload failed:', error);
                    alert('Failed to upload image: ' + error.message);
                }
            }
        });

        // Live preview
        markdownContent.addEventListener('input', updatePreview);
        
        // Initial preview
        updatePreview();
    }

    function updatePreview() {
        if (preview && markdownContent) {
            preview.innerHTML = marked.parse(markdownContent.value);
        }
    }
});