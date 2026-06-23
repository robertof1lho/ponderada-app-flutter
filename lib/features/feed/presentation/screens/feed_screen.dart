import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:get_it/get_it.dart';
import 'package:image_picker/image_picker.dart';
import 'package:dio/dio.dart';
import '../../../../core/auth/auth_service.dart';
import '../../../../core/errors/error_handler.dart';
import '../../../../core/network/api_client.dart';
import '../blocs/feed_bloc.dart';
import '../../data/datasources/feed_remote_data_source.dart';
import '../widgets/web_camera_dialog.dart';

class FeedScreen extends StatelessWidget {
  const FeedScreen({super.key});

  void _openCreateSheet(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (_) => _CreateAlterEgoSheet(parentContext: context),
    );
  }

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (_) => FeedBloc(FeedRemoteDataSource(GetIt.I<ApiClient>().dio))..add(FeedLoadRequested()),
      child: Scaffold(
        appBar: AppBar(
          title: const Text('AlterMe'),
          actions: [
            IconButton(
              icon: const Icon(Icons.logout),
              tooltip: 'Sair',
              onPressed: () async {
                await AuthService.clear();
                if (context.mounted) context.go('/login');
              },
            ),
          ],
        ),
        body: BlocBuilder<FeedBloc, FeedState>(
          builder: (context, state) {
            if (state is FeedLoading) return const Center(child: CircularProgressIndicator());
            if (state is FeedError) return Center(child: Text('Erro: ${state.message}'));
            if (state is FeedLoaded) {
              if (state.items.isEmpty) {
                return const Center(child: Text('Nenhum alter ego ainda. Seja o primeiro!'));
              }
              return RefreshIndicator(
                onRefresh: () async => context.read<FeedBloc>().add(FeedLoadRequested()),
                child: GridView.builder(
                  padding: const EdgeInsets.all(8),
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 2,
                    mainAxisSpacing: 8,
                    crossAxisSpacing: 8,
                  ),
                  itemCount: state.items.length,
                  itemBuilder: (context, i) {
                    final item = state.items[i];
                    return ClipRRect(
                      borderRadius: BorderRadius.circular(12),
                      child: Stack(
                        fit: StackFit.expand,
                        children: [
                          CachedNetworkImage(
                            imageUrl: item.imageUrl,
                            fit: BoxFit.cover,
                            placeholder: (_, __) => const ColoredBox(color: Colors.grey),
                            errorWidget: (_, __, ___) => const Icon(Icons.broken_image),
                          ),
                          Positioned(
                            bottom: 0,
                            left: 0,
                            right: 0,
                            child: Container(
                              padding: const EdgeInsets.all(6),
                              color: Colors.black54,
                              child: Text(item.universe,
                                  style: const TextStyle(color: Colors.white, fontSize: 12)),
                            ),
                          ),
                          Positioned(
                            top: 4,
                            right: 4,
                            child: Material(
                              color: Colors.black45,
                              borderRadius: BorderRadius.circular(20),
                              child: InkWell(
                                borderRadius: BorderRadius.circular(20),
                                onTap: () async {
                                  final confirm = await showDialog<bool>(
                                    context: context,
                                    builder: (_) => AlertDialog(
                                      title: const Text('Excluir imagem'),
                                      content: const Text('Deseja excluir este alter ego?'),
                                      actions: [
                                        TextButton(
                                          onPressed: () => Navigator.pop(context, false),
                                          child: const Text('Cancelar'),
                                        ),
                                        FilledButton(
                                          style: FilledButton.styleFrom(backgroundColor: Colors.red),
                                          onPressed: () => Navigator.pop(context, true),
                                          child: const Text('Excluir'),
                                        ),
                                      ],
                                    ),
                                  );
                                  if (confirm == true && context.mounted) {
                                    try {
                                      final ds = FeedRemoteDataSource(GetIt.I<ApiClient>().dio);
                                      await ds.deleteAlterEgo(item.id);
                                      if (context.mounted) {
                                        context.read<FeedBloc>().add(FeedLoadRequested());
                                      }
                                    } catch (e) {
                                      if (context.mounted) {
                                        ScaffoldMessenger.of(context).showSnackBar(
                                          SnackBar(content: Text(friendlyError(e))),
                                        );
                                      }
                                    }
                                  }
                                },
                                child: const Padding(
                                  padding: EdgeInsets.all(6),
                                  child: Icon(Icons.delete_outline, color: Colors.white, size: 18),
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    );
                  },
                ),
              );
            }
            return const SizedBox.shrink();
          },
        ),
        floatingActionButton: Builder(
          builder: (ctx) => FloatingActionButton.extended(
            onPressed: () => _openCreateSheet(ctx),
            icon: const Icon(Icons.add_a_photo),
            label: const Text('Criar'),
          ),
        ),
      ),
    );
  }
}

class _CreateAlterEgoSheet extends StatefulWidget {
  final BuildContext parentContext;
  const _CreateAlterEgoSheet({required this.parentContext});

  @override
  State<_CreateAlterEgoSheet> createState() => _CreateAlterEgoSheetState();
}

class _CreateAlterEgoSheetState extends State<_CreateAlterEgoSheet> {
  bool _uploading = false;

  Future<void> _pickFromSource(ImageSource source) async {
    Uint8List? bytes;

    if (source == ImageSource.camera && kIsWeb) {
      bytes = await WebCameraDialog.show(context);
      if (bytes == null || !mounted) return;
    } else {
      final picker = ImagePicker();
      final picked = await picker.pickImage(source: source, imageQuality: 85);
      if (picked == null || !mounted) return;
      bytes = await picked.readAsBytes();
    }

    setState(() => _uploading = true);
    try {
      final userId = AuthService.userId ?? 'unknown';
      final fileName = '$userId-${DateTime.now().millisecondsSinceEpoch}.jpg';
      final formData = FormData.fromMap({
        'file': MultipartFile.fromBytes(bytes, filename: fileName),
      });
      final response = await GetIt.I<ApiClient>().dio.post('/upload/selfie', data: formData);
      final selfieUrl = response.data['url'] as String;

      if (mounted) {
        Navigator.of(context).pop();
        widget.parentContext.push('/universe', extra: {'selfie_url': selfieUrl});
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(friendlyError(e))));
      }
    } finally {
      if (mounted) setState(() => _uploading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(
        left: 24, right: 24, top: 24,
        bottom: MediaQuery.of(context).viewInsets.bottom + 40,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(width: 40, height: 4, decoration: BoxDecoration(
            color: Colors.grey[300], borderRadius: BorderRadius.circular(2))),
          const SizedBox(height: 24),
          const Icon(Icons.camera_alt, size: 64, color: Colors.grey),
          const SizedBox(height: 16),
          const Text('Criar Alter Ego',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          const Text(
            'De onde vem sua selfie?',
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.grey),
          ),
          const SizedBox(height: 32),
          if (_uploading)
            const Column(children: [
              CircularProgressIndicator(),
              SizedBox(height: 12),
              Text('Enviando foto...'),
            ])
          else ...[
            SizedBox(
              width: double.infinity,
              child: FilledButton.icon(
                onPressed: () => _pickFromSource(ImageSource.camera),
                icon: const Icon(Icons.camera_alt),
                label: const Text('Tirar foto com a câmera'),
              ),
            ),
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: () => _pickFromSource(ImageSource.gallery),
                icon: const Icon(Icons.photo_library),
                label: const Text('Escolher da galeria'),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
