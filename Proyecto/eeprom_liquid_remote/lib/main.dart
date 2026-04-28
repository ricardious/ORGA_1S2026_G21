import 'dart:async';
import 'dart:io';

import 'package:bluetooth_serial_android/bluetooth_serial_android.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:liquid_glass_renderer/liquid_glass_renderer.dart';
import 'package:permission_handler/permission_handler.dart';

const String kAppName = 'EEPROM Liquid Remote';

void main() {
  runApp(const SmartHomeApp());
}

class SmartHomeApp extends StatelessWidget {
  const SmartHomeApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: kAppName,
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF0B0E14),
        fontFamily: 'Inter',
        textTheme: const TextTheme(
          titleLarge: TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.w600,
          ),
          bodyMedium: TextStyle(color: Color(0xFFB0B3C6)),
        ),
      ),
      home: const ControlPanel(),
    );
  }
}

class RemoteDevice {
  const RemoteDevice({
    required this.name,
    required this.address,
    this.bonded = false,
  });

  final String name;
  final String address;
  final bool bonded;

  factory RemoteDevice.fromMap(Map<dynamic, dynamic> raw) {
    final name = (raw['name'] ?? '').toString().trim();
    final address = (raw['address'] ?? '').toString().trim();
    return RemoteDevice(
      name: name.isEmpty ? 'Dispositivo sin nombre' : name,
      address: address,
      bonded: raw['bonded'] == true,
    );
  }
}

class CommandSpec {
  const CommandSpec({
    required this.title,
    required this.icon,
    required this.command,
    required this.modeLabel,
    required this.successMessage,
  });

  final String title;
  final IconData icon;
  final String command;
  final String modeLabel;
  final String successMessage;
}

class ControlPanel extends StatefulWidget {
  const ControlPanel({super.key});

  @override
  State<ControlPanel> createState() => _ControlPanelState();
}

class _ControlPanelState extends State<ControlPanel> {
  static const _okColor = Color(0xFF00FF66);
  static const _errorColor = Color(0xFFFF3366);
  static const _infoColor = Color(0xFFB0B3C6);
  static const _classicUuid = '00001101-0000-1000-8000-00805F9B34FB';
  static const _discoveryChannel = MethodChannel(
    'eeprom_liquid_remote/discovery',
  );

  final bool _isAndroid = Platform.isAndroid;
  final List<CommandSpec> _commands = const [
    CommandSpec(
      title: 'Modo Fiesta',
      icon: Icons.celebration,
      command: 'modo_fiesta',
      modeLabel: 'Modo Fiesta',
      successMessage: 'Modo Fiesta enviado',
    ),
    CommandSpec(
      title: 'Modo Relajado',
      icon: Icons.spa,
      command: 'modo_relajado',
      modeLabel: 'Modo Relajado',
      successMessage: 'Modo Relajado enviado',
    ),
    CommandSpec(
      title: 'Modo Noche',
      icon: Icons.nightlight_round,
      command: 'modo_noche',
      modeLabel: 'Modo Noche',
      successMessage: 'Modo Noche enviado',
    ),
    CommandSpec(
      title: 'Encender Todo',
      icon: Icons.power_settings_new,
      command: 'encender_todo',
      modeLabel: 'Encender Todo',
      successMessage: 'Encender Todo enviado',
    ),
    CommandSpec(
      title: 'Apagar Todo',
      icon: Icons.power_off,
      command: 'apagar_todo',
      modeLabel: 'Apagar Todo',
      successMessage: 'Apagar Todo enviado',
    ),
    CommandSpec(
      title: 'Estado',
      icon: Icons.analytics,
      command: 'estado',
      modeLabel: '',
      successMessage: 'Consulta de estado enviada',
    ),
  ];

  bool isBluetoothConnected = false;
  bool isProcessing = false;
  bool _readerRunning = false;
  String currentMode = 'Sin conexión';
  String systemMessage = 'Seleccione un dispositivo Bluetooth.';
  Color systemMessageColor = _infoColor;
  String _deviceLabel = 'Sin dispositivo';
  List<RemoteDevice> _pairedDevices = const [];
  List<RemoteDevice> _nearbyDevices = const [];

