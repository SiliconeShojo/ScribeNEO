"""
Main UI Entry Point for ScribeNEO.
Defines the Gradio interface, component layout, and event orchestration
for the Forge Neo extension.
"""
import os
import sys
import json
import gradio as gr

# Add the extension root directory to sys.path to allow direct imports
scripts_dir = os.path.dirname(os.path.abspath(__file__))
ext_root = os.path.dirname(scripts_dir)
if ext_root not in sys.path:
    sys.path.insert(0, ext_root)

from modules import scripts, script_callbacks, shared

from llm_service import llm_service
from tagging_service import tagging_service

# Path to data files
from config_service import load_config, save_config
base_dir = scripts.basedir()
personas_path = os.path.join(base_dir, "personas.json")


def load_personas():
    if os.path.exists(personas_path):
        try:
            with open(personas_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ScribeNEO] Error loading personas: {e}")
            return []
    return []

def save_personas(personas):
    try:
        with open(personas_path, 'w', encoding='utf-8') as f:
            json.dump(personas, f, indent=4)
    except Exception as e:
        print(f"[ScribeNEO] Error saving personas: {e}")

# --- UI COMPONENT BUILDERS ---

def build_enhancer_module(persona_names, last_enhancer, last_persona="None"):
    with gr.Column(scale=1, elem_classes="scribeneo-module"):
        gr.Markdown("### ✨ PROMPT ENHANCER")
        
        with gr.Row(elem_classes="scribeneo-engine-row"):
            enhancer_model = gr.Dropdown(choices=[last_enhancer] if last_enhancer else [], value=last_enhancer, label="AI Engine", scale=3, allow_custom_value=True, elem_id="scribeneo_enhancer_model")
            refresh_enhancer = gr.Button("🔄", elem_classes="scribeneo-refresh-btn", scale=0)
            enhancer_persona = gr.Dropdown(choices=persona_names, value=last_persona, label="Active Persona", scale=2, elem_id="scribeneo_enhancer_persona")
        
        raw_input = gr.Textbox(label="Initial Prompt", lines=5, placeholder="Type keywords or a simple idea...", elem_id="scribeneo_main_input")
        with gr.Row(elem_classes="scribeneo-action-bar"):
            enhance_btn = gr.Button("ENHANCE PROMPT", variant="primary", elem_id="scribeneo_main_enhance_btn", scale=3)
            stop_enhance_btn = gr.Button("⏹️", elem_id="scribeneo_stop_enhance", scale=1)
            copy_enhance_btn = gr.Button("📋", elem_id="scribeneo_copy_enhance", scale=1)
            clear_enhance_btn = gr.Button("🗑️", elem_id="scribeneo_clear_enhance", scale=1)
        
        enhanced_output = gr.Textbox(label="Enhanced Result", lines=8, show_copy_button=False, elem_id="scribeneo_main_result")
        
        with gr.Row(elem_classes="scribeneo-action-row"):
            send_txt2img = gr.Button("📤 Send to txt2img", elem_id="scribeneo_send_txt2img")
            send_img2img = gr.Button("🖼️ Send to img2img", elem_id="scribeneo_send_img2img")
        
        with gr.Group(elem_classes="scribeneo-tip-card"):
            gr.Markdown("""
### 📖 DASHBOARD LEGEND
*   **⏹️ Stop**: Instantly cancels long-running AI requests.
*   **Refresh (🔄)**: Synchronizes with the backend for models.
*   **Enhance / Scan**: Processes input through AI and persona.
*   **Send To (📤)**: Transfers result to txt2img or img2img.
*   **Append (➕)**: Merges scanned metadata into current intent.
""")
    return enhancer_model, refresh_enhancer, enhancer_persona, raw_input, enhance_btn, stop_enhance_btn, copy_enhance_btn, clear_enhance_btn, enhanced_output, send_txt2img, send_img2img

