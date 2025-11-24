let selectedFile = null;
let currentCandidateId = null;

document.addEventListener('DOMContentLoaded', () => {
    setupFileUpload();
    loadResumeList();
    setupSearchButton();
    setupDisplayResumeButton();
});

function setupFileUpload() {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('resumeFile');
    const browseLink = document.getElementById('browseLink');
    const selectedFileDiv = document.getElementById('selectedFile');
    const fileNameSpan = document.getElementById('fileName');
    const removeFileBtn = document.getElementById('removeFile');
    const submitBtn = document.getElementById('submitBtn');

    dropzone.addEventListener('click', () => fileInput.click());
    browseLink.addEventListener('click', (e) => {
        e.stopPropagation();
        fileInput.click();
    });

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, () => dropzone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, () => dropzone.classList.remove('dragover'), false);
    });

    dropzone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            fileInput.files = files;
            handleFileSelect();
        }
    });

    fileInput.addEventListener('change', handleFileSelect);

    function handleFileSelect() {
        if (fileInput.files.length > 0) {
            selectedFile = fileInput.files[0];
            fileNameSpan.textContent = selectedFile.name;
            dropzone.style.display = 'none';
            selectedFileDiv.style.display = 'flex';
        }
    }

    removeFileBtn.addEventListener('click', () => {
        selectedFile = null;
        fileInput.value = '';
        dropzone.style.display = 'block';
        selectedFileDiv.style.display = 'none';
    });

    submitBtn.addEventListener('click', async () => {
        if (!selectedFile) {
            showStatus('Please select a file', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('file', selectedFile);

        showLoading(true);

        try {
            const response = await fetch('/api/upload-resume', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                showStatus(`Resume parsed successfully! Candidate: ${result.name}`, 'success');
                selectedFile = null;
                fileInput.value = '';
                dropzone.style.display = 'block';
                selectedFileDiv.style.display = 'none';
                loadResumeList();
            } else {
                showStatus('Error: ' + (result.detail || 'Unknown error'), 'error');
            }
        } catch (error) {
            showStatus('Upload failed: ' + error.message, 'error');
        } finally {
            showLoading(false);
        }
    });
}

function setupSearchButton() {
    const searchBtn = document.getElementById('searchBtn');
    const skillSearch = document.getElementById('skillSearch');

    searchBtn.addEventListener('click', () => searchBySkills());
    skillSearch.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') searchBySkills();
    });
}

async function searchBySkills() {
    const skillSearch = document.getElementById('skillSearch');
    const searchResults = document.getElementById('searchResults');
    const query = skillSearch.value.trim();

    if (!query) {
        searchResults.innerHTML = '<div class="status-error status-message">Please enter search skills</div>';
        return;
    }

    searchResults.innerHTML = '<div class="loading">Searching candidates...</div>';

    try {
        const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
        const result = await response.json();

        if (result.success && result.results.length > 0) {
            displaySearchResults(result.results);
        } else {
            searchResults.innerHTML = '<div class="no-info"><p>No candidates found matching those skills</p></div>';
        }
    } catch (error) {
        searchResults.innerHTML = `<div class="status-error status-message">Search error: ${error.message}</div>`;
    }
}

function displaySearchResults(results) {
    const searchResults = document.getElementById('searchResults');
    let html = '';

    results.forEach(candidate => {
        const skillsArray = candidate.key_skills || [];
        html += `
            <div class="candidate-item" onclick="selectCandidate(${candidate.id})">
                <div class="candidate-name">${candidate.name}</div>
                <div class="candidate-email">${candidate.email}</div>
                ${candidate.match_percentage ? `<div style="color: #48bb78; font-weight: 600; margin-bottom: 8px;">Match: ${candidate.match_percentage}%</div>` : ''}
                <div class="candidate-skills">
                    ${skillsArray.slice(0, 5).map(skill => 
                        `<span class="skill-badge">${skill}</span>`
                    ).join('')}
                    ${skillsArray.length > 5 ? `<span class="skill-badge">+${skillsArray.length - 5} more</span>` : ''}
                </div>
            </div>
        `;
    });

    searchResults.innerHTML = html;
}

