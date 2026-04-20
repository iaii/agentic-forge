const scenarios = {
    roast: {
        title: "Startup Roaster",
        endpoint: "/api/roast",
        inputs: [
            { id: "input", label: "Your Startup Idea", placeholder: "e.g., Tinder but for houseplants" }
        ]
    },
    zombie: {
        title: "Zombie Survival",
        endpoint: "/api/zombie",
        inputs: [
            { id: "location", label: "Current Location", placeholder: "e.g., Target department store" },
            { id: "items", label: "Items in Pockets", placeholder: "e.g., Car keys, half a roll of duct tape" }
        ]
    },
    excuse: {
        title: "Excuse Generator",
        endpoint: "/api/excuse",
        inputs: [
            { id: "input", label: "Event to Avoid", placeholder: "e.g., My cousin's baby shower" }
        ]
    },
    rpg: {
        title: "RPG Backstory Forge",
        endpoint: "/api/rpg",
        inputs: [
            { id: "input", label: "Character Concept", placeholder: "e.g., A Halfling Barbarian who is afraid of blood" }
        ]
    },
    time: {
        title: "Time Travel",
        endpoint: "/api/time",
        inputs: [
            { id: "change", label: "Historical Disruption", placeholder: "e.g., Someone gave Napoleon a smartphone at Waterloo" }
        ]
    },
    murder: {
        title: "Unsolved Murder Mystery",
        endpoint: "/api/murder",
        inputs: [
            { id: "scene", label: "Bizarre Crime Scene", placeholder: "e.g., A melted clock, feather boa, and a halfeaten hotdog" },
            { id: "suspects", label: "Suspects", placeholder: "e.g., The Mayor, Trapeze Artist, stray dog" }
        ]
    },
    teach: {
        title: "AI Masterclass",
        endpoint: "/api/teach",
        inputs: [
            { id: "topic", label: "Topic to Learn", placeholder: "e.g., Quantum physics, The Roman Empire, How a V8 engine works" },
            { 
                id: "mode", 
                label: "Teaching Style", 
                type: "select", 
                options: [
                    {value: "escalator", label: "Levels of Complexity (ELI5 to PhD)"},
                    {value: "socratic", label: "The Socratic Classroom (Debate/Q&A)"},
                    {value: "panel", label: "The Multidisciplinary Panel"}
                ]
            }
        ]
    },
    sysdesign: {
        title: "System Design",
        endpoint: "/api/sysdesign",
        inputs: [
            { id: "input", label: "Wild App Concept", placeholder: "e.g., Tinder but for ghosts" }
        ]
    },
    component: {
        title: "Micro-Component Forge",
        endpoint: "/api/component",
        inputs: [
            { id: "input", label: "UI Element Request", placeholder: "e.g., A glossy red subscribe button" }
        ]
    },
    fitness: {
        title: "Fitness Planner",
        endpoint: "/api/fitness",
        inputs: [
            { id: "input", label: "Your Fitness Goal", placeholder: "e.g., Lose 10kg in 3 months, vegetarian, gym 3x/week" }
        ]
    }
};

let currentScenario = null;
let eventSource = null;
let agentIndexMap = {}; // Maps agent name to a color index

// DOM Elements
const hubView = document.getElementById('hub-view');
const scenarioView = document.getElementById('scenario-view');
const scenarioCards = document.querySelectorAll('.scenario-card');
const backBtn = document.getElementById('back-btn');
const titleEl = document.getElementById('scenario-title');
const dynamicInputs = document.getElementById('dynamic-inputs');
const scenarioForm = document.getElementById('scenario-form');
const chatContainer = document.getElementById('chat-container');
const runBtn = document.getElementById('run-btn');
const randomizeBtn = document.getElementById('randomize-btn');
const spinner = document.getElementById('spinner');
const typingIndicator = document.getElementById('typing-indicator');
const activeAgentName = document.getElementById('active-agent');

// Navigation
scenarioCards.forEach(card => {
    card.addEventListener('click', () => {
        const type = card.dataset.scenario;
        openScenario(type);
    });
});

