use tauri::Manager;

/// Ingest a file into the wiki via the Python sidecar.
/// Returns JSON string. Implementation deferred to Phase 4.
#[tauri::command]
fn ingest_file(path: String) -> String {
    serde_json::json!({
        "status": "not_implemented",
        "command": "ingest",
        "path": path
    })
    .to_string()
}

/// Query the wiki via the Python sidecar.
/// Returns JSON string. Implementation deferred to Phase 4.
#[tauri::command]
fn query_wiki(text: String) -> String {
    serde_json::json!({
        "status": "not_implemented",
        "command": "query",
        "text": text
    })
    .to_string()
}

/// Run lint pass via the Python sidecar.
/// Returns JSON string. Implementation deferred to Phase 4.
#[tauri::command]
fn run_lint() -> String {
    serde_json::json!({
        "status": "not_implemented",
        "command": "lint"
    })
    .to_string()
}

/// Read current pith.config.json via the Python sidecar.
/// Returns JSON string. Implementation deferred to Phase 4.
#[tauri::command]
fn get_config() -> String {
    serde_json::json!({
        "status": "not_implemented",
        "command": "config"
    })
    .to_string()
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![
            ingest_file,
            query_wiki,
            run_lint,
            get_config
        ])
        .run(tauri::generate_context!())
        .expect("failed to run PITH");
}
