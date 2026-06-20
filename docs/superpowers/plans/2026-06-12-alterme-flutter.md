# AlterMe Flutter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the AlterMe Flutter app with 7 screens, camera selfie capture, AI alter ego generation, community feed, notifications, and sharing — consuming the AlterMe FastAPI backend.

**Architecture:** Clean architecture per feature (data/domain/presentation). BLoC for state management. Dependency injection via get_it. go_router for navigation. Dio for HTTP.

**Tech Stack:** Flutter, flutter_bloc, go_router, get_it, dio, supabase_flutter, camera, share_plus, flutter_local_notifications, mocktail, bloc_test

**Prerequisite:** Backend running at http://localhost:8000 (or deployed URL). Supabase project created with profiles/alter_egos/likes tables and alter-egos storage bucket.

---

## File Map

```
lib/
├── core/
│   ├── di/injection.dart              # get_it service locator setup
│   ├── errors/failures.dart           # Failure classes
│   ├── network/api_client.dart        # Dio wrapper with auth header
│   └── router/app_router.dart         # go_router routes
├── features/
│   ├── auth/
│   │   ├── data/supabase_auth_data_source.dart
│   │   ├── domain/auth_repository.dart       # abstract
│   │   ├── domain/usecases/login_usecase.dart
│   │   ├── domain/usecases/register_usecase.dart
│   │   ├── presentation/bloc/auth_bloc.dart
│   │   ├── presentation/login_screen.dart
│   │   └── presentation/register_screen.dart
│   ├── alter_ego/
│   │   ├── data/alter_ego_remote_data_source.dart
│   │   ├── domain/alter_ego_repository.dart   # abstract
│   │   ├── domain/usecases/generate_alter_ego_usecase.dart
│   │   ├── presentation/bloc/alter_ego_bloc.dart
│   │   ├── presentation/camera_screen.dart
│   │   ├── presentation/universe_selector_screen.dart
│   │   ├── presentation/generating_screen.dart
│   │   └── presentation/result_screen.dart
│   ├── feed/
│   │   ├── data/feed_remote_data_source.dart
│   │   ├── domain/feed_repository.dart         # abstract
│   │   ├── domain/usecases/get_feed_usecase.dart
│   │   ├── presentation/bloc/feed_bloc.dart
│   │   └── presentation/home_screen.dart
│   └── profile/
│       ├── data/profile_remote_data_source.dart
│       ├── domain/profile_repository.dart      # abstract
│       ├── domain/usecases/get_similar_users_usecase.dart
│       ├── presentation/bloc/profile_bloc.dart
│       └── presentation/profile_screen.dart
└── main.dart
```

---

## Task 1: Project Setup

**Files:**
- Modify: `pubspec.yaml`
- Create: `lib/main.dart`
- Create: `lib/core/di/injection.dart`
- Create: `lib/core/router/app_router.dart`

- [ ] **Step 1: Create Flutter project**

```bash
flutter create --org com.alterme --project-name alter_me .
```

- [ ] **Step 2: Write pubspec.yaml dependencies**

```yaml
dependencies:
  flutter:
    sdk: flutter
  flutter_bloc: ^8.1.5
  go_router: ^13.2.1
  get_it: ^7.7.0
  dio: ^5.4.3
  supabase_flutter: ^2.5.0
  camera: ^0.10.5+9
  share_plus: ^9.0.0
  flutter_local_notifications: ^17.1.2
  cached_network_image: ^3.3.1
  image_picker: ^1.1.1

dev_dependencies:
  flutter_test:
    sdk: flutter
  bloc_test: ^9.1.7
  mocktail: ^1.0.4
```

Run:
```bash
flutter pub get
```

- [ ] **Step 3: Write lib/main.dart**

```dart
import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'core/di/injection.dart';
import 'core/router/app_router.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await Supabase.initialize(
    url: const String.fromEnvironment('SUPABASE_URL'),
    anonKey: const String.fromEnvironment('SUPABASE_ANON_KEY'),
  );

  setupDependencies();
  runApp(const AlterMeApp());
}

class AlterMeApp extends StatelessWidget {
  const AlterMeApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'AlterMe',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF6C63FF)),
        useMaterial3: true,
      ),
      routerConfig: AppRouter.router,
    );
  }
}
```

- [ ] **Step 4: Write lib/core/di/injection.dart (skeleton — will be filled per feature)**

```dart
import 'package:get_it/get_it.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../network/api_client.dart';

final sl = GetIt.instance;

void setupDependencies() {
  sl.registerLazySingleton(() => Supabase.instance.client);
  sl.registerLazySingleton(() => ApiClient(supabase: sl()));
}
```

- [ ] **Step 5: Write lib/core/router/app_router.dart (skeleton)**