backBtn.addEventListener('click', () => {
    // Stop any running SSE if we go back
    if (eventSource) {
        eventSource.close();
    }
    scenarioView.classList.remove('active');
    setTimeout(() => {
        hubView.classList.add('active');
    }, 400); // Wait for transition
});

function openScenario(type) {
    currentScenario = scenarios[type];
    titleEl.textContent = currentScenario.title;
    
    // Build inputs
    dynamicInputs.innerHTML = '';
    currentScenario.inputs.forEach(input => {
        const group = document.createElement('div');
        group.className = 'input-group';
        
        let inputHtml = "";
        if (input.type === "select") {
            const options = input.options.map(opt => `<option value="${opt.value}">${opt.label}</option>`).join('');
            inputHtml = `<select id="${input.id}" name="${input.id}" required>${options}</select>`;
        } else {
            inputHtml = `<input type="text" id="${input.id}" name="${input.id}" placeholder="${input.placeholder}" required autocomplete="off">`;
        }
        
        group.innerHTML = `
            <label for="${input.id}">${input.label}</label>
            ${inputHtml}
        `;
        dynamicInputs.appendChild(group);
    });

    // Reset Chat
    chatContainer.innerHTML = '<div class="empty-state">Agents are standing by...</div>';
    agentIndexMap = {};
    typingIndicator.classList.remove('active');

    hubView.classList.remove('active');
    setTimeout(() => {
        scenarioView.classList.add('active');
    }, 400);
}

randomizeBtn.addEventListener('click', async () => {
    if (!currentScenario) return;
    const scenarioKey = Object.keys(scenarios).find(k => scenarios[k] === currentScenario);
    
    randomizeBtn.disabled = true;
    randomizeBtn.textContent = '🎲 Thinking...';
    try {
        const res = await fetch(`/api/randomize?scenario=${scenarioKey}`);
        const data = await res.json();
        for (let key in data) {
            const el = document.getElementById(key);
            if (el && el.tagName !== 'SELECT') {
                el.value = data[key];
            }
        }
    } catch (e) {
        console.error("Failed to randomize", e);
    } finally {
        randomizeBtn.disabled = false;
        randomizeBtn.textContent = '🎲 Random Idea';
    }
});

// Form Submission & SSE Handling
scenarioForm.addEventListener('submit', (e) => {
    e.preventDefault();
    if (eventSource) eventSource.close();
    
    // Clear chat
    chatContainer.innerHTML = '';
    agentIndexMap = {};
    
    // Build query params
    const formData = new FormData(scenarioForm);
    const params = new URLSearchParams();
    for (let [key, value] of formData.entries()) {
        params.append(key, value);
    }
    
    // UI State
    runBtn.disabled = true;
    spinner.style.display = 'block';
    
    // Fake the typing indicator for the first agent
    typingIndicator.classList.add('active');
    activeAgentName.textContent = "Agent";

    const url = `${currentScenario.endpoint}?${params.toString()}`;
    
    eventSource = new EventSource(url);
    
        eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        
        // Check for termination sentinel
        if (data === null) {
            eventSource.close();
            runBtn.disabled = false;
            spinner.style.display = 'none';
            typingIndicator.classList.remove('active');
            scrollToBottom();
            return;
        }

        if (data.type === "ping") {
            // It's just a heartbeat to prevent timeout, update indicator text
            activeAgentName.textContent = "Agent is deep in thought";
            return;
        }

        // Must be a task completion
        renderMessage(data.agent, data.text);
    };

    eventSource.onerror = function(err) {
        console.error("EventSource failed:", err);
        eventSource.close();
        runBtn.disabled = false;
        spinner.style.display = 'none';
        typingIndicator.classList.remove('active');
        
        // Only show error if the connection failed outright, sometimes it errors on natural close.
        renderMessage("System (Error)", "Connection lost or server error. Make sure LM Studio is running on localhost:1234.");
    };
});

function getAgentIndex(name) {
    if (name.includes("System") || name.includes("Error")) return "system";
    if (!(name in agentIndexMap)) {
        // Assign 0, 1, or 2 based on object keys mapping length modulo 3
        const count = Object.keys(agentIndexMap).length;
        agentIndexMap[name] = count % 3;
    }
    return agentIndexMap[name];
}

