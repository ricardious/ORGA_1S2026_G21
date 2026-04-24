import 'package:flutter/material.dart';
import 'package:liquid_glass_renderer/liquid_glass_renderer.dart';

void main() {
  runApp(const SmartHomeApp());
}

class SmartHomeApp extends StatelessWidget {
  const SmartHomeApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Smart Home Control',
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

class ControlPanel extends StatefulWidget {
  const ControlPanel({super.key});

  @override
  State<ControlPanel> createState() => _ControlPanelState();
}

class _ControlPanelState extends State<ControlPanel> {
  bool isBluetoothConnected = true;
  String currentMode = 'Modo Relajado';
  String systemMessage = 'Sistema estable y en línea';
  Color systemMessageColor = const Color(0xFF00FF66);
  bool isProcessing = false;

  void _sendCommand(String mode, String message, {bool isError = false}) {
    setState(() {
      isProcessing = true;
      systemMessage = "Enviando comando...";
      systemMessageColor = const Color(0xFFB0B3C6);
    });

    // Simulate network/bluetooth delay
    Future.delayed(const Duration(milliseconds: 800), () {
      if (!mounted) return;
      setState(() {
        isProcessing = false;
        if (isError) {
          systemMessage = message;
          systemMessageColor = const Color(0xFFFF3366);
        } else {
          currentMode = mode;
          systemMessage = message;
          systemMessageColor = const Color(0xFF00FF66);
        }
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    // Determine layout based on width
    final isTablet = MediaQuery.of(context).size.width >= 900;

    return Scaffold(
      body: Stack(
        children: [
          // Background with blurry colored orbs
          const _AnimatedBackground(),

          SafeArea(
            child: isTablet ? _buildTabletLayout() : _buildPhoneLayout(),
          ),
        ],
      ),
    );
  }

  Widget _buildPhoneLayout() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _buildHeader(),
          const SizedBox(height: 32),
          SizedBox(height: 220, child: _buildStatusPanel()),
          const SizedBox(height: 32),
          Expanded(child: _buildCommandsGrid(2)),
          const SizedBox(height: 24),
          _buildFeedbackPanel(),
        ],
      ),
    );
  }

