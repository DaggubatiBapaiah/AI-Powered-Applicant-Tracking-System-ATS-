const BASE_URL = `https://${window.location.host.replace('-5000', '-5000')}`;
// In Replit, the frontend on port 5000 often accesses the same domain.
// But we'll try to get it right.
const API_URL = `${window.location.origin}`; // Assuming single domain for both

async function apiCall(endpoint, method = 'GET', body = null) {
    const token = localStorage.getItem('token');
    const headers = {
        'Content-Type': 'application/json'
    };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const options = {
        method,
        headers
    };
    if (body) options.body = JSON.stringify(body);

    const res = await fetch(`${API_URL}${endpoint}`, options);
    const data = await res.json();

    if (res.status === 401 || res.status === 403) {
        // Token invalid or role mismatch
        console.warn("Auth error:", res.status, data);
        if (!endpoint.includes('/auth/login')) {
            localStorage.clear();
            alert("Session expired or access denied. Please login again.");
            window.location.href = '/';
            return;
        }
    }

    if (!res.ok) {
        const errorMsg = typeof data.detail === 'object' ? JSON.stringify(data.detail) : (data.detail || 'API Error');
        throw new Error(errorMsg);
    }
    return data;
}

function showToast(message, type = 'info') {
    let toast = document.getElementById('toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'toast';
        toast.style.position = 'fixed';
        toast.style.bottom = '20px';
        toast.style.right = '20px';
        toast.style.padding = '10px 20px';
        toast.style.borderRadius = '5px';
        toast.style.color = 'white';
        toast.style.zIndex = '1000';
        toast.style.transition = 'opacity 0.3s';
        document.body.appendChild(toast);
    }

    toast.textContent = message;
    toast.style.backgroundColor = type === 'error' ? '#dc2626' : (type === 'success' ? '#16a34a' : '#2563eb');
    toast.style.opacity = '1';

    setTimeout(() => {
        toast.style.opacity = '0';
    }, 3000);
}

// Auth
async function handleLogin() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    try {
        const data = await apiCall('/auth/login', 'POST', { email, password });
        localStorage.clear(); // Clear any old data
        localStorage.setItem('token', data.access_token);
        const role = data.role.toLowerCase(); // Normalized 
        localStorage.setItem('role', role);
        localStorage.setItem('email', email);
        // 1. Redirect to dashboard with role param
        window.location.href = `/static/dashboard.html?role=${data.role}`;
    } catch (err) {
        document.getElementById('message').innerText = err.message;
        document.getElementById('message').className = 'error';
    }
}

async function handleSignup() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const role = document.getElementById('role').value;
    try {
        // 1. Signup
        await apiCall('/auth/signup', 'POST', { email, password, role });

        // 2. Auto-login on success
        const loginData = await apiCall('/auth/login', 'POST', { email, password });

        // 3. Save & Redirect
        localStorage.clear();
        localStorage.setItem('token', loginData.access_token);
        const safeRole = loginData.role.toLowerCase();
        localStorage.setItem('role', safeRole);
        localStorage.setItem('email', email);
        window.location.href = `/static/dashboard.html?role=${safeRole}`;

    } catch (err) {
        document.getElementById('message').innerText = err.message;
        document.getElementById('message').className = 'error';
    }
}

function handleLogout() {
    localStorage.clear();
    window.location.href = '/';
}

// Dashboard
async function initDashboard() {
    // 2. Read role from URL or localStorage
    const urlParams = new URLSearchParams(window.location.search);
    let role = urlParams.get('role');

    if (!role) {
        role = localStorage.getItem('role');
    }

    // Normalize role
    if (role) role = role.toLowerCase();

    // Basic Auth Check
    const token = localStorage.getItem('token');
    if (!token || !role) {
        window.location.href = '/';
        return;
    }

    const email = localStorage.getItem('email');
    document.getElementById('user-info').innerText = `${email} (${role})`;

    // Hide both first
    document.getElementById('candidate-view').style.display = 'none';
    document.getElementById('recruiter-view').style.display = 'none';

    // 3. Show correct section
    if (role === 'candidate') {
        document.getElementById('candidate-view').style.display = 'block';
        loadCandidateData();
    } else if (role === 'recruiter') {
        document.getElementById('recruiter-view').style.display = 'block';
        loadRecruiterData();
    }
}