async function loadResumeList() {
    const resumeSelect = document.getElementById('resumeSelect');

    try {
        const response = await fetch('/api/resumes');
        const result = await response.json();

        if (result.success) {
            resumeSelect.innerHTML = '<option value="">Choose a resume...</option>';
            result.resumes.forEach(resume => {
                const option = document.createElement('option');
                option.value = resume.id;
                option.textContent = `${resume.name} - ${resume.email}`;
                resumeSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Failed to load resume list:', error);
    }
}

function setupDisplayResumeButton() {
    const displayBtn = document.getElementById('displayResumeBtn');
    const resumeSelect = document.getElementById('resumeSelect');

    displayBtn.addEventListener('click', () => {
        const candidateId = resumeSelect.value;
        if (candidateId) {
            selectCandidate(parseInt(candidateId));
        } else {
            showStatus('Please select a resume first', 'error');
        }
    });
}

async function selectCandidate(candidateId) {
    currentCandidateId = candidateId;
    showLoading(true);

    try {
        const response = await fetch(`/api/resume/${candidateId}`);
        const result = await response.json();

        if (result.success) {
            displayCandidateInfo(result.candidate);
            displayResumeDocument(candidateId);
        } else {
            showStatus('Failed to load candidate details', 'error');
        }
    } catch (error) {
        showStatus('Error loading candidate: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

function displayResumeDocument(candidateId) {
    const documentViewer = document.getElementById('documentViewer');
    const pdfUrl = `/api/resume/file/${candidateId}`;
    
    documentViewer.innerHTML = `
        <div style="width: 100%; height: 600px; display: flex; flex-direction: column; align-items: center; justify-content: center;">
            <iframe 
                id="pdfFrame" 
                src="${pdfUrl}" 
                type="application/pdf"
                style="width: 100%; height: 100%; border: none; border-radius: 12px;">
            </iframe>
        </div>
    `;
}

function displayCandidateInfo(candidate) {
    const extractedInfo = document.getElementById('extractedInfo');
    
    let html = `
        <div class="info-section">
            <div class="info-section-title"><i class="fas fa-user"></i> Personal Information</div>
            <div class="info-item">
                <div class="info-label">Name</div>
                <div class="info-value">${candidate.name || 'N/A'}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Email</div>
                <div class="info-value">${candidate.email || 'N/A'}</div>
            </div>
            ${candidate.phone ? `
            <div class="info-item">
                <div class="info-label">Phone</div>
                <div class="info-value">${candidate.phone}</div>
            </div>
            ` : ''}
            ${candidate.location ? `
            <div class="info-item">
                <div class="info-label">Location</div>
                <div class="info-value">${candidate.location}</div>
            </div>
            ` : ''}
        </div>
    `;

    if (candidate.skills && candidate.skills.length > 0) {
        html += `
            <div class="info-section">
                <div class="info-section-title"><i class="fas fa-code"></i> Skills</div>
                <div class="skills-grid">
                    ${candidate.skills.map(skill => 
                        `<span class="skill-tag">${skill.name}</span>`
                    ).join('')}
                </div>
            </div>
        `;
    }

    if (candidate.experience && candidate.experience.length > 0) {
        html += `
            <div class="info-section">
                <div class="info-section-title"><i class="fas fa-briefcase"></i> Work Experience</div>
                ${candidate.experience.map(exp => `
                    <div class="experience-item">
                        <div class="item-title">${exp.job_title || 'Position'}</div>
                        <div class="item-subtitle"><strong>${exp.company || 'Company'}</strong> ${exp.duration ? `• ${exp.duration}` : ''}</div>
                        ${exp.description ? `<div class="item-detail">${exp.description}</div>` : ''}
                    </div>
                `).join('')}
            </div>
        `;
    }

    if (candidate.education && candidate.education.length > 0) {
        html += `
            <div class="info-section">
                <div class="info-section-title"><i class="fas fa-graduation-cap"></i> Education</div>
                ${candidate.education.map(edu => `
                    <div class="education-item">
                        <div class="item-title">${edu.degree || 'Degree'}</div>
                        <div class="item-subtitle">${edu.institution || 'Institution'} ${edu.year ? `• ${edu.year}` : ''}</div>
                        ${edu.field_of_study ? `<div class="item-detail">Field: ${edu.field_of_study}</div>` : ''}
                    </div>
                `).join('')}
            </div>
        `;
    }

    extractedInfo.innerHTML = html;
}

function showStatus(message, type) {
    const statusDiv = document.getElementById('uploadStatus');
    statusDiv.innerHTML = `<div class="status-message status-${type}">${message}</div>`;
    
    if (type === 'success' || type === 'error') {
        setTimeout(() => {
            statusDiv.innerHTML = '';
        }, 5000);
    }
}

function showLoading(show) {
    const loadingOverlay = document.getElementById('loadingOverlay');
    loadingOverlay.style.display = show ? 'flex' : 'none';
}