```dart
import 'package:go_router/go_router.dart';
import '../../features/auth/presentation/login_screen.dart';
import '../../features/auth/presentation/register_screen.dart';
import '../../features/feed/presentation/home_screen.dart';
import '../../features/alter_ego/presentation/camera_screen.dart';
import '../../features/alter_ego/presentation/universe_selector_screen.dart';
import '../../features/alter_ego/presentation/generating_screen.dart';
import '../../features/alter_ego/presentation/result_screen.dart';
import '../../features/profile/presentation/profile_screen.dart';

class AppRouter {
  static final router = GoRouter(
    initialLocation: '/login',
    routes: [
      GoRoute(path: '/login',     builder: (_, __) => const LoginScreen()),
      GoRoute(path: '/register',  builder: (_, __) => const RegisterScreen()),
      GoRoute(path: '/home',      builder: (_, __) => const HomeScreen()),
      GoRoute(path: '/camera',    builder: (_, __) => const CameraScreen()),
      GoRoute(path: '/universe',  builder: (context, state) => UniverseSelectorScreen(selfieUrl: state.extra as String)),
      GoRoute(path: '/generating',builder: (context, state) => GeneratingScreen(args: state.extra as Map<String, String>)),
      GoRoute(path: '/result',    builder: (context, state) => ResultScreen(imageUrl: state.extra as String)),
      GoRoute(path: '/profile',   builder: (_, __) => const ProfileScreen()),
    ],
  );
}
```

- [ ] **Step 6: Write lib/core/network/api_client.dart**

```dart
import 'package:dio/dio.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class ApiClient {
  final SupabaseClient supabase;
  late final Dio _dio;

  static const _baseUrl = String.fromEnvironment('API_URL', defaultValue: 'http://10.0.2.2:8000');

  ApiClient({required this.supabase}) {
    _dio = Dio(BaseOptions(baseUrl: _baseUrl))
      ..interceptors.add(InterceptorsWrapper(
        onRequest: (options, handler) {
          final token = supabase.auth.currentSession?.accessToken;
          if (token != null) options.headers['Authorization'] = 'Bearer $token';
          handler.next(options);
        },
      ));
  }

  Dio get dio => _dio;
}
```

- [ ] **Step 7: Write lib/core/errors/failures.dart**

```dart
abstract class Failure {
  final String message;
  const Failure(this.message);
}

class NetworkFailure extends Failure {
  const NetworkFailure(super.message);
}

class AuthFailure extends Failure {
  const AuthFailure(super.message);
}

class GenerationFailure extends Failure {
  const GenerationFailure(super.message);
}

class UnknownFailure extends Failure {
  const UnknownFailure(super.message);
}
```

- [ ] **Step 8: Verify the app builds**

```bash
flutter build apk --debug --dart-define=SUPABASE_URL=https://x.supabase.co --dart-define=SUPABASE_ANON_KEY=x
```
Expected: BUILD SUCCESSFUL

- [ ] **Step 9: Commit**

```bash
git add lib/ pubspec.yaml pubspec.lock
git commit -m "feat: scaffold Flutter project with DI, router and core"
```

---

## Task 2: Auth Feature

**Files:**
- Create: `lib/features/auth/data/supabase_auth_data_source.dart`
- Create: `lib/features/auth/domain/auth_repository.dart`
- Create: `lib/features/auth/domain/usecases/login_usecase.dart`
- Create: `lib/features/auth/domain/usecases/register_usecase.dart`
- Create: `lib/features/auth/presentation/bloc/auth_bloc.dart`
- Create: `lib/features/auth/presentation/login_screen.dart`
- Create: `lib/features/auth/presentation/register_screen.dart`
- Create: `test/features/auth/auth_bloc_test.dart`

- [ ] **Step 1: Write failing test**

```dart
// test/features/auth/auth_bloc_test.dart
import 'package:bloc_test/bloc_test.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:alter_me/features/auth/domain/auth_repository.dart';
import 'package:alter_me/features/auth/presentation/bloc/auth_bloc.dart';

class MockAuthRepository extends Mock implements AuthRepository {}

void main() {
  late MockAuthRepository mockRepo;

  setUp(() {
    mockRepo = MockAuthRepository();
  });

  blocTest<AuthBloc, AuthState>(
    'emits [AuthLoading, AuthAuthenticated] when login succeeds',
    build: () {
      when(() => mockRepo.login(email: any(named: 'email'), password: any(named: 'password')))
          .thenAnswer((_) async => 'user-id-123');
      return AuthBloc(repository: mockRepo);
    },
    act: (bloc) => bloc.add(LoginRequested(email: 'a@b.com', password: '123456')),
    expect: () => [isA<AuthLoading>(), isA<AuthAuthenticated>()],
  );

  blocTest<AuthBloc, AuthState>(
    'emits [AuthLoading, AuthError] when login fails',
    build: () {
      when(() => mockRepo.login(email: any(named: 'email'), password: any(named: 'password')))
          .thenThrow(Exception('Invalid credentials'));
      return AuthBloc(repository: mockRepo);
    },
    act: (bloc) => bloc.add(LoginRequested(email: 'a@b.com', password: 'wrong')),
    expect: () => [isA<AuthLoading>(), isA<AuthError>()],
  );
}
```

- [ ] **Step 2: Run to verify it fails**

```bash
flutter test test/features/auth/auth_bloc_test.dart
```

- [ ] **Step 3: Write domain/auth_repository.dart**

```dart
abstract class AuthRepository {
  Future<String> login({required String email, required String password});
  Future<void> register({required String email, required String password, required String username});
  Future<void> logout();
  String? get currentUserId;
}
```