def build_vision_module(persona_names, last_vision, last_persona="None"):
    with gr.Column(scale=1, elem_classes="scribeneo-module"):
        gr.Markdown("### 👁️ VISION TOOLSET")
        
        with gr.Row(elem_classes="scribeneo-engine-row"):
            caption_model = gr.Dropdown(choices=[last_vision] if last_vision else [], value=last_vision, label="Vision Engine", scale=3, allow_custom_value=True, elem_id="scribeneo_vision_model")
            refresh_vision = gr.Button("🔄", elem_classes="scribeneo-refresh-btn", scale=0)
            caption_persona = gr.Dropdown(choices=persona_names, value=last_persona, label="Vision Persona", scale=2, elem_id="scribeneo_vision_persona")
        
        img_input = gr.Image(label="Source Image", type="pil", elem_classes="scribeneo-image-container")
        with gr.Row(elem_classes="scribeneo-action-bar"):
            tag_btn = gr.Button("SCAN IMAGE", variant="primary", elem_id="scribeneo_decode_btn", scale=3)
            stop_vision_btn = gr.Button("⏹️", elem_id="scribeneo_stop_vision", scale=1)
            copy_vision_btn = gr.Button("📋", elem_id="scribeneo_copy_vision", scale=1)
            clear_vision_btn = gr.Button("🗑️", elem_id="scribeneo_clear_vision", scale=1)
        
        tag_output = gr.Textbox(label="Image Analysis Result", lines=8, show_copy_button=False, elem_id="scribeneo_vision_result")
        
        with gr.Row(elem_classes="scribeneo-action-row"):
            vis_to_txt2img = gr.Button("📤 Send to txt2img", elem_id="scribeneo_vision_send_txt2img")
            vis_to_img2img = gr.Button("🖼️ Send to img2img", elem_id="scribeneo_vision_img2img")
        
        with gr.Row(elem_classes="scribeneo-action-row"):
            append_btn = gr.Button("➕ Append to Prompt")
            replace_btn = gr.Button("🔄 Replace Prompt")
            
    return caption_model, refresh_vision, caption_persona, img_input, tag_btn, stop_vision_btn, copy_vision_btn, clear_vision_btn, tag_output, vis_to_txt2img, vis_to_img2img, append_btn, replace_btn

def build_config_hub(provider, init_key, init_end):
    with gr.Accordion("🛠️ SCRIBE HUB: Configuration", open=False):
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("#### ⚙️ Service Settings")
                provider_input = gr.Dropdown(choices=["OpenRouter", "Hugging Face", "Ollama"], value=provider, label="Active Service Provider", elem_id="scribeneo_provider_input")
                
                with gr.Row(elem_classes="scribeneo-config-row"):
                    api_key_input = gr.Textbox(label="API Key / Token", value=init_key, type="password", scale=4)
                    reveal_api_btn = gr.Button("👁️", elem_id="scribeneo_reveal_api", scale=1)
                
                with gr.Row(elem_classes="scribeneo-config-row"):
                    endpoint_input = gr.Textbox(label="Endpoint URL", value=init_end, scale=4, interactive=False)
                    edit_endpoint_btn = gr.Button("✏️", elem_id="scribeneo_edit_endpoint", scale=1)
                
                with gr.Row():
                    test_conn_btn = gr.Button("🔌 Test Connection", variant="secondary")
                    save_global_btn = gr.Button("💾 Save Configuration", variant="primary")

            with gr.Column(scale=1, elem_id="scribeneo_hub_filler"):
                gr.Markdown("""
### ⚙️ SERVICE REFERENCE
*   **Service Provider**: Cloud engines or local infrastructure.
*   **API Key / Token**: Secure input for authentication credentials.
*   **Endpoint URL**: The target server address.
*   **Test Connection**: Real-time authentication handshake.
*   **Save Configuration**: Persist settings to local config.json.
""", elem_classes="scribeneo-handbook")
    return provider_input, api_key_input, reveal_api_btn, endpoint_input, edit_endpoint_btn, test_conn_btn, save_global_btn

def build_persona_lab(persona_names):
    with gr.Accordion("🎭 PERSONA LAB: Custom AI Personalities", open=False):
        gr.Markdown("Configure neural personas to guide the enhancement process.")
        with gr.Row(elem_classes="scribeneo-engine-row"):
            p_select = gr.Dropdown(choices=persona_names[1:], label="Select to Edit", scale=1)
            p_refresh = gr.Button("🔄", elem_classes="scribeneo-refresh-btn", scale=0)
        
        with gr.Group():
            p_name = gr.Textbox(label="Name", placeholder="e.g. Cinematic Photographer")
            p_desc = gr.Textbox(label="Description", placeholder="A short blurb about this identity")
            p_prompt = gr.Textbox(label="System Prompt", lines=6, placeholder="Define the AI's behavior and style...")
        
        with gr.Row():
            p_save = gr.Button("💾 Save Persona", variant="primary")
            p_delete = gr.Button("🗑️ Delete", variant="stop")
            p_new = gr.Button("✨ New Persona")
            
    return p_select, p_refresh, p_name, p_desc, p_prompt, p_save, p_delete, p_new

