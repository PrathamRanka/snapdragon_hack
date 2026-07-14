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