- [ ] **Step 4: Write presentation/bloc/auth_bloc.dart**

```dart
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../domain/auth_repository.dart';

// Events
abstract class AuthEvent {}
class LoginRequested extends AuthEvent {
  final String email, password;
  LoginRequested({required this.email, required this.password});
}
class RegisterRequested extends AuthEvent {
  final String email, password, username;
  RegisterRequested({required this.email, required this.password, required this.username});
}
class LogoutRequested extends AuthEvent {}

// States
abstract class AuthState {}
class AuthInitial extends AuthState {}
class AuthLoading extends AuthState {}
class AuthAuthenticated extends AuthState { final String userId; AuthAuthenticated(this.userId); }
class AuthError extends AuthState { final String message; AuthError(this.message); }

class AuthBloc extends Bloc<AuthEvent, AuthState> {
  final AuthRepository repository;

  AuthBloc({required this.repository}) : super(AuthInitial()) {
    on<LoginRequested>(_onLogin);
    on<RegisterRequested>(_onRegister);
    on<LogoutRequested>(_onLogout);
  }

  Future<void> _onLogin(LoginRequested event, Emitter<AuthState> emit) async {
    emit(AuthLoading());
    try {
      final userId = await repository.login(email: event.email, password: event.password);
      emit(AuthAuthenticated(userId));
    } catch (e) {
      emit(AuthError(e.toString()));
    }
  }

  Future<void> _onRegister(RegisterRequested event, Emitter<AuthState> emit) async {
    emit(AuthLoading());
    try {
      await repository.register(email: event.email, password: event.password, username: event.username);
      final userId = await repository.login(email: event.email, password: event.password);
      emit(AuthAuthenticated(userId));
    } catch (e) {
      emit(AuthError(e.toString()));
    }
  }

  Future<void> _onLogout(LogoutRequested event, Emitter<AuthState> emit) async {
    await repository.logout();
    emit(AuthInitial());
  }
}
```

- [ ] **Step 5: Write data/supabase_auth_data_source.dart**

```dart
import 'package:supabase_flutter/supabase_flutter.dart';
import '../domain/auth_repository.dart';

class SupabaseAuthDataSource implements AuthRepository {
  final SupabaseClient _client;
  SupabaseAuthDataSource(this._client);

  @override
  Future<String> login({required String email, required String password}) async {
    final res = await _client.auth.signInWithPassword(email: email, password: password);
    if (res.user == null) throw Exception('Login failed');
    return res.user!.id;
  }

  @override
  Future<void> register({required String email, required String password, required String username}) async {
    final res = await _client.auth.signUp(email: email, password: password);
    if (res.user == null) throw Exception('Registration failed');
    await _client.from('profiles').insert({'id': res.user!.id, 'username': username});
  }

  @override
  Future<void> logout() => _client.auth.signOut();

  @override
  String? get currentUserId => _client.auth.currentUser?.id;
}
```

- [ ] **Step 6: Write login_screen.dart**

```dart
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/di/injection.dart';
import '../bloc/auth_bloc.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});
  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _emailCtrl = TextEditingController();
  final _passwordCtrl = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (_) => sl<AuthBloc>(),
      child: BlocConsumer<AuthBloc, AuthState>(
        listener: (context, state) {
          if (state is AuthAuthenticated) context.go('/home');
          if (state is AuthError) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(state.message)));
        },
        builder: (context, state) => Scaffold(
          body: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text('AlterMe', style: Theme.of(context).textTheme.headlineLarge),
                const SizedBox(height: 32),
                TextField(controller: _emailCtrl, decoration: const InputDecoration(labelText: 'Email')),
                const SizedBox(height: 16),
                TextField(controller: _passwordCtrl, obscureText: true, decoration: const InputDecoration(labelText: 'Senha')),
                const SizedBox(height: 24),
                if (state is AuthLoading)
                  const CircularProgressIndicator()
                else
                  FilledButton(
                    onPressed: () => context.read<AuthBloc>().add(
                      LoginRequested(email: _emailCtrl.text, password: _passwordCtrl.text),
                    ),
                    child: const Text('Entrar'),
                  ),
                TextButton(onPressed: () => context.go('/register'), child: const Text('Criar conta')),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
```

- [ ] **Step 7: Write register_screen.dart**

```dart
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/di/injection.dart';
import '../bloc/auth_bloc.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});
  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _emailCtrl = TextEditingController();
  final _passwordCtrl = TextEditingController();
  final _usernameCtrl = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (_) => sl<AuthBloc>(),
      child: BlocConsumer<AuthBloc, AuthState>(
        listener: (context, state) {
          if (state is AuthAuthenticated) context.go('/home');
          if (state is AuthError) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(state.message)));
        },
        builder: (context, state) => Scaffold(
          appBar: AppBar(title: const Text('Criar conta')),
          body: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              children: [
                TextField(controller: _usernameCtrl, decoration: const InputDecoration(labelText: 'Username')),
                const SizedBox(height: 16),
                TextField(controller: _emailCtrl, decoration: const InputDecoration(labelText: 'Email')),
                const SizedBox(height: 16),
                TextField(controller: _passwordCtrl, obscureText: true, decoration: const InputDecoration(labelText: 'Senha')),
                const SizedBox(height: 24),
                if (state is AuthLoading)
                  const CircularProgressIndicator()
                else
                  FilledButton(
                    onPressed: () => context.read<AuthBloc>().add(RegisterRequested(
                      email: _emailCtrl.text,
                      password: _passwordCtrl.text,
                      username: _usernameCtrl.text,
                    )),
                    child: const Text('Cadastrar'),
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
```

