package com.yourbusiness.formfusion

import android.widget.Toast
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import com.yourbusiness.formfusion.ui.components.PrimaryButton
import com.yourbusiness.formfusion.ui.components.SecondaryButton
import com.yourbusiness.formfusion.ui.components.SectionHeader
import com.yourbusiness.formfusion.ui.components.TertiaryTextButton
import com.yourbusiness.formfusion.ui.theme.Spacing
import com.yourbusiness.formfusion.viewmodel.RoleEvent
import com.yourbusiness.formfusion.viewmodel.RoleViewModel

// Pure View: no JSON parsing, no SessionManager access — all delegated to RoleViewModel.
@Composable
fun RoleScreen(
    onHost: () -> Unit,
    onJoin: () -> Unit,
    onBack: () -> Unit
) {
    val context = LocalContext.current
    val viewModel = remember { RoleViewModel() }

    DisposableEffect(viewModel) {
        onDispose { viewModel.dispose() }
    }

    LaunchedEffect(viewModel) {
        viewModel.events.collect { event ->
            when (event) {
                RoleEvent.NavigateToJoinLobby -> onJoin()
                is RoleEvent.ShowError -> Toast.makeText(context, event.message, Toast.LENGTH_SHORT).show()
            }
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .padding(Spacing.xl),
        verticalArrangement = Arrangement.Center
    ) {
        SectionHeader(
            title = "Start with Other Phones",
            subtitle = "Host a multi-angle session or join one nearby"
        )

        PrimaryButton(
            text = "Host Session",
            onClick = onHost,
            modifier = Modifier
                .fillMaxWidth()
                .padding(top = Spacing.xxl)
        )

        SecondaryButton(
            text = "Join Session",
            onClick = {
                launchQrScanner(
                    context = context,
                    onResult = viewModel::onQrScanned,
                    onError = viewModel::onScanFailed
                )
            },
            modifier = Modifier
                .fillMaxWidth()
                .padding(top = Spacing.md)
        )

        TertiaryTextButton(text = "Back", onClick = onBack)
    }
}
