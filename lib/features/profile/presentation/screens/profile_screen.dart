import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:get_it/get_it.dart';
import '../blocs/profile_bloc.dart';
import '../../data/datasources/profile_remote_data_source.dart';
import '../../../../core/network/api_client.dart';

class ProfileScreen extends StatelessWidget {
  final String userId;
  const ProfileScreen({super.key, required this.userId});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (_) => ProfileBloc(ProfileRemoteDataSource(GetIt.I<ApiClient>().dio))
        ..add(ProfileLoadRequested(userId)),
      child: Scaffold(
        appBar: AppBar(title: const Text('Usuários semelhantes')),
        body: BlocBuilder<ProfileBloc, ProfileState>(
          builder: (context, state) {
            if (state is ProfileLoading) return const Center(child: CircularProgressIndicator());
            if (state is ProfileError) return Center(child: Text('Erro: ${state.message}'));
            if (state is ProfileLoaded) {
              if (state.users.isEmpty) {
                return const Center(
                  child: Text('Nenhum usuário com estilo semelhante ainda.\nCrie mais alter egos!',
                      textAlign: TextAlign.center),
                );
              }
              return ListView.builder(
                itemCount: state.users.length,
                itemBuilder: (context, i) {
                  final u = state.users[i];
                  return ListTile(
                    leading: const CircleAvatar(child: Icon(Icons.person)),
                    title: Text(u.userId),
                    subtitle: Text('${u.sharedStyles} estilos em comum'),
                    trailing: const Icon(Icons.chevron_right),
                  );
                },
              );
            }
            return const SizedBox.shrink();
          },
        ),
      ),
    );
  }
}