- [ ] **Step 8: Register auth in injection.dart**

Add to `setupDependencies()`:
```dart
// Auth
sl.registerLazySingleton<AuthRepository>(() => SupabaseAuthDataSource(sl()));
sl.registerFactory(() => AuthBloc(repository: sl()));
```

- [ ] **Step 9: Run tests**

```bash
flutter test test/features/auth/auth_bloc_test.dart
```
Expected: PASS

- [ ] **Step 10: Commit**

```bash
git add lib/features/auth/ test/features/auth/ lib/core/
git commit -m "feat: add auth feature (login, register, BLoC)"
```

---

## Task 3: Alter Ego Feature — Camera to Generation

**Files:**
- Create: `lib/features/alter_ego/data/alter_ego_remote_data_source.dart`
- Create: `lib/features/alter_ego/domain/alter_ego_repository.dart`
- Create: `lib/features/alter_ego/domain/usecases/generate_alter_ego_usecase.dart`
- Create: `lib/features/alter_ego/presentation/bloc/alter_ego_bloc.dart`
- Create: `lib/features/alter_ego/presentation/camera_screen.dart`
- Create: `lib/features/alter_ego/presentation/universe_selector_screen.dart`
- Create: `lib/features/alter_ego/presentation/generating_screen.dart`
- Create: `test/features/alter_ego/alter_ego_bloc_test.dart`

- [ ] **Step 1: Write failing test**

```dart
// test/features/alter_ego/alter_ego_bloc_test.dart
import 'package:bloc_test/bloc_test.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:alter_me/features/alter_ego/domain/alter_ego_repository.dart';
import 'package:alter_me/features/alter_ego/presentation/bloc/alter_ego_bloc.dart';

class MockAlterEgoRepository extends Mock implements AlterEgoRepository {}

void main() {
  late MockAlterEgoRepository mockRepo;

  setUp(() { mockRepo = MockAlterEgoRepository(); });

  blocTest<AlterEgoBloc, AlterEgoState>(
    'emits [AlterEgoGenerating, AlterEgoGenerated] on success',
    build: () {
      when(() => mockRepo.generate(
        selfieUrl: any(named: 'selfieUrl'),
        universe: any(named: 'universe'),
        userId: any(named: 'userId'),
      )).thenAnswer((_) async => 'https://example.com/result.png');
      return AlterEgoBloc(repository: mockRepo);
    },
    act: (bloc) => bloc.add(GenerateRequested(
      selfieUrl: 'https://example.com/selfie.png',
      universe: 'anime',
      userId: 'user-1',
    )),
    expect: () => [isA<AlterEgoGenerating>(), isA<AlterEgoGenerated>()],
  );
}
```

- [ ] **Step 2: Run to verify it fails**

```bash
flutter test test/features/alter_ego/alter_ego_bloc_test.dart
```

- [ ] **Step 3: Write domain/alter_ego_repository.dart**

```dart
abstract class AlterEgoRepository {
  Future<String> generate({
    required String selfieUrl,
    required String universe,
    required String userId,
  });
  Future<void> like({required String alterEgoId, required String userId});
}
```

- [ ] **Step 4: Write presentation/bloc/alter_ego_bloc.dart**

```dart
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../domain/alter_ego_repository.dart';

abstract class AlterEgoEvent {}
class GenerateRequested extends AlterEgoEvent {
  final String selfieUrl, universe, userId;
  GenerateRequested({required this.selfieUrl, required this.universe, required this.userId});
}
class LikeRequested extends AlterEgoEvent {
  final String alterEgoId, userId;
  LikeRequested({required this.alterEgoId, required this.userId});
}

abstract class AlterEgoState {}
class AlterEgoInitial extends AlterEgoState {}
class AlterEgoGenerating extends AlterEgoState {}
class AlterEgoGenerated extends AlterEgoState {
  final String imageUrl;
  AlterEgoGenerated(this.imageUrl);
}
class AlterEgoError extends AlterEgoState {
  final String message;
  AlterEgoError(this.message);
}

class AlterEgoBloc extends Bloc<AlterEgoEvent, AlterEgoState> {
  final AlterEgoRepository repository;
  AlterEgoBloc({required this.repository}) : super(AlterEgoInitial()) {
    on<GenerateRequested>(_onGenerate);
    on<LikeRequested>(_onLike);
  }

  Future<void> _onGenerate(GenerateRequested event, Emitter<AlterEgoState> emit) async {
    emit(AlterEgoGenerating());
    try {
      final imageUrl = await repository.generate(
        selfieUrl: event.selfieUrl,
        universe: event.universe,
        userId: event.userId,
      );
      emit(AlterEgoGenerated(imageUrl));
    } catch (e) {
      emit(AlterEgoError(e.toString()));
    }
  }

  Future<void> _onLike(LikeRequested event, Emitter<AlterEgoState> emit) async {
    await repository.like(alterEgoId: event.alterEgoId, userId: event.userId);
  }
}
```

