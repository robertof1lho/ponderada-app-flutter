import 'dart:async';
import 'dart:convert';
// ignore: avoid_web_libraries_in_flutter
import 'dart:html' as html;
import 'dart:typed_data';
import 'dart:ui_web' as ui_web;

import 'package:flutter/material.dart';

class WebCameraDialog extends StatefulWidget {
  const WebCameraDialog({super.key});

  /// Returns raw JPEG bytes, or null if cancelled.
  static Future<Uint8List?> show(BuildContext context) {
    return showDialog<Uint8List>(
      context: context,
      barrierDismissible: false,
      builder: (_) => const WebCameraDialog(),
    );
  }

  @override
  State<WebCameraDialog> createState() => _WebCameraDialogState();
}

class _WebCameraDialogState extends State<WebCameraDialog> {
  html.VideoElement? _video;
  html.MediaStream? _stream;
  String? _viewId;
  bool _ready = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _startCamera();
  }

  Future<void> _startCamera() async {
    try {
      final stream = await html.window.navigator.mediaDevices!
          .getUserMedia({'video': true, 'audio': false});
      _stream = stream;

      final video = html.VideoElement()
        ..srcObject = stream
        ..autoplay = true
        ..style.width = '100%'
        ..style.height = '100%'
        ..style.objectFit = 'cover';

      final viewId = 'camera-${DateTime.now().millisecondsSinceEpoch}';
      ui_web.platformViewRegistry.registerViewFactory(viewId, (_) => video);

      setState(() {
        _video = video;
        _viewId = viewId;
        _ready = true;
      });
    } catch (e) {
      setState(() => _error = 'Câmera não disponível.\nVerifique as permissões do navegador.');
    }
  }

  Future<void> _capture() async {
    final video = _video;
    if (video == null) return;

    final canvas = html.CanvasElement(width: video.videoWidth, height: video.videoHeight);
    canvas.context2D.drawImage(video, 0, 0);
    final dataUrl = canvas.toDataUrl('image/jpeg', 0.85);

    final base64str = dataUrl.split(',').last;
    final bytes = base64Decode(base64str);

    _stopStream();
    if (mounted) Navigator.of(context).pop(bytes);
  }

  void _stopStream() {
    _stream?.getTracks().forEach((t) => t.stop());
  }

  @override
  void dispose() {
    _stopStream();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: SizedBox(
        width: 360,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const SizedBox(height: 16),
            const Text('Tirar foto', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            ClipRRect(
              borderRadius: BorderRadius.circular(12),
              child: SizedBox(
                width: 320,
                height: 240,
                child: _error != null
                    ? Center(
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Text(_error!,
                              textAlign: TextAlign.center,
                              style: const TextStyle(color: Colors.red)),
                        ),
                      )
                    : _ready && _viewId != null
                        ? HtmlElementView(viewType: _viewId!)
                        : const Center(child: CircularProgressIndicator()),
              ),
            ),
            const SizedBox(height: 16),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: () {
                        _stopStream();
                        Navigator.of(context).pop(null);
                      },
                      child: const Text('Cancelar'),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: FilledButton.icon(
                      onPressed: _ready ? _capture : null,
                      icon: const Icon(Icons.camera),
                      label: const Text('Capturar'),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }
}