function renderMessage(agentName, text) {
    const isSystem = agentName.includes("System") || agentName.includes("Error");
    
    if (!isSystem) {
        activeAgentName.textContent = "Next Agent";
    }

    const colorIndex = getAgentIndex(agentName);
    
    const msgDiv = document.createElement('div');
    msgDiv.className = 'chat-msg';
    msgDiv.setAttribute('data-index', colorIndex);
    
    // Default to collapsed for non-system intermediate agents
    if (!isSystem) {
        msgDiv.classList.add('collapsed');
    }
    
    // Format text nicely (simple markdown logic for bold)
    let formattedText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    const scenarioKeyForFormat = Object.keys(scenarios).find(k => scenarios[k] === currentScenario);
    if (scenarioKeyForFormat === "fitness" && isSystem) {
        formattedText = formattedText
            .replace(/^### (.+)$/gm, '<h4 style="margin:14px 0 6px; color:var(--accent);">$1</h4>')
            .replace(/^## (.+)$/gm, '<h3 style="margin:18px 0 8px; color:var(--accent); border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:4px;">$1</h3>')
            .replace(/^# (.+)$/gm, '<h2 style="margin:20px 0 10px; color:var(--accent);">$1</h2>')
            .replace(/^- (.+)$/gm, '<li style="margin:4px 0; padding-left:4px;">$1</li>')
            .replace(/^(\d+)\. (.+)$/gm, '<li style="margin:4px 0; padding-left:4px;"><strong>$1.</strong> $2</li>')
            .replace(/(<li[\s\S]*?<\/li>)/g, '<ul style="padding-left:20px; margin:6px 0;">$1</ul>')
            .replace(/\n\n/g, '<br/>');
    }
    
    const toggleIconHTML = isSystem ? '' : '<span class="toggle-icon">▼</span>';
    const headerClass = isSystem ? 'msg-header' : 'msg-header collapsible';

    msgDiv.innerHTML = `
        <div class="${headerClass}">
            <span class="agent-badge">${agentName}</span>
            ${toggleIconHTML}
        </div>
        <div class="msg-content">${formattedText}</div>
    `;
    
    if (!isSystem) {
        const headerEl = msgDiv.querySelector('.msg-header');
        headerEl.addEventListener('click', () => {
            msgDiv.classList.toggle('collapsed');
        });
    }
    
    const scenarioKey = Object.keys(scenarios).find(k => scenarios[k] === currentScenario);
    if (scenarioKey === "component" && isSystem && text.includes("```html")) {
        const match = text.match(/```html\n([\s\S]*?)```/);
        if (match && match[1]) {
            const renderBox = document.createElement('div');
            renderBox.style.marginTop = "15px";
            renderBox.style.padding = "20px";
            renderBox.style.background = "rgba(0,0,0,0.5)";
            renderBox.style.borderRadius = "8px";
            renderBox.style.border = "1px solid rgba(255,255,255,0.1)";
            
            const shadow = renderBox.attachShadow({mode: 'open'});
            shadow.innerHTML = match[1];
            
            // Append header
            const header = document.createElement('div');
            header.innerHTML = '<strong style="font-size:0.8rem; text-transform:uppercase; color:var(--accent);">Live Preview</strong><hr style="border-color:rgba(255,255,255,0.1); margin-bottom:15px;"/>';
            msgDiv.appendChild(header);
            msgDiv.appendChild(renderBox);
        }
    }
    
    // Smart Scrolling Logic
    // Check if user is currently near the bottom (within 100px)
    const isScrolledToBottom = chatContainer.scrollHeight - chatContainer.clientHeight <= chatContainer.scrollTop + 100;
    
    chatContainer.appendChild(msgDiv);
    
    // Only force scroll down if they were already at the bottom, OR if it's the final system message
    if (isScrolledToBottom || isSystem) {
        scrollToBottom();
    }
}

function scrollToBottom() {
    chatContainer.scrollTo({
        top: chatContainer.scrollHeight,
        behavior: 'smooth'
    });
}