- [ ] **Step 5: Write data/alter_ego_remote_data_source.dart**

```dart
import 'package:supabase_flutter/supabase_flutter.dart';
import '../domain/alter_ego_repository.dart';
import '../../../../core/network/api_client.dart';

class AlterEgoRemoteDataSource implements AlterEgoRepository {
  final ApiClient _apiClient;
  final SupabaseClient _supabase;

  AlterEgoRemoteDataSource({required ApiClient apiClient, required SupabaseClient supabase})
      : _apiClient = apiClient, _supabase = supabase;

  @override
  Future<String> generate({required String selfieUrl, required String universe, required String userId}) async {
    final response = await _apiClient.dio.post('/alter-ego/generate', data: {
      'selfie_url': selfieUrl,
      'universe': universe,
      'user_id': userId,
    });
    return response.data['image_url'] as String;
  }

  @override
  Future<void> like({required String alterEgoId, required String userId}) async {
    await _apiClient.dio.post('/alter-ego/$alterEgoId/like', data: {'user_id': userId});
  }
}
```

- [ ] **Step 6: Write camera_screen.dart**

```dart
import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class CameraScreen extends StatefulWidget {
  const CameraScreen({super.key});
  @override
  State<CameraScreen> createState() => _CameraScreenState();
}

class _CameraScreenState extends State<CameraScreen> {
  CameraController? _controller;
  bool _uploading = false;

  @override
  void initState() {
    super.initState();
    _initCamera();
  }

  Future<void> _initCamera() async {
    final cameras = await availableCameras();
    final front = cameras.firstWhere((c) => c.lensDirection == CameraLensDirection.front, orElse: () => cameras.first);
    _controller = CameraController(front, ResolutionPreset.medium);
    await _controller!.initialize();
    if (mounted) setState(() {});
  }

  Future<void> _takeSelfie() async {
    if (_controller == null || !_controller!.value.isInitialized) return;
    setState(() => _uploading = true);
    final file = await _controller!.takePicture();
    final bytes = await file.readAsBytes();
    final path = 'selfies/${DateTime.now().millisecondsSinceEpoch}.jpg';
    await Supabase.instance.client.storage.from('alter-egos').uploadBinary(path, bytes);
    final selfieUrl = Supabase.instance.client.storage.from('alter-egos').getPublicUrl(path);
    if (mounted) context.push('/universe', extra: selfieUrl);
  }

  @override
  void dispose() {
    _controller?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_controller == null || !_controller!.value.isInitialized) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    return Scaffold(
      body: Stack(
        children: [
          CameraPreview(_controller!),
          Positioned(
            bottom: 40,
            left: 0, right: 0,
            child: Center(
              child: _uploading
                  ? const CircularProgressIndicator(color: Colors.white)
                  : FloatingActionButton.large(
                      onPressed: _takeSelfie,
                      child: const Icon(Icons.camera_alt),
                    ),
            ),
          ),
        ],
      ),
    );
  }
}
```

- [ ] **Step 7: Write universe_selector_screen.dart**

```dart
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

const _universes = ['Anime', 'Medieval', 'Sci-Fi', 'Político BR'];

class UniverseSelectorScreen extends StatelessWidget {
  final String selfieUrl;
  const UniverseSelectorScreen({super.key, required this.selfieUrl});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Escolha seu universo')),
      body: ListView.separated(
        padding: const EdgeInsets.all(24),
        itemCount: _universes.length,
        separatorBuilder: (_, __) => const SizedBox(height: 12),
        itemBuilder: (context, i) => FilledButton(
          onPressed: () => context.push('/generating', extra: {
            'selfieUrl': selfieUrl,
            'universe': _universes[i],
          }),
          child: Text(_universes[i]),
        ),
      ),
    );
  }
}
```

- [ ] **Step 8: Write generating_screen.dart (triggers generation + notification)**

