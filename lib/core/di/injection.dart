import 'package:get_it/get_it.dart';
import '../network/api_client.dart';

final sl = GetIt.instance;

void setupDependencies() {
  sl.registerLazySingleton(() => ApiClient());
}
