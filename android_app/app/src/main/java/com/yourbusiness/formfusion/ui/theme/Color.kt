package com.yourbusiness.formfusion.ui.theme

import androidx.compose.ui.graphics.Color

// FormFusion design system — calm, clinical, premium. Kept flat/neutral on purpose; most
// UI stays in Background/Surface/Text, with Success/Warning/Error used only for status.

val Background = Color(0xFFF7F7F5) // soft off-white
val Surface = Color(0xFFFFFFFF)
val TextPrimary = Color(0xFF1A1A1A)
val TextSecondary = Color(0xFF6B7280)
val BorderColor = Color(0xFFE6E6E3)
val PrimaryButtonColor = Color(0xFF2C3440) // filled slate

val Success = Color(0xFF5F8D6E)
val Warning = Color(0xFFC9973F)
val Error = Color(0xFFB5533F)

// Dark-mode equivalents. Not specified in the design system (which is light-only) — derived
// to keep the same calm/neutral feel; system UI still respects a dark system theme.
val BackgroundDark = Color(0xFF15161A)
val SurfaceDark = Color(0xFF1E2025)
val TextPrimaryDark = Color(0xFFF2F2F0)
val TextSecondaryDark = Color(0xFF9AA0AC)
val BorderColorDark = Color(0xFF33353B)
val PrimaryButtonColorDark = Color(0xFFC9CDD6)