// Candidate Logic
async function loadCandidateData() {
    console.log("Loading candidate data...");

    // Shared state
    let availableJobs = [];

    // 1. Resumes
    try {
        const resumes = await apiCall('/resumes/me');
        if (resumes.length > 0) {
            // Sort to get the latest resume
            // Sort to get the latest resume
            resumes.sort((a, b) => b.id - a.id);
            const latestContent = resumes[0].content;
            const textarea = document.getElementById('resume-text');
            textarea.value = latestContent;
            textarea.dataset.original = latestContent; // Store for comparison
            document.getElementById('resume-status').innerHTML = `<p class="success">Resume uploaded (ID: ${resumes[0].id})</p>`;
            localStorage.setItem('resume_id', resumes[0].id);
        }
    } catch (err) {
        console.error("Error loading resumes:", err);
    }

    // 2. Jobs
    try {
        availableJobs = await apiCall('/jobs/');
        const jobsList = document.getElementById('jobs-list');
        if (availableJobs.length === 0) {
            jobsList.innerHTML = '<p>No jobs found.</p>';
        } else {
            jobsList.innerHTML = availableJobs.map(job => {
                // Check if already applied
                // Note: We need 'apps' here, but 'apps' is fetched AFTER jobs currently.
                // We should assume 'apps' is not yet available, OR move this rendering after fetching apps.
                // Let's modify the flow: Fetch apps FIRST, then jobs, then render both? 
                // Or just re-render jobs after fetching apps.
                // Simpler: Just render jobs, then fetch apps, then re-render jobs?
                // Actually, the current function structure fetches resumes -> jobs -> apps.
                // We can just store 'availableJobs' and 'apps' and render at the end?
                // For now, let's keep it simple: We can't check 'already applied' easily inside this exact map block 
                // because 'apps' fetches later.
                // BUT, 'loadCandidateData' is async.
                // Let's fetch everything first, THEN render.
                return `
                <div class="card" id="job-card-${job.id}">
                    <h4>${job.title}</h4>
                    <p>${job.description.substring(0, 100)}...</p>
                    <button class="small" onclick="showMatch(${job.id})">Match Score</button>
                    <button class="small secondary" id="apply-btn-${job.id}" onclick="applyToJob(${job.id})">Apply</button>
                </div>
            `}).join('');
        }
    } catch (err) {
        console.error("Error loading jobs:", err);
        document.getElementById('jobs-list').innerHTML = `<p class="error">Failed to load jobs: ${err.message}</p>`;
    }

    // 3. Applications
    try {
        const apps = await apiCall('/applications/me');
        const appsContainer = document.getElementById('candidate-apps');
        if (apps.length === 0) {
            appsContainer.innerHTML = '<p>No applications yet.</p>';
        } else {
            // Update jobs UI to show 'Applied' status
            apps.forEach(app => {
                const btn = document.getElementById(`apply-btn-${app.job_id}`);
                if (btn) {
                    const statusText = app.status.charAt(0).toUpperCase() + app.status.slice(1);
                    btn.innerText = statusText;
                    btn.disabled = true;
                    btn.style.opacity = "1"; // Keep specific opacity for readability
                    // Style based on status
                    if (app.status === 'shortlisted') btn.style.backgroundColor = '#16a34a';
                    else if (app.status === 'interview') btn.style.backgroundColor = '#ca8a04';
                    else if (app.status === 'rejected') btn.style.backgroundColor = '#dc2626';
                    else btn.style.backgroundColor = '#6b7280'; // Grey for applied/pending
                    btn.onclick = null;
                }
            });

            appsContainer.innerHTML = apps.map(app => {
                const job = availableJobs.find(j => j.id === app.job_id);
                const title = job ? job.title : `Job ID: ${app.job_id}`;

                const skillsList = app.missing_skills && app.missing_skills.length > 0 && typeof app.missing_skills === 'string'
                    ? app.missing_skills.split(',').map(s => `<span style="background:#fee2e2; color:#991b1b; padding:2px 6px; border-radius:4px; font-size:0.75em; margin-right:4px;">${s.trim()}</span>`).join('')
                    : '';

                return `
                <div class="card">
                    <div style="display:flex; justify-content:space-between;">
                        <h4>${title}</h4>
                        ${app.match_score ? `<span style="font-weight:bold; color:${app.match_score >= 70 ? '#16a34a' : '#ca8a04'}">${app.match_score}% Match</span>` : ''}
                    </div>
                    <p>Status: <strong>${app.status.toUpperCase()}</strong></p>
                    ${skillsList ? `<div style="margin-top:5px; font-size:0.9em;">Missing: ${skillsList}</div>` : ''}
                </div>
                `;
            }).join('');
        }
    } catch (err) {
        console.error("Error loading applications:", err);
        document.getElementById('candidate-apps').innerHTML = `<p class="error">Failed to load applications: ${err.message}</p>`;
    }
}

