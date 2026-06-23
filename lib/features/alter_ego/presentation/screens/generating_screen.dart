import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:go_router/go_router.dart';
import 'package:get_it/get_it.dart';
import '../blocs/alter_ego_bloc.dart';
import '../../data/datasources/alter_ego_remote_data_source.dart';
import '../../../../core/network/api_client.dart';

class GeneratingScreen extends StatefulWidget {
  final Map<String, dynamic> params;
  const GeneratingScreen({super.key, required this.params});
  @override
  State<GeneratingScreen> createState() => _GeneratingScreenState();
}

class _ShimmerBox extends StatefulWidget {
  const _ShimmerBox();
  @override
  State<_ShimmerBox> createState() => _ShimmerBoxState();
}

class _ShimmerBoxState extends State<_ShimmerBox> with SingleTickerProviderStateMixin {
  late AnimationController _ctrl;
  late Animation<double> _anim;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(vsync: this, duration: const Duration(milliseconds: 1400))..repeat();
    _anim = Tween<double>(begin: -1, end: 2).animate(CurvedAnimation(parent: _ctrl, curve: Curves.easeInOut));
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _anim,
      builder: (_, __) => Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          gradient: LinearGradient(
            begin: Alignment(_anim.value - 1, 0),
            end: Alignment(_anim.value, 0),
            colors: const [Color(0xFFDDDDDD), Color(0xFFF0F0F0), Color(0xFFDDDDDD)],
          ),
        ),
        child: const Center(
          child: Icon(Icons.auto_awesome, size: 32, color: Colors.grey),
        ),
      ),
    );
  }
}

class _GeneratingScreenState extends State<GeneratingScreen> {
  final _notifications = FlutterLocalNotificationsPlugin();

  @override
  void initState() {
    super.initState();
    _initNotifications();
  }

  Future<void> _initNotifications() async {
    const android = AndroidInitializationSettings('@mipmap/ic_launcher');
    const ios = DarwinInitializationSettings();
    await _notifications.initialize(const InitializationSettings(android: android, iOS: ios));
  }

  Future<void> _showNotification(BuildContext context) async {
    if (kIsWeb) {
      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Row(
            children: [
              Icon(Icons.auto_awesome, color: Colors.white),
              SizedBox(width: 8),
              Text('Seu alter ego ficou pronto! 🎉'),
            ],
          ),
          backgroundColor: Colors.deepPurple,
          duration: const Duration(seconds: 3),
          behavior: SnackBarBehavior.floating,
        ),
      );
      return;
    }
    const android = AndroidNotificationDetails('alter_ego', 'AlterMe',
        channelDescription: 'Notificações do AlterMe', importance: Importance.high, priority: Priority.high);
    await _notifications.show(0, 'Seu alter ego ficou pronto! 🎉', 'Toque para ver o resultado',
        const NotificationDetails(android: android));
  }

  @override
  Widget build(BuildContext context) {
    final selfieUrl = widget.params['selfie_url'] as String;
    final universe = widget.params['universe'] as String;

    return BlocProvider(
      create: (_) => AlterEgoBloc(AlterEgoRemoteDataSource(GetIt.I<ApiClient>().dio))
        ..add(GenerateRequested(selfieUrl: selfieUrl, universe: universe)),
      child: BlocListener<AlterEgoBloc, AlterEgoState>(
        listener: (context, state) async {
          final router = GoRouter.of(context);
          final messenger = ScaffoldMessenger.of(context);

          if (state is AlterEgoGenerated) {
            final extra = {
              'id': state.alterEgo.id,
              'image_url': state.alterEgo.imageUrl,
              'style_tags': state.alterEgo.styleTags,
              'selfie_url': selfieUrl,
            };
            await _showNotification(context);
            if (mounted) router.go('/result', extra: extra);
          } else if (state is AlterEgoError) {
            messenger.showSnackBar(SnackBar(content: Text(state.message)));
            router.pop();
          }
        },
        child: Scaffold(
          appBar: AppBar(title: const Text('Criando alter ego...')),
          body: SafeArea(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Side-by-side comparison — each fills half screen width
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
                                child: Image.network(
                                  selfieUrl,
                                  fit: BoxFit.cover,
                                  errorBuilder: (_, __, ___) =>
                                      const ColoredBox(color: Color(0xFFEEEEEE),
                                          child: Icon(Icons.person, size: 48, color: Colors.grey)),
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Column(
                          children: [
                            Text(universe,
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                                style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.grey)),
                            const SizedBox(height: 6),
                            ClipRRect(
                              borderRadius: BorderRadius.circular(12),
                              child: const AspectRatio(
                                aspectRatio: 3 / 4,
                                child: _ShimmerBox(),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const Spacer(),
                  const Center(child: CircularProgressIndicator(strokeWidth: 3)),
                  const SizedBox(height: 12),
                  const Center(
                    child: Text('A IA está transformando sua foto...',
                        style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold)),
                  ),
                  const SizedBox(height: 4),
                  const Center(
                    child: Text('Isso pode levar até 30 segundos',
                        style: TextStyle(color: Colors.grey, fontSize: 12)),
                  ),
                  const SizedBox(height: 16),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
