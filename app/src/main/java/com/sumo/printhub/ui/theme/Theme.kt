package com.sumo.printhub.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val SumoBg = Color(0xFF1A1A2E)
private val SumoSurface = Color(0xFF22223B)
private val SumoPrimary = Color(0xFFE94560)
private val SumoSecondary = Color(0xFF0F3460)
private val SumoAccent = Color(0xFF16C79A)
private val SumoOnPrimary = Color.White
private val SumoOnBg = Color(0xFFEDEAF6)

private val DarkScheme = darkColorScheme(
    primary = SumoPrimary,
    onPrimary = SumoOnPrimary,
    secondary = SumoSecondary,
    onSecondary = Color.White,
    tertiary = SumoAccent,
    background = SumoBg,
    onBackground = SumoOnBg,
    surface = SumoSurface,
    onSurface = SumoOnBg,
    surfaceVariant = Color(0xFF2A2C4D),
    onSurfaceVariant = Color(0xFFCFCFE0),
    error = Color(0xFFE63946),
)

private val LightScheme = lightColorScheme(
    primary = SumoPrimary,
    secondary = SumoSecondary,
    tertiary = SumoAccent
)

@Composable
fun SumoTheme(useDark: Boolean = isSystemInDarkTheme(), content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = if (useDark) DarkScheme else DarkScheme,
        typography = MaterialTheme.typography,
        content = content
    )
}
