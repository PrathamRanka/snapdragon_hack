# FormFusion

Jetpack Compose app with a CameraX preview feeding frames through `ImageAnalysis` into a
`PoseAnalyzer`, which converts each frame to an upright `Bitmap` and passes it to a
`PoseDetector`. Navigation is a simple `Screen` enum switched at the top level (no
Navigation-Compose). Today `PoseDetector` is implemented by `StubPoseDetector`, which returns
an empty landmark list — this proves the camera → analysis → UI pipeline works end to end
before any model exists.

**The only place to integrate the real model:** implement `PoseDetector` in a new
`YourModelPoseDetector` class (see `pose/PoseDetector.kt`) and swap `StubPoseDetector` for it
in `CameraScreen.kt`. Nothing else changes. The model runtime dependency (TFLite/LiteRT, ONNX,
or QNN) and the model asset file get added at that time.

## To activate the ML model

The native/QNN scaffold (`PoseNative`, `ChipSelector`, `RtmPoseDetector`, `cpp/CMakeLists.txt`)
is already wired up and safely inert — it just needs the ML team's build artifacts dropped in:

1. Place `libpose.so` and the QNN runtime `.so` files in `app/src/main/jniLibs/arm64-v8a/`.
2. Place the 6 `.bin` model files (`rtmdet_v73.bin`, `rtmpose_v73.bin`, etc.) in
   `app/src/main/assets/`.
3. Swap `StubPoseDetector` for `RtmPoseDetector` in `CameraScreen.kt` (call `initialize()`
   once before using it).

## Architecture: MVVM

Every screen with real logic follows Model / ViewModel / View, so redesigning the UI never
touches business logic:

- **Model** — `network/` (`SessionManager`, `PoseWebSocketServer`, `PoseWebSocketClient`,
  `QrCodeGenerator`) and `pose/` (`PoseDetector`, `StubPoseDetector`, `RtmPoseDetector`,
  `PoseNative`, `ChipSelector`). Pure data + I/O, no Compose imports.
- **ViewModel** — `viewmodel/` (`RoleViewModel`, `HostViewModel`, `JoinLobbyViewModel`,
  `CameraViewModel`). Each exposes a `StateFlow<UiState>` for the screen to render and a
  `Flow` of one-shot events (navigation, errors) for the screen to react to. All parsing,
  session/server/client lifecycle, and counting logic lives here — never in a Composable.
- **View** — `RoleScreen.kt`, `HostScreen.kt`, `JoinLobbyScreen.kt`, `CameraScreen.kt`. Only
  `collectAsState()` the ViewModel's state, render it, and forward click callbacks to
  ViewModel functions. Safe to restyle freely.

`BaseViewModel` (`viewmodel/BaseViewModel.kt`) is a small custom base — **not**
`androidx.lifecycle.ViewModel`. Since this project has no Navigation-Compose backstack
(just the `Screen` enum switch in `MainActivity.kt`), the real `viewModel()` composable
would scope instances to the whole Activity instead of one screen visit. Instead, each
screen creates its ViewModel with `remember { ... }` and clears it via
`DisposableEffect(Unit) { onDispose { viewModel.dispose() } }`, giving fresh state (and a
freshly started/stopped server or client) every time you navigate to that screen — matching
the previous behavior while keeping the logic out of the View.

`HomeScreen` and `MultiPhonePlaceholderScreen` have no ViewModel — they're pure navigation
with no state or logic, so a ViewModel would be empty ceremony.
