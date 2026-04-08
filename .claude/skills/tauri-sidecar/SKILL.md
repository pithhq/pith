---
name: tauri-sidecar
description: Tauri + Python sidecar patterns for PITH GUI — IPC communication, sidecar process management, and platform-specific packaging.
globs: "src-tauri/**/*.rs,src/**/*.ts,src/**/*.vue"
---

# Tauri + Python Sidecar (PITH GUI)

## Architecture
```
PITH GUI
├── Frontend: [Svelte | Vue | React] (web UI inside Tauri webview)
├── Tauri core: Rust (window management, OS integration, IPC)
└── Python sidecar: PyInstaller binary (all PITH logic)
    └── Communicates via stdin/stdout JSON-RPC
```

## Sidecar Registration (tauri.conf.json)
```json
{
  "tauri": {
    "bundle": {
      "externalBin": ["binaries/pith"]
    }
  }
}
```

## Rust Sidecar Command
```rust
// src-tauri/src/main.rs
use tauri_plugin_shell::ShellExt;

#[tauri::command]
async fn run_pith_command(
    app: tauri::AppHandle,
    command: String,
    args: Vec<String>,
) -> Result<String, String> {
    let output = app
        .shell()
        .sidecar("pith")
        .map_err(|e| e.to_string())?
        .args([command].iter().chain(args.iter()))
        .output()
        .await
        .map_err(|e| e.to_string())?;
    
    if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).to_string())
    } else {
        Err(String::from_utf8_lossy(&output.stderr).to_string())
    }
}
```

## Frontend IPC Call
```typescript
// src/lib/pith.ts
import { invoke } from '@tauri-apps/api/core'

export async function pithIngest(filePath: string): Promise<IngestResult> {
  const output = await invoke<string>('run_pith_command', {
    command: 'ingest',
    args: [filePath, '--json']  // --json flag for machine-readable output
  })
  return JSON.parse(output) as IngestResult
}

export async function pithQuery(query: string): Promise<QueryResult> {
  const output = await invoke<string>('run_pith_command', {
    command: 'query',
    args: [query, '--json']
  })
  return JSON.parse(output) as QueryResult
}
```

## Python CLI JSON Output Mode
```python
# Every command supports --json flag for Tauri IPC
@app.command()
def ingest(
    path: Annotated[Path, typer.Argument()],
    json_output: Annotated[bool, typer.Option("--json")] = False,
) -> None:
    result = run_ingest(path, config)
    
    if json_output:
        import json
        print(json.dumps(result.model_dump()))
    else:
        console.print(f"[green]✓[/green] Ingested {path.name}")
```

## Platform Packaging (GitHub Actions)
```yaml
# .github/workflows/release.yml
strategy:
  matrix:
    include:
      - platform: ubuntu-22.04
        args: '--target x86_64-unknown-linux-gnu'
      - platform: macos-latest
        args: '--target aarch64-apple-darwin'
      - platform: windows-latest
        args: ''

steps:
  - name: Build Python sidecar
    run: |
      pip install pyinstaller
      pyinstaller build.spec
      
  - name: Build Tauri app
    uses: tauri-apps/tauri-action@v0
    with:
      args: ${{ matrix.args }}
```

## Important PITH-Specific Rules
- Sidecar binary is the PyInstaller-packaged `pith` CLI — same binary as the standalone CLI
- GUI never reimplements logic that the CLI handles — it's a wrapper, not a parallel implementation
- All wiki operations go through the sidecar — never access wiki files directly from frontend
- Privacy level enforcement happens in the Python sidecar — never bypass it at the Rust/frontend level