async function submitResume() {
    const btn = document.getElementById('btn-update-resume');
    btn.disabled = true;
    btn.innerText = "Updating...";
    const content = document.getElementById('resume-text').value;

    if (!content || content.trim() === "") {
        showToast("Resume cannot be empty", "error");
        btn.disabled = false;
        btn.innerText = "Update Resume";
        return;
    }

    const original = document.getElementById('resume-text').dataset.original;
    if (content === original) {
        showToast("No changes detected", "info");
        btn.disabled = false;
        btn.innerText = "Update Resume";
        return;
    }

    try {
        const data = await apiCall('/resumes/', 'POST', { content });
        localStorage.setItem('resume_id', data.id);
        // UI Feedback
        document.getElementById('resume-status').innerHTML = `<p class="success">Resume updated successfully! (ID: ${data.id})</p>`;
        loadCandidateData();
    } catch (err) {
        console.error('Resume upload error:', err);
        document.getElementById('resume-status').innerHTML = `<p class="error">${err.message}</p>`;
    } finally {
        btn.disabled = false;
        btn.innerText = "Update Resume";
    }
}

async function showMatch(jobId) {
    const resumeId = localStorage.getItem('resume_id');
    if (!resumeId) {
        alert('Please upload your resume first');
        return;
    }
    try {
        const data = await apiCall('/match/', 'POST', { resume_id: parseInt(resumeId), job_id: jobId });
        // Format missing skills
        const skillsList = data.missing_keywords && data.missing_keywords.length > 0
            ? data.missing_keywords.map(s => `<span style="background:#fee2e2; color:#991b1b; padding:2px 6px; border-radius:4px; font-size:0.85em; margin-right:4px;">${s}</span>`).join('')
            : '<span style="color:#16a34a">None! Great match.</span>';

        showModal(`
            <h3>Match Results</h3>
            <div style="text-align: center; margin-bottom: 1rem;">
                <div style="font-size: 3rem; font-weight: bold; color: ${data.score >= 70 ? '#16a34a' : (data.score >= 40 ? '#ca8a04' : '#dc2626')}">${data.score}%</div>
                <p>Match Score</p>
            </div>
            <div>
                <h4>Missing Skills</h4>
                <div style="margin-top: 0.5rem;">${skillsList}</div>
            </div>
        `);
    } catch (err) {
        console.error('Match error:', err);
        showToast(err.message, 'error');
    }
}

async function applyToJob(jobId) {
    try {
        await apiCall('/applications/', 'POST', { job_id: jobId });
        console.log('Applied successfully');
        loadCandidateData();
        // alert('Application submitted successfully!'); 
    } catch (err) {
        console.error('Application error:', err);
        showToast(err.message || 'Failed to apply', 'error');
    }
}

// Recruiter Logic
async function loadRecruiterData() {
    console.log("Loading recruiter data...");
    try {
        const jobs = await apiCall('/jobs/me');
        const recruiterJobs = document.getElementById('recruiter-jobs');

        if (jobs.length === 0) {
            recruiterJobs.innerHTML = '<p>No jobs posted yet.</p>';
        } else {
            recruiterJobs.innerHTML = jobs.map(job => `
                <div class="card">
                    <h4>${job.title}</h4>
                    <p>${job.description.length > 150 ? job.description.substring(0, 150) + '...' : job.description}</p>
                    <div style="margin-top: 1rem;">
                        <button class="small" onclick="viewApplicants(${job.id})">View Applicants</button>
                        <button class="small secondary" onclick="viewInsights(${job.id})">AI Insights</button>
                    </div>
                </div>
            `).join('');
        }
    } catch (err) {
        console.error("Error loading recruiter data:", err);
        document.getElementById('recruiter-jobs').innerHTML = '<p class="error">Failed to load jobs.</p>';
    }
}

