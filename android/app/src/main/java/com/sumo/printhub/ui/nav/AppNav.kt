package com.sumo.printhub.ui.nav

import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.sumo.printhub.ui.dashboard.DashboardScreen
import com.sumo.printhub.ui.dashboard.DashboardViewModel
import com.sumo.printhub.ui.settings.SettingsScreen
import com.sumo.printhub.ui.setup.SetupScreen
import com.sumo.printhub.ui.setup.SetupViewModel

object Routes {
    const val Setup = "setup"
    const val Dashboard = "dashboard"
    const val Settings = "settings"
}

@Composable
fun AppNav() {
    val nav = rememberNavController()
    val setupVm: SetupViewModel = hiltViewModel()
    val isRegistered by setupVm.isRegistered.collectAsStateWithLifecycle()
    val start = remember(isRegistered) { if (isRegistered) Routes.Dashboard else Routes.Setup }

    NavHost(navController = nav, startDestination = start) {
        composable(Routes.Setup) {
            SetupScreen(
                vm = setupVm,
                onRegistered = {
                    nav.navigate(Routes.Dashboard) {
                        popUpTo(Routes.Setup) { inclusive = true }
                    }
                }
            )
        }
        composable(Routes.Dashboard) {
            val dashVm: DashboardViewModel = hiltViewModel()
            DashboardScreen(
                vm = dashVm,
                onOpenSettings = { nav.navigate(Routes.Settings) }
            )
        }
        composable(Routes.Settings) {
            SettingsScreen(
                onBack = { nav.popBackStack() },
                onUnregistered = {
                    nav.navigate(Routes.Setup) {
                        popUpTo(0) { inclusive = true }
                    }
                }
            )
        }
    }
}
