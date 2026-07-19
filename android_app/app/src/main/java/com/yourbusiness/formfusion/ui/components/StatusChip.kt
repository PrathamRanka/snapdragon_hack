package com.yourbusiness.formfusion.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.yourbusiness.formfusion.ui.theme.Error
import com.yourbusiness.formfusion.ui.theme.Success
import com.yourbusiness.formfusion.ui.theme.TextSecondary
import com.yourbusiness.formfusion.ui.theme.Warning

enum class StatusTone { Neutral, Success, Warning, Error }

/** A small muted pill for session/connection state — never bright, always at-a-glance. */
@Composable
fun StatusChip(text: String, tone: StatusTone = StatusTone.Neutral) {
    val color = when (tone) {
        StatusTone.Neutral -> TextSecondary
        StatusTone.Success -> Success
        StatusTone.Warning -> Warning
        StatusTone.Error -> Error
    }

    Row(
        verticalAlignment = Alignment.CenterVertically,
        modifier = Modifier
            .background(color.copy(alpha = 0.12f), CircleShape)
            .padding(horizontal = 12.dp, vertical = 6.dp)
    ) {
        Box(
            modifier = Modifier
                .size(6.dp)
                .background(color, CircleShape)
        )
        Spacer(modifier = Modifier.width(6.dp))
        Text(
            text = text,
            style = MaterialTheme.typography.labelMedium,
            color = color
        )
    }
}
