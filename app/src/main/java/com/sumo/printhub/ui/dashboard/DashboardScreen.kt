package com.sumo.printhub.ui.dashboard

import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.border
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
import androidx.compose.material.icons.filled.Print
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
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
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.sumo.printhub.data.model.PrinterInfo
import com.sumo.printhub.data.repository.PrintHubRepository
import com.sumo.printhub.data.repository.PrintHubRepository.LiveOrderEntry
import com.sumo.printhub.data.repository.PrintHubRepository.PrintStatus
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DashboardScreen(vm: DashboardViewModel, onOpenSettings: () -> Unit) {
    val status by vm.status.collectAsStateWithLifecycle()
    val cfg by vm.config.collectAsStateWithLifecycle()
    val liveOrders by vm.liveOrders.collectAsStateWithLifecycle()
    val printedToday by vm.ordersPrintedToday.collectAsStateWithLifecycle()
    val lastError by vm.lastError.collectAsStateWithLifecycle()
    val testInProgress by vm.testPrintInProgress.collectAsStateWithLifecycle()
    val testMessage by vm.testPrintMessage.collectAsStateWithLifecycle()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("SUMO Print Hub") },
                actions = {
                    IconButton(onClick = { vm.refreshConfig() }) {
                        Icon(Icons.Filled.Refresh, contentDescription = "Refresh")
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
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(horizontal = 16.dp),
            contentPadding = PaddingValues(vertical = 16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            item { StatusRow(status, cfg?.branchName, printedToday) }
            item {
                cfg?.let { PrinterSummary(it.defaultPrinter, it.stationMap) }
            }
            item {
                TestPrintRow(
                    inProgress = testInProgress,
                    message = testMessage,
                    onTest = { vm.sendTestPrint() },
                    onDismiss = { vm.clearTestPrintMessage() }
                )
            }
            if (!lastError.isNullOrBlank()) {
                item {
                    Text(
                        "Last error: $lastError",
                        color = MaterialTheme.colorScheme.error,
                        style = MaterialTheme.typography.bodySmall
                    )
                }
            }

            item {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text(
                        "Live orders",
                        style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold),
                        color = MaterialTheme.colorScheme.onBackground,
                        modifier = Modifier.weight(1f)
                    )
                    if (liveOrders.any { it.printStatus == PrintStatus.Printing || it.printStatus == PrintStatus.Incoming }) {
                        val transition = rememberInfiniteTransition(label = "spin")
                        val angle by transition.animateFloat(
                            initialValue = 0f, targetValue = 360f,
                            animationSpec = infiniteRepeatable(tween(1000, easing = LinearEasing), RepeatMode.Restart),
                            label = "spin"
                        )
                        Icon(
                            Icons.Filled.Refresh,
                            contentDescription = null,
                            modifier = Modifier.size(16.dp).rotate(angle),
                            tint = MaterialTheme.colorScheme.primary
                        )
                    }
                }
            }

            if (liveOrders.isEmpty()) {
                item {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 32.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            "Waiting for orders…",
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            style = MaterialTheme.typography.bodyMedium
                        )
                    }
                }
            } else {
                items(liveOrders, key = { it.order.id }) { entry ->
                    LiveOrderCard(entry)
                }
            }
        }
    }
}

