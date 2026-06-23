import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class UniverseSelectorScreen extends StatelessWidget {
  const UniverseSelectorScreen({super.key});

  static const _universes = [
    {'key': 'anime', 'label': 'Anime', 'emoji': '⛩️', 'desc': 'Herói de manga japonês'},
    {'key': 'medieval', 'label': 'Medieval', 'emoji': '⚔️', 'desc': 'Cavaleiro ou mago'},
    {'key': 'sci-fi', 'label': 'Sci-Fi', 'emoji': '🚀', 'desc': 'Ser do futuro'},
    {'key': 'politico_br', 'label': 'Político BR', 'emoji': '🏛️', 'desc': 'Político brasileiro'},
  ];

  @override
  Widget build(BuildContext context) {
    final extra = GoRouterState.of(context).extra as Map<String, dynamic>;
    final selfieUrl = extra['selfie_url'] as String;

    return Scaffold(
      appBar: AppBar(title: const Text('Escolha o universo')),
      body: ListView.separated(
        padding: const EdgeInsets.all(16),
        itemCount: _universes.length,
        separatorBuilder: (_, __) => const SizedBox(height: 12),
        itemBuilder: (context, i) {
          final u = _universes[i];
          return Card(
            child: ListTile(
              leading: Text(u['emoji']!, style: const TextStyle(fontSize: 36)),
              title: Text(u['label']!, style: const TextStyle(fontWeight: FontWeight.bold)),
              subtitle: Text(u['desc']!),
              trailing: const Icon(Icons.chevron_right),
              onTap: () => context.push('/generating', extra: {
                'selfie_url': selfieUrl,
                'universe': u['key'],
              }),
            ),
          );
        },
      ),
    );
  }
}