def on_ui_tabs():
    # Initial state
    personas = load_personas()
    persona_names = ["None"] + [p['name'] for p in personas]
    
    conf = load_config()
    provider = "OpenRouter"
    
    # Determine initial key/endpoint based on provider
    init_key = ""
    init_end = ""
    if provider == "OpenRouter":
        init_key = conf["openrouter"]["key"]
        init_end = conf["openrouter"]["endpoint"]
    elif provider == "Hugging Face":
        init_key = conf["huggingface"]["key"]
        init_end = conf["huggingface"]["endpoint"]
    elif provider == "Ollama":
        init_end = conf["ollama"]["endpoint"]

 
    with gr.Blocks(analytics_enabled=False, elem_id="scribe_neo_container") as scribeneo_tab:
        # --- MAIN WORKSPACE ---
        with gr.Row():
            (enhancer_model, refresh_enhancer, enhancer_persona, raw_input, enhance_btn, 
             stop_enhance_btn, copy_enhance_btn, clear_enhance_btn, enhanced_output, 
             send_txt2img, send_img2img) = build_enhancer_module(persona_names, "", "None")

            (caption_model, refresh_vision, caption_persona, img_input, tag_btn, 
             stop_vision_btn, copy_vision_btn, clear_vision_btn, tag_output, 
             vis_to_txt2img, vis_to_img2img, append_btn, replace_btn) = build_vision_module(persona_names, "", "None")

        # --- CONFIGURATION HUB ---
        (provider_input, api_key_input, reveal_api_btn, endpoint_input, 
         edit_endpoint_btn, test_conn_btn, save_global_btn) = build_config_hub(provider, init_key, init_end)

        # --- PERSONA LAB ---
        (p_select, p_refresh, p_name, p_desc, p_prompt, 
         p_save, p_delete, p_new) = build_persona_lab(persona_names)

        # --- EVENT HANDLERS ---
        
        reveal_state = gr.State("password")
        def toggle_reveal(current):
            new_type = "text" if current == "password" else "password"
            icon = "🙈" if new_type == "text" else "👁️"
            return new_type, gr.update(type=new_type), gr.update(value=icon)
        
        reveal_api_btn.click(fn=toggle_reveal, inputs=[reveal_state], outputs=[reveal_state, api_key_input, reveal_api_btn])

        provider_switched = [False]

        def update_hub_fields(provider):
            conf = load_config()
            key_val = ""
            end_val = ""
            if provider == "OpenRouter":
                key_val = conf["openrouter"]["key"]
                end_val = conf["openrouter"]["endpoint"]
            elif provider == "Hugging Face":
                key_val = conf["huggingface"]["key"]
                end_val = conf["huggingface"]["endpoint"]
            elif provider == "Ollama":
                key_val = ""
                end_val = conf["ollama"]["endpoint"]
            
            if provider_switched[0]:
                gr.Info(f"Switched to {provider}. Hit 🔄 to refresh your model lists.")
            provider_switched[0] = True

            return gr.update(value=key_val), gr.update(value=end_val, interactive=False)

        provider_input.change(fn=update_hub_fields, inputs=[provider_input], outputs=[api_key_input, endpoint_input])

        def toggle_edit_endpoint(current_interactive):
            new_state = not current_interactive
            icon = "✅" if new_state else "✏️"
            return gr.update(interactive=new_state), gr.update(value=icon), new_state
        
        endpoint_interactive_state = gr.State(False)
        edit_endpoint_btn.click(
            fn=toggle_edit_endpoint, 
            inputs=[endpoint_interactive_state], 
            outputs=[endpoint_input, edit_endpoint_btn, endpoint_interactive_state]
        )

        def run_test_connection(provider, api_key, endpoint):
            success, msg = llm_service.test_connection(provider, api_key, endpoint)
            if success: gr.Info(msg)
            else: gr.Warning(msg)
            return msg

        test_conn_btn.click(fn=run_test_connection, inputs=[provider_input, api_key_input, endpoint_input])

        def run_sync_models(provider, api_key, endpoint, is_vision=False):
            models = llm_service.fetch_available_models(provider, api_key, endpoint, is_vision=is_vision)
            if not models:
                gr.Warning(f"Failed to fetch {('Vision' if is_vision else 'Text')} models for {provider}.")
                return gr.update()
            
            gr.Info(f"Synced {len(models)} {('Vision' if is_vision else 'Text')} models.")
            return gr.update(choices=models)

        # Inline refresh buttons
        refresh_enhancer.click(fn=run_sync_models, inputs=[provider_input, api_key_input, endpoint_input, gr.State(False)], outputs=[enhancer_model])
        refresh_vision.click(fn=run_sync_models, inputs=[provider_input, api_key_input, endpoint_input, gr.State(True)], outputs=[caption_model])

        def run_save_global(provider, key, endpoint):
            conf = load_config()
            if provider == "OpenRouter":
                conf["openrouter"]["key"] = key
                conf["openrouter"]["endpoint"] = endpoint
            elif provider == "Hugging Face":
                conf["huggingface"]["key"] = key
                conf["huggingface"]["endpoint"] = endpoint
            elif provider == "Ollama":
                conf["ollama"]["endpoint"] = endpoint
            
            save_config(conf)
            gr.Info(f"Local config for {provider} saved.")
            return gr.update(interactive=False), gr.update(value="✏️"), False

        save_global_btn.click(fn=run_save_global, inputs=[provider_input, api_key_input, endpoint_input], outputs=[endpoint_input, edit_endpoint_btn, endpoint_interactive_state])

        # Persona Lab Helpers
        def update_p_fields(name):
            ps = load_personas()
            p = next((x for x in ps if x['name'] == name), None)
            if p: return p['name'], p['description'], p['system_prompt']
            return "", "", ""

        p_select.change(fn=update_p_fields, inputs=[p_select], outputs=[p_name, p_desc, p_prompt])

        def run_save_p(name, desc, prompt, original):
            ps = load_personas()
            new_p = {"name": name, "description": desc, "system_prompt": prompt}
            found = False
            for i, p in enumerate(ps):
                if p['name'] == original:
                    ps[i] = new_p
                    found = True
                    break
            if not found: ps.append(new_p)
            save_personas(ps)
            names_with_none = ["None"] + [x['name'] for x in ps]
            gr.Info(f"Persona '{name}' saved.")
            return gr.update(choices=names_with_none[1:]), gr.update(choices=names_with_none), gr.update(choices=names_with_none)

        def run_delete_p(name):
            if not name: return gr.update(), gr.update(), gr.update()
            ps = load_personas()
            ps = [p for p in ps if p['name'] != name]
            save_personas(ps)
            choices_list = [x['name'] for x in ps]
            all_names = ["None"] + choices_list
            gr.Info(f"Persona '{name}' deleted.")
            return gr.update(choices=choices_list, value=None), gr.update(choices=all_names), gr.update(choices=all_names)

        p_save.click(fn=run_save_p, inputs=[p_name, p_desc, p_prompt, p_select], outputs=[p_select, enhancer_persona, caption_persona])
        p_delete.click(fn=run_delete_p, inputs=[p_select], outputs=[p_select, enhancer_persona, caption_persona])
        p_new.click(fn=lambda: ("", "", "", None), outputs=[p_name, p_desc, p_prompt, p_select])

        # Enhancer & Vision Logic
        def run_enhance(prompt, person_name, model, provider):
            if not prompt: 
                yield "Error: Provide an intent first."
                return
            
            yield "Thinking... [ScribeNEO is formulating your enhanced prompt]"
            
            ps = load_personas()
            p = next((x for x in ps if x['name'] == person_name), None)
            sys_prompt = p['system_prompt'] if p else ""
            
            result = llm_service.enhance_prompt(prompt, sys_prompt, provider=provider.lower().replace(" ",""), model=model)
            yield result

        enhance_event = enhance_btn.click(fn=run_enhance, inputs=[raw_input, enhancer_persona, enhancer_model, provider_input], outputs=[enhanced_output])
        stop_enhance_btn.click(fn=None, cancels=[enhance_event])
        clear_enhance_btn.click(fn=lambda: "", outputs=[enhanced_output])

        def run_vision(img, person_name, model, provider):
            if not img:
                yield "Error: Upload an image."
                return
            
            yield "Thinking... [ScribeNEO is scanning your visuals]"
            
            ps = load_personas()
            p = next((x for x in ps if x['name'] == person_name), None)
            sys_prompt = p['system_prompt'] if p else None
            
            result = tagging_service.interrogate(img, provider=provider.lower().replace(" ",""), model=model, system_prompt=sys_prompt)
            yield result

        vision_event = tag_btn.click(fn=run_vision, inputs=[img_input, caption_persona, caption_model, provider_input], outputs=[tag_output])
        stop_vision_btn.click(fn=None, cancels=[vision_event])
        clear_vision_btn.click(fn=lambda: "", outputs=[tag_output])


        # Passive handlers to ensure Gradio interactivity for JS-overridden buttons
        for btn in [send_txt2img, send_img2img, copy_enhance_btn, vis_to_txt2img, vis_to_img2img, copy_vision_btn]:
            btn.click(fn=None, _js="() => {}")

        # UI Utilities
        append_btn.click(fn=lambda x, y: f"{x}\n{y}" if x else y, inputs=[raw_input, tag_output], outputs=[raw_input])
        replace_btn.click(fn=lambda x: x, inputs=[tag_output], outputs=[raw_input])

        # Initial UI Sync logic for API Keys only
        scribeneo_tab.load(fn=update_hub_fields, inputs=[provider_input], outputs=[api_key_input, endpoint_input])

    return [(scribeneo_tab, "ScribeNEO", "scribe_neo_tab")]

script_callbacks.on_ui_tabs(on_ui_tabs)
