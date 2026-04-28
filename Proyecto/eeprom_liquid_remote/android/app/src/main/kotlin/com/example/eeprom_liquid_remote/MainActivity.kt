package com.example.eeprom_liquid_remote

import android.Manifest
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothManager
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.content.pm.PackageManager
import android.os.Build
import android.os.Handler
import android.os.Looper
import androidx.core.content.ContextCompat
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel

class MainActivity : FlutterActivity() {
    private val discoveryChannel = "eeprom_liquid_remote/discovery"
    private val discoveryTimeoutMs = 9000L
    private var discoveryReceiver: BroadcastReceiver? = null
    private var pendingDiscoveryResult: MethodChannel.Result? = null
    private val discoveryDevices = linkedMapOf<String, Map<String, Any>>()
    private val handler = Handler(Looper.getMainLooper())

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)

        MethodChannel(
            flutterEngine.dartExecutor.binaryMessenger,
            discoveryChannel
        ).setMethodCallHandler { call, result ->
            when (call.method) {
                "scanDevices" -> scanDevices(result)
                else -> result.notImplemented()
            }
        }
    }

    override fun onDestroy() {
        cleanupDiscovery()
        super.onDestroy()
    }

    private fun scanDevices(result: MethodChannel.Result) {
        if (pendingDiscoveryResult != null) {
            result.error("SCAN_IN_PROGRESS", "Ya hay un escaneo en curso.", null)
            return
        }

        val adapter = bluetoothAdapter()
        if (adapter == null) {
            result.error("NO_ADAPTER", "Bluetooth no disponible.", null)
            return
        }
        if (!adapter.isEnabled) {
            result.error("BT_DISABLED", "Bluetooth apagado.", null)
            return
        }
        if (!hasScanPermission()) {
            result.error("NO_PERMISSION", "Permiso de escaneo no concedido.", null)
            return
        }

        discoveryDevices.clear()
        pendingDiscoveryResult = result

        val receiver = object : BroadcastReceiver() {
            override fun onReceive(context: Context?, intent: Intent?) {
                when (intent?.action) {
                    BluetoothDevice.ACTION_FOUND -> {
                        val device = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                            intent.getParcelableExtra(
                                BluetoothDevice.EXTRA_DEVICE,
                                BluetoothDevice::class.java
                            )
                        } else {
                            @Suppress("DEPRECATION")
                            intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE)
                        }
                        if (device != null && hasConnectPermission()) {
                            val name = device.name?.takeIf { it.isNotBlank() }
                                ?: "Dispositivo sin nombre"
                            discoveryDevices[device.address] = mapOf(
                                "name" to name,
                                "address" to device.address,
                                "bonded" to (device.bondState == BluetoothDevice.BOND_BONDED),
                            )
                        }
                    }
                    BluetoothAdapter.ACTION_DISCOVERY_FINISHED -> finishDiscovery()
                }
            }
        }

        discoveryReceiver = receiver
        registerReceiver(
            receiver,
            IntentFilter().apply {
                addAction(BluetoothDevice.ACTION_FOUND)
                addAction(BluetoothAdapter.ACTION_DISCOVERY_FINISHED)
            }
        )

        if (adapter.isDiscovering && hasScanPermission()) {
            runCatching { adapter.cancelDiscovery() }
        }

        if (!adapter.startDiscovery()) {
            cleanupDiscovery()
            result.error("SCAN_FAILED", "No se pudo iniciar el escaneo.", null)
            return
        }

        handler.postDelayed({ finishDiscovery() }, discoveryTimeoutMs)
    }

    private fun finishDiscovery() {
        val adapter = bluetoothAdapter()
        if (adapter?.isDiscovering == true && hasScanPermission()) {
            runCatching { adapter.cancelDiscovery() }
        }

        pendingDiscoveryResult?.success(discoveryDevices.values.toList())
        cleanupDiscovery()
    }

    private fun cleanupDiscovery() {
        handler.removeCallbacksAndMessages(null)
        discoveryReceiver?.let {
            runCatching { unregisterReceiver(it) }
        }
        discoveryReceiver = null
        pendingDiscoveryResult = null
        discoveryDevices.clear()
    }

    private fun bluetoothAdapter(): BluetoothAdapter? {
        val manager = getSystemService(Context.BLUETOOTH_SERVICE) as? BluetoothManager
        return manager?.adapter
    }

    private fun hasScanPermission(): Boolean {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            ContextCompat.checkSelfPermission(
                this,
                Manifest.permission.BLUETOOTH_SCAN
            ) == PackageManager.PERMISSION_GRANTED
        } else {
            true
        }
    }

    private fun hasConnectPermission(): Boolean {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            ContextCompat.checkSelfPermission(
                this,
                Manifest.permission.BLUETOOTH_CONNECT
            ) == PackageManager.PERMISSION_GRANTED
        } else {
            true
        }
    }
}