  List<Object> get _deviceEntries {
    final entries = <Object>[];
    if (_pairedDevices.isNotEmpty) {
      entries
        ..add('GUARDADOS')
        ..addAll(_pairedDevices);
    }

    final pairedAddresses = _pairedDevices.map((device) => device.address).toSet();
    final nearbyOnly = _nearbyDevices
        .where((device) => !pairedAddresses.contains(device.address))
        .toList();
    if (nearbyOnly.isNotEmpty) {
      entries
        ..add('CERCANOS')
        ..addAll(nearbyOnly);
    }
    return entries;
  }

  @override
  void initState() {
    super.initState();
    if (_isAndroid) {
      unawaited(_loadPairedDevices());
    } else {
      currentMode = 'No disponible';
      systemMessage = 'Bluetooth clásico solo está soportado en Android.';
      systemMessageColor = _errorColor;
    }
  }

  @override
  void dispose() {
    _readerRunning = false;
    if (isBluetoothConnected) {
      unawaited(FlutterBluetoothSerial.disconnect());
    }
    super.dispose();
  }

  String _shortBluetoothError(
    Object error, {
    String fallback = 'Error de Bluetooth.',
  }) {
    final raw = error.toString().toLowerCase();

    if (raw.contains('permission') || raw.contains('denied')) {
      return 'Permiso Bluetooth denegado.';
    }
    if (raw.contains('timeout') || raw.contains('timed out')) {
      return 'Tiempo de espera agotado.';
    }
    if (raw.contains('socket') || raw.contains('connect')) {
      return 'No se pudo conectar.';
    }
    if (raw.contains('bond') || raw.contains('pair')) {
      return 'El dispositivo no está emparejado.';
    }
    if (raw.contains('adapter') || raw.contains('disabled')) {
      return 'Active el Bluetooth del teléfono.';
    }
    if (raw.contains('read')) {
      return 'No se pudo leer la respuesta.';
    }
    if (raw.contains('write')) {
      return 'No se pudo enviar el comando.';
    }

    return fallback;
  }

  Future<bool> _ensurePermissions() async {
    try {
      final connectStatus = await Permission.bluetoothConnect.request();
      final scanStatus = await Permission.bluetoothScan.request();
      return connectStatus.isGranted && scanStatus.isGranted;
    } catch (error) {
      _setFeedback(
        _shortBluetoothError(
          error,
          fallback: 'No se pudo pedir permiso Bluetooth.',
        ),
        _errorColor,
      );
      return false;
    }
  }

  Future<void> _loadPairedDevices() async {
    if (!_isAndroid || !await _ensurePermissions()) {
      return;
    }
    try {
      final rawDevices = await FlutterBluetoothSerial.getPairedDevices();
      final devices = rawDevices
          .map(RemoteDevice.fromMap)
          .where((device) => device.address.isNotEmpty)
          .toList()
        ..sort((left, right) => left.name.compareTo(right.name));
      if (!mounted) {
        return;
      }
      setState(() {
        _pairedDevices = devices;
      });
      await _scanNearbyDevices();
    } catch (error) {
      _setFeedback('No se pudieron listar dispositivos guardados.', _errorColor);
    }
  }

  Future<void> _scanNearbyDevices() async {
    if (!_isAndroid) {
      return;
    }
    try {
      final rawDevices = await _discoveryChannel.invokeMethod<List<dynamic>>(
        'scanDevices',
      );
      final devices = (rawDevices ?? const [])
          .map((raw) => RemoteDevice.fromMap(raw as Map<dynamic, dynamic>))
          .where((device) => device.address.isNotEmpty)
          .toList();
      devices.sort((left, right) => left.name.compareTo(right.name));
      if (!mounted) {
        return;
      }
      setState(() {
        _nearbyDevices = devices;
      });
    } on PlatformException catch (error) {
      if (error.code == 'NO_PERMISSION') {
        _setFeedback('Permiso de escaneo no concedido.', _errorColor);
      } else if (error.code == 'BT_DISABLED') {
        _setFeedback('Active el Bluetooth del teléfono.', _errorColor);
      } else if (error.code != 'SCAN_IN_PROGRESS') {
        _setFeedback('No se pudieron buscar dispositivos.', _errorColor);
      }
    } catch (_) {
      _setFeedback('No se pudieron buscar dispositivos.', _errorColor);
    }
  }

