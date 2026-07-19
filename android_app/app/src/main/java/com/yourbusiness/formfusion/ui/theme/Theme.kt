package com.yourbusiness.formfusion.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable

private val DarkColorScheme = darkColorScheme(
    primary = PrimaryButtonColorDark,
    onPrimary = BackgroundDark,
    secondary = TextSecondaryDark,
    background = BackgroundDark,
    surface = SurfaceDark,
    onBackground = TextPrimaryDark,
    onSurface = TextPrimaryDark,
    onSurfaceVariant = TextSecondaryDark,
    outline = BorderColorDark,
    error = Error
)

private val LightColorScheme = lightColorScheme(
    primary = PrimaryButtonColor,
    onPrimary = Surface,
    secondary = TextSecondary,
    background = Background,
    surface = Surface,
    onBackground = TextPrimary,
    onSurface = TextPrimary,
    onSurfaceVariant = TextSecondary,
    outline = BorderColor,
    error = Error
)

/**
 * FormFusion's design system theme: calm/clinical/premium neutral palette (see Color.kt),
 * Inter-equivalent type scale (Type.kt), and soft 14-16dp rounding (Shape.kt).
 *
 * Dynamic (wallpaper-derived) color is intentionally NOT used here, even though it's
 * available on Android 12+ — a health/physiotherapy app should look the same, calm and
 * intentional, regardless of the user's wallpaper, not shift with Material You.
 */
@Composable
fun FormFusionTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        shapes = FormFusionShapes,
        content = content
    )
}
