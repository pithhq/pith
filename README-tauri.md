# PITH — Tauri GUI Build

The GUI is a Tauri 2 application with a Python sidecar.
Tauri provides the native window; the Python CLI binary
handles all domain logic.

## Prerequisites

- Rust toolchain (rustup)
- Tauri CLI: `cargo install tauri-cli`
- Python sidecar built via PyInstaller

## Build Steps

1. Build the Python sidecar binary:

   ```
   make build-linux    # or build-mac / build-windows
   ```

2. Copy the binary into the Tauri sidecar path:

   ```
   cp dist/pith src-tauri/binaries/pith
   ```

   On Windows, copy `dist/pith.exe` to `src-tauri/binaries/pith.exe`.

3. Build the Tauri application:

   ```
   cd src-tauri && cargo tauri build
   ```

   Output appears in `src-tauri/target/release/bundle/`.

## Development

Run the dev server with hot reload:

```
cd src-tauri && cargo tauri dev
```

The frontend source lives in `src/` (index.html, main.js, styles.css).
Tauri commands are defined in `src-tauri/src/lib.rs`.

## Architecture

```
src-tauri/
  Cargo.toml          Rust dependencies (Tauri 2 + shell plugin)
  tauri.conf.json      App config, sidecar declaration
  src/
    main.rs            Entry point
    lib.rs             Tauri command stubs
  binaries/            PyInstaller output (not committed)
  icons/               App icons (Phase 5)

src/
  index.html           Frontend shell
  main.js              Tauri API imports (stub)
  styles.css           PITH colour system
```
