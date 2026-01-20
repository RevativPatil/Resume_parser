let selectedFile = null;
let currentCandidateId = null;
let jobRoles = [];

document.addEventListener('DOMContentLoaded', () => {
    setupFileUpload();
    loadResumeList();
    loadJobRoles();
    setupSearchButton();
    setupDisplayResumeButton();
});

async function loadJobRoles() {
    try {
        const response = await fetch('/api/job-roles');
        const result = await response.json();
        if (result.success) {
            jobRoles = result.job_roles;
        }
    } catch (error) {
        console.error('Failed to load job roles:', error);
    }
}

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
        searchResults.innerHTML = '<div class="status-error status-message">Please enter search skills or job role</div>';
        return;
    }

    searchResults.innerHTML = '<div class="loading">Searching candidates...</div>';

    try {
        const normalizedQuery = query.toLowerCase().replace(/\s+/g, '_').replace(/-/g, '_');

        const matchingRole = jobRoles.find(role =>
            role.key === normalizedQuery ||
            role.title.toLowerCase() === query.toLowerCase()
        );

        if (matchingRole) {
            const response = await fetch(`/api/search-by-role?role=${matchingRole.key}`);
            const result = await response.json();

            if (result.success && result.candidates && result.candidates.length > 0) {
                displayJobRoleResults(result);
            } else {
                searchResults.innerHTML = '<div class="no-info"><p>No candidates found for this job role</p></div>';
            }
        } else {
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
            const result = await response.json();

            if (result.success && result.results && result.results.length > 0) {
                displaySearchResults(result.results);
            } else {
                searchResults.innerHTML = '<div class="no-info"><p>No candidates found matching those skills</p></div>';
            }
        }
    } catch (error) {
        searchResults.innerHTML = `<div class="status-error status-message">Search error: ${error.message}</div>`;
    }
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
    const fileUrl = `/api/resume/file/${candidateId}`;

    documentViewer.innerHTML = `
        <iframe src="${fileUrl}" style="width: 100%; height: 600px; border-radius: 8px;"></iframe>
        <a href="${fileUrl}" target="_blank" style="display:block; margin-top:10px; text-align:center;">Download Resume</a>
    `;
}

function displayCandidateInfo(candidate) {
    const extractedInfo = document.getElementById('extractedInfo');

    let html = `
        <div class="info-section"><h3>Personal Info</h3>
            <p><strong>Name:</strong> ${candidate.name || "N/A"}</p>
            <p><strong>Email:</strong> ${candidate.email || "N/A"}</p>
            <p><strong>Phone:</strong> ${candidate.phone || "N/A"}</p>
            <p><strong>Location:</strong> ${candidate.location || "N/A"}</p>
        </div>
    `;

    if (candidate.skills?.length > 0) {
        html += `
            <div class="info-section"><h3>Skills</h3>
                <div class="skills-grid">
                    ${candidate.skills.map(s => `<span class="skill-tag">${s.name}</span>`).join('')}
                </div>
            </div>
        `;
    }

    if (candidate.experience?.length > 0) {
        html += `
            <div class="info-section"><h3>Work Experience</h3>
                ${candidate.experience.map(exp => `
                    <p><strong>${exp.job_title}</strong> - ${exp.company} (${exp.duration})</p>
                `).join('')}
            </div>
        `;
    }

    if (candidate.education?.length > 0) {
        html += `
            <div class="info-section"><h3>Education</h3>
                ${candidate.education.map(edu => `
                    <p><strong>${edu.degree}</strong> - ${edu.institution} (${edu.year})</p>
                `).join('')}
            </div>
        `;
    }

    /* 🔥 NEW — SHOW PROJECTS HERE */
    if (candidate.projects && candidate.projects.length > 0) {
        html += `
            <div class="info-section">
                <div class="info-section-title"><i class="fas fa-lightbulb"></i> Projects</div>
                ${candidate.projects.map(p => `
                    <div class="project-item">
                        <div class="item-title">${p.title || 'Project'}</div>
                        ${p.description ? `<div class="item-detail">${p.description}</div>` : ''}
                        ${p.technologies_used ? `<div class="item-detail"><strong>Tech:</strong> ${p.technologies_used}</div>` : ''}
                        ${p.role ? `<div class="item-detail"><strong>Role:</strong> ${p.role}</div>` : ''}
                        ${p.duration ? `<div class="item-detail"><strong>Duration:</strong> ${p.duration}</div>` : ''}
                        ${p.github_link ? `<a href="${p.github_link}" target="_blank" class="gh-link">GitHub Repo</a>` : ''}
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
    setTimeout(() => statusDiv.innerHTML = '', 3000);
}

function showLoading(show) {
    document.getElementById('loadingOverlay').style.display = show ? 'flex' : 'none';
}
