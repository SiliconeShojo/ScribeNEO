function set_active_prompt_text(text, targetTab) {
    const prefix = targetTab === "txt2img" ? 'txt2img' : 'img2img';
    const textarea = gradioApp().querySelector(`#${prefix}_prompt textarea`);
    if (textarea) {
        textarea.value = text;
        updateInput(textarea);
    }
}

function handle_send_to_tab(sourceId, targetTab) {
    const source = gradioApp().querySelector(`#${sourceId} textarea`);
    if (source && source.value) {
        set_active_prompt_text(source.value, targetTab);
        if (targetTab === "txt2img") {
            if (typeof switch_to_txt2img === 'function') switch_to_txt2img();
            else gradioApp().querySelector('#tabs').querySelectorAll('button')[0].click();
        } else {
            if (typeof switch_to_img2img === 'function') switch_to_img2img();
            else gradioApp().querySelector('#tabs').querySelectorAll('button')[1].click();
        }
    }
}

function scribeneo_copy_to_clipboard(id) {
    const selector = `#${id} textarea`;
    const textarea = gradioApp().querySelector(selector);
    if (textarea && textarea.value) {
        navigator.clipboard.writeText(textarea.value).then(() => {
            // Visual feedback could be added here
        });
    }
}

function watchForCompletion(resultId) {
    const container = gradioApp().getElementById(resultId);
    if (!container) return;

    let lastValue = '';
    let unchangedPolls = 0;
    let hasReceivedContent = false;

    const interval = setInterval(() => {
        const textarea = container.querySelector('textarea');
        if (!textarea) return;

        const val = textarea.value || '';

        if (val !== lastValue) {
            lastValue = val;
            unchangedPolls = 0;
            if (val && !val.startsWith('Thinking...')) {
                hasReceivedContent = true;
            }
        } else if (hasReceivedContent) {
            unchangedPolls++;
            if (unchangedPolls >= 3) {
                container.classList.remove('scribeneo-active');
                clearInterval(interval);
            }
        }
    }, 400);

    // Safety fallback — 2 minutes max for vision tasks
    setTimeout(() => {
        container.classList.remove('scribeneo-active');
        clearInterval(interval);
    }, 120000);
}

function attach_scribeneo_listeners() {
    // Enhancer
    const send_txt = gradioApp().getElementById('scribeneo_send_txt2img');
    const send_img = gradioApp().getElementById('scribeneo_send_img2img');
    const copy_enhance = gradioApp().getElementById('scribeneo_copy_enhance');

    if (send_txt) send_txt.onclick = () => handle_send_to_tab('scribeneo_main_result', 'txt2img');
    if (send_img) send_img.onclick = () => handle_send_to_tab('scribeneo_main_result', 'img2img');
    if (copy_enhance) copy_enhance.onclick = () => scribeneo_copy_to_clipboard('scribeneo_main_result');

    // Vision
    const vision_send_txt = gradioApp().getElementById('scribeneo_vision_send_txt2img');
    const vision_send_img = gradioApp().getElementById('scribeneo_vision_img2img');
    const copy_vision = gradioApp().getElementById('scribeneo_copy_vision');

    if (vision_send_txt) vision_send_txt.onclick = () => handle_send_to_tab('scribeneo_vision_result', 'txt2img');
    if (vision_send_img) vision_send_img.onclick = () => handle_send_to_tab('scribeneo_vision_result', 'img2img');
    if (copy_vision) copy_vision.onclick = () => scribeneo_copy_to_clipboard('scribeneo_vision_result');

    // Enhancement Animation — smart content watcher instead of fixed timeout
    const enhance_btn = gradioApp().getElementById('scribeneo_main_enhance_btn');
    const enhance_result = gradioApp().getElementById('scribeneo_main_result');
    if (enhance_btn && enhance_result && !enhance_btn.has_listener) {
        enhance_btn.addEventListener('click', () => {
            enhance_result.classList.add('scribeneo-active');
            watchForCompletion('scribeneo_main_result');
        });
        enhance_btn.has_listener = true;
    }

    const scan_btn = gradioApp().getElementById('scribeneo_decode_btn');
    const scan_result = gradioApp().getElementById('scribeneo_vision_result');
    if (scan_btn && scan_result && !scan_btn.has_listener) {
        scan_btn.addEventListener('click', () => {
            scan_result.classList.add('scribeneo-active');
            watchForCompletion('scribeneo_vision_result');
        });
        scan_btn.has_listener = true;
    }
}

// Watch for tab changes to ensure listeners remain attached in dynamic Gradio env
onUiTabChange(() => {
    attach_scribeneo_listeners();
});

// Initial load
onUiLoaded(() => {
    attach_scribeneo_listeners();
});