  Future<void> _connectToDevice(RemoteDevice device) async {
    if (!_isAndroid) {
      return;
    }
    if (!await _ensurePermissions()) {
      _setFeedback('Permisos Bluetooth denegados.', _errorColor);
      return;
    }

    setState(() {
      isProcessing = true;
    });
    _setFeedback('Conectando con ${device.name}...', _infoColor);

    try {
      if (isBluetoothConnected) {
        await FlutterBluetoothSerial.disconnect();
      }
      final connected = await FlutterBluetoothSerial.connect(
        device.address,
        uuid: _classicUuid,
        timeoutMs: 900,
      );
      if (!mounted) {
        return;
      }
      if (!connected) {
        _setFeedback('No fue posible establecer la conexión.', _errorColor);
        return;
      }

      setState(() {
        _deviceLabel = device.name;
        isBluetoothConnected = true;
        currentMode = 'Conectado';
      });
      _setFeedback('Conectado a ${device.name}.', _okColor);
      _startReadLoop();
    } catch (error) {
      _setFeedback(
        _shortBluetoothError(error, fallback: 'Error al conectar.'),
        _errorColor,
      );
    } finally {
      if (mounted) {
        setState(() {
          isProcessing = false;
        });
      }
    }
  }

  Future<void> _disconnectBluetooth() async {
    _readerRunning = false;
    try {
      await FlutterBluetoothSerial.disconnect();
    } catch (_) {
      // Ignore explicit disconnect failures.
    }
    if (!mounted) {
      return;
    }
    setState(() {
      isBluetoothConnected = false;
      currentMode = 'Sin conexión';
      _deviceLabel = 'Sin dispositivo';
    });
    _setFeedback('Bluetooth desconectado.', _errorColor);
  }

  void _startReadLoop() {
    if (_readerRunning) {
      return;
    }
    _readerRunning = true;
    unawaited(_readLoop());
  }

  Future<void> _readLoop() async {
    while (_readerRunning && isBluetoothConnected) {
      try {
        final line = await FlutterBluetoothSerial.readLine('\n');
        if (!_readerRunning || !mounted) {
          break;
        }
        final trimmed = line?.trim() ?? '';
        if (trimmed.isEmpty) {
          await Future<void>.delayed(const Duration(milliseconds: 80));
          continue;
        }
        _handleIncomingLine(trimmed);
      } catch (error) {
        if (!mounted) {
          break;
        }
        setState(() {
          isBluetoothConnected = false;
          isProcessing = false;
          currentMode = 'Sin conexión';
          _deviceLabel = 'Sin dispositivo';
        });
        _setFeedback('Se perdió la conexión Bluetooth.', _errorColor);
        break;
      }
    }
    _readerRunning = false;
  }

  void _handleIncomingLine(String line) {
    if (!mounted) {
      return;
    }

    setState(() {
      isProcessing = false;
    });

    if (line == 'READY') {
      _setFeedback('Arduino listo para recibir comandos.', _okColor);
      return;
    }
    if (line.startsWith('MODE_OK:')) {
      final mode = line.split(':').last.trim();
      setState(() {
        currentMode = _formatMode(mode);
      });
      _setFeedback('${_formatMode(mode)} activado.', _okColor);
      return;
    }
    if (line.startsWith('STATUS:')) {
      final parts = line.split(':');
      if (parts.length >= 3) {
        setState(() {
          currentMode = _formatMode(parts[1]);
        });
        _setFeedback(
          parts[2].trim().toUpperCase() == 'OK'
              ? 'Estado correcto en ${_formatMode(parts[1])}.'
              : 'Arduino reportó error en ${_formatMode(parts[1])}.',
          parts[2].trim().toUpperCase() == 'OK' ? _okColor : _errorColor,
        );
        return;
      }
    }
    if (line == 'DOOR_OPEN') {
      _setFeedback('Puerta abierta.', _okColor);
      return;
    }
    if (line == 'DOOR_CLOSED') {
      _setFeedback('Puerta cerrada.', _okColor);
      return;
    }
    if (line == 'CMD_ERROR' || line == 'MODE_ERROR') {
      _setFeedback('El Arduino rechazó el comando.', _errorColor);
      return;
    }

    _setFeedback(line, _infoColor);
  }

