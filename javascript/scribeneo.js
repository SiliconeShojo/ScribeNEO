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
    const textarea = gradioApp().querySelector(`#${id} textarea`);
    if (textarea && textarea.value) {
        navigator.clipboard.writeText(textarea.value);
    }
}

onUiLoaded(() => {
    // Enhancer Listeners
    const send_txt = gradioApp().getElementById('scribeneo_send_txt2img');
    const send_img = gradioApp().getElementById('scribeneo_send_img2img');
    
    if (send_txt) send_txt.onclick = () => handle_send_to_tab('scribeneo_main_result', 'txt2img');
    if (send_img) send_img.onclick = () => handle_send_to_tab('scribeneo_main_result', 'img2img');

    // Utility - Copy
    const copy_enhance = gradioApp().getElementById('scribeneo_copy_enhance');
    if (copy_enhance) copy_enhance.onclick = () => scribeneo_copy_to_clipboard('scribeneo_main_result');

    // Vision Listeners
    const vision_send_txt = gradioApp().getElementById('scribeneo_vision_send_txt2img');
    const vision_send_img = gradioApp().getElementById('scribeneo_vision_img2img');
    
    if (vision_send_txt) vision_send_txt.onclick = () => handle_send_to_tab('scribeneo_vision_result', 'txt2img');
    if (vision_send_img) vision_send_img.onclick = () => handle_send_to_tab('scribeneo_vision_result', 'img2img');

    // Utility - Copy Vision
    const copy_vision = gradioApp().getElementById('scribeneo_copy_vision');
    if (copy_vision) copy_vision.onclick = () => scribeneo_copy_to_clipboard('scribeneo_vision_result');

    // Animation / Feedback
    const enhance_btn = gradioApp().getElementById('scribeneo_main_enhance_btn');
    const enhance_result = gradioApp().getElementById('scribeneo_main_result');
    if (enhance_btn && enhance_result) {
        enhance_btn.addEventListener('click', () => {
            enhance_btn.classList.add('scribeneo-active');
            enhance_result.classList.add('scribeneo-active');
            setTimeout(() => {
                enhance_btn.classList.remove('scribeneo-active');
                enhance_result.classList.remove('scribeneo-active');
            }, 10000);
        });
    }

    const scan_btn = gradioApp().getElementById('scribeneo_decode_btn');
    const scan_result = gradioApp().getElementById('scribeneo_vision_result');
    if (scan_btn && scan_result) {
        scan_btn.addEventListener('click', () => {
            scan_btn.classList.add('scribeneo-active');
            scan_result.classList.add('scribeneo-active');
            setTimeout(() => {
                scan_btn.classList.remove('scribeneo-active');
                scan_result.classList.remove('scribeneo-active');
            }, 10000);
        });
    }
});