async function postJob() {
    const titleBtn = document.getElementById('job-title');
    const skillsBtn = document.getElementById('job-skills');
    const descBtn = document.getElementById('job-desc');
    const btn = document.getElementById('btn-post-job');

    const title = titleBtn.value;
    const skills = skillsBtn.value;
    const description = descBtn.value;

    if (!title || !description) {
        showToast("Please fill in both fields", "error");
        return;
    }

    btn.disabled = true;
    btn.innerText = "Posting...";

    try {
        const fullDescription = skills ? `${description}\n\nRequired Skills: ${skills}` : description;
        await apiCall('/jobs/', 'POST', { title, description: fullDescription });
        showToast('Job posted successfully!', 'success');
        titleBtn.value = '';
        skillsBtn.value = '';
        descBtn.value = '';
        loadRecruiterData();
    } catch (err) {
        console.error('Post job error:', err);
        showToast(err.message, 'error');
    } finally {
        btn.disabled = false;
        btn.innerText = "Post Job";
    }
}

async function viewApplicants(jobId) {
    try {
        const apps = await apiCall(`/applications/job/${jobId}`);
        // Sort: Match Score Descending
        apps.sort((a, b) => (b.match_score || 0) - (a.match_score || 0));

        showModal(`
            <h3>Applicants for Job ID: ${jobId}</h3>
            ${apps.length ? apps.map(app => `
                <div class="card" style="margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <p><strong>${app.candidate_email || 'Candidate ID: ' + app.candidate_id}</strong></p>
                        <p>Status: <span style="font-weight: bold; color: ${getStatusColor(app.status)}">${app.status.toUpperCase()}</span></p>
                        ${app.match_score ? `<p style="font-size: 0.9em; color: #666;">Match Score: <strong>${app.match_score}%</strong></p>` : ''}
                        ${app.missing_skills ? `<div style="margin-top:4px; font-size:0.85em;">Missing: ${app.missing_skills.split(',').map(s => `<span style="background:#fee2e2; color:#991b1b; padding:1px 4px; border-radius:3px; margin-right:2px;">${s.trim()}</span>`).join('')}</div>` : ''}
                    </div>
                    <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; justify-content: flex-end;">
                        <button class="small" style="background:#16a34a" onclick="updateStatus(${app.id}, 'shortlisted')">Shortlist</button>
                        <button class="small" style="background:#ca8a04" onclick="updateStatus(${app.id}, 'interview')">Interview</button>
                        <button class="small" style="background:#dc2626" onclick="updateStatus(${app.id}, 'rejected')">Reject</button>
                    </div>
                </div>
            `).join('') : '<p>No applicants yet.</p>'}
        `);
    } catch (err) {
        console.error('View applicants error:', err);
        showToast(err.message, 'error');
    }
}

function getStatusColor(status) {
    switch (status) {
        case 'shortlisted': return '#16a34a'; // Green
        case 'interview': return '#ca8a04';   // Yellow/Gold
        case 'rejected': return '#dc2626';    // Red
        default: return '#2563eb';            // Blue
    }
}

