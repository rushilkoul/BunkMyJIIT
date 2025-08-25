const themeToggle = document.getElementById('theme-toggle');

const currentTheme = localStorage.getItem('theme') || 'light';
document.body.className = currentTheme + '-theme';
updateThemeUI(currentTheme);

themeToggle.addEventListener('click', () => {
    const isDark = document.body.classList.contains('dark-theme');
    const newTheme = isDark ? 'light' : 'dark';

    document.body.className = newTheme + '-theme';
    localStorage.setItem('theme', newTheme);
    updateThemeUI(newTheme);
});

function updateThemeUI(theme) {
    if (theme === 'dark') {
        themeToggle.className = 'bi bi-sun';
    } else {
        themeToggle.className = 'bi bi-moon';
    }
}

const campusPills = document.querySelectorAll('.campus-pill');
const campusPillsContainer = document.querySelector('.campus-pills');
const campusPillBackground = campusPillsContainer.querySelector('.campus-pill-background');

const storedCampus = localStorage.getItem('selectedCampus') || 'btech-62';
let selectedCampus = storedCampus;

function repositionCampusPillBackground() {
    const activePill = campusPillsContainer.querySelector('.campus-pill.active');
    if (!activePill) return;
    campusPillBackground.style.left = activePill.offsetLeft + 'px';
    campusPillBackground.style.width = activePill.offsetWidth + 'px';
}

function setActiveCampus(campus) {
    campusPills.forEach((p) => {
        p.classList.toggle('active', p.dataset.campus === campus);
    });
    repositionCampusPillBackground();
}

setActiveCampus(selectedCampus);

campusPills.forEach((pill) => {
    pill.addEventListener('click', () => {
        selectedCampus = pill.dataset.campus;
        localStorage.setItem('selectedCampus', selectedCampus);
        setActiveCampus(selectedCampus);
    });
});

const dayPills = document.querySelectorAll('.day-pill');
const dayPillsContainer = document.querySelector('.day-pills');
const pillBackground = document.querySelector('.pill-background');

const storedDay = localStorage.getItem('selectedDay') || 'Monday';
let selectedDay = storedDay;

function repositionActivePillBackground() {
    const activePill = document.querySelector('.day-pill.active');
    if (!activePill) return;
    pillBackground.style.left = activePill.offsetLeft + 'px';
    pillBackground.style.width = activePill.offsetWidth + 'px';
}

function setActiveDay(day) {
    let activeIndex = 0;
    dayPills.forEach((p, i) => {
        if (p.dataset.day === day) {
            activeIndex = i;
            p.classList.add('active');
        } else {
            p.classList.remove('active');
        }
    });
    repositionActivePillBackground();
}

// Initialize active day from storage (or Monday)
setActiveDay(selectedDay);

dayPills.forEach((pill) => {
    pill.addEventListener('click', () => {
        selectedDay = pill.dataset.day;
        localStorage.setItem('selectedDay', selectedDay);
        setActiveDay(selectedDay);
    });
});

let resizeTimer;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
        repositionActivePillBackground();
        repositionCampusPillBackground();
    }, 100);
});

window.addEventListener('load', () => {
    repositionActivePillBackground();
    repositionCampusPillBackground();
});

const pickerFrom = document.getElementById('picker_from');
const pickerTo = document.getElementById('picker_to');

function toAmPm(time24) {
    if (!time24) return '';
    const [hh, mm] = time24.split(':');
    let hours = parseInt(hh, 10);
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    if (hours === 0) hours = 12;
    return `${hours}:${mm} ${ampm}`;
}

function amPmTo24h(amPmStr) {
    if (!amPmStr) return '';
    const match = amPmStr.trim().match(/^(\d{1,2}):(\d{2})\s*(AM|PM)$/i);
    if (!match) return '';
    let hours = parseInt(match[1], 10);
    const minutes = match[2];
    const period = match[3].toUpperCase();
    if (period === 'AM') {
        if (hours === 12) hours = 0;
    } else {
        if (hours !== 12) hours += 12;
    }
    const hh = String(hours).padStart(2, '0');
    return `${hh}:${minutes}`;
}

const storedFrom24 = localStorage.getItem('fromTime24');
const storedTo24 = localStorage.getItem('toTime24');
const legacyFrom = localStorage.getItem('fromTime'); // e.g., "8:00 AM"
const legacyTo = localStorage.getItem('toTime');

const initialFrom = storedFrom24 || (legacyFrom ? amPmTo24h(legacyFrom) : '');
const initialTo = storedTo24 || (legacyTo ? amPmTo24h(legacyTo) : '');