@Composable
private fun LiveOrderCard(entry: LiveOrderEntry) {
    val (borderColor, bgTint) = when (entry.printStatus) {
        PrintStatus.Incoming -> Color(0xFFE9C46A) to Color(0xFF2B2820)
        PrintStatus.Printing -> Color(0xFF4D9FEC) to Color(0xFF1A2433)
        PrintStatus.Printed  -> Color(0xFF16C79A) to Color(0xFF172420)
        PrintStatus.Partial  -> Color(0xFFF4A261) to Color(0xFF2B2015)
        PrintStatus.Failed   -> Color(0xFFE63946) to Color(0xFF2B1518)
    }

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .border(width = 1.5.dp, color = borderColor, shape = RoundedCornerShape(12.dp)),
        colors = CardDefaults.cardColors(containerColor = bgTint),
        shape = RoundedCornerShape(12.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 0.dp)
    ) {
        Column(modifier = Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {

            Row(verticalAlignment = Alignment.CenterVertically) {
                StatusPill(entry.printStatus)
                Spacer(Modifier.width(10.dp))
                Text(
                    "#${entry.displayNumber}",
                    style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold),
                    color = Color.White
                )
                Spacer(Modifier.width(8.dp))
                TypeChip(entry.typeLabel)
                Spacer(Modifier.weight(1f))
                Text(
                    timeFmt.format(Date(entry.ts)),
                    style = MaterialTheme.typography.bodySmall,
                    color = Color(0xFF8A9BB0)
                )
            }

            if (entry.customerLabel.isNotBlank()) {
                Text(
                    entry.customerLabel,
                    style = MaterialTheme.typography.bodyMedium,
                    color = Color(0xFFCDD5E0)
                )
            }

            if (entry.order.items.isNotEmpty()) {
                HorizontalDivider(color = Color(0xFF2E3A4A), thickness = 0.5.dp)
                entry.order.items.take(5).forEach { item ->
                    Row {
                        Text(
                            "×${item.displayQty}",
                            style = MaterialTheme.typography.bodySmall.copy(fontWeight = FontWeight.Bold),
                            color = Color(0xFF8A9BB0),
                            modifier = Modifier.width(30.dp)
                        )
                        Text(
                            item.displayName,
                            style = MaterialTheme.typography.bodySmall,
                            color = Color(0xFFCDD5E0),
                            modifier = Modifier.weight(1f)
                        )
                    }
                }
                if (entry.order.items.size > 5) {
                    Text(
                        "+${entry.order.items.size - 5} more items",
                        style = MaterialTheme.typography.bodySmall,
                        color = Color(0xFF8A9BB0)
                    )
                }
            }

            if (entry.printStatus == PrintStatus.Printing) {
                HorizontalDivider(color = Color(0xFF2E3A4A), thickness = 0.5.dp)
                Row(verticalAlignment = Alignment.CenterVertically) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(14.dp),
                        strokeWidth = 2.dp,
                        color = Color(0xFF4D9FEC)
                    )
                    Spacer(Modifier.width(8.dp))
                    Text(
                        "Sending to printer…",
                        style = MaterialTheme.typography.bodySmall,
                        color = Color(0xFF4D9FEC)
                    )
                }
            }

            if (entry.printStatus == PrintStatus.Printed && entry.printersOk.isNotEmpty()) {
                HorizontalDivider(color = Color(0xFF2E3A4A), thickness = 0.5.dp)
                Text(
                    "✓ " + entry.printersOk.joinToString(" · "),
                    style = MaterialTheme.typography.bodySmall,
                    color = Color(0xFF16C79A)
                )
            }

            if (entry.printStatus == PrintStatus.Partial) {
                HorizontalDivider(color = Color(0xFF2E3A4A), thickness = 0.5.dp)
                if (entry.printersOk.isNotEmpty()) {
                    Text(
                        "✓ " + entry.printersOk.joinToString(" · "),
                        style = MaterialTheme.typography.bodySmall,
                        color = Color(0xFF16C79A)
                    )
                }
                Text(
                    "✗ Failed: " + entry.printersFailed.joinToString(" · "),
                    style = MaterialTheme.typography.bodySmall,
                    color = Color(0xFFF4A261)
                )
                if (!entry.error.isNullOrBlank()) {
                    Text(
                        entry.error,
                        style = MaterialTheme.typography.bodySmall,
                        color = Color(0xFF8A9BB0)
                    )
                }
            }

            if (entry.printStatus == PrintStatus.Failed) {
                HorizontalDivider(color = Color(0xFF2E3A4A), thickness = 0.5.dp)
                Text(
                    "✗ Print failed",
                    style = MaterialTheme.typography.bodySmall.copy(fontWeight = FontWeight.Bold),
                    color = Color(0xFFE63946)
                )
                if (!entry.error.isNullOrBlank()) {
                    Text(
                        entry.error,
                        style = MaterialTheme.typography.bodySmall,
                        color = Color(0xFFE07070)
                    )
                }
                if (entry.printersFailed.isNotEmpty()) {
                    Text(
                        "Printer: " + entry.printersFailed.joinToString(" · "),
                        style = MaterialTheme.typography.bodySmall,
                        color = Color(0xFF8A9BB0)
                    )
                }
            }
        }
    }
}

@Composable
private fun StatusPill(status: PrintStatus) {
    val (label, color) = when (status) {
        PrintStatus.Incoming -> "New"      to Color(0xFFE9C46A)
        PrintStatus.Printing -> "Printing" to Color(0xFF4D9FEC)
        PrintStatus.Printed  -> "Printed"  to Color(0xFF16C79A)
        PrintStatus.Partial  -> "Partial"  to Color(0xFFF4A261)
        PrintStatus.Failed   -> "Failed"   to Color(0xFFE63946)
    }
    Box(
        modifier = Modifier
            .background(color.copy(alpha = 0.18f), RoundedCornerShape(6.dp))
            .padding(horizontal = 8.dp, vertical = 3.dp)
    ) {
        Text(label, style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold), color = color)
    }
}