```dart
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:go_router/go_router.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../../../../core/di/injection.dart';
import '../bloc/alter_ego_bloc.dart';

final _notificationsPlugin = FlutterLocalNotificationsPlugin();

Future<void> _initNotifications() async {
  const androidSettings = AndroidInitializationSettings('@mipmap/ic_launcher');
  const iosSettings = DarwinInitializationSettings();
  await _notificationsPlugin.initialize(
    const InitializationSettings(android: androidSettings, iOS: iosSettings),
  );
}

Future<void> _showDoneNotification() async {
  await _notificationsPlugin.show(
    0,
    'AlterMe',
    'Seu alter ego ficou pronto! 🎨',
    const NotificationDetails(
      android: AndroidNotificationDetails('alterme', 'AlterMe', importance: Importance.high),
      iOS: DarwinNotificationDetails(),
    ),
  );
}

class GeneratingScreen extends StatefulWidget {
  final Map<String, String> args;
  const GeneratingScreen({super.key, required this.args});
  @override
  State<GeneratingScreen> createState() => _GeneratingScreenState();
}

class _GeneratingScreenState extends State<GeneratingScreen> {
  @override
  void initState() {
    super.initState();
    _initNotifications();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final userId = Supabase.instance.client.auth.currentUser!.id;
      context.read<AlterEgoBloc>().add(GenerateRequested(
        selfieUrl: widget.args['selfieUrl']!,
        universe: widget.args['universe']!,
        userId: userId,
      ));
    });
  }

  @override
  Widget build(BuildContext context) {
    return BlocListener<AlterEgoBloc, AlterEgoState>(
      listener: (context, state) async {
        if (state is AlterEgoGenerated) {
          await _showDoneNotification();
          if (context.mounted) context.pushReplacement('/result', extra: state.imageUrl);
        }
        if (state is AlterEgoError) {
          if (context.mounted) {
            ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(state.message)));
            context.pop();
          }
        }
      },
      child: Scaffold(
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const CircularProgressIndicator(),
              const SizedBox(height: 24),
              Text('Gerando seu alter ego...', style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: 8),
              Text('universo: ${widget.args['universe']}', style: Theme.of(context).textTheme.bodySmall),
            ],
          ),
        ),
      ),
    );
  }
}
```

- [ ] **Step 9: Register alter ego in injection.dart**

Add to `setupDependencies()`:
```dart
// AlterEgo
sl.registerLazySingleton<AlterEgoRepository>(() => AlterEgoRemoteDataSource(apiClient: sl(), supabase: sl()));
sl.registerFactory(() => AlterEgoBloc(repository: sl()));
```

- [ ] **Step 10: Run tests**

```bash
flutter test test/features/alter_ego/alter_ego_bloc_test.dart
```
Expected: PASS

- [ ] **Step 11: Commit**

```bash
git add lib/features/alter_ego/ test/features/alter_ego/
git commit -m "feat: add alter ego feature (camera, universe, generating, BLoC)"
```

---

## Task 4: Result Screen (Share)

**Files:**
- Create: `lib/features/alter_ego/presentation/result_screen.dart`

- [ ] **Step 1: Write result_screen.dart**

```dart
import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:share_plus/share_plus.dart';

class ResultScreen extends StatelessWidget {
  final String imageUrl;
  const ResultScreen({super.key, required this.imageUrl});

  Future<void> _share() async {
    await Share.share(
      'Esse é meu alter ego no AlterMe 🤖\n$imageUrl',
      subject: 'Meu Alter Ego',
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Seu Alter Ego'), automaticallyImplyLeading: false),
      body: Column(
        children: [
          Expanded(
            child: CachedNetworkImage(
              imageUrl: imageUrl,
              fit: BoxFit.contain,
              placeholder: (_, __) => const Center(child: CircularProgressIndicator()),
              errorWidget: (_, __, ___) => const Icon(Icons.error),
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(24),
            child: Row(
              children: [
                Expanded(
                  child: FilledButton.icon(
                    onPressed: _share,
                    icon: const Icon(Icons.share),
                    label: const Text('Compartilhar'),
                  ),
                ),
                const SizedBox(width: 12),
                OutlinedButton(
                  onPressed: () => context.go('/home'),
                  child: const Text('Ver feed'),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add lib/features/alter_ego/presentation/result_screen.dart
git commit -m "feat: add result screen with share_plus"
```

---

## Task 5: Feed Feature

**Files:**
- Create: `lib/features/feed/data/feed_remote_data_source.dart`
- Create: `lib/features/feed/domain/feed_repository.dart`
- Create: `lib/features/feed/presentation/bloc/feed_bloc.dart`
- Create: `lib/features/feed/presentation/home_screen.dart`
- Create: `test/features/feed/feed_bloc_test.dart`

- [ ] **Step 1: Write failing test**

```dart
// test/features/feed/feed_bloc_test.dart
import 'package:bloc_test/bloc_test.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:alter_me/features/feed/domain/feed_repository.dart';
import 'package:alter_me/features/feed/presentation/bloc/feed_bloc.dart';

class MockFeedRepository extends Mock implements FeedRepository {}

void main() {
  late MockFeedRepository mockRepo;
  setUp(() { mockRepo = MockFeedRepository(); });

  blocTest<FeedBloc, FeedState>(
    'emits [FeedLoading, FeedLoaded] on success',
    build: () {
      when(() => mockRepo.getFeed(limit: any(named: 'limit'), offset: any(named: 'offset')))
          .thenAnswer((_) async => []);
      return FeedBloc(repository: mockRepo);
    },
    act: (bloc) => bloc.add(LoadFeed()),
    expect: () => [isA<FeedLoading>(), isA<FeedLoaded>()],
  );
}
```

- [ ] **Step 2: Run to verify it fails**

```bash
flutter test test/features/feed/feed_bloc_test.dart
```

- [ ] **Step 3: Write domain/feed_repository.dart**

```dart
abstract class FeedRepository {
  Future<List<Map<String, dynamic>>> getFeed({int limit = 20, int offset = 0});
}
```

- [ ] **Step 4: Write presentation/bloc/feed_bloc.dart**

