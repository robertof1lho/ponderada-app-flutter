import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:share_plus/share_plus.dart';
import 'package:get_it/get_it.dart';
import '../blocs/alter_ego_bloc.dart';
import '../../data/datasources/alter_ego_remote_data_source.dart';
import '../../../../core/network/api_client.dart';

class ResultScreen extends StatelessWidget {
  final Map<String, dynamic> params;
  const ResultScreen({super.key, required this.params});

  @override
  Widget build(BuildContext context) {
    final id = params['id'] as String;
    final imageUrl = params['image_url'] as String;
    final selfieUrl = params['selfie_url'] as String? ?? '';
    final tags = (params['style_tags'] as List<dynamic>? ?? []).cast<String>();

    return BlocProvider(
      create: (_) => AlterEgoBloc(AlterEgoRemoteDataSource(GetIt.I<ApiClient>().dio)),
      child: BlocListener<AlterEgoBloc, AlterEgoState>(
        listener: (context, state) {
          if (state is AlterEgoDeleted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('Alter ego excluído')),
            );
            context.go('/feed');
          } else if (state is AlterEgoError) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text(state.message)),
            );
          }
        },
        child: Scaffold(
          appBar: AppBar(
            title: const Text('Seu Alter Ego'),
            actions: [
              IconButton(
                icon: const Icon(Icons.home),
                onPressed: () => context.go('/feed'),
              ),
            ],
          ),
          body: SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: Column(
                        children: [
                          const Text('Original',
                              style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.grey)),
                          const SizedBox(height: 6),
                          ClipRRect(
                            borderRadius: BorderRadius.circular(12),
                            child: AspectRatio(
                              aspectRatio: 3 / 4,
                              child: selfieUrl.isNotEmpty
                                  ? Image.network(selfieUrl, fit: BoxFit.cover,
                                      errorBuilder: (_, __, ___) => const ColoredBox(
                                          color: Color(0xFFEEEEEE),
                                          child: Icon(Icons.person, size: 48, color: Colors.grey)))
                                  : const ColoredBox(color: Color(0xFFEEEEEE),
                                      child: Icon(Icons.person, size: 48, color: Colors.grey)),
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Column(
                        children: [
                          const Text('Alter Ego',
                              style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.grey)),
                          const SizedBox(height: 6),
                          ClipRRect(
                            borderRadius: BorderRadius.circular(12),
                            child: AspectRatio(
                              aspectRatio: 3 / 4,
                              child: CachedNetworkImage(
                                imageUrl: imageUrl,
                                fit: BoxFit.cover,
                                placeholder: (_, __) => const ColoredBox(
                                    color: Color(0xFFEEEEEE),
                                    child: Center(child: CircularProgressIndicator())),
                                errorWidget: (_, __, ___) => const ColoredBox(
                                    color: Color(0xFFEEEEEE),
                                    child: Icon(Icons.broken_image, size: 48)),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                Wrap(
                  spacing: 8,
                  runSpacing: 4,
                  children: tags.map((t) => Chip(label: Text(t))).toList(),
                ),
                const SizedBox(height: 24),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    BlocBuilder<AlterEgoBloc, AlterEgoState>(
                      builder: (context, state) => OutlinedButton.icon(
                        style: OutlinedButton.styleFrom(foregroundColor: Colors.red),
                        onPressed: state is AlterEgoGenerating
                            ? null
                            : () async {
                                final confirm = await showDialog<bool>(
                                  context: context,
                                  builder: (_) => AlertDialog(
                                    title: const Text('Excluir alter ego'),
                                    content: const Text('Tem certeza que deseja excluir esta imagem?'),
                                    actions: [
                                      TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancelar')),
                                      FilledButton(
                                        style: FilledButton.styleFrom(backgroundColor: Colors.red),
                                        onPressed: () => Navigator.pop(context, true),
                                        child: const Text('Excluir'),
                                      ),
                                    ],
                                  ),
                                );
                                if (confirm == true && context.mounted) {
                                  context.read<AlterEgoBloc>().add(DeleteRequested(id));
                                }
                              },
                        icon: const Icon(Icons.delete_outline),
                        label: const Text('Excluir'),
                      ),
                    ),
                    OutlinedButton.icon(
                      onPressed: () => Share.share('Veja meu alter ego gerado pela IA! $imageUrl'),
                      icon: const Icon(Icons.share),
                      label: const Text('Compartilhar'),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                OutlinedButton(
                  onPressed: () => context.go('/feed'),
                  child: const Text('Ver minhas criações'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