function buildTimePicker(rootEl, storageKey, initial24h, allowedHours, onChange) {
    rootEl.classList.add('tp-root');
    rootEl.innerHTML = `
                    <button type="button" class="time-display" aria-haspopup="listbox" aria-expanded="false"></button>
                    <div class="time-popover" role="listbox" hidden></div>
                `;
    const displayBtn = rootEl.querySelector('.time-display');
    const popover = rootEl.querySelector('.time-popover');

    const options = [];
    const hoursToRender = Array.isArray(allowedHours) && allowedHours.length ? allowedHours : Array.from({ length: 13 }, (_, i) => 8 + i);
    hoursToRender.forEach((h) => {
        const hh = String(h).padStart(2, '0');
        const v24 = `${hh}:00`;
        const label = toAmPm(v24);
        const opt = document.createElement('button');
        opt.type = 'button';
        opt.className = 'time-option';
        opt.setAttribute('role', 'option');
        opt.dataset.value24 = v24;
        opt.textContent = label;
        options.push(opt);
        popover.appendChild(opt);
    });

    function setValue(v24) {
        if (!v24) {
            displayBtn.textContent = rootEl.dataset.label || 'Time';
            rootEl.dataset.value24 = '';
            options.forEach(o => o.classList.remove('selected'));
            return;
        }
        displayBtn.textContent = toAmPm(v24);
        rootEl.dataset.value24 = v24;
        options.forEach(o => {
            o.classList.toggle('selected', o.dataset.value24 === v24);
        });
        localStorage.setItem(storageKey, v24);
    }

    const allowedSet = new Set(hoursToRender.map(h => `${String(h).padStart(2, '0')}:00`));
    if (initial24h && allowedSet.has(initial24h)) {
        setValue(initial24h);
    } else {
        setValue('');
    }

    displayBtn.addEventListener('click', () => {
        const isHidden = popover.hasAttribute('hidden');
        document.querySelectorAll('.time-popover').forEach(p => p.setAttribute('hidden', ''));
        if (isHidden) {
            popover.removeAttribute('hidden');
            displayBtn.setAttribute('aria-expanded', 'true');
        } else {
            popover.setAttribute('hidden', '');
            displayBtn.setAttribute('aria-expanded', 'false');
        }
    });

    options.forEach(opt => {
        opt.addEventListener('click', () => {
            const newVal = opt.dataset.value24;
            setValue(newVal);
            popover.setAttribute('hidden', '');
            displayBtn.setAttribute('aria-expanded', 'false');
            if (typeof onChange === 'function') onChange(newVal);
        });
    });

    document.addEventListener('click', (e) => {
        if (!rootEl.contains(e.target)) {
            popover.setAttribute('hidden', '');
            displayBtn.setAttribute('aria-expanded', 'false');
        }
    });

    return {
        get value24() { return rootEl.dataset.value24 || ''; },
        set(value24) { setValue(value24); }
    };
}

const fromHours = Array.from({ length: 10 }, (_, i) => 7 + i);
const toHours = Array.from({ length: 11 }, (_, i) => 7 + i);

const toAllowedSet = new Set(toHours.map(h => `${String(h).padStart(2, '0')}:00`));

const toPicker = buildTimePicker(pickerTo, 'toTime24', initialTo, toHours);
const fromPicker = buildTimePicker(pickerFrom, 'fromTime24', initialFrom, fromHours, (newFrom) => {
    const [fh, fm] = newFrom.split(':');
    const h = parseInt(fh, 10) + 1;
    const candidate = `${String(h).padStart(2, '0')}:${fm}`;
    if (toAllowedSet.has(candidate)) {
        toPicker.set(candidate);
    }
});

function validateTimeRange(fromTime, toTime) {
    if (!fromTime || !toTime) return { isValid: false, message: "Please select both start and end times." };
    
    const from24 = fromTime;
    const to24 = toTime;
    
    const fromMinutes = parseInt(from24.split(':')[0]) * 60 + parseInt(from24.split(':')[1]);
    const toMinutes = parseInt(to24.split(':')[0]) * 60 + parseInt(to24.split(':')[1]);
    
    if (fromMinutes >= toMinutes) {
        return { isValid: false, message: "From time cannot be after or equal to To time." };
    }
    
    return { isValid: true };
}

function showTimeValidationError() {
    const fromContainer = document.querySelector('#picker_from').closest('.time-picker-container');
    const toContainer = document.querySelector('#picker_to').closest('.time-picker-container');
    
    fromContainer.classList.add('time-error');
    toContainer.classList.add('time-error');
    
    let responseElm = document.getElementById("res");
    responseElm.innerText = "From time cannot be after To time";
    responseElm.classList.add('error-message');
    
    setTimeout(() => {
        fromContainer.classList.remove('time-error');
        toContainer.classList.remove('time-error');
        responseElm.classList.remove('error-message');
        responseElm.innerText = "";
    }, 2000);
}

function populateAvailableRooms(rooms) {
    let roomArray = rooms.split(',').map(room => room.trim());
    let responseParent = document.querySelector(".responses-container");
    responseParent.innerHTML = '';
    roomArray.forEach(room => {
        let roomDiv = document.createElement("div");
        roomDiv.className = "free-class";
        roomDiv.innerHTML = `<i class="bi bi-backpack2"></i><div><h1>${room}</h1><p>Available</p></div>`;
        responseParent.appendChild(roomDiv);
    });
    // trim whitespace 

}

async function getRoomLocation(roomID) {
    const response = await fetch("/api/getRoomLocation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            room_id: roomID
        })
    });
    const data = await response.json();
    alert(data.message)

}

document.getElementById("check-button").addEventListener("click", async () => {
    const fromRaw = fromPicker.value24;
    const toRaw = toPicker.value24;

    const validation = validateTimeRange(fromRaw, toRaw);
    if (!validation.isValid) {
        showTimeValidationError();
        return;
    }

    const response = await fetch("/api/tabledata", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            campus: selectedCampus,
            day: selectedDay,
            from: toAmPm(fromRaw),
            to: toAmPm(toRaw)
        })
    });
    const data = await response.json();

    let responseElm = document.getElementById("res");
    if (data.status === "success") {
        if (data.free_classes && data.free_classes.length > 0) {
            const freeRooms = data.free_classes.map(cls => cls.room).join(", ");
            populateAvailableRooms(freeRooms);
            // Add fade-in animation
            const observer = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animate-on-scroll');
                        observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.1 });

            document.querySelectorAll('.free-class').forEach(card => {
                requestAnimationFrame(() => {
                    observer.observe(card);
                });
            });
        } else {
            responseElm.innerText = "No free rooms found for the selected time.";
        }
    } else {
        responseElm.innerText = `Error: ${data.message || "Unknown error"}`;
    }
});