  Future<void> _sendCommand(CommandSpec command) async {
    if (!isBluetoothConnected) {
      _setFeedback('Conecte un dispositivo Bluetooth primero.', _errorColor);
      return;
    }

    setState(() {
      isProcessing = true;
    });
    _setFeedback('Enviando comando...', _infoColor);

    try {
      await FlutterBluetoothSerial.write('${command.command}\r\n');
      if (command.modeLabel.isNotEmpty) {
        setState(() {
          currentMode = command.modeLabel;
        });
      }
      _setFeedback(command.successMessage, _okColor);
    } catch (error) {
      if (!mounted) {
        return;
      }
      setState(() {
        isProcessing = false;
      });
      _setFeedback('No se pudo enviar el comando.', _errorColor);
    }
  }

  Future<void> _openBluetoothSheet() async {
    if (!_isAndroid) {
      _setFeedback('Bluetooth clásico solo está soportado en Android.', _errorColor);
      return;
    }

    await _loadPairedDevices();
    if (!mounted) {
      return;
    }

    await showModalBottomSheet<void>(
      context: context,
      backgroundColor: const Color(0xFF10141C),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(28)),
      ),
      builder: (context) {
        return SafeArea(
          child: Padding(
            padding: const EdgeInsets.fromLTRB(20, 16, 20, 20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Expanded(
                      child: Text(
                        'Dispositivos Bluetooth',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 20,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ),
                    IconButton(
                      onPressed: () {
                        unawaited(_loadPairedDevices());
                        Navigator.of(context).pop();
                        unawaited(_openBluetoothSheet());
                      },
                      icon: const Icon(Icons.refresh, color: Colors.white),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                const Text(
                  'Se muestran guardados y encontrados cercanos.',
                  style: TextStyle(color: Color(0xFFB0B3C6)),
                ),
                const SizedBox(height: 16),
                Expanded(
                  child: (_pairedDevices.isEmpty && _nearbyDevices.isEmpty)
                      ? const Center(
                          child: Text(
                            'No se encontraron dispositivos.',
                            style: TextStyle(color: Color(0xFFB0B3C6)),
                          ),
                        )
                      : ListView.separated(
                          itemCount: _deviceEntries.length,
                          separatorBuilder: (_, _) => Divider(
                            color: Colors.white.withValues(alpha: 0.08),
                          ),
                          itemBuilder: (context, index) {
                            final entry = _deviceEntries[index];
                            if (entry is String) {
                              return Padding(
                                padding: const EdgeInsets.only(top: 8, bottom: 4),
                                child: Text(
                                  entry,
                                  style: const TextStyle(
                                    color: Color(0xFFB0B3C6),
                                    fontSize: 12,
                                    fontWeight: FontWeight.w700,
                                    letterSpacing: 0.8,
                                  ),
                                ),
                              );
                            }
                            final device = entry as RemoteDevice;
                            return ListTile(
                              contentPadding: EdgeInsets.zero,
                              leading: const Icon(
                                Icons.bluetooth,
                                color: Colors.white,
                              ),
                              title: Text(
                                device.name,
                                style: const TextStyle(color: Colors.white),
                              ),
                              subtitle: Text(
                                device.bonded
                                    ? '${device.address} • Guardado'
                                    : '${device.address} • Cercano',
                                style: const TextStyle(color: Color(0xFFB0B3C6)),
                              ),
                              trailing: FilledButton(
                                onPressed: () {
                                  Navigator.of(context).pop();
                                  unawaited(_connectToDevice(device));
                                },
                                child: const Text('Conectar'),
                              ),
                            );
                          },
                        ),
                ),
                if (isBluetoothConnected)
                  Padding(
                    padding: const EdgeInsets.only(top: 12),
                    child: SizedBox(
                      width: double.infinity,
                      child: OutlinedButton.icon(
                        onPressed: () {
                          Navigator.of(context).pop();
                          unawaited(_disconnectBluetooth());
                        },
                        icon: const Icon(Icons.link_off),
                        label: const Text('Desconectar'),
                      ),
                    ),
                  ),
              ],
            ),
          ),
        );
      },
    );
  }

  void _setFeedback(String message, Color color) {
    if (!mounted) {
      return;
    }
    setState(() {
      systemMessage = message;
      systemMessageColor = color;
    });
  }

  String _formatMode(String rawMode) {
    switch (rawMode.trim().toLowerCase()) {
      case 'modo_fiesta':
        return 'Modo Fiesta';
      case 'modo_relajado':
        return 'Modo Relajado';
      case 'modo_noche':
        return 'Modo Noche';
      case 'encender_todo':
        return 'Encender Todo';
      case 'apagar_todo':
        return 'Apagar Todo';
      default:
        return rawMode;
    }
  }

  @override
  Widget build(BuildContext context) {
    final media = MediaQuery.of(context);
    final isTablet = media.size.shortestSide >= 600;
    final isPortrait = media.orientation == Orientation.portrait;

    return Scaffold(
      body: SafeArea(
        child: isTablet
            ? (isPortrait
                ? _buildTabletPortraitLayout()
                : _buildTabletLandscapeLayout())
            : _buildPhoneLayout(),
      ),
    );
  }

  Widget _buildPhoneLayout() {
    return _buildBackgroundSurface(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(16, 8, 16, 6),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _buildHeader(compact: true),
            const SizedBox(height: 8),
            Expanded(
              flex: 16,
              child: _buildStatusPanel(compact: true),
            ),
            const SizedBox(height: 8),
            Expanded(
              flex: 36,
              child: _buildCommandsGrid(2, compact: true),
            ),
            const SizedBox(height: 8),
            _buildFeedbackPanel(compact: true),
          ],
        ),
      ),
    );
  }

  Widget _buildTabletPortraitLayout() {
    return _buildBackgroundSurface(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(28, 24, 28, 20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _buildHeader(),
            const SizedBox(height: 24),
            SizedBox(
              height: 220,
              child: _buildStatusPanel(),
            ),
            const SizedBox(height: 24),
            const Align(
              alignment: Alignment.centerLeft,
              child: Text(
                'Comandos Principales',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.w600,
                  color: Colors.white,
                ),
              ),
            ),
            const SizedBox(height: 24),
            Expanded(child: _buildCommandsGrid(2)),
            const SizedBox(height: 20),
            _buildFeedbackPanel(),
          ],
        ),
      ),
    );
  }

  Widget _buildTabletLandscapeLayout() {
    return _buildBackgroundSurface(
      child: Padding(
        padding: const EdgeInsets.all(32.0),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Expanded(
              flex: 3,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  _buildHeader(),
                  const SizedBox(height: 48),
                  Expanded(child: _buildStatusPanel()),
                  const SizedBox(height: 24),
                  _buildFeedbackPanel(),
                ],
              ),
            ),
            const SizedBox(width: 48),
            Expanded(
              flex: 7,
              child: Column(
                children: [
                  const SizedBox(height: 20),
                  const Align(
                    alignment: Alignment.centerLeft,
                    child: Text(
                      'Comandos Principales',
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.w600,
                        color: Colors.white,
                      ),
                    ),
                  ),
                  const SizedBox(height: 32),
                  Expanded(child: _buildCommandsGrid(3)),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBackgroundSurface({required Widget child}) {
    return Stack(
      children: [
        Positioned.fill(
          child: Image.asset(
            'assets/bg.png',
            fit: BoxFit.cover,
            alignment: Alignment.center,
          ),
        ),
        child,
      ],
    );
  }

  Widget _buildHeader({bool compact = false}) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Expanded(
          child: Text(
            kAppName,
            maxLines: 2,
            style: TextStyle(
              fontSize: compact ? 19 : 24,
              fontWeight: FontWeight.w700,
              color: Colors.white,
              letterSpacing: -0.5,
            ),
          ),
        ),
        const SizedBox(width: 16),
        GestureDetector(
          onTap: _openBluetoothSheet,
          child: LiquidGlass.withOwnLayer(
            fake: true,
            settings: const LiquidGlassSettings(
              thickness: 10,
              blur: 15,
              glassColor: Color(0x22FFFFFF),
            ),
            shape: const LiquidOval(),
            child: Container(
              padding: EdgeInsets.all(compact ? 9 : 12),
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                border: Border.all(
                  color: isBluetoothConnected
                      ? const Color(0xFF0055FF).withValues(alpha: 0.5)
                      : Colors.white10,
                  width: 1,
                ),
              ),
              child: Icon(
                isBluetoothConnected
                    ? Icons.bluetooth_connected
                    : Icons.bluetooth_disabled,
                color: isBluetoothConnected
                    ? const Color(0xFF0055FF)
                    : const Color(0xFFB0B3C6),
                size: compact ? 18 : 24,
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildStatusPanel({bool compact = false}) {
    return LiquidGlassLayer(
      fake: true,
      settings: const LiquidGlassSettings(
        thickness: 15,
        blur: 20,
        glassColor: Color(0x11FFFFFF),
        lightIntensity: 1.2,
      ),
      child: LiquidGlass(
        shape: LiquidRoundedSuperellipse(borderRadius: 32),
        child: Container(
          width: double.infinity,
          height: double.infinity,
          padding: EdgeInsets.all(compact ? 14 : 32),
          decoration: BoxDecoration(
            border: Border.all(
              color: Colors.white.withValues(alpha: 0.1),
              width: 1.0,
            ),
            borderRadius: BorderRadius.circular(32),
          ),
          child: LayoutBuilder(
            builder: (context, constraints) {
              final panelHeight = constraints.maxHeight;
              final labelSize =
                  compact ? (panelHeight * 0.11).clamp(13.0, 16.0) : 14.0;
              final modeSize =
                  compact ? (panelHeight * 0.24).clamp(20.0, 28.0) : 26.0;
              final statusSize =
                  compact ? (panelHeight * 0.12).clamp(12.0, 15.0) : 14.0;
              final topGap = compact
                  ? (panelHeight * 0.06).clamp(4.0, 8.0)
                  : 8.0;
              final bottomGap = compact
                  ? (panelHeight * 0.08).clamp(6.0, 12.0)
                  : 12.0;

              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Spacer(),
                  Text(
                    'Modo Actual',
                    style: TextStyle(
                      fontSize: labelSize,
                      fontWeight: FontWeight.w600,
                      color: const Color(0xFFB0B3C6),
                      letterSpacing: 0.8,
                    ),
                  ),
                  SizedBox(height: topGap),
                  Text(
                    currentMode,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(
                      fontSize: modeSize,
                      fontWeight: FontWeight.w700,
                      color: Colors.white,
                    ),
                  ),
                  SizedBox(height: bottomGap),
                  Row(
                    children: [
                      Container(
                        width: 8,
                        height: 8,
                        decoration: BoxDecoration(
                          color: isBluetoothConnected ? _okColor : _errorColor,
                          shape: BoxShape.circle,
                          boxShadow: [
                            BoxShadow(
                              color: (isBluetoothConnected ? _okColor : _errorColor)
                                  .withValues(alpha: 0.5),
                              blurRadius: 8,
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          isBluetoothConnected
                              ? '$_deviceLabel conectado'
                              : 'Sistema No Disponible',
                          overflow: TextOverflow.ellipsis,
                          style: TextStyle(
                            fontSize: statusSize,
                            fontWeight: FontWeight.w500,
                            color: const Color(0xFFB0B3C6),
                          ),
                        ),
                      ),
                    ],
                  ),
                  const Spacer(),
                ],
              );
            },
          ),
        ),
      ),
    );
  }

  Widget _buildCommandsGrid(
    int crossAxisCount, {
    bool shrinkWrap = false,
    bool compact = false,
  }) {
    final isPhone = crossAxisCount == 2;
    final spacing = compact ? 8.0 : (isPhone ? 12.0 : 16.0);

    return LiquidGlassLayer(
      fake: true,
      settings: const LiquidGlassSettings(
        thickness: 10,
        blur: 15,
        glassColor: Color(0x0CFFFFFF),
        lightIntensity: 1.0,
      ),
      child: LayoutBuilder(
        builder: (context, constraints) {
          final rowCount = (_commands.length / crossAxisCount).ceil();
          final tileWidth =
              (constraints.maxWidth - (spacing * (crossAxisCount - 1))) /
              crossAxisCount;
          final tileHeight =
              (constraints.maxHeight - (spacing * (rowCount - 1))) / rowCount;
          final childAspectRatio = tileWidth / tileHeight;
          final dense = compact || tileHeight < 140;
          final iconSize = dense ? (tileHeight * 0.26).clamp(22.0, 34.0) : 46.0;
          final textSize = dense ? (tileHeight * 0.11).clamp(11.0, 13.0) : 14.0;
          final verticalPadding = dense
              ? (tileHeight * 0.08).clamp(6.0, 10.0)
              : 16.0;
          final textGap = dense ? (tileHeight * 0.05).clamp(4.0, 8.0) : 16.0;

          return GridView.builder(
            shrinkWrap: shrinkWrap,
            physics: const NeverScrollableScrollPhysics(),
            gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: crossAxisCount,
              crossAxisSpacing: spacing,
              mainAxisSpacing: spacing,
              childAspectRatio: childAspectRatio,
            ),
            itemCount: _commands.length,
            itemBuilder: (context, index) {
              final command = _commands[index];
              return LiquidStretch(
                stretch: 0.3,
                interactionScale: 0.95,
                child: GestureDetector(
                  onTap: () => _sendCommand(command),
                  child: LiquidGlass(
                    shape: LiquidRoundedSuperellipse(borderRadius: 24),
                    child: GlassGlow(
                      glowColor: Colors.white.withValues(alpha: 0.15),
                      glowRadius: 1.5,
                      child: Container(
                        padding: EdgeInsets.symmetric(
                          horizontal: dense ? 8 : (isPhone ? 10 : 12),
                          vertical: verticalPadding,
                        ),
                        decoration: BoxDecoration(
                          border: Border.all(
                            color: Colors.white.withValues(alpha: 0.05),
                            width: 1.0,
                          ),
                        ),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(
                              command.icon,
                              size: iconSize,
                              color: Colors.white,
                            ),
                            SizedBox(height: textGap),
                            Text(
                              command.title,
                              textAlign: TextAlign.center,
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                              style: TextStyle(
                                fontSize: textSize,
                                fontWeight: FontWeight.w500,
                                color: Colors.white,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }

  Widget _buildFeedbackPanel({bool compact = false}) {
    return LiquidGlass.withOwnLayer(
      fake: true,
      settings: const LiquidGlassSettings(
        thickness: 8,
        blur: 15,
        glassColor: Color(0x1AFFFFFF),
      ),
      shape: const LiquidRoundedRectangle(borderRadius: 100),
      child: Container(
        padding: EdgeInsets.symmetric(
          horizontal: compact ? 14 : 24,
          vertical: compact ? 10 : 16,
        ),
        decoration: BoxDecoration(
          border: Border.all(
            color: systemMessageColor.withValues(alpha: 0.3),
            width: 1.0,
          ),
          boxShadow: [
            BoxShadow(
              color: systemMessageColor.withValues(alpha: 0.05),
              blurRadius: 20,
              spreadRadius: 2,
            ),
          ],
        ),
        child: Row(
          children: [
            if (isProcessing)
              Container(
                width: 16,
                height: 16,
                margin: const EdgeInsets.only(right: 12),
                child: const CircularProgressIndicator(
                  strokeWidth: 2,
                  valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                ),
              )
            else
              Icon(
                systemMessageColor == _errorColor
                    ? Icons.error_outline
                    : Icons.check_circle_outline,
                color: systemMessageColor,
                size: compact ? 18 : 20,
              ),
            if (!isProcessing) const SizedBox(width: 12),
            Expanded(
              child: Text(
                systemMessage,
                maxLines: compact ? 2 : null,
                overflow: compact ? TextOverflow.ellipsis : null,
                style: TextStyle(
                  color: isProcessing ? Colors.white : systemMessageColor,
                  fontWeight: FontWeight.w500,
                  fontSize: compact ? 12 : 15,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