async function viewInsights(jobId) {
    try {
        const insights = await apiCall(`/match/job/${jobId}`);
        // Sort by score descending
        insights.sort((a, b) => b.score - a.score);

        // Stats Calculation
        const count = insights.length;
        const avgScore = count > 0 ? (insights.reduce((acc, curr) => acc + curr.score, 0) / count).toFixed(1) : 0;
        const maxScore = count > 0 ? Math.max(...insights.map(i => i.score)) : 0;

        // Common Missing Skills
        const skillCounts = {};
        insights.forEach(i => {
            if (i.missing_keywords && i.missing_keywords.length > 0) {
                // Check if string or array (backend schema varies, usually string in this project now)
                const skills = Array.isArray(i.missing_keywords) ? i.missing_keywords : i.missing_keywords.split(',');
                skills.forEach(s => {
                    const clean = s.trim();
                    if (clean) skillCounts[clean] = (skillCounts[clean] || 0) + 1;
                });
            }
        });
        const topMissing = Object.entries(skillCounts)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 3)
            .map(([skill, num]) => `${skill} (${num})`)
            .join(', ');

        showModal(`
            <h3>AI Insights</h3>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 10px; margin-bottom: 20px; text-align: center;">
                <div style="background: #f3f4f6; padding: 10px; border-radius: 8px;">
                    <div style="font-size: 1.2em; font-weight: bold;">${count}</div>
                    <div style="font-size: 0.7em; color: #666;">Applicants</div>
                </div>
                <div style="background: #f3f4f6; padding: 10px; border-radius: 8px;">
                    <div style="font-size: 1.2em; font-weight: bold; color: ${avgScore >= 70 ? '#16a34a' : '#ca8a04'}">${avgScore}%</div>
                    <div style="font-size: 0.7em; color: #666;">Avg Match</div>
                </div>
                 <div style="background: #f3f4f6; padding: 10px; border-radius: 8px;">
                    <div style="font-size: 1.2em; font-weight: bold; color: #16a34a">${maxScore}%</div>
                    <div style="font-size: 0.7em; color: #666;">Top Match</div>
                </div>
                 <div style="background: #f3f4f6; padding: 10px; border-radius: 8px;">
                    <div style="font-size: 0.8em; font-weight: bold; overflow:hidden; text-overflow:ellipsis;">${topMissing || 'None'}</div>
                    <div style="font-size: 0.7em; color: #666;">Missing</div>
                </div>
            </div>

            ${insights.length ? insights.map(i => {
            // Handle both string (backend) and potential array formats
            let missingArr = [];
            if (i.missing_keywords) {
                if (Array.isArray(i.missing_keywords)) {
                    missingArr = i.missing_keywords;
                } else if (typeof i.missing_keywords === 'string') {
                    missingArr = i.missing_keywords.split(',');
                }
            }

            const skillsList = missingArr.length > 0
                ? missingArr.map(s => `<span style="background:#fee2e2; color:#991b1b; padding:2px 6px; border-radius:4px; font-size:0.85em;">${s.trim()}</span>`).join(' ')
                : '<span>None</span>';

            return `
                <div class="card" style="margin-bottom: 0.5rem">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <p><strong>${i.candidate_email}</strong></p>
                        <span style="font-size: 1.2em; font-weight: bold; color: ${i.score >= 70 ? '#16a34a' : '#ca8a04'}">${i.score}%</span>
                    </div>
                    <p style="margin-top:0.5rem; font-size:0.9em;"><strong>Missing Skills:</strong> ${skillsList}</p>
                </div>
            `;
        }).join('') : '<p>No match data available yet.</p>'}
        `);
    } catch (err) {
        console.error('View insights error:', err);
        showToast(err.message, 'error');
    }
}

async function updateStatus(appId, status) {
    try {
        await apiCall(`/applications/${appId}`, 'PATCH', { status });
        showToast(`Status updated to ${status}`, 'success');
        closeModal(); // Optionally reload applicants if we had context, but closing is fine
    } catch (err) {
        console.error('Update status error:', err);
        showToast(err.message, 'error');
    }
}

// Demo Data Helper
function populateDemoData() {
    const jobTitle = document.getElementById('job-title');
    if (jobTitle) {
        jobTitle.value = "Senior Python Developer";
        document.getElementById('job-desc').value = "We are looking for an expert in Python, FastAPI, and AI integration. Must have experience with React or Vanilla JS.";
    }

    const resumeText = document.getElementById('resume-text');
    if (resumeText) {
        resumeText.value = "Experienced Python Developer with 5 years in FastAPI, Machine Learning, and Cloud Computing. Skilled in Docker, Kubernetes, and SQL.";
    }
}

// Modal helper
function showModal(content) {
    document.getElementById('modal-body').innerHTML = content;
    document.getElementById('modal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('modal').style.display = 'none';
}