@Composable
private fun TypeChip(label: String) {
    Box(
        modifier = Modifier
            .background(Color(0xFF2E3A4A), RoundedCornerShape(6.dp))
            .padding(horizontal = 8.dp, vertical = 3.dp)
    ) {
        Text(label, style = MaterialTheme.typography.labelSmall, color = Color(0xFF8A9BB0))
    }
}

@Composable
private fun StatusRow(
    status: PrintHubRepository.ConnectionStatus,
    branchName: String?,
    printedToday: Int
) {
    val (label, color) = when (status) {
        PrintHubRepository.ConnectionStatus.Online       -> "Online – live" to Color(0xFF16C79A)
        PrintHubRepository.ConnectionStatus.Polling      -> "Polling fallback" to Color(0xFFF4A261)
        PrintHubRepository.ConnectionStatus.Connecting   -> "Connecting…" to Color(0xFFE9C46A)
        PrintHubRepository.ConnectionStatus.Offline      -> "Offline" to Color(0xFFE63946)
        PrintHubRepository.ConnectionStatus.Disconnected -> "Disconnected" to Color(0xFFE63946)
    }
    Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(modifier = Modifier.size(12.dp).background(color, CircleShape))
            Spacer(Modifier.width(12.dp))
            Column(Modifier.weight(1f)) {
                Text(label, color = MaterialTheme.colorScheme.onSurface, style = MaterialTheme.typography.titleMedium)
                if (!branchName.isNullOrBlank()) {
                    Text("Branch: $branchName", color = MaterialTheme.colorScheme.onSurfaceVariant, style = MaterialTheme.typography.bodySmall)
                }
            }
            Column(horizontalAlignment = Alignment.End) {
                Text("$printedToday", color = MaterialTheme.colorScheme.primary, style = MaterialTheme.typography.headlineSmall)
                Text("today", color = MaterialTheme.colorScheme.onSurfaceVariant, style = MaterialTheme.typography.bodySmall)
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
            Text("Printers", style = MaterialTheme.typography.titleMedium, color = MaterialTheme.colorScheme.onSurface)
            if (default != null) {
                Text("Default: ${default.name} → ${default.ipAddress}:${default.port}", color = MaterialTheme.colorScheme.onSurfaceVariant, style = MaterialTheme.typography.bodySmall)
            } else {
                Text("No default printer configured", color = MaterialTheme.colorScheme.error, style = MaterialTheme.typography.bodySmall)
            }
            for ((station, p) in stations) {
                Text("$station → ${p.name} (${p.ipAddress})", color = MaterialTheme.colorScheme.onSurfaceVariant, style = MaterialTheme.typography.bodySmall)
            }
        }
    }
}

@Composable
private fun TestPrintRow(
    inProgress: Boolean,
    message: String?,
    onTest: () -> Unit,
    onDismiss: () -> Unit
) {
    Card(
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Column(Modifier.weight(1f)) {
                    Text("Server-rendered test", style = MaterialTheme.typography.titleSmall, color = MaterialTheme.colorScheme.onSurface)
                    Text("Tests full pipeline: server → relay → printer", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
                Spacer(Modifier.width(12.dp))
                Button(
                    onClick = onTest,
                    enabled = !inProgress,
                    contentPadding = PaddingValues(horizontal = 14.dp, vertical = 8.dp)
                ) {
                    if (inProgress) {
                        CircularProgressIndicator(modifier = Modifier.size(16.dp), strokeWidth = 2.dp, color = MaterialTheme.colorScheme.onPrimary)
                    } else {
                        Icon(Icons.Filled.Print, contentDescription = null, modifier = Modifier.size(16.dp))
                    }
                    Spacer(Modifier.width(6.dp))
                    Text(if (inProgress) "Sending…" else "Test print", fontSize = 13.sp)
                }
            }
            if (!message.isNullOrBlank()) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(
                        message,
                        modifier = Modifier.weight(1f),
                        color = if (message.startsWith("✓")) Color(0xFF16C79A)
                                else if (message.startsWith("⚠")) Color(0xFFF4A261)
                                else MaterialTheme.colorScheme.error,
                        style = MaterialTheme.typography.bodySmall
                    )
                    IconButton(onClick = onDismiss, modifier = Modifier.size(28.dp)) {
                        Icon(Icons.Filled.Refresh, contentDescription = "Dismiss", modifier = Modifier.size(16.dp))
                    }
                }
            }
        }
    }
}

private val timeFmt = SimpleDateFormat("HH:mm:ss", Locale.US)