```dart
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../domain/feed_repository.dart';

abstract class FeedEvent {}
class LoadFeed extends FeedEvent {}

abstract class FeedState {}
class FeedInitial extends FeedState {}
class FeedLoading extends FeedState {}
class FeedLoaded extends FeedState {
  final List<Map<String, dynamic>> items;
  FeedLoaded(this.items);
}
class FeedError extends FeedState { final String message; FeedError(this.message); }

class FeedBloc extends Bloc<FeedEvent, FeedState> {
  final FeedRepository repository;
  FeedBloc({required this.repository}) : super(FeedInitial()) {
    on<LoadFeed>(_onLoad);
  }

  Future<void> _onLoad(LoadFeed event, Emitter<FeedState> emit) async {
    emit(FeedLoading());
    try {
      final items = await repository.getFeed(limit: 20, offset: 0);
      emit(FeedLoaded(items));
    } catch (e) {
      emit(FeedError(e.toString()));
    }
  }
}
```

- [ ] **Step 5: Write data/feed_remote_data_source.dart**

```dart
import '../domain/feed_repository.dart';
import '../../../../core/network/api_client.dart';

class FeedRemoteDataSource implements FeedRepository {
  final ApiClient _apiClient;
  FeedRemoteDataSource({required ApiClient apiClient}) : _apiClient = apiClient;

  @override
  Future<List<Map<String, dynamic>>> getFeed({int limit = 20, int offset = 0}) async {
    final response = await _apiClient.dio.get('/feed', queryParameters: {'limit': limit, 'offset': offset});
    return List<Map<String, dynamic>>.from(response.data);
  }
}
```

- [ ] **Step 6: Write home_screen.dart**

```dart
import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/di/injection.dart';
import '../bloc/feed_bloc.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (_) => sl<FeedBloc>()..add(LoadFeed()),
      child: Scaffold(
        appBar: AppBar(
          title: const Text('AlterMe'),
          actions: [
            IconButton(icon: const Icon(Icons.person), onPressed: () => context.push('/profile')),
          ],
        ),
        floatingActionButton: FloatingActionButton(
          onPressed: () => context.push('/camera'),
          child: const Icon(Icons.add_a_photo),
        ),
        body: BlocBuilder<FeedBloc, FeedState>(
          builder: (context, state) {
            if (state is FeedLoading) return const Center(child: CircularProgressIndicator());
            if (state is FeedError) return Center(child: Text(state.message));
            if (state is FeedLoaded) {
              if (state.items.isEmpty) return const Center(child: Text('Nenhum alter ego ainda. Seja o primeiro!'));
              return GridView.builder(
                padding: const EdgeInsets.all(8),
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: 2, crossAxisSpacing: 8, mainAxisSpacing: 8),
                itemCount: state.items.length,
                itemBuilder: (context, i) {
                  final item = state.items[i];
                  return ClipRRect(
                    borderRadius: BorderRadius.circular(12),
                    child: CachedNetworkImage(
                      imageUrl: item['image_url'] as String,
                      fit: BoxFit.cover,
                      placeholder: (_, __) => const Center(child: CircularProgressIndicator()),
                    ),
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
```

- [ ] **Step 7: Register feed in injection.dart**

```dart
// Feed
sl.registerLazySingleton<FeedRepository>(() => FeedRemoteDataSource(apiClient: sl()));
sl.registerFactory(() => FeedBloc(repository: sl()));
```

- [ ] **Step 8: Run tests**

```bash
flutter test test/features/feed/feed_bloc_test.dart
```
Expected: PASS

- [ ] **Step 9: Commit**

```bash
git add lib/features/feed/ test/features/feed/
git commit -m "feat: add feed feature (home screen, BLoC)"
```

---

## Task 6: Profile Feature

**Files:**
- Create: `lib/features/profile/data/profile_remote_data_source.dart`
- Create: `lib/features/profile/domain/profile_repository.dart`
- Create: `lib/features/profile/presentation/bloc/profile_bloc.dart`
- Create: `lib/features/profile/presentation/profile_screen.dart`
- Create: `test/features/profile/profile_bloc_test.dart`

- [ ] **Step 1: Write failing test**

```dart
// test/features/profile/profile_bloc_test.dart
import 'package:bloc_test/bloc_test.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:alter_me/features/profile/domain/profile_repository.dart';
import 'package:alter_me/features/profile/presentation/bloc/profile_bloc.dart';

class MockProfileRepository extends Mock implements ProfileRepository {}

void main() {
  late MockProfileRepository mockRepo;
  setUp(() { mockRepo = MockProfileRepository(); });

  blocTest<ProfileBloc, ProfileState>(
    'emits [ProfileLoading, ProfileLoaded] on success',
    build: () {
      when(() => mockRepo.getSimilarUsers(userId: any(named: 'userId')))
          .thenAnswer((_) async => []);
      return ProfileBloc(repository: mockRepo);
    },
    act: (bloc) => bloc.add(LoadProfile(userId: 'user-1')),
    expect: () => [isA<ProfileLoading>(), isA<ProfileLoaded>()],
  );
}
```

