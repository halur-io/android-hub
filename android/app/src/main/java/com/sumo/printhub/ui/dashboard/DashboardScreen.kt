package com.sumo.printhub.ui.dashboard

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.sumo.printhub.data.model.PrinterInfo
import com.sumo.printhub.data.repository.PrintHubRepository
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DashboardScreen(vm: DashboardViewModel, onOpenSettings: () -> Unit) {
    val status by vm.status.collectAsStateWithLifecycle()
    val cfg by vm.config.collectAsStateWithLifecycle()
    val log by vm.printLog.collectAsStateWithLifecycle()
    val printedToday by vm.ordersPrintedToday.collectAsStateWithLifecycle()
    val lastError by vm.lastError.collectAsStateWithLifecycle()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("SUMO Print Hub") },
                actions = {
                    IconButton(onClick = { vm.refreshConfig() }) {
                        Icon(Icons.Filled.Refresh, contentDescription = "Refresh config")
                    }
                    IconButton(onClick = onOpenSettings) {
                        Icon(Icons.Filled.Settings, contentDescription = "Settings")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.surface,
                    titleContentColor = MaterialTheme.colorScheme.primary,
                    actionIconContentColor = MaterialTheme.colorScheme.onSurface
                )
            )
        },
        containerColor = MaterialTheme.colorScheme.background
    ) { padding ->
        Column(
            modifier = Modifier.fillMaxSize().padding(padding).padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            StatusRow(status, cfg?.branchName, printedToday)
            cfg?.let { PrinterSummary(it.defaultPrinter, it.stationMap) }
            lastError?.let {
                Text(
                    "Last error: $it",
                    color = MaterialTheme.colorScheme.error,
                    style = MaterialTheme.typography.bodySmall
                )
            }
            Text(
                "Recent prints",
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onBackground
            )
            LazyColumn(
                contentPadding = PaddingValues(vertical = 4.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
                modifier = Modifier.fillMaxSize()
            ) {
                items(log, key = { it.ts.toString() + it.orderId }) { entry ->
                    PrintLogCard(entry)
                }
                if (log.isEmpty()) {
                    item {
                        Text(
                            "No orders printed yet.",
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun StatusRow(
    status: PrintHubRepository.ConnectionStatus,
    branchName: String?,
    printedToday: Int
) {
    val (label, color) = when (status) {
        PrintHubRepository.ConnectionStatus.Online -> "Online (live)" to Color(0xFF16C79A)
        PrintHubRepository.ConnectionStatus.Polling -> "Polling fallback" to Color(0xFFF4A261)
        PrintHubRepository.ConnectionStatus.Connecting -> "Connecting..." to Color(0xFFE9C46A)
        PrintHubRepository.ConnectionStatus.Offline -> "Offline" to Color(0xFFE63946)
        PrintHubRepository.ConnectionStatus.Disconnected -> "Disconnected" to Color(0xFFE63946)
    }
    Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(modifier = Modifier.size(14.dp).background(color, CircleShape))
            Spacer(Modifier.width(12.dp))
            Column(Modifier.weight(1f)) {
                Text(label, color = MaterialTheme.colorScheme.onSurface, style = MaterialTheme.typography.titleMedium)
                if (!branchName.isNullOrBlank()) {
                    Text("Branch: $branchName", color = MaterialTheme.colorScheme.onSurfaceVariant, style = MaterialTheme.typography.bodySmall)
                }
            }
            Column(horizontalAlignment = Alignment.End) {
                Text("$printedToday", color = MaterialTheme.colorScheme.primary, style = MaterialTheme.typography.headlineSmall)
                Text("printed", color = MaterialTheme.colorScheme.onSurfaceVariant, style = MaterialTheme.typography.bodySmall)
            }
        }
    }
}

@Composable
private fun PrinterSummary(default: PrinterInfo?, stations: Map<String, PrinterInfo>) {
    Card(
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Text(
                "Printers",
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onSurface
            )
            if (default != null) {
                Text(
                    "Default: ${default.name} → ${default.ipAddress}:${default.port}",
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            } else {
                Text("No default printer configured", color = MaterialTheme.colorScheme.error)
            }
            for ((station, p) in stations) {
                Text(
                    "$station → ${p.name} (${p.ipAddress})",
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    style = MaterialTheme.typography.bodySmall
                )
            }
        }
    }
}

private val timeFmt = SimpleDateFormat("HH:mm:ss", Locale.US)

@Composable
private fun PrintLogCard(entry: PrintHubRepository.PrintLogEntry) {
    val isOk = entry.outcome == "success"
    val color = when (entry.outcome) {
        "success" -> Color(0xFF16C79A)
        "partial" -> Color(0xFFF4A261)
        else -> Color(0xFFE63946)
    }
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        shape = RoundedCornerShape(10.dp)
    ) {
        Row(modifier = Modifier.padding(12.dp), verticalAlignment = Alignment.CenterVertically) {
            Box(modifier = Modifier.size(12.dp).background(color, CircleShape))
            Spacer(Modifier.width(12.dp))
            Column(Modifier.weight(1f)) {
                Text(
                    "Order ${entry.displayNumber ?: entry.orderNumber}",
                    color = MaterialTheme.colorScheme.onSurface,
                    style = MaterialTheme.typography.titleSmall
                )
                val target = (entry.printersOk + entry.printersFailed.map { "$it (failed)" }).joinToString(", ")
                if (target.isNotBlank()) {
                    Text(target, color = MaterialTheme.colorScheme.onSurfaceVariant, style = MaterialTheme.typography.bodySmall)
                }
                if (!isOk && !entry.error.isNullOrBlank()) {
                    Text(
                        entry.error,
                        color = MaterialTheme.colorScheme.error,
                        style = MaterialTheme.typography.bodySmall
                    )
                }
            }
            Text(timeFmt.format(Date(entry.ts)), color = MaterialTheme.colorScheme.onSurfaceVariant, style = MaterialTheme.typography.bodySmall)
        }
    }
}
