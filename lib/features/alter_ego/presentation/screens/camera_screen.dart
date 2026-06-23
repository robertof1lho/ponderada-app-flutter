import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:image_picker/image_picker.dart';
import 'package:dio/dio.dart';
import '../../../../core/di/injection.dart';
import '../../../../core/network/api_client.dart';
import '../../../../core/auth/auth_service.dart';

class CameraScreen extends StatefulWidget {
  const CameraScreen({super.key});
  @override
  State<CameraScreen> createState() => _CameraScreenState();
}

class _CameraScreenState extends State<CameraScreen> {
  bool _uploading = false;

  Future<void> _takeSelfie() async {
    final picker = ImagePicker();
    final picked = await picker.pickImage(source: ImageSource.gallery, imageQuality: 85);
    if (picked == null || !mounted) return;

    setState(() => _uploading = true);
    try {
      final bytes = await picked.readAsBytes();
      final userId = AuthService.userId ?? 'unknown';
      final fileName = '$userId-${DateTime.now().millisecondsSinceEpoch}.jpg';

      final formData = FormData.fromMap({
        'file': MultipartFile.fromBytes(bytes, filename: fileName),
      });

      final dio = sl<ApiClient>().dio;
      final response = await dio.post('/upload/selfie', data: formData);
      final selfieUrl = response.data['url'] as String;

      if (mounted) context.push('/universe', extra: {'selfie_url': selfieUrl});
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Erro: $e')));
      }
    } finally {
      if (mounted) setState(() => _uploading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Tire uma selfie')),
      body: Center(
        child: _uploading
            ? const Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [CircularProgressIndicator(), SizedBox(height: 16), Text('Enviando...')],
              )
            : Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.camera_alt, size: 80, color: Colors.grey),
                  const SizedBox(height: 24),
                  const Text('Selecione uma foto para criar seu alter ego!', textAlign: TextAlign.center),
                  const SizedBox(height: 32),
                  FilledButton.icon(
                    onPressed: _takeSelfie,
                    icon: const Icon(Icons.photo_library),
                    label: const Text('Selecionar foto'),
                  ),
                ],
              ),
      ),
    );
  }
}
