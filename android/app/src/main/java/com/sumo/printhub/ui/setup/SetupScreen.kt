package com.sumo.printhub.ui.setup

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle

@Composable
fun SetupScreen(vm: SetupViewModel, onRegistered: () -> Unit) {
    val state by vm.state.collectAsStateWithLifecycle()
    Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
        Column(
            modifier = Modifier.fillMaxSize().padding(24.dp).verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                "SUMO Print Hub",
                style = MaterialTheme.typography.headlineMedium,
                color = MaterialTheme.colorScheme.primary
            )
            Spacer(Modifier.height(8.dp))
            Text(
                "Connect this tablet to your SUMO server",
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.onBackground
            )
            Spacer(Modifier.height(24.dp))

            val fieldMod = Modifier.fillMaxWidth().widthIn(max = 480.dp)

            OutlinedTextField(
                value = state.serverUrl,
                onValueChange = { v -> vm.update { it.copy(serverUrl = v.trim()) } },
                label = { Text("Server URL (https://...)") },
                singleLine = true,
                enabled = !state.submitting,
                modifier = fieldMod
            )
            Spacer(Modifier.height(12.dp))

            OutlinedTextField(
                value = state.apiKey,
                onValueChange = { v -> vm.update { it.copy(apiKey = v.trim()) } },
                label = { Text("API Key") },
                singleLine = true,
                enabled = !state.submitting,
                modifier = fieldMod
            )
            Spacer(Modifier.height(12.dp))

            OutlinedTextField(
                value = state.branchId,
                onValueChange = { v -> vm.update { it.copy(branchId = v.filter { c -> c.isDigit() }) } },
                label = { Text("Branch ID") },
                singleLine = true,
                enabled = !state.submitting,
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                modifier = fieldMod
            )
            Spacer(Modifier.height(12.dp))

            OutlinedTextField(
                value = state.deviceName,
                onValueChange = { v -> vm.update { it.copy(deviceName = v) } },
                label = { Text("Device name (e.g. Kitchen Tablet)") },
                singleLine = true,
                enabled = !state.submitting,
                modifier = fieldMod
            )
            Spacer(Modifier.height(20.dp))

            state.error?.let {
                Text(it, color = MaterialTheme.colorScheme.error)
                Spacer(Modifier.height(12.dp))
            }

            Button(
                onClick = { vm.submit(onRegistered) },
                enabled = !state.submitting,
                modifier = fieldMod
            ) {
                if (state.submitting) {
                    CircularProgressIndicator(
                        strokeWidth = 2.dp,
                        modifier = Modifier.height(20.dp),
                        color = MaterialTheme.colorScheme.onPrimary
                    )
                } else Text("Register Device")
            }
        }
    }
}
