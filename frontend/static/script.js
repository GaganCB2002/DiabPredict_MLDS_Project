document.addEventListener('DOMContentLoaded', () => {

    // 0. Cookie Consent Toast
    const overlay = document.getElementById('consentOverlay');
    const acceptBtn = document.getElementById('consentAcceptBtn');
    const declineBtn = document.getElementById('consentDeclineBtn');

    if (overlay) {
        // Check local storage
        if (localStorage.getItem('cookieConsent')) {
            overlay.remove();
        } else {
            // Animate in after a short delay
            setTimeout(() => {
                overlay.classList.remove('translate-y-full', 'opacity-0', 'pointer-events-none');
            }, 1000);
            
            const handleConsent = (status) => {
                localStorage.setItem('cookieConsent', status);
                overlay.classList.add('translate-y-full', 'opacity-0', 'pointer-events-none');
                setTimeout(() => overlay.remove(), 500);
            };

            if (acceptBtn) acceptBtn.addEventListener('click', () => handleConsent('accepted'));
            if (declineBtn) declineBtn.addEventListener('click', () => handleConsent('declined'));
        }
    }

    // 1. Lenis Smooth Scroll
    let lenis = null;
    try {
        lenis = new Lenis({
            duration: 2.5, /* Increased for smoother premium feel */
            easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
            direction: 'vertical',
            gestureDirection: 'vertical',
            smooth: true,
            mouseMultiplier: 0.8,
            smoothTouch: false,
        });

        function raf(time) {
            if (lenis) lenis.raf(time);
            requestAnimationFrame(raf);
        }
        requestAnimationFrame(raf);
    } catch (e) {
        console.warn('Lenis not available:', e);
    }

    // 2. Premium Video Parallax Background
    const initVideoParallax = () => {
        const video = document.getElementById('bg-video');
        if (!video) return;

        let scrollY = 0;
        if (lenis) {
            lenis.on('scroll', (e) => { scrollY = e.scroll; });
        }

        // Interactive Mouse Parallax
        let mouseX = 0;
        let mouseY = 0;
        let targetMouseX = 0;
        let targetMouseY = 0;
        const windowHalfX = window.innerWidth / 2;
        const windowHalfY = window.innerHeight / 2;

        document.addEventListener('mousemove', (event) => {
            targetMouseX = (event.clientX - windowHalfX) * 0.05;
            targetMouseY = (event.clientY - windowHalfY) * 0.05;
        });

        // Ensure video has transform origin center for smooth scaling/moving
        video.style.transformOrigin = "center center";

        const tick = () => {
            // Smooth Mouse Interpolation
            mouseX += (targetMouseX - mouseX) * 0.05;
            mouseY += (targetMouseY - mouseY) * 0.05;
            
            // Calculate parallax based on scroll
            const yOffset = scrollY * 0.15;
            
            // Apply scale (to prevent borders showing during parallax) and translate
            video.style.transform = `translate3d(${mouseX}px, ${yOffset + mouseY}px, 0) scale(1.05)`;
            
            requestAnimationFrame(tick);
        };
        tick();

        const nav = document.querySelector('nav');
        if (nav && lenis) {
            lenis.on('scroll', (e) => {
                if (e.scroll > 50) {
                    nav.classList.add('navbar-blur');
                } else {
                    nav.classList.remove('navbar-blur');
                }
            });
        }
    };
    initVideoParallax();

    // 3. GSAP ScrollTrigger Animations
    if (typeof gsap !== 'undefined') {
        try {
            gsap.registerPlugin(ScrollTrigger);

            // Premium Reverse Storytelling
            gsap.utils.toArray(".clip-reveal").forEach(el => {
                gsap.fromTo(el,
                    { clipPath: "polygon(0 100%, 100% 100%, 100% 100%, 0 100%)", opacity: 0, y: 20 },
                    {
                        scrollTrigger: { trigger: el, start: "top 85%", toggleActions: "play none none reverse" },
                        clipPath: "polygon(0 0, 100% 0, 100% 100%, 0 100%)",
                        opacity: 1, y: 0,
                        duration: 1.5,
                        ease: "power4.out"
                    }
                );
            });

            gsap.utils.toArray(".scroll-fade").forEach(el => {
                gsap.fromTo(el, 
                    { opacity: 0, y: 50, filter: "blur(8px)" },
                    {
                        scrollTrigger: { trigger: el, start: "top 90%", end: "top 60%", scrub: 1 },
                        opacity: 1, y: 0, filter: "blur(0px)"
                    }
                );
            });

            // Scroll-based Marquee and Coding Text Movement (Scrubbing)
            gsap.utils.toArray(".coding-text-effect:not(.reverse)").forEach(el => {
                gsap.to(el, {
                    scrollTrigger: { trigger: el, start: "top bottom", end: "bottom top", scrub: 1 },
                    xPercent: -50,
                    ease: "none"
                });
            });

            // Typing effect for Neural Workflow code blocks
            gsap.utils.toArray(".coding-effect-container").forEach(container => {
                const textEl = container.querySelector('.coding-effect');
                if (!textEl) return;
                const fullText = textEl.getAttribute('data-code');
                if (!fullText) return;
                
                textEl.textContent = ''; // Start empty
                
                ScrollTrigger.create({
                    trigger: container,
                    start: "top 85%",
                    onEnter: () => {
                        let i = 0;
                        textEl.textContent = '';
                        clearInterval(container.typeInterval);
                        container.typeInterval = setInterval(() => {
                            textEl.textContent += fullText.charAt(i);
                            i++;
                            if (i >= fullText.length) {
                                clearInterval(container.typeInterval);
                            }
                        }, 15); // Fast typing effect
                    },
                    onLeaveBack: () => {
                        // Reset when scrolling back up to type again
                        clearInterval(container.typeInterval);
                        textEl.textContent = '';
                    }
                });
            });

            gsap.utils.toArray(".coding-text-effect.reverse").forEach(el => {
                gsap.to(el, {
                    scrollTrigger: { trigger: el, start: "top bottom", end: "bottom top", scrub: 1 },
                    xPercent: 50,
                    ease: "none"
                });
            });

            gsap.utils.toArray(".scroll-fade-up").forEach(el => {
                gsap.from(el, {
                    scrollTrigger: { 
                        trigger: el, 
                        start: "top 85%", 
                        toggleActions: "play none none reverse" // Reverses cleanly when scrolling up
                    },
                    opacity: 0, y: 80, scale: 0.95, filter: "blur(12px)", duration: 1.2, ease: "power3.out"
                });
            });

            // 3D Scroll Scrubbing on Glass Cards
            gsap.utils.toArray(".glass-card").forEach(card => {
                gsap.to(card, {
                    scrollTrigger: {
                        trigger: card,
                        start: "top 95%",
                        end: "bottom 5%",
                        scrub: 1.5
                    },
                    rotationX: () => -3 + Math.random() * 6,
                    rotationY: () => -3 + Math.random() * 6,
                    z: 50,
                    ease: "none",
                    transformPerspective: 1000,
                    transformOrigin: "center center"
                });
            });



            gsap.utils.toArray(".scroll-scale-x").forEach(el => {
                gsap.to(el, {
                    scrollTrigger: { trigger: el, start: "top 80%", end: "top 30%", scrub: 1 },
                    scaleX: 1
                });
            });

            const counters = document.querySelectorAll('.counter:not([data-api-key])');
            counters.forEach(counter => {
                ScrollTrigger.create({
                    trigger: counter,
                    start: "top 80%",
                    once: true,
                    onEnter: () => {
                        const target = +counter.getAttribute('data-target');
                        const isDecimal = target % 1 !== 0;
                        const decimals = isDecimal ? String(target).split('.')[1].length : 0;
                        gsap.to(counter, {
                            val: target,
                            duration: 2.5,
                            ease: "power3.out",
                            onUpdate: function() {
                                const v = this.targets()[0].val;
                                counter.innerHTML = isDecimal ? v.toFixed(decimals) : Math.round(v).toLocaleString();
                            }
                        });
                    }
                });
            });
        } catch (e) {
            console.warn('GSAP init failed:', e);
        }
    }

    // 4. Chart.js defaults
    if (typeof Chart !== 'undefined') {
        try {
            Chart.defaults.color = '#6B7280';
            Chart.defaults.font.family = "'Inter', sans-serif";
            Chart.defaults.borderColor = 'rgba(0,0,0,0.08)';
        } catch (e) {
            console.warn('Chart init failed:', e);
        }
    }

    // Risk Distribution Chart from API
    const riskChartCanvas = document.getElementById('riskChart');
    if (riskChartCanvas && typeof Chart !== 'undefined') {
        fetch('/api/dashboard')
            .then(r => r.json())
            .then(stats => {
                try {
                    new Chart(riskChartCanvas, {
                        type: 'doughnut',
                        data: {
                            labels: ['High Risk', 'Low Risk'],
                            datasets: [{
                                data: [stats.high_risk || 0, stats.low_risk || 1],
                                backgroundColor: ['#DC2626', '#0891B2'],
                                borderWidth: 0,
                                cutout: '70%'
                            }]
                        },
                        options: {
                            responsive: true, maintainAspectRatio: false,
                            plugins: {
                                legend: { position: 'bottom', labels: { usePointStyle: true, padding: 20, color: '#6B7280' } }
                            }
                        }
                    });
                } catch (e) {
                    console.warn('Risk chart error:', e);
                }
            })
            .catch(() => {
                try {
                    new Chart(riskChartCanvas, {
                        type: 'doughnut',
                        data: {
                            labels: ['No Data'],
                            datasets: [{ data: [1], backgroundColor: ['rgba(0,0,0,0.05)'], borderWidth: 0, cutout: '70%' }]
                        },
                        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
                    });
                } catch (e) {}
            });
    }

    let radarChartObj = null;

    // 5. Prediction Form – Validation + Backend
    const form = document.getElementById('predictionForm');
    const formError = document.getElementById('formError');

    function validateField(id, min, max) {
        const el = document.getElementById(id);
        const val = parseFloat(el.value);
        const msg = el.parentElement.querySelector('.validation-msg');
        let valid = true;
        if (el.value.trim() === '' || isNaN(val) || val < min || val > max) {
            el.classList.add('border-red-500');
            el.classList.remove('border-[#D1D5DB]');
            if (msg) msg.classList.remove('hidden');
            valid = false;
        } else {
            el.classList.remove('border-red-500');
            el.classList.add('border-[#D1D5DB]');
            if (msg) msg.classList.add('hidden');
        }
        return valid;
    }

    function validateForm() {
        let ok = true;
        const name = document.getElementById('name');
        const nameMsg = name.parentElement.querySelector('.validation-msg');
        if (name.value.trim() === '') {
            name.classList.add('border-red-500');
            if (nameMsg) nameMsg.classList.remove('hidden');
            ok = false;
        } else {
            name.classList.remove('border-red-500');
            if (nameMsg) nameMsg.classList.add('hidden');
        }
        const fields = [
            { id: 'glucose', min: 0, max: 300 },
            { id: 'bmi', min: 0, max: 100 },
            { id: 'age', min: 0, max: 120 },
            { id: 'bloodPressure', min: 0, max: 300 },
            { id: 'insulin', min: 0, max: 1000 },
            { id: 'skinThickness', min: 0, max: 100 },
            { id: 'pregnancies', min: 0, max: 20 },
            { id: 'diabetesPedigreeFunction', min: 0, max: 10 }
        ];
        fields.forEach(f => { if (!validateField(f.id, f.min, f.max)) ok = false; });
        return ok;
    }

    if (form) {
        const nameEl = document.getElementById('name');
        if (nameEl) {
            nameEl.addEventListener('blur', () => {
                const msg = nameEl.parentElement.querySelector('.validation-msg');
                if (nameEl.value.trim() === '') {
                    nameEl.classList.add('border-red-500');
                    if (msg) msg.classList.remove('hidden');
                } else {
                    nameEl.classList.remove('border-red-500');
                    if (msg) msg.classList.add('hidden');
                }
            });
        }
        ['glucose','bmi','age','bloodPressure','insulin','skinThickness','pregnancies','diabetesPedigreeFunction'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.addEventListener('blur', () => validateField(id, 0, parseFloat(el.max) || 1000));
        });
    }

    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            if (!validateForm()) {
                if (formError) {
                    formError.textContent = 'Please fix the highlighted fields before submitting.';
                    formError.classList.remove('hidden');
                }
                return;
            }
            if (formError) formError.classList.add('hidden');

            const authEl = document.getElementById('authStatus');
            if (authEl && authEl.dataset.authenticated !== 'true') {
                window.location.href = '/login?next=/';
                return;
            }

            const btnText = document.getElementById('btn-text');
            const btnIcon = document.getElementById('btn-icon');
            const submitBtn = document.getElementById('submitBtn');

            btnText.textContent = 'Generating Report...';
            btnIcon.className = 'fa-solid fa-spinner fa-spin';
            submitBtn.style.pointerEvents = 'none';
            submitBtn.style.opacity = '0.5';

            const fd = new FormData(form);
            const inputData = {};
            fd.forEach((v, k) => { if (k !== 'name') inputData[k] = parseFloat(v); });

            const name = document.getElementById('name').value.trim();

            fetch('/predict', {
                method: 'POST',
                body: fd
            })
            .then(r => r.json())
            .then(res => {
                if (res.error) throw new Error(res.error);
                // Fetch previous results for same patient
                fetch('/api/predictions/by-name?name=' + encodeURIComponent(name))
                    .then(r2 => r2.json())
                    .then(history => {
                        showResult(res, inputData, history);
                    })
                    .catch(() => {
                        showResult(res, inputData, []);
                    });
                btnText.textContent = 'Execute Analysis';
                btnIcon.className = 'fa-solid fa-arrow-right';
                submitBtn.style.pointerEvents = '';
                submitBtn.style.opacity = '';
            })
            .catch(err => {
                if (formError) {
                    formError.textContent = err.message || 'Server error generating report. Please try again.';
                    formError.classList.remove('hidden');
                }
                btnText.textContent = 'Execute Analysis';
                btnIcon.className = 'fa-solid fa-arrow-right';
                submitBtn.style.pointerEvents = '';
                submitBtn.style.opacity = '';
            });
        });
    }

    const NORMAL_RANGES = {
        glucose: { min: 70, max: 100, unit: 'mg/dL', label: 'Glucose', assess: (v) => v <= 100 ? 'Normal fasting glucose.' : v <= 125 ? 'Pre-diabetic range. Monitor closely.' : 'Elevated — diabetic range. Consult physician.' },
        bmi: { min: 18.5, max: 24.9, unit: '', label: 'BMI', assess: (v) => v < 18.5 ? 'Underweight.' : v <= 24.9 ? 'Healthy weight range.' : v <= 29.9 ? 'Overweight. Increased diabetes risk.' : 'Obese. High diabetes risk.' },
        age: { min: 0, max: 120, unit: 'yrs', label: 'Age', assess: (v) => v < 30 ? 'Low age-related risk.' : v < 45 ? 'Moderate age-related risk.' : v < 60 ? 'Elevated age-related risk.' : 'High age-related risk. Regular screening advised.' },
        bloodPressure: { min: 60, max: 80, unit: 'mmHg', label: 'Blood Pressure', assess: (v) => v <= 80 ? 'Normal diastolic pressure.' : v <= 90 ? 'Elevated. Monitor regularly.' : 'Hypertensive. Medical evaluation recommended.' },
        insulin: { min: 16, max: 166, unit: 'IU/mL', label: 'Insulin', assess: (v) => v >= 16 && v <= 166 ? 'Normal insulin level.' : v < 16 ? 'Low insulin production. May indicate pancreatic dysfunction.' : 'Elevated insulin. Possible insulin resistance.' },
        skinThickness: { min: 10, max: 40, unit: 'mm', label: 'Skin Thickness', assess: (v) => v >= 10 && v <= 40 ? 'Within typical range.' : v < 10 ? 'Below average.' : 'Above average body fat indicator.' },
        pregnancies: { min: 0, max: 20, unit: '', label: 'Pregnancies', assess: (v) => v === 0 ? 'No pregnancy history.' : v <= 3 ? 'Low parity.' : v <= 6 ? 'Moderate parity. Monitor gestational diabetes history.' : 'High parity. Elevated risk.' },
        diabetesPedigreeFunction: { min: 0, max: 0.5, unit: '', label: 'Pedigree Func.', assess: (v) => v <= 0.5 ? 'Low genetic predisposition.' : v <= 0.8 ? 'Moderate genetic risk factor.' : 'Strong genetic predisposition to diabetes.' }
    };

    const FIELD_MAP = {
        glucose: 'glucose', bmi: 'bmi', age: 'age', bloodPressure: 'bloodPressure',
        insulin: 'insulin', skinThickness: 'skinThickness',
        pregnancies: 'pregnancies', diabetesPedigreeFunction: 'diabetesPedigreeFunction'
    };

    function getStatusClass(val, min, max) {
        if (val >= min && val <= max) return 'text-brand-emerald';
        if (val < min) return 'text-brand-warning';
        return 'text-brand-danger';
    }

    function getStatusLabel(val, min, max) {
        if (val >= min && val <= max) return 'Normal';
        if (val < min) return 'Below';
        return 'Above';
    }

    function renderDetailedMetrics(res, history) {
        const container = document.getElementById('detailedMetrics');
        const tbody = document.getElementById('metricsDetailBody');
        container.classList.remove('hidden');
        let html = '';
        for (const [key, field] of Object.entries(FIELD_MAP)) {
            const range = NORMAL_RANGES[key];
            const val = parseFloat(res[field]) || 0;
            const statusClass = getStatusClass(val, range.min, range.max);
            const statusLabel = getStatusLabel(val, range.min, range.max);
            html += `<tr class="border-b border-[#E8E0D8]">
                <td class="px-4 py-3 font-medium">${range.label}</td>
                <td class="px-4 py-3 font-bold tabular-nums">${val}${range.unit ? ' ' + range.unit : ''}</td>
                <td class="px-4 py-3 text-gray-400">${range.min}${range.max ? ' – ' + range.max : '+'}${range.unit ? ' ' + range.unit : ''}</td>
                <td class="px-4 py-3"><span class="${statusClass} font-bold text-xs px-2 py-1 rounded-full ${statusClass === 'text-brand-emerald' ? 'bg-emerald-50' : statusClass === 'text-brand-warning' ? 'bg-yellow-50' : 'bg-red-50'}">${statusLabel}</span></td>
                <td class="px-4 py-3 text-gray-400 text-xs max-w-[200px]">${range.assess(val)}</td>
            </tr>`;
        }
        tbody.innerHTML = html;
    }

    function renderHistoryComparison(res, history) {
        const container = document.getElementById('historyComparison');
        const tbody = document.getElementById('historyComparisonBody');
        const nameSpan = document.getElementById('historyPatientName');
        // Filter out the current prediction and any null entries
        const prev = (history || []).filter(p => p.id !== res.id);
        if (prev.length === 0) {
            container.classList.add('hidden');
            return;
        }
        container.classList.remove('hidden');
        nameSpan.textContent = res.name || 'Patient';
        let html = '';
        prev.slice(0, 10).forEach(p => {
            const isHigh = p.prediction == 1;
            const prob = (p.probability * 100).toFixed(1);
            const riskClass = isHigh ? 'text-brand-danger' : 'text-brand-emerald';
            const riskLabel = isHigh ? 'HIGH' : 'LOW';
            html += `<tr class="border-b border-[#E8E0D8]">
                <td class="px-4 py-3 text-xs">${p.timestamp ? p.timestamp.split(' ')[0] : '-'}</td>
                <td class="px-4 py-3"><span class="${riskClass} font-bold text-xs">${riskLabel}</span></td>
                <td class="px-4 py-3 tabular-nums ${riskClass}">${prob}%</td>
                <td class="px-4 py-3">${p.glucose || '-'}</td>
                <td class="px-4 py-3">${p.bmi || '-'}</td>
                <td class="px-4 py-3">${p.bloodPressure || '-'}</td>
                <td class="px-4 py-3">${p.insulin || '-'}</td>
            </tr>`;
        });
        tbody.innerHTML = html;
    }

    const showResult = (res, inputData, history) => {
        const resultArea = document.getElementById('resultArea');
        const conf = document.getElementById('resultConfidence');
        const verdict = document.getElementById('resultVerdict');
        const msg = document.getElementById('resultMessage');
        
        if (typeof gsap === 'undefined') {
            document.getElementById('predictionForm').style.display = 'none';
            resultArea.classList.remove('opacity-0', 'pointer-events-none', 'translate-x-12');
            resultArea.classList.add('opacity-100', 'translate-x-0');
            const prob = res.probability * 100;
            const isHigh = res.prediction === 1;
            conf.textContent = prob.toFixed(1);
            conf.style.color = isHigh ? '#DC2626' : '#0891B2';
            verdict.textContent = isHigh ? 'CRITICAL RISK DETECTED' : 'NOMINAL RANGE';
            verdict.style.color = isHigh ? '#DC2626' : '#0891B2';
            msg.textContent = res.message;
            renderRadar(inputData, isHigh);
            renderDetailedMetrics(res, history || []);
            renderHistoryComparison(res, history || []);
            return;
        }
        gsap.to("#predictionForm > div", {
            opacity: 0, x: -50, duration: 0.5, stagger: 0.1, ease: "power2.in",
            onComplete: () => {
                document.getElementById('predictionForm').style.display = 'none';
                resultArea.classList.remove('opacity-0', 'pointer-events-none', 'translate-x-12');
                resultArea.classList.add('opacity-100', 'translate-x-0');
                const prob = res.probability * 100;
                const isHigh = res.prediction === 1;
                let obj = { val: 0 };
                gsap.to(obj, {
                    val: prob, duration: 2, ease: "power4.out",
                    onUpdate: () => {
                        conf.textContent = obj.val.toFixed(1);
                        conf.style.color = isHigh ? '#DC2626' : '#0891B2';
                    }
                });
                verdict.textContent = isHigh ? 'CRITICAL RISK DETECTED' : 'NOMINAL RANGE';
                verdict.style.color = isHigh ? '#DC2626' : '#0891B2';
                msg.textContent = res.message;
                renderRadar(inputData, isHigh);
                renderDetailedMetrics(res, history || []);
                renderHistoryComparison(res, history || []);
            }
        });
    };

    const renderRadar = (data, isHigh) => {
        const ctx = document.getElementById('radarChart').getContext('2d');
        if (radarChartObj) radarChartObj.destroy();
        const color = isHigh ? '#DC2626' : '#0891B2';
        const vals = [
            Math.min((data.glucose / 200) * 100, 100),
            Math.min((data.bmi / 50) * 100, 100),
            Math.min((data.age / 80) * 100, 100),
            Math.min((data.bloodPressure / 120) * 100, 100),
            Math.min((data.insulin / 300) * 100, 100)
        ];
        radarChartObj = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['GLU', 'BMI', 'AGE', 'B.P.', 'INS'],
                datasets: [{
                    data: vals,
                    backgroundColor: isHigh ? 'rgba(239, 68, 68, 0.2)' : 'rgba(6, 182, 212, 0.2)',
                    borderColor: color,
                    borderWidth: 1,
                    pointBackgroundColor: '#000',
                    pointBorderColor: color
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    r: {
                        angleLines: { color: 'rgba(255,255,255,0.05)' },
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        pointLabels: { color: '#6b7280', font: { family: 'Space Grotesk', size: 10 } },
                        ticks: { display: false }
                    }
                }
            }
        });
    };

    // 6. Terminal / AI Assistant
    const termToggle = document.getElementById('terminal-toggle');
    const term = document.getElementById('ai-terminal');
    const closeTerm = document.getElementById('close-terminal');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');

    if (termToggle && term) {
        termToggle.addEventListener('click', () => {
            term.classList.remove('translate-y-full');
            termToggle.classList.add('opacity-0', 'pointer-events-none');
            setTimeout(() => chatInput.focus(), 700);
        });
        closeTerm.addEventListener('click', () => {
            term.classList.add('translate-y-full');
            termToggle.classList.remove('opacity-0', 'pointer-events-none');
        });
        chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const msg = chatInput.value.trim();
            if(!msg) return;
            const userDiv = document.createElement('div');
            userDiv.className = 'text-white';
            userDiv.innerHTML = '<span class="text-gray-500 mr-2">USR></span> ' + msg;
            chatMessages.appendChild(userDiv);
            chatInput.value = '';
            chatInput.disabled = true;
            chatMessages.scrollTop = chatMessages.scrollHeight;
            const loadDiv = document.createElement('div');
            loadDiv.className = 'text-gray-500 animate-pulse';
            loadDiv.innerHTML = '<span class="text-brand-accent mr-2">SYS></span> Processing query...';
            chatMessages.appendChild(loadDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: msg })
            })
            .then(r => r.json())
            .then(data => {
                loadDiv.remove();
                const aiDiv = document.createElement('div');
                aiDiv.className = 'text-gray-400';
                aiDiv.innerHTML = '<span class="text-brand-accent mr-2">SYS></span> ' + (data.reply || 'Error computing.');
                chatMessages.appendChild(aiDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            })
            .catch(err => { 
                loadDiv.remove(); 
                const errDiv = document.createElement('div');
                errDiv.className = 'text-brand-danger';
                errDiv.innerHTML = '<span class="text-brand-accent mr-2">SYS></span> Connection error: ' + err.message;
                chatMessages.appendChild(errDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            })
            .finally(() => {
                chatInput.disabled = false;
                chatInput.focus();
            });
        });
    }

    // 8. Dashboard API Integration
    (function loadDashboard() {
        const section = document.getElementById('overview');
        if (!section) return;
        fetch('/api/dashboard')
            .then(r => r.json())
            .then(stats => {
                document.querySelectorAll('.counter[data-api-key]').forEach(el => {
                    const key = el.dataset.apiKey;
                    const val = parseFloat(stats[key]) || 0;
                    const decimals = parseInt(el.dataset.decimals) || 0;
                    el.dataset.target = val;
                    if (typeof ScrollTrigger !== 'undefined' && typeof gsap !== 'undefined') {
                        try {
                            ScrollTrigger.create({
                                trigger: el,
                                start: 'top 80%',
                                once: true,
                                onEnter: () => {
                                    gsap.to(el, {
                                        val: val,
                                        duration: 2.5,
                                        ease: 'power3.out',
                                        onUpdate: function() {
                                            const v = this.targets()[0].val;
                                            el.innerHTML = decimals > 0 ? v.toFixed(decimals) : Math.round(v).toLocaleString();
                                        }
                                    });
                                }
                            });
                        } catch (e) {
                            el.innerHTML = decimals > 0 ? val.toFixed(decimals) : Math.round(val).toLocaleString();
                        }
                    } else {
                        el.innerHTML = decimals > 0 ? val.toFixed(decimals) : Math.round(val).toLocaleString();
                    }
                });
            })
            .catch(err => {
                console.error('Dashboard API error:', err);
                document.querySelectorAll('.counter[data-api-key]').forEach(el => {
                    const target = parseFloat(el.dataset.target) || 0;
                    const decimals = parseInt(el.dataset.decimals) || 0;
                    el.innerHTML = decimals > 0 ? target.toFixed(decimals) : Math.round(target).toLocaleString();
                });
            });
    })();

    // 7. Subtle UI Enhancements
    const heroText = document.querySelector('.hero-text-container');
    if (heroText) {
        document.addEventListener('mousemove', (e) => {
            const rx = (e.clientX / window.innerWidth - 0.5) * 15;
            const ry = (e.clientY / window.innerHeight - 0.5) * 15;
            gsap.to(heroText, { x: rx, y: ry, duration: 2, ease: 'power2.out' });
        });
    }

    // Scroll progress bar
    const progressRing = document.createElement('div');
    progressRing.style.cssText = 'position:fixed;bottom:8px;left:50%;transform:translateX(-50%);z-index:45;width:80px;height:3px;background:rgba(0,0,0,0.08);border-radius:2px;overflow:hidden';
    const progressFill = document.createElement('div');
    progressFill.style.cssText = 'width:0%;height:100%;background:linear-gradient(90deg,#2563EB,#0891B2);border-radius:2px;transition:width 0.1s linear';
    progressRing.appendChild(progressFill);
    document.body.appendChild(progressRing);
    if (lenis) {
        lenis.on('scroll', (e) => {
            const denom = document.documentElement.scrollHeight - window.innerHeight;
            const pct = denom > 0 ? (e.scroll / denom) * 100 : 0;
            progressFill.style.width = Math.min(pct, 100) + '%';
        });
    }
});