- [ ] **Step 2: Run to verify it fails**

```bash
flutter test test/features/profile/profile_bloc_test.dart
```

- [ ] **Step 3: Write domain/profile_repository.dart**

```dart
abstract class ProfileRepository {
  Future<List<Map<String, dynamic>>> getSimilarUsers({required String userId});
}
```

- [ ] **Step 4: Write presentation/bloc/profile_bloc.dart**

```dart
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../domain/profile_repository.dart';

abstract class ProfileEvent {}
class LoadProfile extends ProfileEvent { final String userId; LoadProfile({required this.userId}); }

abstract class ProfileState {}
class ProfileInitial extends ProfileState {}
class ProfileLoading extends ProfileState {}
class ProfileLoaded extends ProfileState {
  final List<Map<String, dynamic>> similarUsers;
  ProfileLoaded(this.similarUsers);
}
class ProfileError extends ProfileState { final String message; ProfileError(this.message); }

class ProfileBloc extends Bloc<ProfileEvent, ProfileState> {
  final ProfileRepository repository;
  ProfileBloc({required this.repository}) : super(ProfileInitial()) {
    on<LoadProfile>(_onLoad);
  }

  Future<void> _onLoad(LoadProfile event, Emitter<ProfileState> emit) async {
    emit(ProfileLoading());
    try {
      final users = await repository.getSimilarUsers(userId: event.userId);
      emit(ProfileLoaded(users));
    } catch (e) {
      emit(ProfileError(e.toString()));
    }
  }
}
```

- [ ] **Step 5: Write data/profile_remote_data_source.dart**

```dart
import '../domain/profile_repository.dart';
import '../../../../core/network/api_client.dart';

class ProfileRemoteDataSource implements ProfileRepository {
  final ApiClient _apiClient;
  ProfileRemoteDataSource({required ApiClient apiClient}) : _apiClient = apiClient;

  @override
  Future<List<Map<String, dynamic>>> getSimilarUsers({required String userId}) async {
    final response = await _apiClient.dio.get('/profile/$userId/similar');
    return List<Map<String, dynamic>>.from(response.data);
  }
}
```

- [ ] **Step 6: Write profile_screen.dart**

```dart
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../../../../core/di/injection.dart';
import '../bloc/profile_bloc.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final userId = Supabase.instance.client.auth.currentUser!.id;
    return BlocProvider(
      create: (_) => sl<ProfileBloc>()..add(LoadProfile(userId: userId)),
      child: Scaffold(
        appBar: AppBar(title: const Text('Perfil')),
        body: BlocBuilder<ProfileBloc, ProfileState>(
          builder: (context, state) {
            if (state is ProfileLoading) return const Center(child: CircularProgressIndicator());
            if (state is ProfileError) return Center(child: Text(state.message));
            if (state is ProfileLoaded) {
              if (state.similarUsers.isEmpty) {
                return const Center(child: Text('Gere mais alter egos para encontrar usuários similares!'));
              }
              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Padding(
                    padding: const EdgeInsets.all(16),
                    child: Text('Usuários com estilo similar', style: Theme.of(context).textTheme.titleMedium),
                  ),
                  Expanded(
                    child: ListView.builder(
                      itemCount: state.similarUsers.length,
                      itemBuilder: (context, i) {
                        final user = state.similarUsers[i];
                        return ListTile(
                          leading: const CircleAvatar(child: Icon(Icons.person)),
                          title: Text(user['username'] ?? ''),
                          trailing: Text('${user['shared_styles']} estilos em comum'),
                        );
                      },
                    ),
                  ),
                ],
              );
            }
            return const SizedBox.shrink();
          },
        ),
      ),
    );
  }
}
```

- [ ] **Step 7: Register profile in injection.dart**

```dart
// Profile
sl.registerLazySingleton<ProfileRepository>(() => ProfileRemoteDataSource(apiClient: sl()));
sl.registerFactory(() => ProfileBloc(repository: sl()));
```

- [ ] **Step 8: Run all tests**

```bash
flutter test
```
Expected: all tests PASS

- [ ] **Step 9: Commit**

```bash
git add lib/features/profile/ test/features/profile/
git commit -m "feat: add profile feature (similar users, BLoC)"
```

---

## Task 7: End-to-End Smoke Test

- [ ] **Step 1: Run the backend**

```bash
cd backend && uvicorn app.main:app --reload
```

- [ ] **Step 2: Run the Flutter app**

```bash
flutter run --dart-define=SUPABASE_URL=https://your-project.supabase.co \
            --dart-define=SUPABASE_ANON_KEY=your-anon-key \
            --dart-define=API_URL=http://10.0.2.2:8000
```

- [ ] **Step 3: Verify golden path**

Walk through manually:
1. Register new account → redirects to home feed
2. Tap FAB → camera opens → take selfie
3. Universe selector appears → choose "Anime"
4. Generating screen shows loading animation
5. Local notification fires when done
6. Result screen shows generated image
7. Share button opens native share sheet
8. Back to home → alter ego appears in grid
9. Profile → similar users list appears

- [ ] **Step 4: Final commit**

```bash
git add .
git commit -m "feat: complete AlterMe Flutter app"
```