  Widget _buildTabletLayout() {
    return Padding(
      padding: const EdgeInsets.all(32.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Left Column (30%)
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
          // Right Column (70%)
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
    );
  }

  Widget _buildHeader() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        const Expanded(
          child: Text(
            'Control Center',
            overflow: TextOverflow.ellipsis,
            style: TextStyle(
              fontSize: 28,
              fontWeight: FontWeight.w700,
              color: Colors.white,
              letterSpacing: -0.5,
            ),
          ),
        ),
        const SizedBox(width: 16),
        GestureDetector(
          onTap: () {
            setState(() {
              isBluetoothConnected = !isBluetoothConnected;
              if (!isBluetoothConnected) {
                systemMessage = "Bluetooth desconectado";
                systemMessageColor = const Color(0xFFFF3366);
              } else {
                systemMessage = "Bluetooth conectado";
                systemMessageColor = const Color(0xFF00FF66);
              }
            });
          },
          child: LiquidGlass.withOwnLayer(
            fake: true,
            settings: const LiquidGlassSettings(
              thickness: 10,
              blur: 15,
              glassColor: Color(0x22FFFFFF),
            ),
            shape: const LiquidOval(),
            child: Container(
              padding: const EdgeInsets.all(12),
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
                size: 24,
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildStatusPanel() {
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
          padding: const EdgeInsets.all(32),
          decoration: BoxDecoration(
            border: Border.all(
              color: Colors.white.withValues(alpha: 0.1),
              width: 1.0,
            ),
            borderRadius: BorderRadius.circular(32), // Visual fallback
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(
                Icons.home_rounded,
                size: 48,
                color: Colors.white.withValues(alpha: 0.9),
              ),
              const Spacer(),
              const Text(
                'Modo Actual',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w500,
                  color: Color(0xFFB0B3C6),
                  letterSpacing: 1.0,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                currentMode,
                style: const TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.w700,
                  color: Colors.white,
                ),
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Container(
                    width: 8,
                    height: 8,
                    decoration: BoxDecoration(
                      color: isBluetoothConnected
                          ? const Color(0xFF00FF66)
                          : const Color(0xFFFF3366),
                      shape: BoxShape.circle,
                      boxShadow: [
                        BoxShadow(
                          color: isBluetoothConnected
                              ? const Color(0xFF00FF66).withValues(alpha: 0.5)
                              : const Color(0xFFFF3366).withValues(alpha: 0.5),
                          blurRadius: 8,
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      isBluetoothConnected
                          ? 'Sistema Listo'
                          : 'Sistema No Disponible',
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        fontSize: 14,
                        color: Color(0xFFB0B3C6),
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildCommandsGrid(int crossAxisCount) {
    // Map of commands to icons and action
    final commands = [
      {
        'title': 'Modo Fiesta',
        'icon': Icons.celebration,
        'action': () => _sendCommand('Modo Fiesta', 'Modo Fiesta activado'),
      },
      {
        'title': 'Modo Relajado',
        'icon': Icons.spa,
        'action': () => _sendCommand('Modo Relajado', 'Modo Relajado activado'),
      },
      {
        'title': 'Modo Noche',
        'icon': Icons.nightlight_round,
        'action': () => _sendCommand('Modo Noche', 'Modo Noche activado'),
      },
      {
        'title': 'Encender Todo',
        'icon': Icons.power_settings_new,
        'action': () => _sendCommand(currentMode, 'Todas las luces encendidas'),
      },
      {
        'title': 'Apagar Todo',
        'icon': Icons.power_off,
        'action': () => _sendCommand('Modo Noche', 'Todo el sistema apagado'),
      },
      {
        'title': 'Estado',
        'icon': Icons.analytics,
        'action': () =>
            _sendCommand(currentMode, 'Análisis: Todo operando normal'),
      },
    ];

    return LiquidGlassLayer(
      fake: true,
      settings: const LiquidGlassSettings(
        thickness: 10,
        blur: 15,
        glassColor: Color(0x0CFFFFFF),
        lightIntensity: 1.0,
      ),
      child: GridView.builder(
        physics: const NeverScrollableScrollPhysics(),
        gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: crossAxisCount,
          crossAxisSpacing: 16,
          mainAxisSpacing: 16,
          childAspectRatio: 1.1,
        ),
        itemCount: commands.length,
        itemBuilder: (context, index) {
          final cmd = commands[index];
          return LiquidStretch(
            stretch: 0.3,
            interactionScale: 0.95,
            child: GestureDetector(
              onTap: () {
                if (!isBluetoothConnected) {
                  _sendCommand(
                    currentMode,
                    'Error: Bluetooth desconectado',
                    isError: true,
                  );
                  return;
                }
                (cmd['action'] as Function)();
              },
              child: LiquidGlass(
                shape: LiquidRoundedSuperellipse(borderRadius: 24),
                child: GlassGlow(
                  glowColor: Colors.white.withValues(alpha: 0.15),
                  glowRadius: 1.5,
                  child: Container(
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
                          cmd['icon'] as IconData,
                          size: 36,
                          color: Colors.white,
                        ),
                        const SizedBox(height: 16),
                        Text(
                          cmd['title'] as String,
                          textAlign: TextAlign.center,
                          style: const TextStyle(
                            fontSize: 14,
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
      ),
    );
  }

  Widget _buildFeedbackPanel() {
    return LiquidGlass.withOwnLayer(
      fake: true,
      settings: const LiquidGlassSettings(
        thickness: 8,
        blur: 15,
        glassColor: Color(0x1AFFFFFF),
      ),
      shape: const LiquidRoundedRectangle(borderRadius: 100), // Pill shape
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
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
                systemMessageColor == const Color(0xFFFF3366)
                    ? Icons.error_outline
                    : Icons.check_circle_outline,
                color: systemMessageColor,
                size: 20,
              ),
            if (!isProcessing) const SizedBox(width: 12),
            Expanded(
              child: Text(
                systemMessage,
                style: TextStyle(
                  color: isProcessing ? Colors.white : systemMessageColor,
                  fontWeight: FontWeight.w500,
                  fontSize: 15,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// A background with colorful blurred orbs that create beautiful glass refraction
class _AnimatedBackground extends StatelessWidget {
  const _AnimatedBackground();

  @override
  Widget build(BuildContext context) {
    return Positioned.fill(
      child: Image.asset('assets/bg.png', fit: BoxFit.cover),
    );
  }
}
